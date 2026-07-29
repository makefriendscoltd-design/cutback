/**
 * VoiceoverEngine
 *
 * 보이스오버/스크립트 처리 통합 엔진
 */

import type { Transcript, SentenceTimeline } from '@cutback/shared';
import { SentenceSegmenter } from './sentence-segmenter.js';
import { ScriptParser, type ScriptParseOptions } from './script-parser.js';

export class VoiceoverEngine {
  private sentenceSegmenter: SentenceSegmenter;
  private scriptParser: ScriptParser;

  constructor() {
    this.sentenceSegmenter = new SentenceSegmenter();
    this.scriptParser = new ScriptParser();
  }

  /**
   * STT transcript → SentenceTimeline 변환
   */
  fromTranscript(transcript: Transcript): SentenceTimeline {
    return this.sentenceSegmenter.segmentBySentence(
      transcript.words,
      transcript.language
    );
  }

  /**
   * 스크립트 텍스트 → SentenceTimeline 변환
   */
  fromScript(
    scriptText: string,
    language: string = 'ko',
    options?: ScriptParseOptions
  ): SentenceTimeline {
    return this.scriptParser.parseScript(scriptText, language, options);
  }

  /**
   * SentenceTimeline을 SRT 자막 형식으로 내보내기
   */
  exportToSRT(timeline: SentenceTimeline): string {
    let srt = '';

    timeline.sentences.forEach((sentence, index) => {
      const startTime = this.formatSRTTime(sentence.start);
      const endTime = this.formatSRTTime(sentence.end);

      srt += `${index + 1}\n`;
      srt += `${startTime} --> ${endTime}\n`;
      srt += `${sentence.text}\n\n`;
    });

    return srt;
  }

  /**
   * 초 단위 시간을 SRT 타임코드로 변환 (HH:MM:SS,mmm)
   */
  private formatSRTTime(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const millis = Math.floor((seconds % 1) * 1000);

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')},${String(millis).padStart(3, '0')}`;
  }
}
