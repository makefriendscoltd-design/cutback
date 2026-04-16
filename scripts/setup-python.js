/**
 * Cutback - Python 환경 자동 설정 스크립트
 *
 * 다른 PC 에서도 한 번에 동작하도록 다음을 수행:
 *   1) Python 인터프리터 탐색 (python3 / python / py -3)
 *   2) 버전 체크 (>= 3.9)
 *   3) venv 가 없으면 생성, 있으면 재사용
 *   4) pip 업그레이드 후 requirements.txt 설치
 *   5) ffmpeg 가용성 체크 (ffmpeg-static 우선, 시스템 PATH fallback)
 *   6) 모든 단계 마지막에 한 줄 요약 + 다음 단계 안내
 *
 * 실행: pnpm run setup:python   (또는 node scripts/setup-python.js)
 *
 * 종료 코드:
 *   0 = 모두 성공
 *   1 = 치명적 실패 (Python 미발견 / venv 생성 실패)
 *   2 = 부분 성공 (의존성 설치 일부 실패 - 다시 실행 권장)
 */

const { execSync, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const SERVICES = [
  { name: 'stt_service', dir: path.join(ROOT, 'python', 'stt_service'), required: true },
  { name: 'vad_service', dir: path.join(ROOT, 'python', 'vad_service'), required: false },
];

// ─── ANSI 색상 (Windows 10+ 도 ANSI 지원) ────────────────────────────
const C = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
};

function header(s) {
  console.log(`\n${C.bold}${C.cyan}━━ ${s} ━━${C.reset}`);
}
function ok(s) {
  console.log(`  ${C.green}✓${C.reset} ${s}`);
}
function warn(s) {
  console.log(`  ${C.yellow}!${C.reset} ${s}`);
}
function fail(s) {
  console.log(`  ${C.red}✗${C.reset} ${s}`);
}
function info(s) {
  console.log(`  ${C.dim}${s}${C.reset}`);
}

// ─── Python 탐색 ─────────────────────────────────────────────────────

/** Python 후보 명령들을 차례로 시도. 가장 먼저 응답하는 걸 사용. */
function detectPython() {
  const candidates =
    process.platform === 'win32'
      ? [['py', ['-3']], ['python', []], ['python3', []]]
      : [['python3', []], ['python', []]];

  for (const [cmd, args] of candidates) {
    const probe = spawnSync(cmd, [...args, '--version'], {
      encoding: 'utf-8',
      timeout: 5000,
    });
    if (probe.status === 0) {
      const verLine = (probe.stdout || probe.stderr || '').trim();
      const m = verLine.match(/Python\s+(\d+)\.(\d+)\.(\d+)/);
      if (m) {
        const major = parseInt(m[1], 10);
        const minor = parseInt(m[2], 10);
        return {
          cmd,
          baseArgs: args,
          version: `${m[1]}.${m[2]}.${m[3]}`,
          major,
          minor,
        };
      }
    }
  }
  return null;
}

// ─── 명령 실행 (실시간 출력) ─────────────────────────────────────────

function runStream(cmd, args, cwd) {
  const result = spawnSync(cmd, args, { cwd, stdio: 'inherit' });
  return result.status === 0;
}

// ─── 서비스 setup ────────────────────────────────────────────────────

function setupService(service, py) {
  header(`${service.name} 환경 구성`);

  if (!fs.existsSync(service.dir)) {
    if (service.required) {
      fail(`${service.dir} 폴더가 없습니다. 저장소가 손상됐을 수 있습니다.`);
      return false;
    }
    warn(`${service.dir} 폴더 없음 - optional 서비스이므로 skip`);
    return true;
  }

  const reqFile = path.join(service.dir, 'requirements.txt');
  if (!fs.existsSync(reqFile)) {
    warn('requirements.txt 없음 - skip');
    return true;
  }

  const venvDir = path.join(service.dir, 'venv');
  const isWin = process.platform === 'win32';
  const venvPython = isWin
    ? path.join(venvDir, 'Scripts', 'python.exe')
    : path.join(venvDir, 'bin', 'python');
  const venvPip = isWin
    ? path.join(venvDir, 'Scripts', 'pip.exe')
    : path.join(venvDir, 'bin', 'pip');

  // 1) venv 생성 (없거나 깨졌을 때)
  const venvHealthy = fs.existsSync(venvPython);
  if (!venvHealthy) {
    info('venv 생성 중... (1~2 분)');
    const ok1 = runStream(py.cmd, [...py.baseArgs, '-m', 'venv', 'venv'], service.dir);
    if (!ok1 || !fs.existsSync(venvPython)) {
      fail('venv 생성 실패. 다음 명령으로 수동 진단 가능:');
      info(`    cd ${service.dir}`);
      info(`    ${py.cmd} ${py.baseArgs.join(' ')} -m venv venv`);
      return false;
    }
    ok('venv 생성 완료');
  } else {
    ok('venv 이미 존재 - 재사용');
  }

  // 2) pip upgrade
  info('pip 업그레이드 중...');
  runStream(venvPython, ['-m', 'pip', 'install', '--upgrade', 'pip'], service.dir);

  // 3) requirements 설치
  info('의존성 설치 중... (faster-whisper / torch 포함, 첫 설치 5~10 분)');
  const installed = runStream(
    venvPip,
    ['install', '--prefer-binary', '-r', 'requirements.txt'],
    service.dir
  );
  if (!installed) {
    fail('의존성 설치 실패. 네트워크 또는 디스크 공간 확인 후 재실행:');
    info('    pnpm run setup:python');
    return false;
  }

  // 4) sanity check - faster_whisper import 가 되는지
  if (service.name === 'stt_service') {
    const probe = spawnSync(
      venvPython,
      ['-c', 'import faster_whisper, zmq, requests; print("OK")'],
      { encoding: 'utf-8' }
    );
    if (probe.status === 0 && (probe.stdout || '').includes('OK')) {
      ok('faster_whisper / pyzmq / requests import 확인');
    } else {
      warn('faster_whisper sanity check 실패 - 첫 실행 때 다시 검증됨');
      if (probe.stderr) info(probe.stderr.trim().split('\n').slice(-3).join('\n'));
    }
  }

  ok(`${service.name} 준비 완료`);
  return true;
}

// ─── ffmpeg 체크 (ffmpeg-static 우선) ────────────────────────────────

function checkFfmpeg() {
  header('ffmpeg 가용성 확인');

  // 1) ffmpeg-static (pnpm install 시 자동 설치되는 npm 패키지)
  try {
    // node_modules 가 워크스페이스 hoist 라 root 또는 audio-engine 양쪽에 있을 수 있음.
    const candidates = [
      path.join(ROOT, 'node_modules', 'ffmpeg-static'),
      path.join(ROOT, 'packages', 'audio-engine', 'node_modules', 'ffmpeg-static'),
      path.join(ROOT, 'packages', 'capcut-controller', 'node_modules', 'ffmpeg-static'),
    ];
    let bundled = null;
    for (const c of candidates) {
      try {
        // require 로 module 의 default export (binary path) 가져오기
        bundled = require(c);
        if (bundled) break;
      } catch {
        /* ignore */
      }
    }
    if (bundled && fs.existsSync(bundled)) {
      ok(`ffmpeg-static 사용 가능: ${bundled}`);
      return true;
    }
  } catch {
    /* fall through to system check */
  }

  // 2) 시스템 PATH 의 ffmpeg
  try {
    execSync('ffmpeg -version', { stdio: 'pipe', timeout: 5000 });
    ok('시스템 PATH 에 ffmpeg 발견');
    return true;
  } catch {
    fail('ffmpeg 를 찾지 못했습니다.');
    info('해결 방법:');
    info('  - 권장: 저장소 루트에서 `pnpm install` 재실행 (ffmpeg-static 자동 설치)');
    info('  - 수동: https://www.gyan.dev/ffmpeg/builds/  (ffmpeg.exe 를 PATH 에 추가)');
    info('  - choco: choco install ffmpeg');
    info('  - scoop: scoop install ffmpeg');
    return false;
  }
}

// ─── 메인 ────────────────────────────────────────────────────────────

console.log(`${C.bold}Cutback Python 환경 설정${C.reset}`);
console.log(`${C.dim}루트: ${ROOT}${C.reset}`);

header('Python 인터프리터 탐색');
const py = detectPython();
if (!py) {
  fail('Python 을 찾지 못했습니다.');
  info('해결 방법 (Python 3.9+ 필요):');
  info('  - Windows: https://www.python.org/downloads/  (설치 시 "Add to PATH" 체크)');
  info('  - macOS:   brew install python@3.11');
  info('  - Linux:   sudo apt install python3 python3-venv  (또는 dnf/pacman)');
  process.exit(1);
}

if (py.major < 3 || (py.major === 3 && py.minor < 9)) {
  fail(`Python ${py.version} 은 너무 낮습니다. 3.9 이상 필요.`);
  info('  새 Python 설치 후 다시 실행하세요.');
  process.exit(1);
}
ok(`Python ${py.version} (${py.cmd}${py.baseArgs.length ? ' ' + py.baseArgs.join(' ') : ''})`);

// ffmpeg
const ffmpegOk = checkFfmpeg();

// services
let allOk = true;
for (const svc of SERVICES) {
  const r = setupService(svc, py);
  if (!r && svc.required) allOk = false;
}

// ─── 요약 ────────────────────────────────────────────────────────────

console.log('');
header('요약');
console.log(`  Python:       ${py.version} (${py.cmd})`);
console.log(`  ffmpeg:       ${ffmpegOk ? C.green + 'OK' + C.reset : C.red + 'MISSING' + C.reset}`);
for (const svc of SERVICES) {
  const venvDir = path.join(svc.dir, 'venv');
  const isWin = process.platform === 'win32';
  const venvPython = isWin
    ? path.join(venvDir, 'Scripts', 'python.exe')
    : path.join(venvDir, 'bin', 'python');
  const ready = fs.existsSync(venvPython);
  const status = ready
    ? C.green + 'ready' + C.reset
    : svc.required
      ? C.red + 'MISSING' + C.reset
      : C.dim + 'optional/skip' + C.reset;
  console.log(`  ${svc.name.padEnd(13)} ${status}`);
}

if (allOk && ffmpegOk) {
  console.log(`\n${C.bold}${C.green}✓ 모든 준비 완료. 다음:${C.reset}\n  pnpm dev`);
  process.exit(0);
} else if (allOk) {
  console.log(`\n${C.bold}${C.yellow}⚠ ffmpeg 미설치 - 영상 처리가 실패합니다.${C.reset}`);
  console.log(`  pnpm install 을 먼저 실행한 다음 다시: pnpm run setup:python`);
  process.exit(2);
} else {
  console.log(`\n${C.bold}${C.red}✗ 일부 단계 실패 - 위 안내에 따라 재시도하세요.${C.reset}`);
  process.exit(2);
}
