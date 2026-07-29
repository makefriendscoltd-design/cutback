/**
 * Mode A 롱폼 테스트 스크립트
 *
 * Electron 없이 파이프라인만 끝까지 돌려서
 * 단계별 소요 시간과 실패 지점을 찍는다.
 *
 * 사용법:
 *   tsx scripts/test-longform.ts <video.mp4> [presetId]
 *
 * 예시:
 *   tsx scripts/test-longform.ts "D:/영상/강의1화.mp4"
 *   tsx scripts/test-longform.ts lecture.mp4 vlog-style
 */

import { spawn } from 'child_process';
import path from 'path';
import { writeFile, mkdir } from 'fs/promises';
import { ProcessingPipeline } from '../packages/core/src/pipeline.js';
import { presetLoader } from '../packages/preset-manager/src/preset-loader.js';
import { generateSRT } from '../packages/capcut-controller/src/srt-generator.js';
import { resolveFfmpegPath } from '../packages/shared/src/utils/ffmpeg-resolver.js';
import type { Job } from '../packages/shared/src/types/index.js';

/** ffprobe 대신 ffmpeg -i 로 길이 파싱 (ffmpeg-static 에는 ffprobe 가 없음) */
function probeDuration(videoPath: string): Promise<number> {
  return new Promise((resolve) => {
    const bin = resolveFfmpegPath();
    if (!bin) return resolve(0);
    const proc = spawn(bin, ['-i', videoPath]);
    let stderr = '';
    proc.stderr.on('data', (d: Buffer) => (stderr += d.toString()));
    proc.on('close', () => {
      const m = stderr.match(/Duration:\s*(\d+):(\d+):(\d+\.?\d*)/);
      if (!m) return resolve(0);
      resolve(+m[1] * 3600 + +m[2] * 60 + +m[3]);
    });
    proc.on('error', () => resolve(0));
  });
}

const fmt = (s: number) => {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  return h > 0 ? `${h}h ${m}m ${sec}s` : m > 0 ? `${m}m ${sec}s` : `${sec}s`;
};

async function main() {
  const [videoPath, presetId = 'info-talking-head'] = process.argv.slice(2);

  if (!videoPath) {
    console.error('Usage: tsx scripts/test-longform.ts <video.mp4> [presetId]');
    console.error('');
    console.error('presetId: info-talking-head (기본) | vlog-style | ad-short-form');
    process.exit(1);
  }

  const absVideo = path.resolve(videoPath);
  const outDir = path.resolve('longform-test-output');
  await mkdir(outDir, { recursive: true });

  console.log('🎬 Mode A 롱폼 테스트');
  console.log('영상   :', absVideo);
  console.log('프리셋 :', presetId);

  const duration = await probeDuration(absVideo);
  console.log('길이   :', duration > 0 ? fmt(duration) : '(측정 실패)');
  console.log('');

  presetLoader.setBaseDir(path.resolve('presets'));
  const preset = await presetLoader.load(presetId);

  const job: Job = {
    id: 'longform-test',
    videoPath: absVideo,
    presetId,
    status: 'PROCESSING' as never,
    progress: 0,
    createdAt: new Date(),
    editMode: 'mode-a',
  };

  // 단계별 타이밍 기록
  const t0 = Date.now();
  let lastStage = '';
  let lastStageStart = t0;
  const timings: Array<{ stage: string; seconds: number }> = [];

  const closeStage = () => {
    if (!lastStage) return;
    const sec = (Date.now() - lastStageStart) / 1000;
    timings.push({ stage: lastStage, seconds: sec });
    console.log(`   └─ ${lastStage} 완료 (${fmt(sec)})`);
  };

  const pipeline = new ProcessingPipeline();

  let results;
  try {
    results = await pipeline.execute(job, preset, (stage, progress, detail) => {
      if (stage !== lastStage) {
        closeStage();
        lastStage = stage;
        lastStageStart = Date.now();
        console.log(`\n▶ [${String(progress).padStart(3)}%] ${stage}`);
      }
      if (detail) console.log(`      ${detail}`);
    });
    closeStage();
  } catch (err) {
    closeStage();
    console.error('\n❌ 파이프라인 실패');
    console.error('   실패 단계 :', lastStage || '(시작 전)');
    console.error('   경과 시간 :', fmt((Date.now() - t0) / 1000));
    console.error('   에러      :', (err as Error).message);
    console.error((err as Error).stack);
    process.exit(1);
  }

  const total = (Date.now() - t0) / 1000;

  // 결과 저장
  const srt = generateSRT(results.captions ?? []);
  await writeFile(path.join(outDir, 'captions.srt'), srt, 'utf-8');
  await writeFile(
    path.join(outDir, 'results.json'),
    JSON.stringify(results, null, 2),
    'utf-8'
  );

  const stats = results.statistics;
  console.log('\n' + '='.repeat(56));
  console.log('✅ 완료');
  console.log('='.repeat(56));
  console.log('총 소요     :', fmt(total));
  if (duration > 0) {
    console.log(`실시간 배속 : ${(duration / total).toFixed(2)}x (1.0 미만이면 영상보다 느림)`);
  }
  console.log('');
  console.log('단계별 소요 (느린 순):');
  for (const t of [...timings].sort((a, b) => b.seconds - a.seconds)) {
    const pct = ((t.seconds / total) * 100).toFixed(0);
    console.log(`  ${t.stage.padEnd(16)} ${fmt(t.seconds).padStart(10)}  ${pct.padStart(3)}%`);
  }
  console.log('');
  if (stats) {
    console.log('편집 결과:');
    console.log(`  원본 ${fmt(stats.original_duration)} → 편집 후 ${fmt(stats.edited_duration)}`);
    console.log(`  무음 ${stats.silence_removed} / 말버릇 ${stats.fillers_removed} / 재시도 ${stats.retakes_removed}`);
    console.log(`  총 컷 ${stats.total_cuts}개 (분당 ${stats.cut_frequency}회)`);
    console.log(`  자연스러움 ${stats.naturalness_score}`);
  }
  console.log(`  자막 ${results.captions?.length ?? 0}개`);
  console.log('');
  console.log('출력:', outDir);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
