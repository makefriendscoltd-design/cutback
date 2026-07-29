/**
 * FFmpeg 실행 파일 경로 결정.
 *
 * 우선순위:
 *  1) 환경변수 CUTBACK_FFMPEG (사용자 강제 지정)
 *  2) ffmpeg-static (npm 으로 함께 설치되는 정적 바이너리) - 다른 PC 에서도 별도 설치 불필요
 *  3) PATH 의 시스템 ffmpeg
 *
 * 실패해도 throw 하지 않고 null 을 반환해서 preflight 가 깔끔한 에러 메시지를 보여줄 수 있게 함.
 *
 * 캐시: 한 번 결정되면 프로세스 동안 재사용.
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

let cached: string | null | undefined = undefined;

function tryElectronResources(): string | null {
  try {
    // Electron main process에서만 존재하는 process.resourcesPath
    // packaged 앱: resources/ffmpeg/ffmpeg.exe (extraResources로 복사됨)
    // dev 모드: Electron 자체 resources 폴더라 ffmpeg 없음 → null 반환하여 다음 단계로
    const rp = (process as NodeJS.Process & { resourcesPath?: string }).resourcesPath;
    if (!rp) return null;
    const exe = process.platform === 'win32' ? 'ffmpeg.exe' : 'ffmpeg';
    const p = path.join(rp, 'ffmpeg', exe);
    if (fs.existsSync(p)) return p;
    return null;
  } catch {
    return null;
  }
}

function tryResolveStatic(): string | null {
  try {
    // ffmpeg-static 은 default export 로 path 문자열을 준다.
    // 일부 환경(electron asar)에서 .replace('app.asar', 'app.asar.unpacked') 가 필요.
    // require 로 동기 로드 (선택적 의존성).
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const mod = require('ffmpeg-static');
    let p: string | null =
      typeof mod === 'string' ? mod : (mod && mod.default) || null;
    if (!p) return null;

    // Electron asar 환경에서 .exe 를 unpacked 폴더에서 실제 실행 가능하도록 경로 보정
    p = p.replace(/app\.asar([\\/])/, 'app.asar.unpacked$1');

    if (fs.existsSync(p)) return p;
    return null;
  } catch {
    return null;
  }
}

function trySystem(): string | null {
  // Windows 면 ffmpeg, ffmpeg.exe 둘 다 시도. where/which 로 PATH 조회.
  const isWin = process.platform === 'win32';
  const probeCmd = isWin ? 'where ffmpeg' : 'which ffmpeg';
  try {
    const out = execSync(probeCmd, {
      stdio: ['ignore', 'pipe', 'ignore'],
      timeout: 3000,
    })
      .toString()
      .trim();
    if (!out) return null;
    // 여러 줄이면 첫 줄
    const first = out.split(/\r?\n/)[0].trim();
    if (first && fs.existsSync(first)) return first;
    return null;
  } catch {
    return null;
  }
}

/** ffmpeg 실행 파일 절대 경로. 못 찾으면 null. */
export function resolveFfmpegPath(forceReload = false): string | null {
  if (!forceReload && cached !== undefined) return cached;

  // 1) 환경변수
  const envPath = process.env.CUTBACK_FFMPEG;
  if (envPath && fs.existsSync(envPath)) {
    cached = envPath;
    return cached;
  }

  // 2) Electron extraResources (packaged 앱)
  const electronPath = tryElectronResources();
  if (electronPath) {
    cached = electronPath;
    return cached;
  }

  // 3) ffmpeg-static (dev 모드)
  const staticPath = tryResolveStatic();
  if (staticPath) {
    cached = staticPath;
    return cached;
  }

  // 4) PATH 의 시스템 ffmpeg
  const sys = trySystem();
  if (sys) {
    cached = sys;
    return cached;
  }

  cached = null;
  return cached;
}

/** 실행 가능 여부만 빠르게. */
export function isFfmpegAvailable(): boolean {
  return resolveFfmpegPath() !== null;
}

/** 사람용 표시 (없으면 'not found'). */
export function describeFfmpegSource(): string {
  const p = resolveFfmpegPath();
  if (!p) return 'not found';
  if (process.env.CUTBACK_FFMPEG === p) return `env (${p})`;
  // ffmpeg-static path 는 보통 node_modules 안에 있음
  if (p.includes('ffmpeg-static') || p.includes('node_modules')) return `bundled (${p})`;
  return `system (${p})`;
}
