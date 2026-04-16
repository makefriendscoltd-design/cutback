import { Caption, createLogger } from '@cutback/shared';
import fs from 'fs/promises';

const logger = createLogger('srt-generator');

/**
 * 초를 SRT 타임코드로 변환
 * SRT 포맷: HH:MM:SS,mmm
 */
function toSRTTimecode(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);

  return [
    String(h).padStart(2, '0'),
    ':',
    String(m).padStart(2, '0'),
    ':',
    String(s).padStart(2, '0'),
    ',',
    String(ms).padStart(3, '0'),
  ].join('');
}

/**
 * Caption 배열을 SRT 문자열로 변환
 */
export function generateSRT(captions: Caption[]): string {
  const sorted = [...captions].sort((a, b) => a.start - b.start);

  const lines: string[] = [];

  sorted.forEach((caption, index) => {
    lines.push(String(index + 1));
    lines.push(
      `${toSRTTimecode(caption.start)} --> ${toSRTTimecode(caption.end)}`
    );

    // 사용자 요구: 자막은 항상 한 줄로만 출력. 줄바꿈을 절대 넣지 않는다.
    // (CapCut에서 자막 폭 자동 줄바꿈은 사용자가 원하면 직접 활성화)
    const text = caption.text.replace(/\s*\n\s*/g, ' ').trim();
    lines.push(text);
    lines.push('');
  });

  logger.info('SRT generated', { captionCount: sorted.length });
  return lines.join('\n');
}

/**
 * SRT 파일로 저장 (UTF-8 BOM 포함 - CapCut 호환)
 */
export async function saveSRT(
  captions: Caption[],
  outputPath: string
): Promise<void> {
  const content = generateSRT(captions);
  // BOM 추가 (CapCut 한국어 인코딩 호환)
  const bom = '\uFEFF';
  await fs.writeFile(outputPath, bom + content, 'utf-8');
  logger.info('SRT saved', { path: outputPath });
}
