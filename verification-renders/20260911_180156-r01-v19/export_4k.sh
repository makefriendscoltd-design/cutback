#!/bin/sh
set -eu
cd "$(dirname "$0")"
ffmpeg -hide_banner -n -i 'AI학교_01_자막검정그림자_v19.mp4' -map 0:v:0 -map 0:a:0 -vf 'scale=2160:3840:flags=lanczos,setsar=1' -c:v h264_videotoolbox -b:v 40M -pix_fmt yuv420p -c:a copy -movflags +faststart 'AI학교_01_완성본_v19_4K.mp4'
