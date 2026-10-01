"""Existing Owen audio library, edited voice ducking and source-timed effects."""
from pathlib import Path
import json,subprocess,os
ROOT=Path(__file__).resolve().parent
LIB=Path(os.environ.get('OWEN_AUDIO_DIR','/Users/apple/orca/projects/cutback/videos/_assets/audio-eleven-20260920'))
DUR=json.loads((ROOT/'cuts.json').read_text())['duration'];E=json.loads((ROOT/'events.json').read_text())
sfx=[(0,'impact-low-hook',-8)]
for sid,(st,du,kind) in E['scenes'].items():
 if st>.05:
  sfx.append((st,'whoosh-short-cut',-14))
  if kind!='ovl':sfx.append((st+.06,'ui-panel-appear',-11))
for t in E['ticks']:sfx.append((t,'ui-tick',-10))
sfx.append((DUR-1.55,'ping-comment',-9));sfx.sort()
args=['-i',str(ROOT/'assets/voice.m4a'),'-stream_loop','-1','-i',str(LIB/'bed-ambient-tech-33s.wav')]
for t,n,g in sfx:args+=['-i',str(LIB/(n+'.wav'))]
f=['[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[voice][sc]',f'[1:a]atrim=0:{DUR},aformat=sample_rates=48000:channel_layouts=stereo,volume=-3dB,afade=t=in:d=0.7,afade=t=out:st={DUR-1.5}:d=1.5[bed0]','[bed0][sc]sidechaincompress=threshold=0.1:ratio=2:attack=20:release=300[bed]']
for i,(t,n,g) in enumerate(sfx):f.append(f'[{i+2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={round(t*1000)}|{round(t*1000)}[s{i}]')
f.append('[voice][bed]'+''.join(f'[s{i}]' for i in range(len(sfx)))+f'amix=inputs={len(sfx)+2}:normalize=0:duration=first[m]');f.append('[m]loudnorm=I=-14:TP=-1.0:LRA=7[out]')
subprocess.run(['ffmpeg','-v','error','-y',*args,'-filter_complex',';'.join(f),'-map','[out]','-t',str(DUR),'-ar','48000','-c:a','aac','-b:a','256k',str(ROOT/'assets/mix.m4a')],check=True)
print('Mixed',len(sfx),'SFX',DUR,'seconds')
