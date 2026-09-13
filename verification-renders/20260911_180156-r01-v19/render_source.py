"""Deterministic export: preserve HyperFrames output and use its validated t=0 snapshot for frame 0.
HyperFrames 0.8.35 check shows the headline at t=0, but movie capture omits it on frame0.
Do not add more GSAP timing patches. The authored clean snapshot defines frame0; all later frames and audio retain their timing.
Run after build_v12.py and check --at 0 --snapshots; this script can render or finalize an existing intermediate.
"""
from pathlib import Path
import subprocess,sys,shutil
R=Path(__file__).resolve().parent
OUT=R/'original-source-52s.mp4'
RAW=R/'hyperframes-render.mp4'
FRAME=R/'composition/snapshots/frame-00-at-0.0s.png'
if '--existing' in sys.argv:
 if not RAW.exists():shutil.move(OUT,RAW)
else:
 subprocess.run(['npx','--yes','hyperframes@0.8.35','render',str(R/'composition'),'--quality','high','--fps','30','--workers','2','--no-best-effort','--output',str(RAW)],check=True)
assert FRAME.exists()
subprocess.run(['ffmpeg','-v','error','-y','-i',str(RAW),'-i',str(FRAME),'-filter_complex',"[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]",'-map','[v]','-map','0:a','-c:v','h264_videotoolbox','-b:v','14000k','-pix_fmt','yuv420p','-c:a','copy','-frames:v','1579','-movflags','+faststart',str(OUT)],check=True)
print(OUT)
