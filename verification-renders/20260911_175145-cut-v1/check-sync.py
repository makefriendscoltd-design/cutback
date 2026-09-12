import numpy as np,subprocess,json,pathlib
r=pathlib.Path(__file__).resolve().parent;p=json.load(open(r/'edit-plan.json'));sr=16000
src='/Users/apple/Downloads/20260911_175145_편집본.mp4';out='/Users/apple/Downloads/20260911_175145_컷편집_v1.mp4'
def wav(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',f,'-vn','-ac','1','-ar',str(sr),'-f','f32le','-']),dtype=np.float32)
a=wav(src);b=wav(out);rows=[]
for i,c in enumerate(p['clips']):
 mid=c['duration']/2;size=min(3200,int(c['duration']*sr/2));u=int((c['source_start']+mid)*sr);v=int((c['start']+mid)*sr)
 x=a[u:u+size];best=(-1,0)
 for shift in range(-320,321):
  y=b[v+shift:v+shift+size]
  if len(y)!=len(x):continue
  score=float(np.dot(x,y)/(np.linalg.norm(x)*np.linalg.norm(y)+1e-12))
  if score>best[0]:best=(score,shift)
 rows.append(dict(clip=i,correlation=best[0],offset_ms=best[1]/16))
(r/'audio-source-verification.json').write_text(json.dumps(rows,indent=2))
print('clips',len(rows),'min correlation',min(x['correlation'] for x in rows),'max offset ms',max(abs(x['offset_ms']) for x in rows))
assert min(x['correlation'] for x in rows)>.95
