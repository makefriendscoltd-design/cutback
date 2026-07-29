import {
  Word,
  Transcript,
  CutDecision,
  createLogger,
} from '@cutback/shared';
import { compareTwoStrings } from 'string-similarity';
import { v4 as uuidv4 } from 'uuid';

const logger = createLogger('retake-detector');

export interface RetakeMatch {
  /** 원본 (제거 대상) 구간의 단어들 */
  originalWords: Word[];
  /** 재촬영/재시도 (유지 대상) 구간의 단어들 */
  retakeWords: Word[];
  /** 텍스트 유사도 (0.0 ~ 1.0) */
  similarity: number;
  /** 그룹 ID */
  groupId: string;
}

export interface RetakeDetectorOptions {
  /** 유사도 임계값 (기본 0.6) */
  similarityThreshold?: number;
  /** 비교 윈도우 크기 - 단어 수 (기본 5) */
  windowSize?: number;
  /** 최대 gap 허용 시간 (초) - 이 이상 떨어지면 다른 구간 (기본 3.0) */
  maxGapSeconds?: number;
  /** 최소 단어 수 - 이 이하는 무시 (기본 2) */
  minWords?: number;
}

/**
 * Retake(재시도) 감지기
 *
 * 화자가 말을 더듬거나 문장을 다시 시작하는 패턴을 감지.
 * 이전 시도를 제거 대상으로 마킹하고, 마지막 시도만 유지.
 *
 * 감지 전략:
 * 1. 슬라이딩 윈도우로 인접 구간 텍스트 유사도 비교
 * 2. 유사도가 임계값 이상이면 retake 후보
 * 3. pause gap으로 문장 경계 판단
 * 4. 같은 retake 그룹에서 마지막 시도만 유지
 */
export class RetakeDetector {
  private options: Required<RetakeDetectorOptions>;

  constructor(options?: RetakeDetectorOptions) {
    this.options = {
      similarityThreshold: options?.similarityThreshold ?? 0.6,
      windowSize: options?.windowSize ?? 5,
      maxGapSeconds: options?.maxGapSeconds ?? 3.0,
      minWords: options?.minWords ?? 2,
    };
  }

  /**
   * Transcript에서 retake 패턴 감지
   */
  detectRetakes(transcript: Transcript): RetakeMatch[] {
    const { words } = transcript;
    if (words.length < this.options.minWords * 2) return [];

    const matches: RetakeMatch[] = [];
    const usedIndices = new Set<number>();

    // 1단계: pause 기반으로 구(phrase)를 분리
    const phrases = this.splitIntoPhrases(words);

    // 2단계: 인접 phrase 간 유사도 비교
    for (let i = 0; i < phrases.length - 1; i++) {
      if (this.isPhraseUsed(phrases[i], usedIndices)) continue;

      for (let j = i + 1; j < phrases.length; j++) {
        if (this.isPhraseUsed(phrases[j], usedIndices)) continue;

        const gap = phrases[j][0].start - phrases[i][phrases[i].length - 1].end;
        if (gap > this.options.maxGapSeconds) break;

        const textA = phrases[i].map((w) => w.text).join(' ');
        const textB = phrases[j].map((w) => w.text).join(' ');

        // 너무 짧은 phrase는 건너뛰기
        if (
          phrases[i].length < this.options.minWords ||
          phrases[j].length < this.options.minWords
        ) {
          continue;
        }

        const similarity = compareTwoStrings(textA, textB);

        if (similarity >= this.options.similarityThreshold) {
          const groupId = uuidv4();
          matches.push({
            originalWords: phrases[i],
            retakeWords: phrases[j],
            similarity,
            groupId,
          });

          // 원본 phrase의 인덱스를 사용됨으로 마킹
          const startIdx = words.indexOf(phrases[i][0]);
          for (let k = 0; k < phrases[i].length; k++) {
            usedIndices.add(startIdx + k);
          }
          break; // 이 phrase는 매칭 완료
        }
      }
    }

    logger.info('Retake detection completed', {
      phrasesAnalyzed: phrases.length,
      retakesFound: matches.length,
    });

    return matches;
  }

  /**
   * RetakeMatch를 CutDecision으로 변환
   * 원본(이전 시도)을 제거 대상으로 마킹
   */
  toCutDecisions(matches: RetakeMatch[]): CutDecision[] {
    return matches.map((match) => {
      const firstWord = match.originalWords[0];
      const lastWord = match.originalWords[match.originalWords.length - 1];

      return {
        id: uuidv4(),
        type: 'retake' as const,
        start: firstWord.start,
        end: lastWord.end,
        duration: lastWord.end - firstWord.start,
        confidence: match.similarity,
        reason: 'duplicate_phrase' as const,
        reasonText: `중복 발화 (similarity ${match.similarity.toFixed(2)})`,
        source: 'automatic' as const,
        metadata: {
          retake_group_id: match.groupId,
        },
        enabled: true,
        user_approved: false,
      };
    });
  }

  /**
   * pause 기반으로 단어들을 구(phrase)로 분리
   * pause가 0.5초 이상이면 새로운 phrase 시작
   */
  private splitIntoPhrases(words: Word[]): Word[][] {
    const phrases: Word[][] = [];
    let currentPhrase: Word[] = [];

    for (let i = 0; i < words.length; i++) {
      currentPhrase.push(words[i]);

      const nextWord = words[i + 1];
      if (!nextWord) {
        // 마지막 단어
        if (currentPhrase.length > 0) {
          phrases.push(currentPhrase);
        }
        break;
      }

      const gap = nextWord.start - words[i].end;

      // pause 또는 문장부호로 phrase 경계 판단
      const isSentenceEnd = /[.!?。？！]$/.test(words[i].text);

      if (gap > 0.5 || isSentenceEnd) {
        if (currentPhrase.length > 0) {
          phrases.push(currentPhrase);
          currentPhrase = [];
        }
      }
    }

    return phrases;
  }

  /**
   * phrase의 단어들이 이미 사용되었는지 확인
   */
  private isPhraseUsed(phrase: Word[], usedIndices: Set<number>): boolean {
    // 첫 번째 단어의 start time으로 판단
    return usedIndices.has(phrase[0].start as unknown as number);
  }
}

/**
 * 편의 함수: Retake 감지 및 Cut Decision 생성
 */
export async function detectRetakes(
  transcript: Transcript,
  options?: RetakeDetectorOptions
): Promise<CutDecision[]> {
  const detector = new RetakeDetector(options);
  const matches = detector.detectRetakes(transcript);
  return detector.toCutDecisions(matches);
}
