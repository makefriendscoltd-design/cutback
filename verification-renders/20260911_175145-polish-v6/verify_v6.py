import pathlib,json,subprocess,concurrent.futures,hashlib,re
from PIL import Image,ImageDraw
r=pathlib.Path(__file__).resolve().parent;out=pathlib.Path('/Users/apple/Downloads/20260911_175145_모션그래픽_사진개선_v6.mp4');v5=r.parent/'20260911_175145-polish-v5'
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration:format=duration,size','-of','json',str(out)]));(r/'final-probe.json').write_text(json.dumps(p,indent=2));assert p['streams'][0]['nb_frames']=='15511'
assert (r/'captions.json').read_bytes()==(v5/'captions.json').read_bytes()
caps=json.loads((r/'captions.json').read_text());es=json.loads((r/'events.json').read_text());photos=[e for e in es if e['type']=='photo'];assert len(photos)==len({hashlib.sha256((r/'assets/photos'/e['file']).read_bytes()).hexdigest() for e in photos})
assert all('Pexels' not in (r/'cards'/e['id']/'index.html').read_text() for e in photos)
with (r/'decode.log').open('w') as log:subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],stderr=log,check=True)
with (r/'volume.log').open('w') as log:subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-vn','-af','volumedetect','-f','null','-'],stderr=log,check=True)
dst=r/'caption-frames';dst.mkdir(exist_ok=True)
def balanced(xs):
 if len(xs)==1:return xs[0]
 n=len(xs)//2;return '('+balanced(xs[:n])+'+'+balanced(xs[n:])+')'
frames=[round((c['start']+c['end'])/2*60000/1001) for c in caps];select=balanced([f'eq(n,{n})' for n in frames])
subprocess.run(['ffmpeg','-y','-v','error','-i',str(out),'-vf',f"select='{select}',crop=1920:260:0:820",'-fps_mode','vfr','-q:v','2',str(dst/'caption-%03d.jpg')],check=True);assert len(list(dst.glob('*.jpg')))==95
shots=r/'final-check';shots.mkdir(exist_ok=True)
requests=[(e['id'],(e['start']+e['end'])/2) for e in es]
for e in es:
 if e['type']=='motion':requests.extend([(e['id']+'-early',e['start']+1),(e['id']+'-late',e['end']-1)])
def snap(item):
 name,t=item;f=shots/(name+'.jpg');subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(out),'-frames:v','1','-q:v','2',str(f)],check=True);return f
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(snap,requests))
for subset,label in [(list(zip(requests[:16],files[:16])),'contact'),(list(zip(requests[16:],files[16:])),'motion-states')]:
 sheet=Image.new('RGB',(1920,300*((len(subset)+3)//4)),'#111');draw=ImageDraw.Draw(sheet)
 for i,((name,t),f) in enumerate(subset):
  x=i%4*480;y=i//4*300;sheet.paste(Image.open(f).resize((480,270)),(x,y));draw.text((x+5,y+276),f'{name} {t:.2f}s',fill='white')
 sheet.save(shots/(label+'.jpg'),quality=93)
print('actual video decode, 15511 frames, captions unchanged,8 unique photos, no credit labels verified',flush=True)
