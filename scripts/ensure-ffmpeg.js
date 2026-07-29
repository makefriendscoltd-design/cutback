'use strict';

/**
 * pnpm postinstall 에서 호출.
 * ffmpeg-static 바이너리가 없으면 install.js 를 재실행해서 다운받는다.
 * 네트워크 문제로 최초 install 시 다운로드가 실패해도 재시도한다.
 */

const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');

function resolveFfmpegStaticDir() {
  try {
    // require.resolve 는 package.json 위치를 줌
    const pkgPath = require.resolve('ffmpeg-static/package.json');
    return path.dirname(pkgPath);
  } catch {
    return null;
  }
}

function getBinaryPath(dir) {
  const isWin = process.platform === 'win32';
  return path.join(dir, isWin ? 'ffmpeg.exe' : 'ffmpeg');
}

const dir = resolveFfmpegStaticDir();
if (!dir) {
  console.warn('[ensure-ffmpeg] ffmpeg-static 패키지를 찾을 수 없음 — 건너뜀');
  process.exit(0);
}

const binaryPath = getBinaryPath(dir);

if (fs.existsSync(binaryPath)) {
  console.log('[ensure-ffmpeg] OK:', binaryPath);
  process.exit(0);
}

console.log('[ensure-ffmpeg] ffmpeg 바이너리 없음 — 다운로드 시도...');
const installScript = path.join(dir, 'install.js');

try {
  execFileSync(process.execPath, [installScript], {
    stdio: 'inherit',
    cwd: dir,
  });
} catch (err) {
  console.error('[ensure-ffmpeg] 다운로드 실패:', err.message);
  console.error('해결 방법:');
  console.error('  1) 네트워크 연결 확인 후 pnpm install 재실행');
  console.error('  2) 또는 ffmpeg 를 직접 설치하고 CUTBACK_FFMPEG 환경변수로 경로 지정');
  process.exit(1); // install 전체를 실패로 표시
}

if (fs.existsSync(binaryPath)) {
  console.log('[ensure-ffmpeg] 다운로드 완료:', binaryPath);
} else {
  console.error('[ensure-ffmpeg] 다운로드 후에도 바이너리 없음 — install.js 를 확인하세요');
  process.exit(1);
}
