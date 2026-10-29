# Short01 storyboard. All times are SOURCE seconds; build.py maps them once with M(t).
# Example UIs are labelled 화면 예시; the GitHub panel is a real headless capture (assets/shots/github-repo.png).
TAG='.tag{position:absolute;right:16px;top:60px;z-index:5;font-size:19px;font-weight:700;color:#cfe6f5;background:#0a1524e8;border:1px solid #64d2ff55;border-radius:6px;padding:4px 10px}'

# 1) Hook: user-specified head copy (2026-10-29 chat), card layout so the presenter is visible from frame 0.
hook(1.50,5.10,'쓰레기 AI 컨텐츠','싹 다 잡아버림')

# 2) Invisible characters inside a draft (concept example, not a claim about any vendor).
add('s02-hidden',5.10,8.85,'<div class="window">'+bar('블로그초안.txt')+'''<div class="tag">화면 예시</div>
<div class="doc"><div class="ln">오늘 소개할<span class="chip c1"><i>U+200B</i></span>텀블러는</div>
<div class="ln">가볍고<span class="chip c2"><i>U+202F</i></span>튼튼합니다<span class="chip c3"><i>U+200B</i></span></div>
<div class="scan"></div></div>
<div class="found"><b class="px">HIDDEN</b><span>보이지 않는 문자 2 · 특이 공백 1</span></div></div>''',
TAG+'''.doc{position:absolute;left:40px;top:80px;width:870px;height:270px}.ln{font-size:50px;font-weight:700;color:#eef4ff;line-height:1;margin:30px 0 40px;white-space:nowrap;display:flex;align-items:center}
.chip{display:inline-block;width:0;overflow:hidden;opacity:0;margin:0 4px;vertical-align:middle}.chip i{display:block;font-style:normal;font-family:'JetBrains Mono';font-size:22px;font-weight:700;color:#ff635e;border:2px solid #ff635e;background:#ff3b3018;border-radius:8px;padding:6px 8px;white-space:nowrap;width:118px;text-align:center}
.scan{position:absolute;left:-40px;top:0;width:8px;height:270px;background:#64d2ff;box-shadow:0 0 30px #64d2ff;opacity:0}
.found{position:absolute;left:40px;bottom:36px;display:flex;gap:18px;align-items:center;opacity:0}.found .px{font-family:'Silkscreen';font-size:26px;color:#07101c;background:#ff635e;padding:6px 12px;border-radius:6px;font-weight:700}.found span{font-size:30px;font-weight:800;color:#fff}''',
ENTER+'''tl.fromTo('.scan',{x:0,opacity:1},{x:900,duration:.7,ease:'none'},@scan);tl.to('.scan',{opacity:0,duration:.1},@scan+.7);
tl.to('.chip',{width:134,opacity:1,duration:.25,stagger:.12,ease:'back.out(1.6)'},@mark);
tl.fromTo('.found',{opacity:0,y:20},{opacity:1,y:0,duration:.25,ease:'power3.out'},@count);''','card',
{'scan':(5.70,'whoosh-short-cut',-17),'mark':(5.98,'soft-pop',-11),'count':(7.42,'ui-tick',-12)})

# 3) Presenter only: unverified copy/paste line stays speech + caption only, no graphic.
presenter('s03-check',8.85,13.98)

# 4) Real GitHub repository, then README install commands typed verbatim.
TERM='''<div class="term"><small>README 설치 명령 그대로</small>
<div class="l l1"><b>$</b> git clone https://github.com/guillaumemeyer/watermarks-remover.git</div>
<div class="l l2"><b>$</b> cd watermarks-remover</div>
<div class="l l3"><b>$</b> python3 install_skill.py --skill clean-user-facing-text --target codex</div></div>'''
TERM_CSS='''.term{position:absolute;left:0;right:0;bottom:0;height:236px;background:#050b14f5;border-top:2px solid #64d2ff66;padding:18px 26px;z-index:4;transform:translateY(240px)}.term small{display:block;font-size:19px;color:#8fb3cc;margin-bottom:12px}
.term .l{font-family:'JetBrains Mono';font-size:19.5px;color:#e6f0f8;white-space:nowrap;margin:12px 0;clip-path:inset(0 100% 0 0)}.term .l b{color:#64d2ff;margin-right:8px}'''
TERM_JS='''tl.to('.term',{y:0,duration:.3,ease:'power3.out'},@install);
['.l1','.l2','.l3'].forEach((s,i)=>tl.to(s,{clipPath:'inset(0 0% 0 0)',duration:.3,ease:'steps(24)'},@install+.2+i*.3));'''
shot('s04-repo',13.98,16.90,'github-repo.png','github.com/guillaumemeyer/watermarks-remover',
     [(13.98,640,330,.745,0),(14.30,330,205,1.45,.45)],[('title',30,185,292,36,False)],
     TERM,TERM_CSS,TERM_JS,{'title':(14.36,'ui-tick',-12),'install':(15.80,'ui-panel-appear',-14)},
     label='실제 GitHub 화면 · 2026-10-29 캡처')

# 5) Paste own draft, type the Korean request (speech wording), send.
REQ='clean-user-facing-text로 내용은 그대로 두고 숨은 문자와 어색한 표현을 정리해줘'
add('s05-ask',16.90,22.20,'<div class="window">'+bar('AI 채팅')+'''<div class="tag">화면 예시</div>
<div class="bubble"><b class="mono">clean-user-facing-text</b>로 <span class="cyan">내용은 그대로</span> 두고 <span class="red">숨은 문자</span>와 <span class="red">어색한 표현</span>을 정리해줘</div>
<div class="preview"><small>블로그초안.txt</small>오늘 소개할 텀블러는 가볍고 튼튼합니다…</div>
<div class="composer"><div class="att"><b>TXT</b>블로그초안.txt</div><div class="input"><span class="typed"></span><span class="caret">▍</span></div><div class="sendb">↑</div></div></div>''',
TAG+'''.bubble{position:absolute;right:30px;top:90px;width:620px;background:#1b3a55;border:1px solid #64d2ff55;border-radius:22px 22px 6px 22px;padding:20px 24px;font-size:29px;font-weight:700;line-height:1.35;opacity:0}.bubble .mono{font-size:24px;color:#9fe3ff}
.composer{position:absolute;left:24px;right:24px;bottom:22px;height:200px;background:#101c2d;border:2px solid #385371;border-radius:22px;padding:16px 20px}
.att{display:inline-flex;align-items:center;gap:12px;background:#e8eef4;color:#132a3d;font-size:23px;font-weight:700;border-radius:12px;padding:8px 16px;opacity:0}.att b{font-family:'JetBrains Mono';font-size:17px;background:#2d7389;color:#fff;border-radius:5px;padding:3px 7px}
.preview{position:absolute;left:24px;top:76px;width:560px;background:#e8eef4;color:#21384b;border-radius:16px;padding:14px 18px;font-size:24px;font-weight:600;line-height:1.35;opacity:0}.preview small{display:block;font-family:'JetBrains Mono';font-size:17px;color:#2d7389;margin-bottom:4px}
.input{margin-top:12px;width:780px;font-size:31px;font-weight:600;line-height:1.35;color:#eef4ff;min-height:80px}.caret{color:#64d2ff}.sendb{position:absolute;right:20px;bottom:18px;width:64px;height:64px;border-radius:50%;background:#64d2ff;color:#07101c;font-size:36px;font-weight:900;display:grid;place-items:center}''',
ENTER+'''tl.fromTo('.att',{opacity:0,scale:.7,y:20},{opacity:1,scale:1,y:0,duration:.28,ease:'back.out(1.8)'},@paste);
const REQ='''+repr(REQ)+''';const ty=q('.typed');const st={n:0};
tl.to(st,{n:REQ.length,duration:@send-@type-.15,ease:'none',onUpdate:()=>{ty.textContent=REQ.slice(0,Math.round(st.n))}},@type);
tl.fromTo('.caret',{opacity:1},{opacity:0,duration:.01,repeat:15,yoyo:true,repeatDelay:.2},0);
tl.fromTo('.sendb',{scale:1},{scale:1.2,duration:.12,repeat:1,yoyo:true},@send);
tl.fromTo('.preview',{opacity:0,y:20},{opacity:1,y:0,duration:.25,ease:'power3.out'},@paste+.05);tl.to('.preview',{opacity:0,y:-30,duration:.15},@send);tl.set('.typed',{opacity:0},@send+.12);tl.to('.att',{opacity:0,duration:.12},@send+.12);
tl.fromTo('.bubble',{opacity:0,y:60},{opacity:1,y:0,duration:.25,ease:'power3.out'},@send+.1);''','card',
{'paste':(17.10,'soft-pop',-11),'type':(17.74,'ui-tick',-17),'send':(21.98,'ui-tick',-14)})

# 6) Presenter beat.
presenter('s06-say',22.20,24.10)

# 7) Where to use it: blog post and product page, checked before publishing (generic example).
add('s07-draft',24.10,28.15,'''<div class="tile t1"><div class="th">블로그 · 새 글</div><h3>텀블러 한 달 써본 후기</h3><i></i><i></i><i class="s"></i><div class="btn">발행</div><div class="ok">✓</div></div>
<div class="tile t2"><div class="th">상품 소개 · 편집</div><div class="img"><svg viewBox="0 0 60 80"><path d="M14 10h32l-4 64H18z"/><path d="M10 10h40" /></svg></div><h3>데일리 텀블러</h3><i class="s"></i><div class="btn">등록</div><div class="ok">✓</div></div>
<div class="gate"><span>올리기 전에</span><b>숨은 문자 검사</b><em>→</em><b>표현 정리</b></div><div class="ex">예시</div>''',
'''.tile{position:absolute;top:310px;width:456px;height:420px;background:#f4f6f8;color:#172b3c;border-radius:20px;padding:22px 26px;box-shadow:0 20px 50px #0008;opacity:0}.t1{left:64px}.t2{left:560px}
.th{font-size:20px;font-weight:700;color:#5c7283;border-bottom:1px solid #d5dee5;padding-bottom:12px}.tile h3{font-size:31px;margin:18px 0 16px}.tile i{display:block;height:14px;background:#d8e0e7;border-radius:7px;margin:13px 0}.tile i.s{width:62%}
.img{height:120px;background:linear-gradient(135deg,#d7e6e8,#b8d3da);border-radius:12px;margin-top:16px;display:grid;place-items:center}.img svg{height:96px}.img path{fill:none;stroke:#206275;stroke-width:4}
.btn{position:absolute;right:24px;bottom:22px;font-size:24px;font-weight:800;color:#fff;background:#2d7389;border-radius:12px;padding:10px 26px}.ok{position:absolute;left:24px;bottom:18px;width:54px;height:54px;border-radius:50%;background:#64d2ff;color:#07101c;font-size:34px;font-weight:900;display:grid;place-items:center;transform:scale(0)}
.gate{position:absolute;left:64px;top:748px;width:952px;height:66px;border:2px solid #64d2ff;border-radius:16px;background:#0b1a2b;display:flex;align-items:center;justify-content:center;gap:16px;font-size:28px;font-weight:800;opacity:0}.gate span{color:#9fb6c9}.gate b{color:#64d2ff}.gate em{font-style:normal;color:#fff}
.ex{position:absolute;right:76px;top:318px;font-size:18px;font-weight:700;color:#5c7283;z-index:3}''',
'''tl.fromTo('.t1',{opacity:0,y:40,rotation:-3},{opacity:1,y:0,rotation:0,duration:.3,ease:'back.out(1.5)'},@blog);
tl.fromTo('.t2',{opacity:0,y:40,rotation:3},{opacity:1,y:0,rotation:0,duration:.3,ease:'back.out(1.5)'},@product);
tl.fromTo('.gate',{opacity:0,y:-16},{opacity:1,y:0,duration:.25,ease:'power3.out'},@before);tl.to('.btn',{opacity:.35,duration:.2},@before);
tl.to('.ok',{scale:1,duration:.25,stagger:.1,ease:'back.out(2)'},@check);tl.to('.btn',{opacity:1,background:'#1f9fc9',duration:.2},@check+.15);''','card',
{'blog':(24.13,'soft-pop',-12),'product':(25.10,'soft-pop',-12),'before':(26.10,'ui-panel-appear',-15),'check':(27.14,'ui-tick',-11)})

# 8) Graphics only: original kept, revised copy, changed parts listed (example result).
add('s08-diff',28.15,31.45,'''<div class="dt"><span class="serif">before</span> 원본.txt <em>그대로 보관</em></div>
<div class="pane p1"><div class="row">오늘 소개할<s class="hid">U+200B<i class="st"></i></s>텀블러는 가볍고<s class="hid">U+202F<i class="st"></i></s>튼튼합니다</div><div class="row"><u class="aw">다양한 상황에서 활용 가능한<i class="st"></i></u> 제품입니다</div></div>
<div class="dt d2"><span class="serif">after</span> 수정본.txt <em>새 파일</em></div>
<div class="pane p2"><div class="row">오늘 소개할 텀블러는 가볍고 튼튼합니다</div><div class="row"><mark class="nw">어디서나 쓰기 좋은</mark> 제품입니다</div></div>
<div class="sum"><b>바뀐 부분 3곳</b><span>숨은 문자 2 · 표현 1</span></div><div class="ex2">화면 예시 · 실제 실행 결과 아님</div>''',
'''.dt{position:absolute;left:64px;top:320px;font-size:30px;font-weight:800;color:#fff;display:flex;gap:14px;align-items:baseline}.dt .serif{font-family:'Instrument Serif';font-style:italic;font-weight:400;font-size:44px;color:#64d2ff}.dt em{font-style:normal;font-size:22px;color:#8fb3cc}.d2{top:700px}
.pane{position:absolute;left:64px;width:836px;background:#0d1726;border:1px solid #385371;border-radius:20px;padding:26px 30px}.p1{top:380px}.p2{top:760px;border-color:#64d2ff88;opacity:0}
.row{font-size:33px;font-weight:700;color:#e6f0f8;white-space:nowrap;margin:12px 0 18px}
.hid{text-decoration:none;display:inline-block;font-family:'JetBrains Mono';font-size:18px;color:#ff635e;border:2px solid #ff635e;border-radius:6px;padding:2px 6px;margin:0 6px;vertical-align:middle;position:relative}
.st{position:absolute;left:-4px;right:-4px;top:50%;height:3px;background:#ff3b30;transform:scaleX(0);transform-origin:0 50%}
.aw{text-decoration:none;position:relative;color:#ffb3ae}.nw{background:#64d2ff33;color:#9fe3ff;border-radius:6px;padding:0 6px}
.sum{position:absolute;left:64px;top:1130px;width:836px;height:92px;border-radius:18px;background:#64d2ff;color:#07101c;display:flex;align-items:center;justify-content:center;gap:24px;opacity:0}.sum b{font-size:38px;font-weight:900}.sum span{font-size:28px;font-weight:700}
.ex2{position:absolute;left:64px;top:1240px;width:836px;text-align:center;font-size:21px;color:#8fb3cc}''',
'''tl.fromTo('.p1',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);tl.fromTo('.d2',{opacity:0},{opacity:1,duration:.2},@rev);
tl.fromTo('.p2',{opacity:0,y:40},{opacity:1,y:0,duration:.3,ease:'power3.out'},@rev);
tl.fromTo('.st',{scaleX:0},{scaleX:1,duration:.22,stagger:.12,ease:'power2.out'},@diff);tl.to('.aw',{color:'#ff635e',duration:.15},@diff+.24);
tl.fromTo('.sum',{opacity:0,scale:.9},{opacity:1,scale:1,duration:.25,ease:'back.out(1.8)'},@sum);''','hide',
{'rev':(28.96,'soft-pop',-12),'diff':(29.52,'ui-tick',-11),'sum':(30.14,'soft-pop',-12)})

# 9) Presenter beat.
presenter('s09-guide-say',31.45,32.64)

# 10) Real contents of the comment-delivered guide (actual-guide-final.md headings + its Korean command).
add('s10-guide',32.64,36.75,'<div class="window">'+bar('댓글 자료 · 실제 목차')+'''
<div class="gd"><h2>AI로 쓴 글, 올리기 전에 정리하는 법</h2><p>핵심 요약 + 한글 사용 명령</p>
<div class="toc r1"><b>01</b>설치하기</div><div class="toc r2"><b>02</b>글 한 편 정리하기</div><div class="toc r3"><b>03</b>파일로 받기</div><div class="toc r4"><b>04</b>반복해서 쓸 때 저장할 요청</div><div class="toc r5"><b>05</b>확인하고 내보내기</div></div>
<div class="cmd"><small>한글 명령 예</small>clean-user-facing-text로 아래 글을 점검해줘 이상한 공백이나 보이지 않는 문자를 확인하고 문장은 내 말투에 맞게 다듬어줘</div></div>''',
'''.gd{position:absolute;left:36px;top:70px;width:520px}.gd h2{font-size:30px;margin:0 0 6px;line-height:1.2}.gd p{font-size:20px;color:#8fb3cc;margin:0 0 14px}
.toc{font-size:25px;font-weight:700;color:#c9d8e6;padding:9px 14px;margin:5px 0;border-radius:10px;border:1px solid transparent}.toc b{font-family:'JetBrains Mono';color:#64d2ff;margin-right:14px;font-size:21px}.toc.on{background:#64d2ff1f;border-color:#64d2ff88;color:#fff}
.cmd{position:absolute;right:28px;top:96px;width:340px;background:#f4f6f8;color:#172b3c;border-radius:16px;padding:18px 20px;font-size:21px;font-weight:600;line-height:1.45;box-shadow:0 16px 40px #0008;opacity:0}.cmd small{display:block;font-size:17px;font-weight:800;color:#2d7389;margin-bottom:8px}''',
ENTER+'''const ON={backgroundColor:'#64d2ff1f',borderColor:'#64d2ff88',color:'#ffffff',duration:.18};tl.to('.r1',ON,.05);
tl.fromTo('.cmd',{opacity:0,x:60,rotation:4},{opacity:1,x:0,rotation:1,duration:.3,ease:'back.out(1.5)'},@copy);
['.r2','.r3','.r4'].forEach((s,i)=>tl.to(s,ON,@cmd+i*.12));
tl.to('.r5',ON,@done);tl.fromTo('.gd h2',{color:'#eef4ff'},{color:'#64d2ff',duration:.25},@done);''','card',
{'copy':(32.70,'soft-pop',-14),'cmd':(33.86,'ui-tick',-12),'done':(35.38,'ui-tick',-13)})

# 11) CTA: comment field below the face under a bottom-anchored close-up.
comment(36.75,40.40,'정리')
CAM_SRC.append((36.75,'full',1.36,0))
