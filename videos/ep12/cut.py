#!/usr/bin/env python3
"""Episode 12 cuts: preserve the complete take and tighten measured pauses."""
from pathlib import Path
import json, subprocess
ROOT=Path(__file__).resolve().parent
START,END=3.62,51.54
# 50 ms RMS and non-VAD word timestamps; only inter-phrase pauses over 0.28 s.
GAPS=[(5.82,6.32),(8.58,8.92),(9.98,10.66),(12.58,12.94),(15.96,16.62),
      (17.88,18.34),(21.86,22.44),(26.12,26.56),(36.58,37.14),
      (42.44,43.02),(46.26,46.84)]
segments=[];cursor=START;out_t=0.0
for a,b in GAPS+[(END+.06,END+.06)]:
    end=min(a+.06,END)
    if end>cursor:
        d=end-cursor;segments.append(dict(src_start=round(cursor,3),src_end=round(end,3),out_start=round(out_t,3),out_end=round(out_t+d,3)));out_t+=d
    cursor=b-.06
(ROOT/'cuts.json').write_text(json.dumps({'segments':segments,'duration':round(out_t,3),'gaps':GAPS,'source_duration':53.9364},indent=2))
f=[]
for i,s in enumerate(segments):
    d=s['src_end']-s['src_start']
    f += [f"[0:v]trim={s['src_start']}:{s['src_end']},setpts=PTS-STARTPTS,fps=30[v{i}]",
          f"[0:a]atrim={s['src_start']}:{s['src_end']},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={max(0,d-.008):.3f}:d=0.008[a{i}]"]
f.append(''.join(f'[v{i}][a{i}]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=1:a=1[v][a]')
(ROOT/'src/fg.txt').write_text(';'.join(f))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'src/source.mp4'),'-filter_complex_script',str(ROOT/'src/fg.txt'),'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k',str(ROOT/'src/person_cut.mp4')],check=True)
for name,opts in [('person.mp4',['-an','-c:v','copy']),('voice.m4a',['-vn','-c:a','copy'])]:
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'src/person_cut.mp4'),*opts,str(ROOT/'assets'/name)],check=True)
print(f'{len(segments)} segments, {out_t:.3f}s from original 53.9364s')
