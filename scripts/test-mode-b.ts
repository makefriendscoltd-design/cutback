/**
 * Mode B 테스트 스크립트
 *
 * 사용법:
 *   tsx scripts/test-mode-b.ts <voiceover.mp3> <broll1.mp4> <broll2.mp4> ...
 */

import { ModeBPipeline } from '../packages/core/src/mode-b-pipeline.js';
import type { Job, Preset } from '../packages/shared/src/types/index.js';
import { writeFile } from 'fs/promises';
import path from 'path';

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error('Usage: tsx scripts/test-mode-b.ts <voiceover.mp3> <broll1.mp4> <broll2.mp4> ...');
    console.error('');
    console.error('Example:');
    console.error('  tsx scripts/test-mode-b.ts voiceover.mp3 clip1.mp4 clip2.mp4 clip3.mp4');
    process.exit(1);
  }

  const [voiceoverPath, ...assetPaths] = args;

  console.log('🎙️  Mode B 테스트 시작');
  console.log('보이스오버:', voiceoverPath);
  console.log('B-roll 클립:', assetPaths.join(', '));
  console.log('');

  // Mock Job
  const job: Job = {
    id: 'test-mode-b',
    videoPath: voiceoverPath,
    assetPaths,
    presetId: 'ad-product-broll',
    status: 'PROCESSING' as any,
    progress: 0,
    createdAt: new Date(),
    editMode: 'mode-b',
  };

  // Mock Preset
  const preset: Preset = {
    name: '테스트 프리셋',
    type: 'custom',
    version: '1.0.0',
    editMode: 'mode-b',
    canvas: {
      aspect_ratio: '9:16',
      width: 1080,
      height: 1920,
    },
    modeBParams: {
      matchConfig: {
        keywordMatching: {
          enabled: true,
          minScore: 0.3,
        },
        speedAdjustment: {
          min: 0.8,
          max: 1.3,
        },
        allowRepeat: false,
        allowFreeze: true,
      },
      autoApplyThreshold: 0.6,
      transitionStyle: 'cut',
    },
  };

  const pipeline = new ModeBPipeline();

  try {
    console.log('⏳ 파이프라인 실행 중...\n');

    const results = await pipeline.execute(job, preset, (stage, progress, message) => {
      console.log(`[${progress}%] ${stage}: ${message}`);
    });

    console.log('\n✅ 파이프라인 완료!\n');

    // 결과 출력
    if (results.sentenceTimeline) {
      console.log('📝 문장 타임라인:');
      console.log(`  - 문장 수: ${results.sentenceTimeline.sentences.length}`);
      console.log(`  - 총 길이: ${results.sentenceTimeline.totalDuration.toFixed(2)}초`);
      console.log(`  - 언어: ${results.sentenceTimeline.language}`);
      console.log('');
    }

    if (results.assetIndex) {
      console.log('🎬 에셋 인덱스:');
      console.log(`  - 클립 수: ${results.assetIndex.assets.length}`);
      console.log(`  - 총 길이: ${results.assetIndex.totalDuration.toFixed(2)}초`);
      results.assetIndex.assets.forEach((asset, i) => {
        console.log(`  ${i + 1}. ${asset.fileName} (${asset.duration.toFixed(1)}초)`);
      });
      console.log('');
    }

    if (results.roughCutTimeline) {
      console.log('🎞️  러프컷 타임라인:');
      console.log(`  - 트랙 수: ${results.roughCutTimeline.tracks.length}`);
      console.log(`  - 총 길이: ${results.roughCutTimeline.totalDuration.toFixed(2)}초`);
      console.log(`  - 평균 confidence: ${(results.roughCutTimeline.metadata.averageConfidence * 100).toFixed(1)}%`);
      console.log(`  - 검수 필요: ${results.roughCutTimeline.metadata.reviewRequiredCount}개`);

      const videoTrack = results.roughCutTimeline.tracks.find(t => t.type === 'video');
      if (videoTrack) {
        console.log(`  - 클립 수: ${videoTrack.clips.length}`);
        console.log('');
        console.log('  클립 상세:');
        videoTrack.clips.slice(0, 5).forEach((clip, i) => {
          console.log(`    ${i + 1}. ${clip.timelineStart.toFixed(1)}s ~ ${clip.timelineEnd.toFixed(1)}s`);
          console.log(`       속도: ${clip.playbackSpeed.toFixed(2)}x, confidence: ${(clip.confidence * 100).toFixed(1)}%`);
        });
        if (videoTrack.clips.length > 5) {
          console.log(`    ... 외 ${videoTrack.clips.length - 5}개`);
        }
      }
      console.log('');

      // EDL 내보내기
      if (results.assetIndex) {
        const edl = pipeline.exportToEDL(
          results.sentenceTimeline!,
          results.assetIndex,
          results.roughCutTimeline
        );

        const outputPath = path.join(process.cwd(), 'output-roughcut.edl');
        await writeFile(outputPath, edl, 'utf-8');
        console.log(`💾 EDL 저장: ${outputPath}`);
      }

      // SRT 내보내기
      if (results.sentenceTimeline) {
        const srt = pipeline.exportToSRT(results.sentenceTimeline);
        const srtPath = path.join(process.cwd(), 'output-voiceover.srt');
        await writeFile(srtPath, srt, 'utf-8');
        console.log(`💾 SRT 저장: ${srtPath}`);
      }
    }

    console.log('\n🎉 테스트 완료!');
  } catch (error) {
    console.error('\n❌ 에러 발생:', error);
    process.exit(1);
  }
}

main();
