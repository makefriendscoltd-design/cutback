#!/usr/bin/env python3
"""Semantic-cue mix; EP02 stem calibration + EP05 shared timeline events.
No source voice edits. Build-generated event times are the only timing authority.
"""
from pathlib import Path
import json,subprocess,re,os,hashlib
R=Path(__file__).resolve().parent;Q=R/'qc/audio';Q.mkdir(parents=True,exist_ok=True)
LIB=Path(os.environ.get('OWEN_AUDIO_DIR','/Users/apple/orca/projects/cutback/videos/_assets/audio-eleven-20260920'))
DUR=json.loads((R/'cuts.json').read_text())['duration'];raw=(R/'events.json').read_bytes();events=json.loads(raw);cues=events['actions']
assert not (R/'assets/mix.m4a').is_symlink(),'Never write through an original mix symlink'
def run(args):return subprocess.run(args,capture_output=True,text=True,check=True)
def level(p):
 x=run(['ffmpeg','-hide_banner','-nostats','-i',str(p),'-af','loudnorm=I=-14:TP=-1:LRA=7:print_format=json','-f','null','-']).stderr
 return json.loads(re.search(r'\{\s*"input_i".*?\}',x,re.S).group())
voice=Q/'voice.wav';bed=Q/'bed.wav';sfx=Q/'sfx.wav';pre=Q/'premix.wav'
run(['ffmpeg','-v','error','-y','-i',str(R/'assets/voice.m4a'),'-af','loudnorm=I=-16:TP=-2:LRA=11,apad','-t',str(DUR),'-ar','48000','-ac','2',str(voice)])
bed_src=level(LIB/'bed-ambient-tech-33s.wav');bed_gain=-28-float(bed_src['input_i'])
run(['ffmpeg','-v','error','-y','-stream_loop','-1','-i',str(LIB/'bed-ambient-tech-33s.wav'),'-i',str(voice),'-filter_complex',f'[0:a]atrim=0:{DUR},aformat=sample_rates=48000:channel_layouts=stereo,volume={bed_gain}dB,afade=t=in:d=0.8,afade=t=out:st={DUR-1.5}:d=1.5[b];[b][1:a]sidechaincompress=threshold=0.05:ratio=2:attack=20:release=300[out]','-map','[out]','-ar','48000','-t',str(DUR),str(bed)])
args=[];filters=[];labels=[]
for i,c in enumerate(cues):
 assert 0<=c['time']<DUR and (LIB/(c['sound']+'.wav')).exists(),c
 args+=['-i',str(LIB/(c['sound']+'.wav'))]
 delay=round(c['time']*1000);filters.append(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={c["gain_db"]}dB,adelay={delay}|{delay}[s{i}]');labels.append(f'[s{i}]')
filters.append(''.join(labels)+f'amix=inputs={len(cues)}:normalize=0:duration=longest,apad,atrim=0:{DUR}[out]')
run(['ffmpeg','-v','error','-y',*args,'-filter_complex',';'.join(filters),'-map','[out]','-ar','48000',str(sfx)])
run(['ffmpeg','-v','error','-y','-i',str(voice),'-i',str(bed),'-i',str(sfx),'-filter_complex','[0:a][1:a][2:a]amix=inputs=3:normalize=0:duration=first[out]','-map','[out]',str(pre)])
measured=level(pre);gain=-14-float(measured['input_i'])
run(['ffmpeg','-v','error','-y','-i',str(pre),'-af',f'volume={gain}dB,alimiter=limit=0.84:level=false,apad','-t',str(DUR),'-ar','48000','-c:a','aac','-b:a','256k',str(R/'assets/mix.m4a')])
levels={name:level(path) for name,path in [('voice',voice),('bed',bed),('sfx',sfx),('final',R/'assets/mix.m4a')]}
report={'events_sha256':hashlib.sha256(raw).hexdigest(),'cue_count':len(cues),'cues':cues,'bed_source_lufs':bed_src['input_i'],'bed_gain_db':bed_gain,'master_gain_db':gain,'levels':levels,'voice_minus_bed_lufs':round(float(levels['voice']['input_i'])-float(levels['bed']['input_i']),2)}
assert report['voice_minus_bed_lufs']>=12
assert -14.6<float(levels['final']['input_i'])<-13.4
assert float(levels['final']['input_tp'])<=-1
(Q/'mix-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'cue_count':len(cues),'lufs':levels['final']['input_i'],'true_peak':levels['final']['input_tp'],'voice_minus_bed':report['voice_minus_bed_lufs']},ensure_ascii=False))
