/**
 * JSON-based calibration repository.
 *
 * 사용자가 반복적으로 manual override 한 패턴을 학습해 다음 작업에 추천값으로 적용.
 * 현재는 단순 JSON 파일 기반 (Electron userData 디렉터리).
 * Repository interface 로 감싸서 추후 DB (better-sqlite3) 로 이관할 때 호출부를 안 바꿔도 되도록 함.
 */

import fs from 'fs/promises';
import path from 'path';
import {
  CalibrationRepository,
  PresetCalibration,
  createLogger,
} from '@cutback/shared';

const logger = createLogger('calibration');

/** EWMA (지수 가중 이동 평균) — 최근값에 더 큰 가중치 */
function ewma(prev: number | undefined, next: number, alpha = 0.3): number {
  if (typeof prev !== 'number') return next;
  return alpha * next + (1 - alpha) * prev;
}

function emptyCalibration(presetId: string): PresetCalibration {
  return {
    presetId,
    restoredFillers: {},
    manualCutAvgMs: 0,
    manualCutCount: 0,
    sampleCount: 0,
    lastUpdated: new Date().toISOString(),
  };
}

export class JsonCalibrationRepository implements CalibrationRepository {
  private filePath: string;
  private cache: Record<string, PresetCalibration> | null = null;

  constructor(storeDir: string) {
    this.filePath = path.join(storeDir, 'calibration.json');
  }

  private async load(): Promise<Record<string, PresetCalibration>> {
    if (this.cache) return this.cache;
    try {
      const raw = await fs.readFile(this.filePath, 'utf-8');
      this.cache = JSON.parse(raw) as Record<string, PresetCalibration>;
    } catch {
      this.cache = {};
    }
    return this.cache;
  }

  private async persist(): Promise<void> {
    if (!this.cache) return;
    try {
      await fs.mkdir(path.dirname(this.filePath), { recursive: true });
      await fs.writeFile(this.filePath, JSON.stringify(this.cache, null, 2), 'utf-8');
    } catch (err) {
      logger.error('Failed to persist calibration', {
        error: (err as Error).message,
      });
    }
  }

  async get(presetId: string): Promise<PresetCalibration | null> {
    const all = await this.load();
    return all[presetId] ?? null;
  }

  async record(
    presetId: string,
    delta: {
      restoredFillerWords?: string[];
      manualCutDurationsMs?: number[];
      silenceThresholdDb?: number;
      minSilenceMs?: number;
      fillerStrength?: 'conservative' | 'balanced' | 'aggressive';
    }
  ): Promise<PresetCalibration> {
    const all = await this.load();
    const current = all[presetId] ?? emptyCalibration(presetId);

    // restored filler words 누적
    if (delta.restoredFillerWords) {
      for (const word of delta.restoredFillerWords) {
        current.restoredFillers[word] = (current.restoredFillers[word] ?? 0) + 1;
      }
    }

    // manual cut 평균 길이 (EWMA)
    if (delta.manualCutDurationsMs && delta.manualCutDurationsMs.length > 0) {
      const avg =
        delta.manualCutDurationsMs.reduce((s, n) => s + n, 0) /
        delta.manualCutDurationsMs.length;
      current.manualCutAvgMs = ewma(current.manualCutAvgMs || undefined, avg);
      current.manualCutCount += delta.manualCutDurationsMs.length;
    }

    // 선호 threshold (EWMA)
    if (typeof delta.silenceThresholdDb === 'number') {
      current.preferredSilenceThresholdDb = ewma(
        current.preferredSilenceThresholdDb,
        delta.silenceThresholdDb
      );
    }
    if (typeof delta.minSilenceMs === 'number') {
      current.preferredMinSilenceMs = ewma(
        current.preferredMinSilenceMs,
        delta.minSilenceMs
      );
    }
    // 선호 filler strength: 가장 자주 선택한 값 (가중치 추적은 sampleCount 비교)
    if (delta.fillerStrength) {
      // 단순 last-write-wins. 추후 빈도 카운팅으로 개선 가능.
      current.preferredFillerStrength = delta.fillerStrength;
    }

    current.sampleCount += 1;
    current.lastUpdated = new Date().toISOString();

    all[presetId] = current;
    this.cache = all;
    await this.persist();

    logger.info('Calibration updated', {
      presetId,
      sampleCount: current.sampleCount,
      restoredCount: Object.keys(current.restoredFillers).length,
    });

    return current;
  }

  async reset(presetId: string): Promise<void> {
    const all = await this.load();
    delete all[presetId];
    this.cache = all;
    await this.persist();
  }

  async list(): Promise<PresetCalibration[]> {
    const all = await this.load();
    return Object.values(all);
  }
}

/** 싱글톤 인스턴스 — main process 가 init 시점에 storeDir 을 주입 */
let _instance: CalibrationRepository | null = null;

export function initCalibrationRepository(storeDir: string): CalibrationRepository {
  _instance = new JsonCalibrationRepository(storeDir);
  return _instance;
}

export function getCalibrationRepository(): CalibrationRepository {
  if (!_instance) {
    throw new Error('Calibration repository not initialized. Call initCalibrationRepository first.');
  }
  return _instance;
}
