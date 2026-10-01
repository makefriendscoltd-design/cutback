#!/usr/bin/env python3
"""Episode 11 — Omnisend email AI employee, approved Owen camera format."""
import os, sys, json, re
ROOT=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(ROOT,'..','nick-plugins-mg'))
import build as lib
W,H=1080,1920
CUTS=json.load(open(os.path.join(ROOT,'cuts.json'))); DUR=CUTS['duration']; SEGS=CUTS['segments']
TX=json.load(open(os.path.join(ROOT,'src/transcript.json')))['raw']; WORDS=[w for s in TX for w in s['words']]
def M(t):
    for s in SEGS:
        if t<s['src_start']: return s['out_start']
        if t<=s['src_end']: return round(s['out_start']+t-s['src_start'],3)
    return DUR

NAVY='linear-gradient(180deg,#07101c,#0d1b2e)'
lib.BASE += '''
#root{color:#f5f9ff}.panel{position:absolute;left:64px;top:300px;width:952px;height:520px;border:2px solid #315776;border-radius:28px;background:#0b1728;overflow:hidden;box-shadow:0 25px 60px #0008}
.chrome{height:52px;background:#0c1726;border-bottom:1px solid #315776;display:flex;align-items:center;gap:9px;padding:0 22px;color:#bed2e9;font-size:20px;font-family:'JetBrains Mono'}
.chrome i{width:10px;height:10px;border-radius:100%;background:#64d2ff}.chrome em{font-style:normal;margin-left:15px}.stage{position:absolute;left:0;right:0;top:52px;bottom:0;overflow:hidden}
.gridbg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 30%,#163450 0%,transparent 65%),repeating-linear-gradient(0deg,#64d2ff0b 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,#64d2ff0b 0 1px,transparent 1px 48px)}
.label{font-size:23px;letter-spacing:3px;color:#a9c4df;font-weight:700}.cyan{color:#64d2ff}.red{color:#ff3b30}.big{font-weight:900;font-size:62px;line-height:1.2}.small{font-size:27px;line-height:1.5;color:#d8e5f2}.example{position:absolute;right:22px;top:15px;font-size:19px;color:#aac1d7}
'''
S={}; OVL=set(); CAM_SRC=[]
LAYOUT={'s01-hook':'card','s02-connect':'card','s03-friction':'full','s04-ask':'card','s05-prompts':'card','s06-data':'full','s07-draft':'card','s08-read':'full','s09-permission':'card','s10-review':'full','s11-ebook':'card','s12-cta':'full'}
PRESENTER_ONLY={'s03-friction','s06-data','s08-read','s10-review'}
def panel(title,body): return '<div class="panel"><div class="chrome"><i></i><i></i><i></i><em>'+title+'</em></div><div class="stage">'+body+'</div></div>'
def scene(sid,a,b,body='',css='',js=''):
    mode=LAYOUT[sid]
    if sid in PRESENTER_ONLY: body=css=js=''
    st=M(a); du=round(M(b)-st,3)
    S[sid]=(st,du,lib.scene(sid,('' if mode=='full' else '<div class="gridbg"></div>')+body,css,js,'transparent'))
    if mode=='full': OVL.add(sid)
    CAM_SRC.append((a,mode,1.10 if mode=='full' else 1,0))
IN="tl.fromTo('.panel',{opacity:0,y:35,scale:.96},{opacity:1,y:0,scale:1,duration:.3,ease:'power3.out'},0);"

scene('s01-hook',3.78,8.26,'<div class="hook"><div>이메일 성과 분석부터</div><strong>초안까지 맡기는 AI 직원</strong></div>',
      '.hook{position:absolute;left:64px;top:245px;width:952px;text-align:center;font-size:66px;line-height:1.16;font-weight:900;letter-spacing:-3px;text-shadow:0 3px 18px #000}.hook strong{display:block;font-size:58px;background:#64d2ff;color:#07101c;padding:20px 8px;margin-top:22px;border-radius:17px;text-shadow:none}',
      "tl.fromTo('.hook strong',{scale:.96},{scale:1,duration:.3,ease:'back.out(1.6)'},0);")
scene('s02-connect',8.80,11.50,panel('OMNISEND / AI 연결','<div class="connect"><div>Omnisend</div><span>↔</span><div>ChatGPT<br><small>또는 Claude</small></div></div><div class="example">연결 흐름 예시</div>'),
      '.connect{display:flex;align-items:center;justify-content:space-between;padding:95px 42px}.connect div{width:330px;text-align:center;border:2px solid #64d2ff;border-radius:18px;padding:28px 10px;font-size:39px;font-weight:900;background:#14324a}.connect span{font-size:72px;color:#64d2ff}.connect small{font-size:23px;color:#c8d9e8}',IN+"tl.fromTo('.connect span',{opacity:0,scale:.6},{opacity:1,scale:1,duration:.3,ease:'back.out(2)'},.35);")
scene('s03-friction',13.88,18.30)
scene('s04-ask',18.30,20.20,panel('성과를 말로 물어보기','<div class="chat"><span>나</span><p>지난달 성과를 정리해줘</p></div><div class="reply"><b>AI</b><p>계정 데이터를 확인할게요</p></div><div class="example">대화 예시</div>'),
      '.chat,.reply{position:absolute;left:40px;right:40px;padding:22px;border-radius:16px;font-size:31px}.chat{top:70px;background:#17364f}.reply{top:230px;background:#10273b}.chat span,.reply b{display:inline-block;width:62px;color:#64d2ff}.chat p,.reply p{display:inline;margin:0}',IN+"tl.fromTo('.reply',{opacity:0,y:18},{opacity:1,y:0,duration:.28},.45);")
scene('s05-prompts',20.74,25.48,panel('바로 묻는 두 가지','<div class="prompts"><div><b>01</b>지난달 매출 만든 이메일 찾아줘</div><div><b>02</b>잘된 메일 공통점 정리해줘</div></div><div class="example">명령 예시</div>'),
      '.prompts{padding:60px 35px}.prompts div{padding:28px 24px;background:#17364f;border:2px solid #3e6683;border-radius:15px;margin-bottom:22px;font-size:31px;font-weight:800}.prompts b{color:#64d2ff;margin-right:22px;font-family:"JetBrains Mono"}',IN+"tl.fromTo('.prompts div',{opacity:0,x:-30},{opacity:1,x:0,stagger:.45,duration:.3},.2);")
scene('s06-data',25.92,28.16)
scene('s07-draft',28.74,33.38,panel('분석 다음 단계','<div class="flow"><div>고객군 만들기</div><i>→</i><div>이메일 초안</div></div><div class="draft">DRAFT <span>발송 전</span></div><div class="example">활용 흐름 예시</div>'),
      '.flow{display:flex;align-items:center;justify-content:space-between;padding:80px 35px 0}.flow div{width:330px;padding:30px 8px;text-align:center;border:2px solid #64d2ff;border-radius:16px;font-size:33px;font-weight:900;background:#15374b}.flow i{font-style:normal;font-size:58px;color:#64d2ff}.draft{position:absolute;left:310px;bottom:42px;border:2px solid #527894;border-radius:10px;padding:13px 22px;font:700 27px "JetBrains Mono"}.draft span{color:#64d2ff;margin-left:20px}',IN+"tl.fromTo('.flow>*',{opacity:0,x:-22},{opacity:1,x:0,stagger:.35,duration:.28},.25);tl.fromTo('.draft',{opacity:0,y:16},{opacity:1,y:0,duration:.25},1.1);")
scene('s08-read',33.96,38.54)
scene('s09-permission',39.20,42.46,panel('권한은 나눠서','<div class="perm"><div><span>성과 분석</span><strong>읽기 권한</strong></div><div><span>고객군 · 캠페인 생성</span><strong>쓰기 권한</strong></div></div><div class="example">권한 설정 원칙</div>'),
      '.perm{padding:52px 40px}.perm div{display:flex;align-items:center;justify-content:space-between;padding:28px;background:#16344b;border-radius:15px;margin-bottom:20px;font-size:29px}.perm strong{font-size:33px;color:#64d2ff;border:2px solid #64d2ff;border-radius:10px;padding:12px 16px}',IN+"tl.fromTo('.perm div',{opacity:0,y:24},{opacity:1,y:0,stagger:.4,duration:.3},.2);")
scene('s10-review',43.02,47.16,'<div class="review"><div class="label">발송 전 직접 확인</div><div><b>01</b>대상</div><div><b>02</b>링크</div><div><b>03</b>할인 조건</div></div>',
      '.review{position:absolute;left:95px;right:95px;top:280px;text-align:center}.review>.label{font-size:31px;margin-bottom:26px;color:#fff}.review>div:not(.label){display:inline-block;width:255px;margin:8px;padding:25px 8px;background:#0b1728e8;border:2px solid #64d2ff;border-radius:17px;font-size:36px;font-weight:900}.review b{display:block;color:#64d2ff;font:700 25px "JetBrains Mono";margin-bottom:10px}',
      "tl.fromTo('.review>div:not(.label)',{opacity:0,y:24},{opacity:1,y:0,stagger:.28,duration:.3},.1);")
scene('s11-ebook',47.74,52.28,panel('전자책으로 정리 중','<div class="chapters"><div><b>01</b>AI 활용법</div><div><b>02</b>최신 정보</div><div><b>03</b>수익화 방법</div></div>'),
      '.chapters{padding:35px 42px}.chapters div{padding:23px 25px;background:#163149;border-radius:12px;margin-bottom:17px;font-size:38px;font-weight:800}.chapters b{color:#64d2ff;margin-right:40px;font-family:"JetBrains Mono"}',IN+"tl.fromTo('.chapters div',{opacity:0,x:-35},{opacity:1,x:0,stagger:.4,duration:.3},.15);")
scene('s12-cta',52.88,56.12,'<div class="cta"><div class="label">댓글 키워드</div><strong>전자책</strong><span>↑</span></div>',
      '.cta{position:absolute;left:64px;top:1080px;width:836px;text-align:center;background:#07101ce8;border:3px solid #64d2ff;border-radius:22px;padding:24px}.cta .label{font-size:25px}.cta strong{display:inline-block;margin-top:10px;font-size:66px;color:#64d2ff}.cta span{display:inline-block;margin-left:25px;background:#64d2ff;color:#07101c;border-radius:50%;width:60px;height:60px;line-height:60px;font-size:42px;font-weight:900}',
      "tl.fromTo('.cta',{opacity:0,scale:.88},{opacity:1,scale:1,duration:.3,ease:'back.out(1.8)'},0);")

CAM=[]
for i,(t,m,z,_) in enumerate(CAM_SRC):
    tw=.3 if i and CAM_SRC[i-1][1]!=m else 0
    CAM.append((0.0 if i==0 else M(t),m,z,tw))
FACE=(1000,320)
C_SRC=[
 (3.78,'오늘도 AI 직원을','AI 직원'),(4.70,'뽑았습니다',''),(6.26,'이번에는 이메일 마케팅','이메일 마케팅'),(7.66,'담당이에요',''),
 (8.80,'옴니센드에 챗GPT나','옴니센드'),(10.20,'클로드를 연결하는 겁니다','클로드'),
 (13.88,'이메일 보냈는데','이메일'),(14.78,'뭐가 잘됐는지 보려면','잘됐는지'),(16.52,'이것저것 눌러봐야 하잖아요',''),
 (18.30,'연결해두면 말로','말로'),(19.42,'물어볼 수 있습니다',''),
 (20.74,'지난달 매출을 만든','매출'),(21.86,'이메일 찾아줘','이메일'),(23.20,'잘된 메일은 뭐가 비슷한지','잘된 메일'),(24.98,'정리해줘',''),
 (25.92,'실제 계정 데이터를 보고','실제 계정 데이터'),(27.22,'답을 해주는 겁니다',''),
 (28.74,'다음에 보낼 고객군을 만들고','고객군'),(30.84,'이메일 초안 쓰는 것까지','이메일 초안'),(32.34,'다 맡길 수 있고요',''),
 (33.96,'대신 성과만 볼 거면','성과만'),(37.16,'읽기 권한만 주세요','읽기 권한'),
 (39.20,'고객군이나 캠페인 만들 때','캠페인'),(40.68,'필요한 쓰기 권한은','쓰기 권한'),(41.86,'따로 주고요',''),
 (43.02,'보내기 전에 대상이나 링크','대상이나 링크'),(45.12,'할인 조건은 직접','직접'),(46.20,'확인하셔야 됩니다',''),
 (47.74,'이런 AI 활용법부터','AI 활용법'),(49.10,'최신 정보 수익화 방법까지','수익화 방법'),(50.86,'전자책으로 정리하고 있습니다','전자책'),
 (52.88,'궁금하신 분들은 댓글에','댓글'),(54.46,'전자책이라고 남겨주세요','전자책')]
WARN=['보내기 전에','할인 조건','직접']
def geo(mode):
    if mode=='card':
        box=dict(left=40,top=880,width=1000,height=1040,borderRadius='80px 80px 0 0'); s=1040/1080
        img=dict(width=1920*s,height=1040,left=500-FACE[0]*s,top=0); org=(500,FACE[1]*s)
    else:
        box=dict(left=0,top=0,width=1080,height=1920,borderRadius='0px'); s=1920/1080
        img=dict(width=1920*s,height=1920,left=540-FACE[0]*s,top=-40); org=(540,FACE[1]*s-40)
    return box,img,org
fmt=lambda d:'{'+','.join(f'{k}:{json.dumps(round(v,1) if isinstance(v,float) else v)}' for k,v in d.items())+'}'
cam_js=[]
for t,mode,z,tw in CAM:
    box,img,org=geo(mode); zo=f"{{scale:{z},transformOrigin:'{org[0]:.0f}px {org[1]:.0f}px'}}"
    if tw:
        cam_js.append(f"tl.to('#camBox',{{...{fmt(box)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camImg',{{...{fmt(img)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camZoom',{{...{zo},duration:{tw},ease:'power2.inOut'}},{t});")
    else:
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:1,...{fmt(box)}}},{t});tl.set('#camImg',{fmt(img)},{t});tl.set('#camZoom',{zo},{t});")
for i,(t,mode,z,tw) in enumerate(CAM):
    nxt=CAM[i+1][0] if i+1<len(CAM) else DUR
    if nxt-t>.8 and not (i+1<len(CAM) and CAM[i+1][3]): cam_js.append(f"tl.to('#camZoom',{{scale:{z*1.035:.3f},duration:{nxt-t-max(tw,0)-.05:.2f},ease:'none'}},{t+max(tw,0)+.01:.2f});")
def mode_at(t):
    m=CAM[0][1]
    for tt,mm,*_ in CAM:
        if tt<=t+1e-6:m=mm
    return m
CAPS=[]
for i,(s,txt,acc) in enumerate(C_SRC):
    nxt=C_SRC[i+1][0] if i+1<len(C_SRC) else 1e9
    last=max([w['end'] for w in WORDS if s-.01<=w['start']<nxt] or [s+.5])
    a=0.0 if i==0 else M(s); e=min(M(nxt) if nxt<1e8 else DUR,M(last)+.35)
    if i+1<len(C_SRC) and M(nxt)-e<.25:e=M(nxt)
    CAPS.append([a,round(e,3),txt,mode_at(a),acc])
scene_divs=''.join(f'<div id="{sid}" class="{"ovl" if sid in OVL else "scn"}" data-composition-id="{sid}" data-composition-src="scenes/{sid}.html" data-start="{st}" data-duration="{du}" data-track-index="{2 if sid in OVL else 0}" data-width="{W}" data-height="{H}"></div>\n' for sid,(st,du,_) in S.items())
ib,ii,io=geo(CAM[0][1])
def cssg(d): return ';'.join(re.sub(r'([A-Z])',lambda m:'-'+m[1].lower(),k)+':'+(str(v)+'px' if isinstance(v,(int,float)) else v) for k,v in d.items())
HTML=f'''<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width={W},height={H}"><title>이메일 성과 분석부터 초안까지 맡기는 AI 직원</title><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{lib.FONTS}
body{{margin:0;background:#000;font-family:'Pretendard',sans-serif}}#root{{position:relative;width:100%;height:100%;overflow:hidden;background:#07101c}}#root *{{box-sizing:border-box}}.scn{{position:absolute;inset:0;z-index:1}}.ovl{{position:absolute;inset:0;z-index:3}}
#camBox{{position:absolute;overflow:hidden;z-index:2;background:#111;opacity:1;visibility:visible;{cssg(ib)}}}#camZoom{{position:absolute;inset:0}}#camImg{{position:absolute;{cssg(ii)}}}#person{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#captions{{position:absolute;inset:0;z-index:4;pointer-events:none}}.caption{{position:absolute;text-align:center;white-space:nowrap}}.caption.card{{left:64px;width:952px}}.caption.full{{left:64px;width:836px}}.caption span{{display:inline-block;font-family:'Pretendard';font-weight:800;font-size:60px;line-height:1.05;color:#fff;letter-spacing:-1px;white-space:nowrap;text-shadow:0 2px 8px #000,0 0 3px #000,0 0 3px #000}}.caption b{{font-weight:inherit;color:#64d2ff}}.caption b.warn{{color:#ff3b30}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">{scene_divs}<div id="camBox"><div id="camZoom" data-layout-allow-overflow><div id="camImg" data-layout-allow-overflow><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1" muted></video></div></div></div><div id="captions"></div><audio id="voice" src="assets/mix.m4a" data-start="0" data-duration="{DUR}" data-track-index="9"></audio></div>
<script>const WARN={json.dumps(WARN,ensure_ascii=False)};const CAPS={json.dumps(CAPS,ensure_ascii=False)};const CAMERA={json.dumps(CAM)};const host=document.getElementById('captions');const strip=t=>t.replace(/[.,?!"'…“”‘’]/g,'');const esc=t=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;');CAPS.forEach((c,i)=>{{const [s,e,text,mode,acc]=c;const d=document.createElement('div');d.id='cap-'+i;const m=mode==='card'?'card':'full';d.className='clip caption '+m;d.dataset.start=s;d.dataset.duration=(e-s).toFixed(3);d.dataset.trackIndex=8;d.style.top=(m==='card'?840:1345)+'px';let h=esc(strip(text));const a=strip(acc||'');if(a)h=h.replace(esc(a),'<b'+(WARN.includes(a)?' class="warn"':'')+'>'+esc(a)+'</b>');d.innerHTML='<span>'+h+'</span>';host.appendChild(d);}});function fit(){{CAPS.forEach((c,i)=>{{const sp=document.getElementById('cap-'+i).firstChild,max=c[3]==='card'?930:836;sp.style.fontSize='60px';if(sp.scrollWidth>max)sp.style.fontSize=Math.floor(60*max/sp.scrollWidth)+'px';}})}}fit();if(document.fonts)document.fonts.ready.then(fit);const tl=gsap.timeline({{paused:true}});CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');if(i===0)tl.set(el,{{opacity:1,scale:1}},0);else tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);tl.set(el,{{opacity:0}},c[1]);}});CAPS.forEach((c,i)=>{{const j=CAMERA.findIndex(k=>Math.abs(k[0]-c[0])<.001&&k[3]>0);if(j>0){{const newY=CAMERA[j][1]==='card'?840:1345,textNode=document.getElementById('cap-'+i).firstChild;tl.set(textNode,{{y:1345-newY}},c[0]);tl.set(textNode,{{y:0}},c[0]+CAMERA[j][3]);}}}});{''.join(cam_js)}window.__timelines['main']=tl;</script></body></html>'''
os.makedirs(os.path.join(ROOT,'scenes'),exist_ok=True)
for sid,(st,du,sh) in S.items(): open(os.path.join(ROOT,'scenes',sid+'.html'),'w').write(sh)
open(os.path.join(ROOT,'index.html'),'w').write(HTML)
EV={'scenes':{sid:[st,du,'ovl' if sid in OVL else 'scn'] for sid,(st,du,_) in S.items()},'cam':CAM,'ticks':[M(t) for t in [8.8,18.3,20.74,23.2,28.74,30.84,39.2,40.68,43.02,45.12,47.74,49.1,54.46]]}
json.dump(EV,open(os.path.join(ROOT,'events.json'),'w'),indent=2);json.dump({'captions':CAPS,'camera':CAM,'scenes':EV['scenes']},open(os.path.join(ROOT,'timing.json'),'w'),ensure_ascii=False,indent=2)
print(f'wrote {len(S)} scenes, {len(CAPS)} captions, {DUR}s')
