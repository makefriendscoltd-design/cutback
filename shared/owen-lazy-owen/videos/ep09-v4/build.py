#!/usr/bin/env python3
"""Owen episode 9: source-timed scenes in the approved full/card camera language."""
import os,sys,json,re,html
ROOT=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(ROOT,'..','nick-plugins-mg'))
import build as lib
W,H=1080,1920
CUTS=json.load(open(os.path.join(ROOT,'cuts.json')));DUR=CUTS['duration'];SEGS=CUTS['segments']
TX=json.load(open(os.path.join(ROOT,'src/transcript.json')))['segments'];WORDS=[w for s in TX for w in s['words']]
def M(t):
 for s in SEGS:
  if t<s['src_start']:return s['out_start']
  if t<=s['src_end']:return round(s['out_start']+t-s['src_start'],3)
 return DUR
NAVY='linear-gradient(180deg,#07101c,#0d1b2e)'
lib.BASE+='''
#root{color:#f5f9ff}.gridbg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 30%,#163450 0%,transparent 65%),repeating-linear-gradient(0deg,#64d2ff0b 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,#64d2ff0b 0 1px,transparent 1px 48px)}
.panel{position:absolute;left:64px;top:300px;width:952px;height:520px;border:2px solid #315776;border-radius:28px;background:#0b1728;overflow:hidden;box-shadow:0 25px 60px #0008}.chrome{height:52px;background:#0c1726;border-bottom:1px solid #315776;display:flex;align-items:center;gap:9px;padding:0 22px;color:#bed2e9;font-size:20px;font-family:'JetBrains Mono'}.chrome i{width:10px;height:10px;border-radius:50%;background:#64d2ff}.chrome em{font-style:normal;margin-left:15px}.stage{position:absolute;inset:52px 0 0;overflow:hidden}.doc{position:absolute}.source{position:absolute;bottom:14px;right:18px;background:#07101cee;border:1px solid #38536f;padding:6px 12px;border-radius:7px;font-size:18px}.cyan{color:#64d2ff}.red{color:#ff3b30}
'''
S={};OVL=set();CAM_SRC=[];ACTIONS=[]
LAYOUT={'s01-hook':'card','s02-assign':'full','s03-tired':'full','s04-claude':'card','s05-design':'card','s06-prototype':'card','s07-research':'card','s08-council':'card','s09-meeting':'card','s10-korean':'full','s11-canva':'card','s12-image':'full','s13-video':'card','s14-videojob':'card','s15-ebook':'full','s16-comment':'full'}
PRESENTER_ONLY={'s02-assign','s03-tired','s10-korean','s12-image','s15-ebook','s16-comment'}
def panel(title,body):return '<div class="panel"><div class="chrome"><i></i><i></i><i></i><em>'+title+'</em></div><div class="stage">'+body+'</div></div>'
SOUNDS={'opening':('impact-low-hook',-10),'prototype_click':('ui-panel-appear',-13),'claude_focus':('ui-tick',-12),'design_focus':('ui-tick',-12),'research_focus':('ui-tick',-12),'council_compare':('ui-panel-appear',-11),'meeting_capture':('ui-tick',-12),'minutes_ready':('ui-tick',-12),'canva_focus':('ui-tick',-12),'image_handoff':('ui-tick',-12),'video_focus':('ui-tick',-12),'timeline_play':('ui-panel-appear',-11)}
def scene(sid,a,b,body='',css='',js='',cues=()):
 mode=LAYOUT[sid]
 if sid in PRESENTER_ONLY:body,css,js='','',''
 if mode=='full':assert not body.strip(),(sid,'full presenter must remain unobstructed')
 st=M(a);du=round(M(b)-st,3)
 for name,src in cues:
  local=round(M(src)-st,3);assert 0<=local<du,(sid,name,local,du);assert '@'+name in js,(sid,name,'cue not bound')
  js=js.replace('@'+name,str(local));sound,gain=SOUNDS[name];ACTIONS.append({'name':name,'scene':sid,'source':src,'time':M(src),'local':local,'sound':sound,'gain_db':gain})
 assert '@' not in js,(sid,js)
 S[sid]=(st,du,lib.scene(sid,('' if mode=='full' else '<div class="gridbg"></div>')+body,css,js,'transparent'))
 if mode=='full':OVL.add(sid)
 CAM_SRC.append((a,mode,1.10 if mode=='full' else 1,0))
IN="tl.fromTo('.panel',{opacity:0,y:35,scale:.96},{opacity:1,y:0,scale:1,duration:.3,ease:'power3.out'},0);"
scene('s01-hook',1.20,4.70,'<div class="hook"><small>이 일엔 무슨 AI?</small><strong>업무별로 딱 골라줌</strong></div>','.hook{position:absolute;left:64px;top:345px;width:952px;text-align:center;font-weight:900}.hook small{display:block;font-family:JetBrains Mono;font-size:43px;margin-bottom:24px}.hook strong{display:block;font-family:NanumMyeongjo;font-size:76px;line-height:1.15;background:#64d2ff;color:#07101c;padding:24px 12px;border-radius:18px}',"tl.set('.hook strong',{opacity:1,scale:1},@opening);",cues=[('opening',1.20)])
scene('s02-assign',4.70,9.00)
scene('s03-tired',9.00,11.96)
def shot(sid,a,b,title,file,cue_name,cue_src,top,rect):
 x,y,w,h=rect;scale=952/1080;fx=x*scale;fy=y*scale+top;fw=w*scale;fh=h*scale;cx=(x+w/2)/1080*100;cy=(y+h/2)/1920*100
 scene(sid,a,b,panel(title,f'<img class="doc" data-layout-allow-overflow src="assets/shots/{file}"><div class="focus"></div><div class="source">공식 화면 · 원본 좌표 {x},{y}</div>'),f'.doc{{width:952px;left:0;top:{top}px;transform-origin:{cx:.1f}% {cy:.1f}%}}.focus{{position:absolute;left:{fx:.1f}px;top:{fy:.1f}px;width:{fw:.1f}px;height:{fh:.1f}px;border:4px solid #64d2ff;border-radius:14px;box-shadow:0 0 28px #64d2ff55}}',IN+f"tl.to('.doc',{{scale:1.12,y:-45,duration:1.15,ease:'power2.inOut'}},@{cue_name});tl.fromTo('.focus',{{opacity:0,scaleX:.25}},{{opacity:1,scaleX:1,duration:.38,ease:'power2.out'}},@{cue_name}+.76);",cues=[(cue_name,cue_src)])
shot('s04-claude',11.96,15.90,'글 / Claude','claude.png','claude_focus',12.88,-700,(180,920,760,180))
shot('s05-design',15.90,18.88,'홈페이지 / Claude Design','claude-design.png','design_focus',17.44,-120,(230,160,710,130))
scene('s06-prototype',18.88,21.82,'<div class="mini"><div class="prompt">말로 설명한 화면</div><button>시제품 만들기</button><div class="page">✓ 눌러보는 페이지</div></div>','.mini{position:absolute;left:90px;top:260px;width:900px;height:480px;padding:45px;background:#0b1728;border:2px solid #315776;border-radius:28px}.prompt{font-family:JetBrains Mono;font-size:31px}.mini button{margin-top:70px;padding:22px 32px;font-size:35px;background:#64d2ff;border:0;border-radius:14px}.page{position:absolute;inset:50px;background:#17394e;border:3px solid #64d2ff;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:47px;font-weight:900}',"tl.set('.page',{opacity:0,scale:.9},0);tl.to('button',{scale:.9,duration:.12},@prototype_click);tl.to('.page',{opacity:1,scale:1,duration:.35,ease:'back.out(1.5)'},@prototype_click+.14);",cues=[('prototype_click',20.18)])
shot('s07-research',21.82,25.08,'조사 / Perplexity Model Council','perplexity-council.png','research_focus',23.04,-145,(300,155,720,315))
scene('s08-council',25.08,28.40,'<div class="council"><div>MODEL A<small>근거 중심</small></div><div>MODEL B<small>실행 중심</small></div><div>MODEL C<small>리스크 중심</small></div><strong>답변 비교 완료</strong></div>','.council{position:absolute;left:65px;top:250px;width:950px;display:flex;gap:15px}.council div{flex:1;padding:42px 14px;background:#122a40;border:2px solid #315776;border-radius:18px;text-align:center;font-family:JetBrains Mono;font-size:27px}.council small{display:block;margin-top:35px;font-family:Pretendard;font-size:24px}.council strong{position:absolute;top:300px;left:220px;background:#64d2ff;color:#07101c;padding:18px 40px;border-radius:13px;font-size:38px}',"tl.fromTo('.council div',{opacity:0,y:30},{opacity:1,y:0,stagger:.18,duration:.28},0);tl.fromTo('.council strong',{opacity:0,scale:.8},{opacity:1,scale:1,duration:.3},@council_compare);",cues=[('council_compare',27.38)])
shot('s09-meeting',28.40,30.72,'회의록 / Fireflies','fireflies-korean.png','meeting_capture',29.10,-300,(60,700,630,90))
scene('s10-korean',30.72,32.14)
shot('s11-canva',32.14,33.32,'PPT / Canva','canva-ppt.png','canva_focus',32.30,-70,(120,260,840,260))
scene('s12-image',33.32,34.70)
shot('s13-video',34.70,36.30,'영상 / Higgsfield','higgsfield-home.png','video_focus',34.86,-85,(120,180,840,300))
scene('s14-videojob',36.30,40.24,'<div class="timeline"><div class="asset">사진 + 글</div><div class="track"><i></i><i></i><i></i></div><div class="preview">▶ VIDEO</div></div>','.timeline{position:absolute;left:75px;top:280px;width:930px;height:470px;background:#0b1728;border:2px solid #315776;border-radius:24px;padding:35px}.asset{font-size:34px}.track{display:flex;gap:8px;margin-top:55px}.track i{height:78px;flex:1;background:#23506b;border-radius:9px}.preview{margin-top:45px;text-align:center;font-family:Silkscreen;font-size:50px;color:#64d2ff}',"tl.fromTo('.track i',{scaleX:0},{scaleX:1,stagger:.18,duration:.3},0);tl.fromTo('.preview',{opacity:0,scale:.8},{opacity:1,scale:1,duration:.3},@timeline_play);",cues=[('timeline_play',38.30)])
scene('s15-ebook',40.24,45.62,panel('AI 활용법을 한 권으로','<div class="book"><span>집필 중</span><strong>AI 활용법<br>전자책</strong><small>최신 정보 · 수익화 방법</small></div><div class="note">일마다 맞는<br><b>AI 직원</b> 배치</div>'),'.book{position:absolute;left:70px;top:35px;width:355px;height:380px;background:#17394e;border:3px solid #64d2ff;border-left:16px solid #64d2ff;border-radius:5px 17px 17px 5px;padding:27px;box-shadow:16px 12px #06101b}.book span{font-size:22px}.book strong{display:block;margin-top:35px;font-size:53px;line-height:1.2;color:#64d2ff}.book small{display:block;margin-top:38px;font-size:21px}.note{position:absolute;left:500px;top:135px;font-size:48px;line-height:1.35;font-weight:900}.note b{color:#64d2ff}',IN+"tl.fromTo('.book',{opacity:0,x:-35,rotation:-5},{opacity:1,x:0,rotation:-2,duration:.35},.1);tl.fromTo('.note',{opacity:0,y:20},{opacity:1,y:0,duration:.3},.55);")
scene('s16-comment',45.62,49.94)
CAM=[]
for i,(t,m,z,_) in enumerate(CAM_SRC):CAM.append((0.0 if i==0 else M(t),m,z,.3 if i and CAM_SRC[i-1][1]!=m else 0))
FACE=(1000,340)
def geo(mode):
 if mode=='card':
  box=dict(left=40,top=880,width=1000,height=1040,borderRadius='80px 80px 0 0');s=1040/1080;img=dict(width=1920*s,height=1040,left=500-FACE[0]*s,top=0);org=(500,FACE[1]*s)
 else:
  box=dict(left=0,top=0,width=1080,height=1920,borderRadius='0px');s=1920/1080;img=dict(width=1920*s,height=1920,left=540-FACE[0]*s,top=-40);org=(540,FACE[1]*s-40)
 return box,img,org
fmt=lambda d:'{'+','.join(f'{k}:{json.dumps(round(v,1) if isinstance(v,float) else v)}' for k,v in d.items())+'}'
cam_js=[]
for t,mode,z,tw in CAM:
 box,img,org=geo(mode);zo=f"{{scale:{z},transformOrigin:'{org[0]:.0f}px {org[1]:.0f}px'}}"
 if tw:cam_js.append(f"tl.to('#camBox',{{...{fmt(box)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camImg',{{...{fmt(img)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camZoom',{{...{zo},duration:{tw},ease:'power2.inOut'}},{t});")
 else:cam_js.append(f"tl.set('#camBox',{{autoAlpha:1,...{fmt(box)}}},{t});tl.set('#camImg',{fmt(img)},{t});tl.set('#camZoom',{zo},{t});")
def mode_at(t):
 m=CAM[0][1]
 for tt,mm,*_ in CAM:
  if tt<=t+1e-6:m=mm
 return m
C_SRC=[(1.20,'오늘도 AI 직원을','AI 직원'),(2.26,'뽑았습니다',''),(4.70,'일마다 담당을','담당'),(6.42,'따로 정했거든요',''),(9.00,'AI 하나로 다 하려니까','AI 하나'),(10.48,'피곤하잖아요','피곤'),(11.96,'글은 클로드','클로드'),(12.88,'기획안 초안은 여기 맡깁니다','초안'),(15.90,'홈페이지는 클로드 디자인','클로드 디자인'),(17.44,'말로 설명하면',''),(18.88,'눌러볼 수 있는 시제품을','시제품'),(20.18,'만들어줘요',''),(21.82,'조사는 퍼플렉시티','퍼플렉시티'),(23.04,'모델 카운슬 기능이 있는데','모델 카운슬'),(25.08,'여러 AI한테 같은 질문을 던지고','여러 AI'),(27.38,'답을 비교해줘요','비교'),(28.40,'회의록은 파이어플라이즈','파이어플라이즈'),(30.72,'한국어도 받아 적고요','한국어'),(32.14,'PPT는 캔바','캔바'),(33.32,'이미지는 챗GPT','챗GPT'),(34.70,'영상은 힉스필드','힉스필드'),(36.30,'사진이나 글로 영상을 만드는','영상'),(38.30,'작업을 맡기는 거예요','맡기는'),(40.24,'이런 AI 활용법부터','AI 활용법'),(41.52,'최신 정보','최신 정보'),(42.72,'수익화 방법까지','수익화'),(43.68,'전자책으로 정리하고 있습니다','전자책'),(45.62,'궁금하신 분들은',''),(47.58,'댓글에 전자책이라고','전자책'),(49.12,'남겨주세요','')]
WARN=['피곤']
CAPS=[]
for i,(s,txt,acc) in enumerate(C_SRC):
 nxt=C_SRC[i+1][0] if i+1<len(C_SRC) else 1e9;last=max([w['end'] for w in WORDS if w['start'] is not None and s-.01<=w['start']<nxt] or [s+.5]);a=0 if i==0 else M(s);e=min(M(nxt) if nxt<1e8 else DUR,M(last)+.35)
 if i+1<len(C_SRC) and M(nxt)-e<.25:e=M(nxt)
 CAPS.append([a,round(e,3),txt,mode_at(a),acc])
scene_divs=''.join(f'<div id="{sid}" class="{"ovl" if sid in OVL else "scn"}" data-composition-id="{sid}" data-composition-src="scenes/{sid}.html" data-start="{st}" data-duration="{du}" data-track-index="{2 if sid in OVL else 0}" data-width="1080" data-height="1920"></div>\n' for sid,(st,du,_) in S.items())
ib,ii,io=geo(CAM[0][1])
def cssg(d):return ';'.join(re.sub(r'([A-Z])',lambda m:'-'+m[1].lower(),k)+':'+(str(v)+'px' if isinstance(v,(int,float)) else v) for k,v in d.items())
HTML=f'''<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080,height=1920"><title>AI학교 9탄 · AI 직원 배치표</title><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{lib.FONTS}body{{margin:0;background:#000;font-family:Pretendard,sans-serif}}#root{{position:relative;width:100%;height:100%;overflow:hidden;background:#07101c}}#root *{{box-sizing:border-box}}.scn{{position:absolute;inset:0;z-index:1}}.ovl{{position:absolute;inset:0;z-index:3}}#camBox{{position:absolute;overflow:hidden;z-index:2;background:#111;{cssg(ib)}}}#camZoom{{position:absolute;inset:0}}#camImg{{position:absolute;{cssg(ii)}}}#person{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}#captions{{position:absolute;inset:0;z-index:4;pointer-events:none}}.caption{{position:absolute;text-align:center;white-space:nowrap}}.caption.card{{left:64px;width:952px}}.caption.full{{left:64px;width:836px}}.caption span{{display:inline-block;font-weight:800;font-size:60px;line-height:1.05;color:#fff;letter-spacing:-1px;white-space:nowrap;text-shadow:0 2px 8px #000,0 0 3px #000}}.caption b{{font-weight:inherit;color:#64d2ff}}.caption b.warn{{color:#ff3b30}}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">{scene_divs}<div id="camBox"><div id="camZoom" data-layout-allow-overflow><div id="camImg" data-layout-allow-overflow><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1" muted></video></div></div></div><div id="captions"></div><audio id="voice" src="assets/mix.m4a" data-start="0" data-duration="{DUR}" data-track-index="9"></audio></div><script>const WARN={json.dumps(WARN,ensure_ascii=False)},CAPS={json.dumps(CAPS,ensure_ascii=False)},CAMERA={json.dumps(CAM)};const host=document.getElementById('captions'),strip=t=>t.replace(/[.,?!"'…“”‘’]/g,''),esc=t=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;');CAPS.forEach((c,i)=>{{const [s,e,text,mode,acc]=c,d=document.createElement('div');d.id='cap-'+i;d.className='clip caption '+(mode==='card'?'card':'full');d.dataset.start=s;d.dataset.duration=(e-s).toFixed(3);d.dataset.trackIndex=8;d.style.top=(mode==='card'?840:1345)+'px';let h=esc(strip(text)),a=strip(acc||'');if(a)h=h.replace(esc(a),'<b'+(WARN.includes(a)?' class="warn"':'')+'>'+esc(a)+'</b>');d.innerHTML='<span>'+h+'</span>';host.appendChild(d)}});function fit(){{CAPS.forEach((c,i)=>{{const sp=document.querySelector('#cap-'+i+' span'),max=c[3]==='card'?930:836;sp.style.fontSize='60px';if(sp.scrollWidth>max)sp.style.fontSize=Math.floor(60*max/sp.scrollWidth)+'px'}})}}fit();document.fonts&&document.fonts.ready.then(fit);const tl=gsap.timeline({{paused:true}});CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');if(i===0)tl.set(el,{{opacity:1,scale:1}},0);else tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);tl.set(el,{{opacity:0}},c[1])}});CAPS.forEach((c,i)=>{{const j=CAMERA.findIndex(k=>Math.abs(k[0]-c[0])<.001&&k[3]>0);if(j>0){{const oldY=CAMERA[j-1][1]==='card'?840:1345,newY=CAMERA[j][1]==='card'?840:1345,n=document.querySelector('#cap-'+i+' span');tl.set(n,{{y:1345-newY}},c[0]);tl.set(n,{{y:0}},c[0]+CAMERA[j][3])}}}});{''.join(cam_js)}window.__timelines.main=tl;</script></body></html>'''
os.makedirs(os.path.join(ROOT,'scenes'),exist_ok=True)
for f in os.listdir(os.path.join(ROOT,'scenes')):
 if os.path.isfile(os.path.join(ROOT,'scenes',f)):os.remove(os.path.join(ROOT,'scenes',f))
for sid,(st,du,sh) in S.items():open(os.path.join(ROOT,'scenes',sid+'.html'),'w').write(sh)
open(os.path.join(ROOT,'index.html'),'w').write(HTML)
EV={'scenes':{sid:[st,du,'ovl' if sid in OVL else 'scn'] for sid,(st,du,_) in S.items()},'cam':CAM,'ticks':[M(t) for t in [2.26,6.42,10.48,12.88,17.44,20.18,23.04,27.38,30.72,32.14,33.32,34.70,38.30,41.52,42.72,47.58]],'actions':ACTIONS}
json.dump(EV,open(os.path.join(ROOT,'events.json'),'w'),indent=2);json.dump({'captions':CAPS,'camera':CAM,'scenes':EV['scenes']},open(os.path.join(ROOT,'timing.json'),'w'),ensure_ascii=False,indent=2)
print(f'wrote {len(S)} scenes, {len(CAPS)} captions, {DUR}s')
