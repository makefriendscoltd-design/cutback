#!/bin/zsh
set -eu
cd "${0:A:h}"
npx hyperframes render . --format mp4 --fps 30 --workers 2 --quality high --output editor-authored-36s.mp4 > qa/render.log 2>&1
ffmpeg -y -hide_banner -i editor-authored-36s.mp4 -i assets/editor-mix.wav -filter_complex '[0:v]setpts=PTS/2[v];[1:a]atempo=2[a]' -map '[v]' -map '[a]' -r 60 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -t 18 -movflags +faststart '/Users/apple/Downloads/AI학교_가상편집과정_2배속_18초.mp4' > qa/final-encode.log 2>&1
