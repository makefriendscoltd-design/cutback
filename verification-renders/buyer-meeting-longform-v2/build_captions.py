from pathlib import Path
from PIL import ImageFont
import json,re,math
r=Path(__file__).resolve().parent;plan=json.loads((r/'edit-plan.json').read_text());groups=json.loads((r/'sentence-groups.json').read_text());trans=json.loads((r/'transcript.json').read_text());allwords=[w for s in trans['segments'] for w in s.get('words',[])];size=50;maxwidth=1400;measurement_size=41;font=ImageFont.truetype(str(r/'assets/Pretendard-SemiBold.ttf'),measurement_size)
def tm(t):
 for c in plan['clips']:
  if c['source_start']<=t<=c['source_end']:return c['start']+t-c['source_start']
  if t<c['source_start']:return c['start']
 return plan['duration']
def split(tokens):
 if font.getlength(' '.join(tokens))<=maxwidth:return [(0,len(tokens))]
 result=[];a=0
 while a<len(tokens):
  end=a+1
  while end<len(tokens) and font.getlength(' '.join(tokens[a:end+1]))<=maxwidth:end+=1
  if end==len(tokens):result.append((a,end));break
  remaining_width=font.getlength(' '.join(tokens[a:]));ideal=remaining_width/math.ceil(remaining_width/maxwidth)
  candidates=[]
  for k in range(a+1,end+1):
   width=font.getlength(' '.join(tokens[a:k]));w=tokens[k-1];nxt=tokens[k] if k<len(tokens) else ''
   semantic=3 if w.endswith(('고','고요','는데','는데요','경우','경우에는','때문에','때는','하면','하시면','지만','지만요','보면','보시면','아니라','다음에')) else 0
   if nxt in ['그래서','그리고','하지만','그런데','또는','또','그러면']:semantic+=3
   if width>=ideal*.65 and font.getlength(' '.join(tokens[k:]))>=maxwidth*.22:candidates.append((semantic*45-abs(width-ideal),k))
  k=max(candidates)[1] if candidates else end;result.append((a,k));a=k
 return result
caps=[];splitcount=0
for si,g in enumerate(groups):
 text=re.sub(r'(?<!\d)[.!?。！？]+|[.!?。！？]+(?!\d)','',g['text']).strip();tokens=text.split();ranges=split(tokens);splitcount+=len(ranges)>1
 ws=[w for w in allwords if w['end']>g['source_start']+.001 and w['start']<g['source_end']-.001]
 def boundary(i):
  if i==0:return g['source_start']
  if i>=len(tokens):return g['source_end']
  return ws[min(len(ws)-1,round(i*len(ws)/len(tokens)))]['start'] if ws else g['source_start']+(g['source_end']-g['source_start'])*i/len(tokens)
 for a,b in ranges:
  sa=boundary(a);sb=boundary(b);start=tm(sa);end=tm(sb)
  if end-start<.12:continue
  caps.append({'start':round(start,3),'end':round(end,3),'text':' '.join(tokens[a:b]),'sentence_index':si,'split_reason':'width_exceeds_1400px' if len(ranges)>1 else None,'source_start':sa,'source_end':sb})
for i,c in enumerate(caps[:-1]):
 c['end']=min(c['end'],caps[i+1]['start'])
 if 0<=caps[i+1]['start']-c['end']<.4:c['end']=caps[i+1]['start']
assert all(font.getlength(c['text'])<=maxwidth and c['end']>c['start'] for c in caps)
(r/'captions.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2)+'\n')
style={'font_family':'Pretendard SemiBold','ass_font_size':size,'css_font_size_px':measurement_size,'font_file':str(r/'assets/Pretendard-SemiBold.ttf'),'text':'#FFFFFF','background_opacity':.68,'max_width':maxwidth,'ass_margin_v':132,'reference':'User screenshot 2026-09-14: larger text over lower picture','grouping':'whole sentences; semantic split only if rendered width exceeds limit','sentences':len(groups),'sentences_split_for_width':splitcount,'cues':len(caps),'max_rows':1};(r/'caption-style.json').write_text(json.dumps(style,ensure_ascii=False,indent=2)+'\n')
def stamp(t,ass=False):
 n=round(t*(100 if ass else 1000));u=100 if ass else 1000
 return f'{n//(u*3600):02d}:{n//(u*60)%60:02d}:{n//u%60:02d}'+('.'+f'{n%u:02d}' if ass else ','+f'{n%u:03d}')
(r/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(caps))+'\n')
header=f'''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Pretendard SemiBold,{size},&H00FFFFFF,&H00FFFFFF,&H52000000,&H52000000,0,0,0,0,100,100,0,0,3,10,0,2,120,120,132,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
(r/'captions.ass').write_text(header+'\n'.join(f'Dialogue: 0,{stamp(c["start"],True)},{stamp(c["end"],True)},Default,,0,0,0,,{c["text"]}' for c in caps)+'\n');print(json.dumps(style,ensure_ascii=False))
