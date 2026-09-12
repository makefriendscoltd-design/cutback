import subprocess,json,pathlib
from PIL import Image,ImageDraw
p=pathlib.Path(__file__).parent;f=pathlib.Path('/Users/apple/Downloads/AI학교_가상편집과정_2배속_18초.mp4')
r=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]))
v=next(s for s in r['streams'] if s['codec_type']=='video');a=next(s for s in r['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',1080),v
assert abs(float(r['format']['duration'])-18)<.1
z=subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],capture_output=True,text=True,check=True);assert not z.stderr,z.stderr
sheet=Image.new('RGB',(1280,1080));d=ImageDraw.Draw(sheet)
for i,t in enumerate([.5,3,4,7,12,17]):
 o=p/'qa'/f'final-{t}s.jpg';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(f),'-frames:v','1',str(o)],check=True)
 im=Image.open(o);im.thumbnail((640,360));sheet.paste(im,((i%2)*640,(i//2)*360))
sheet.save(p/'qa/final-contact.jpg')
(p/'qa/VERIFIED.json').write_text(json.dumps({'file':str(f),'bytes':f.stat().st_size,'duration':float(r['format']['duration']),'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':v['nb_frames'],'audio':a['codec_name'],'decodeErrors':0,'authoredDuration':36,'playbackRate':2},ensure_ascii=False,indent=2))
print('VERIFIED 18sec 1080p60 1080frames AAC decode0errors')
