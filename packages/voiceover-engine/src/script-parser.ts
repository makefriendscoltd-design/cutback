/**
 * ScriptParser
 *
 * 스크립트 텍스트 파일 → SentenceTimeline 변환
 * (보이스오버 없이 텍스트만 있는 경우)
 */

import type { Sentence, SentenceTimeline } from '@cutback/shared';
import { v4 as uuidv4 } from 'uuid';

export interface ScriptParseOptions {
  /** 평균 읽기 속도 (words per minute) - 타이밍 추정용 */
  averageWPM?: number;
  /** 문장 간 pause (초) */
  pauseBetweenSentences?: number;
}

export class ScriptParser {
  private readonly defaultWPM = 150; // 한국어 평균 읽기 속도
  private readonly defaultPause = 0.3; // 문장 간 기본 pause

  /**
   * 스크립트 텍스트를 파싱하여 SentenceTimeline 생성
   */
  parseScript(
    scriptText: string,
    language: string = 'ko',
    options: ScriptParseOptions = {}
  ): SentenceTimeline {
    const wpm = options.averageWPM ?? this.defaultWPM;
    const pause = options.pauseBetweenSentences ?? this.defaultPause;

    // 문장 단위로 분할
    const rawSentences = this.splitIntoSentences(scriptText, language);

    // 각 문장의 타이밍 추정
    const sentences: Sentence[] = [];
    let currentTime = 0;

    for (const text of rawSentences) {
      const wordCount = this.countWords(text, language);
      const duration = (wordCount / wpm) * 60; // 초 단위

      sentences.push({
        id: uuidv4(),
        text: text.trim(),
        start: currentTime,
        end: currentTime + duration,
        duration,
        words: [], // 스크립트 파싱에서는 word-level 타임스탬프 없음
      });

      currentTime += duration + pause;
    }

    return {
      sentences,
      totalDuration: currentTime - pause, // 마지막 pause 제외
      language,
      source: 'script',
    };
  }

  /**
   * 텍스트를 문장 단위로 분할
   */
  private splitIntoSentences(text: string, language: string): string[] {
    // 줄바꿈으로 명시적 분할 우선 처리
    const lines = text.split('\n').map((line) => line.trim()).filter(Boolean);

    const sentences: string[] = [];

    for (const line of lines) {
      if (language === 'ko') {
        // 한국어: 마침표, 물음표, 느낌표로 분할
        const splits = line.split(/([.?!。？！])\s*/);
        let current = '';

        for (let i = 0; i < splits.length; i++) {
          const part = splits[i];
          if (!part) continue;

          if (/^[.?!。？！]$/.test(part)) {
            current += part;
            if (current.trim()) {
              sentences.push(current.trim());
            }
            current = '';
          } else {
            current += part;
          }
        }

        if (current.trim()) {
          sentences.push(current.trim());
        }
      } else {
        // 영어: 마침표/물음표/느낌표로 분할
        const splits = line.split(/([.?!])\s*/);
        let current = '';

        for (let i = 0; i < splits.length; i++) {
          const part = splits[i];
          if (!part) continue;

          if (/^[.?!]$/.test(part)) {
            current += part;
            if (current.trim()) {
              sentences.push(current.trim());
            }
            current = '';
          } else {
            current += part;
          }
        }

        if (current.trim()) {
          sentences.push(current.trim());
        }
      }
    }

    return sentences.filter(Boolean);
  }

  /**
   * 단어 개수 세기
   */
  private countWords(text: string, language: string): number {
    if (language === 'ko') {
      // 한국어: 음절 수로 추정 (공백 기준 분할)
      // 더 정확하려면 형태소 분석 필요
      return text.replace(/\s+/g, ' ').trim().split(' ').length;
    } else {
      // 영어: 공백 기준
      return text.split(/\s+/).filter(Boolean).length;
    }
  }
}
