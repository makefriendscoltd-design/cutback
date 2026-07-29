/**
 * SentenceSegmenter
 *
 * Word-level transcript → 문장 단위 세그먼트 생성
 */

import type { Word, Sentence, SentenceTimeline } from '@cutback/shared';
import { v4 as uuidv4 } from 'uuid';

export class SentenceSegmenter {
  /**
   * Word-level transcript를 문장 단위로 세그먼트
   */
  segmentBySentence(
    words: Word[],
    language: string = 'ko'
  ): SentenceTimeline {
    if (words.length === 0) {
      return {
        sentences: [],
        totalDuration: 0,
        language,
        source: 'stt',
      };
    }

    const sentences: Sentence[] = [];
    let currentWords: Word[] = [];
    let sentenceStart = words[0].start;

    for (let i = 0; i < words.length; i++) {
      const word = words[i];
      currentWords.push(word);

      // 문장 종료 감지:
      // 1. 마침표, 물음표, 느낌표로 끝나는 경우
      // 2. 긴 pause (1초 이상) 다음
      // 3. 마지막 단어
      const isLastWord = i === words.length - 1;
      const nextWord = isLastWord ? null : words[i + 1];
      const endsWithPunctuation = /[.?!。？！]$/.test(word.text);
      const longPause = nextWord && (nextWord.start - word.end) > 1.0;

      if (endsWithPunctuation || longPause || isLastWord) {
        const text = currentWords.map((w) => w.text).join(' ');
        const start = sentenceStart;
        const end = word.end;

        sentences.push({
          id: uuidv4(),
          text: text.trim(),
          start,
          end,
          duration: end - start,
          words: [...currentWords],
        });

        // 다음 문장 준비
        if (nextWord) {
          currentWords = [];
          sentenceStart = nextWord.start;
        }
      }
    }

    const totalDuration = words[words.length - 1].end;

    return {
      sentences,
      totalDuration,
      language,
      source: 'stt',
    };
  }

  /**
   * 긴 문장을 자막 표시에 적합한 크기로 추가 분할
   * (Phase 2 이상 - 현재는 스텁)
   */
  splitLongSentences(
    sentences: Sentence[],
    maxCharsPerSegment: number = 60
  ): Sentence[] {
    const result: Sentence[] = [];

    for (const sentence of sentences) {
      if (sentence.text.length <= maxCharsPerSegment) {
        result.push(sentence);
        continue;
      }

      // TODO: 자연스러운 지점(쉼표, 접속사)에서 분할
      // 지금은 단순히 원본 문장 유지
      result.push(sentence);
    }

    return result;
  }
}
