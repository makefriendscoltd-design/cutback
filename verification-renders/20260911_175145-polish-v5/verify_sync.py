import json,subprocess,array,math,pathlib
r=pathlib.Path(__file__).resolve().parent;p=json.load(open(r/'timeline.json'));out='/Users/apple/Downloads/20260911_175145_홍보삽입_줌_재조명_v5.mp4'
def audio(path,t):
 return array.array('f',subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(path),'-t','1','-vn','-ac','1','-ar','16000','-f','f32le','-']))
def corr(a,b,k):
 a=a[2000:12000:8];b=b[2000+k:12000+k:8];ma=sum(a)/len(a);mb=sum(b)/len(b)
 return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
sharp=r.parent/'20260911_175145-polish-v4/assets/presenter-sharp.mp4';results=[]
for name,src,t,u in [('opening',sharp,11,11),('promo',p['promo_path'],15,15+p['promo_start']),('introduction',sharp,23,23+p['downstream_shift']),('ending',sharp,205,205+p['downstream_shift'])]:
 a=audio(src,t);b=audio(out,u);score,lag=max((corr(a,b,k),k) for k in range(-1600,1601,8));score,lag=max((corr(a,b,k),k) for k in range(lag-7,lag+8));assert score>.95 and abs(lag/16)<16.6834,(name,score,lag);results.append({'segment':name,'audio_correlation':score,'lag_ms':lag/16})
(r/'sync-verification.json').write_text(json.dumps(results,indent=2));print(results)
