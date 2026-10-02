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
.display{font-family:Georgia,serif;font-weight:400}.data{font-family:'JetBrains Mono',monospace}
'''
S={}; OVL=set(); CAM_SRC=[]; ACTIONS=[]
LAYOUT={'s01-hook':'card','s02-connect':'card','s03-friction':'full','s04-ask':'card','s05-prompts':'card','s06-data':'full','s07-draft':'card','s08-read':'full','s09-permission':'card','s10-review':'card','s11-ebook':'full','s12-cta':'card'}
PRESENTER_ONLY={'s03-friction','s06-data','s08-read','s11-ebook'}
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

scene('s01-hook',3.78,8.26,'<div class="hook"><div>클로드가 이제</div><strong>이메일 마케팅까지 직접?</strong></div>',
      '.hook{position:absolute;left:64px;top:245px;width:952px;text-align:center;font-size:66px;line-height:1.16;font-weight:900;letter-spacing:-3px;text-shadow:0 3px 18px #000}.hook strong{display:block;font-size:58px;background:#64d2ff;color:#07101c;padding:20px 8px;margin-top:22px;border-radius:17px;text-shadow:none}',
      "tl.fromTo('.hook strong',{scale:.96},{scale:1,duration:.3,ease:'back.out(1.6)'},0);")
scene('s02-connect',8.80,11.50,panel('OMNISEND / AI 연결','<div class="connect"><div>Omnisend</div><span>↔</span><div>ChatGPT<br><small>또는 Claude</small></div></div><div class="example">연결 흐름 예시</div>'),
      '.connect{display:flex;align-items:center;justify-content:space-between;padding:95px 42px}.connect div{width:330px;text-align:center;border:2px solid #64d2ff;border-radius:18px;padding:28px 10px;font-size:39px;font-weight:900;background:#14324a}.connect span{font-size:72px;color:#64d2ff}.connect small{font-size:23px;color:#c8d9e8}',IN+"tl.fromTo('.connect span',{opacity:0,scale:.6},{opacity:1,scale:1,duration:.3,ease:'back.out(2)'},@link);",cues={'link':(9.72,'ui-tick',-10)})
scene('s03-friction',13.88,18.30)
scene('s04-ask',18.30,20.20,panel('성과를 말로 물어보기','<div class="chat"><span>나</span><p>지난달 성과를 정리해줘</p></div><div class="reply"><b>AI</b><p>계정 데이터를 확인할게요</p></div><div class="example">대화 예시</div>'),
      '.chat,.reply{position:absolute;left:40px;right:40px;padding:22px;border-radius:16px;font-size:31px}.chat{top:70px;background:#17364f}.reply{top:230px;background:#10273b}.chat span,.reply b{display:inline-block;width:62px;color:#64d2ff}.chat p,.reply p{display:inline;margin:0}',IN+"tl.fromTo('.reply',{opacity:0,y:18},{opacity:1,y:0,duration:.28},@reply);",cues={'reply':(19.20,'ui-panel-appear',-11)})
scene('s05-prompts',20.74,25.48,panel('CAMPAIGN PERFORMANCE','<div class="mailrows"><div><b>봄 클래스 오픈</b><i>₩4.8M</i><span style="--w:88%"></span></div><div><b>신규 구독자 안내</b><i>₩2.1M</i><span style="--w:46%"></span></div><div><b>주말 리마인드</b><i>₩3.4M</i><span style="--w:67%"></span></div></div><div class="focusrect"></div><div class="insight"><small>AI SUMMARY</small><strong>매출 1위 메일 선택</strong><em>공통점 분석 중 ···</em></div><div class="example">성과 화면 예시</div>'),
      '.mailrows{padding:40px 34px}.mailrows div{position:relative;height:82px;padding:15px 18px;background:#112b40;border-bottom:1px solid #36536c;font-size:24px}.mailrows b{display:inline-block;width:430px}.mailrows i{font:700 23px "JetBrains Mono";font-style:normal;color:#dcecff}.mailrows span{position:absolute;left:18px;bottom:8px;width:var(--w);height:5px;background:#64d2ff;border-radius:5px}.focusrect{position:absolute;left:27px;top:34px;width:897px;height:92px;border:4px solid #64d2ff;border-radius:8px}.insight{position:absolute;right:32px;bottom:24px;width:430px;padding:18px 22px;background:#f1f6f8;color:#10283a;border-radius:12px;box-shadow:0 15px 40px #0007}.insight small{font:700 17px "JetBrains Mono";color:#39728c}.insight strong{display:block;font-size:28px;margin:7px 0}.insight em{font-style:normal;font-size:20px;color:#5d7484}',IN+"tl.fromTo('.mailrows div',{opacity:0,x:-24},{opacity:1,x:0,stagger:.16,duration:.22},.08);tl.fromTo('.focusrect',{opacity:0,scaleX:.7},{opacity:1,scaleX:1,duration:.28},@prompt);tl.fromTo('.insight',{opacity:0,y:34,scale:.92},{opacity:1,y:0,scale:1,duration:.3,ease:'back.out(1.5)'},@summary);",cues={'prompt':(21.30,'ui-tick',-10),'summary':(23.20,'ui-panel-appear',-10)})
scene('s06-data',25.92,28.16)
scene('s07-draft',28.74,33.38,panel('AUDIENCE → DRAFT','<div class="filter"><small>AUDIENCE FILTER</small><div><b>최근 구매</b><i></i></div><div><b>이메일 열람</b><i></i></div></div><div class="compose"><small>EMAIL DRAFT</small><strong>다시 만나 반가워요</strong><p>지난 관심 상품을 바탕으로<br>새 소식을 준비했습니다.</p><em>발송 전 검토</em></div><svg class="handoff"><path d="M390 210 C470 210 470 210 550 210"/><circle cx="390" cy="210" r="8"/></svg><div class="example">고객군·초안 화면 예시</div>'),
      '.filter{position:absolute;left:35px;top:54px;width:350px;padding:20px;background:#122d43;border-radius:14px}.filter small{font:700 17px "JetBrains Mono";letter-spacing:2px;color:#83a8c2}.compose small{font:700 17px "JetBrains Mono";letter-spacing:2px;color:#516f83}.filter div{display:flex;justify-content:space-between;font-size:23px;padding:18px 0;border-bottom:1px solid #35536a}.filter i{width:54px;height:28px;border-radius:20px;background:#31516a;position:relative}.filter i:after{content:"";position:absolute;width:22px;height:22px;left:3px;top:3px;border-radius:50%;background:#9ab1c2}.filter .on i{background:#2e829b}.filter .on i:after{left:29px;background:#e9fbff}.compose{position:absolute;right:32px;top:48px;width:450px;height:340px;padding:22px 27px;background:#f4f7f8;color:#132a3a;border-radius:14px}.compose strong{display:block;font:400 39px Georgia;margin:23px 0 12px}.compose p{font-size:21px;line-height:1.55;color:#435c6c}.compose em{position:absolute;right:20px;bottom:18px;font:700 17px "JetBrains Mono";font-style:normal;color:#2e7189}.handoff{position:absolute;inset:0;width:952px;height:468px}.handoff path{fill:none;stroke:#64d2ff;stroke-width:4;stroke-dasharray:180;stroke-dashoffset:180}.handoff circle{fill:#dffaff}',IN+"tl.set('.compose',{opacity:.18},0);tl.to('.filter div:first-of-type',{className:'+=on',duration:.01},@segment);tl.to('.filter div:nth-of-type(2)',{className:'+=on',duration:.01},@segment+.35);tl.to('.handoff path',{strokeDashoffset:0,duration:.45,ease:'none'},@segment+.3);tl.to('.handoff circle',{x:160,duration:.45,ease:'none'},@segment+.3);tl.to('.compose',{opacity:1,duration:.25},@draft);tl.fromTo('.compose strong,.compose p',{opacity:0},{opacity:1,stagger:.2,duration:.22},@draft);",cues={'segment':(29.28,'ui-tick',-10),'draft':(30.84,'ui-panel-appear',-10)})
scene('s08-read',33.96,38.54)
scene('s09-permission',39.20,42.46,panel('ACCESS CONTROL','<div class="perm"><div><span>성과 데이터 읽기</span><i class="toggle on"></i></div><div><span>고객군 생성</span><i class="toggle"></i></div><div><span>캠페인 발송</span><i class="toggle locked">LOCK</i></div></div><div class="scope">필요할 때만 쓰기 권한 추가</div><div class="example">권한 설정 예시</div>'),
      '.perm{padding:38px 42px}.perm div{display:flex;align-items:center;justify-content:space-between;padding:20px 24px;background:#16344b;border-radius:12px;margin-bottom:13px;font-size:25px}.toggle{position:relative;width:66px;height:34px;border-radius:20px;background:#38556b}.toggle:after{content:"";position:absolute;width:26px;height:26px;border-radius:50%;background:#9db1c0;left:4px;top:4px}.toggle.on{background:#2b839d}.toggle.on:after{left:36px;background:white}.toggle.locked{width:82px;border-radius:7px;color:#ff8a83;background:#452f39;font:700 16px/34px "JetBrains Mono";text-align:center}.toggle.locked:after{display:none}.scope{position:absolute;right:42px;bottom:24px;color:#64d2ff;font-size:21px}',IN+"tl.fromTo('.perm div',{opacity:0,x:-24},{opacity:1,x:0,stagger:.16,duration:.22},.08);tl.to('.perm div:nth-child(2) .toggle',{className:'toggle on',duration:.01},@write);tl.fromTo('.scope',{opacity:0,y:12},{opacity:1,y:0,duration:.2},@write);",cues={'write':(40.68,'ui-tick',-10)})
scene('s10-review',43.02,47.16,'<div class="review"><div class="label">발송 전 직접 확인</div><div><b>01</b>대상</div><div><b>02</b>링크</div><div><b>03</b>할인 조건</div></div>',
      '.review{position:absolute;left:95px;right:95px;top:280px;text-align:center}.review>.label{font-size:31px;margin-bottom:26px;color:#fff}.review>div:not(.label){display:inline-block;width:255px;margin:8px;padding:25px 8px;background:#0b1728e8;border:2px solid #64d2ff;border-radius:17px;font-size:36px;font-weight:900}.review b{display:block;color:#64d2ff;font:700 25px "JetBrains Mono";margin-bottom:10px}',
      "tl.fromTo('.review>div:not(.label)',{opacity:0,y:24},{opacity:1,y:0,stagger:.28,duration:.3},.1);")
scene('s11-ebook',47.74,52.28,panel('전자책으로 정리 중','<div class="chapters"><div><b>01</b>AI 활용법</div><div><b>02</b>최신 정보</div><div><b>03</b>수익화 방법</div></div>'),
      '.chapters{padding:35px 42px}.chapters div{padding:23px 25px;background:#163149;border-radius:12px;margin-bottom:17px;font-size:38px;font-weight:800}.chapters b{color:#64d2ff;margin-right:40px;font-family:"JetBrains Mono"}',IN+"tl.fromTo('.chapters div',{opacity:0,x:-35},{opacity:1,x:0,stagger:.4,duration:.3},.15);")
scene('s12-cta',52.88,56.12,'<div class="cta"><div class="label">댓글 키워드</div><strong>전자책</strong><span>↑</span></div>',
      '.cta{position:absolute;left:190px;top:520px;width:700px;text-align:center;background:#07101ce8;border:3px solid #64d2ff;border-radius:22px;padding:24px}.cta .label{font-size:25px}.cta strong{display:inline-block;margin-top:10px;font-size:66px;color:#64d2ff}.cta span{display:inline-block;margin-left:25px;background:#64d2ff;color:#07101c;border-radius:50%;width:60px;height:60px;line-height:60px;font-size:42px;font-weight:900}',
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
EV={'scenes':{sid:[st,du,'ovl' if sid in OVL else 'scn'] for sid,(st,du,_) in S.items()},'cam':CAM,'actions':ACTIONS}
json.dump(EV,open(os.path.join(ROOT,'events.json'),'w'),indent=2);json.dump({'captions':CAPS,'camera':CAM,'scenes':EV['scenes']},open(os.path.join(ROOT,'timing.json'),'w'),ensure_ascii=False,indent=2)
print(f'wrote {len(S)} scenes, {len(CAPS)} captions, {DUR}s')
