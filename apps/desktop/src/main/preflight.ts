/**
 * 앱 부팅 시 환경 점검 (Preflight Health Check).
 *
 * 다른 PC 에서도 깔끔하게 동작하도록, 영상 작업을 시작하기 전에
 * 모든 외부 의존성을 한 번에 검증해서 사용자가 곧바로 무엇을 고쳐야 하는지
 * 알 수 있도록 한다.
 *
 * 점검 항목:
 *  - ffmpeg 실행 파일 (bundled / system / env)
 *  - Python venv (apps/desktop 옆 python/stt_service/venv)
 *  - faster-whisper / pyzmq import 가 되는지 (선택적)
 *  - filler lexicon JSON 존재
 *  - presets 디렉토리 존재
 *  - CapCut Drafts 디렉토리 (optional, 못 찾아도 EDL/SRT/MP4 export 는 가능)
 *
 * 결과는 IPC 'health:get' 으로 노출되어 renderer 가 사용자에게 친절한 안내 표시.
 */

import fs from 'fs';
import path from 'path';
import { spawnSync } from 'child_process';
import { app } from 'electron';
import {
  resolveFfmpegPath,
  describeFfmpegSource,
  createLogger,
} from '@cutback/shared';
import { findCapCutDraftsDir } from '@cutback/capcut-controller';

const logger = createLogger('preflight');

export type CheckStatus = 'ok' | 'warn' | 'fail';

export interface CheckResult {
  id: string;
  label: string;
  status: CheckStatus;
  detail: string;
  /** 사용자가 즉시 실행할 수 있는 해결 명령/링크. 여러 개 가능. */
  fixes?: string[];
}

export interface HealthReport {
  generatedAt: string;
  overall: CheckStatus;
  checks: CheckResult[];
}

let cached: HealthReport | null = null;

// ─── 개별 체크 ─────────────────────────────────────────────────────

function checkFfmpeg(): CheckResult {
  const p = resolveFfmpegPath();
  if (p) {
    return {
      id: 'ffmpeg',
      label: 'FFmpeg',
      status: 'ok',
      detail: describeFfmpegSource(),
    };
  }
  return {
    id: 'ffmpeg',
    label: 'FFmpeg',
    status: 'fail',
    detail: '실행 파일을 찾지 못했습니다. 영상 처리/렌더링 단계가 모두 실패합니다.',
    fixes: [
      'pnpm install   (ffmpeg-static 자동 설치 - 권장)',
      'choco install ffmpeg   (Windows + chocolatey)',
      'scoop install ffmpeg   (Windows + scoop)',
      'https://www.gyan.dev/ffmpeg/builds/   에서 다운로드 후 PATH 추가',
    ],
  };
}

function findProjectRoot(): string {
  // Electron dev: app.getAppPath() 는 보통 apps/desktop
  // packaged:    app.asar 의 부모 = resourcesPath
  const candidates = [
    path.resolve(app.getAppPath(), '..', '..'),
    path.resolve(app.getAppPath(), '..', '..', '..', '..'),
    path.resolve(__dirname, '..', '..', '..', '..'),
    process.cwd(),
  ];
  for (const c of candidates) {
    if (fs.existsSync(path.join(c, 'python', 'stt_service'))) return c;
  }
  return path.resolve(app.getAppPath(), '..', '..');
}

function checkPython(): CheckResult {
  const isWin = process.platform === 'win32';

  // ─── Packaged: 번들된 cutback-stt.exe 만 검증 ──────────────────
  if (app.isPackaged) {
    const exeName = isWin ? 'cutback-stt.exe' : 'cutback-stt';
    const bundled = path.join(process.resourcesPath, 'cutback-stt', exeName);
    if (fs.existsSync(bundled)) {
      return {
        id: 'python_venv',
        label: 'STT 엔진 (번들)',
        status: 'ok',
        detail: bundled,
      };
    }
    return {
      id: 'python_venv',
      label: 'STT 엔진 (번들)',
      status: 'fail',
      detail: `번들된 STT 실행 파일을 찾지 못했습니다 (${bundled}). 설치가 손상됐을 수 있습니다.`,
      fixes: ['앱을 재설치하거나 자동 업데이트를 기다려주세요.'],
    };
  }

  // ─── Dev: venv + import sanity check ────────────────────────────
  const root = findProjectRoot();
  const venvPython = isWin
    ? path.join(root, 'python', 'stt_service', 'venv', 'Scripts', 'python.exe')
    : path.join(root, 'python', 'stt_service', 'venv', 'bin', 'python');

  if (!fs.existsSync(venvPython)) {
    return {
      id: 'python_venv',
      label: 'Python venv (STT)',
      status: 'fail',
      detail: `${venvPython} 가 없습니다. STT (자막 생성) 가 동작하지 않습니다.`,
      fixes: ['pnpm run setup:python   (Python 3.9+ 필요)'],
    };
  }

  const probe = spawnSync(
    venvPython,
    ['-c', 'import faster_whisper, zmq, requests; print("OK")'],
    { encoding: 'utf-8', timeout: 8000 }
  );
  if (probe.status === 0 && (probe.stdout || '').includes('OK')) {
    return {
      id: 'python_venv',
      label: 'Python venv (STT)',
      status: 'ok',
      detail: 'faster-whisper / pyzmq / requests import 확인',
    };
  }
  return {
    id: 'python_venv',
    label: 'Python venv (STT)',
    status: 'warn',
    detail:
      'venv 는 있지만 일부 패키지 import 가 실패했습니다. setup 스크립트 재실행 권장.',
    fixes: ['pnpm run setup:python'],
  };
}

function checkLexicon(): CheckResult {
  const root = findProjectRoot();
  const candidates = [
    process.env.CUTBACK_FILLER_LEXICON,
    path.join(root, 'presets', 'lexicons', 'korean-fillers.json'),
    process.resourcesPath
      ? path.join(process.resourcesPath, 'presets', 'lexicons', 'korean-fillers.json')
      : null,
  ].filter((x): x is string => Boolean(x));

  for (const p of candidates) {
    if (fs.existsSync(p)) {
      return {
        id: 'filler_lexicon',
        label: 'Filler 사전',
        status: 'ok',
        detail: p,
      };
    }
  }
  return {
    id: 'filler_lexicon',
    label: 'Filler 사전',
    status: 'warn',
    detail:
      'korean-fillers.json 을 찾지 못했습니다. legacy 내장 사전으로 fallback (정확도↓).',
    fixes: ['저장소를 다시 받거나 presets/lexicons/korean-fillers.json 을 복원하세요.'],
  };
}

function checkPresets(): CheckResult {
  const root = findProjectRoot();
  const candidates = [
    path.join(root, 'presets'),
    process.resourcesPath ? path.join(process.resourcesPath, 'presets') : null,
  ].filter((x): x is string => Boolean(x));

  for (const p of candidates) {
    if (fs.existsSync(p)) {
      return {
        id: 'presets_dir',
        label: '프리셋 폴더',
        status: 'ok',
        detail: p,
      };
    }
  }
  return {
    id: 'presets_dir',
    label: '프리셋 폴더',
    status: 'fail',
    detail: 'presets/ 폴더를 찾지 못했습니다. 프리셋 로드/저장이 실패합니다.',
    fixes: ['저장소를 다시 받거나 presets/ 폴더를 복원하세요.'],
  };
}

function checkCapCut(): CheckResult {
  const draftsDir = findCapCutDraftsDir();
  if (draftsDir) {
    return {
      id: 'capcut',
      label: 'CapCut Drafts 폴더',
      status: 'ok',
      detail: draftsDir,
    };
  }
  return {
    id: 'capcut',
    label: 'CapCut Drafts 폴더',
    status: 'warn',
    detail:
      'CapCut Drafts 폴더를 찾지 못했습니다. CapCut export 만 영향 (EDL/SRT/MP4 export 는 정상).',
    fixes: [
      'https://www.capcut.com/  에서 CapCut Desktop 설치',
      '설치 후 한 번 실행해서 초기 폴더가 생성되도록 해주세요.',
    ],
  };
}

// ─── 종합 ──────────────────────────────────────────────────────────

function aggregate(checks: CheckResult[]): CheckStatus {
  if (checks.some((c) => c.status === 'fail')) return 'fail';
  if (checks.some((c) => c.status === 'warn')) return 'warn';
  return 'ok';
}

export function runPreflight(force = false): HealthReport {
  if (cached && !force) return cached;

  const checks: CheckResult[] = [
    checkFfmpeg(),
    checkPython(),
    checkLexicon(),
    checkPresets(),
    checkCapCut(),
  ];

  const report: HealthReport = {
    generatedAt: new Date().toISOString(),
    overall: aggregate(checks),
    checks,
  };

  // 부팅 시 한 줄 요약 로그
  for (const c of checks) {
    const fn =
      c.status === 'ok'
        ? logger.info
        : c.status === 'warn'
          ? logger.warn
          : logger.error;
    fn.call(logger, `preflight ${c.label}: ${c.status}`, { detail: c.detail });
  }

  cached = report;
  return report;
}

export function getHealth(): HealthReport {
  return cached ?? runPreflight();
}
