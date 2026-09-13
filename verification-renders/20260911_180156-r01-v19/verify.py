import json,subprocess
from pathlib import Path
from array import array
import math
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;V=R/'AI학교_01_자막검정그림자_v19.mp4'
E=json.loads((R/'body-retime-edl.json').read_text());D=E['output_frames']/30
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(V)]));v=next(x for x in p['streams']if x['codec_type']=='video');a=next(x for x in p['streams']if x['codec_type']=='audio')
assert int(v['nb_frames'])==E['output_frames'] and (v['width'],v['height'])==(1080,1920)
assert abs(float(v['duration'])-D)<.001 and abs(float(a['duration'])-D)<.03
subprocess.run(['ffmpeg','-v','error','-i',str(V),'-f','null','-'],check=True)
def pcm(path):return array('f',subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ar','48000','-ac','1','-f','f32le','-']))
x=pcm(V);y=pcm(R/'assets/mix.wav');n=min(len(x),len(y));corr=sum(a*b for a,b in zip(x,y))/math.sqrt(sum(a*a for a in x[:n])*sum(b*b for b in y[:n]));assert corr>.98,corr
d=R/'verification';d.mkdir(exist_ok=True);canvas=Image.new('RGB',(1260,350),'#151515')
for i,t in enumerate([0,0.7,1.1,3,8.4,12,D-0.4]):
 f=d/f'frame-{i}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(V),'-frames:v','1',str(f)],check=True);im=Image.open(f);im.thumbnail((180,320));canvas.paste(im,(i*180,25));ImageDraw.Draw(canvas).text((i*180+5,5),f'{t}s',fill='white')
canvas.save(d/'contact.jpg');(R/'delivery-verification.json').write_text(json.dumps({'output':str(V),'duration':D,'frames':E['output_frames'],'resolution':[1080,1920],'full_decode':'passed','encoded_audio_mix_correlation':corr,'visual_review':'pending','head_ends':1,'first_spoken_caption':0.0667,'audio_evidence':'dark-audio-analysis.json','listening':'unverified'},indent=2));print('verified',corr)
