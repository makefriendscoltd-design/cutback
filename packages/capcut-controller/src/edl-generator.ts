import { CutDecision, createLogger } from '@cutback/shared';
import fs from 'fs/promises';

const logger = createLogger('edl-generator');

/**
 * Timecode 변환 (초 → HH:MM:SS:FF)
 * @param seconds 초 단위 시간
 * @param fps 프레임 레이트 (기본 30)
 */
function toTimecode(seconds: number, fps: number = 30): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const f = Math.floor((seconds % 1) * fps);

  return [
    String(h).padStart(2, '0'),
    String(m).padStart(2, '0'),
    String(s).padStart(2, '0'),
    String(f).padStart(2, '0'),
  ].join(':');
}

/**
 * CMX3600 EDL 포맷 생성
 *
 * Cut decisions에서 *유지할 구간*을 계산하여 EDL 생성.
 * EDL은 "이 구간을 사용하라"는 형식이므로,
 * 제거할 구간의 반전(gap)이 실제 EDL 이벤트가 됨.
 */
export function generateEDL(
  cutDecisions: CutDecision[],
  totalDuration: number,
  options: {
    title?: string;
    fps?: number;
    reelName?: string;
  } = {}
): string {
  const {
    title = 'Cutback Export',
    fps = 30,
    reelName = 'AX',
  } = options;

  const enabledCuts = cutDecisions
    .filter((c) => c.enabled)
    .sort((a, b) => a.start - b.start);

  // 유지할 구간 계산 (제거 구간의 반전)
  const keepSegments: Array<{ start: number; end: number }> = [];
  let cursor = 0;

  for (const cut of enabledCuts) {
    if (cut.start > cursor) {
      keepSegments.push({ start: cursor, end: cut.start });
    }
    cursor = Math.max(cursor, cut.end);
  }

  // 마지막 유지 구간
  if (cursor < totalDuration) {
    keepSegments.push({ start: cursor, end: totalDuration });
  }

  // EDL 헤더
  const lines: string[] = [
    `TITLE: ${title}`,
    `FCM: NON-DROP FRAME`,
    '',
  ];

  // EDL 이벤트 생성
  let recordCursor = 0;

  keepSegments.forEach((segment, index) => {
    const eventNum = String(index + 1).padStart(3, '0');
    const duration = segment.end - segment.start;

    const sourceIn = toTimecode(segment.start, fps);
    const sourceOut = toTimecode(segment.end, fps);
    const recordIn = toTimecode(recordCursor, fps);
    const recordOut = toTimecode(recordCursor + duration, fps);

    lines.push(
      `${eventNum}  ${reelName}    V     C        ${sourceIn} ${sourceOut} ${recordIn} ${recordOut}`
    );
    lines.push(
      `${eventNum}  ${reelName}    A     C        ${sourceIn} ${sourceOut} ${recordIn} ${recordOut}`
    );
    lines.push('');

    recordCursor += duration;
  });

  logger.info('EDL generated', {
    events: keepSegments.length,
    removedCuts: enabledCuts.length,
  });

  return lines.join('\n');
}

/**
 * EDL 파일로 저장
 */
export async function saveEDL(
  cutDecisions: CutDecision[],
  totalDuration: number,
  outputPath: string,
  options?: { title?: string; fps?: number }
): Promise<void> {
  const content = generateEDL(cutDecisions, totalDuration, options);
  await fs.writeFile(outputPath, content, 'utf-8');
  logger.info('EDL saved', { path: outputPath });
}
