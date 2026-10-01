#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) echo 'Native Windows/Git Bash is unsupported. Use WSL2 and bash run-wsl.sh (WINDOWS.md).' >&2; exit 2 ;;
  Linux)
    if uname -r | grep -qi microsoft; then
      bash "$ROOT/run-wsl.sh" preflight
      if [[ -x "$ROOT/.venv/bin/python3" ]]; then export PATH="$ROOT/.venv/bin:$PATH"; fi
    fi ;;
esac
export OWEN_AUDIO_DIR="$ROOT/assets/audio"
EP="$ROOT/videos/ep07-v3"
prepare_browser() { (cd "$EP" && npx --yes hyperframes@0.8.103 browser ensure); }
case "${1:-build}" in
  prepare) prepare_browser ;;
  smoke) python3 "$ROOT/smoke.py" ;;
  build) python3 "$EP/build.py"; python3 "$ROOT/videos/check_owen_camera.py" "$EP" ;;
  check) prepare_browser; node "$EP/qc/caption-audit.mjs"; (cd "$EP" && npx --yes hyperframes@0.8.103 check --json) ;;
  render)
    test -s "$EP/src/source.mp4" || { echo 'Missing private input: videos/ep07-v3/src/source.mp4' >&2; exit 2; }
    python3 "$EP/cut.py"
    python3 "$EP/build.py"
    python3 "$EP/mix.py"
    prepare_browser
    node "$EP/qc/caption-audit.mjs"
    python3 "$ROOT/videos/check_owen_camera.py" "$EP"
    (cd "$EP" && npx --yes hyperframes@0.8.103 check --json)
    python3 "$ROOT/videos/render_serial.py" --project "$EP" --output renders/AI학교_7탄_Plugins_Owen_v3.mp4
    python3 "$ROOT/finalize_audio.py" "$EP" "$EP/renders/AI학교_7탄_Plugins_Owen_v3.mp4"
    python3 "$EP/qc/verify_render.py" ;;
  *) echo 'Usage: bash run.sh prepare|build|check|render|smoke' >&2; exit 2 ;;
esac
