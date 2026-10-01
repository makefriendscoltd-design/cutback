#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export OWEN_AUDIO_DIR="$ROOT/assets/audio"
EP="$ROOT/videos/ep07-v3"
case "${1:-build}" in
  build) python3 "$EP/build.py"; python3 "$ROOT/videos/check_owen_camera.py" "$EP" ;;
  check) node "$EP/qc/caption-audit.mjs"; (cd "$EP" && npx --yes hyperframes@0.8.103 check --json) ;;
  render)
    test -s "$EP/src/source.mp4" || { echo 'Missing private input: videos/ep07-v3/src/source.mp4' >&2; exit 2; }
    python3 "$EP/cut.py"
    python3 "$EP/build.py"
    python3 "$EP/mix.py"
    node "$EP/qc/caption-audit.mjs"
    python3 "$ROOT/videos/check_owen_camera.py" "$EP"
    (cd "$EP" && npx --yes hyperframes@0.8.103 check --json)
    python3 "$ROOT/videos/render_serial.py" --project "$EP" --output renders/AI학교_7탄_Plugins_Owen_v3.mp4
    python3 "$ROOT/finalize_audio.py" "$EP" "$EP/renders/AI학교_7탄_Plugins_Owen_v3.mp4"
    python3 "$EP/qc/verify_render.py" ;;
  *) echo 'Usage: bash run.sh build|check|render' >&2; exit 2 ;;
esac
