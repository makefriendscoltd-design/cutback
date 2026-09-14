from pathlib import Path
import subprocess,sys,shutil,json,hashlib
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()

r=Path(__file__).resolve().parent
mode=sys.argv[1] if len(sys.argv)>1 else 'check'
def call(name):subprocess.run([sys.executable,'-X','utf8',str(r/name)],cwd=r,check=True)
if mode=='check':
 import PIL,numpy
 for exe in ['ffmpeg','ffprobe']:
  if not shutil.which(exe):raise SystemExit('Missing '+exe+' on PATH. Install an FFmpeg build with libass and libx264, then reopen the terminal.')
 filters=subprocess.check_output(['ffmpeg','-hide_banner','-filters'],stderr=subprocess.STDOUT,text=True)
 encoders=subprocess.check_output(['ffmpeg','-hide_banner','-encoders'],stderr=subprocess.STDOUT,text=True)
 assert 'subtitles' in filters and 'libx264' in encoders,'FFmpeg needs libass and libx264'
 manifest=r/'SHA256.json'
 if manifest.exists():
  for name,expected_digest in json.loads(manifest.read_text(encoding='utf-8')).items():
   assert digest(r/name)==expected_digest,name+' differs from delivery'
 print('DEPENDENCIES AND PACKAGE OK. Next: python -X utf8 run.py preview')
elif mode=='preview':
 call('build_captions.py');subprocess.run([sys.executable,'-X','utf8',str(r/'assemble.py'),'--preview'],cwd=r,check=True)
elif mode=='render':call('build_captions.py');call('assemble.py')
elif mode=='verify':call('verify_delivery.py')
else:raise SystemExit('Use check, preview, render, or verify')
