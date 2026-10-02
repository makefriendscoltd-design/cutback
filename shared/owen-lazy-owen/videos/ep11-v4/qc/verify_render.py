from pathlib import Path
import json,subprocess,re,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else R/'renders/AI학교_6탄_Mantis_Owen_v1.mp4';Q=R/'qc'/sys.argv[2] if len(sys.argv)>2 else R/'qc';Q.mkdir(exist_ok=True)
def run(a):return subprocess.run(a,capture_output=True,text=True,check=True)
p=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,duration,nb_frames','-of','json',str(out)]).stdout)
v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'])==(1080,1920,'30/1')
expected=json.loads((R/'cuts.json').read_text())['duration'];assert abs(float(p['format']['duration'])-expected)<.08
assert abs(float(v['duration'])-float(a['duration']))<.08
r=run(['ffmpeg','-v','error','-i',str(out),'-f','null','-']);assert not r.stderr.strip()
audio=run(['ffmpeg','-hide_banner','-nostats','-i',str(out),'-vn','-af','loudnorm=I=-14:TP=-1:LRA=7:print_format=json','-f','null','-'])
m=json.loads(re.search(r'\{\s*"input_i".*?\}',audio.stderr,re.S).group());assert -15<float(m['input_i'])<-13;assert float(m['input_tp'])<=-.8
sc=json.loads((R/'timing.json').read_text())['scenes'];times=[round(t+d/2,3) for t,d,_ in sc.values()]+[expected-.12]
rows=(len(times)+3)//4;sheet=Image.new('RGB',(1080,rows*505),'#111827');draw=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
 path=Q/f'final-{i:02}.jpg';run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(out),'-frames:v','1','-vf','scale=270:480',str(path)])
 sheet.paste(Image.open(path),(i%4*270,i//4*505+25));draw.text((i%4*270+8,i//4*505+6),f'{t:.2f}s',fill='white')
sheet.save(Q/'final-contact-sheet.jpg',quality=90)
report={'probe':p,'expected_duration':expected,'decode_errors':0,'audio':m,'scene_midpoints':times,'captions':json.loads((R/'qc/caption-audit.json').read_text()).get('totals',{})}
(Q/'render-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'duration':p['format']['duration'],'size_MB':round(int(p['format']['size'])/1e6,2),'frames':v.get('nb_frames'),'lufs':m['input_i'],'true_peak':m['input_tp'],'decode_errors':0},ensure_ascii=False))
