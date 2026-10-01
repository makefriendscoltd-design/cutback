"""Episode 7 source-specific cuts. Preserve words; shorten only measured inter-sentence silence."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parent
START,END=4.80,67.10
# RMS valleys cross-checked against both VAD/non-VAD word timestamps.
# Sentence pauses plus incomplete takes; use the later complete takes.
GAPS=[(10.68,11.04),(19.40,19.87),(20.39,20.73),(21.51,24.76),(30.10,30.43),(38.26,47.36),(55.06,55.30)]
segments=[];cursor=START;t=0
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
print(f'{len(segments)} segments, {t:.3f}s from original 69.611s')
