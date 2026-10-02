"""Replace attenuated renderer audio with the verified own mix; preserve encoded video."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1]
out=R/'renders/AI학교_12탄_Owen_v5.mp4'
tmp=R/'renders/AI학교_12탄_Owen_v5.remux.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out),'-i',str(R/'assets/mix.m4a'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-shortest','-movflags','+faststart',str(tmp)],check=True)
tmp.replace(out)
print(out)
