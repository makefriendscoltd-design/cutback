#!/bin/bash
# capture.sh <url> <out.png> [width] [height]  — real-page screenshots for on-screen UI (dark mode, 2x)
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W=${3:-1280}; H=${4:-2000}
"$C" --headless=new --disable-gpu --hide-scrollbars --force-dark-mode --blink-settings=preferredColorScheme=0 \
  --force-device-scale-factor=2 --window-size=$W,$H --virtual-time-budget=8000 \
  --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36" \
  --screenshot="$2" "$1" 2>/dev/null
ls -la "$2" | awk '{print $5, $9}'
