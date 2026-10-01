#!/usr/bin/env python3
"""Owen episode 8: Claude and Codex mutual-review development loop."""
import os, sys, json, re
ROOT=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(ROOT,'..','nick-plugins-mg'))
import build as lib
W,H=1080,1920
CUTS=json.load(open(os.path.join(ROOT,'cuts.json')));DUR=CUTS['duration'];SEGS=CUTS['segments']
WORDS=[w for s in json.load(open(os.path.join(ROOT,'src/transcript.json')))['raw'] for w in s['words']]
def M(t):
 for s in SEGS:
  if t<s['src_start']: return s['out_start']
  if t<=s['src_end']: return round(s['out_start']+t-s['src_start'],3)
 return DUR
NAVY='linear-gradient(180deg,#07101c,#0d1b2e)'
lib.BASE+='''
#root{color:#f5f9ff}.panel{position:absolute;left:64px;top:300px;width:952px;height:520px;border:2px solid #315776;border-radius:28px;background:#0b1728;overflow:hidden;box-shadow:0 25px 60px #0008}.chrome{height:52px;background:#0c1726;border-bottom:1px solid #315776;display:flex;align-items:center;gap:9px;padding:0 22px;color:#bed2e9;font-size:20px;font-family:'JetBrains Mono'}.chrome i{width:10px;height:10px;border-radius:50%;background:#64d2ff}.chrome em{font-style:normal;margin-left:15px}.stage{position:absolute;inset:52px 0 0;overflow:hidden}.gridbg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 30%,#163450,transparent 65%),repeating-linear-gradient(0deg,#64d2ff0b 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,#64d2ff0b 0 1px,transparent 1px 48px)}.big{font-weight:900;font-size:58px;line-height:1.18}.small{font-size:26px;color:#c9d9e7}.cyan{color:#64d2ff}.red{color:#ff746b}.pill{border:2px solid #4b7898;border-radius:15px;background:#17334a;padding:20px 24px;font-size:31px;font-weight:800}.arrow{color:#64d2ff;font-size:55px;font-weight:900}.example{position:absolute;right:22px;top:15px;color:#aac1d7;font-size:18px}
'''
S={};OVL=set();CAM_SRC=[]
LAYOUT={'s01-hook':'card','s02-name':'full','s03-plan':'card','s04-review':'full','s05-profit':'card','s06-costs':'card','s07-business':'full','s08-check':'card','s09-loop':'full','s10-build':'card','s11-test':'card','s12-mutual':'full','s13-flow':'card','s14-cost':'full','s15-human':'card','s16-cta':'full'}
PRESENTER_ONLY={'s02-name','s04-review','s07-business','s09-loop','s12-mutual','s14-cost','s16-cta'}
def panel(title,body): return '<div class="panel"><div class="chrome"><i></i><i></i><i></i><em>'+title+'</em></div><div class="stage">'+body+'</div></div>'
def scene(sid,a,b,body='',css='',js=''):
 mode=LAYOUT[sid]
 if sid in PRESENTER_ONLY: body=css=js=''
 st=M(a);du=round(M(b)-st,3)
 S[sid]=(st,du,lib.scene(sid,('' if mode=='full' else '<div class="gridbg"></div>')+body,css,js,'transparent'))
 if mode=='full': OVL.add(sid)
 CAM_SRC.append((a,mode,1.10 if mode=='full' else 1,0))
IN="tl.fromTo('.panel',{opacity:0,y:35,scale:.96},{opacity:1,y:0,scale:1,duration:.3,ease:'power3.out'},0);"
scene('s01-hook',1.16,7.60,'<div class="hook"><span>AI 한 명만 쓰지 마세요</span><strong>둘이 서로 검사하게 하세요</strong></div>','.hook{position:absolute;left:64px;top:380px;width:952px;text-align:center;font-size:65px;font-weight:900;line-height:1.16}.hook strong{display:block;margin-top:24px;padding:20px 8px;border-radius:16px;background:#64d2ff;color:#07101c;font-size:61px}',"tl.fromTo('.hook strong',{scale:.97},{scale:1.02,duration:2.2,ease:'none'},0);")
scene('s02-name',7.60,12.52)
scene('s03-plan',12.52,18.86,panel('CLAUDEX LOOP / 계획 검토','<div class="duo"><div><b>FABLE 5.1</b><span>계획 작성</span></div><i>→</i><div><b>GPT-6 ASTRA</b><span>계획 검토</span></div></div>'),'.duo{display:flex;align-items:center;justify-content:center;gap:22px;padding-top:100px}.duo div{width:330px;border:2px solid #4d7a9a;border-radius:18px;background:#17344b;padding:34px 12px;text-align:center}.duo b{display:block;color:#64d2ff;font-size:32px}.duo span{display:block;margin-top:22px;font-size:31px;font-weight:800}.duo i{font-style:normal;color:#64d2ff;font-size:60px}',IN+"tl.fromTo('.duo>*',{opacity:0,x:-25},{opacity:1,x:0,stagger:.32,duration:.3},.2);")
scene('s04-review',18.86,23.70)
scene('s05-profit',23.70,28.26,panel('상품별 이익 대시보드','<div class="bars"><div><span>매출</span><b style="width:86%"></b></div><div><span>비용</span><b style="width:58%"></b></div><div><span>실제 이익</span><b class="profit" style="width:38%"></b></div></div>'),'.bars{padding:70px 48px}.bars div{margin-bottom:35px;font-size:28px}.bars span{display:block;margin-bottom:10px}.bars b{display:block;height:30px;border-radius:8px;background:#526a80}.bars b.profit{background:#64d2ff}',IN+"tl.fromTo('.bars b',{scaleX:0,transformOrigin:'left center'},{scaleX:1,stagger:.35,duration:.45,ease:'power2.out'},.2);")
scene('s06-costs',28.26,35.34,panel('매출만 보면 놓치는 비용','<div class="costs"><div>가격 기준</div><div>배송비</div><div>환불</div><div>광고비</div></div>'),'.costs{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:58px}.costs div{border:2px solid #466f8d;background:#173249;border-radius:16px;padding:29px 15px;text-align:center;font-size:36px;font-weight:900}.costs div:last-child{border-color:#ff746b;color:#ff9a94}',IN+"tl.fromTo('.costs div',{opacity:0,scale:.85},{opacity:1,scale:1,stagger:.32,duration:.3,ease:'back.out(1.5)'},.2);")
scene('s07-business',35.34,39.18)
scene('s08-check',39.18,43.36,panel('ASTRA / 계획 검토','<div class="review"><div class="data">데이터 + 계산 기준</div><div class="arrow">↓</div><div class="result">계획이 맞는지 확인</div></div>'),'.review{text-align:center;padding:65px}.review div:not(.arrow){border:2px solid #4a7898;border-radius:16px;padding:22px;font-size:34px;font-weight:900;background:#17334a}.review .result{border-color:#64d2ff;color:#64d2ff}',IN+"tl.fromTo('.review>*',{opacity:0,y:-18},{opacity:1,y:0,stagger:.3,duration:.28},.2);")
scene('s09-loop',43.36,48.28)
scene('s10-build',48.28,53.32,panel('검토 뒤 실제 개발','<div class="pipe"><div>계획 통과</div><i>→</i><div>대시보드 제작</div><i>→</i><div>데이터 연결</div></div>'),'.pipe{display:flex;align-items:center;gap:14px;padding:130px 25px}.pipe div{flex:1;border:2px solid #477691;border-radius:14px;padding:25px 8px;text-align:center;font-size:27px;font-weight:900;background:#17334a}.pipe i{font-style:normal;color:#64d2ff;font-size:40px}',IN+"tl.fromTo('.pipe>*',{opacity:0,x:-20},{opacity:1,x:0,stagger:.25,duration:.25},.2);")
scene('s11-test',53.32,58.82,panel('FABLE / 코드 재검토','<div class="checks"><div><b>✓</b>사업 기준대로 계산</div><div><b>✓</b>정해둔 테스트 실행</div><div><b>✓</b>결과 다시 확인</div></div>'),'.checks{padding:60px 52px}.checks div{margin-bottom:20px;padding:22px;border:1px solid #456c88;background:#163149;border-radius:13px;font-size:32px;font-weight:800}.checks b{color:#64d2ff;margin-right:22px}',IN+"tl.fromTo('.checks div',{opacity:0,x:30},{opacity:1,x:0,stagger:.45,duration:.3},.2);")
scene('s12-mutual',58.82,62.92)
scene('s13-flow',62.92,67.64,panel('복붙 없이 한 흐름으로','<div class="flow"><div>계획</div><i>→</i><div>지적</div><i>→</i><div>수정</div><i>→</i><div>검토</div></div>'),'.flow{display:flex;align-items:center;gap:9px;padding:145px 24px}.flow div{flex:1;padding:24px 5px;text-align:center;border:2px solid #47718f;background:#163249;border-radius:13px;font-size:28px;font-weight:900}.flow i{font-style:normal;color:#64d2ff;font-size:31px}',IN+"tl.fromTo('.flow>*',{opacity:0,x:-16},{opacity:1,x:0,stagger:.18,duration:.22},.2);")
scene('s14-cost',67.64,70.58)
scene('s15-human',70.58,76.667,panel('마지막 확인은 사람이','<div class="warning"><span>AI 상호검토</span><b>≠</b><strong>사업 기준 자동 보장</strong><small>이익 계산이 맞는지 직접 확인</small></div>'),'.warning{text-align:center;padding:50px}.warning span{display:block;font-size:35px;font-weight:900;color:#64d2ff}.warning b{display:block;font-size:58px;color:#ff746b}.warning strong{display:block;font-size:40px}.warning small{display:block;margin-top:30px;font-size:28px;color:#cadbe9}',IN+"tl.fromTo('.warning>*',{opacity:0,y:18},{opacity:1,y:0,stagger:.28,duration:.25},.2);")
scene('s16-cta',76.667,82.30)
CAM=[]
for i,(t,m,z,_) in enumerate(CAM_SRC): CAM.append((0.0 if i==0 else M(t),m,z,.3 if i and CAM_SRC[i-1][1]!=m else 0))
FACE=(1000,340)
C_SRC=[(1.16,'오늘도 AI 직원을','AI 직원'),(3.10,'뽑았습니다',''),(4.00,'이번엔 클로드랑 코덱스를','클로드랑 코덱스'),(5.70,'한 팀으로 묶었어요','한 팀'),(7.60,'이름은 클로덱스 루프','클로덱스 루프'),(9.20,'둘을 연결하는',''),(10.15,'무료 오픈소스 스킬입니다','무료'),(12.52,'원본에서 소개한 조합은',''),(14.10,'페이블 5.1이 계획을 짜고','계획'),(16.25,'GPT-6 아스트라가','GPT-6 아스트라'),(17.55,'만들기 전에 계획부터 따져봐요','계획부터'),(18.86,'예를 들어 어떤 상품이','상품'),(20.55,'실제로 돈을 남기는지 보는','돈을 남기는지'),(22.20,'대시보드를 만든다고 해볼게요','대시보드'),(23.70,'매출만 봐서는 모르잖아요','매출만'),(28.26,'가격 기준 배송비 환불 광고비를','비용'),(31.55,'페이블한테 줍니다','페이블'),(33.20,'우리 사업에서 이익을 어떻게 계산할지','이익'),(36.00,'정리하고 개발 계획을 짜게 해요','개발 계획'),(39.18,'아스트라는 데이터와 계산으로','데이터와 계산'),(41.20,'계획이 맞는지 확인합니다','확인'),(43.36,'지적이 나오면 페이블이 고치고','지적'),(46.00,'다시 검토받고요','검토'),(48.28,'그다음 아스트라가 대시보드를 만들고','대시보드'),(51.10,'데이터를 연결합니다','데이터'),(53.32,'페이블은 코드가 사업 기준대로','사업 기준'),(56.00,'짜였는지 확인하고 테스트도 돌려요','테스트'),(58.82,'서로 만든 걸 서로 검사하는 거죠','서로 검사'),(62.92,'채팅창 두 개 사이에서 복붙 없이','복붙 없이'),(65.00,'계획 지적 수정이 한 흐름에 남습니다','한 흐름'),(67.64,'스킬은 무료지만','무료'),(68.58,'모델 두 개 비용은 따로 들어요','비용'),(70.58,'서로 검사해도 이익 계산이','이익 계산'),(72.78,'우리 사업에 맞는지는','우리 사업'),(73.94,'마지막에 직접 확인해야 하고요','직접 확인'),(76.88,'클로덱스 루프 스킬과 설정 방법이','설정 방법'),(79.30,'궁금하시면 댓글에 팀이라고','팀'),(81.44,'남겨주세요','')]
WARN=['비용']
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
 if tw: cam_js.append(f"tl.to('#camBox',{{...{fmt(box)},duration:.3,ease:'power2.inOut'}},{t});tl.to('#camImg',{{...{fmt(img)},duration:.3,ease:'power2.inOut'}},{t});tl.to('#camZoom',{{...{zo},duration:.3,ease:'power2.inOut'}},{t});")
 else: cam_js.append(f"tl.set('#camBox',{{autoAlpha:1,...{fmt(box)}}},{t});tl.set('#camImg',{fmt(img)},{t});tl.set('#camZoom',{zo},{t});")
def mode_at(t):
 m=CAM[0][1]
 for tt,mm,*_ in CAM:
  if tt<=t+1e-6:m=mm
 return m
CAPS=[]
for i,(s,txt,acc) in enumerate(C_SRC):
 nxt=C_SRC[i+1][0] if i+1<len(C_SRC) else 1e9
 last=max([w['end'] for w in WORDS if s-.08<=w['start']<nxt] or [s+.5])
 a=0 if i==0 else M(s);e=min(M(nxt) if nxt<1e8 else DUR,M(last)+.25)
 if i+1<len(C_SRC) and M(nxt)-e<.2:e=M(nxt)
 CAPS.append([a,round(e,3),txt,mode_at(a),acc])
scene_divs=''.join(f'<div id="{sid}" class="{"ovl" if sid in OVL else "scn"}" data-composition-id="{sid}" data-composition-src="scenes/{sid}.html" data-start="{st}" data-duration="{du}" data-track-index="{2 if sid in OVL else 0}" data-width="{W}" data-height="{H}"></div>\n' for sid,(st,du,_) in S.items())
ibox,iimg,iorg=geo(CAM[0][1])
def cssg(d): return ';'.join(re.sub(r'([A-Z])',lambda m:'-'+m[1].lower(),k)+':'+(str(v)+'px' if isinstance(v,(int,float)) else v) for k,v in d.items())
HTML=f'''<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width={W},height={H}"><title>클로덱스 루프 — Owen 스타일</title><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{lib.FONTS}body{{margin:0;background:#000;font-family:'Pretendard',sans-serif}}#root{{position:relative;width:100%;height:100%;overflow:hidden;background:#07101c}}#root *{{box-sizing:border-box}}.scn{{position:absolute;inset:0;z-index:1}}.ovl{{position:absolute;inset:0;z-index:3}}#camBox{{position:absolute;overflow:hidden;z-index:2;background:#111;opacity:1;visibility:visible;{cssg(ibox)}}}#camZoom{{position:absolute;inset:0}}#camImg{{position:absolute;{cssg(iimg)}}}#person{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}#captions{{position:absolute;inset:0;z-index:4;pointer-events:none}}.caption{{position:absolute;text-align:center;white-space:nowrap}}.caption.card{{left:64px;width:952px}}.caption.full{{left:64px;width:836px}}.caption span{{display:inline-block;font-family:'Pretendard';font-weight:800;font-size:60px;line-height:1.05;color:#fff;letter-spacing:-1px;white-space:nowrap;text-shadow:0 2px 8px #000,0 0 3px #000}}.caption b{{font-weight:inherit;color:#64d2ff}}.caption b.warn{{color:#ff3b30}}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">{scene_divs}<div id="camBox"><div id="camZoom" data-layout-allow-overflow><div id="camImg" data-layout-allow-overflow><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1" muted></video></div></div></div><div id="captions"></div><audio id="voice" src="assets/mix.m4a" data-start="0" data-duration="{DUR}" data-track-index="9"></audio></div><script>const WARN={json.dumps(WARN,ensure_ascii=False)};const CAPS={json.dumps(CAPS,ensure_ascii=False)};const CAMERA={json.dumps(CAM)};const host=document.getElementById('captions');const strip=t=>t.replace(/[.,?!\"'…“”‘’]/g,'');const esc=t=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;');CAPS.forEach((c,i)=>{{const[s,e,text,mode,acc]=c,d=document.createElement('div');d.id='cap-'+i;const m=mode==='card'?'card':'full';d.className='clip caption '+m;d.dataset.start=s;d.dataset.duration=(e-s).toFixed(3);d.dataset.trackIndex=8;d.style.top=(m==='card'?840:1345)+'px';let h=esc(strip(text)),a=strip(acc||'');if(a)h=h.replace(esc(a),'<b'+(WARN.includes(a)?' class="warn"':'')+'>'+esc(a)+'</b>');d.innerHTML='<span>'+h+'</span>';host.appendChild(d)}});function fit(){{CAPS.forEach((c,i)=>{{const sp=document.getElementById('cap-'+i).firstChild,max=c[3]==='card'?930:836;sp.style.fontSize='60px';if(sp.scrollWidth>max)sp.style.fontSize=Math.floor(60*max/sp.scrollWidth)+'px'}})}}fit();if(document.fonts)document.fonts.ready.then(fit);const tl=gsap.timeline({{paused:true}});CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');if(i===0)tl.set(el,{{opacity:1,scale:1}},0);else tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);tl.set(el,{{opacity:0}},c[1])}});CAPS.forEach((c,i)=>{{const j=CAMERA.findIndex(k=>Math.abs(k[0]-c[0])<.001&&k[3]>0);if(j>0){{const newY=CAMERA[j][1]==='card'?840:1345,textNode=document.getElementById('cap-'+i).firstChild;tl.set(textNode,{{y:1345-newY}},c[0]);tl.set(textNode,{{y:0}},c[0]+CAMERA[j][3])}}}});{chr(10).join(cam_js)}window.__timelines['main']=tl;</script></body></html>'''
os.makedirs(os.path.join(ROOT,'scenes'),exist_ok=True)
for f in os.listdir(os.path.join(ROOT,'scenes')):
 if os.path.isfile(os.path.join(ROOT,'scenes',f)):os.remove(os.path.join(ROOT,'scenes',f))
for sid,(st,du,h) in S.items():open(os.path.join(ROOT,'scenes',sid+'.html'),'w').write(h)
open(os.path.join(ROOT,'index.html'),'w').write(HTML)
EV={'scenes':{sid:[st,du,'ovl' if sid in OVL else 'scn'] for sid,(st,du,_) in S.items()},'cam':CAM,'ticks':[M(t) for t in [7.6,12.52,18.86,23.7,28.26,35.34,39.18,43.36,48.28,53.32,58.82,62.92,67.64,70.58,76.667]]}
json.dump(EV,open(os.path.join(ROOT,'events.json'),'w'),indent=2);json.dump({'captions':CAPS,'camera':CAM,'scenes':EV['scenes']},open(os.path.join(ROOT,'timing.json'),'w'),ensure_ascii=False,indent=2)
print(f'wrote {len(S)} scenes, {len(CAPS)} captions, {DUR}s')
