"""Scan upper graphic region (0-1130px) for holds >0.5s. Block-based so small element motion counts."""
import subprocess,sys,json,numpy as np
p=sys.argv[1];a,b=float(sys.argv[2]),float(sys.argv[3]);w,h=216,102
raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(a),'-to',str(b),'-i',p,'-vf',f'crop=2160:2260:0:0,scale={w}:{h}','-f','rawvideo','-pix_fmt','gray','-'])
fr=np.frombuffer(raw,np.uint8).reshape(-1,h,w).astype(np.int16);d=np.abs(np.diff(fr,axis=0))
blk=d.reshape(len(d),6,17,6,36).mean(axis=(2,4)).max(axis=(1,2))  # max block-mean diff per frame
still=blk<1.5;runs=[];n=0
for i,s in enumerate(still):
 n=n+1 if s else 0
 if n and (i+1==len(still) or not still[i+1]):runs.append((n,i+1-n))
runs.sort(reverse=True);out=[{'frames':r,'seconds':round(r/30,2),'at':round(a+f/30,2)} for r,f in runs[:6]]
res={'range':[a,b],'frames':len(fr),'longest_holds':out,'pass':all(r['frames']<=15 for r in out)};print(json.dumps(res));open(p.rsplit('.',1)[0]+'.holds.json','w').write(json.dumps(res,indent=1))
