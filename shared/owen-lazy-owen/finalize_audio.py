#!/usr/bin/env python3
"""Keep the validated Owen mix intact instead of renderer-side audio processing."""
from pathlib import Path
import argparse,subprocess,json,re,os
p=argparse.ArgumentParser();p.add_argument('project',type=Path);p.add_argument('video',type=Path);a=p.parse_args()
r=a.project.resolve();video=a.video.resolve();mix=r/'assets/mix.m4a'
s=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(mix),'-af','loudnorm=I=-14:TP=-1:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
m=json.loads(re.search(r'\{\s*"input_i".*?\}',s,re.S).group())
if not (-15<float(m['input_i'])<-13 and float(m['input_tp'])<=-.8):
 raise SystemExit('Source mix fails loudness gate; revise mix before finalization: '+json.dumps(m))
dur=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=duration','-of','default=nw=1:nk=1',str(video)],capture_output=True,text=True,check=True).stdout.strip()
tmp=video.with_name(video.stem+'.audio-final.tmp.mp4')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-i',str(mix),'-map','0:v:0','-map','1:a:0','-c','copy','-t',dur,'-movflags','+faststart',str(tmp)],check=True)
os.replace(tmp,video)
print(json.dumps({'source_mix_lufs':m['input_i'],'source_mix_dbtp':m['input_tp'],'video_stream_copy':True,'audio_stream_copy':True}))
