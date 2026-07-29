/**
 * Electron main process 번들러
 *
 * 왜 esbuild 가 필요한가?
 * - pnpm workspace 는 @cutback/* 을 심볼릭 링크로 연결
 * - tsc 는 번들링 없이 require('@cutback/shared') 같은 require 를 남김
 * - electron-builder 가 asar 만들 때 심볼릭 링크 따라가서 외부 경로 탐지 → 실패
 *
 * 해결: esbuild 로 main entry 를 번들링해서 @cutback/* 을 인라인.
 *       런타임에 node_modules/@cutback/* 을 안 참조하게 되어 asar 에 넣을 필요 없음.
 *
 * external:
 *   - electron / electron-log / electron-updater: Node 로 로드되는 electron runtime
 *   - better-sqlite3 / zeromq: native .node 바이너리 (asarUnpack 으로 처리)
 */
import { build } from 'esbuild';

const EXTERNAL = [
  'electron',
  'electron-log',
  'electron-updater',
  'better-sqlite3',
  'zeromq', // native N-API 바이너리 (prebuilds 포함)
  'ffmpeg-static', // __dirname 기반 경로 반환 → 번들하면 경로 깨짐
  // Node built-ins 는 esbuild 가 자동으로 external 처리
];

await build({
  entryPoints: ['src/main/index.ts'],
  outfile: 'dist/main/index.js',
  bundle: true,
  platform: 'node',
  target: 'node20',
  format: 'cjs',
  sourcemap: false,
  minify: false,
  external: EXTERNAL,
  logLevel: 'info',
});

console.log('[build-main] done');
