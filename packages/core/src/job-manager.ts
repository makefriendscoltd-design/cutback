import {
  Job,
  JobStatus,
  JobResults,
  CutDecision,
  Transcript,
  Caption,
  Preset,
  createLogger,
} from '@cutback/shared';
import { getDatabase } from './database';
import { ProcessingPipeline, ProgressCallback } from './pipeline';
import { presetLoader } from '@cutback/preset-manager';
import { v4 as uuidv4 } from 'uuid';

const logger = createLogger('job-manager');

export interface CreateJobParams {
  videoPath: string;
  presetId: string;
}

/**
 * 작업(Job) 생명주기 관리
 */
export class JobManager {
  private pipeline: ProcessingPipeline;
  private progressListeners: Map<string, ProgressCallback> = new Map();

  constructor() {
    this.pipeline = new ProcessingPipeline();
  }

  /**
   * 새 작업 생성
   */
  async createJob(params: CreateJobParams): Promise<Job> {
    const db = getDatabase();
    const job: Job = {
      id: uuidv4(),
      videoPath: params.videoPath,
      presetId: params.presetId,
      status: JobStatus.PENDING,
      progress: 0,
      createdAt: new Date(),
    };

    db.prepare(
      `INSERT INTO jobs (id, video_path, preset_id, status, progress, created_at)
       VALUES (?, ?, ?, ?, ?, ?)`
    ).run(
      job.id,
      job.videoPath,
      job.presetId,
      job.status,
      job.progress,
      job.createdAt.toISOString()
    );

    logger.info('Job created', { jobId: job.id, preset: job.presetId });
    return job;
  }

  /**
   * 작업 처리 시작
   */
  async processJob(
    jobId: string,
    onProgress?: ProgressCallback
  ): Promise<JobResults> {
    const db = getDatabase();
    const job = this.getJob(jobId);

    if (!job) throw new Error(`Job not found: ${jobId}`);
    if (job.status === JobStatus.PROCESSING) {
      throw new Error(`Job already processing: ${jobId}`);
    }

    // 상태 업데이트: PROCESSING
    db.prepare(
      `UPDATE jobs SET status = ?, started_at = ? WHERE id = ?`
    ).run(JobStatus.PROCESSING, new Date().toISOString(), jobId);

    // 프리셋 로드
    let preset: Preset;
    try {
      preset = await presetLoader.load(job.presetId);
    } catch {
      throw new Error(`Preset not found: ${job.presetId}`);
    }

    const progressCallback: ProgressCallback = (stage, progress, detail) => {
      db.prepare(`UPDATE jobs SET progress = ? WHERE id = ?`).run(
        progress,
        jobId
      );
      onProgress?.(stage, progress, detail);
      this.progressListeners.get(jobId)?.(stage, progress, detail);
    };

    try {
      // 파이프라인 실행
      const results = await this.pipeline.execute(
        { ...job, status: JobStatus.PROCESSING },
        preset,
        progressCallback
      );

      // 결과 DB 저장
      this.saveResults(jobId, results);

      // 상태 업데이트: COMPLETED
      db.prepare(
        `UPDATE jobs SET status = ?, progress = 100, completed_at = ? WHERE id = ?`
      ).run(JobStatus.COMPLETED, new Date().toISOString(), jobId);

      logger.info('Job completed', { jobId });
      return results;
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : 'Unknown pipeline error';

      // 상태 업데이트: FAILED
      db.prepare(`UPDATE jobs SET status = ?, error = ? WHERE id = ?`).run(
        JobStatus.FAILED,
        errorMsg,
        jobId
      );

      logger.error('Job failed', { jobId, error: errorMsg });
      throw err;
    }
  }

  /**
   * 작업 취소
   */
  cancelJob(jobId: string): void {
    const db = getDatabase();
    db.prepare(`UPDATE jobs SET status = ? WHERE id = ?`).run(
      JobStatus.CANCELLED,
      jobId
    );
    logger.info('Job cancelled', { jobId });
  }

  /**
   * 작업 조회
   */
  getJob(jobId: string): Job | null {
    const db = getDatabase();
    const row = db
      .prepare(`SELECT * FROM jobs WHERE id = ?`)
      .get(jobId) as Record<string, unknown> | undefined;

    if (!row) return null;
    return this.rowToJob(row);
  }

  /**
   * 전체 작업 목록
   */
  listJobs(): Job[] {
    const db = getDatabase();
    const rows = db
      .prepare(`SELECT * FROM jobs ORDER BY created_at DESC`)
      .all() as Record<string, unknown>[];

    return rows.map((row) => this.rowToJob(row));
  }

  /**
   * 작업 결과 조회
   */
  getJobResults(jobId: string): JobResults | null {
    const db = getDatabase();

    // Transcript
    const transcriptRow = db
      .prepare(`SELECT * FROM transcripts WHERE job_id = ?`)
      .get(jobId) as Record<string, unknown> | undefined;

    if (!transcriptRow) return null;

    const transcript: Transcript = {
      words: JSON.parse(transcriptRow.words_json as string),
      full_text: transcriptRow.full_text as string,
      language: transcriptRow.language as string,
      duration: transcriptRow.duration as number,
    };

    // Cut Decisions
    const cutRows = db
      .prepare(`SELECT * FROM cut_decisions WHERE job_id = ? ORDER BY start_time`)
      .all(jobId) as Record<string, unknown>[];

    const cutDecisions: CutDecision[] = cutRows.map((row) => ({
      id: row.id as string,
      type: row.type as CutDecision['type'],
      start: row.start_time as number,
      end: row.end_time as number,
      duration: row.duration as number,
      confidence: row.confidence as number,
      metadata: row.metadata ? JSON.parse(row.metadata as string) : undefined,
      enabled: Boolean(row.enabled),
      user_approved: Boolean(row.user_approved),
    }));

    // Captions
    const captionRows = db
      .prepare(`SELECT * FROM captions WHERE job_id = ? ORDER BY start_time`)
      .all(jobId) as Record<string, unknown>[];

    const captions: Caption[] = captionRows.map((row) => ({
      id: row.id as string,
      text: row.text as string,
      start: row.start_time as number,
      end: row.end_time as number,
      style: row.style_json ? JSON.parse(row.style_json as string) : undefined,
    }));

    // Statistics 재계산
    const enabledCuts = cutDecisions.filter((c) => c.enabled);
    const totalRemoved = enabledCuts.reduce((sum, c) => sum + c.duration, 0);
    const naturalness = this.calculateNaturalness(enabledCuts, transcript.duration);

    return {
      transcript,
      cutDecisions,
      captions,
      naturalness_score: naturalness,
      statistics: {
        original_duration: transcript.duration,
        edited_duration: Math.max(0, transcript.duration - totalRemoved),
        silence_removed: enabledCuts.filter((c) => c.type === 'silence').length,
        fillers_removed: enabledCuts.filter((c) => c.type === 'filler_word').length,
        retakes_removed: enabledCuts.filter((c) => c.type === 'retake').length,
        total_cuts: enabledCuts.length,
        cut_frequency:
          transcript.duration > 0
            ? Math.round(
                (enabledCuts.length / (transcript.duration / 60)) * 10
              ) / 10
            : 0,
        naturalness_score: naturalness,
      },
    };
  }

  /**
   * Cut Decision 활성/비활성 토글
   */
  toggleCutDecision(cutId: string, enabled: boolean): void {
    const db = getDatabase();
    db.prepare(`UPDATE cut_decisions SET enabled = ? WHERE id = ?`).run(
      enabled ? 1 : 0,
      cutId
    );
  }

  /**
   * Progress 리스너 등록
   */
  onProgress(jobId: string, callback: ProgressCallback): void {
    this.progressListeners.set(jobId, callback);
  }

  /**
   * Progress 리스너 제거
   */
  offProgress(jobId: string): void {
    this.progressListeners.delete(jobId);
  }

  /**
   * 작업 삭제
   */
  deleteJob(jobId: string): void {
    const db = getDatabase();
    db.prepare(`DELETE FROM jobs WHERE id = ?`).run(jobId);
    logger.info('Job deleted', { jobId });
  }

  // --- Private helpers ---

  private calculateNaturalness(cuts: CutDecision[], duration: number): number {
    if (duration === 0 || cuts.length === 0) return 1.0;
    let score = 1.0;
    const cutsPerMinute = cuts.length / (duration / 60);
    if (cutsPerMinute > 20) score -= (cutsPerMinute - 20) * 0.01;
    for (const cut of cuts) {
      if (cut.duration < 0.3) score -= 0.02;
    }
    for (let i = 0; i < cuts.length - 1; i++) {
      const gap = cuts[i + 1].start - cuts[i].end;
      if (gap < 0.5) score -= 0.03;
    }
    const totalRemoved = cuts.reduce((sum, c) => sum + c.duration, 0);
    const removalRatio = totalRemoved / duration;
    if (removalRatio > 0.5) score -= (removalRatio - 0.5) * 0.3;
    return Math.max(0, Math.min(1, Math.round(score * 100) / 100));
  }

  private saveResults(jobId: string, results: JobResults): void {
    const db = getDatabase();

    const insertMany = db.transaction(() => {
      // Transcript 저장
      db.prepare(
        `INSERT OR REPLACE INTO transcripts (job_id, full_text, language, duration, words_json)
         VALUES (?, ?, ?, ?, ?)`
      ).run(
        jobId,
        results.transcript.full_text,
        results.transcript.language,
        results.transcript.duration,
        JSON.stringify(results.transcript.words)
      );

      // Cut Decisions 저장
      const cutStmt = db.prepare(
        `INSERT INTO cut_decisions (id, job_id, type, start_time, end_time, duration, confidence, metadata, enabled, user_approved)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      );

      for (const cut of results.cutDecisions) {
        cutStmt.run(
          cut.id,
          jobId,
          cut.type,
          cut.start,
          cut.end,
          cut.duration,
          cut.confidence,
          cut.metadata ? JSON.stringify(cut.metadata) : null,
          cut.enabled ? 1 : 0,
          cut.user_approved ? 1 : 0
        );
      }

      // Captions 저장
      const capStmt = db.prepare(
        `INSERT INTO captions (id, job_id, text, start_time, end_time, style_json)
         VALUES (?, ?, ?, ?, ?, ?)`
      );

      for (const cap of results.captions) {
        capStmt.run(
          cap.id,
          jobId,
          cap.text,
          cap.start,
          cap.end,
          cap.style ? JSON.stringify(cap.style) : null
        );
      }
    });

    insertMany();
    logger.info('Results saved to DB', { jobId });
  }

  private rowToJob(row: Record<string, unknown>): Job {
    return {
      id: row.id as string,
      videoPath: row.video_path as string,
      presetId: row.preset_id as string,
      status: row.status as JobStatus,
      progress: row.progress as number,
      createdAt: new Date(row.created_at as string),
      startedAt: row.started_at
        ? new Date(row.started_at as string)
        : undefined,
      completedAt: row.completed_at
        ? new Date(row.completed_at as string)
        : undefined,
      error: (row.error as string) || undefined,
    };
  }
}
