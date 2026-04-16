/**
 * Cutback - PyInstaller 로 STT service 를 단일 실행 폴더로 빌드.
 *
 * 결과:
 *   python/stt_service/dist/cutback-stt/
 *     ├── cutback-stt.exe          (또는 Unix: cutback-stt)
 *     └── ... (torch DLL, faster-whisper, 기타 의존성)
 *
 * 이 폴더 전체가 electron-builder 의 extraResources 로 복사된다.
 * 사용자 PC 에는 Python / venv / pip 이 일절 필요 없다.
 *
 * 실행: pnpm run build:python-exe   (또는 node scripts/build-python-exe.js)
 *
 * 전제: pnpm run setup:python 이 한 번 이상 실행되어 venv 가 있어야 함.
 */

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const STT_DIR = path.join(ROOT, 'python', 'stt_service');
const VENV_DIR = path.join(STT_DIR, 'venv');
const SPEC_FILE = path.join(STT_DIR, 'stt_service.spec');

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
function fail(s) {
  console.log(`  ${C.red}✗${C.reset} ${s}`);
}
function info(s) {
  console.log(`  ${C.dim}${s}${C.reset}`);
}

const isWin = process.platform === 'win32';
const venvPython = isWin
  ? path.join(VENV_DIR, 'Scripts', 'python.exe')
  : path.join(VENV_DIR, 'bin', 'python');

header('PyInstaller 로 STT service 빌드');

// 1) venv 존재 확인
if (!fs.existsSync(venvPython)) {
  fail(`venv 가 없습니다: ${venvPython}`);
  info('먼저 다음을 실행하세요:  pnpm run setup:python');
  process.exit(1);
}
ok(`venv 발견: ${venvPython}`);

// 2) PyInstaller 가 없으면 설치
const probe = spawnSync(venvPython, ['-c', 'import PyInstaller; print(PyInstaller.__version__)'], {
  encoding: 'utf-8',
});
if (probe.status !== 0) {
  info('PyInstaller 설치 중... (1~2분)');
  const install = spawnSync(
    venvPython,
    ['-m', 'pip', 'install', '--prefer-binary', 'pyinstaller>=6.0'],
    { stdio: 'inherit' }
  );
  if (install.status !== 0) {
    fail('PyInstaller 설치 실패');
    process.exit(1);
  }
  ok('PyInstaller 설치 완료');
} else {
  ok(`PyInstaller ${probe.stdout.trim()} 발견`);
}

// 3) 이전 빌드 정리
const buildDir = path.join(STT_DIR, 'build');
const distDir = path.join(STT_DIR, 'dist');
for (const d of [buildDir, distDir]) {
  if (fs.existsSync(d)) {
    info(`기존 ${path.basename(d)} 폴더 삭제 중...`);
    fs.rmSync(d, { recursive: true, force: true });
  }
}

// 4) PyInstaller 실행 (spec 파일 모드)
info('PyInstaller 실행 중... (5~10분, torch/onnxruntime 수집)');
const result = spawnSync(
  venvPython,
  ['-m', 'PyInstaller', '--clean', '--noconfirm', SPEC_FILE],
  { cwd: STT_DIR, stdio: 'inherit' }
);
if (result.status !== 0) {
  fail('PyInstaller 빌드 실패');
  process.exit(1);
}

// 5) 결과 확인
const exeName = isWin ? 'cutback-stt.exe' : 'cutback-stt';
const exePath = path.join(distDir, 'cutback-stt', exeName);
if (!fs.existsSync(exePath)) {
  fail(`예상 출력이 없습니다: ${exePath}`);
  process.exit(1);
}

// 용량 측정
function dirSizeMB(dir) {
  let total = 0;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) total += dirSizeMB(p) * 1024 * 1024;
    else total += fs.statSync(p).size;
  }
  return Math.round(total / 1024 / 1024);
}
const sizeMB = dirSizeMB(path.join(distDir, 'cutback-stt'));

ok(`빌드 완료: ${exePath}`);
ok(`총 용량: ${sizeMB} MB`);
console.log(
  `\n${C.bold}${C.green}✓ STT 실행 폴더 준비 완료.${C.reset}\n` +
    `  다음 단계:  pnpm dist   (Electron installer 생성)`
);
