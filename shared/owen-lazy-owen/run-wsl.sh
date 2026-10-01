#!/usr/bin/env bash
# Windows entry: execute inside WSL2; keep the original POSIX render lock.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
ACTION="${1:-preflight}"
case "$ACTION" in preflight|prepare|build|check|render|smoke) ;; *) echo 'Usage: bash run-wsl.sh preflight|prepare|build|check|render|smoke' >&2; exit 2 ;; esac
if [[ "$(uname -s)" != Linux ]] || ! uname -r | grep -Eqi 'microsoft.*wsl2'; then
  echo 'WSL2 required. In Windows PowerShell: wsl --list --verbose. Then enter your WSL2 distro and run this script there. Native Windows/Git Bash/WSL1 are unsupported.' >&2
  exit 2
fi
if [[ -x "$ROOT/.venv/bin/python3" ]]; then export PATH="$ROOT/.venv/bin:$PATH"; fi
for tool in python3 node npm npx ffmpeg ffprobe; do
  command -v "$tool" >/dev/null || { echo "Missing Linux dependency: $tool (see WINDOWS.md)" >&2; exit 2; }
  case "$(command -v "$tool")" in /mnt/*|*.exe|*.cmd) echo "Use a Linux-installed $tool inside WSL, not the Windows installation." >&2; exit 2 ;; esac
done
python3 - <<'PY'
import sys,fcntl,tempfile
if sys.version_info < (3,10): raise SystemExit('Python 3.10+ required')
try: import PIL,numpy
except ImportError as e: raise SystemExit('Activate the Linux .venv and install requirements.txt: '+str(e))
with tempfile.TemporaryFile() as f: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
print('Python/imports/POSIX flock: PASS')
PY
node -e 'if(process.platform!=="linux" || +process.versions.node.split(".")[0]<22) {console.error("Linux Node.js 22+ required");process.exit(2)}'
ffmpeg -hide_banner -encoders 2>/dev/null | grep 'libx264' >/dev/null || { echo 'FFmpeg with libx264 required' >&2; exit 2; }
echo 'WSL2 preflight passed; browser/render remain unverified until smoke completes.'
[[ "$ACTION" != preflight ]] || exit 0
exec bash "$ROOT/run.sh" "$ACTION"
