import json, subprocess, pathlib, array, math, argparse
from PIL import Image, ImageDraw, ImageStat, ImageChops
parser=argparse.ArgumentParser();parser.add_argument('--version',default='v1',choices=['v1','v2','v3','v4','v5']);args=parser.parse_args()
r=pathlib.Path(__file__).resolve().parents[1];p=json.loads((r/('edit-plan.json' if args.version=='v1' else f'edit-plan-{args.version}.json')).read_text());out=r/f'day1-sc-vlog-{args.version}.mp4';vdir=r/'verification'/args.version;vdir.mkdir(exist_ok=True)
def run(a): return subprocess.check_output(a)
m=json.loads(run(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(out)]));v=next(x for x in m['streams'] if x['codec_type']=='video');a=next(x for x in m['streams'] if x['codec_type']=='audio')
assert v['width']==1080 and v['height']==1920 and v['r_frame_rate']=='30/1'
assert abs(float(m['format']['duration'])-49.6)<.1
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True,stderr=open(vdir/'decode-errors.log','w'))
sheet=Image.new('RGB',(6*180,4*350),'#222');d=ImageDraw.Draw(sheet);stats=[]
for i,s in enumerate(p['shots']):
 t=s['output_start']+s['duration']/2;f=vdir/f'shot-{i+1:02}.jpg';run(['ffmpeg','-v','error','-ss',str(t),'-i',str(out),'-frames:v','1','-vf','scale=180:320','-y',str(f)]);im=Image.open(f);st=ImageStat.Stat(im.convert('L'));assert st.mean[0]>10 and st.stddev[0]>10
 sheet.paste(im,((i%6)*180,(i//6)*350+25));d.text(((i%6)*180+4,(i//6)*350+5),f'{i+1:02} {t:.2f}s',fill='white');stats.append({'shot':i+1,'time':t,'luma':st.mean[0],'contrast':st.stddev[0]})
sheet.save(vdir/'render-contact.jpg')
for i,s in enumerate(p['shots']):
 ims=[]
 for k,t in enumerate([s['output_start']+.04,s['output_start']+s['duration']-.06]):
  f=vdir/f'motion-{i+1:02}-{k}.jpg';run(['ffmpeg','-v','error','-ss',str(t),'-i',str(out),'-frames:v','1','-vf','scale=90:160','-y',str(f)]);ims.append(Image.open(f).convert('RGB'))
 delta=sum(ImageStat.Stat(ImageChops.difference(*ims)).mean)/3
 stats[i]['motion_pixel_mean_difference']=delta
 assert delta>.2,('possible frozen shot',i+1,delta)

def pcm(path):
 b=run(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar','8000','-f','f32le','-']);x=array.array('f');x.frombytes(b);return x
x=pcm(out);y=pcm(r/'audio-prep/voice.wav');n=min(len(x),len(y));xy=sum(x[i]*y[i] for i in range(n));corr=xy/math.sqrt(sum(t*t for t in x[:n])*sum(t*t for t in y[:n]));assert corr>.97,corr
report={'duration':m['format']['duration'],'video':{'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':v.get('nb_frames')},'audio_codec':a['codec_name'],'audio_correlation_to_clean_voice':corr,'cuts':len(p['shots']),'source_files':len(set(s['source'] for s in p['shots'])),'decode_passed':True,'shot_luminance_checks':stats,'listening':'unverified; waveform and decoded audio checked'}
(vdir/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='shot_luminance_checks'},indent=2))
