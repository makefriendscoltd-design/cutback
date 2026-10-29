#!/usr/bin/env python3
"""Short01 v2 cuts: same single take as v1, faster pace.
- Pauses >0.28s (v1 list) plus one 0.22s pause before nasal '남겨' -> 0.07s (0.035s margin each side).
  Closure silences before stops/affricates (ㅂ ㄷ ㅈ ㅎ onsets) are left alone so first consonants stay intact.
- Whole programme then sped up with pitch-preserving atempo=TEMPO (video setpts matches, lip sync kept).
M(t) = (out_start + t - src_start) / TEMPO.
"""
from pathlib import Path
import json, subprocess
ROOT=Path(__file__).resolve().parent
TEMPO=1.12
START,END=1.52,40.40
PAD=.035
GAPS=[(3.30,3.58),(8.22,8.90),(10.64,11.26),(15.26,15.77),(22.04,22.32),
      (23.60,24.13),(27.62,28.20),(30.90,31.52),(36.38,36.81),(39.44,39.66)]
segments=[];cursor=START;out_t=0.0
for a,b in GAPS+[(END+PAD,END+PAD)]:
    end=min(a+PAD,END)
    if end>cursor:
        cursor=round(cursor*30)/30;end=round(end*30)/30;d=end-cursor
        segments.append(dict(src_start=round(cursor,3),src_end=round(end,3),out_start=round(out_t,4),out_end=round(out_t+d,4)));out_t+=d
    cursor=b-PAD
dur=round(out_t/TEMPO,3)
(ROOT/'cuts.json').write_text(json.dumps({'segments':segments,'tempo':TEMPO,'pre_tempo_duration':round(out_t,3),'duration':dur,'gaps':GAPS,'source_duration':42.475},indent=2))
n=len(segments)
f=[f"[0:v]fps=30,scale=1080:1920:flags=lanczos,setsar=1,split={n}"+''.join(f'[p{i}]' for i in range(n))]
for i,s in enumerate(segments):
    d=s['src_end']-s['src_start']
    f += [f"[p{i}]trim=start_frame={round(s['src_start']*30)}:end_frame={round(s['src_end']*30)},setpts=PTS-STARTPTS[v{i}]",
          f"[0:a]atrim={s['src_start']}:{s['src_end']},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={max(0,d-.006):.3f}:d=0.006[a{i}]"]
f.append(''.join(f'[v{i}][a{i}]' for i in range(n))+f'concat=n={n}:v=1:a=1[vc][ac]')
f.append(f'[vc]setpts=PTS/{TEMPO},fps=30[v]');f.append(f'[ac]aresample=48000,atempo={TEMPO}[a]')
(ROOT/'src/fg.txt').write_text(';'.join(f))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'src/source.mp4'),'-filter_complex_script',str(ROOT/'src/fg.txt'),'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','48000','-t',str(dur),str(ROOT/'src/person_cut.mp4')],check=True)
for name,opts in [('person.mp4',['-an','-c:v','copy']),('voice.m4a',['-vn','-c:a','copy'])]:
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'src/person_cut.mp4'),*opts,str(ROOT/'assets'/name)],check=True)
print(f'{n} segments, {out_t:.3f}s before tempo -> {dur:.3f}s at x{TEMPO}')
