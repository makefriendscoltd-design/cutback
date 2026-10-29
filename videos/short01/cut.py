#!/usr/bin/env python3
"""Short01 cuts: keep the single complete take, tighten measured pauses (>0.28s -> 0.12s).
Boundaries come from 20ms RMS profiles (qc/cut-rms.txt), not ASR starts (ASR put 1.26/27.94/31.44 early).
Source is 3840x2160 with -90 rotation metadata; ffmpeg autorotate yields upright 2160x3840, scaled to 1080x1920.
"""
from pathlib import Path
import json, subprocess
ROOT=Path(__file__).resolve().parent
START,END=1.50,40.40
# (speech end, next speech onset) in source seconds; every pair here is >=0.28s of silence/breath.
GAPS=[(3.30,3.58),(8.22,8.90),(10.64,11.26),(15.26,15.77),(22.04,22.32),
      (23.60,24.13),(27.62,28.20),(30.90,31.52),(36.38,36.81)]
segments=[];cursor=START;out_t=0.0
for a,b in GAPS+[(END+.06,END+.06)]:
    end=min(a+.06,END)
    if end>cursor:
        # Quantise each kept span to whole 30fps frames so concat never pads audio and M(t) stays exact.
        cursor=round(cursor*30)/30;end=round(end*30)/30;d=end-cursor;segments.append(dict(src_start=round(cursor,3),src_end=round(end,3),out_start=round(out_t,3),out_end=round(out_t+d,3)));out_t+=d
    cursor=b-.06
(ROOT/'cuts.json').write_text(json.dumps({'segments':segments,'duration':round(out_t,3),'gaps':GAPS,'source_duration':42.475},indent=2))
f=[f"[0:v]fps=30,scale=1080:1920:flags=lanczos,setsar=1,split={len(segments)}"+''.join(f'[p{i}]' for i in range(len(segments)))]
for i,s in enumerate(segments):
    d=s['src_end']-s['src_start']
    f += [f"[p{i}]trim=start_frame={round(s['src_start']*30)}:end_frame={round(s['src_end']*30)},setpts=PTS-STARTPTS[v{i}]",
          f"[0:a]atrim={s['src_start']}:{s['src_end']},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={max(0,d-.008):.3f}:d=0.008[a{i}]"]
f.append(''.join(f'[v{i}][a{i}]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=1:a=1[v][a]')
(ROOT/'src/fg.txt').write_text(';'.join(f))
(ROOT/'assets').mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'src/source.mp4'),'-filter_complex_script',str(ROOT/'src/fg.txt'),'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','48000',str(ROOT/'src/person_cut.mp4')],check=True)
for name,opts in [('person.mp4',['-an','-c:v','copy']),('voice.m4a',['-vn','-c:a','copy'])]:
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'src/person_cut.mp4'),*opts,str(ROOT/'assets'/name)],check=True)
print(f'{len(segments)} segments, {out_t:.3f}s from original 42.475s')
