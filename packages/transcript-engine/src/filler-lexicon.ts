import fs from 'fs';
import path from 'path';
import { createLogger } from '@cutback/shared';

const logger = createLogger('filler-lexicon');

/**
 * Filler 사전 외부 JSON 로딩.
 *
 * - 기본 경로: <repo>/presets/lexicons/korean-fillers.json
 * - 환경변수 CUTBACK_FILLER_LEXICON 으로 override 가능
 * - 로딩 실패 시 안전한 빈 사전 + 경고 (기존 KOREAN_FILLER_WORDS fallback은 detector 쪽에서 처리)
 *
 * 한 번 읽고 메모리에 캐시. 파이프라인 한 번 실행마다 reload 할 필요 없음.
 */

export interface FillerLexicon {
  high_confidence: string[];
  medium_confidence: string[];
  context_dependent: string[];
  /** 두 단어 이상 패턴 (정규화된 토큰을 공백으로 join 해서 매칭) */
  phrases: string[];
  /** 절대 제거 금지 단어 (정규화 후 정확 일치) */
  protected_words: string[];
  scoring: ScoringConfig;
}

export interface ScoringConfig {
  context_multipliers: {
    preceding_silence_long: { min_sec: number; factor: number };
    preceding_silence_short: { min_sec: number; factor: number };
    following_silence_long: { min_sec: number; factor: number };
    isolated_short_word: { max_dur_sec: number; factor: number };
    very_short_word: { max_dur_sec: number; factor: number };
    at_sentence_start: { factor: number };
    at_sentence_end: { factor: number };
    repeated_within_sec: { window_sec: number; factor: number };
  };
  default_threshold: number;
  review_band: [number, number];
}

const DEFAULT_SCORING: ScoringConfig = {
  context_multipliers: {
    preceding_silence_long: { min_sec: 0.5, factor: 1.2 },
    preceding_silence_short: { min_sec: 0.2, factor: 1.05 },
    following_silence_long: { min_sec: 0.4, factor: 1.15 },
    isolated_short_word: { max_dur_sec: 0.25, factor: 1.1 },
    very_short_word: { max_dur_sec: 0.15, factor: 1.2 },
    at_sentence_start: { factor: 0.7 },
    at_sentence_end: { factor: 0.85 },
    repeated_within_sec: { window_sec: 5.0, factor: 1.15 },
  },
  default_threshold: 0.65,
  review_band: [0.5, 0.65],
};

const EMPTY_LEXICON: FillerLexicon = {
  high_confidence: [],
  medium_confidence: [],
  context_dependent: [],
  phrases: [],
  protected_words: [],
  scoring: DEFAULT_SCORING,
};

let cached: FillerLexicon | null = null;

/**
 * Lexicon JSON 의 가능한 위치를 순차 탐색.
 * dev (소스 트리) / prod (Electron resourcesPath) 양쪽 지원.
 */
function findLexiconPath(): string | null {
  // 1) 사용자 강제 지정
  const env = process.env.CUTBACK_FILLER_LEXICON;
  if (env && fs.existsSync(env)) return env;

  const candidates: string[] = [];

  // 2) Electron 패키징 환경 - resourcesPath/presets/...
  // process.resourcesPath 는 main process 에서만 정의. 안전하게 try.
  const resourcesPath = (process as NodeJS.Process & { resourcesPath?: string })
    .resourcesPath;
  if (resourcesPath) {
    candidates.push(
      path.join(resourcesPath, 'presets', 'lexicons', 'korean-fillers.json'),
      // electron-builder 의 extraResources 가 app/ 아래로 두는 경우
      path.join(resourcesPath, 'app', 'presets', 'lexicons', 'korean-fillers.json'),
    );
  }

  // 3) dev 모노레포 - transcript-engine/dist 또는 src 기준 상대 경로
  // dist (build 후): packages/transcript-engine/dist/filler-lexicon.js → ../../../../presets
  // src (ts-node):  packages/transcript-engine/src/filler-lexicon.ts  → 동일
  // Windows/Unix 안전하게 여러 깊이 시도.
  const bases = [
    __dirname,
    path.resolve(__dirname, '..'),
    path.resolve(__dirname, '..', '..'),
    path.resolve(__dirname, '..', '..', '..'),
    path.resolve(__dirname, '..', '..', '..', '..'),
    path.resolve(__dirname, '..', '..', '..', '..', '..'),
  ];
  for (const b of bases) {
    candidates.push(path.join(b, 'presets', 'lexicons', 'korean-fillers.json'));
  }

  // 4) CWD 기준 fallback (npm run / pnpm 으로 루트에서 실행할 때)
  candidates.push(
    path.resolve(process.cwd(), 'presets', 'lexicons', 'korean-fillers.json')
  );

  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) return p;
    } catch {
      /* ignore */
    }
  }
  return null;
}

interface RawLexiconJson {
  high_confidence?: { tokens?: unknown };
  medium_confidence?: { tokens?: unknown };
  context_dependent?: { tokens?: unknown };
  phrases?: { tokens?: unknown };
  protected_words?: { tokens?: unknown };
  scoring?: Partial<ScoringConfig>;
}

function asStringArray(v: unknown): string[] {
  if (!Array.isArray(v)) return [];
  return v.filter((x): x is string => typeof x === 'string');
}

/** Lexicon 로딩 (캐시). 실패 시 빈 사전 반환 + 경고. */
export function loadFillerLexicon(forceReload: boolean = false): FillerLexicon {
  if (cached && !forceReload) return cached;

  const lexPath = findLexiconPath();
  if (!lexPath) {
    logger.warn('Filler lexicon JSON not found, using empty (fallback to legacy KOREAN_FILLER_WORDS)');
    cached = { ...EMPTY_LEXICON };
    return cached;
  }

  try {
    const raw = JSON.parse(fs.readFileSync(lexPath, 'utf-8')) as RawLexiconJson;
    cached = {
      high_confidence: asStringArray(raw.high_confidence?.tokens),
      medium_confidence: asStringArray(raw.medium_confidence?.tokens),
      context_dependent: asStringArray(raw.context_dependent?.tokens),
      phrases: asStringArray(raw.phrases?.tokens),
      protected_words: asStringArray(raw.protected_words?.tokens),
      scoring: { ...DEFAULT_SCORING, ...(raw.scoring ?? {}) } as ScoringConfig,
    };
    logger.info('Filler lexicon loaded', {
      path: lexPath,
      high: cached.high_confidence.length,
      medium: cached.medium_confidence.length,
      context: cached.context_dependent.length,
      phrases: cached.phrases.length,
      protected: cached.protected_words.length,
    });
    return cached;
  } catch (err) {
    logger.warn('Filler lexicon load failed, using empty', {
      path: lexPath,
      error: (err as Error).message,
    });
    cached = { ...EMPTY_LEXICON };
    return cached;
  }
}

/** 테스트/리셋용 */
export function _resetLexiconCache(): void {
  cached = null;
}
