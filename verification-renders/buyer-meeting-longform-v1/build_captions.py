from pathlib import Path
import json,re,html,shutil
from PIL import ImageFont
r=Path(__file__).resolve().parent;plan=json.loads((r/'edit-plan.json').read_text());trans=json.loads((r/'transcript.json').read_text());fix=json.loads((r/'transcript-corrections.json').read_text())
a=r/'assets';a.mkdir(exist_ok=True);fontsrc=Path('/Users/apple/orca/projects/cutback/auto_editor/assets/fonts/Pretendard-SemiBold.ttf');shutil.copy2(fontsrc,a/fontsrc.name)
size=30;font=ImageFont.truetype(str(a/fontsrc.name),size)
style={'font_family':'Pretendard SemiBold','font_file':str(a/fontsrc.name),'requested_capcut_font_size':5,'render_font_size_px':size,'size_conversion_status':'approximation; exact CapCut UI conversion unverified','text':'#FFFFFF','background_rgba':[0,0,0,.68],'max_lines':2,'caption_baseline_bottom':1040,'max_width':1550}
(r/'caption-style.json').write_text(json.dumps(style,ensure_ascii=False,indent=2))
def tm(t):
 for c in plan['clips']:
  if c['source_start']<=t<=c['source_end']:return c['start']+t-c['source_start']
  if t<c['source_start']:return c['start']
 return plan['duration']
def clean(s):
 for f in fix:s=s.replace(f['before'],f['after'])
 return re.sub(r'(?<!\d)[.!?。！？]+|[.!?。！？]+(?!\d)','',s).strip()
caps=[]
for seg in trans['segments']:
 text=clean(seg['text']);tokens=text.split();ws=seg.get('words',[])
 if not tokens or not ws:continue
 # Align clean tokens to word timing; use proportional original boundary index for occasional word-count changes.
 def boundary(i,end=False):
  k=min(len(ws)-1,max(0,round(i*len(ws)/len(tokens))))
  return ws[k]['end' if end else 'start']
 groups=[];cur=[];st=0
 for i,token in enumerate(tokens):
  candidate=' '.join(cur+[token]);elapsed=boundary(i,True)-boundary(st)
  if cur and (len(candidate)>35 or elapsed>4.2 or font.getlength(candidate)>1480):groups.append((st,i,cur));cur=[];st=i
  cur.append(token)
  if len(' '.join(cur))>=14 and token.endswith(('습니다','겠습니다','됩니다','거든요','는데요','고요','세요','합니다','입니다','있어요')):
   groups.append((st,i+1,cur));cur=[];st=i+1
 if cur:groups.append((st,len(tokens),cur))
 for start,end,words in groups:
  s=tm(boundary(start));e=tm(ws[-1]['end'] if end==len(tokens) else boundary(end));txt=' '.join(words)
  if e-s<.16:continue
  caps.append({'start':round(s,3),'end':round(e,3),'text':txt,'source_start':boundary(start),'source_end':ws[-1]['end'] if end==len(tokens) else boundary(end)})
for i,c in enumerate(caps):
 if i+1<len(caps):c['end']=min(c['end'],caps[i+1]['start'])
assert all('\n' not in c['text'] and font.getlength(c['text'])<1550 for c in caps)
(r/'captions.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2))
def stamp(t,ass=False):
 n=round(t*(100 if ass else 1000));unit=100 if ass else 1000
 return f'{n//(unit*3600):01d}:{n//(unit*60)%60:02d}:{n//unit%60:02d}.'+f'{n%unit:02d}' if ass else f'{n//3600000:02d}:{n//60000%60:02d}:{n//1000%60:02d},{n%1000:03d}'
(r/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(caps))+'\n')
header=f'''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Pretendard SemiBold,{size},&H00FFFFFF,&H00FFFFFF,&H52000000,&H52000000,0,0,0,0,100,100,0,0,3,8,0,2,120,120,22,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
(r/'captions.ass').write_text(header+'\n'.join(f'Dialogue: 0,{stamp(c["start"],True)},{stamp(c["end"],True)},Default,,0,0,0,,{c["text"]}' for c in caps)+'\n')
print('CAPTIONS',len(caps),'physical_rows_max=1')
