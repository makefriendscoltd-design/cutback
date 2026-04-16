import {
  Word,
  Transcript,
  CutDecision,
  FillerWordParams,
  KOREAN_FILLER_WORDS,
  createLogger,
} from '@cutback/shared';
import { v4 as uuidv4 } from 'uuid';
import { loadFillerLexicon, type FillerLexicon, type ScoringConfig } from './filler-lexicon';

const logger = createLogger('filler-detector');

// ─── Normalization ──────────────────────────────────────────────────

/**
 * Whisper 가 한국어 filler 를 뽑을 때 종종 문장부호/물결/말줄임표가 붙고
 * ('어...', '음,', '어~') 같은 음절을 길게 늘여 적기도 한다('어어어어').
 *
 * - \p{L}\p{N} 외 전부 제거 (마침표, 쉼표, 물결, 말줄임, 따옴표, 공백)
 * - 같은 글자 3회+ 연속 → 2회로 축약
 * - lowercase
 *
 * 사전과 단어 양쪽에 동일 정규화를 적용해 매칭 견고화.
 */
export function normalizeFillerToken(text: string): string {
  if (!text) return '';
  let cleaned = text.replace(/[^\p{L}\p{N}]+/gu, '');
  cleaned = cleaned.replace(/(.)\1{2,}/gu, '$1$1');
  return cleaned.toLowerCase();
}

// ─── Public types ───────────────────────────────────────────────────

export type FillerTier =
  | 'high_confidence'
  | 'medium_confidence'
  | 'context_dependent'
  | 'phrase';

export interface FillerWordMatch {
  /** 단일 단어 또는 phrase 의 첫 단어 */
  word: Word;
  /** phrase 매칭이면 마지막 단어 (start..end 범위 계산용) */
  endWord: Word;
  tier: FillerTier;
  rawText: string;
  normalized: string;
  baseScore: number;
  confidence: number;
  factors: string[];
  removal_recommendation: boolean;
  reviewRequired: boolean;
}

// ─── Tier base scores ───────────────────────────────────────────────

const TIER_BASE_SCORE: Record<FillerTier, number> = {
  high_confidence: 0.95,
  phrase: 0.9,
  medium_confidence: 0.6,
  context_dependent: 0.4,
};

// ─── Detector ───────────────────────────────────────────────────────

export class FillerDetector {
  private lexicon: FillerLexicon;
  private highSet: Set<string>;
  private mediumSet: Set<string>;
  private contextSet: Set<string>;
  private protectedSet: Set<string>;
  /** phrase 정규화 토큰 배열 (각 phrase 는 토큰 배열) */
  private phraseTokens: string[][];

  constructor(customFillers?: string[]) {
    this.lexicon = loadFillerLexicon();

    // Lexicon JSON 이 비어 있으면 (파일 못 찾았거나 깨졌으면)
    // 기존 KOREAN_FILLER_WORDS 로 fallback. 절대 빈 detector 가 되지 않게.
    const high =
      this.lexicon.high_confidence.length > 0
        ? this.lexicon.high_confidence
        : KOREAN_FILLER_WORDS.high_confidence;
    const medium =
      this.lexicon.medium_confidence.length > 0
        ? this.lexicon.medium_confidence
        : KOREAN_FILLER_WORDS.medium_confidence;
    const context =
      this.lexicon.context_dependent.length > 0
        ? this.lexicon.context_dependent
        : KOREAN_FILLER_WORDS.context_dependent;

    const allHigh = [...high, ...(customFillers ?? [])];

    this.highSet = new Set(allHigh.map(normalizeFillerToken).filter(Boolean));
    this.mediumSet = new Set(medium.map(normalizeFillerToken).filter(Boolean));
    this.contextSet = new Set(context.map(normalizeFillerToken).filter(Boolean));
    this.protectedSet = new Set(
      this.lexicon.protected_words.map(normalizeFillerToken).filter(Boolean)
    );
    this.phraseTokens = this.lexicon.phrases
      .map((p) => p.split(/\s+/).map(normalizeFillerToken).filter(Boolean))
      .filter((arr) => arr.length >= 2);
  }

  // ─── Tier classification ──────────────────────────────────────────

  private classifyToken(normalized: string): FillerTier | null {
    if (!normalized) return null;
    // protected 우선 - 의미어는 절대 filler 후보에서 제외
    if (this.protectedSet.has(normalized)) return null;
    if (this.highSet.has(normalized)) return 'high_confidence';
    if (this.mediumSet.has(normalized)) return 'medium_confidence';
    if (this.contextSet.has(normalized)) return 'context_dependent';
    return null;
  }

  // ─── Confidence scoring ──────────────────────────────────────────

  /**
   * Context multiplier 적용. 모든 multiplier 는 곱연산.
   * 결과는 0..1 클램프 (이론상 1 초과 가능 → cap).
   */
  private scoreWithContext(args: {
    tier: FillerTier;
    word: Word;
    endWord: Word;
    allWords: Word[];
    index: number;
    recentMatchTimestamps: Map<string, number[]>;
    normalized: string;
    scoring: ScoringConfig;
  }): { confidence: number; factors: string[] } {
    const { tier, word, endWord, allWords, index, recentMatchTimestamps, normalized, scoring } = args;

    const base = TIER_BASE_SCORE[tier];
    const m = scoring.context_multipliers;
    let factor = 1.0;
    const factors: string[] = [];

    // 단어 길이
    const dur = endWord.end - word.start;
    if (dur <= m.very_short_word.max_dur_sec) {
      factor *= m.very_short_word.factor;
      factors.push('very_short_word');
    } else if (dur <= m.isolated_short_word.max_dur_sec) {
      factor *= m.isolated_short_word.factor;
      factors.push('isolated_short_word');
    }

    // 앞쪽 무음
    if (index > 0) {
      const prev = allWords[index - 1];
      const gap = word.start - prev.end;
      if (gap >= m.preceding_silence_long.min_sec) {
        factor *= m.preceding_silence_long.factor;
        factors.push('preceding_silence_long');
      } else if (gap >= m.preceding_silence_short.min_sec) {
        factor *= m.preceding_silence_short.factor;
        factors.push('preceding_silence_short');
      }
    }

    // 뒤쪽 무음
    const nextIdx = index + (endWord === word ? 1 : 2); // phrase 면 +2
    if (nextIdx < allWords.length) {
      const next = allWords[nextIdx];
      const gap = next.start - endWord.end;
      if (gap >= m.following_silence_long.min_sec) {
        factor *= m.following_silence_long.factor;
        factors.push('following_silence_long');
      }
    }

    // 문장 시작/끝 (간이 휴리스틱: 앞쪽 무음 ≥ 0.6초면 sentence start)
    const isSentenceStart =
      index === 0 ||
      (index > 0 && word.start - allWords[index - 1].end >= 0.6);
    const isSentenceEnd =
      nextIdx >= allWords.length ||
      (nextIdx < allWords.length && allWords[nextIdx].start - endWord.end >= 0.6);

    if (isSentenceStart) {
      factor *= m.at_sentence_start.factor;
      factors.push('at_sentence_start');
    } else if (isSentenceEnd) {
      factor *= m.at_sentence_end.factor;
      factors.push('at_sentence_end');
    }

    // 반복 출현 (최근 N초 내 동일 normalized 가 이미 detect 됨)
    const recent = recentMatchTimestamps.get(normalized) ?? [];
    const windowStart = word.start - m.repeated_within_sec.window_sec;
    const repeats = recent.filter((t) => t >= windowStart).length;
    if (repeats > 0) {
      factor *= m.repeated_within_sec.factor;
      factors.push(`repeated_within_${m.repeated_within_sec.window_sec}s`);
    }

    const confidence = Math.max(0, Math.min(1, base * factor));
    return { confidence, factors };
  }

  // ─── Main detect ─────────────────────────────────────────────────

  detectFillers(transcript: Transcript, params: FillerWordParams): FillerWordMatch[] {
    const { words } = transcript;
    const matches: FillerWordMatch[] = [];

    if (words.length === 0) return matches;

    const scoring = this.lexicon.scoring;
    const threshold =
      params.confidence_threshold ?? scoring.default_threshold;
    const reviewLow = scoring.review_band[0];
    const minDurationMs = params.min_removable_duration_ms ?? 80; // 기본 80ms 미만은 보호

    // Pre-normalize all words
    const normalized: string[] = words.map((w) => normalizeFillerToken(w.text));

    const recent: Map<string, number[]> = new Map();

    let i = 0;
    while (i < words.length) {
      const word = words[i];
      const norm = normalized[i];

      if (!norm) {
        i++;
        continue;
      }

      // Protected words (음악, 어제 등) 은 강제 skip
      if (this.protectedSet.has(norm)) {
        i++;
        continue;
      }

      // Phrase 매칭 우선 (긴 매칭 우선)
      const phraseMatch = this.matchPhraseAt(normalized, i);
      if (phraseMatch) {
        const endWord = words[i + phraseMatch.length - 1];
        const dur = endWord.end - word.start;
        if (dur * 1000 < minDurationMs) {
          // 너무 짧은 phrase 도 cut 하면 부자연. skip
          i += phraseMatch.length;
          continue;
        }

        const phraseNorm = phraseMatch.tokens.join(' ');
        const { confidence, factors } = this.scoreWithContext({
          tier: 'phrase',
          word,
          endWord,
          allWords: words,
          index: i,
          recentMatchTimestamps: recent,
          normalized: phraseNorm,
          scoring,
        });

        const reviewRequired = confidence < threshold && confidence >= reviewLow;
        const remove = confidence >= threshold;

        matches.push({
          word,
          endWord,
          tier: 'phrase',
          rawText: words.slice(i, i + phraseMatch.length).map((w) => w.text).join(' '),
          normalized: phraseNorm,
          baseScore: TIER_BASE_SCORE.phrase,
          confidence,
          factors,
          removal_recommendation: remove,
          reviewRequired,
        });

        recent.set(phraseNorm, [...(recent.get(phraseNorm) ?? []), word.start]);
        i += phraseMatch.length;
        continue;
      }

      // 단일 토큰 매칭
      const tier = this.classifyToken(norm);
      if (!tier) {
        i++;
        continue;
      }

      const dur = word.end - word.start;
      if (dur * 1000 < minDurationMs) {
        // 80ms 미만 cut 은 들리지도 않게 짧고 오히려 호흡 끊음
        i++;
        continue;
      }

      const { confidence, factors } = this.scoreWithContext({
        tier,
        word,
        endWord: word,
        allWords: words,
        index: i,
        recentMatchTimestamps: recent,
        normalized: norm,
        scoring,
      });

      // removal_strength 보정
      const adjusted = applyStrengthAdjust(confidence, tier, params.removal_strength);
      const reviewRequired = adjusted < threshold && adjusted >= reviewLow;
      const remove = adjusted >= threshold;

      matches.push({
        word,
        endWord: word,
        tier,
        rawText: word.text,
        normalized: norm,
        baseScore: TIER_BASE_SCORE[tier],
        confidence: adjusted,
        factors,
        removal_recommendation: remove,
        reviewRequired,
      });

      recent.set(norm, [...(recent.get(norm) ?? []), word.start]);
      i++;
    }

    const recommended = matches.filter((m) => m.removal_recommendation).length;
    const review = matches.filter((m) => m.reviewRequired).length;
    logger.info('Filler detection completed', {
      totalMatches: matches.length,
      autoRemove: recommended,
      review,
      threshold,
    });

    return matches;
  }

  /**
   * 위치 i 에서 시작하는 가장 긴 phrase 매칭 반환 (정규화된 토큰 기준).
   * 매칭된 토큰 배열과 길이 반환, 없으면 null.
   */
  private matchPhraseAt(
    normalized: string[],
    i: number
  ): { tokens: string[]; length: number } | null {
    // 길이 내림차순
    const sorted = [...this.phraseTokens].sort((a, b) => b.length - a.length);
    for (const tokens of sorted) {
      if (i + tokens.length > normalized.length) continue;
      let ok = true;
      for (let k = 0; k < tokens.length; k++) {
        if (normalized[i + k] !== tokens[k]) {
          ok = false;
          break;
        }
      }
      if (ok) return { tokens, length: tokens.length };
    }
    return null;
  }

  toCutDecisions(matches: FillerWordMatch[]): CutDecision[] {
    return matches
      .filter((m) => m.removal_recommendation || m.reviewRequired)
      .map((m) => {
        const reasonParts = [
          `filler[${m.tier}] '${m.rawText}'`,
          m.factors.length ? `(${m.factors.join(', ')})` : '',
          `score=${m.confidence.toFixed(2)}`,
        ].filter(Boolean);

        return {
          id: uuidv4(),
          type: 'filler_word' as const,
          start: m.word.start,
          end: m.endWord.end,
          duration: m.endWord.end - m.word.start,
          confidence: m.confidence,
          reason: reasonParts.join(' '),
          reviewRequired: m.reviewRequired,
          metadata: {
            filler_text: m.rawText,
            filler_tier: m.tier,
            score_factors: m.factors,
          },
          // review band 인 항목은 enabled=false 로 들어와야 자동 적용 안 됨
          enabled: m.removal_recommendation && !m.reviewRequired,
          user_approved: false,
        };
      });
  }
}

// ─── Strength adjust ────────────────────────────────────────────────

/**
 * removal_strength 가 conservative 면 medium/context 점수를 깎고,
 * aggressive 면 높임. high_confidence 는 영향 없음 (어차피 거의 1).
 */
function applyStrengthAdjust(
  confidence: number,
  tier: FillerTier,
  strength: FillerWordParams['removal_strength']
): number {
  if (tier === 'high_confidence' || tier === 'phrase') return confidence;
  if (strength === 'conservative') {
    return tier === 'context_dependent' ? confidence * 0.7 : confidence * 0.85;
  }
  if (strength === 'aggressive') {
    return Math.min(1, confidence * 1.15);
  }
  return confidence;
}

// ─── Convenience ────────────────────────────────────────────────────

export async function detectFillers(
  transcript: Transcript,
  params: FillerWordParams
): Promise<CutDecision[]> {
  const detector = new FillerDetector(params.custom_fillers);
  const matches = detector.detectFillers(transcript, params);
  return detector.toCutDecisions(matches);
}
