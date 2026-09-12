import pathlib,json,re,difflib,unicodedata
from PIL import ImageFont
r=pathlib.Path(__file__).resolve().parent;v4=r.parent/'20260911_175145-polish-v4'
prior=json.loads((v4/'captions.json').read_text());old=json.loads((r.parent/'20260911_175145-polish-v3/captions.json').read_text())
by={}
for c in prior:by.setdefault(c['source_cue'],[]).append(c)
def clean(s):return re.sub(r'\s+',' ',re.sub(r'[.,!?…]','',s)).strip()
canon={i:clean(' '.join(x['text'] for x in cs)) for i,cs in by.items()}
font=ImageFont.truetype(str(r/'assets/Pretendard-Bold.ttf'),76)
manual={
7:'안녕하세요|AI 학교 aixscool을 설립한|교장 나민수입니다',
10:'그러다가 어머님 버킷리스트인|카페를 만들었습니다',
13:'제 손으로 카페를 지어서|2년 동안 운영도 했습니다',
16:'돈 되는 건 다 들어봤는데|성과는 하나도 없었어요',
18:'로고 하나를 3만 원에|직접 만들어서 팔았을 때였습니다',
25:'해외 영상을 하루에 100개씩|석 달을 봤어요',
30:'그리고 반복하던 일을 AI에 맡기는 자동화를|만들어서 가르치고 있습니다',
33:'그래서 새로운 도구 강의 영상도|계속 쏟아집니다',
34:'그런데 정작 나는 어디서부터|어떻게 시작해야 되는지',
37:'그래서 여러분이 혼자 찾아 헤매던 배움을|한 곳에 다 모았습니다',
39:'직접 만들어서 내 일에 쓰는 것까지|이어지도록요',
42:'그리고 잘 아는 문제에서|앞으로 해볼 일을 찾을 겁니다',
46:'글과 영상 디자인 고객 응대|그리고 업무 자동화',
47:'내 상황에 맞춰서 실행하고 고치고|다시 해보는 겁니다',
49:'매주 함께 점검하는 시간을|만들어 놨어요',
56:'취업을 준비하는 분은|자신의 역량을 보여줄 결과물을 내시면 되고요',
60:'직접 시도해 볼 첫 서비스를|만들어 가길 바랍니다',
62:'변화 앞에서 무엇부터 배워야 할지|헤매기보다',
63:'스스로 배우고 만들고|자기 일을 이어갈 수 있기를 바랍니다',
71:'여러분이 앞으로 만들어갈 일을|이 학교에서 함께 시작하겠습니다'}
# Keep the subject attached to the following clause instead of stranding “이 학교가”.
groups=[]
for i in range(72):
 if i in [55,65]:continue
 if i==54:groups.append((i,old[i]['start'],old[55]['end'],canon[i]+' '+canon[55],['제가 카페를 직접 지어봤듯이','여러분도 여기서 자기 걸 하나','직접 짓고 나가는 겁니다']))
 elif i==64:groups.append((i,old[i]['start'],old[65]['end'],canon[i]+' '+canon[65],['10월 6일 무료 라이브에서','이 학교가 어떤 배움과 과정을 준비했는지','직접 보여드리겠습니다']))
 else:groups.append((i,old[i]['start'],old[i]['end'],canon[i],manual.get(i,canon[i]).split('|')))
source=json.loads((r.parent/'20260911_175145-cut-v2-tight/output-transcript.json').read_text());words=[w for s in source['segments'] for w in s['words']]
def norm(s):return ''.join(x.lower() for x in unicodedata.normalize('NFKC',s) if x.isalnum())
caps=[]
for i,start,end,text,chunks in groups:
 assert norm(''.join(chunks))==norm(text),(i,text,chunks)
 for line in chunks:assert font.getlength(line)<1560,(i,line,round(font.getlength(line)))
 raw='';times=[]
 for w in words:
  if w['start']>=end or w['end']<=start:continue
  token=norm(w['word'])
  for j,ch in enumerate(token):raw+=ch;times.append(w['start']+(w['end']-w['start'])*j/max(1,len(token)))
 target=norm(text);mapped=[None]*len(target)
 for a,b,n in difflib.SequenceMatcher(None,raw,target,autojunk=False).get_matching_blocks():
  for k in range(n):mapped[b+k]=times[a+k]
 bounds=[start];cnt=0
 for ch in chunks[:-1]:
  cnt+=len(norm(ch));t=mapped[cnt] if cnt<len(mapped) else None
  if t is None:t=min((abs(j-cnt),v) for j,v in enumerate(mapped) if v is not None)[1]
  bounds.append(max(bounds[-1]+.3,min(end-.3,t)))
 bounds.append(end)
 for j,line in enumerate(chunks):caps.append({'start':round(bounds[j],3),'end':round(bounds[j+1],3),'lines':[line],'text':line,'source_cue':i})
(r/'captions-base.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2))
assert not any(re.search(r'[.,!?…]',c['text']) for c in caps)
print('semantic caption cues',len(caps),'max width',round(max(font.getlength(c['text']) for c in caps)))
