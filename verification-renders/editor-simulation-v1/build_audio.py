import array, math, random, wave, json, subprocess
from pathlib import Path
p=Path(__file__).parent; sr=48000; rng=random.Random(815); out=array.array('f',[0])*(sr*36)
clicks=[1.05,3.5,4.2,4.75,5.65,10,10.85,11.8,16.75,17.45,18.45,22.8,27.65,30.0]
for at in clicks+[7.05,13.05,19.2,24.25,28.15]:
 d=.045 if at in clicks else .12
 for j in range(int(d*sr)):
  t=j/sr; s=(rng.gauss(0,1)*.045+math.sin(2*math.pi*1200*t)*.07)*math.exp(-t*(150 if at in clicks else 65));out[int(at*sr)+j]+=s
pcm=array.array('h')
for x in out:
 v=int(max(-1,min(1,x))*32767);pcm.extend((v,v))
with wave.open(str(p/'assets/editor-sfx.wav'),'wb') as f:
 f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm.tobytes())
subprocess.run(['ffmpeg','-y','-v','error','-i',str(p/'assets/preview-voice.wav'),'-i',str(p/'assets/editor-sfx.wav'),'-filter_complex','[0:a][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=0[a]','-map','[a]','-t','36',str(p/'assets/editor-mix.wav')],check=True)
(p/'assets/audio-ledger.json').write_text(json.dumps({'sfx':'Original deterministic synthesized mouse clicks, key taps and snap tones','seed':815,'voice':'Original user-owned source recording, actual preview-map','duration':36,'finalPlaybackRate':2},ensure_ascii=False,indent=2))
print('AUDIO_READY')
