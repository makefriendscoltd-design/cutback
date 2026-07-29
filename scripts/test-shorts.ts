/**
 * Shorts Composer (Mode C) 테스트 스크립트
 *
 * 사용법:
 *   tsx scripts/test-shorts.ts [옵션] <clip1.mp4> <clip2.mp4> ...
 *
 * 옵션:
 *   --script "자막 텍스트"     음절 단위 빠른 템포 자막
 *   --voiceover vo.mp3        보이스오버 (총 길이 = 오디오 길이)
 *   --bgm bgm.mp3             배경음악
 *   --out out.mp4             출력 경로 (기본 ./shorts-output.mp4)
 *   --res fhd|4k              해상도 (기본 fhd = 1080x1920)
 *   --font <id>               pretendard-extrabold | pretendard-bold | suit-bold
 *   --clip-min 1.0            클립당 최소 길이(초)
 *   --clip-max 2.5            클립당 최대 길이(초)
 *   --tempo 6                 초당 음절 수 (음성 없을 때)
 *
 * 예시:
 *   tsx scripts/test-shorts.ts --script "집에서 할 수 있는 세가지 운동. 첫째 플랭크." --res 4k a.mp4 b.mp4 c.mp4
 */

import { ShortsComposer, listFonts } from '../packages/shorts-composer/src/index.js';
import type { ShortsCompositionSpec, ShortsResolution } from '../packages/shorts-composer/src/index.js';
import path from 'path';

function parseArgs(argv: string[]) {
  const opts: Record<string, string> = {};
  const clips: string[] = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      opts[a.slice(2)] = argv[++i];
    } else {
      clips.push(a);
    }
  }
  return { opts, clips };
}

async function main() {
  const { opts, clips } = parseArgs(process.argv.slice(2));

  if (clips.length === 0) {
    console.error('Usage: tsx scripts/test-shorts.ts [--script "..."] [--voiceover vo.mp3] [--res 4k] <clip1.mp4> ...');
    console.error('Fonts:', listFonts().map((f) => `${f.id}${f.available ? '' : ' (미다운로드)'}`).join(', '));
    process.exit(1);
  }

  const spec: ShortsCompositionSpec = {
    clips,
    script: opts['script'],
    voiceoverPath: opts['voiceover'],
    bgmPath: opts['bgm'],
    outputPath: path.resolve(opts['out'] ?? 'shorts-output.mp4'),
    resolution: (opts['res'] as ShortsResolution) ?? 'fhd',
    clipDuration: {
      min: Number(opts['clip-min'] ?? 1.0),
      max: Number(opts['clip-max'] ?? 2.5),
    },
    subtitleMode: (opts['subtitle-mode'] as 'burn' | 'srt' | 'both') ?? undefined,
    subtitle: {
      fontId: opts['font'],
      syllablesPerSecond: opts['tempo'] ? Number(opts['tempo']) : undefined,
    },
  };

  console.log('🎬 Shorts Composer 테스트 시작');
  console.log('클립:', clips.join(', '));
  if (spec.script) console.log('자막:', spec.script.slice(0, 60));
  if (spec.voiceoverPath) console.log('보이스오버:', spec.voiceoverPath);
  console.log('출력:', spec.outputPath, `(${spec.resolution})`);
  console.log('');

  const composer = new ShortsComposer();
  const started = Date.now();
  let lastMsg = '';
  const result = await composer.compose(spec, (p) => {
    const msg = `[${p.stage}] ${Math.round(p.progress * 100)}% ${p.message}`;
    if (msg !== lastMsg) {
      process.stdout.write(`\r${msg}          `);
      lastMsg = msg;
    }
  });

  console.log('\n');
  console.log('✅ 완료:', result.outputPath);
  console.log(`   ${result.width}x${result.height}, ${result.durationSec.toFixed(1)}초`);
  console.log(`   세그먼트 ${result.segmentCount}개, 자막 이벤트 ${result.subtitleEventCount}개`);
  if (result.srtPath) console.log(`   SRT: ${result.srtPath}`);
  console.log(`   소요시간 ${((Date.now() - started) / 1000).toFixed(1)}초`);
}

main().catch((err) => {
  console.error('\n❌ 실패:', err.message);
  process.exit(1);
});
