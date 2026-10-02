#!/usr/bin/env python3
"""Episode 12 — Jev customer inquiry classifier, approved Owen camera format."""
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
.display{font-family:'Instrument Serif',serif;font-weight:400}.data{font-family:'JetBrains Mono',monospace}
'''
S={}; OVL=set(); CAM_SRC=[]; ACTIONS=[]
LAYOUT={'s01-hook':'card','s02-name':'full','s03-ticket':'card','s04-route':'full','s05-questions':'card','s06-format':'full','s07-score':'card','s08-automation':'full','s09-branch':'card','s10-risk':'full','s11-boundary':'card','s12-cta':'card'}
PRESENTER_ONLY={'s02-name','s04-route','s06-format','s08-automation','s10-risk'}
def panel(title,body): return '<div class="panel"><div class="chrome"><i></i><i></i><i></i><em>'+title+'</em></div><div class="stage">'+body+'</div></div>'
def scene(sid,a,b,body='',css='',js='',cues=None):
    mode=LAYOUT[sid]
    if sid in PRESENTER_ONLY: body=css=js=''
    if mode=='full': assert not body.strip(),(sid,'full presenter must remain unobstructed')
    st=M(a); du=round(M(b)-st,3)
    for name,(src,sound,gain) in (cues or {}).items():
        local=round(M(src)-st,3); assert 0<=local<du,(sid,name,local,du); assert '@'+name in js
        js=js.replace('@'+name,str(local)); ACTIONS.append(dict(name=name,scene=sid,source=src,time=M(src),local=local,sound=sound,gain_db=gain))
    assert not re.search(r'@[A-Za-z]',js),(sid,'unresolved action')
    S[sid]=(st,du,lib.scene(sid,('' if mode=='full' else '<div class="gridbg"></div>')+body,css,js,'transparent'))
    if mode=='full': OVL.add(sid)
    CAM_SRC.append((a,mode,1.10 if mode=='full' else 1,0))
IN="tl.fromTo('.panel',{opacity:0,y:35,scale:.96},{opacity:1,y:0,scale:1,duration:.3,ease:'power3.out'},0);"

scene('s01-hook',3.62,8.58,'<div class="hook"><div>챗GPT랑은 전혀 다른</div><strong>판단하는 AI</strong></div>',
      '.hook{position:absolute;left:64px;top:245px;width:952px;text-align:center;font-size:66px;line-height:1.16;font-weight:900;letter-spacing:-3px;text-shadow:0 3px 18px #000}.hook strong{display:block;font-size:58px;background:#64d2ff;color:#07101c;padding:20px 8px;margin-top:22px;border-radius:17px;text-shadow:none}',
      "tl.fromTo('.hook strong',{scale:.96},{scale:1,duration:.3,ease:'back.out(1.6)'},0);")
scene('s02-name',8.92,9.98)
scene('s03-ticket',10.66,15.96,panel('새 고객 문의','<div class="ticket"><b>결제가 두 번 됐어요</b><span>빨리 해결해 주세요</span></div><div class="route">어디로 보내야 할까?</div><div class="example">문의 예시</div>'),
      '.ticket{position:absolute;left:45px;right:45px;top:55px;background:#18364e;border:2px solid #4a7698;border-radius:17px;padding:26px}.ticket b{display:block;font-size:38px}.ticket span{display:block;margin-top:16px;color:#ff746b;font-size:29px}.route{position:absolute;left:0;right:0;bottom:43px;text-align:center;font-size:39px;font-weight:900;color:#64d2ff}',IN+"tl.fromTo('.ticket',{opacity:0,y:20},{opacity:1,y:0,duration:.3},.1);tl.fromTo('.route',{opacity:0},{opacity:1,duration:.25},@route);",cues={'route':(13.72,'ui-panel-appear',-10)})
scene('s04-route',16.62,17.88)
scene('s05-questions',18.34,21.86,panel('제브에게 따로 묻기','<div class="questions"><div><b>01</b>결제 문의인가?</div><div><b>02</b>얼마나 급한가?</div><div><b>03</b>사람이 꼭 봐야 하나?</div></div><div class="example">질문 예시</div>'),
      '.questions{padding:30px 38px}.questions div{padding:20px 24px;background:#17364f;border-radius:13px;margin-bottom:14px;font-size:32px;font-weight:800}.questions b{color:#64d2ff;margin-right:24px;font-family:"JetBrains Mono"}',IN+"tl.fromTo('.questions div',{opacity:0,x:-28},{opacity:1,x:0,stagger:.3,duration:.28},@questions);",cues={'questions':(18.84,'ui-tick',-10)})
scene('s06-format',22.44,24.06)
scene('s07-score',24.06,26.12,panel('CLASSIFICATION / JSON','<pre class="json"><i>{</i>\n  <b>"category"</b>: <span>"billing"</span>,\n  <b>"urgency"</b>: <span>0.82</span>,\n  <b>"needs_human"</b>: <em>true</em>\n<i>}</i></pre><div class="meter"><span></span><strong>82%</strong></div><div class="example">구조화된 결과 예시</div>'),
      '.json{position:absolute;left:48px;top:35px;margin:0;font:25px/1.65 "JetBrains Mono";color:#c8d8e7}.json b{color:#7ccfff}.json span{color:#8fe0bd}.json em{color:#ff8a83;font-style:normal}.json i{color:#8aa1b7;font-style:normal}.meter{position:absolute;right:42px;bottom:42px;width:320px;height:18px;background:#29445a;border-radius:12px}.meter span{display:block;width:82%;height:100%;background:#64d2ff;border-radius:12px;transform-origin:left}.meter strong{position:absolute;right:0;top:-42px;font:700 26px "JetBrains Mono"}',IN+"tl.fromTo('.json',{opacity:0,x:-20},{opacity:1,x:0,duration:.3},.08);tl.fromTo('.meter span',{scaleX:0},{scaleX:1,duration:.5,ease:'power2.out'},@score);tl.fromTo('.meter strong',{opacity:0,scale:1.4},{opacity:1,scale:1,duration:.2},@score+.4);",cues={'score':(24.34,'soft-pop',-10)})
scene('s08-automation',26.56,29.88)
scene('s09-branch',30.16,36.58,panel('자동화 분류 흐름','<div class="branch"><div class="in">실제 문의</div><span>→</span><div class="ok">확실함<br><small>담당 팀</small></div><div class="maybe">애매함<br><small>사람 검토함</small></div></div><div class="example">분기 예시</div>'),
      '.branch{position:absolute;inset:65px 35px 30px;display:grid;grid-template-columns:220px 80px 1fr;grid-template-rows:1fr 1fr;gap:16px;align-items:center}.branch .in{grid-row:1/3;background:#64d2ff;color:#07101c}.branch>span{grid-row:1/3;text-align:center;font-size:55px;color:#64d2ff}.branch div{padding:24px 10px;text-align:center;border:2px solid #4a7698;border-radius:15px;font-size:32px;font-weight:900;background:#17364f}.branch small{font-size:23px;color:#c7d9e8}.branch .maybe{border-color:#ff746b}.packet{position:absolute;width:20px;height:20px;border-radius:50%;background:white;box-shadow:0 0 18px #64d2ff}',IN+"tl.fromTo('.branch div',{opacity:0,x:-20},{opacity:1,x:0,stagger:.3,duration:.28},.15);tl.to('.maybe',{borderColor:'#ff3b30',scale:1.04,duration:.25},@human);tl.to('.ok',{opacity:.35,duration:.2},@human);",cues={'human':(33.92,'soft-pop',-9)})
scene('s10-risk',37.14,42.44)
scene('s11-boundary',43.02,46.26,panel('AI가 맡는 선','<div class="boundary"><div><b>AI</b><span>문의 분류</span></div><i>≠</i><div class="human"><b>사람</b><span>환불 · 계약 결정</span></div></div>'),
      '.boundary{display:flex;align-items:center;justify-content:space-between;padding:92px 42px}.boundary div{width:330px;text-align:center;border:2px solid #64d2ff;border-radius:17px;padding:26px;background:#16364d}.boundary b{display:block;color:#64d2ff;font-size:37px}.boundary span{display:block;margin-top:14px;font-size:28px}.boundary i{font-style:normal;font-size:58px;color:#ff746b}.boundary .human{border-color:#ff746b}',IN+"tl.fromTo('.boundary>*',{opacity:0,scale:.9},{opacity:1,scale:1,stagger:.28,duration:.28},.15);")
scene('s12-cta',46.84,51.54,'<div class="cta"><div class="label">댓글 키워드</div><strong>판단</strong><span>↑</span></div>',
      '.cta{position:absolute;left:190px;top:520px;width:700px;text-align:center;background:#07101ce8;border:3px solid #64d2ff;border-radius:22px;padding:24px}.cta .label{font-size:25px}.cta strong{display:inline-block;margin-top:10px;font-size:66px;color:#64d2ff}.cta span{display:inline-block;margin-left:25px;background:#64d2ff;color:#07101c;border-radius:50%;width:60px;height:60px;line-height:60px;font-size:42px;font-weight:900}',
      "tl.fromTo('.cta',{opacity:0,scale:.88},{opacity:1,scale:1,duration:.3,ease:'back.out(1.8)'},0);")

CAM=[]
for i,(t,m,z,_) in enumerate(CAM_SRC):
    tw=.3 if i and CAM_SRC[i-1][1]!=m else 0
    CAM.append((0.0 if i==0 else M(t),m,z,tw))
FACE=(1000,320)
C_SRC=[
 (3.62,'오늘도 AI 직원을','AI 직원'),(5.38,'뽑았습니다',''),(6.32,'고객 문의부터 분류해주는','고객 문의'),(7.90,'직원인데요',''),
 (8.92,'이름은 제브입니다','제브'),(10.66,'결제가 두 번 됐어요','두 번'),(11.84,'빨리 해결해 주세요','빨리'),(12.94,'이런 문의 오면','문의'),
 (13.72,'어디로 보내야 할지부터','어디로'),(15.20,'정해야 하잖아요',''),(16.62,'제브한테 따로','제브'),(17.36,'물어보는 겁니다',''),
 (18.34,'결제 문의인지','결제 문의'),(19.10,'얼마나 급한지','급한지'),(20.14,'사람이 꼭 봐야 하는지','사람'),
 (22.44,'정해둔 형식으로 답하고','정해둔 형식'),(24.06,'확률과 확신도도','확률과 확신도'),(25.36,'같이 주게 됩니다',''),
 (26.56,'그다음 자동화 도구에 연결해서','자동화 도구'),(28.84,'문의를 나눕니다',''),
 (30.16,'실제 문의로 어디서 틀리는지','실제 문의'),(32.14,'확인해서 기준을 정하고','기준'),(33.92,'애매한 건 사람 검토함으로','사람 검토함'),(36.02,'보내는 거예요',''),
 (37.14,'환불이나 계약처럼','환불이나 계약'),(38.32,'잘못 처리하면 곤란한 건','잘못 처리'),(40.30,'처음부터 사람이 보게 해주세요','사람'),
 (43.02,'분류를 맡기는 거지','분류'),(43.98,'결정을 다 넘기는 건 아닙니다','결정'),
 (46.84,'제브로 문의 분류하는 법이','제브'),(48.26,'궁금하시면 댓글에','댓글'),(50.00,'판단이라고 남겨주세요','판단')]
WARN=['빨리','환불이나 계약','잘못 처리','사람']
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
HTML=f'''<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width={W},height={H}"><title>애매한 고객 문의만 사람에게 넘기는 제브 활용법</title><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{lib.FONTS}
body{{margin:0;background:#000;font-family:'Pretendard',sans-serif}}#root{{position:relative;width:100%;height:100%;overflow:hidden;background:#07101c}}#root *{{box-sizing:border-box}}.scn{{position:absolute;inset:0;z-index:1}}.ovl{{position:absolute;inset:0;z-index:3}}
#camBox{{position:absolute;overflow:hidden;z-index:2;background:#111;opacity:1;visibility:visible;{cssg(ib)}}}#camZoom{{position:absolute;inset:0}}#camImg{{position:absolute;{cssg(ii)}}}#person{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#captions{{position:absolute;inset:0;z-index:4;pointer-events:none}}.caption{{position:absolute;text-align:center;white-space:nowrap}}.caption.card{{left:64px;width:952px}}.caption.full{{left:64px;width:836px}}.caption span{{display:inline-block;font-family:'Pretendard';font-weight:800;font-size:60px;line-height:1.05;color:#fff;letter-spacing:-1px;white-space:nowrap;text-shadow:0 2px 8px #000,0 0 3px #000,0 0 3px #000}}.caption b{{font-weight:inherit;color:#64d2ff}}.caption b.warn{{color:#ff3b30}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">{scene_divs}<div id="camBox"><div id="camZoom" data-layout-allow-overflow><div id="camImg" data-layout-allow-overflow><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1" muted></video></div></div></div><div id="captions"></div><audio id="voice" src="assets/mix.m4a" data-start="0" data-duration="{DUR}" data-track-index="9"></audio></div>
<script>const WARN={json.dumps(WARN,ensure_ascii=False)};const CAPS={json.dumps(CAPS,ensure_ascii=False)};const CAMERA={json.dumps(CAM)};const host=document.getElementById('captions');const strip=t=>t.replace(/[.,?!"'…“”‘’]/g,'');const esc=t=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;');CAPS.forEach((c,i)=>{{const [s,e,text,mode,acc]=c;const d=document.createElement('div');d.id='cap-'+i;const m=mode==='card'?'card':'full';d.className='clip caption '+m;d.dataset.start=s;d.dataset.duration=(e-s).toFixed(3);d.dataset.trackIndex=8;d.style.top=(m==='card'?840:1345)+'px';let h=esc(strip(text));const a=strip(acc||'');if(a)h=h.replace(esc(a),'<b'+(WARN.includes(a)?' class="warn"':'')+'>'+esc(a)+'</b>');d.innerHTML='<span>'+h+'</span>';host.appendChild(d);}});function fit(){{CAPS.forEach((c,i)=>{{const sp=document.getElementById('cap-'+i).firstChild,max=c[3]==='card'?930:836;sp.style.fontSize='60px';if(sp.scrollWidth>max)sp.style.fontSize=Math.floor(60*max/sp.scrollWidth)+'px';}})}}fit();if(document.fonts)document.fonts.ready.then(fit);const tl=gsap.timeline({{paused:true}});CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');if(i===0)tl.set(el,{{opacity:1,scale:1}},0);else tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);tl.set(el,{{opacity:0}},c[1]);}});CAPS.forEach((c,i)=>{{const j=CAMERA.findIndex(k=>Math.abs(k[0]-c[0])<.001&&k[3]>0);if(j>0){{const newY=CAMERA[j][1]==='card'?840:1345,textNode=document.getElementById('cap-'+i).firstChild;tl.set(textNode,{{y:1345-newY}},c[0]);tl.set(textNode,{{y:0}},c[0]+CAMERA[j][3]);}}}});{''.join(cam_js)}window.__timelines['main']=tl;</script></body></html>'''
os.makedirs(os.path.join(ROOT,'scenes'),exist_ok=True)
for sid,(st,du,sh) in S.items(): open(os.path.join(ROOT,'scenes',sid+'.html'),'w').write(sh)
open(os.path.join(ROOT,'index.html'),'w').write(HTML)
EV={'scenes':{sid:[st,du,'ovl' if sid in OVL else 'scn'] for sid,(st,du,_) in S.items()},'cam':CAM,'actions':ACTIONS}
json.dump(EV,open(os.path.join(ROOT,'events.json'),'w'),indent=2);json.dump({'captions':CAPS,'camera':CAM,'scenes':EV['scenes']},open(os.path.join(ROOT,'timing.json'),'w'),ensure_ascii=False,indent=2)
print(f'wrote {len(S)} scenes, {len(CAPS)} captions, {DUR}s')
