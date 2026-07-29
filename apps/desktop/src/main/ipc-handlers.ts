import { ipcMain, BrowserWindow, dialog, shell } from 'electron';
import { execSync } from 'child_process';
import path from 'path';
import {
  JobManager,
  recomputeCuts,
  getCalibrationRepository,
  PythonClient,
} from '@cutback/core';
import { presetLoader } from '@cutback/preset-manager';
import { saveEDL, saveSRT, installToCapCut, findCapCutDraftsDir, capCutAutomation, renderVideo } from '@cutback/capcut-controller';
import { extractWaveformPeaks, generatePreviewVideo } from '@cutback/audio-engine';
import {
  ShortsComposer,
  listFonts,
  buildSubtitleEvents,
} from '@cutback/shorts-composer';
import type {
  ShortsCompositionSpec,
  SubtitleEvent,
  WordTiming,
} from '@cutback/shorts-composer';
import { IPC_CHANNELS, createLogger } from '@cutback/shared';
import { runPreflight, getHealth } from './preflight';
import { checkUpdatesManually, installNow, getLastUpdateStatus } from './updater';

const logger = createLogger('ipc');

const jobManager = new JobManager();

/**
 * 모든 IPC 핸들러 등록
 */
export function registerIPCHandlers(
  getMainWindow: () => BrowserWindow | null
): void {
  // ===== Job Management =====

  ipcMain.handle(IPC_CHANNELS.JOB_CREATE, async (_event, params) => {
    try {
      const job = await jobManager.createJob(params);

      // 비동기로 파이프라인 실행 시작
      jobManager.processJob(job.id, ((
        stage: string,
        progress: number,
        detail?: string,
        partial?: unknown
      ) => {
        getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_PROGRESS, {
          jobId: job.id,
          stage,
          progress,
          detail,
        });
        // 부분 결과가 있으면 별도 채널로 스트리밍 (Live Analysis Timeline 용)
        if (partial) {
          getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_PARTIAL, {
            jobId: job.id,
            stage,
            partial,
          });
        }
      }) as Parameters<typeof jobManager.processJob>[1]).then((results) => {
        getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_COMPLETED, {
          jobId: job.id,
          results,
        });
      }).catch((err) => {
        getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_ERROR, {
          jobId: job.id,
          error: (err as Error).message,
        });
      });

      return { success: true, job };
    } catch (err) {
      logger.error('Job creation failed', { error: (err as Error).message });
      return { success: false, error: (err as Error).message };
    }
  });

  ipcMain.handle(IPC_CHANNELS.JOB_LIST, async () => {
    return jobManager.listJobs();
  });

  ipcMain.handle(IPC_CHANNELS.JOB_GET, async (_event, jobId: string) => {
    const job = jobManager.getJob(jobId);
    const results = jobManager.getJobResults(jobId);
    return { job, results };
  });

  ipcMain.handle(IPC_CHANNELS.JOB_CANCEL, async (_event, jobId: string) => {
    jobManager.cancelJob(jobId);
    return { success: true };
  });

  ipcMain.handle(IPC_CHANNELS.JOB_DELETE, async (_event, jobId: string) => {
    try {
      jobManager.deleteJob(jobId);
      return { success: true };
    } catch (err) {
      return { success: false, error: (err as Error).message };
    }
  });

  // ===== Audio Peaks (Live Analysis Timeline) =====

  ipcMain.handle(
    IPC_CHANNELS.AUDIO_PEAKS,
    async (
      _event,
      { audioPath, bucketCount }: { audioPath: string; bucketCount?: number }
    ) => {
      try {
        const peaks = await extractWaveformPeaks(audioPath, bucketCount ?? 1500);
        return { success: true, ...peaks };
      } catch (err) {
        logger.error('Audio peaks extraction failed', {
          error: (err as Error).message,
        });
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // ===== Browser-playable preview (HEVC 등 미지원 코덱 우회) =====

  ipcMain.handle(
    IPC_CHANNELS.VIDEO_PREVIEW,
    async (_event, { sourcePath }: { sourcePath: string }) => {
      try {
        const result = await generatePreviewVideo(sourcePath, (p) => {
          getMainWindow()?.webContents.send('video:preview-progress', {
            sourcePath,
            current: p.current,
            total: p.total,
          });
        });
        return { success: true, ...result };
      } catch (err) {
        logger.error('preview generation failed', {
          error: (err as Error).message,
        });
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // ===== Cut Recompute (Threshold preview) =====

  ipcMain.handle(
    IPC_CHANNELS.CUT_RECOMPUTE,
    async (_event, req: Parameters<typeof recomputeCuts>[0]) => {
      return await recomputeCuts(req);
    }
  );

  // ===== Calibration (preset learning) =====

  ipcMain.handle(
    IPC_CHANNELS.CALIBRATION_GET,
    async (_event, presetId: string) => {
      try {
        return { success: true, calibration: await getCalibrationRepository().get(presetId) };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  ipcMain.handle(
    IPC_CHANNELS.CALIBRATION_RECORD,
    async (
      _event,
      payload: { presetId: string; delta: Parameters<ReturnType<typeof getCalibrationRepository>['record']>[1] }
    ) => {
      try {
        const updated = await getCalibrationRepository().record(payload.presetId, payload.delta);
        return { success: true, calibration: updated };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  ipcMain.handle(IPC_CHANNELS.CALIBRATION_LIST, async () => {
    try {
      return { success: true, calibrations: await getCalibrationRepository().list() };
    } catch (err) {
      return { success: false, error: (err as Error).message };
    }
  });

  ipcMain.handle(
    IPC_CHANNELS.CALIBRATION_RESET,
    async (_event, presetId: string) => {
      try {
        await getCalibrationRepository().reset(presetId);
        return { success: true };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // ===== Cut Decision Toggle =====

  ipcMain.handle(
    'cut:toggle',
    async (_event, { cutId, enabled }: { cutId: string; enabled: boolean }) => {
      jobManager.toggleCutDecision(cutId, enabled);
      return { success: true };
    }
  );

  // ===== Preset Management =====

  ipcMain.handle(IPC_CHANNELS.PRESET_LIST, async () => {
    return presetLoader.listAll();
  });

  ipcMain.handle(
    IPC_CHANNELS.PRESET_LOAD,
    async (_event, presetId: string) => {
      return presetLoader.load(presetId);
    }
  );

  ipcMain.handle(
    IPC_CHANNELS.PRESET_SAVE,
    async (_event, { id, preset }) => {
      await presetLoader.save(id, preset);
      return { success: true };
    }
  );

  ipcMain.handle(
    IPC_CHANNELS.PRESET_DELETE,
    async (_event, presetId: string) => {
      await presetLoader.delete(presetId);
      return { success: true };
    }
  );

  // ===== File Dialog =====

  ipcMain.handle('dialog:openVideo', async () => {
    const result = await dialog.showOpenDialog({
      title: '영상 파일 선택',
      filters: [
        {
          name: '영상 파일',
          extensions: ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv'],
        },
        { name: '모든 파일', extensions: ['*'] },
      ],
      properties: ['openFile'],
    });

    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }

    return result.filePaths[0];
  });

  // Mode B: 보이스오버 (오디오 또는 영상)
  ipcMain.handle('dialog:openVoiceover', async () => {
    const result = await dialog.showOpenDialog({
      title: '보이스오버 파일 선택 (오디오/영상)',
      filters: [
        {
          name: '오디오/영상',
          extensions: ['mp3', 'wav', 'm4a', 'aac', 'flac', 'ogg', 'mp4', 'mov'],
        },
        { name: '모든 파일', extensions: ['*'] },
      ],
      properties: ['openFile'],
    });
    if (result.canceled || result.filePaths.length === 0) return null;
    return result.filePaths[0];
  });

  // Mode B: B-roll 클립 다중 선택
  ipcMain.handle('dialog:openMultipleVideos', async () => {
    const result = await dialog.showOpenDialog({
      title: 'B-roll 클립 선택 (여러 개 가능)',
      filters: [
        {
          name: '영상 파일',
          extensions: ['mp4', 'mov', 'avi', 'mkv', 'webm'],
        },
        { name: '모든 파일', extensions: ['*'] },
      ],
      properties: ['openFile', 'multiSelections'],
    });
    if (result.canceled || result.filePaths.length === 0) return [];
    return result.filePaths;
  });

  // ===== Export =====

  ipcMain.handle(
    IPC_CHANNELS.EXPORT_EDL,
    async (_event, { jobId }: { jobId: string }) => {
      const results = jobManager.getJobResults(jobId);
      if (!results) return { success: false, error: 'No results found' };

      const saveResult = await dialog.showSaveDialog({
        title: 'EDL 파일 저장',
        defaultPath: 'cutback-export.edl',
        filters: [{ name: 'EDL', extensions: ['edl'] }],
      });

      if (saveResult.canceled || !saveResult.filePath) {
        return { success: false, error: 'Cancelled' };
      }

      if (!results.cutDecisions || !results.statistics) {
        return { success: false, error: 'No cut decisions or statistics available' };
      }

      await saveEDL(
        results.cutDecisions,
        results.statistics.original_duration,
        saveResult.filePath
      );

      return { success: true, path: saveResult.filePath };
    }
  );

  ipcMain.handle(
    IPC_CHANNELS.EXPORT_SRT,
    async (_event, { jobId }: { jobId: string }) => {
      const results = jobManager.getJobResults(jobId);
      if (!results) return { success: false, error: 'No results found' };

      const saveResult = await dialog.showSaveDialog({
        title: 'SRT 자막 파일 저장',
        defaultPath: 'cutback-captions.srt',
        filters: [{ name: 'SRT Subtitles', extensions: ['srt'] }],
      });

      if (saveResult.canceled || !saveResult.filePath) {
        return { success: false, error: 'Cancelled' };
      }

      if (!results.captions) {
        return { success: false, error: 'No captions available' };
      }

      await saveSRT(results.captions, saveResult.filePath);

      return { success: true, path: saveResult.filePath };
    }
  );

  ipcMain.handle(
    IPC_CHANNELS.EXPORT_CAPCUT,
    async (_event, { jobId }: { jobId: string }) => {
      const job = jobManager.getJob(jobId);
      const results = jobManager.getJobResults(jobId);
      if (!results || !job) return { success: false, error: 'No results found' };

      // 프리셋에서 canvas 정보 로드
      let width = 1920;
      let height = 1080;
      try {
        const preset = await presetLoader.load(job.presetId);
        if (preset.canvas) {
          width = preset.canvas.width;
          height = preset.canvas.height;
        }
      } catch { /* 프리셋 로드 실패 시 기본값 사용 */ }

      if (!results.cutDecisions || !results.captions || !results.statistics) {
        return { success: false, error: 'Missing required data for CapCut export' };
      }

      try {
        // CapCut 프로젝트 폴더에 직접 설치
        const { projectDir } = await installToCapCut(
          results.cutDecisions,
          results.captions,
          {
            videoPath: job.videoPath,
            videoDuration: Math.round(results.statistics.original_duration * 1_000_000),
            width,
            height,
          }
        );

        // CapCut이 실행 중이 아니면 자동 실행 시도
        if (!capCutAutomation.isRunning()) {
          try {
            const capCutExe = findCapCutExe();
            if (capCutExe) {
              execSync(`start "" "${capCutExe}"`, { shell: 'cmd.exe', timeout: 5000 });
              logger.info('CapCut launched', { exe: capCutExe });
            }
          } catch (launchErr) {
            logger.warn('CapCut auto-launch failed', { error: (launchErr as Error).message });
          }
        }

        return { success: true, path: projectDir, message: 'CapCut 프로젝트가 생성되었습니다. CapCut을 열면 프로젝트 목록에 나타납니다.' };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // ===== Video Render (FFmpeg) =====

  ipcMain.handle(
    IPC_CHANNELS.EXPORT_VIDEO,
    async (_event, { jobId }: { jobId: string }) => {
      const job = jobManager.getJob(jobId);
      const results = jobManager.getJobResults(jobId);
      if (!results || !job) return { success: false, error: 'No results found' };

      const saveResult = await dialog.showSaveDialog({
        title: '편집 영상 저장',
        defaultPath: path.basename(job.videoPath, path.extname(job.videoPath)) + '_edited.mp4',
        filters: [{ name: 'MP4 Video', extensions: ['mp4'] }],
      });

      if (saveResult.canceled || !saveResult.filePath) {
        return { success: false, error: 'Cancelled' };
      }

      if (!results.cutDecisions || !results.statistics) {
        return { success: false, error: 'Missing required data for video rendering' };
      }

      try {
        await renderVideo(
          results.cutDecisions,
          {
            videoPath: job.videoPath,
            outputPath: saveResult.filePath,
            videoDuration: results.statistics.original_duration,
          },
          (percent: number, detail: string) => {
            getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_PROGRESS, {
              jobId,
              stage: 'rendering',
              progress: percent,
              detail,
            });
          }
        );
        // 렌더링 완료 후 파일 탐색기에서 보기
        shell.showItemInFolder(saveResult.filePath);
        return { success: true, path: saveResult.filePath };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // ===== CapCut Automation =====

  ipcMain.handle('capcut:status', async () => {
    return {
      running: capCutAutomation.isRunning(),
      projectsPath: capCutAutomation.getProjectsPath(),
    };
  });

  ipcMain.handle(
    'capcut:apply',
    async (_event, { jobId }: { jobId: string }) => {
      const results = jobManager.getJobResults(jobId);
      if (!results) return { success: false, error: 'No results found' };

      if (!results.cutDecisions) {
        return { success: false, error: 'No cut decisions available' };
      }

      try {
        const result = await capCutAutomation.applyCuts(
          results.cutDecisions,
          (current, total) => {
            getMainWindow()?.webContents.send(IPC_CHANNELS.JOB_PROGRESS, {
              jobId,
              stage: 'capcut_apply',
              progress: Math.round((current / total) * 100),
              detail: `CapCut 적용 중... (${current}/${total})`,
            });
          }
        );
        return { success: true, ...result };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // ===== Mode C: Shorts Composer =====

  ipcMain.handle('shorts:fonts', async () => {
    return listFonts();
  });

  /**
   * 자막 미리보기/검수용 이벤트 생성.
   * 보이스오버가 있으면 STT(faster-whisper)로 자동 받아쓰기 → 단어 타임스탬프로
   * 정확히 싱크된 자막을 만든다. 없으면 스크립트를 음절 단위 템포로 배치.
   * 사용자는 반환된 events 를 표에서 수정한 뒤 compose 에 그대로 넘긴다.
   */
  ipcMain.handle(
    'shorts:previewSubtitles',
    async (
      _event,
      params: {
        script?: string;
        voiceoverPath?: string;
        chunkSyllables?: number;
        syllablesPerSecond?: number;
      }
    ): Promise<{
      success: boolean;
      events?: SubtitleEvent[];
      source?: 'stt' | 'script' | 'none';
      sttError?: string;
      error?: string;
    }> => {
      try {
        let wordTimings: WordTiming[] | undefined;
        let voiceoverDur: number | undefined;
        let sttError: string | undefined;
        let source: 'stt' | 'script' | 'none' = 'none';

        if (params.voiceoverPath) {
          // 미디어 길이는 항상 확보 (STT 실패해도 비례 배분에 쓰임)
          try {
            const client = new PythonClient();
            const healthy = await client.checkHealth();
            if (!healthy) {
              sttError = 'STT 서비스가 실행 중이 아닙니다. 스크립트 기반으로 대체합니다.';
            } else {
              const transcript = await client.transcribe(params.voiceoverPath, 'ko');
              voiceoverDur = transcript.duration;
              if (transcript.words && transcript.words.length > 0) {
                wordTimings = transcript.words.map((w) => ({
                  text: w.text,
                  start: w.start,
                  end: w.end,
                }));
                source = 'stt';
              }
            }
          } catch (err) {
            sttError = `STT 실패: ${(err as Error).message}. 스크립트 기반으로 대체합니다.`;
            logger.warn('Shorts STT failed', { error: (err as Error).message });
          }
        }

        const events = buildSubtitleEvents({
          script: params.script,
          wordTimings,
          voiceoverDur,
          chunkSyllables: params.chunkSyllables,
          syllablesPerSecond: params.syllablesPerSecond,
        });

        if (source !== 'stt') {
          source = events.length > 0 ? 'script' : 'none';
        }

        return { success: true, events, source, sttError };
      } catch (err) {
        return { success: false, error: (err as Error).message };
      }
    }
  );

  // spec 은 outputPath 없이 오고, 여기서 저장 다이얼로그로 결정한다
  let shortsComposing = false;
  ipcMain.handle(
    'shorts:compose',
    async (_event, spec: Omit<ShortsCompositionSpec, 'outputPath'>) => {
      if (shortsComposing) {
        return { success: false, error: '이미 릴스 생성이 진행 중입니다.' };
      }

      const saveResult = await dialog.showSaveDialog({
        title: '릴스 영상 저장',
        defaultPath: `reels-${new Date().toISOString().slice(0, 10)}.mp4`,
        filters: [{ name: 'MP4 Video', extensions: ['mp4'] }],
      });
      if (saveResult.canceled || !saveResult.filePath) {
        return { success: false, error: 'Cancelled' };
      }

      shortsComposing = true;
      try {
        const composer = new ShortsComposer();
        const result = await composer.compose(
          { ...spec, outputPath: saveResult.filePath },
          (p) => {
            getMainWindow()?.webContents.send('shorts:progress', p);
          }
        );
        shell.showItemInFolder(result.outputPath);
        return { success: true, ...result };
      } catch (err) {
        logger.error('Shorts compose failed', { error: (err as Error).message });
        return { success: false, error: (err as Error).message };
      } finally {
        shortsComposing = false;
      }
    }
  );

  // ===== Health / Preflight =====

  ipcMain.handle(IPC_CHANNELS.HEALTH_GET, async (_event, opts?: { force?: boolean }) => {
    if (opts?.force) {
      return runPreflight(true);
    }
    return getHealth();
  });

  // ===== Auto Update =====

  ipcMain.handle(IPC_CHANNELS.UPDATE_CHECK, async () => {
    return checkUpdatesManually();
  });

  ipcMain.handle(IPC_CHANNELS.UPDATE_STATUS, async () => {
    return getLastUpdateStatus();
  });

  ipcMain.handle(IPC_CHANNELS.UPDATE_INSTALL, async () => {
    installNow();
    return { success: true };
  });

  logger.info('All IPC handlers registered');
}

/**
 * CapCut Desktop 실행 파일 경로 탐색
 */
function findCapCutExe(): string | null {
  const localAppData = process.env.LOCALAPPDATA || '';
  const programFiles = process.env.ProgramFiles || 'C:\\Program Files';
  const userProfile = process.env.USERPROFILE || '';

  const possiblePaths = [
    // LOCALAPPDATA 직접 설치 (가장 흔함)
    localAppData ? path.join(localAppData, 'CapCut', 'CapCut.exe') : '',
    localAppData ? path.join(localAppData, 'CapCut', 'Apps', 'CapCut.exe') : '',
    localAppData ? path.join(localAppData, 'Programs', 'CapCut', 'CapCut.exe') : '',
    // Program Files
    path.join(programFiles, 'CapCut', 'CapCut.exe'),
    // JianyingPro (중국판)
    path.join(programFiles, 'JianyingPro', 'JianyingPro.exe'),
    // USERPROFILE 폴백
    userProfile ? path.join(userProfile, 'AppData', 'Local', 'CapCut', 'CapCut.exe') : '',
  ].filter(Boolean);

  for (const p of possiblePaths) {
    try {
      require('fs').accessSync(p);
      return p;
    } catch {
      continue;
    }
  }
  return null;
}
