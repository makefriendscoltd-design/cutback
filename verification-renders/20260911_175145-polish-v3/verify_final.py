import pathlib,json,subprocess,concurrent.futures,re
from PIL import Image,ImageOps,ImageDraw,ImageFont
r=pathlib.Path(__file__).resolve().parent;out=pathlib.Path('/Users/apple/Downloads/20260911_175145_선명보정_이미지_자막_v3.mp4');dst=r/'final-check';dst.mkdir(exist_ok=True)
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,duration,nb_frames:format=duration,size','-of','json',str(out)]))
(r/'final-probe.json').write_text(json.dumps(p,indent=2))
with open(r/'decode.log','w') as log:subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],stderr=log,check=True)
with open(r/'final-volume.log','w') as log:subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-af','volumedetect','-vn','-f','null','-'],stderr=log,check=True)
caps=json.loads((r/'captions.json').read_text());font=ImageFont.truetype(str(r/'assets/Pretendard-Bold.ttf'),66)
maxw=max(font.getlength(line) for c in caps for line in c['lines']);assert maxw<1640
assert all(len(c['lines'])<=2 for c in caps)
assert all(c['end']<=caps[i+1]['start']+.001 for i,c in enumerate(caps[:-1]))
assert p['streams'][0]['nb_frames']=='12577'
assert not (r/'decode.log').read_text().strip()
ts=[1,28.5,34,56,82,94,128,142,159,180,187,208]
def snap(t):
 f=dst/f'{t}.jpg';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(out),'-frames:v','1','-q:v','2',str(f)],check=True);return f
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:fs=list(pool.map(snap,ts))
sheet=Image.new('RGB',(1440,4*300),'#111');draw=ImageDraw.Draw(sheet)
for i,(t,f) in enumerate(zip(ts,fs)):
 x=(i%3)*480;y=(i//3)*300;im=ImageOps.fit(Image.open(f),(480,270));sheet.paste(im,(x,y));draw.text((x+10,y+276),f'{t}s',fill='white')
sheet.save(dst/'contact-sheet.jpg',quality=90)
report={'output':str(out),'duration':p['format']['duration'],'frames':12577,'decode_errors':0,'caption_count':len(caps),'max_caption_lines':max(len(c['lines']) for c in caps),'max_caption_width_at_66px':round(maxw,1),'picture_events':len(json.loads((r/'events.json').read_text())),'voice_and_person':'same approved timeline, luma sharpening only; no face reconstruction','visual_inspection':'contact-sheet.jpg and selected full frames pending root review','manual_listening':'not performed; full decode and audio peak checks performed'}
(r/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
