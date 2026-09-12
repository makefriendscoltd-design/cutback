import pathlib,json,re,difflib,unicodedata
from PIL import ImageFont
r=pathlib.Path(__file__).resolve().parent
old=json.loads((r.parent/'20260911_175145-polish-v3/captions.json').read_text())
audit=json.loads((r/'caption-audit.json').read_text())
fix={x['cue_index']:x['to'] for x in audit['corrections']}
# Minimal grammatical repair: the intended object is work entrusted to AI.
fix[30]='그리고 반복하던 일을 AI에 맡기는 자동화를 만들어서 가르치고 있습니다.'
source=json.loads((r.parent/'20260911_175145-cut-v2-tight/output-transcript.json').read_text())
words=[w for s in source['segments'] for w in s['words']]
font=ImageFont.truetype(str(r/'assets/Pretendard-Bold.ttf'),76)
splits={
0:'학교를 졸업하고 취업하면|준비가 끝날까요?',
2:'자기 일을 만들어가는 힘이|필요하다고 생각합니다.',
5:'그 결과 다른 사람에게|보여줄 수 있는 힘이요.',
7:'안녕하세요. AI 학교|aixscool을 설립한|교장 나민수입니다.',
10:'그러다가 어머님 버킷리스트인|카페를 만들었습니다.',
13:'제 손으로 카페를 지어서|2년 동안 운영도 했습니다.',
14:'그 뒤로 부업 강의에|한 3~4천만 원을 썼거든요.',
16:'돈 되는 건 다 들어봤는데|성과는 하나도 없었어요.',
17:'처음 돈을 번 건|강의를 들었을 때가 아니라',
18:'로고 하나를 3만 원에|직접 만들어서 팔았을 때였습니다.',
19:'그 손님을 모으려고|블로그 글을 쓰는데',
25:'해외 영상을 하루에 100개씩|석 달을 봤어요.',
30:'그리고 반복하던 일을|AI에 맡기는 자동화를|만들어서 가르치고 있습니다.',
33:'그래서 새로운 도구, 강의, 영상도|계속 쏟아집니다.',
34:'그런데 정작 나는|어디서부터 어떻게 시작해야 되는지,',
37:'그래서 여러분이 혼자 찾아 헤매던|배움을 한 곳에 다 모았습니다.',
39:'직접 만들어서 내 일에 쓰는 것까지|이어지도록요.',
42:'그리고 잘 아는 문제에서|앞으로 해볼 일을 찾을 겁니다.',
46:'글과 영상, 디자인, 고객 응대,|그리고 업무 자동화,',
47:'내 상황에 맞춰서|실행하고 고치고 다시 해보는 겁니다.',
48:'혼자 하다가 막히면|질문할 사람이 있고',
49:'매주 함께 점검하는 시간을|만들어 놨어요.',
51:'저희가 졸업에서 확인하려는 것도|분명합니다.',
53:'자신의 문제를 정하고|결과물로 해결할 수 있는가?',
54:'제가 카페를 직접 지어봤듯이|여러분도 여기서',
56:'취업을 준비하는 분은|자신의 역량을 보여줄 결과물을|내시면 되고요.',
58:'자기 일의 방식을 바꿀|도구를 만드시면 됩니다.',
60:'직접 시도해 볼 첫 서비스를|만들어 가길 바랍니다.',
62:'변화 앞에서 무엇부터 배워야 할지|헤매기보다',
63:'스스로 배우고 만들고|자기 일을 이어갈 수 있기를 바랍니다.',
64:'10월 6일 무료 라이브에서|이 학교가',
65:'어떤 배움과 과정을 준비했는지|직접 보여드리겠습니다.',
68:'카톡방 입장 링크와|내 일 AI 적용 키트를',
71:'여러분이 앞으로 만들어갈 일을|이 학교에서 함께 시작하겠습니다.'}
def norm(x):return ''.join(c.lower() for c in unicodedata.normalize('NFKC',x) if c.isalnum())
new=[]
for i,c in enumerate(old):
 text=fix.get(i,c['text']);chunks=splits.get(i,text).split('|')
 assert norm(''.join(chunks))==norm(text),(i,chunks,text)
 for line in chunks:assert font.getlength(line)<1480,(i,line,font.getlength(line))
 raw='';times=[]
 for w in words:
  if w['start']>=c['end'] or w['end']<=c['start']:continue
  token=norm(w['word'])
  for j,ch in enumerate(token):
   raw+=ch;times.append(w['start']+(w['end']-w['start'])*j/max(1,len(token)))
 target=norm(text);mapped=[None]*len(target)
 for a,b,n in difflib.SequenceMatcher(None,raw,target,autojunk=False).get_matching_blocks():
  for k in range(n):mapped[b+k]=times[a+k]
 bounds=[c['start']];count=0
 for ch in chunks[:-1]:
  count+=len(norm(ch));t=mapped[count] if count<len(mapped) else None
  if t is None:
   candidates=[(abs(j-count),tm) for j,tm in enumerate(mapped) if tm is not None]
   t=min(candidates)[1] if candidates else c['start']+(c['end']-c['start'])*count/len(target)
  bounds.append(max(bounds[-1]+.30,min(c['end']-.30,t)))
 bounds.append(c['end'])
 for j,line in enumerate(chunks):
  new.append({'start':round(bounds[j],3),'end':round(bounds[j+1],3),'lines':[line],'text':line,'source_cue':i})
assert all(x['end']>x['start'] for x in new)
assert all(x['end']<=new[i+1]['start']+.001 for i,x in enumerate(new[:-1]))
(r/'captions.json').write_text(json.dumps(new,ensure_ascii=False,indent=2))
def st(t):
 n=round(t*1000);return f'{n//3600000:02d}:{n//60000%60:02d}:{n//1000%60:02d},{n%1000:03d}'
(r/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{st(x["start"])} --> {st(x["end"])}\n{x["text"]}' for i,x in enumerate(new))+'\n')
(r/'caption-final-audit.json').write_text(json.dumps({'user_canonical':{'brand':'aixscool','presenter':'나민수'},'correction_count':len(fix),'grammatical_repair':{'source_cue':30,'from':'AI가 맡기는','to':'AI에 맡기는','reason':'Minimal particle correction to express speaker intended meaning; audio unchanged.'},'cues':len(new),'physical_lines_per_cue':1,'max_width_px_at_76px':round(max(font.getlength(x['text']) for x in new),1),'max_allowed_width_px':1480,'timing':'Split points aligned to word timestamps, with character alignment for spelling corrections.'},ensure_ascii=False,indent=2))
print('cues',len(new),'max width',max(font.getlength(x['text']) for x in new),'short cues',[(x['text'],round(x['end']-x['start'],2)) for x in new if x['end']-x['start']<.65])
