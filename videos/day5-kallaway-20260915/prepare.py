from pathlib import Path
import json,subprocess
import numpy as np
R=Path(__file__).resolve().parent;A=R/'assets';ROOT=R.parents[1];sr=48000
plan=json.loads((R/'edit-plan.json').read_text());D=plan['duration'];st=json.loads((R/'audio-settings.json').read_text())
timing=json.loads((R/'timing.json').read_text());SFX=Path('/Users/apple/.agents/skills/media-use/audio/assets/sfx')
def pcm(p,loop=False):
 args=['ffmpeg','-v','error']+(['-stream_loop','-1']if loop else[])+['-i',str(p),'-t',str(D),'-vn','-ar',str(sr),'-ac','2','-f','f32le','-'];return np.frombuffer(subprocess.check_output(args),dtype=np.float32).reshape(-1,2).copy()
n=round(D*sr);v=pcm(A/'voice-cut.wav')[:n];bg=pcm(ROOT/'verification-renders/20260911_180156-r01-v14/assets/bgm-dark-fast-128bpm.wav',True)[:n];bg*=10**(st['bgm_rms_dbfs']/20)/np.sqrt(np.mean(bg**2));bg[-sr:]*=np.linspace(1,0,sr)[:,None]
# kind -> (file, peak, pre-roll seconds)
KINDS={'whoosh':('whoosh-cinematic.mp3',st['sfx_target_peak'],.45),'click':('click-soft.mp3',.12,0),'pop':('pop.mp3',.16,0),'typing':('typing.mp3',.08,0)}
sfx=np.zeros_like(v);used={}
for kind,(f,peak,pre) in KINDS.items():
 ev=timing.get(kind,[])
 if not ev:continue
 x=pcm(SFX/f);x*=peak/max(np.max(np.abs(x)),1e-6)
 if kind=='typing':x=x[:int(1.1*sr)];x[-int(.1*sr):]*=np.linspace(1,0,int(.1*sr))[:,None]
 for t in ev:
  s0=max(0,round((t-pre)*sr));c=min(len(x),n-s0)
  if c>0:sfx[s0:s0+c]+=x[:c]
 used[kind]={'file':f,'peak':peak,'events':ev}
mix=v+bg+sfx;peak=np.max(np.abs(mix));gain=min(1,.97/peak);mix*=gain
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(sr),'-ac','2','-i','-','-c:a','pcm_s24le',str(A/'mix.wav')],input=mix.astype(np.float32).tobytes(),check=True)
(R/'audio-plan.json').write_text(json.dumps({'duration':D,'music_rms_dbfs':st['bgm_rms_dbfs'],'sfx':used,'output_gain':float(gain),'output_peak':float(np.max(np.abs(mix)))},indent=2,ensure_ascii=False))
print('duration',D,'gain',round(gain,3),{k:len(v['events']) for k,v in used.items()})
