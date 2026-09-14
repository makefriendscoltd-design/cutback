from pathlib import Path
import json,subprocess,hashlib,wave,math
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parent;o=Path('/Users/apple/Downloads/바이어_온라인_오프라인_미팅_롱폼_편집_v2_문장자막.mp4');plan=json.loads((r/'edit-plan.json').read_text());caps=json.loads((r/'captions.json').read_text());events=json.loads((r/'graphic-events.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(o)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio');assert int(v['nb_frames'])==plan['frames'];assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='25/1';assert abs(float(v['duration'])-float(a['duration']))<.05
p=subprocess.run(['ffmpeg','-v','error','-i',str(o),'-f','null','-'],capture_output=True,text=True);assert p.returncode==0 and not p.stderr,p.stderr
sync=[]
for t in [5,200,500,724]:
 arr=[]
 for k,src in enumerate([r/'cut-base.mp4',o]):
  raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(src),'-t','5','-vn','-ar','8000','-ac','1','-f','f32le','-']);x=np.frombuffer(raw,dtype='<f4').astype(float);x-=x.mean();arr.append(x)
 n=min(map(len,arr));x,y=[z[:n] for z in arr];N=1<<(2*n-1).bit_length();corr=np.fft.irfft(np.fft.rfft(x,N)*np.conj(np.fft.rfft(y,N)),N);lags=np.arange(-800,801);lag=int(lags[np.argmax(corr[lags%N])]);assert abs(lag)<=320,(t,lag);sync.append({'at':t,'lag_ms':lag/8})
times=[4,10]+[round(e['start']+3,2) for e in events[1:]]+[300,600,732]
imgs=[]
for i,t in enumerate(times):
 p=r/'qa'/f'delivery-{i:02}-{t}.jpg';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(o),'-frames:v','1',str(p)],check=True);im=Image.open(p);im.thumbnail((640,360));imgs.append(im.copy())
sheet=Image.new('RGB',(1920,math.ceil(len(imgs)/3)*360));
for i,im in enumerate(imgs):sheet.paste(im,((i%3)*640,(i//3)*360))
sheet.save(r/'qa/delivery-contact.jpg')
vol=subprocess.run(['ffmpeg','-hide_banner','-i',str(o),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True)
peak=[x.strip() for x in vol.stderr.splitlines() if 'max_volume' in x or 'mean_volume' in x]
result={'output':str(o),'bytes':o.stat().st_size,'duration':float(v['duration']),'frames':int(v['nb_frames']),'width':1920,'height':1080,'fps':25,'source_duration':plan['source_duration'],'removed_seconds':round(plan['source_duration']-plan['duration'],3),'decode_errors':0,'captions':len(caps),'caption_rows_max':1,'caption_font':'Pretendard SemiBold (libass actual fontselect verified)','caption_background_opacity':.68,'ass_font_size':50,'reference':'user screenshot 2026-09-14 supersedes CapCut numeric estimate','position':'lower picture; ASS marginV132','graphics':len(events),'sync_samples':sync,'audio_volume':peak,'speech_sample_audit':'../buyer-meeting-longform-v1/qa/cut-audio-audit.json','correction_audit':'../buyer-meeting-longform-v1/qa/correction-audio-audit.json','visual_review':'pending actual delivery contact sheet inspection'}
(r/'DELIVERY-VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
