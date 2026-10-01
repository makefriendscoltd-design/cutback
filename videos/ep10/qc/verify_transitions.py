from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];q=r/'qc';out=r/'renders/AI학교_10탄_AI비교_Owen_v1.mp4'
cam=json.loads((r/'timing.json').read_text())['camera'];events=[(i,t,m,tw) for i,(t,m,z,tw) in enumerate(cam) if tw]
for page,start in enumerate(range(0,len(events),4)):
 group=events[start:start+4];sheet=Image.new('RGB',(810,505*len(group)),'#111827');d=ImageDraw.Draw(sheet)
 for row,(i,t,m,tw) in enumerate(group):
  for col,delta in enumerate([-.067,.15,.367]):
   ts=max(0,t+delta);p=q/f'transition-{i:02}-{col}.jpg'
   subprocess.run(['ffmpeg','-v','error','-y','-ss',str(ts),'-i',str(out),'-frames:v','1','-vf','scale=270:480',str(p)],check=True)
   sheet.paste(Image.open(p),(col*270,row*505+25));d.text((col*270+8,row*505+7),f'{ts:.3f}s to {m}',fill='white')
 sheet.save(q/f'encoded-transitions-{page+1}.jpg',quality=92)
print(f'{len(events)} transitions, {len(events)*3} actual MP4 frames')
