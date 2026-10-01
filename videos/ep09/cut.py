"""Episode 9 source-specific cut: keep every spoken word, shorten measured sentence pauses."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parent
START,END=1.20,49.94
# Word timestamps from small/int8 without VAD plus -36 dB silence scan.
GAPS=[(3.90,4.70),(8.68,9.00),(11.42,11.96),(15.26,15.90),(21.42,21.82),(30.32,30.72),(31.76,32.14),(34.30,34.70),(35.76,36.30),(39.52,40.24),(42.30,42.72),(45.02,45.62)]
segments=[];cursor=START;t=0.0
for a,b in GAPS+[(END+.06,END+.06)]:
 end=min(a+.06,END)
 if end>cursor:
  d=end-cursor;segments.append(dict(src_start=round(cursor,3),src_end=round(end,3),out_start=round(t,3),out_end=round(t+d,3)));t+=d
 cursor=b-.06
(ROOT/'cuts.json').write_text(json.dumps(dict(segments=segments,duration=round(t,3),gaps=GAPS),indent=2))
f=[]
for i,s in enumerate(segments):
 d=s['src_end']-s['src_start']
 f += [f"[0:v]trim={s['src_start']}:{s['src_end']},setpts=PTS-STARTPTS,fps=30[v{i}]",f"[0:a]atrim={s['src_start']}:{s['src_end']},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={max(0,d-.008):.3f}:d=0.008[a{i}]"]
f.append(''.join(f'[v{i}][a{i}]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=1:a=1[v][a]')
(ROOT/'src/fg.txt').write_text(';'.join(f))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'src/source.mp4'),'-filter_complex_script',str(ROOT/'src/fg.txt'),'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k',str(ROOT/'src/person_cut.mp4')],check=True)
for out,opts in [('person.mp4',['-an','-c:v','copy']),('voice.m4a',['-vn','-c:a','copy'])]:
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'src/person_cut.mp4'),*opts,str(ROOT/'assets'/out)],check=True)
print(f'{len(segments)} segments, {t:.3f}s from original 52.824s')
