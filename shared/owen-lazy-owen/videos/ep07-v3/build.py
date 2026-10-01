#!/usr/bin/env python3
"""Owen episode 6. Source-timed semantic scenes; no stock episode text reused."""
import os,sys,json,re,html
ROOT=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(ROOT,'..','nick-plugins-mg'))
import build as lib
W,H=1080,1920
CUTS=json.load(open(os.path.join(ROOT,'cuts.json')));DUR=CUTS['duration'];SEGS=CUTS['segments']
TX=json.load(open(os.path.join(ROOT,'src/transcript.json')))['raw'];WORDS=[w for s in TX for w in s['words']]
def M(t):
 for s in SEGS:
  if t<s['src_start']:return s['out_start']
  if t<=s['src_end']:return round(s['out_start']+t-s['src_start'],3)
 return DUR
NAVY='linear-gradient(180deg,#07101c,#0d1b2e)'
lib.BASE += '''
#root{color:#f5f9ff}
.panel{position:absolute;left:64px;top:300px;width:952px;height:520px;border:2px solid #315776;border-radius:28px;background:#0b1728;overflow:hidden;box-shadow:0 25px 60px #0008}
.chrome{height:52px;background:#0c1726;border-bottom:1px solid #315776;display:flex;align-items:center;gap:9px;padding:0 22px;color:#bed2e9;font-size:20px;font-family:'JetBrains Mono'}
.chrome i{width:10px;height:10px;border-radius:100%;background:#64d2ff}.chrome em{font-style:normal;margin-left:15px}
.stage{position:absolute;left:0;right:0;top:52px;bottom:0;overflow:hidden}
.gridbg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 30%,#163450 0%,transparent 65%),repeating-linear-gradient(0deg,#64d2ff0b 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,#64d2ff0b 0 1px,transparent 1px 48px)}
.label{font-size:23px;letter-spacing:3px;color:#a9c4df;font-weight:700}.cyan{color:#64d2ff}.red{color:#ff3b30}.big{font-weight:900;font-size:62px;line-height:1.2}.small{font-size:27px;line-height:1.5;color:#d8e5f2}
.badge{display:inline-block;border:2px solid #64d2ff;border-radius:10px;padding:10px 22px;color:#64d2ff;font-weight:800;font-size:26px;background:#0b1c2d}.badge.warn{border-color:#ff3b30;color:#ff3b30}
.doc{position:absolute;left:0;top:0;transform-origin:0 0}.source{position:absolute;bottom:15px;right:18px;background:#07101cee;color:#eaf4ff;border:1px solid #38536f;padding:6px 12px;border-radius:7px;font-size:18px}
.example{position:absolute;right:22px;top:15px;font-size:19px;color:#aac1d7}
'''
S={};OVL=set();CAM_SRC=[]
# Explicit camera edit. No implicit fixed-card default.
LAYOUT={'s01-hook':'card','s02-four':'full','s03-supabase':'card','s04-database':'card','s05-table':'full','s06-vercel':'card','s07-deploy':'full','s08-logs':'card','s09-omc':'full','s10-team':'card','s11-roles':'full','s12-chrome':'card','s13-browser':'card','s14-eyes':'full','s15-contents':'card','s16-ebook':'card','s17-comment':'full'}
PRESENTER_ONLY={'s02-four','s05-table','s07-deploy','s09-omc','s11-roles','s17-comment'}

def panel(title,body):return '<div class="panel"><div class="chrome"><i></i><i></i><i></i><em>'+title+'</em></div><div class="stage">'+body+'</div></div>'
def scene(sid,a,b,body,css='',js='',mode='card'):
 mode=LAYOUT[sid]
 if sid in PRESENTER_ONLY: body,css,js='','',''
 st=M(a);du=round(M(b)-st,3)
 S[sid]=(st,du,lib.scene(sid,('' if mode=='full' else '<div class="gridbg"></div>')+body,css,js,NAVY if mode=='hide' else 'transparent'))
 if mode=='full':OVL.add(sid)
 CAM_SRC.append((a,mode,1.10 if mode=='full' else 1,0))
IN="tl.fromTo('.panel',{opacity:0,y:35,scale:.96},{opacity:1,y:0,scale:1,duration:.3,ease:'power3.out'},0);"
# First-frame hook and presenter; exact approved episode style, episode-specific copy.
scene('s01-hook',4.80,7.32,'<div class="hook"><div>이 플러그인 4개 깔기 전엔</div><strong>클로드 코드 시작하지 마세요</strong></div>','.hook{position:absolute;left:64px;top:395px;width:952px;text-align:center;font-size:74px;line-height:1.13;font-weight:900;letter-spacing:-3px}.hook strong{display:block;font-size:68px;background:#64d2ff;color:#07101c;padding:22px 8px;margin-top:25px;border-radius:17px}',"tl.fromTo('.hook strong',{scale:1},{scale:1.02,duration:2.3,ease:'none'},.05);")
# Four-slot reveal adapted from installed registry stagger-lattice (finite seek-safe stagger).
scene('s02-four',7.32,11.10,panel('CLAUDE CODE / AI 직원 4명','<div class="socket"><div class="slot"><b>01</b>데이터<small>Supabase</small></div><div class="slot"><b>02</b>배포<small>Vercel</small></div><div class="slot"><b>03</b>팀 작업<small>OMC</small></div><div class="slot"><b>04</b>브라우저<small>DevTools</small></div></div><div class="plugline">클로드 코드에 연결</div>'),'.socket{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;padding:70px 28px 0}.slot{background:#18334a;border:2px solid #4a7698;border-radius:20px;text-align:center;padding:25px 0;font-size:31px;font-weight:800}.slot b{display:block;color:#64d2ff;font-size:42px;margin-bottom:20px}.slot small{display:block;font-size:21px;color:#c9d9e6;margin-top:15px}.plugline{position:absolute;bottom:44px;left:0;right:0;text-align:center;color:#64d2ff;font-size:30px;font-weight:800}',IN+"tl.fromTo('.slot',{opacity:0,y:30,scale:.86},{opacity:1,y:0,scale:1,stagger:.22,duration:.35,ease:'back.out(1.4)'},.2);tl.fromTo('.plugline',{opacity:0},{opacity:1,duration:.3},1.3);")
# Crop official pages to the product name and descriptive copy; no dynamic count emphasis.
def official(sid,a,b,title,file,offset=-245):
 scene(sid,a,b,panel(title,f'<img class="doc" data-layout-allow-overflow src="assets/shots/{file}"><div class="source">공식 플러그인 소개</div>'),f'.doc{{width:1750px;left:-425px;top:{offset-100}px}}',IN+"tl.fromTo('.doc',{y:12},{y:-25,duration:1.8,ease:'none'},.2);")
official('s03-supabase',11.10,12.90,'01 / Supabase · 데이터 창고','supabase-plugin.png',-240)
scene('s04-database',12.90,16.32,panel('신청자 명단을 쌓는 창고','<div class="example">데이터 예시</div><div class="db"><div class="dbrow head"><span>이름</span><span>신청 강의</span><span>상태</span></div><div class="dbrow"><span>김○○</span><span>AI 입문</span><span>접수</span></div><div class="dbrow"><span>이○○</span><span>자동화</span><span>접수</span></div><div class="dbrow"><span>박○○</span><span>AI 입문</span><span>접수</span></div></div>'),'.db{position:absolute;left:35px;right:35px;top:62px}.dbrow{display:grid;grid-template-columns:1fr 1.4fr .7fr;font-size:30px;padding:20px 25px;background:#152c41;border-bottom:1px solid #34536d}.dbrow.head{color:#64d2ff;font-weight:800;background:#203e55}.dbrow:last-child{border-radius:0 0 16px 16px}',IN+"tl.fromTo('.dbrow:not(.head)',{opacity:0,y:24},{opacity:1,y:0,stagger:.35,duration:.3},.35);tl.to('.db',{y:-12,duration:1.4,ease:'none'},1.7);")
scene('s05-table',16.32,19.90,panel('클로드가 직접 표 만들고 정리','<div class="chat">신청자 명단 정리해줘</div><div class="tableflow"><div>표 만들기</div><i>→</i><div>데이터 정리</div></div><div class="done">Supabase 연결</div>'),'.chat{position:absolute;left:44px;top:45px;right:44px;background:#233e55;padding:25px;border-radius:16px;font-size:39px;font-weight:800}.tableflow{position:absolute;top:190px;left:45px;right:45px;display:flex;justify-content:space-between;align-items:center}.tableflow div{padding:30px;background:#153b49;border:2px solid #64d2ff;border-radius:15px;font-size:37px;font-weight:800}.tableflow i{font-style:normal;color:#64d2ff;font-size:55px}.done{position:absolute;left:0;right:0;bottom:30px;text-align:center;font-size:28px;color:#b7d0e3}',IN+"tl.fromTo('.chat',{opacity:0,y:20},{opacity:1,y:0,duration:.3},.1);tl.fromTo('.tableflow > *',{opacity:0,x:-25},{opacity:1,x:0,stagger:.35,duration:.3},.55);tl.fromTo('.done',{opacity:0},{opacity:1,duration:.3},1.9);")
official('s06-vercel',19.90,25.50,'02 / Vercel · 사이트 배포','vercel-plugin.png',-245)
scene('s07-deploy',25.50,27.14,panel('내 컴퓨터에서 인터넷으로','<div class="deploy"><div class="computer">만든 사이트<small>내 컴퓨터</small></div><span>→</span><div class="internet">인터넷<small>사이트 공개</small></div></div>'),'.deploy{display:flex;align-items:center;justify-content:space-between;padding:95px 45px}.deploy div{width:335px;text-align:center;border:3px solid #64d2ff;border-radius:18px;padding:30px 10px;font-size:40px;font-weight:900}.deploy small{display:block;font-size:27px;color:#c6d9e8;margin-top:22px}.deploy span{font-size:75px;color:#64d2ff}',IN+"tl.fromTo('.internet',{opacity:0,x:-35},{opacity:1,x:0,duration:.35},.4);")
scene('s08-logs',27.14,30.42,panel('배포하고 문제가 생기면 로그 확인','<div class="example">작업 흐름 예시</div><div class="logs"><div class="log">배포 요청 <b>전송</b></div><div class="log warn">문제 발생 <b>확인 필요</b></div><div class="log">배포 로그 <b>원인 확인</b></div></div>'),'.logs{padding:60px 35px}.log{padding:22px 25px;background:#183149;margin-bottom:14px;font-size:32px;border-radius:10px}.log b{float:right;color:#64d2ff}.log.warn b{color:#ff746b}',IN+"tl.fromTo('.log',{opacity:0,x:30},{opacity:1,x:0,stagger:.6,duration:.25},.25);")
scene('s09-omc',30.42,32.40,panel('03 / oh-my-claudecode','<img class="doc" src="assets/shots/omc-repo.png"><div class="repotitle">오 마이 클로드 코드</div><div class="source">공식 GitHub 저장소</div>'),'.doc{width:1100px;top:-70px;left:-15px}.repotitle{position:absolute;left:35px;right:35px;top:210px;background:#07101cf2;border:2px solid #64d2ff;border-radius:16px;padding:26px;font-size:47px;font-weight:900;color:#64d2ff;text-align:center}',IN+"tl.to('.doc',{y:-35,duration:1.5,ease:'none'},.2);tl.fromTo('.repotitle',{opacity:0,scale:.93},{opacity:1,scale:1,duration:.25},.3);")
scene('s10-team',32.40,35.22,panel('필요한 역할을 팀으로 호출','<div class="team"><div class="task">할 일</div><svg viewBox="0 0 860 110"><path d="M430 0V55H120V110M430 55V110M430 55H740V110"/></svg><div class="people"><div>기획</div><div>제작</div><div>확인</div></div></div>'),'.team{position:absolute;left:45px;right:45px;top:35px}.task{margin:auto;width:235px;border-radius:15px;padding:18px;text-align:center;background:#64d2ff;color:#07101c;font-size:36px;font-weight:900}.team svg{display:block;width:100%;height:100px}.team path{fill:none;stroke:#64d2ff;stroke-width:4;stroke-dasharray:1400;stroke-dashoffset:1400}.people{display:flex;justify-content:space-between}.people div{width:235px;text-align:center;border:2px solid #5084a8;padding:27px;background:#18364e;border-radius:15px;font-size:38px;font-weight:900}',IN+"tl.to('.team path',{strokeDashoffset:0,duration:.7},.2);tl.fromTo('.people div',{opacity:0,y:20},{opacity:1,y:0,stagger:.23,duration:.3},.6);")
scene('s11-roles',35.22,47.30,'<div class="roleboard"><div class="label">혼자 다 하지 않고</div><div class="big">역할을 나눠서</div><div class="role r1"><b>01</b><span>기획하는 쪽</span></div><div class="role r2"><b>02</b><span>만드는 쪽</span></div><div class="role r3"><b>03</b><span>확인하는 쪽</span></div></div>','.roleboard{position:absolute;left:95px;right:95px;top:350px}.roleboard>.label{text-align:center}.roleboard>.big{text-align:center;font-size:86px;margin:35px 0 55px}.role{display:flex;gap:40px;align-items:center;border:2px solid #47718e;background:#142c43;padding:36px;margin-top:24px;border-radius:22px;font-size:48px;font-weight:900}.role b{color:#64d2ff;font-size:64px}',"tl.fromTo('.role',{opacity:0,x:-45},{opacity:1,x:0,stagger:.5,duration:.32},0);",'hide')
official('s12-chrome',47.30,51.00,'04 / Chrome DevTools MCP','cdt-plugin.png',-245)
scene('s13-browser',51.00,55.30,panel('브라우저 화면과 에러를 직접 확인','<div class="example">점검 화면 예시</div><div class="browser"><div class="page"><strong>내 사이트</strong><div class="input">신청 정보</div><div class="btn">신청하기</div></div><div class="console"><b>CONSOLE</b><div class="error">! 오류 확인</div><div class="network">요청 기록 확인</div><div class="inspect">화면 직접 확인</div></div></div>'),'.browser{display:flex;gap:22px;position:absolute;left:30px;right:30px;top:65px;bottom:30px}.page{width:50%;border:2px solid #395e7b;border-radius:15px;padding:28px;background:#142d43}.page strong{font-size:40px}.input{margin-top:35px;padding:16px;font-size:27px;background:#274359;border-radius:8px}.btn{margin-top:20px;padding:16px;background:#64d2ff;color:#07101c;text-align:center;font-size:28px;font-weight:900;border-radius:8px}.console{flex:1;padding:22px 16px;background:#06101a;border-radius:15px;font-size:27px}.console b{color:#b9cddd;font-family:"JetBrains Mono";font-size:24px}.console div{padding:24px 0;border-bottom:1px solid #25415a}.error{color:#ff746b}.inspect{color:#64d2ff}',IN+"tl.fromTo('.console div',{opacity:0,x:25},{opacity:1,x:0,stagger:.65,duration:.3},.35);tl.to('.btn',{boxShadow:'0 0 0 5px #64d2ff66',duration:.3,yoyo:true,repeat:3},1.6);")
scene('s14-eyes',55.30,58.84,'<div class="eyes"><div class="old">눈 감고 고치기</div><div class="new">눈 뜨고 고치기</div></div>','.eyes{position:absolute;left:64px;top:1050px;width:836px;text-align:center;font-weight:900}.old{font-size:45px;color:#d0dae3;text-decoration:line-through}.new{font-size:67px;color:#64d2ff;margin-top:23px;text-shadow:0 2px 12px #000}',"tl.fromTo('.old',{opacity:0,y:-20},{opacity:1,y:0,duration:.25},0);tl.fromTo('.new',{opacity:0,scale:.85},{opacity:1,scale:1,duration:.3,ease:'back.out(1.5)'},1.2);",'full')
scene('s15-contents',58.84,61.92,panel('전자책으로 정리하고 있어요','<div class="chapters"><div><b>01</b>AI 활용법</div><div><b>02</b>최신 정보</div><div><b>03</b>수익화 방법</div></div>'),'.chapters{padding:35px 42px}.chapters div{padding:23px 25px;background:#163149;border-radius:12px;margin-bottom:17px;font-size:38px;font-weight:800}.chapters b{color:#64d2ff;margin-right:40px;font-family:"JetBrains Mono"}',IN+"tl.fromTo('.chapters div',{opacity:0,x:-35},{opacity:1,x:0,stagger:.45,duration:.3},.15);")
scene('s16-ebook',61.92,64.94,panel('AI 활용부터 수익화까지','<div class="book"><span>집필 중</span><strong>AI 활용법<br>전자책</strong><small>최신 정보 · 수익화 방법</small></div><div class="booknote">한 권으로<br>정리 중</div>'),'.book{position:absolute;left:80px;top:28px;width:355px;height:380px;background:#17394e;border:3px solid #64d2ff;border-left:16px solid #64d2ff;border-radius:5px 17px 17px 5px;padding:27px;box-shadow:16px 12px 0 #06101b}.book span{font-size:22px;color:#b7d4e8}.book strong{display:block;margin-top:37px;font-size:54px;line-height:1.2;color:#64d2ff}.book small{display:block;margin-top:40px;font-size:21px}.booknote{position:absolute;left:520px;top:120px;font-size:59px;line-height:1.3;font-weight:900}',IN+"tl.fromTo('.book',{opacity:0,x:-40,rotation:-6},{opacity:1,x:0,rotation:-2,duration:.35},.2);tl.fromTo('.booknote',{opacity:0,y:20},{opacity:1,y:0,duration:.3},.6);")
scene('s17-comment',64.94,67.10,panel('자료가 궁금하면 댓글에','<div class="comment"><div class="label">댓글 키워드</div><div class="field"><span>전자책</span><b>↑</b></div><div class="small">AI 활용법 · 최신 정보 · 수익화 방법</div></div>'),'.comment{padding:62px 50px}.field{margin-top:28px;border:3px solid #64d2ff;border-radius:18px;padding:20px 30px;font-size:58px;font-weight:900;color:#64d2ff;background:#132c42}.field b{float:right;color:#07101c;background:#64d2ff;border-radius:50%;font-size:42px;width:55px;height:55px;text-align:center;line-height:53px}.comment .small{margin-top:25px;font-size:28px}',IN+"tl.fromTo('.field span',{opacity:0},{opacity:1,duration:.15},.3);tl.fromTo('.field b',{scale:.7},{scale:1,duration:.3,ease:'back.out(2)'},.8);")
# Face position measured from source frame (1920x1080); same framing as approved series.
CAM=[]
for i,(t,m,z,_) in enumerate(CAM_SRC):
    tw=.3 if i and CAM_SRC[i-1][1]!=m else 0
    CAM.append((0.0 if i==0 else M(t),m,z,tw))
FACE=(1000,340)
C_SRC=[(4.8, '오늘도 AI 직원을', 'AI 직원'), (6.48, '뽑았습니다', ''), (7.32, '클로드 코드로', '클로드 코드'), (8.14, '사이트 만들 때', '사이트'), (9.18, '붙일 4가지입니다', '4가지'), (11.1, '첫 번째 수파베이스', '수파베이스'), (12.9, '신청자 명단 같은', '신청자 명단'), (14.34, '데이터를 쌓는 창고거든요', '창고'), (16.32, '클로드가 직접 들어가서', '직접'), (17.98, '표 만들고 정리합니다', '표'), (19.9, '두 번째 버셀', '버셀'), (24.3, '만든 사이트를', '사이트'), (25.5, '인터넷에 올려주는 곳이에요', '인터넷'), (27.14, '클로드가 배포하고', '배포'), (28.14, '문제가 생기면', '문제'), (29.0, '로그까지 확인합니다', '로그'), (30.42, '세 번째', ''), (30.88, '오 마이 클로드 코드', '오 마이 클로드 코드'), (32.4, '필요한 역할을', '역할'), (33.3, '팀으로 불러서', '팀으로'), (34.12, '나눠서 일합니다', '나눠서'), (35.22, '기획하는 쪽', '기획'), (35.86, '만드는 쪽', '만드는'), (36.7, '확인한 쪽', '확인'), (37.4, '나누는 거죠', ''), (47.3, '네 번째', ''), (48.96, '크롬 데브툴즈 MCP', '크롬 데브툴즈 MCP'), (51.0, '클로드가 진짜 브라우저를', '브라우저'), (52.68, '열어서 에러랑', '에러'), (53.78, '화면을 직접 봐요', '직접'), (55.3, '눈 감고 고치는 걸', '눈 감고'), (56.78, '눈 뜨고 고치게 되는 거죠', '눈 뜨고'), (58.84, '이런 AI 활용법부터', 'AI 활용법'), (60.22, '최신 정보', '최신 정보'), (60.94, '수익화 방법까지', '수익화'), (61.92, '전자책으로', '전자책'), (62.92, '정리하고 있으니까', ''), (63.94, '궁금한 분들은', ''), (64.94, '댓글에 전자책', '전자책'), (66.3, '남겨주세요', '')]
WARN=['문제','에러','눈 감고']

def geo(mode):
    if mode == "card":   # person card 1000x1040 at (40,880)
        box = dict(left=40, top=880, width=1000, height=1040, borderRadius="80px 80px 0 0")
        s = 1040 / 1080; img = dict(width=1920 * s, height=1040, left=500 - FACE[0] * s, top=0)
        org = (500, FACE[1] * s)
    else:
        box = dict(left=0, top=0, width=1080, height=1920, borderRadius="0px")
        s = 1920 / 1080; img = dict(width=1920 * s, height=1920, left=540 - FACE[0] * s, top=-40)
        org = (540, FACE[1] * s - 40)
    return box, img, org
cam_js = []
fmt = lambda d: "{" + ",".join(f"{k}:{json.dumps(round(v,1) if isinstance(v,float) else v)}" for k, v in d.items()) + "}"
for t, mode, z, tw in CAM:
    if mode == "hide":
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:0}},{t});"); continue
    box, img, org = geo(mode)
    zo = f"{{scale:{z},transformOrigin:'{org[0]:.0f}px {org[1]:.0f}px'}}"
    if tw:
        cam_js.append(f"tl.to('#camBox',{{...{fmt(box)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camImg',{{...{fmt(img)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camZoom',{{...{zo},duration:{tw},ease:'power2.inOut'}},{t});")
    else:
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:1,...{fmt(box)}}},{t});tl.set('#camImg',{fmt(img)},{t});tl.set('#camZoom',{zo},{t});")
for i, (t, mode, z, tw) in enumerate(CAM):
    if mode == "hide": continue
    nxt = CAM[i + 1][0] if i + 1 < len(CAM) else DUR
    if nxt - t > .8 and not (i + 1 < len(CAM) and CAM[i + 1][3]):
        cam_js.append(f"tl.to('#camZoom',{{scale:{z*1.035:.3f},duration:{nxt-t-max(tw,0)-.05:.2f},ease:'none'}},{t+max(tw,0)+.01:.2f});")


def mode_at(t):
    m = CAM[0][1]
    for tt, mm, *_ in CAM:
        if tt <= t + 1e-6: m = mm
    return m
CAPS = []
for i, (s, txt, acc) in enumerate(C_SRC):
    nxt = C_SRC[i + 1][0] if i + 1 < len(C_SRC) else 1e9
    last_end = max([w["end"] for w in WORDS if s - .01 <= w["start"] < nxt] or [s + .5])
    a = 0.0 if i == 0 else M(s)
    e = min(M(nxt) if nxt < 1e8 else DUR, M(last_end) + .35)
    if i + 1 < len(C_SRC) and M(nxt) - e < .25: e = M(nxt)
    m = mode_at(a)
    CAPS.append([a, round(e, 3), txt, m, acc])


scene_divs = "".join(f'<div id="{sid}" class="{"ovl" if sid in OVL else "scn"}" data-composition-id="{sid}" data-composition-src="scenes/{sid}.html" data-start="{st}" data-duration="{du}" data-track-index="{2 if sid in OVL else 0}" data-width="{W}" data-height="{H}"></div>\n' for sid, (st, du, _) in S.items())

initial_box, initial_img, initial_org = geo(CAM[0][1])
def css_geometry(values):
    return ';'.join(re.sub(r'([A-Z])',lambda m:'-'+m[1].lower(),k)+':'+(str(v)+'px' if isinstance(v,(int,float)) else v) for k,v in values.items())
HTML = f"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width={W},height={H}">
<title>클로드 코드 플러그인 4개 — Owen 스타일</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
{lib.FONTS}
body{{margin:0;background:#000;font-family:'Pretendard',sans-serif}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;background:#07101c}}
#root *{{box-sizing:border-box}}
.scn{{position:absolute;inset:0;z-index:1}} .ovl{{position:absolute;inset:0;z-index:3}}
#camBox{{position:absolute;overflow:hidden;z-index:2;background:#111;opacity:1;visibility:visible;{css_geometry(initial_box)}}}
#camZoom{{position:absolute;inset:0}}
#camImg{{position:absolute;{css_geometry(initial_img)}}}
#person{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#captions{{position:absolute;inset:0;z-index:4;pointer-events:none}}
.caption{{position:absolute;text-align:center;white-space:nowrap}}
.caption.card{{left:64px;width:952px}}
.caption.full{{left:64px;width:836px}}  /* y>=1000 → x<=900 (IG safe zone) */
.caption span{{display:inline-block;font-family:'Pretendard';font-weight:800;font-size:60px;line-height:1.05;color:#fff;letter-spacing:-1px;white-space:nowrap;text-shadow:0 2px 8px #000,0 0 3px #000,0 0 3px #000}}
.caption b{{font-weight:inherit;color:#64d2ff}}
.caption b.warn{{color:#ff3b30}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{scene_divs}
<div id="camBox"><div id="camZoom" data-layout-allow-overflow><div id="camImg" data-layout-allow-overflow><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1" muted></video></div></div></div>
<div id="captions"></div>
<audio id="voice" src="assets/mix.m4a" data-start="0" data-duration="{DUR}" data-track-index="9"></audio>
</div>
<script>
const WARN={json.dumps(WARN, ensure_ascii=False)};
const CAPS={json.dumps(CAPS, ensure_ascii=False)};
const CAMERA={json.dumps(CAM)};
const host=document.getElementById('captions');
const strip=(t)=>t.replace(/[.,?!"'…“”‘’]/g,'');
const esc=(t)=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;');
CAPS.forEach((c,i)=>{{const [s,e,text,mode,acc]=c;const d=document.createElement('div');d.id='cap-'+i;
 const m=(mode==='card')?'card':'full';d.className='clip caption '+m;
 d.dataset.start=s;d.dataset.duration=(e-s).toFixed(3);d.dataset.trackIndex=8;d.style.top=(m==='card'?840:1345)+'px';
 let h=esc(strip(text));const a=strip(acc||'');if(a)h=h.replace(esc(a),'<b'+(WARN.includes(a)?' class="warn"':'')+'>'+esc(a)+'</b>');
 d.innerHTML='<span>'+h+'</span>';host.appendChild(d);}});
function fit(){{CAPS.forEach((c,i)=>{{const d=document.getElementById('cap-'+i);const sp=d.firstChild;const max=(c[3]==='card')?930:836;sp.style.fontSize='60px';if(sp.scrollWidth>max)sp.style.fontSize=Math.floor(60*max/sp.scrollWidth)+'px'}})}}
fit();if(document.fonts)document.fonts.ready.then(fit);
const tl=gsap.timeline({{paused:true}});
CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');if(i===0)tl.set(el,{{opacity:1,scale:1}},0);else tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);tl.set(el,{{opacity:0}},c[1]);}});
CAPS.forEach((c,i)=>{{const j=CAMERA.findIndex(k=>Math.abs(k[0]-c[0])<.001&&k[3]>0);if(j>0){{const oldY=CAMERA[j-1][1]==='card'?840:1345;const newY=CAMERA[j][1]==='card'?840:1345;const textNode=document.getElementById('cap-'+i).firstChild;tl.set(textNode,{{y:1345-newY}},c[0]);tl.set(textNode,{{y:0}},c[0]+CAMERA[j][3]);}}}});
{chr(10).join(cam_js)}
window.__timelines["main"]=tl;
</script></body></html>
"""
os.makedirs(os.path.join(ROOT, "scenes"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "scenes")):
    if os.path.isfile(os.path.join(ROOT, "scenes", f)): os.remove(os.path.join(ROOT, "scenes", f))
for sid, (st, du, html) in S.items():
    open(os.path.join(ROOT, "scenes", sid + ".html"), "w").write(html)
open(os.path.join(ROOT, "index.html"), "w").write(HTML)

EV={'scenes':{sid:[st,du,'ovl' if sid in OVL else 'scn'] for sid,(st,du,_) in S.items()},'cam':CAM,'ticks':[M(t) for t in [11.56,14.34,17.98,20.69,27.14,29,30.88,33.30,35.22,35.86,36.70,48.96,53.06,56.78,60.22,60.94,65.62]]}
json.dump(EV,open(os.path.join(ROOT,'events.json'),'w'),indent=2)
json.dump({'captions':CAPS,'camera':CAM,'scenes':EV['scenes']},open(os.path.join(ROOT,'timing.json'),'w'),ensure_ascii=False,indent=2)
print(f'wrote {len(S)} scenes, {len(CAPS)} captions, {DUR}s')
