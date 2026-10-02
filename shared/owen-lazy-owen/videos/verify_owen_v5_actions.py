#!/usr/bin/env python3
"""Extract actual encoded action triplets and measure encoded audio alignment."""
from pathlib import Path
import json,subprocess,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw
r=Path(sys.argv[1]).resolve();q=r/'qc';v=next((r/'renders').glob('*v5.mp4'));e=json.loads((r/'events.json').read_text());dur=json.loads((r/'cuts.json').read_text())['duration']
def pcm(p):return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',str(p),'-vn','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout,dtype=np.float32).astype(float)
a=pcm(v);b=pcm(r/'assets/mix.m4a');n=min(len(a),len(b));a=a[:n];b=b[:n];size=1<<(2*n-1).bit_length();c=np.fft.irfft(np.fft.rfft(a,size)*np.conj(np.fft.rfft(b,size)),size);lags=np.arange(-1600,1601);lag=int(lags[np.argmax(c[lags%size])]);aa=a[max(0,lag):min(n,n+lag)];bb=b[max(0,-lag):min(n,n-lag)];corr=float(np.corrcoef(aa,bb)[0,1]);assert abs(lag)<=16000/30 and corr>.98
items=[(x['name'],x['time']) for x in e['actions'] if x['scene']!='main' and not x['name'].endswith('_entrance')]
for k in range(0,len(items),4):
 batch=items[k:k+4];im=Image.new('RGB',(810,len(batch)*505),'#111827');d=ImageDraw.Draw(im)
 for row,(name,t) in enumerate(batch):
  for col,off in enumerate((-.08,.16,.48)):
   at=max(0,min(dur-.06,t+off));out=q/f'action-{k+row:02}-{col}.jpg';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(at),'-i',str(v),'-frames:v','1','-vf','scale=270:480',str(out)],check=True);im.paste(Image.open(out),(col*270,row*505+25));d.text((col*270+4,row*505+5),f'{name} {at:.2f}s',fill='white')
 im.save(q/f'action-review-{k//4}.jpg',quality=92)
report={'lag_ms':round(lag/16,3),'correlation':round(corr,6),'semantic_actions':len(items),'mix_hash_matches':hashlib.sha256((r/'events.json').read_bytes()).hexdigest()==json.loads((q/'audio/mix-report.json').read_text())['events_sha256'],'direct_listening':'not performed'}
assert report['mix_hash_matches'];(q/'action-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
