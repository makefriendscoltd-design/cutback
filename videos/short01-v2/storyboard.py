# Short01 v2 storyboard (reference grammar: top UI card + lower presenter card, state change every ~0.7-1.0s).
# All times are SOURCE seconds. Cue = (source time, sound or None, gain). None = visual-only state change.
# Example UIs carry 화면 예시; the GitHub panel is the real 2026-10-29 headless capture.
TAG='.tag{position:absolute;right:16px;top:60px;z-index:5;font-size:19px;font-weight:700;color:#cfe6f5;background:#0a1524e8;border:1px solid #64d2ff55;border-radius:6px;padding:4px 10px}'
LIGHT='.window.light{background:#f6f8fa;border-color:#c9d6e2}.window.light .bar{background:#eaeef2;border-bottom-color:#d0d9e2}.window.light .bar span{color:#4b6072}'
DOC_CSS='''.doc{position:absolute;left:36px;top:78px;width:880px}.ln{font-size:44px;font-weight:700;color:#14283a;line-height:1;margin:22px 0 30px;white-space:nowrap;display:flex;align-items:center}
.chip{display:inline-block;width:0;overflow:hidden;opacity:0;margin:0 3px;vertical-align:middle}.chip i{display:block;font-style:normal;font-family:'JetBrains Mono';font-size:21px;font-weight:700;color:#e5322b;border:2px solid #ff3b30;background:#ff3b3014;border-radius:8px;padding:5px 7px;white-space:nowrap;width:116px;text-align:center}
.scan{position:absolute;left:-30px;top:0;width:8px;height:250px;background:#64d2ff;box-shadow:0 0 30px #64d2ff;opacity:0}'''

# 1) Opening (~3s): head copy pinned at the top, only the panel below changes; presenter card below.
add('s01-hook',1.52,5.10,'''<div class="hl"><div class="q">쓰레기 AI 컨텐츠</div><div class="a">싹 다 잡아버림</div></div>
<div class="window light mini">'''+bar('AI가 쓴 글.txt')+'''<div class="mdoc"><div class="m1"><span>오늘 소개할 텀블러는</span></div><div class="m2"><span>가볍고<b class="dot d1"></b> 튼튼합니다<b class="dot d2"></b></span></div></div><div class="stamp">AI 작성</div><div class="scan"></div></div>''',
LIGHT+'''.hl{position:absolute;left:64px;top:300px;width:952px;text-align:center;font-weight:900;letter-spacing:-3px}.hl .q{font-size:76px;color:#fff;line-height:1.1;white-space:nowrap}.hl .a{display:inline-block;font-size:70px;color:#07101c;background:#64d2ff;border-radius:16px;margin-top:14px;padding:10px 34px;white-space:nowrap;box-shadow:0 15px 50px #64d2ff30}
.mini{top:548px;height:272px}.mdoc{position:absolute;left:34px;top:70px}.mdoc div{font-size:40px;font-weight:700;color:#14283a;margin:0 0 22px;white-space:nowrap}.mdoc span{display:inline-block;clip-path:inset(0 100% 0 0)}
.dot{display:inline-block;width:16px;height:16px;border-radius:50%;background:#ff3b30;margin:0 4px 6px;transform:scale(0);box-shadow:0 0 14px #ff3b30}
.stamp{position:absolute;right:30px;top:72px;font-family:'Silkscreen';font-weight:700;font-size:24px;color:#2d7389;border:3px solid #2d7389;border-radius:6px;padding:4px 10px;transform:rotate(-8deg) scale(0);opacity:0}
.mini .scan{height:200px;top:60px}''',
'''tl.fromTo('.mini',{opacity:0,y:40},{opacity:1,y:0,duration:.28,ease:'power3.out'},0);tl.fromTo('.hl .a',{scaleX:.4,opacity:0},{scaleX:1,opacity:1,duration:.25,ease:'back.out(1.8)'},.05);
tl.to('.m1 span',{clipPath:'inset(0 0% 0 0)',duration:.35,ease:'steps(10)'},@line1);tl.to('.m2 span',{clipPath:'inset(0 0% 0 0)',duration:.35,ease:'steps(9)'},@line2);
tl.to('.stamp',{scale:1,opacity:1,duration:.22,ease:'back.out(2.5)'},@stamp);
tl.fromTo('.mini .scan',{x:0,opacity:1},{x:880,duration:.45,ease:'none'},@scan);tl.to('.mini .scan',{opacity:0,duration:.05},@scan+.45);
tl.to('.dot',{scale:1,duration:.18,stagger:.1,ease:'back.out(3)'},@dots);''','card',
{'line1':(2.20,None,0),'line2':(2.68,None,0),'stamp':(3.58,'soft-pop',-13),'scan':(4.42,'whoosh-short-cut',-18),'dots':(4.80,None,0)})

# 2) Hidden characters light up one by one (concept example, no vendor claim).
add('s02-hidden',5.10,8.85,'<div class="window light">'+bar('AI가 쓴 글.txt')+'''<div class="tag">화면 예시</div>
<div class="doc"><div class="ln">오늘 소개할<span class="chip c1"><i>U+200B</i></span>텀블러는</div>
<div class="ln">가볍고<span class="chip c2"><i>U+202F</i></span>튼튼합니다<span class="chip c3"><i>U+200B</i></span></div><div class="scan"></div></div>
<div class="found"><b class="px">HIDDEN</b><span class="n">숨은 문자 <em>0</em>개</span><span class="kind">보이지 않는 문자 2 · 특이 공백 1</span></div></div>''',
LIGHT+TAG+DOC_CSS+'''.found{position:absolute;left:36px;bottom:30px;display:flex;gap:16px;align-items:center}.found .px{font-family:'Silkscreen';font-size:24px;color:#fff;background:#ff3b30;padding:6px 12px;border-radius:6px;font-weight:700}.found .n{font-size:32px;font-weight:900;color:#14283a}.found .n em{font-style:normal;color:#e5322b}.found .kind{font-size:24px;font-weight:700;color:#4b6072;opacity:0}''',
ENTER+'''tl.fromTo('.doc .scan',{x:0,opacity:1},{x:880,duration:.4,ease:'none'},.1);tl.to('.doc .scan',{opacity:0,duration:.05},.5);
const n=q('.found .n em');[['.c1',@c1,1],['.c2',@c2,2],['.c3',@c3,3]].forEach(([s,t,k])=>{tl.to(s,{width:128,opacity:1,duration:.22,ease:'back.out(1.8)'},t);tl.call(()=>{n.textContent=k},null,t);tl.call(()=>{n.textContent=k-1},null,t-.001)});
tl.fromTo('.found .kind',{opacity:0,x:-20},{opacity:1,x:0,duration:.25},@kind);tl.fromTo('.chip i',{boxShadow:'0 0 0 #ff3b30'},{boxShadow:'0 0 22px #ff3b30',duration:.3,repeat:1,yoyo:true},@pulse);''','card',
{'c1':(5.52,'soft-pop',-12),'c2':(5.96,None,0),'c3':(6.50,None,0),'kind':(6.94,'ui-tick',-13),'pulse':(7.70,None,0)})

# 3) Presenter emphasis #1. The unverified copy/paste line stays speech + caption only.
presenter('s03-paste',8.85,11.20)

# 4) Check -> hidden chars disappear -> awkward phrase rewritten (example of what the tool does).
add('s04-check',11.20,13.98,'<div class="window light">'+bar('AI가 쓴 글.txt')+'''<div class="tag">화면 예시</div>
<div class="doc"><div class="ln">오늘 소개할<span class="chip on"><i>U+200B</i></span>텀블러는</div>
<div class="ln">가볍고<span class="chip on"><i>U+202F</i></span>튼튼합니다<span class="chip on"><i>U+200B</i></span></div>
<div class="ln l3"><span class="old">다양한 상황에서 활용 가능한</span><span class="new">어디서나 쓰기 좋은</span>&nbsp;제품</div><div class="scan"></div></div>
<div class="status"><b class="s1">검사 중</b><b class="s2">숨은 문자 3개 정리</b><b class="s3">표현 1곳 다듬음</b></div></div>''',
LIGHT+TAG+DOC_CSS+'''.chip.on{width:128px;opacity:1}.l3{position:relative}.old{position:relative;color:#a03a33}.old::after{content:'';position:absolute;left:0;right:0;top:52%;height:4px;background:#ff3b30;transform:scaleX(var(--k,0));transform-origin:0 50%}
.new{position:absolute;left:0;top:-2px;background:#64d2ff40;color:#0b5a78;border-radius:8px;padding:0 6px;opacity:0}
.status{position:absolute;left:36px;bottom:28px;display:flex;gap:14px}.status b{font-size:25px;font-weight:800;border-radius:10px;padding:8px 14px;opacity:0}.s1{background:#14283a;color:#fff}.s2{background:#64d2ff;color:#07101c}.s3{background:#64d2ff;color:#07101c}''',
ENTER+'''tl.to('.ln:not(.l3)',{backgroundColor:'#64d2ff22',duration:.2},@glow);
tl.fromTo('.doc .scan',{x:0,opacity:1},{x:880,duration:.4,ease:'none'},@scan);tl.to('.doc .scan',{opacity:0,duration:.05},@scan+.4);tl.to('.s1',{opacity:1,duration:.15},@scan);
tl.to('.chip',{width:0,opacity:0,duration:.25,stagger:.08,ease:'power2.in'},@clean);tl.to('.s1',{opacity:0,duration:.1},@clean);tl.fromTo('.s2',{opacity:0,y:12},{opacity:1,y:0,duration:.2},@clean+.1);
tl.to('.old',{'--k':1,duration:.2},@fix);tl.to('.old',{opacity:0,duration:.15},@fix+.25);tl.to('.new',{opacity:1,duration:.2},@fix+.3);tl.fromTo('.s3',{opacity:0,y:12},{opacity:1,y:0,duration:.2},@fix+.3);''','card',
{'glow':(11.82,None,0),'scan':(12.18,'whoosh-short-cut',-17),'clean':(12.96,'ui-tick',-12),'fix':(13.40,None,0)})

# 5) Real GitHub capture: area-by-area zoom with drawn outlines.
shot('s05-repo',13.98,15.72,'github-repo.png','github.com/guillaumemeyer/watermarks-remover',
     [(13.98,640,330,.745,0),(14.30,330,205,1.45,.3),(14.74,500,1600,1.35,.3)],
     [('title',30,185,292,36,False),('mit',444,1578,114,32,False)],
     cues={'title':(14.30,None,0),'mit':(14.80,None,0)},label='실제 GitHub 화면 · 2026-10-29 캡처')

# 6) README install commands, split with shell line continuations so they read on a phone.
add('s06-install',15.72,17.05,'''<div class="window term">'''+bar('terminal · README 설치 명령')+'''<pre class="cmds"><span class="k k1"><b>$</b> git clone \\
    https://github.com/guillaumemeyer/watermarks-remover.git</span>
<span class="k k2"><b>$</b> cd watermarks-remover</span>
<span class="k k3"><b>$</b> python3 install_skill.py \\
    --skill clean-user-facing-text \\
    --target codex</span></pre></div>''',
'''.window.term{background:#050b14}.cmds{position:absolute;left:28px;top:70px;margin:0;font-family:'JetBrains Mono';font-size:24px;line-height:1.55;color:#e6f0f8}.cmds b{color:#64d2ff}.k{display:inline-block;clip-path:inset(0 100% 0 0)}''',
ENTER+'''tl.to('.k1',{clipPath:'inset(0 0% 0 0)',duration:.28,ease:'steps(14)'},@cmd1);tl.to('.k2',{clipPath:'inset(0 0% 0 0)',duration:.2,ease:'steps(8)'},@cmd2);tl.to('.k3',{clipPath:'inset(0 0% 0 0)',duration:.3,ease:'steps(14)'},@cmd3);''','card',
{'cmd1':(15.77,'ui-panel-appear',-15),'cmd2':(16.10,None,0),'cmd3':(16.46,None,0)})

# 7) Paste own draft, type the request phrase by phrase in sync with speech, send.
add('s07-ask',17.05,22.20,'<div class="window light">'+bar('AI 채팅')+'''<div class="tag">화면 예시</div>
<div class="preview"><small>블로그초안.txt</small>오늘 소개할 텀블러는 가볍고 튼튼합니다…</div>
<div class="bubble"><b class="mono">clean-user-facing-text</b>로 <span class="hc">내용은 그대로</span> 두고 <span class="hr">숨은 문자</span>와 <span class="hr">어색한 표현</span>을 정리해줘</div>
<div class="composer"><div class="att"><b>TXT</b>블로그초안.txt</div><div class="input"><span class="t t0">clean-user-facing-text로 </span><span class="t t1">내용은 그대로 두고 </span><span class="t t2">숨은 문자와 </span><span class="t t3">어색한 표현을 </span><span class="t t4">정리해줘</span><span class="caret">▍</span></div><div class="sendb">↑</div></div></div>''',
LIGHT+TAG+'''.preview{position:absolute;left:24px;top:72px;width:560px;background:#fff;border:1px solid #d0d9e2;color:#21384b;border-radius:16px;padding:12px 18px;font-size:24px;font-weight:600;opacity:0}.preview small{display:block;font-family:'JetBrains Mono';font-size:17px;color:#2d7389}
.bubble{position:absolute;right:26px;top:72px;width:640px;background:#1b3a55;color:#fff;border-radius:22px 22px 6px 22px;padding:18px 22px;font-size:29px;font-weight:700;line-height:1.35;opacity:0}.bubble .mono{font-size:23px;color:#9fe3ff}.hc{color:#64d2ff}.hr{color:#ff8a84}
.composer{position:absolute;left:24px;right:24px;bottom:20px;height:232px;background:#fff;border:2px solid #9fb6c9;border-radius:22px;padding:14px 20px}
.att{display:inline-flex;align-items:center;gap:12px;background:#e8eef4;color:#132a3d;font-size:22px;font-weight:700;border-radius:12px;padding:6px 14px;opacity:0}.att b{font-family:'JetBrains Mono';font-size:16px;background:#2d7389;color:#fff;border-radius:5px;padding:3px 7px}
.input{margin-top:10px;width:790px;font-size:31px;font-weight:700;line-height:1.38;color:#14283a}.t{display:none}.t0{font-family:'JetBrains Mono';font-size:25px;color:#2d7389}.caret{color:#2d7389}
.sendb{position:absolute;right:18px;bottom:16px;width:62px;height:62px;border-radius:50%;background:#64d2ff;color:#07101c;font-size:34px;font-weight:900;display:grid;place-items:center}''',
ENTER+'''tl.fromTo('.att',{opacity:0,scale:.7},{opacity:1,scale:1,duration:.25,ease:'back.out(1.8)'},@paste);tl.fromTo('.preview',{opacity:0,y:20},{opacity:1,y:0,duration:.25},@paste+.05);
[['.t0',@t0],['.t1',@t1],['.t2',@t2],['.t3',@t3],['.t4',@t4]].forEach(([s,t])=>{tl.set(s,{display:'inline'},t);tl.fromTo(s,{opacity:0},{opacity:1,duration:.18},t)});
tl.to('.t1',{color:'#0b7fa6',duration:.2},@keep);
tl.fromTo('.sendb',{scale:1},{scale:1.2,duration:.12,repeat:1,yoyo:true},@send);tl.to('.preview,.att,.input',{opacity:0,duration:.12},@send+.1);
tl.fromTo('.bubble',{opacity:0,y:60},{opacity:1,y:0,duration:.25,ease:'power3.out'},@send+.1);
tl.fromTo('.caret',{opacity:1},{opacity:0,duration:.01,repeat:19,yoyo:true,repeatDelay:.2},0);''','card',
{'paste':(17.10,'soft-pop',-12),'t0':(17.40,None,0),'t1':(17.74,None,0),'keep':(18.58,None,0),'t2':(19.50,None,0),'t3':(20.50,None,0),'t4':(21.46,None,0),'send':(21.98,None,0)})

# 8) Presenter emphasis #2.
presenter('s08-say',22.20,24.10)

# 9) Where: blog post and product page, checked before publishing (generic example).
add('s09-draft',24.10,28.15,'''<div class="tile t1"><div class="th">블로그 · 새 글</div><h3><span>텀블러 한 달 써본 후기</span></h3><i></i><i></i><i class="s"></i><div class="btn">발행</div><div class="ok">✓</div></div>
<div class="tile t2"><div class="th">상품 소개 · 편집</div><div class="img"><svg viewBox="0 0 60 80"><path d="M14 10h32l-4 64H18z"/><path d="M10 10h40"/></svg></div><h3><span>데일리 텀블러</span></h3><i class="s"></i><div class="btn">등록</div><div class="ok">✓</div></div>
<div class="gate"><span>올리기 전에</span><b>숨은 문자 검사</b><em>→</em><b>표현 정리</b></div><div class="ex">예시</div>''',
'''.tile{position:absolute;top:310px;width:456px;height:420px;background:#f6f8fa;color:#172b3c;border-radius:20px;padding:22px 26px;box-shadow:0 20px 50px #0008;opacity:0}.t1{left:64px}.t2{left:560px}
.th{font-size:20px;font-weight:700;color:#5c7283;border-bottom:1px solid #d5dee5;padding-bottom:12px}.tile h3{font-size:31px;margin:18px 0 16px}.tile h3 span{display:inline-block;clip-path:inset(0 100% 0 0)}.tile i{display:block;height:14px;background:#d8e0e7;border-radius:7px;margin:13px 0;transform:scaleX(0);transform-origin:0 50%}.tile i.s{width:62%}
.img{height:120px;background:linear-gradient(135deg,#d7e6e8,#b8d3da);border-radius:12px;margin-top:16px;display:grid;place-items:center}.img svg{height:96px}.img path{fill:none;stroke:#206275;stroke-width:4}
.btn{position:absolute;right:24px;bottom:22px;font-size:24px;font-weight:800;color:#fff;background:#2d7389;border-radius:12px;padding:10px 26px}.ok{position:absolute;left:24px;bottom:18px;width:54px;height:54px;border-radius:50%;background:#64d2ff;color:#07101c;font-size:34px;font-weight:900;display:grid;place-items:center;transform:scale(0)}
.gate{position:absolute;left:64px;top:748px;width:952px;height:66px;border:2px solid #64d2ff;border-radius:16px;background:#0b1a2b;display:flex;align-items:center;justify-content:center;gap:16px;font-size:28px;font-weight:800;opacity:0}.gate span{color:#9fb6c9}.gate b{color:#64d2ff}.gate em{font-style:normal;color:#fff}
.ex{position:absolute;right:76px;top:318px;font-size:18px;font-weight:700;color:#5c7283;z-index:3}''',
'''tl.fromTo('.t1',{opacity:0,y:40,rotation:-3},{opacity:1,y:0,rotation:0,duration:.28,ease:'back.out(1.5)'},@blog);
tl.to('.t1 h3 span',{clipPath:'inset(0 0% 0 0)',duration:.3,ease:'steps(10)'},@btxt);tl.to('.t1 i',{scaleX:1,duration:.2,stagger:.07},@btxt+.2);
tl.fromTo('.t2',{opacity:0,y:40,rotation:3},{opacity:1,y:0,rotation:0,duration:.28,ease:'back.out(1.5)'},@product);
tl.to('.t2 h3 span',{clipPath:'inset(0 0% 0 0)',duration:.25,ease:'steps(6)'},@ptxt);tl.to('.t2 i',{scaleX:1,duration:.2},@ptxt+.2);
tl.fromTo('.gate',{opacity:0,y:-16},{opacity:1,y:0,duration:.25,ease:'power3.out'},@before);tl.to('.btn',{opacity:.35,duration:.2},@before);
tl.to('.t1 .ok',{scale:1,duration:.22,ease:'back.out(2)'},@check1);tl.to('.t2 .ok',{scale:1,duration:.22,ease:'back.out(2)'},@check2);tl.to('.btn',{opacity:1,background:'#1f9fc9',duration:.2},@check2+.12);''','card',
{'blog':(24.13,None,0),'btxt':(24.62,None,0),'product':(25.10,None,0),'ptxt':(25.66,None,0),'before':(26.10,'ui-panel-appear',-16),'check1':(26.70,None,0),'check2':(27.14,'ui-tick',-12)})

# 10) Original kept / revised file / changed parts, struck one by one (example result).
add('s10-diff',28.15,31.45,'''<div class="pane p1"><div class="ph"><span class="serif">before</span> 원본.txt <em>그대로 보관</em></div><div class="row">오늘 소개할<s class="hid h1">U+200B<i class="st"></i></s>텀블러는 가볍고<s class="hid h2">U+202F<i class="st"></i></s>튼튼합니다</div><div class="row"><u class="aw">다양한 상황에서 활용 가능한<i class="st"></i></u> 제품입니다</div></div>
<div class="pane p2"><div class="ph"><span class="serif">after</span> 수정본.txt <em>새 파일</em></div><div class="row">오늘 소개할 텀블러는 가볍고 튼튼합니다</div><div class="row"><mark class="nw">어디서나 쓰기 좋은</mark> 제품입니다</div></div>
<div class="sum"><b>바뀐 부분 3곳</b></div><div class="ex2">화면 예시 · 실제 실행 결과 아님</div>''',
'''.pane{position:absolute;left:64px;width:952px;height:240px;background:#f6f8fa;color:#14283a;border-radius:18px;padding:16px 26px;box-shadow:0 16px 40px #0007}.p1{top:300px}.p2{top:556px;border:3px solid #64d2ff;opacity:0}
.ph{font-size:24px;font-weight:800;display:flex;gap:12px;align-items:baseline}.ph .serif{font-family:'Instrument Serif';font-style:italic;font-weight:400;font-size:38px;color:#1f8fb8}.ph em{font-style:normal;font-size:19px;color:#5c7283}
.row{font-size:31px;font-weight:700;white-space:nowrap;margin:14px 0 10px}
.hid{text-decoration:none;display:inline-block;font-family:'JetBrains Mono';font-size:17px;color:#b81f19;border:2px solid #ff3b30;border-radius:6px;padding:2px 5px;margin:0 5px;vertical-align:middle;position:relative}
.st{position:absolute;left:-4px;right:-4px;top:50%;height:4px;background:#ff3b30;transform:scaleX(0);transform-origin:0 50%}.aw{text-decoration:none;position:relative;color:#a03a33}
.nw{background:#64d2ff55;color:#0b5a78;border-radius:6px;padding:0 6px}
.sum{position:absolute;right:76px;top:568px;z-index:4;border-radius:12px;background:#64d2ff;color:#07101c;padding:8px 18px;opacity:0}.sum b{font-size:28px;font-weight:900}
.ex2{position:absolute;left:64px;top:804px;width:952px;text-align:right;font-size:17px;color:#8fb3cc}''',
'''tl.fromTo('.p1',{opacity:0,y:-30},{opacity:1,y:0,duration:.28,ease:'power3.out'},0);
tl.fromTo('.p2',{opacity:0,y:40},{opacity:1,y:0,duration:.28,ease:'power3.out'},@rev);
tl.to('.h1 .st',{scaleX:1,duration:.2},@s1);tl.to('.h2 .st',{scaleX:1,duration:.2},@s2);tl.to('.aw .st',{scaleX:1,duration:.25},@s3);
tl.fromTo('.nw',{backgroundColor:'#64d2ff00'},{backgroundColor:'#64d2ff55',duration:.25},@s3+.1);
tl.fromTo('.sum',{opacity:0,scale:.8},{opacity:1,scale:1,duration:.22,ease:'back.out(2)'},@sum);''','card',
{'rev':(28.96,'soft-pop',-13),'s1':(29.52,None,0),'s2':(29.82,None,0),'s3':(30.14,None,0),'sum':(30.55,'soft-pop',-14)})

# 11) Actual guide headings (actual-guide-final.md), checked one by one while the list scrolls down.
add('s11-guide',31.45,36.75,'<div class="window light">'+bar('댓글 자료 · 실제 목차')+'''
<div class="gd"><h2>AI로 쓴 글, 올리기 전에 정리하는 법</h2><div class="lw"><div class="list">
<div class="toc r1"><b>01</b>설치하기<i>✓</i></div><div class="toc r2"><b>02</b>글 한 편 정리하기<i>✓</i></div><div class="toc r3"><b>03</b>파일로 받기<i>✓</i></div><div class="toc r4"><b>04</b>반복해서 쓸 때 저장할 요청<i>✓</i></div><div class="toc r5"><b>05</b>확인하고 내보내기<i>✓</i></div></div></div></div>
<div class="cmd"><small>한글 명령 예</small>clean-user-facing-text로 아래 글을 점검해줘 이상한 공백이나 보이지 않는 문자를 확인하고 문장은 내 말투에 맞게 다듬어줘</div></div>''',
LIGHT+'''.gd{position:absolute;left:30px;top:66px;width:540px}.lw{height:370px;overflow:hidden}.gd h2{font-size:29px;margin:0 0 12px;line-height:1.2;color:#14283a}.list{position:relative}
.toc{font-size:29px;font-weight:700;color:#4b6072;padding:15px 16px;margin:8px 0;border-radius:12px;border:2px solid #d0d9e2;background:#fff;display:flex;align-items:center}.toc b{font-family:'JetBrains Mono';color:#1f8fb8;margin-right:14px;font-size:22px}.toc i{margin-left:auto;font-style:normal;width:36px;height:36px;border-radius:50%;background:#64d2ff;color:#07101c;font-weight:900;display:grid;place-items:center;transform:scale(0)}
.cmd{position:absolute;right:26px;top:96px;width:340px;background:#14283a;color:#eef4ff;border-radius:16px;padding:18px 20px;font-size:21px;font-weight:600;line-height:1.45;box-shadow:0 16px 40px #0006;opacity:0}.cmd small{display:block;font-size:17px;font-weight:800;color:#64d2ff;margin-bottom:8px}''',
ENTER+'''const ON={borderColor:'#64d2ff',color:'#14283a',duration:.15};
[['.r1',@r1,0],['.r2',@r2,0],['.r3',@r3,-24],['.r4',@r4,-48],['.r5',@r5,-58]].forEach(([s,t,y])=>{tl.to(s,ON,t);tl.to(s+' i',{scale:1,duration:.2,ease:'back.out(2.5)'},t);tl.to('.list',{y:y,duration:.25,ease:'power2.inOut'},t)});
tl.fromTo('.cmd',{opacity:0,x:60,rotation:4},{opacity:1,x:0,rotation:1,duration:.28,ease:'back.out(1.5)'},@cmd);''','card',
{'r1':(31.60,None,0),'r2':(32.64,None,0),'cmd':(33.30,'soft-pop',-14),'r3':(33.86,None,0),'r4':(34.56,None,0),'r5':(35.38,'ui-tick',-14)})

# 12) CTA: comment field below the face, keyword typed large in #64d2ff.
comment(36.75,40.40,'정리')
CAM_SRC.append((36.75,'full',1.36,0))
