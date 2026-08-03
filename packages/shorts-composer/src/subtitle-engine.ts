/**
 * 음절 단위 자막 엔진
 *
 * 스크립트를 음절 덩어리(기본 3음절)로 쪼개서 빠른 템포의 숏폼 자막 이벤트를 만들고,
 * libass 로 하드번 가능한 ASS 문자열을 생성한다.
 *
 * 타이밍 소스 우선순위:
 *  1) wordTimings (STT 단어 타임스탬프) — 보이스오버와 정확히 싱크
 *  2) totalDuration (보이스오버 길이만 아는 경우) — 음절 비례 배분
 *  3) 템포 (음성 없음) — 초당 음절 수로 순차 배치
 */

import type {
  SubtitleChunkMode,
  SubtitleEvent,
  SubtitleStyleOptions,
  WordTiming,
} from './types.js';
import { getFont } from './fonts.js';

/** 한 이벤트의 최소/최대 노출 시간 (초) — 가독성 하한, 늘어짐 상한 */
const MIN_EVENT_SEC = 0.18;
const MAX_EVENT_SEC = 1.6;

/**
 * 문장 모드에서 한 줄에 허용하는 최대 음절 수.
 * PlayResX 1080, 좌우 마진 60, fontSize 96(≈전각 1글자≈96px) 기준
 * 대략 9글자면 864px < 960px 사용폭 → 두 번째 줄로 넘어가지 않는다.
 */
const MAX_LINE_SYLLABLES = 9;

const HANGUL_SYLLABLE = /[가-힣]/;

/** 자막 길이 가중치: 한글 음절 1, 공백 0, 그 외 문자 0.5 */
export function countSyllables(text: string): number {
  let n = 0;
  for (const ch of text) {
    if (/\s/.test(ch)) continue;
    n += HANGUL_SYLLABLE.test(ch) ? 1 : 0.5;
  }
  return Math.max(n, 0.5);
}

/**
 * 스크립트 → 음절 덩어리 배열.
 * 단어(공백 기준) 경계를 최대한 지키면서 chunkSyllables 를 채우고,
 * 한 단어가 너무 길면 음절 단위로 강제 분할한다.
 * 문장부호(. ! ? 줄바꿈)에서는 무조건 끊는다.
 */
export function chunkScript(script: string, chunkSyllables = 3): string[] {
  const chunks: string[] = [];
  // 문장 경계 먼저 분리 (부호는 앞 덩어리에 붙임)
  const sentences = script
    .split(/(?<=[.!?…])\s+|\n+/)
    .map((s) => s.trim())
    .filter(Boolean);

  for (const sentence of sentences) {
    const words = sentence.split(/\s+/).filter(Boolean);
    let current = '';

    const flush = () => {
      if (current) {
        chunks.push(current);
        current = '';
      }
    };

    for (const word of words) {
      const wordSyl = countSyllables(word);

      // 단어 자체가 한 덩어리 한도를 크게 넘으면 음절 단위로 쪼갬
      if (wordSyl > chunkSyllables + 1) {
        flush();
        const chars = Array.from(word);
        let piece = '';
        for (const ch of chars) {
          piece += ch;
          if (countSyllables(piece) >= chunkSyllables) {
            chunks.push(piece);
            piece = '';
          }
        }
        if (piece) chunks.push(piece);
        continue;
      }

      const combined = current ? `${current} ${word}` : word;
      if (countSyllables(combined) > chunkSyllables && current) {
        flush();
        current = word;
      } else {
        current = combined;
      }
    }
    flush();
  }
  return chunks;
}

/**
 * 문장 단위 청킹.
 * 문장부호(. ! ? … 줄바꿈)로 끊어 문장을 통째로 유지하되,
 * 한 문장이 한 줄 폭(maxLine 음절)을 넘으면 단어 경계로 "균등" 분할한다.
 * (ASS WrapStyle=2 라 자동 줄바꿈이 없으므로, 길면 화면 밖으로 넘침 → 여기서 미리 잘라 방지)
 */
export function chunkBySentence(script: string, maxLine = MAX_LINE_SYLLABLES): string[] {
  const sentences = script
    .split(/(?<=[.!?…])\s+|\n+/)
    .map((s) => s.trim())
    .filter(Boolean);

  const chunks: string[] = [];
  for (const sentence of sentences) {
    if (countSyllables(sentence) <= maxLine) {
      chunks.push(sentence);
      continue;
    }
    // 긴 문장: 줄 수를 먼저 정하고(ceil) 줄당 목표 음절을 균등하게 잡아 분배
    const words = sentence.split(/\s+/).filter(Boolean);
    const total = countSyllables(sentence);
    const lineCount = Math.ceil(total / maxLine);
    const target = total / lineCount;
    let current = '';

    for (const word of words) {
      // 단어 하나가 한 줄 폭을 넘으면(URL·긴 영문 등) 음절 단위로 강제 분할
      if (countSyllables(word) > maxLine) {
        if (current) { chunks.push(current); current = ''; }
        let piece = '';
        for (const ch of Array.from(word)) {
          piece += ch;
          if (countSyllables(piece) >= maxLine) { chunks.push(piece); piece = ''; }
        }
        if (piece) current = piece;
        continue;
      }
      const combined = current ? `${current} ${word}` : word;
      if (
        current &&
        (countSyllables(combined) > maxLine || countSyllables(current) >= target)
      ) {
        chunks.push(current);
        current = word;
      } else {
        current = combined;
      }
    }
    if (current) chunks.push(current);
  }
  return chunks;
}

/** 끊기 옵션 → 실제 텍스트 덩어리 배열 (음절 모드 vs 문장 모드 분기) */
function chunkText(
  script: string,
  opts: { chunkMode?: SubtitleChunkMode; chunkSyllables?: number; maxLineSyllables?: number }
): string[] {
  if (opts.chunkMode === 'sentence') {
    return chunkBySentence(script, opts.maxLineSyllables ?? MAX_LINE_SYLLABLES);
  }
  return chunkScript(script, opts.chunkSyllables ?? 3);
}

/** 자막 빌더 공통 끊기 옵션 */
interface ChunkOpts {
  chunkMode?: SubtitleChunkMode;
  chunkSyllables?: number;
  maxLineSyllables?: number;
}

/** 템포 모드: 초당 음절 수 기준으로 순차 배치 */
export function buildTempoEvents(
  script: string,
  opts: ChunkOpts & { syllablesPerSecond?: number } = {}
): SubtitleEvent[] {
  const sps = opts.syllablesPerSecond ?? 6;
  const chunks = chunkText(script, opts);

  const events: SubtitleEvent[] = [];
  let t = 0;
  for (const text of chunks) {
    const dur = clamp(countSyllables(text) / sps, MIN_EVENT_SEC, MAX_EVENT_SEC);
    events.push({ text, start: t, end: t + dur });
    t += dur;
  }
  return events;
}

/** 총 길이만 아는 모드: 템포 이벤트를 totalDuration 에 맞게 스케일 */
export function buildScaledEvents(
  script: string,
  totalDuration: number,
  opts: ChunkOpts = {}
): SubtitleEvent[] {
  const events = buildTempoEvents(script, opts);
  if (events.length === 0) return events;
  const naturalEnd = events[events.length - 1].end;
  if (naturalEnd <= 0) return events;
  const scale = totalDuration / naturalEnd;
  return events.map((e) => ({
    text: e.text,
    start: e.start * scale,
    end: e.end * scale,
  }));
}

/**
 * 자막 이벤트 빌더 (통합).
 * 타이밍 소스 우선순위: wordTimings(STT) > voiceoverDur(비례) > 템포(음성 없음).
 * compose() 와 미리보기 IPC 가 동일 로직을 쓰도록 한 곳에 모음.
 */
export function buildSubtitleEvents(opts: {
  script?: string;
  wordTimings?: WordTiming[];
  voiceoverDur?: number;
  chunkMode?: SubtitleChunkMode;
  chunkSyllables?: number;
  maxLineSyllables?: number;
  syllablesPerSecond?: number;
}): SubtitleEvent[] {
  const subOpts = {
    chunkMode: opts.chunkMode,
    chunkSyllables: opts.chunkSyllables,
    maxLineSyllables: opts.maxLineSyllables,
    syllablesPerSecond: opts.syllablesPerSecond,
  };
  if (opts.wordTimings && opts.wordTimings.length > 0) {
    return buildTimedEvents(opts.wordTimings, subOpts);
  }
  if (!opts.script?.trim()) return [];
  if (opts.voiceoverDur !== undefined) {
    return buildScaledEvents(opts.script, opts.voiceoverDur, subOpts);
  }
  return buildTempoEvents(opts.script, subOpts);
}

/** STT 단어 타임스탬프 모드: 덩어리에 속한 단어들의 시작~끝을 그대로 사용 */
export function buildTimedEvents(
  wordTimings: WordTiming[],
  opts: ChunkOpts = {}
): SubtitleEvent[] {
  const sentenceMode = opts.chunkMode === 'sentence';
  // 문장 모드면 한 줄 폭까지 모으고 문장부호에서 끊는다. 아니면 음절 덩어리 크기.
  const cap = sentenceMode
    ? opts.maxLineSyllables ?? MAX_LINE_SYLLABLES
    : opts.chunkSyllables ?? 3;
  const events: SubtitleEvent[] = [];
  let group: WordTiming[] = [];
  let groupSyl = 0;

  const flush = () => {
    if (group.length === 0) return;
    events.push({
      text: group.map((w) => w.text).join(' '),
      start: group[0].start,
      end: group[group.length - 1].end,
    });
    group = [];
    groupSyl = 0;
  };

  for (const w of wordTimings) {
    const syl = countSyllables(w.text);
    if (groupSyl + syl > cap && group.length > 0) flush();
    group.push(w);
    groupSyl += syl;
    // 문장 모드: STT 텍스트가 문장부호로 끝나면 거기서 문장을 마감
    if (sentenceMode && /[.!?…]$/.test(w.text)) flush();
  }
  flush();
  return events;
}

// ---------------------------------------------------------------------------
// ASS 생성
// ---------------------------------------------------------------------------

function clamp(v: number, lo: number, hi: number): number {
  return Math.min(Math.max(v, lo), hi);
}

/** '#RRGGBB' → ASS '&H00BBGGRR' */
function toAssColor(hex: string): string {
  const m = /^#?([0-9a-fA-F]{6})$/.exec(hex);
  if (!m) throw new Error(`Invalid color: ${hex} (expected #RRGGBB)`);
  const rr = m[1].slice(0, 2);
  const gg = m[1].slice(2, 4);
  const bb = m[1].slice(4, 6);
  return `&H00${bb}${gg}${rr}`.toUpperCase();
}

function toAssTime(sec: number): string {
  const s = Math.max(0, sec);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const ss = Math.floor(s % 60);
  const cs = Math.floor((s * 100) % 100);
  return `${h}:${String(m).padStart(2, '0')}:${String(ss).padStart(2, '0')}.${String(cs).padStart(2, '0')}`;
}

function escapeAssText(text: string): string {
  return text.replace(/\\/g, '\\\\').replace(/\{/g, '(').replace(/\}/g, ')');
}

/**
 * ASS 자막 문자열 생성.
 * PlayRes 는 1080x1920 고정 — libass 가 실제 출력 해상도에 맞춰 스케일하므로
 * 4K 출력이어도 fontSize 등 스타일 값은 1080 기준으로 동일하게 쓰면 된다.
 */
export function generateAss(
  events: SubtitleEvent[],
  style: SubtitleStyleOptions = {}
): string {
  const font = getFont(style.fontId);
  const fontSize = style.fontSize ?? 96;
  const primary = toAssColor(style.primaryColor ?? '#FFFFFF');
  const outline = toAssColor(style.outlineColor ?? '#000000');
  const position = style.position ?? 'center';
  const popIn = style.popIn ?? true;

  // Alignment (numpad): 5 = 정중앙, 2 = 하단 중앙
  const alignment = position === 'center' ? 5 : 2;
  const marginV = position === 'center' ? 0 : 380;
  const boldFlag = font.bold ? -1 : 0;

  const header = `[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,${font.family},${fontSize},${primary},${primary},${outline},&H80000000,${boldFlag},0,0,0,100,100,0,0,1,7,0,${alignment},60,60,${marginV},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
`;

  const fx = popIn
    ? '{\\fad(40,20)\\fscx82\\fscy82\\t(0,70,\\fscx100\\fscy100)}'
    : '';

  const lines = events.map(
    (e) =>
      `Dialogue: 0,${toAssTime(e.start)},${toAssTime(e.end)},Caption,,0,0,0,,${fx}${escapeAssText(e.text)}`
  );

  return header + lines.join('\n') + '\n';
}

/** SRT 타임코드 'HH:MM:SS,mmm' */
function toSrtTime(sec: number): string {
  const s = Math.max(0, sec);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const ss = Math.floor(s % 60);
  const ms = Math.round((s - Math.floor(s)) * 1000);
  return (
    `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:` +
    `${String(ss).padStart(2, '0')},${String(ms).padStart(3, '0')}`
  );
}

/**
 * SRT 자막 문자열 생성 (캡컷 등에서 텍스트로 편집 가능한 sidecar).
 * 스타일 정보는 없음 — 캡컷 기본 자막 스타일로 표시됨.
 */
export function generateSrt(events: SubtitleEvent[]): string {
  return (
    events
      .map((e, i) => {
        return `${i + 1}\n${toSrtTime(e.start)} --> ${toSrtTime(e.end)}\n${e.text}`;
      })
      .join('\n\n') + '\n'
  );
}
