import fs from 'fs/promises';
import path from 'path';
import { Preset, createLogger } from '@cutback/shared';

const logger = createLogger('preset-loader');

/**
 * 프리셋 로더
 * JSON 파일에서 프리셋을 로드하고 캐싱
 */
export class PresetLoader {
  private cache: Map<string, Preset> = new Map();
  private baseDir: string = path.join(process.cwd(), 'presets');

  /**
   * 프리셋 베이스 디렉토리 설정
   * Electron 패키징 환경에서 app.getPath 등으로 설정 가능
   */
  setBaseDir(dir: string): void {
    this.baseDir = dir;
    this.cache.clear();
    logger.info('Preset base dir set', { dir });
  }

  getBaseDir(): string {
    return this.baseDir;
  }

  /**
   * 프리셋 ID로 로드
   * 예: 'ad-short-form', 'info-talking-head', 'brands/brand-a'
   */
  async load(presetId: string): Promise<Preset> {
    // 캐시 확인
    if (this.cache.has(presetId)) {
      logger.debug('Preset loaded from cache', { presetId });
      return this.cache.get(presetId)!;
    }

    // 파일에서 로드
    const preset = await this.loadFromFile(presetId);

    // 캐시 저장
    this.cache.set(presetId, preset);

    logger.info('Preset loaded', { presetId });
    return preset;
  }

  /**
   * 파일에서 프리셋 로드
   */
  private async loadFromFile(presetId: string): Promise<Preset> {
    // 타입별 프리셋 경로
    const typePath = path.join(this.baseDir, 'types', `${presetId}.json`);

    // 브랜드 프리셋 경로
    const brandPath = path.join(
      this.baseDir,
      'brands',
      `${presetId}.json`
    );

    // 커스텀 프리셋 경로
    const customPath = path.join(
      this.baseDir,
      'custom',
      `${presetId}.json`
    );

    // 순서대로 시도
    for (const filePath of [typePath, brandPath, customPath]) {
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        const preset = JSON.parse(content) as Preset;

        // base_preset이 있으면 재귀적으로 로드 및 병합
        if (preset.base_preset) {
          const basePreset = await this.load(preset.base_preset);
          return this.mergePresets(basePreset, preset);
        }

        return preset;
      } catch (err) {
        // 파일이 없으면 다음 경로 시도
        continue;
      }
    }

    throw new Error(`Preset not found: ${presetId}`);
  }

  /**
   * 베이스 프리셋과 오버라이드 프리셋 병합
   */
  private mergePresets(base: Preset, override: Preset): Preset {
    const merged: Preset = {
      ...base,
      ...override,
      canvas: { ...base.canvas, ...(override.canvas || {}) },
    };

    // Mode A 전용 필드들
    if (base.audio || override.audio) {
      merged.audio = { ...(base.audio || {}), ...(override.audio || {}) } as any;
    }
    if (base.filler_words || override.filler_words) {
      merged.filler_words = {
        ...(base.filler_words || {}),
        ...(override.filler_words || {}),
      } as any;
    }
    if (base.captions || override.captions) {
      merged.captions = {
        ...(base.captions || {}),
        ...(override.captions || {}),
      } as any;
    }
    if (base.style || override.style) {
      merged.style = { ...(base.style || {}), ...(override.style || {}) } as any;
    }
    if (base.pacing || override.pacing) {
      merged.pacing = {
        ...(base.pacing || {}),
        ...(override.pacing || {}),
      } as any;
    }
    if (base.effects || override.effects) {
      merged.effects = {
        ...(base.effects || {}),
        ...(override.effects || {}),
      } as any;
    }

    // Mode B 전용 필드
    if (base.modeBParams || override.modeBParams) {
      merged.modeBParams = {
        ...(base.modeBParams || {}),
        ...(override.modeBParams || {}),
      } as any;
    }

    return merged;
  }

  /**
   * 사용 가능한 모든 프리셋 목록
   */
  async listAll(): Promise<{ id: string; preset: Preset }[]> {
    const presets: { id: string; preset: Preset }[] = [];

    // types 폴더
    const typesDir = path.join(this.baseDir, 'types');
    const typeFiles = await this.listJsonFiles(typesDir);
    for (const file of typeFiles) {
      const id = path.basename(file, '.json');
      const preset = await this.load(id);
      presets.push({ id, preset });
    }

    // brands 폴더
    const brandsDir = path.join(this.baseDir, 'brands');
    const brandFiles = await this.listJsonFiles(brandsDir);
    for (const file of brandFiles) {
      const id = `brands/${path.basename(file, '.json')}`;
      const preset = await this.load(id);
      presets.push({ id, preset });
    }

    // custom 폴더
    const customDir = path.join(this.baseDir, 'custom');
    const customFiles = await this.listJsonFiles(customDir);
    for (const file of customFiles) {
      const id = `custom/${path.basename(file, '.json')}`;
      const preset = await this.load(id);
      presets.push({ id, preset });
    }

    return presets;
  }

  /**
   * 디렉토리 내 JSON 파일 목록
   */
  private async listJsonFiles(dir: string): Promise<string[]> {
    try {
      const files = await fs.readdir(dir);
      return files
        .filter((f) => f.endsWith('.json'))
        .map((f) => path.join(dir, f));
    } catch (err) {
      // 디렉토리가 없으면 빈 배열 반환
      return [];
    }
  }

  /**
   * 프리셋 저장 (커스텀 프리셋)
   */
  async save(presetId: string, preset: Preset): Promise<void> {
    const filePath = path.join(
      this.baseDir,
      'custom',
      `${presetId}.json`
    );

    await fs.mkdir(path.dirname(filePath), { recursive: true });
    await fs.writeFile(filePath, JSON.stringify(preset, null, 2), 'utf-8');

    // 캐시 업데이트
    this.cache.set(`custom/${presetId}`, preset);

    logger.info('Preset saved', { presetId });
  }

  /**
   * 프리셋 삭제 (커스텀 프리셋만 가능)
   */
  async delete(presetId: string): Promise<void> {
    if (!presetId.startsWith('custom/')) {
      throw new Error('Only custom presets can be deleted');
    }

    const filePath = path.join(
      this.baseDir,
      'custom',
      `${presetId.replace('custom/', '')}.json`
    );

    await fs.unlink(filePath);

    // 캐시 제거
    this.cache.delete(presetId);

    logger.info('Preset deleted', { presetId });
  }

  /**
   * 캐시 초기화
   */
  clearCache(): void {
    this.cache.clear();
    logger.info('Preset cache cleared');
  }
}

// 싱글톤 인스턴스
export const presetLoader = new PresetLoader();
