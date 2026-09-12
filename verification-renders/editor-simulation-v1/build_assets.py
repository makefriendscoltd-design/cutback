import pathlib,subprocess,json,wave,array,math,random,shutil
from PIL import Image,ImageOps
r=pathlib.Path(__file__).resolve().parent;a=r/'assets';qa=r/'qa';a.mkdir(exist_ok=True);qa.mkdir(exist_ok=True);src='/Users/apple/Downloads/20260911_175145_편집본.mp4';v5=r.parent/'20260911_175145-polish-v5'
for name in ['Pretendard-Bold.ttf','gsap.min.js']:
 p=a/name
 if not p.exists():p.symlink_to((v5/'assets'/name).resolve())
def run(args):
 with (qa/'media-build.log').open('a') as log:subprocess.run(['ffmpeg','-y','-hide_banner',*args],stdout=log,stderr=subprocess.STDOUT,check=True)
run(['-ss','28','-i',src,'-t','24','-vn','-ar','8000','-ac','1',str(a/'source-wave.wav')])
with wave.open(str(a/'source-wave.wav'),'rb') as f:data=array.array('h',f.readframes(f.getnframes()))
peaks=[]
for i in range(1440):
 xs=data[i*len(data)//1440:(i+1)*len(data)//1440];peaks.append(round(min(1,max(abs(x) for x in xs)/15000),4))
(a/'waveform.json').write_text(json.dumps({'peaks':peaks,'duration':24,'source_start':28}))
run(['-ss','28','-i',src,'-t','24','-vf','fps=1/2,scale=320:180','-q:v','2',str(a/'thumb-%02d.jpg')])
strip=Image.new('RGB',(1440,76))
for i in range(12):strip.paste(ImageOps.fit(Image.open(a/f'thumb-{i+1:02d}.jpg'),(120,76)),(i*120,0))
strip.save(a/'filmstrip.jpg',quality=95)
# Preview transports: live sections while playing/scrubbing and frozen frames while trimming.
segments=[(28,90,False),(32.48,180,True),(33.4,90,False),(35.46,120,True),(36.08,90,False),(36.88,330,True),(33.324604,64,False),(36.079542,24,False),(37.323313,83,False),(40.345625,9,False)]
parts=a/'preview-parts';parts.mkdir(exist_ok=True)
for i,(start,n,freeze) in enumerate(segments):
 d=n/30;out=parts/f'{i:02d}.mov'
 if freeze:
  run(['-ss',str(start),'-i',src,'-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-filter_complex',f'[0:v]fps=30,trim=end_frame=1,scale=960:540,tpad=stop_mode=clone:stop_duration={d},trim=end_frame={n},setpts=N/(30*TB)[v]','-map','[v]','-map','1:a','-t',str(d),'-c:v','h264_videotoolbox','-b:v','5M','-c:a','pcm_s16le',str(out)])
 else:
  run(['-ss',str(start),'-i',src,'-t',str(d),'-vf',f'fps=30,scale=960:540,trim=end_frame={n},setpts=N/(30*TB)','-af',f'apad,atrim=duration={d}','-c:v','h264_videotoolbox','-b:v','5M','-c:a','pcm_s16le','-ar','48000','-ac','2',str(out)])
(parts/'list.txt').write_text(''.join(f"file '{i:02d}.mov'\n" for i in range(len(segments))))
run(['-f','concat','-safe','0','-i',str(parts/'list.txt'),'-map','0:v','-an','-c:v','copy',str(a/'preview.mp4')])
run(['-f','concat','-safe','0','-i',str(parts/'list.txt'),'-vn','-af','volume=0.6','-ar','48000','-ac','2',str(a/'preview-voice.wav')])
(r/'preview-map.json').write_text(json.dumps([{'source_start':t,'frames':n,'freeze':f} for t,n,f in segments],indent=2))
print('ASSETS_READY',flush=True)
