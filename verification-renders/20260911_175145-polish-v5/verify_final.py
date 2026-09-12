import pathlib,json,subprocess,concurrent.futures
from PIL import Image,ImageOps,ImageDraw
r=pathlib.Path(__file__).resolve().parent;out=pathlib.Path('/Users/apple/Downloads/20260911_175145_홍보삽입_줌_재조명_v5.mp4')
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration:format=duration,size','-of','json',str(out)]));(r/'final-probe.json').write_text(json.dumps(p,indent=2))
assert p['streams'][0]['nb_frames']=='15511'
with open(r/'decode.log','w') as log:subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],stderr=log,check=True)
with open(r/'final-volume.log','w') as log:subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-vn','-af','volumedetect','-f','null','-'],stderr=log,check=True)
caps=json.loads((r/'captions.json').read_text());dst=r/'caption-frames';dst.mkdir(exist_ok=True)
frames=[round((c['start']+c['end'])/2*60000/1001) for c in caps]
def balanced(items):
 if len(items)==1:return items[0]
 mid=len(items)//2;return '('+balanced(items[:mid])+'+'+balanced(items[mid:])+')'
select=balanced([f'eq(n,{n})' for n in frames])
subprocess.run(['ffmpeg','-y','-v','error','-i',str(out),'-vf',f"select='{select}',crop=1920:260:0:820",'-fps_mode','vfr','-q:v','2',str(dst/'caption-%03d.jpg')],check=True)
assert len(list(dst.glob('*.jpg')))==len(caps)
shots=r/'final-check';shots.mkdir(exist_ok=True)
ts=[1.2,5.3,21.4,23,45,70.8,71.7,73.45,75.15,104,229,258]
def snap(t):
 f=shots/f'{t}.jpg';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(out),'-frames:v','1','-q:v','2',str(f)],check=True);return f
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(snap,ts))
sheet=Image.new('RGB',(1440,1200),'#111');draw=ImageDraw.Draw(sheet)
for i,(t,f) in enumerate(zip(ts,files)):
 x=i%3*480;y=i//3*300;sheet.paste(ImageOps.fit(Image.open(f),(480,270)),(x,y));draw.text((x+8,y+276),f'{t}s',fill='white')
sheet.save(shots/'contact.jpg',quality=92)
print('decode passed; original frame count preserved; extracted',len(caps),'actual caption frames')
