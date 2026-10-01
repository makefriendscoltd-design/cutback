#!/usr/bin/env python3
"""Render the unmodified approved composition against synthetic media in isolation."""
from pathlib import Path
import tempfile,shutil,subprocess,os,json,sys
root=Path(__file__).resolve().parent
work=Path(tempfile.mkdtemp(prefix='owen-shared-smoke-'))/'package'
shutil.copytree(root,work,ignore=shutil.ignore_patterns('.venv','__pycache__','renders','.hyperframes','node_modules'))
ep=work/'videos/ep07-v3';a=ep/'assets';duration=json.loads((ep/'cuts.json').read_text())['duration']
def run(cmd,**kw):subprocess.run(cmd,check=True,**kw)
run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=c=0x42566b:s=1920x1080:r=30:d={duration}','-vf','drawgrid=w=120:h=120:t=3:c=white@0.3','-an','-c:v','libx264','-preset','ultrafast','-threads','2','-pix_fmt','yuv420p',str(a/'person.mp4')])
run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f'sine=frequency=330:sample_rate=48000:duration={duration}','-ac','2','-c:a','aac',str(a/'voice.m4a')])
env=dict(os.environ,OWEN_AUDIO_DIR=str(work/'assets/audio'))
run([sys.executable,str(ep/'build.py')]);run([sys.executable,str(ep/'mix.py')],env=env)
run([sys.executable,str(work/'videos/check_owen_camera.py'),str(ep)])
run(['node',str(ep/'qc/caption-audit.mjs')])
with (ep/'qc/check.json').open('w') as f:run(['npx','--yes','hyperframes@0.8.103','check','--json'],cwd=ep,stdout=f)
run([sys.executable,str(work/'videos/render_serial.py'),'--project',str(ep),'--output','renders/synthetic-smoke.mp4'])
run([sys.executable,str(root/'finalize_audio.py'),str(ep),str(ep/'renders/synthetic-smoke.mp4')])
run([sys.executable,str(ep/'qc/verify_render.py'),str(ep/'renders/synthetic-smoke.mp4')])
print(json.dumps({'synthetic_only':True,'directory':str(work),'result':str(ep/'qc/render-verification.json')}))
