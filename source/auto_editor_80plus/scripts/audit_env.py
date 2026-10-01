import importlib.util, json, shutil, subprocess, sys
from pathlib import Path
checks=['ffmpeg','ffprobe','node','npm','python3']; result={}; missing=[]
for c in checks:
 p=shutil.which(c); result[c]=p or 'MISSING'; missing += [] if p else [c]
for m in ['cv2','PIL','faster_whisper']:
 result[m]='OK' if importlib.util.find_spec(m) else 'MISSING'
result['remotion']='OK' if Path('node_modules/.bin/remotion').exists() else 'MISSING'
print(json.dumps(result,ensure_ascii=False,indent=2))
if missing or any(result[x]=='MISSING' for x in ['cv2','PIL','faster_whisper','remotion']): sys.exit(1)
