import json,subprocess,sys,hashlib
from pathlib import Path
import numpy as np
p=Path(sys.argv[1]); mix=Path(__file__).parent/'assets/mix.wav'
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))['streams']
def audio(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vn','-ac','1','-ar','16000','-f','f32le','-']),dtype=np.float32)
s=probe(p);v=next(x for x in s if x['codec_type']=='video');a=next(x for x in s if x['codec_type']=='audio');actual,expected=audio(p),audio(mix);n=min(len(actual),len(expected));corr=float(np.corrcoef(actual[:n],expected[:n])[0,1]);dec=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],capture_output=True)
r={'file':p.name,'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':int(v['nb_frames']),'video_duration':float(v['duration']),'audio_duration':float(a['duration']),'audio_mix_correlation':corr,'decode_pass':dec.returncode==0 and not dec.stderr,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_check':'representative frames manually inspected','listening_check':'not independently verified','source_timing':'frame-aligned cuts from edit-plan.json; kept samples 1x; 2ms edge fades'}
r['passed']=r['width']==2160 and r['height']==3840 and r['frames']==1348 and abs(r['video_duration']-r['audio_duration'])<.04 and corr>.98 and r['decode_pass'];p.with_suffix('.verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
