#!/usr/bin/env python3
"""EP06 rebuilt from the original Owen source mechanisms, not the v3 panel template.
All editorial times are SOURCE seconds. Named actions drive both visuals and SFX.
Original speech, source cuts and approved hook remain unchanged.
"""
import os,sys,json,re,html
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'nick-plugins-mg'))
import build as lib
W,H=1080,1920
CUTS=json.loads((ROOT/'cuts.json').read_text());DUR=CUTS['duration'];SEGS=CUTS['segments']
WORDS=[w for s in json.loads((ROOT/'src/transcript.json').read_text())['raw'] for w in s['words']]
def M(t):
    for s in SEGS:
        if t<s['src_start']:return s['out_start']
        if t<=s['src_end']:return round(s['out_start']+t-s['src_start'],3)
    return DUR
NAVY='linear-gradient(180deg,#07101c,#0d1b2e)'
lib.FONTS+="@font-face{font-family:'Nanum Myeongjo';src:url('assets/fonts/NanumMyeongjo-Bold.ttf');font-weight:700}"
lib.BASE='''
#root{position:absolute;inset:0;overflow:hidden;font-family:'Pretendard';color:#eef4ff;-webkit-font-smoothing:antialiased}#root *{box-sizing:border-box}.abs{position:absolute}
.gridbg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 35%,#16345088,transparent 65%),repeating-linear-gradient(0deg,#64d2ff08 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,#64d2ff08 0 1px,transparent 1px 48px)}
.cyan{color:#64d2ff}.red{color:#ff635e}.mono{font-family:'JetBrains Mono'}
.window{position:absolute;left:64px;top:300px;width:952px;height:520px;border:1px solid #385371;border-radius:24px;background:#0d1726;overflow:hidden;box-shadow:0 25px 65px #0008,0 0 35px #64d2ff0c}
.bar{height:48px;display:flex;align-items:center;gap:8px;background:#101b2c;padding:0 18px;border-bottom:1px solid #293f58}.bar i{display:block;width:10px;height:10px;border-radius:50%;background:#53657f}.bar i:first-child{background:#fe7771}.bar i:nth-child(2){background:#e7b454}.bar i:nth-child(3){background:#65bda6}.bar span{font-family:'JetBrains Mono';font-size:18px;color:#a0b5cd;margin-left:12px}
.vp{position:absolute;left:0;top:48px;width:950px;height:470px;overflow:hidden}.pan{position:absolute;left:0;top:0;transform-origin:0 0}.pan img{position:absolute;left:0;top:0}.source{position:absolute;right:18px;bottom:14px;padding:5px 10px;font-size:18px;color:#d1e1ef;background:#091424ed;border-radius:5px}.example{font-size:24px;color:#91a8bd;position:absolute;left:80px;top:1235px}.outline{fill:#64d2ff;fill-opacity:0;stroke:#64d2ff;stroke-width:7;stroke-dasharray:1;stroke-dashoffset:1}.outline.red{fill:#ff635e;stroke:#ff635e}
'''
S={};OVL=set();ACTIONS=[];CAM_SRC=[];SCENE_META={}
def bar(label):return '<div class="bar"><i></i><i></i><i></i><span>'+label+'</span></div>'
def add(sid,a,b,body,css='',js='',mode='card',cues=None):
    st=M(a);end=M(b);du=round(end-st,3)
    for name,(src,sound,gain) in (cues or {}).items():
        at=M(src);local=round(at-st,3)
        assert 0<=local<du,(sid,name,local,du)
        assert '@'+name in js,(sid,name,'unused cue')
        js=js.replace('@'+name,str(local))
        ACTIONS.append(dict(name=name,scene=sid,source=src,time=at,local=local,sound=sound,gain_db=gain))
    assert not re.search(r'@[A-Za-z]',js),(sid,'unresolved event')
    S[sid]=(st,du,lib.scene(sid,('' if mode=='full' else '<div class="gridbg"></div>')+body,css,js,NAVY if mode=='hide' else 'transparent'))
    if mode=='full':OVL.add(sid)
    SCENE_META[sid]={'source':[a,b],'mode':mode}
    CAM_SRC.append((a,mode,1.04 if mode=='full' else 1,0))
ENTER="tl.fromTo('.window',{opacity:0,y:-35},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);"
def presenter(sid,a,b):add(sid,a,b,'',mode='full')
def shot(sid,a,b,asset,url,keys,boxes,extra='',extra_css='',extra_js='',cues=None):
    """Adapted ep03 shot_card: image-coordinate poses/boxes, now keyed in source seconds."""
    iw,ih=Image.open(ROOT/'assets/shots'/asset).size
    def pose(cx,cy,z):return f'x:{475-cx*z:.3f},y:{235-cy*z:.3f},scale:{z}'
    js=[ENTER]
    for i,(src,cx,cy,z,d) in enumerate(keys):
        t=round(M(src)-M(a),3)
        js.append(f"tl.{'set' if i==0 else 'to'}('.pan',{{{pose(cx,cy,z)}"+('' if i==0 else f",duration:{d},ease:'{'none' if d>1.2 else 'power2.inOut'}'")+f'}},{t});')
    rects=[]
    for i,(name,x,y,w,h,red) in enumerate(boxes):
        rects.append(f'<rect class="outline b{i} {"red" if red else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" pathLength="1"/>')
        js.append(f"tl.fromTo('.b{i}',{{strokeDashoffset:1,fillOpacity:0}},{{strokeDashoffset:0,fillOpacity:.08,duration:.35,ease:'power2.inOut'}},@{name});")
    body=f'<div class="window">{bar(url)}<div class="vp"><div class="pan" style="width:{iw}px;height:{ih}px"><img src="assets/shots/{asset}" width="{iw}" height="{ih}"><svg style="position:absolute;inset:0" width="{iw}" height="{ih}" viewBox="0 0 {iw} {ih}">{"".join(rects)}</svg></div></div><div class="source">실제 공식 문서</div>{extra}</div>'
    add(sid,a,b,body,extra_css,'\n'.join(js)+extra_js,'card',cues)

# Approved opening is byte-for-byte preserved from v3; only subsequent scene grammar changes.
add('s01-hook',4.57,6.76,'''<div class="hook"><div class="hook-question">해커도 못 뚫는다고?</div><div class="hook-answer">구글이 만든 AI 스킬</div><div class="hook-line"></div></div>''','''.hook{position:absolute;left:64px;top:395px;width:952px;text-align:center;font-weight:900;letter-spacing:-3px;line-height:1.22}.hook-question{font-size:88px;color:#fff;white-space:nowrap}.hook-answer{font-size:82px;white-space:nowrap;color:#07101c;background:#64d2ff;border-radius:17px;margin-top:32px;padding:22px 10px;box-shadow:0 15px 50px #64d2ff20}.hook-line{height:5px;width:120px;margin:42px auto 0;background:#64d2ff;border-radius:5px}''',"tl.fromTo('.hook-line',{scaleX:1},{scaleX:2.8,duration:1.8,ease:'power2.out'},.1);")
# Semantic badge, not a second transcription of the sentence. Physical stamp/settle from ep03.
add('s02-security',6.76,8.32,'<div class="idcard"><div class="lanyard"></div><div class="pic"><svg viewBox="0 0 100 100"><path d="M50 8L87 23V49Q85 76 50 94Q15 76 13 49V23Z"/><path class="check" d="M29 49L44 64L73 35"/></svg></div><div class="idtext"><small>AI EMPLOYEE / 06</small><strong>Security</strong><span>MANTIS</span></div><div class="stamp">HIRED</div></div>',
'''.idcard{position:absolute;left:95px;top:1040px;width:760px;height:215px;background:#f0f3ef;color:#102437;border-radius:22px;display:flex;padding:27px 30px;gap:28px;box-shadow:0 18px 45px #0006;transform-origin:50% 0}.lanyard{position:absolute;left:340px;top:-12px;width:85px;height:15px;border-radius:8px;background:#244c60}.pic{width:135px;height:155px;background:#d7e6e8;border-radius:12px;padding:20px}.pic svg{width:95px;height:110px}.pic path{fill:none;stroke:#206275;stroke-width:6}.pic .check{stroke-dasharray:90;stroke-dashoffset:90}.idtext small{font-family:'JetBrains Mono';font-size:20px;color:#3e5661}.idtext strong{font-family:'Instrument Serif';font-size:69px;font-weight:400;display:block;line-height:1.1}.idtext span{font-family:'Silkscreen';color:#2d7389;font-size:27px}.stamp{position:absolute;right:30px;bottom:20px;color:#296e65;border:3px solid #296e65;font-family:'JetBrains Mono';font-size:25px;padding:5px 12px;transform:rotate(-12deg)}''',
"tl.fromTo('.idcard',{y:60,rotation:-8,opacity:0},{y:0,rotation:2,opacity:1,duration:.32,ease:'back.out(1.5)'},0);tl.to('.check',{strokeDashoffset:0,duration:.32},.15);tl.fromTo('.stamp',{scale:2,opacity:0},{scale:1,opacity:1,duration:.2,ease:'power3.in'},@hire);tl.to('.idcard',{rotation:-1,duration:.6,ease:'sine.inOut'},.65);",'full',{'hire':(7.23,'soft-pop',-9)})
shot('s03-google',8.32,10.38,'google-blog.png','cloud.google.com / Mantis',[(8.32,540,580,.87,0),(8.75,540,270,.92,.45),(9.42,540,260,.94,1.2)],[('mantis_name',40,75,1000,230,False)],cues={'mantis_name':(9.08,'ui-tick',-10)})

# Synthetic shop is a labeled example; IDs are illustrative, never live customer records.
def shop_body(fixed=False):
    rows=''.join(f'<div class="shoprow r{i}"><span>#{1024+i}</span><span>{"내 주문" if i==0 else "다른 계정"}</span><span>온라인 클래스</span><b>{"확인" if i==0 else "주문 완료"}</b></div>' for i in range(4))
    return f'''<div class="store"><div class="storetop"><b>MY SHOP</b><span>주문 내역</span><i>내 계정</i></div><div class="urlpath">shop.example/order/<span class="digits"><b class="old">1024</b><b class="new">1025</b></span></div><div class="tablehead"><span>주문번호</span><span>주문자</span><span>상품</span><span>상태</span></div><div class="rows">{rows}</div><div class="focusbox"></div><div class="detail"><small>ORDER DETAILS</small><h3>온라인 클래스</h3><div class="detail-row">주문번호 <b>#1025</b></div><div class="detail-row">주문자 <b>다른 계정</b></div><div class="detail-row">신청 상태 <b>완료</b></div><div class="alertmark">!</div></div><div class="denied"><svg viewBox="0 0 100 100"><rect x="19" y="45" width="62" height="48" rx="9"/><path d="M32 45V28a18 18 0 0 1 36 0v17"/></svg><h3>접근할 수 없습니다</h3><p>이 주문서를 볼 권한이 없습니다</p><div>주문 목록으로 돌아가기</div></div><div class="pointer" data-layout-allow-overlap>↖</div></div>'''
SHOP_CSS='''
.store{position:absolute;left:70px;top:340px;width:900px;height:825px;background:#f4f6f8;color:#1c2a3b;border-radius:23px;overflow:hidden;box-shadow:0 35px 70px #0008;transform-origin:50% 45%}.storetop{display:flex;align-items:center;height:85px;padding:0 32px;gap:38px;background:white;border-bottom:1px solid #d5dce4}.storetop b{font-family:'JetBrains Mono';font-size:27px;letter-spacing:-1px}.storetop span{font-size:26px;color:#5f7183}.storetop i{margin-left:auto;font-style:normal;font-size:21px;background:#e0edf3;padding:9px 16px;border-radius:30px}.urlpath{height:85px;padding:27px 32px;font-size:27px;font-family:'JetBrains Mono';background:#e7edf3;border-bottom:1px solid #d0dbe7}.digits{position:relative;display:inline-block;width:78px;height:33px;vertical-align:middle}.digits b{position:absolute;top:0;left:0}.digits .new{color:#c73536}.tablehead,.shoprow{display:grid;grid-template-columns:1fr 1fr 1.5fr 1fr;align-items:center;padding:0 24px;gap:12px}.tablehead{height:63px;font-size:22px;color:#506176}.shoprow{height:91px;border-top:1px solid #d5dfe7;background:#fff;font-size:24px}.shoprow b{font-size:20px;font-weight:600;color:#44768d}.focusbox{position:absolute;left:13px;top:324px;width:874px;height:91px;border:4px solid #e15a5b;border-radius:6px}.detail{position:absolute;left:62px;right:62px;top:210px;background:#fff;border:1px solid #c9d7e1;border-radius:18px;padding:35px;box-shadow:0 25px 80px #14283c50}.detail small{font-family:'JetBrains Mono';font-size:22px;color:#596d80}.detail h3{font-size:44px;margin:21px 0 30px}.detail-row{display:flex;justify-content:space-between;padding:19px 0;border-top:1px solid #d8e0e9;font-size:27px;color:#617383}.detail-row b{color:#192d41}.alertmark{position:absolute;right:25px;top:23px;width:62px;height:62px;border-radius:50%;background:#ed635c;color:white;font-size:48px;text-align:center;font-weight:900;line-height:62px}.pointer{position:absolute;left:575px;top:345px;font-size:60px;color:#0e2334;text-shadow:2px 2px white}.denied{position:absolute;inset:170px 0 0;background:#f4f6f8;text-align:center;padding-top:65px}.denied svg{width:120px;height:120px;fill:none;stroke:#357b90;stroke-width:7}.denied h3{font-size:44px;margin:25px 0 18px}.denied p{font-size:26px;color:#637689}.denied div{margin:32px auto;width:390px;background:#143d54;color:white;border-radius:11px;padding:20px;font-size:25px}
'''
# White browser UI contains useful controls and state, not another dark explanation card.
add('s04-shop',10.38,13.56,'<div class="window light">'+bar('my-shop / 신청 페이지')+'<div class="shopform"><div class="product"><div class="cover"><small>ONLINE</small><strong>Class</strong><span>신청서 예시</span></div><div><h3>온라인 클래스</h3><p>수강 신청</p><div class="input">이름 <b>○○○</b></div><div class="input">연락처 <b>입력 완료</b></div><div class="submit"><span>신청하기</span><b>✓ 신청 완료</b></div></div></div><div class="mouse">↖</div><div class="tiny">화면 예시</div></div></div>',
'''.light{background:#f4f6f8}.shopform{position:absolute;top:48px;left:0;right:0;bottom:0;color:#18334b;padding:27px 30px}.product{display:grid;grid-template-columns:270px 1fr;gap:30px}.cover{height:342px;border-radius:12px;background:linear-gradient(145deg,#183e51,#5b9ca6);padding:35px 24px;color:white;box-shadow:8px 10px 0 #cad8df}.cover small{font-family:'JetBrains Mono';font-size:20px}.cover strong{font-family:'Instrument Serif';font-size:77px;display:block;font-weight:400;margin-top:38px}.cover span{font-size:22px;display:block;margin-top:40px}.product h3{font-size:35px;margin:0 0 8px}.product p{font-size:23px;color:#738797;margin:0 0 18px}.input{padding:15px;border:1px solid #c5d3dc;border-radius:8px;background:white;font-size:24px;margin-top:12px}.input b{float:right;font-weight:500;color:#586f7e}.submit{height:62px;background:#153e54;color:white;margin-top:18px;border-radius:8px;position:relative;text-align:center;font-size:26px}.submit span,.submit b{position:absolute;inset:15px 0}.mouse{position:absolute;right:63px;bottom:24px;font-size:58px;color:#142638;text-shadow:2px 2px white}.tiny{position:absolute;right:15px;bottom:8px;font-size:18px;color:#596f80}''',
ENTER+"tl.fromTo('.cover',{rotation:-5,scale:.9,opacity:0},{rotation:0,scale:1,opacity:1,duration:.35,ease:'back.out(1.4)'},.1);tl.fromTo('.input',{opacity:0,x:20},{opacity:1,x:0,stagger:.12,duration:.25},.25);tl.set('.submit b',{opacity:0},0);tl.to('.mouse',{x:-160,y:-52,duration:.32,ease:'power2.inOut'},@submit);tl.to('.submit span',{opacity:0,duration:.12},@submit);tl.to('.submit b',{opacity:1,duration:.12},@submit);",cues={'submit':(11.86,'ui-tick',-9)})
presenter('s05-works',13.56,14.64)
add('s06-leak',14.64,18.62,shop_body()+'<div class="example">취약점 설명용 예시 · 실제 고객 정보 아님</div>',SHOP_CSS,
"tl.set('.new,.focusbox,.detail,.denied',{opacity:0},0);tl.fromTo('.store',{y:50,scale:.94,opacity:0},{y:0,scale:1,opacity:1,duration:.3,ease:'power3.out'},0);tl.fromTo('.shoprow',{opacity:0,x:25},{opacity:1,x:0,stagger:.055,duration:.18},.1);tl.to('.pointer',{x:-240,y:-228,duration:.3,ease:'power2.inOut'},.15);tl.to('.old',{y:-25,opacity:0,duration:.15},@order_digit);tl.fromTo('.new',{y:25,opacity:0},{y:0,opacity:1,duration:.15},@order_digit);tl.to('.focusbox',{opacity:1,duration:.16},@order_digit);tl.to('.rows,.tablehead',{opacity:0,duration:.12},@leak_open);tl.to('.pointer',{opacity:0,duration:.08},@order_digit+.2);tl.fromTo('.detail',{opacity:0,y:60,scale:.9},{opacity:1,y:0,scale:1,duration:.3,ease:'back.out(1.6)'},@leak_open);tl.fromTo('.alertmark',{scale:2,opacity:0},{scale:1,opacity:1,duration:.2,ease:'power3.in'},@leak_alarm);tl.to('.detail',{x:6,duration:.045,repeat:3,yoyo:true},@leak_alarm);tl.to('.store',{scale:1.035,duration:1.0,ease:'none'},@leak_alarm);",'hide',{'order_digit':(14.90,'ui-tick',-8),'leak_open':(15.86,'ui-panel-appear',-9),'leak_alarm':(17.06,'soft-pop',-8)})
presenter('s07-mantis',18.62,19.46)
shot('s08-team',19.46,21.56,'repo-desktop.png','github.com/google/mantis',[(19.46,540,390,.88,0),(19.70,275,450,1.30,.45),(20.50,275,680,1.30,.6)],[('role_files',27,183,650,460,False)],cues={'role_files':(19.92,'ui-tick',-10)})

# Code map: individual files and a request moving through the actual depicted path.
files=[('index.html',90,355),('orders.ts',365,470),('auth.ts',650,355),('database',650,745),('order.test',110,745)]
nodes=''.join(f'<div class="file f{i}" style="left:{x}px;top:{y}px"><span>{"{}" if i<3 else "▤"}</span><b>{n}</b><small>{["신청 페이지","주문 API","로그인 확인","주문 데이터","재현 테스트"][i]}</small></div>' for i,(n,x,y) in enumerate(files))
add('s09-map',21.56,24.70,'<div class="codeworld"><div class="maphead"><span class="mono">my-shop / src</span><b>코드 지도</b></div><svg class="paths" viewBox="0 0 1000 1100"><path class="base" d="M190 430H465V545H755V820H215V430M465 545V430H755"/><path class="trace" d="M190 430H465V545H755V820"/><circle class="packet" cx="190" cy="430" r="11"/></svg>'+nodes+'<div class="missing">권한 확인은 어디에?</div><div class="repochips"><i>routes</i><i>models</i><i>tests</i><i>services</i><i>config</i></div></div><div class="example">코드 구조·접근 경로 설명용 예시</div>',
'''.codeworld{position:absolute;left:40px;top:210px;width:1000px;height:1060px}.maphead{position:absolute;left:55px;right:80px;top:75px;border-bottom:1px solid #34526a;padding-bottom:30px;display:flex;justify-content:space-between;align-items:center}.maphead span{font-size:27px;color:#95aec4}.maphead b{font-size:44px}.paths{position:absolute;inset:0;width:1000px;height:1100px}.base{fill:none;stroke:#315773;stroke-width:3}.trace{fill:none;stroke:#64d2ff;stroke-width:6;stroke-dasharray:1300;stroke-dashoffset:1300}.packet{fill:#e3faff;filter:drop-shadow(0 0 10px #64d2ff)}.file{position:absolute;width:190px;height:140px;border:1px solid #436581;background:#12263b;border-radius:14px;padding:17px 14px;box-shadow:0 12px 35px #0005}.file span{font-family:'JetBrains Mono';font-size:28px;color:#64d2ff}.file b{font-family:'JetBrains Mono';font-size:23px;display:block;margin-top:10px;white-space:nowrap}.file small{font-size:20px;color:#94aec5;display:block;margin-top:9px}.missing{position:absolute;left:320px;top:950px;color:#ff8983;border-bottom:3px solid #ff635e;font-size:39px;font-weight:800;padding:8px 12px}.repochips{position:absolute;left:65px;top:220px;display:flex;gap:20px}.repochips i{font-family:'JetBrains Mono';font-style:normal;font-size:20px;color:#8da6be;padding:6px 15px;border:1px solid #344c64;border-radius:6px}''',
"tl.fromTo('.file',{scale:.8,y:30,opacity:0},{scale:1,y:0,opacity:1,stagger:.09,duration:.28,ease:'back.out(1.5)'},0);tl.fromTo('.repochips i',{opacity:0},{opacity:1,stagger:.06,duration:.15},.1);tl.to('.trace',{strokeDashoffset:0,duration:1.3,ease:'none'},.25);tl.to('.packet',{x:275,duration:.4,ease:'none'},.25);tl.to('.packet',{y:115,duration:.2,ease:'none'},.65);tl.to('.packet',{x:565,duration:.4,ease:'none'},.85);tl.to('.packet',{y:390,duration:.4,ease:'none'},1.25);tl.to('.f2',{opacity:.25,duration:.2},@path_gap);tl.to('.f1',{borderColor:'#ff635e',backgroundColor:'#3d2531',duration:.25},@path_gap);tl.fromTo('.missing',{opacity:0,scale:.8},{opacity:1,scale:1,duration:.25,ease:'back.out(1.8)'},@path_gap);",'hide',{'path_gap':(23.28,'ui-tick',-9)})
presenter('s10-examine',24.70,25.94)
# Evidence is inspected, not replaced by another generic 'review' heading.
add('s11-review',25.94,28.57,'<div class="window">'+bar('review / orders.ts')+'<div class="reviewcode"><div><em>18</em><span>const order = findOrder(id)</span></div><div class="vulnerable"><em>19</em><span>return order</span></div><div><em>20</em><span>// caller / owner ?</span></div></div><div class="issue"><small>FINDING / 01</small><strong>주문자 확인</strong><p>주문 소유자 확인이 빠져 있음</p></div><div class="reviewstamp">재검토</div><div class="source">코드 흐름 예시</div></div>',
'''.reviewcode{position:absolute;left:30px;top:100px;right:30px;font-family:'JetBrains Mono';font-size:29px;line-height:2}.reviewcode div{padding:8px;border-radius:8px}.reviewcode em{font-style:normal;color:#9ab0c5;margin-right:28px}.reviewcode span{color:#d2e1f0}.vulnerable{background:#53313b}.issue{position:absolute;left:44px;right:44px;bottom:55px;border-left:5px solid #ff635e;background:#172b40;padding:14px 22px}.issue small{font-family:'JetBrains Mono';font-size:18px;color:#ff918b}.issue strong{font-size:29px;display:block;margin-top:4px}.issue p{font-size:22px;color:#a8bfd2;margin:7px 0 0}.reviewstamp{position:absolute;right:52px;top:285px;padding:10px 15px;border:3px solid #64d2ff;color:#64d2ff;background:#0d1726;font-size:27px;font-weight:800;transform:rotate(-7deg)}''',
ENTER+"tl.fromTo('.reviewcode div',{opacity:0,x:20},{opacity:1,x:0,stagger:.1,duration:.2},.1);tl.fromTo('.issue',{opacity:0,y:30},{opacity:1,y:0,duration:.25},.35);tl.fromTo('.reviewstamp',{scale:1.8,opacity:0},{scale:1,opacity:1,duration:.22,ease:'power3.in'},@review_check);tl.to('.vulnerable',{backgroundColor:'#244f58',duration:.3},@review_check);",cues={'review_check':(27.12,'soft-pop',-9)})

# Terminal contents are illustrative pseudocode; the same request/test is reused after patching.
TERMINAL_CSS='''
.editor{position:absolute;left:65px;top:330px;width:930px;height:860px;border:1px solid #3c5670;border-radius:20px;background:#0a1522;overflow:hidden;box-shadow:0 30px 70px #0008}.editor .tabs{height:63px;display:flex;align-items:center;gap:30px;padding:0 25px;font-family:'JetBrains Mono';font-size:23px;background:#142337;border-bottom:1px solid #345169}.tabs b{font-weight:500;color:#e0edfa}.tabs span{color:#6f8ba5}.codeblock{padding:35px 32px;font-family:'JetBrains Mono';font-size:25px;line-height:1.95;color:#c8dbea;white-space:pre}.ln{color:#52708b;margin-right:25px}.purple{color:#c4a6f0}.green{color:#74d9b7}.console{position:absolute;left:0;right:0;top:420px;bottom:0;background:#080f1b;border-top:1px solid #35526e;padding:27px 32px;font-family:'JetBrains Mono';font-size:25px;color:#a0bacf;line-height:1.8}.console .status{font-size:39px;font-weight:800;color:#ff726c;margin-top:22px}.console .note{font-family:'Pretendard';font-size:28px;margin-top:12px;color:#d7e5f0}.console .cmd{color:#d1f0e7}.cline{display:block}.redline{background:#4b2635;color:#ffb0ae;padding:8px 16px}.greenline{background:#174136;color:#a0e7c8;padding:8px 16px}.gutter{font-family:'JetBrains Mono';font-size:23px;color:#7d99b0}.patchtag{position:absolute;right:25px;bottom:25px;font-family:'JetBrains Mono';color:#75d9b7;border:2px solid #75d9b7;border-radius:8px;padding:10px 18px;font-size:24px}
'''
add('s12-test',28.57,31.14,'<div class="editor"><div class="tabs"><b>order.test</b><span>orders.ts</span></div><div class="codeblock"><span class="ln">01</span><span class="purple">test</span>("owner access", () =&gt; {\n<span class="ln">02</span>  request(<span class="green">"/order/1025"</span>)\n<span class="ln">03</span>  expect(owner).toBe(viewer)\n<span class="ln">04</span>})</div><div class="console"><div class="gutter">TERMINAL</div><div class="cmd">$ run order.test</div><div class="resultline">request /order/1025</div><div class="status">✕ FAIL</div><div class="note">다른 계정의 주문서가 열림</div></div></div><div class="example">테스트 흐름 설명용 예시 · 실행 결과 아님</div>',TERMINAL_CSS,
"tl.fromTo('.editor',{y:50,opacity:0,scale:.97},{y:0,opacity:1,scale:1,duration:.3,ease:'power3.out'},0);tl.fromTo('.codeblock',{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)',duration:.55,ease:'steps(4)'},.1);tl.fromTo('.cmd',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.4,ease:'steps(16)'},.4);tl.fromTo('.resultline',{opacity:0},{opacity:1,duration:.1},.8);tl.fromTo('.status',{opacity:0,scale:1.5},{opacity:1,scale:1,duration:.22,ease:'power3.in'},@test_fail);tl.fromTo('.note',{opacity:0,y:15},{opacity:1,y:0,duration:.2},@test_fail);",'hide',{'test_fail':(29.88,'soft-pop',-8)})
add('s13-patch',31.14,33.89,'<div class="window patch">'+bar('orders.ts / patch')+'<div class="diff"><div class="redline">− return order</div><div class="greenline">+ if (owner !== viewer)</div><div class="greenline">+ &nbsp; denyAccess()</div><div class="greenline">+ return order</div></div><div class="patchtag">PATCH</div><div class="source">수정 흐름 예시</div></div>',TERMINAL_CSS+'''.diff{position:absolute;left:28px;right:28px;top:80px;font-family:'JetBrains Mono';font-size:31px;line-height:1.5}.diff>div{margin-bottom:12px;border-radius:6px}.patchtag{bottom:60px}''',
ENTER+"tl.fromTo('.redline',{opacity:0,x:-20},{opacity:1,x:0,duration:.18},0);tl.to('.redline',{opacity:.35,duration:.25},@patch_insert);tl.fromTo('.greenline',{clipPath:'inset(0 100% 0 0)',opacity:0},{clipPath:'inset(0 0% 0 0)',opacity:1,duration:.25,stagger:.14,ease:'power2.out'},@patch_insert);tl.fromTo('.patchtag',{scale:1.6,opacity:0},{scale:1,opacity:1,duration:.22,ease:'back.out(1.8)'},@patch_done);",cues={'patch_insert':(31.43,'ui-tick',-9),'patch_done':(32.28,'soft-pop',-10)})
presenter('s14-repeat',33.89,35.84)
add('s15-block',35.84,38.22,shop_body(True)+'<div class="example">동일한 주문서로 재검사하는 흐름 예시</div>',SHOP_CSS,
"tl.set('.old,.focusbox,.detail,.pointer',{opacity:0},0);tl.set('.new',{color:'#25748b'},0);tl.set('.denied',{opacity:0,clipPath:'inset(0 0 100% 0)'},0);tl.fromTo('.store',{opacity:0,y:45,scale:.96},{opacity:1,y:0,scale:1,duration:.3,ease:'power3.out'},0);tl.to('.denied',{opacity:1,clipPath:'inset(0 0 0% 0)',duration:.3,ease:'power3.inOut'},@blocked);tl.fromTo('.denied svg',{scale:1.3},{scale:1,duration:.25,ease:'back.out(1.7)'},@blocked);tl.to('.store',{scale:1.025,duration:.9,ease:'none'},.8);",'hide',{'blocked':(36.38,'soft-pop',-8)})
presenter('s16-caution',38.22,40.20)
add('s17-isolate',40.20,42.48,'<div class="window">'+bar('실행 환경 분리')+'<div class="environments"><div class="prod"><svg viewBox="0 0 100 100"><rect x="15" y="15" width="70" height="22" rx="5"/><rect x="15" y="43" width="70" height="22" rx="5"/><rect x="15" y="71" width="70" height="22" rx="5"/></svg><b>실제 서비스</b><small>고객 데이터</small></div><div class="wire"><svg viewBox="0 0 150 100"><path d="M0 50H150"/></svg><b>×</b></div><div class="sandbox"><svg viewBox="0 0 100 100"><path d="M15 30L50 10L85 30V70L50 90L15 70Z M15 30L50 50L85 30 M50 50V90"/></svg><b>격리 환경</b><small>테스트용 코드</small></div></div></div>',
'''.environments{position:absolute;top:95px;left:45px;right:45px;display:flex;align-items:center;justify-content:space-between}.prod,.sandbox{width:290px;text-align:center;border:1px solid #45617c;border-radius:18px;padding:24px 15px;background:#15283c}.prod svg,.sandbox svg{width:110px;height:110px;fill:none;stroke:#8ca9bd;stroke-width:5}.sandbox svg{stroke:#64d2ff}.environments b{display:block;font-size:34px;margin-top:20px}.environments small{display:block;font-size:24px;color:#8da7bd;margin-top:10px}.wire{width:130px;position:relative}.wire svg{width:130px;height:100px;fill:none;stroke:#6086a2;stroke-width:4;stroke-dasharray:10 8}.wire b{position:absolute;inset:0;text-align:center;color:#ff635e;font-size:80px;line-height:90px;margin:0}''',
ENTER+"tl.fromTo('.prod,.sandbox',{opacity:0,y:20},{opacity:1,y:0,stagger:.12,duration:.25},.1);tl.fromTo('.wire b',{scale:0,rotation:-90},{scale:1,rotation:0,duration:.25,ease:'back.out(2)'},@isolate);tl.to('.wire path',{opacity:.25,duration:.2},@isolate);tl.to('.prod',{x:-10,opacity:.45,duration:.25},@isolate);tl.to('.sandbox',{x:10,borderColor:'#64d2ff',boxShadow:'0 0 25px #64d2ff30',duration:.25},@isolate);",cues={'isolate':(41.00,'ui-tick',-9)})
shot('s18-expert',42.48,44.28,'readme-caution.png','google/mantis / IMPORTANT',[(42.48,540,750,.87,0),(42.76,540,752,.99,.4)],[('expert_review',100,706,885,88,True)],cues={'expert_review':(43.24,'ui-tick',-9)})
presenter('s19-confirm',44.28,46.76)
# Native comment action from ep05, lowered below the face for this particular source framing.
add('s20-comment',46.76,50.74,'<div class="comment"><div class="avatar">나</div><div class="field">댓글에 <b class="keyword"></b><span class="cursor">▍</span></div><div class="send">게시</div></div>',
'''.comment{position:absolute;left:64px;top:1100px;width:836px;height:123px;background:#fff;border-radius:60px;display:flex;align-items:center;gap:20px;padding:0 22px;box-shadow:0 24px 60px #0007}.avatar{width:75px;height:75px;border-radius:50%;background:#32788f;color:#fff;display:grid;place-items:center;font-size:30px;font-weight:800}.field{flex:1;color:#172e43;font-size:38px;font-weight:700}.keyword{color:#227a95}.cursor{color:#328ba0}.send{font-size:30px;color:#217896;font-weight:800;padding-right:12px}''',
"tl.fromTo('.comment',{opacity:0,y:40,scale:.95},{opacity:1,y:0,scale:1,duration:.3,ease:'back.out(1.5)'},0);const kw=q('.keyword');tl.fromTo({n:0},{n:0},{n:2,duration:.35,ease:'steps(2)',onUpdate:function(){kw.textContent='보안'.slice(0,Math.round(this.targets()[0].n))}},@comment_type);tl.fromTo('.cursor',{opacity:1},{opacity:0,duration:.01,repeat:11,yoyo:true,repeatDelay:.17},0);tl.fromTo('.send',{scale:1},{scale:1.16,duration:.15,repeat:1,yoyo:true},@comment_send);",'full',{'comment_type':(48.46,'ping-comment',-10),'comment_send':(49.74,'ui-tick',-11)})

# Reframe on spoken emphasis rather than adding a generic move to every scene.
CAM_SRC.extend([(17.06,'hide',1,0),(27.12,'card',1.035,.22),(34.64,'full',1.14,.24),(39.06,'full',1.15,.24),(45.14,'full',1.11,.25),(48.46,'full',1.10,.25)])
CAM_SRC.sort(key=lambda p:p[0])

# Face position measured from source frame (1920x1080); same framing as approved series.
CAM=[(0.0 if i==0 else M(t),m,z,tw if tw else (.32 if i and m in ('card','full') and CAM_SRC[i-1][1] in ('card','full') and m!=CAM_SRC[i-1][1] else 0)) for i,(t,m,z,tw) in enumerate(CAM_SRC)]
FACE=(1020,380)
C_SRC=[(4.62,'오늘도 AI 직원을','AI 직원'),(5.94,'뽑았습니다',''),(6.76,'이번엔 보안팀이에요','보안팀'),(8.32,'구글이 공개한','구글'),(9.08,'맨티스입니다','맨티스'),(10.38,'AI로 신청서 페이지나','신청서'),(11.86,'쇼핑몰 만들어 보셨죠','쇼핑몰'),(13.56,'돌아가긴 하는데',''),(14.64,'남의 주문서까지','남의 주문서'),(15.86,'열리는 구멍이 있는지','구멍'),(17.06,'우리가 모르잖아요','모르잖아요'),(18.62,'그래서 맨티스는','맨티스'),(19.46,'그걸 팀으로 검사합니다','팀으로'),(21.56,'먼저 코드 지도를 그리고','코드 지도'),(23.28,'어디로 뚫릴지','뚫릴지'),(24.70,'다 살펴보고요',''),(25.94,'약한 곳을 찾으면','약한 곳'),(27.12,'다시 검토를 합니다','다시 검토'),(28.57,'재현할 수 있는 문제면','재현'),(29.88,'테스트를 만들고','테스트'),(31.14,'막는 코드까지 다 짜요','막는 코드'),(33.89,'그다음에 같은 테스트를','같은 테스트'),(35.84,'다시 해서',''),(36.38,'막혔는지 확인하고요','확인'),(38.22,'대신 두 가지는','두 가지'),(39.06,'꼭 지키세요','꼭'),(40.20,'실제 서비스랑','실제 서비스'),(41.00,'분리된 환경에서만 돌리고','분리된 환경'),(42.48,'결과는',''),(43.24,'보안 전문가한테','보안 전문가'),(44.28,'한 번 더 확인받으셔야 됩니다','한 번 더'),(46.76,'맨티스 쓰는 법이','맨티스'),(47.84,'궁금하시면',''),(48.46,'댓글에 보안이라고','보안'),(49.74,'남겨주세요','')]
WARN=['남의 주문서','구멍','모르잖아요','뚫릴지','약한 곳','두 가지','꼭','실제 서비스','분리된 환경']

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
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:1}},{t});tl.to('#camBox',{{...{fmt(box)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camImg',{{...{fmt(img)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camZoom',{{...{zo},duration:{tw},ease:'power2.inOut'}},{t});")
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
<title>맨티스 AI 보안팀 — Owen 스타일</title>
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
<div id="camBox"><div id="camZoom" data-layout-allow-overflow><div id="camImg"><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1" muted></video></div></div></div>
<div id="captions"></div>
<audio id="voice" src="assets/mix.m4a" data-start="0" data-duration="{DUR}" data-track-index="9"></audio>
</div>
<script>
const WARN={json.dumps(WARN, ensure_ascii=False)};
const CAPS={json.dumps(CAPS, ensure_ascii=False)};
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
CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);tl.set(el,{{opacity:0}},c[1]);}});
{chr(10).join(cam_js)}
const CAMERA={json.dumps(CAM)};
CAMERA.forEach(([t,m,z,tw])=>{{tl.set('.caption',{{top:1345,width:836}},t);if(m==='card')tl.set('.caption',{{top:840,width:836}},t+tw);}});
window.__timelines["main"]=tl;
</script></body></html>
"""
os.makedirs(os.path.join(ROOT, "scenes"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "scenes")):
    os.remove(os.path.join(ROOT, "scenes", f))
for sid, (st, du, html) in S.items():
    open(os.path.join(ROOT, "scenes", sid + ".html"), "w").write(html)
open(os.path.join(ROOT, "index.html"), "w").write(HTML)


# This manifest is the only SFX timing input. No stale mix can silently survive a scene edit.
for i,(t,m,z,tw) in enumerate(CAM):
    if i and tw:
        ACTIONS.append(dict(name=f'camera_{i}',scene='main',source=CAM_SRC[i][0],time=t,local=t,sound='whoosh-down-cut' if m=='full' else 'whoosh-up-cut',gain_db=-16))
ACTIONS.append(dict(name='opening',scene='s01-hook',source=4.57,time=0,local=0,sound='impact-low-hook',gain_db=-10))
# Sparse visual entrances; do not stack two generic SFX at every scene boundary.
for sid,(st,du,_) in S.items():
    mode=SCENE_META[sid]['mode']
    if mode!='full' and st>.05 and not any(abs(x['time']-st)<.12 for x in ACTIONS):
        ACTIONS.append(dict(name=sid+'_entrance',scene=sid,source=SCENE_META[sid]['source'][0],time=st,local=0,sound='ui-panel-appear' if mode=='card' else 'whoosh-short-cut',gain_db=-15))
ACTIONS.sort(key=lambda x:x['time'])
EV={'scenes':{sid:[st,du,'ovl' if sid in OVL else 'scn'] for sid,(st,du,_) in S.items()},'cam':CAM,'actions':ACTIONS}
(ROOT/'events.json').write_text(json.dumps(EV,ensure_ascii=False,indent=2))
(ROOT/'timing.json').write_text(json.dumps({'captions':CAPS,'camera':CAM,'scenes':EV['scenes'],'actions':ACTIONS},ensure_ascii=False,indent=2))
print(f'Built {len(S)} scenes, {len(CAPS)} captions, {len(ACTIONS)} visual/audio cues, {DUR}s')
