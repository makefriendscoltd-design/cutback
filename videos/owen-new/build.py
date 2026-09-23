#!/usr/bin/env python3
"""Owen-style 9:16 edit of the 2026-09-23 talking-head take ("클로드 코드 플러그인 5개").
Person = jump-cut footage (cut.py → assets/person.mp4). Graphics = HyperFrames sub-compositions.
Run: python3 cut.py (once) && python3 build.py
"""
import os, sys, json, re
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "nick-plugins-mg"))
import build as lib

W, H = 1080, 1920
CUTS = json.load(open(os.path.join(ROOT, "cuts.json")))
DUR = CUTS["duration"]
NANUM = "@font-face{font-family:'Nanum Myeongjo';src:url('assets/fonts/NanumMyeongjo-Bold.ttf') format('truetype');font-weight:700}\n"
lib.FONTS = lib.FONTS + NANUM
NAVY = "linear-gradient(180deg,#07101c 0%,#0d1b2e 100%)"
lib.BASE = lib.BASE.replace("background:linear-gradient(180deg,#F3A784 0%,#E8845A 45%,#fff 110%)","background:linear-gradient(180deg,#d6f3ff 0%,#64d2ff 60%,#2f9ed6 115%)") + "\n.palm{position:absolute;inset:0;background:radial-gradient(60% 35% at 50% 18%,rgba(100,210,255,.16),transparent 70%),repeating-linear-gradient(0deg,rgba(100,210,255,.05) 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,rgba(100,210,255,.05) 0 1px,transparent 1px 48px)}\n.card.term{box-shadow:0 0 0 1px rgba(100,210,255,.35),0 24px 70px rgba(0,0,0,.55),0 0 60px rgba(100,210,255,.12)}\n" + "\n.kserif{font-family:'Nanum Myeongjo','Instrument Serif',serif;font-weight:700}\n"
KO = os.path.join(ROOT, "..", "nick-5plugins-ko", "scenes")

S = {}
def add(sid, start, end, body, css, js, bg):
    S[sid] = (start, round(end - start, 3), lib.scene(sid, body, css, js, bg))
def copy_scene(sid, src_sid, start, end, patch=()):
    html = open(os.path.join(KO, src_sid + ".html")).read().replace(src_sid, sid)
    for a, b in patch:
        assert a in html, (sid, a[:50]); html = html.replace(a, b)
    S[sid] = (start, round(end - start, 3), html)

TERM_CSS = """
.term{background:#141519;color:#c9ccd4;font-family:'JetBrains Mono','Pretendard',monospace}
.tb{height:40px;display:flex;align-items:center;gap:8px;padding:0 18px;border-bottom:1px solid #22252d}.tb span{width:11px;height:11px;border-radius:50%}
.tb span:nth-child(1){background:#E8845A}.tb span:nth-child(2){background:#F5C542}.tb span:nth-child(3){background:#4FC29A}.tb em{font-style:normal;color:#8f95a3;font-size:13px;margin-left:8px}
.body{padding:22px 30px;font-size:25px;line-height:1.7}.l{white-space:nowrap;overflow:hidden}
.o{color:#64d2ff}.g{color:#4FC29A}.dim{color:#8f95a3}.w{color:#fff;font-weight:600}.r{color:#ff6b6b}
"""
TB = lambda t: f'<div class="tb"><span></span><span></span><span></span><em>{t}</em></div>'
CARD = "\n.card{left:50px;right:50px;top:150px;height:540px;border-radius:26px}\n"

# ---------------------------------------------------------------- o00 0–1.58 head copy: ASCII scramble → CLAUDE CODE (reference opening)
copy_scene("o00-claude", "k01-claude", 0.0, 1.58, [("font-size:150px;line-height:.95;color:#E8845A", "font-size:140px;line-height:1.08;color:#E8845A")])

# ---------------------------------------------------------------- o01 1.58–3.78 installer + 1..5 (from ko project)
copy_scene("o01-install", "k02-installer", 1.58, 3.78, [(".nums .n{position:absolute;font-size:110px;color:#BE6C4A;", ".nums .n{position:absolute;font-size:110px;color:#64d2ff;"),("#root{background:#EAE3D4}","#root{background:linear-gradient(180deg,#07101c,#0d1b2e)}"),("stroke:#111;stroke-width:3.5","stroke:#d6f3ff;stroke-width:3.5"),(".bar{width:640px;height:10px;background:#cfc6b4",".bar{width:640px;height:10px;background:#1d2a3e"),("letter-spacing:3px;color:#6a655b}","letter-spacing:3px;color:#8ea2c8}"),(".fill{width:100%;height:100%;background:#E8845A",".fill{width:100%;height:100%;background:#64d2ff")])

# ---------------------------------------------------------------- o02 3.78–6.06 overlay: FREE sticker over person
add("o02-free", 3.78, 6.06, """
<div class="abs stk"><div class="big">₩0</div><div class="sm">5개 전부 무료</div></div>""", """
.stk{left:0;right:0;top:250px;display:flex;flex-direction:column;align-items:center}
.big{background:#64d2ff;color:#07101c;font-weight:900;font-size:150px;line-height:1;padding:20px 60px 26px;border-radius:30px;transform:rotate(-4deg);box-shadow:0 20px 50px rgba(0,0,0,.35)}
.sm{margin-top:22px;background:#111;color:#fff;font-weight:800;font-size:42px;padding:10px 26px;border-radius:14px;transform:rotate(2deg)}
""", """
tl.fromTo('.big',{scale:0,rotation:-25},{scale:1,rotation:-4,duration:.4,ease:'back.out(2.2)'},0);
tl.fromTo('.sm',{opacity:0,y:30},{opacity:1,y:0,duration:.3,ease:'power3.out'},.25);
tl.to('.stk',{y:-10,duration:1.6,ease:'sine.inOut'},.5);
""", "transparent")

# ---------------------------------------------------------------- title scenes (N번째 + icon + name)
import math
SUN = '<svg viewBox="0 0 100 100"><g stroke="#E8845A" stroke-width="5" stroke-linecap="round">' + "".join(
    f'<line x1="50" y1="50" x2="{50+38*math.cos(a*math.pi/6):.1f}" y2="{50+38*math.sin(a*math.pi/6):.1f}"/>' for a in range(12)) + '</g><circle cx="50" cy="50" r="9" fill="#E8845A"/></svg>'
OCTO = '<svg viewBox="0 0 100 100"><path fill="#111" d="M50 6C25 6 5 26 5 51c0 20 13 37 31 43 2 0 3-1 3-2v-8c-13 3-15-6-15-6-2-5-5-7-5-7-4-3 0-3 0-3 5 0 7 5 7 5 4 7 11 5 13 4 0-3 2-5 3-6-10-1-21-5-21-23 0-5 2-9 5-12-1-1-2-6 0-12 0 0 4-1 13 5 4-1 8-2 12-2s8 1 12 2c9-6 13-5 13-5 2 6 1 11 0 12 3 3 5 7 5 12 0 18-11 22-21 23 2 2 3 4 3 8v12c0 1 1 2 3 2 18-6 31-23 31-43C95 26 75 6 50 6z"/></svg>'
AMARK = '<svg viewBox="0 0 200 120"><path d="M60 10 L20 110 H40 L48 88 H92 L100 110 H120 L80 10Z M70 32 L86 72 H54Z" fill="#111"/><path d="M120 10 H142 L182 110 H160Z" fill="#111"/></svg>'
APP_CSS = ".app{width:400px;height:400px;border-radius:92px;background:#fff;box-shadow:0 40px 90px rgba(0,0,0,.18),0 0 0 1px #eee;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px}.app svg{width:150px;height:150px}.app span{font-size:38px;color:#111}.gh span{font-weight:800;font-size:52px}.am svg{width:230px;height:140px}"
def title(sid, start, end, kicker, icon, name, sub=""):
    js = """
tl.fromTo('.k',{opacity:0,y:40,filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.4,ease:'power2.out'},0);
tl.fromTo('.ic',{opacity:0,scale:.6,y:60},{opacity:1,scale:1,y:0,duration:.45,ease:'back.out(1.5)'},.08);
tl.fromTo('.nm',{opacity:0,y:40,filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.4,ease:'power2.out'},.4);
tl.fromTo('.sb',{opacity:0},{opacity:1,duration:.3},.7);
tl.fromTo('.ic',{rotation:0},{rotation:-3,duration:.8,yoyo:true,repeat:1,ease:'sine.inOut'},.5);
"""
    add(sid, start, end, f"""
<div class="abs k kserif grad">{kicker}</div><div class="abs ic">{icon}</div>
<div class="abs nm">{name}</div><div class="abs sb">{sub}</div>""", f"""
.k{{left:0;right:0;top:400px;text-align:center;font-size:104px}}
.ic{{left:0;right:0;top:540px;display:flex;justify-content:center}}
.nm{{left:0;right:0;top:990px;text-align:center;font-family:'Instrument Serif';font-style:italic;font-size:124px;letter-spacing:-3px;background:linear-gradient(180deg,#ffffff,#d6f3ff 45%,#64d2ff 110%);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sb{{left:0;right:0;top:1150px;text-align:center;font-size:30px;color:#8ea2c8;letter-spacing:2px}}
{APP_CSS}""", js, NAVY)

title("o03-title-mem", 6.06, 7.62, "첫 번째", f'<div class="app">{SUN}<span class="mono">claude-mem</span></div>', "claude-mem", "세션 간 기억")
title("o05-title-sp", 12.18, 13.72, "두 번째", f'<div class="app gh">{OCTO}<span>GitHub</span></div>', "superpowers", "계획 먼저, 코드는 나중")
title("o08-title-c7", 22.06, 23.82, "세 번째", f'<div class="app gh">{OCTO}<span>GitHub</span></div>', "Context7", "최신 문서로 코딩")
title("o11-title-fs", 29.6, 30.98, "네 번째", f'<div class="app gh">{OCTO}<span>GitHub</span></div>', "find-skills", "맞는 스킬 자동 설치")
title("o14-title-fd", 36.52, 38.2, "다섯 번째", f'<div class="app am">{AMARK}</div>', "frontend-design", "Anthropic 공식")

# ---------------------------------------------------------------- o04 7.62–10.08 card: claude-mem restores yesterday
add("o04-mem", 7.62, 10.08, '<div class="palm"></div><div class="card term">' + TB("claude — ~/my-site") + """<div class="body">
 <div class="l dim">SessionStart hook · <span class="o">claude-mem</span></div>
 <div class="l"><span class="o">◆</span> <span class="w">Restoring context from 3 past sessions…</span></div>
 <div class="mem"><div class="l"><span class="dim">어제 21:14</span>  로그인 페이지 리팩터 — 폼 검증 추가</div>
 <div class="l"><span class="dim">어제 22:02</span>  결제 모듈 버그 수정 (중복 결제)</div>
 <div class="l"><span class="dim">어제 23:40</span>  다음 할 일: 비밀번호 재설정 메일</div></div>
 <div class="l g">✓ project: my-site · 12 files remembered</div>
 <div class="l"><span class="o">&gt;</span> <span class="w">이어서 하자</span><span class="cur o">▍</span></div></div></div>""",
 TERM_CSS + CARD + """
.mem{margin:12px 0;border-left:3px solid #64d2ff;padding-left:16px;color:#e6e8ee}
.mem .l,.body>.l{opacity:0}
""", """
tl.fromTo('.card',{opacity:0,y:-40},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
qa('.body .l').forEach((l,i)=>tl.fromTo(l,{opacity:0,x:-12},{opacity:1,x:0,duration:.18,ease:'power2.out'},.15+i*.24));
tl.fromTo('.mem',{backgroundColor:'rgba(232,132,90,0)'},{backgroundColor:'rgba(100,210,255,.12)',duration:.3},.9);
tl.fromTo('.cur',{opacity:1},{opacity:0,duration:.001,repeat:13,yoyo:true,repeatDelay:.14},0);
""", NAVY)

# ---------------------------------------------------------------- o06 13.72–18.14 card: superpowers plan → ask → build
add("o06-sp", 13.72, 18.14, '<div class="palm"></div><div class="card term">' + TB("claude — superpowers") + """<div class="body">
 <div class="l"><span class="o">&gt;</span> <span class="w typed">로그인 페이지 만들어줘</span></div>
 <div class="l s1 dim">⏺ superpowers:brainstorming — 바로 코드 안 짬</div>
 <div class="l s2"><span class="o">📝</span> <span class="w">plan.md</span> <span class="dim">— 4단계 계획 작성</span></div>
 <div class="q s3"><div class="l w">? 로그인 방식은 어떻게 할까요?</div><div class="l"><span class="o">❯ 1.</span> 이메일 + 비밀번호</div><div class="l dim">  2. 구글 소셜 로그인</div></div>
 <div class="l s4 g">✓ 승인됨 → 1/4 단계 구현 시작</div></div></div>""",
 TERM_CSS + CARD + """
.typed{display:inline-block;clip-path:inset(0 100% 0 0)}
.q{margin:12px 0;border:2px solid #F5C542;border-radius:12px;padding:10px 16px;background:rgba(245,197,66,.06)}
.s1,.s2,.s3,.s4{opacity:0}
""", """
tl.fromTo('.card',{opacity:0,y:-40},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.typed',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.6,ease:'steps(12)'},.1);
tl.fromTo('.s1',{opacity:0,x:-12},{opacity:1,x:0,duration:.2},.9);
tl.fromTo('.s2',{opacity:0,x:-12},{opacity:1,x:0,duration:.2},2.0);
tl.fromTo('.s3',{opacity:0,scale:.92},{opacity:1,scale:1,duration:.3,ease:'back.out(1.8)'},2.95);
tl.fromTo('.s3',{boxShadow:'0 0 0 0 rgba(245,197,66,0)'},{boxShadow:'0 0 0 8px rgba(245,197,66,.25)',duration:.25,yoyo:true,repeat:1},3.25);
tl.fromTo('.s4',{opacity:0,x:-12},{opacity:1,x:0,duration:.2},3.85);
""", NAVY)

# ---------------------------------------------------------------- o09 23.82–29.6 card: old docs error → Context7 latest
add("o09-c7", 23.82, 29.6, '<div class="palm"></div><div class="card term ed">' + TB("app/login/page.tsx") + """<div class="body">
 <div class="tag old">📚 참고 문서: Next.js <b>v12</b> (2022)</div><div class="tag new">📚 context7 · Next.js <b>v15</b> (latest)</div>
 <div class="l"><span class="dim">1</span>  <span class="o">'use client'</span></div>
 <div class="l"><span class="dim">2</span>  <span class="o">import</span> { useRouter } <span class="o">from</span> <span class="swap"><span class="bad">'next/router'</span><span class="good">'next/navigation'</span></span></div>
 <div class="l"><span class="dim">3</span>  </div>
 <div class="l"><span class="dim">4</span>  <span class="o">export default function</span> <span class="w">Login</span>() {</div>
 <div class="l"><span class="dim">5</span>    <span class="o">const</span> router = useRouter()</div>
 <div class="err">✗ Error: NextRouter was not mounted.</div><div class="ok">✓ Compiled successfully</div></div></div>""",
 TERM_CSS + CARD + """
.ed .body{position:relative;padding-top:74px}
.tag{position:absolute;left:28px;top:18px;font-size:16px;padding:6px 14px;border-radius:8px}
.tag.old{background:#3a1f1f;color:#ff9b9b}.tag.new{background:#173226;color:#7be3b5;opacity:0}
.swap{position:relative;display:inline-block}.bad{color:#ff6b6b;text-decoration:wavy underline #ff6b6b}.good{position:absolute;left:0;top:0;color:#4FC29A;white-space:nowrap;opacity:0}
.err,.ok{position:absolute;left:28px;right:28px;bottom:-60px;padding:10px 16px;border-radius:10px;font-size:18px}
.err{background:#3a1f1f;color:#ff8080;opacity:0}.ok{background:#173226;color:#7be3b5;opacity:0}
""", """
tl.fromTo('.card',{opacity:0,y:-40},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
qa('.body > .l').forEach((l,i)=>tl.fromTo(l,{opacity:0},{opacity:1,duration:.08},.15+i*.12));
tl.fromTo('.tag.old',{opacity:0,y:-8},{opacity:1,y:0,duration:.25},.6);
tl.fromTo('.err',{opacity:0,y:10},{opacity:1,y:0,duration:.25,ease:'back.out(2)'},1.9);
tl.fromTo('.card',{x:0},{x:7,duration:.04,repeat:7,yoyo:true},1.9);
// 27.18 root → local 3.36: switch to latest docs
tl.to('.tag.old',{opacity:0,duration:.15},3.4).fromTo('.tag.new',{opacity:0,y:-8},{opacity:1,y:0,duration:.25},3.45);
tl.to('.bad',{opacity:0,duration:.15},3.9).fromTo('.good',{opacity:0,x:10},{opacity:1,x:0,duration:.25},3.95);
tl.to('.err',{opacity:0,duration:.15},4.4).fromTo('.ok',{opacity:0,y:10},{opacity:1,y:0,duration:.25,ease:'back.out(2)'},4.45);
""", NAVY)

# ---------------------------------------------------------------- o12 30.98–35.0 card: find-skills search → install
add("o12-fs", 30.98, 35.0, '<div class="palm"></div><div class="card term">' + TB("claude — find-skills") + """<div class="body">
 <div class="l"><span class="o">&gt;</span> <span class="w typed">쇼핑몰 랜딩페이지 만들고 싶어</span></div>
 <div class="l s1">⟳ 스킬 라이브러리 검색 <span class="bar"><i></i></span> <span class="cnt dim">0</span></div>
 <div class="l s2 dim">  checking: <span class="nm">seo-audit</span></div>
 <div class="l s3 o">● 찾음: landing-page-builder · ecommerce-copy</div>
 <div class="l s4">⤓ 설치 중 <span class="bar b2"><i></i></span> <span class="pc dim">0%</span></div>
 <div class="l s5 g">✓ 스킬 2개 설치 완료 — 바로 사용 가능</div></div></div>""",
 TERM_CSS + CARD + """
.typed{display:inline-block;clip-path:inset(0 100% 0 0)}
.s1,.s2,.s3,.s4,.s5{opacity:0}
.bar{display:inline-block;width:260px;height:8px;background:#2a2d36;border-radius:4px;overflow:hidden;vertical-align:middle}.bar i{display:block;height:100%;width:100%;background:#64d2ff;transform-origin:left;transform:scaleX(0)}
""", """
tl.fromTo('.card',{opacity:0,y:-40},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.typed',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.6,ease:'steps(15)'},.1);
tl.fromTo('.s1',{opacity:0},{opacity:1,duration:.1},.9).fromTo('.s2',{opacity:0},{opacity:1,duration:.1},1.0);
tl.fromTo('.s1 .bar i',{scaleX:0},{scaleX:1,duration:1.1,ease:'power1.inOut'},.95);
const cnt=q('.cnt');tl.fromTo({v:0},{v:0},{v:100000,duration:1.1,ease:'power1.inOut',onUpdate:function(){cnt.textContent=Math.round(this.targets()[0].v).toLocaleString()+'개'}},.95);
const names=['seo-audit','copy-rewriter','stripe-checkout','hero-section','ecommerce-copy','landing-page-builder'];const nm=q('.nm');
tl.fromTo({i:0},{i:0},{i:names.length-1,duration:1.0,ease:'none',onUpdate:function(){nm.textContent=names[Math.round(this.targets()[0].i)]}},1.0);
tl.fromTo('.s3',{opacity:0,x:-12},{opacity:1,x:0,duration:.2},1.45);
tl.fromTo('.s4',{opacity:0},{opacity:1,duration:.1},2.72);
tl.fromTo('.b2 i',{scaleX:0},{scaleX:1,duration:.9,ease:'power1.inOut'},2.75);
const pc=q('.pc');tl.fromTo({v:0},{v:0},{v:100,duration:.9,ease:'power1.inOut',onUpdate:function(){pc.textContent=Math.round(this.targets()[0].v)+'%'}},2.75);
tl.fromTo('.s5',{opacity:0,x:-12},{opacity:1,x:0,duration:.2},3.7);
""", NAVY)

# ---------------------------------------------------------------- o15 38.2–39.8 Anthropic official (from ko project)
copy_scene("o15-anthropic", "k14-anthropic", 38.2, 39.8, [
    ("#root{background:#ffffff}","#root{background:linear-gradient(180deg,#07101c,#0d1b2e)}"),('fill="#111"','fill="#fff"'),("color:#111}","color:#fff}"),
    ("tl.fromTo('.wm',{opacity:0,letterSpacing:'30px'},{opacity:1,letterSpacing:'10px',duration:.5,ease:'power2.out'},1.2);",
     "tl.fromTo('.wm',{opacity:0,letterSpacing:'30px'},{opacity:1,letterSpacing:'10px',duration:.5,ease:'power2.out'},.45);")])

# ---------------------------------------------------------------- o16 39.8–42.52 samey AI sites grid
def site(i):
    return f"""<div class="st s{i}"><div class="nav"><b>◆ Nova{['AI','ly','Flow','Labs','Hub','Gen'][i]}</b><span>Features</span><span>Pricing</span><em>Get started</em></div>
 <div class="hero"><div class="pill">✨ Powered by AI</div><div class="h">Build the future<br>with AI</div><div class="p">The all-in-one platform to supercharge your workflow.</div><div class="btn">Get started →</div></div>
 <div class="feat"><i></i><i></i><i></i></div></div>"""
add("o16-samey", 39.8, 42.52, '<div class="abs grid">' + "".join(site(i) for i in range(6)) + '</div>', """
.grid{left:40px;right:40px;top:150px;display:grid;grid-template-columns:1fr 1fr;gap:26px}
.st{height:330px;border-radius:18px;overflow:hidden;background:#0d0b1a;box-shadow:0 20px 40px rgba(0,0,0,.25);position:relative}
.nav{display:flex;gap:14px;align-items:center;padding:12px 16px;font-size:11px;color:#b9b3d6}.nav b{color:#fff;font-size:13px;margin-right:auto}.nav em{font-style:normal;background:#7c5cff;color:#fff;padding:4px 10px;border-radius:12px}
.hero{text-align:center;padding:14px 18px;background:radial-gradient(60% 70% at 50% 0%,rgba(124,92,255,.55),transparent 70%)}
.pill{display:inline-block;font-size:10px;color:#d9d0ff;border:1px solid #5b47c9;border-radius:10px;padding:3px 8px}
.h{font-size:30px;font-weight:800;color:#fff;line-height:1.05;margin-top:8px;background:linear-gradient(90deg,#fff,#b9a6ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.p{font-size:10px;color:#a79fc9;margin-top:6px}.btn{display:inline-block;margin-top:10px;background:linear-gradient(90deg,#7c5cff,#b05cff);color:#fff;font-size:11px;padding:6px 14px;border-radius:14px}
.feat{display:flex;gap:10px;padding:0 18px}.feat i{flex:1;height:44px;border-radius:8px;background:#1b1733;border:1px solid #2c2550}
""", """
qa('.st').forEach((s,i)=>tl.fromTo(s,{opacity:0,y:40,scale:.9},{opacity:1,y:0,scale:1,duration:.3,ease:'power3.out'},i*.12));
tl.to('.grid',{scale:1.04,duration:2.6,ease:'none',transformOrigin:'50% 30%'},0);
""", NAVY)

# ---------------------------------------------------------------- o17 42.52–44.02 before → after (distinctive design)
add("o17-distinct", 42.52, 44.02, """
<div class="abs before"><div class="nav"><b>◆ NovaAI</b></div><div class="h">Build the future<br>with AI</div><div class="btn">Get started →</div></div>
<div class="abs after"><div class="topbar"><span>BREW LAB</span><span>SEOUL · EST 2026</span></div>
 <div class="big">Slow<br>coffee,<br><i>fast</i><br>mornings.</div>
 <div class="side"><div class="n">01</div><div class="t">싱글 오리진 원두를 매주 새로 볶아 보냅니다.</div><div class="cta">구독 시작하기 ↗</div></div>
 <div class="stamp2">NO.<br>24</div></div>
<div class="abs wipe"></div>""", """
.before,.after{left:40px;right:40px;top:150px;height:1060px;border-radius:26px;overflow:hidden}
.before{background:radial-gradient(60% 50% at 50% 0%,rgba(124,92,255,.6),#0d0b1a 75%);text-align:center;color:#fff}
.before .nav{padding:26px;text-align:left;font-size:22px}.before .h{margin-top:220px;font-size:84px;font-weight:800;line-height:1.05}.before .btn{display:inline-block;margin-top:40px;background:#7c5cff;padding:16px 34px;border-radius:30px;font-size:26px}
.after{background:#F1E9DA;color:#1a1410;clip-path:inset(0 100% 0 0)}
.topbar{display:flex;justify-content:space-between;padding:26px 34px;font-size:20px;letter-spacing:4px;font-weight:700;border-bottom:3px solid #1a1410}
.big{position:absolute;left:34px;top:110px;font-family:'Instrument Serif';font-size:190px;line-height:.86;letter-spacing:-6px}
.big i{color:#D2451E}
.side{position:absolute;right:34px;bottom:40px;width:330px}.side .n{font-family:'Instrument Serif';font-size:90px;color:#D2451E;line-height:1}.side .t{font-size:24px;line-height:1.45;margin-top:10px;font-weight:600}.side .cta{margin-top:20px;display:inline-block;border:3px solid #1a1410;padding:12px 20px;font-weight:800;font-size:22px}
.stamp2{position:absolute;right:50px;top:130px;width:150px;height:150px;border-radius:50%;background:#D2451E;color:#F1E9DA;font-weight:900;font-size:34px;display:grid;place-items:center;text-align:center;line-height:1}
.wipe{top:150px;height:1060px;left:40px;width:14px;background:#F5C542;opacity:0;border-radius:7px}
""", """
tl.fromTo('.before',{scale:.96,opacity:0},{scale:1,opacity:1,duration:.2},0);
tl.fromTo('.after',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.5,ease:'power3.inOut'},.35);
tl.fromTo('.wipe',{opacity:1,x:0},{x:986,duration:.5,ease:'power3.inOut'},.35).to('.wipe',{opacity:0,duration:.1},.85);
tl.fromTo('.big',{y:40,opacity:0},{y:0,opacity:1,duration:.45,ease:'power3.out'},.55);
tl.fromTo('.stamp2',{scale:0,rotation:-40},{scale:1,rotation:-12,duration:.4,ease:'back.out(2)'},.8);
""", NAVY)

# ---------------------------------------------------------------- o18 44.02–46.28 card: 5-plugin checklist
PL = [("claude-mem", "기억"), ("superpowers", "계획"), ("Context7", "최신 문서"), ("find-skills", "스킬 찾기"), ("frontend-design", "디자인")]
rows = "".join(f'<div class="row"><span class="ck">✓</span><span class="n">{i+1}</span><b>{a}</b><em>{b}</em></div>' for i, (a, b) in enumerate(PL))
add("o18-list", 44.02, 46.28, '<div class="palm"></div><div class="card lst"><div class="hd">클로드 코드 필수 플러그인 <span>5</span></div>' + rows + '</div>', CARD + """
.lst{background:#0f1a2b;box-shadow:0 0 0 1px rgba(100,210,255,.35),0 30px 80px rgba(0,0,0,.5);padding:30px 40px}
.hd{font-size:34px;font-weight:900;color:#fff;margin-bottom:18px}.hd span{display:inline-grid;place-items:center;width:48px;height:48px;border-radius:12px;background:#64d2ff;color:#fff;margin-left:8px}
.row{display:flex;align-items:center;gap:18px;height:78px;border-top:1px solid #1d2a3e;font-size:30px}
.ck{width:40px;height:40px;border-radius:50%;background:#4FC29A;color:#fff;display:grid;place-items:center;font-size:22px;font-weight:900}
.n{color:#8ea2c8;font-weight:700;width:24px}.row b{font-family:'JetBrains Mono';font-weight:700;color:#fff}.row em{font-style:normal;margin-left:auto;color:#8ea2c8;font-size:24px}
""", """
tl.fromTo('.card',{opacity:0,y:-40},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
qa('.row').forEach((r,i)=>{tl.fromTo(r,{opacity:0,x:-20},{opacity:1,x:0,duration:.22,ease:'power3.out'},.2+i*.2);
 tl.fromTo(r.querySelector('.ck'),{scale:0},{scale:1,duration:.25,ease:'back.out(2.5)'},.3+i*.2)});
""", NAVY)

# ---------------------------------------------------------------- o19 46.28–48.36 overlay: comment box
add("o19-comment", 46.28, DUR, """
<div class="abs cm"><div class="av">나</div><div class="in">댓글에 <b class="kw"></b><span class="cur">▍</span></div><div class="send">게시</div></div>""", """
.cm{left:60px;right:60px;top:230px;height:120px;background:#fff;border-radius:60px;display:flex;align-items:center;gap:20px;padding:0 20px;box-shadow:0 24px 60px rgba(0,0,0,.35)}
.av{width:80px;height:80px;border-radius:50%;background:#64d2ff;color:#fff;font-weight:900;font-size:34px;display:grid;place-items:center}
.in{flex:1;font-size:44px;font-weight:700;color:#111}.kw{color:#64d2ff}.cur{color:#64d2ff;font-weight:400}
.send{font-size:34px;font-weight:800;color:#3897f0}
""", """
tl.fromTo('.cm',{opacity:0,y:-60,scale:.92},{opacity:1,y:0,scale:1,duration:.35,ease:'back.out(1.6)'},0);
const kw=q('.kw');const word='"플러그인"';
tl.fromTo({n:0},{n:0},{n:word.length,duration:.6,ease:'steps('+word.length+')',onUpdate:function(){kw.textContent=word.slice(0,Math.round(this.targets()[0].n))}},.4);
tl.fromTo('.cur',{opacity:1},{opacity:0,duration:.001,repeat:11,yoyo:true,repeatDelay:.14},0);
tl.fromTo('.send',{scale:1},{scale:1.2,duration:.15,yoyo:true,repeat:1},1.3);
""", "transparent")

# ================================================================ host
# camera layouts: (time, mode, zoom, tween_seconds)   mode: card | full | hide
CAM = [(0.0, "card", 1.0, 0), (1.58, "hide", 1, 0), (3.78, "full", 1.12, 0), (6.06, "hide", 1, 0),
       (7.62, "card", 1.0, 0), (10.08, "full", 1.18, .3), (12.18, "hide", 1, 0), (13.72, "card", 1.0, 0),
       (18.14, "full", 1.0, 0), (20.82, "full", 1.2, .18), (22.06, "hide", 1, 0), (23.82, "card", 1.0, 0),
       (27.18, "card", 1.06, 0), (29.6, "hide", 1, 0), (30.98, "card", 1.0, 0), (35.0, "full", 1.15, .3),
       (36.52, "hide", 1, 0), (44.02, "card", 1.0, 0), (46.28, "full", 1.1, 0)]
# source is 1920x1080, face ≈ (1010, 430)
FACE = (1010, 430)
def geo(mode):
    if mode == "card":   # box 1000x1160 at (40,760); video height 1160
        box = dict(left=40, top=760, width=1000, height=1160, borderRadius="80px 80px 0 0")
        s = 1160 / 1080; img = dict(width=1920 * s, height=1160, left=500 - FACE[0] * s, top=0)
        org = (500, FACE[1] * s)
    else:                # full frame; video height 1920
        box = dict(left=0, top=0, width=1080, height=1920, borderRadius="0px")
        s = 1920 / 1080; img = dict(width=1920 * s, height=1920, left=540 - FACE[0] * s, top=-40)
        org = (540, FACE[1] * s - 40)
    return box, img, org

cam_js = []
for t, mode, z, tw in CAM:
    if mode == "hide":
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:0}},{t});"); continue
    box, img, org = geo(mode)
    fmt = lambda d: "{" + ",".join(f"{k}:{json.dumps(round(v,1) if isinstance(v,float) else v)}" for k, v in d.items()) + "}"
    zo = f"{{scale:{z},transformOrigin:'{org[0]:.0f}px {org[1]:.0f}px'}}"
    if tw:
        cam_js.append(f"tl.to('#camBox',{{...{fmt(box)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camImg',{{...{fmt(img)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camZoom',{{...{zo},duration:{tw},ease:'power2.inOut'}},{t});")
    else:
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:1,...{fmt(box)}}},{t});tl.set('#camImg',{fmt(img)},{t});tl.set('#camZoom',{zo},{t});")
# slow drift inside each visible hold (keeps talking head alive)
for i, (t, mode, z, tw) in enumerate(CAM):
    if mode == "hide": continue
    nxt = CAM[i + 1][0] if i + 1 < len(CAM) else DUR
    if nxt - t > .8 and not (i + 1 < len(CAM) and CAM[i + 1][3]):
        cam_js.append(f"tl.to('#camZoom',{{scale:{z*1.035:.3f},duration:{nxt-t-.05:.2f},ease:'none'}},{t+.01:.2f});")

# captions: (start, end, text, accent, style)   style auto from camera mode unless given
C_ = [
 (0.0, .6, "클로드 코드", "클로드 코드"), (.6, 1.58, "처음 쓰시는 분들", ""), (1.58, 2.6, "이 5개부터", "5개", "serifD"), (2.6, 3.78, "깔고 시작하세요", "", "serifD"),
 (3.78, 4.68, "다 무료고요", "무료"), (4.68, 6.06, "저도 이렇게 쓰고 있습니다", ""),
 (7.62, 8.54, "어제 한 작업을", "어제 한 작업"), (8.54, 9.36, "기억합니다", "기억"),
 (9.36, 10.08, "내 프로젝트", ""), (10.08, 10.94, "매번 다시", ""), (10.94, 12.18, "설명 안 해도 되거든요", "설명 안 해도"),
 (13.76, 14.4, "시키자마자", ""), (14.4, 15.72, "코드를 막 짜는 게 아니라", "코드를 막"), (15.72, 16.7, "계획 세우고", "계획"),
 (16.7, 17.58, "저한테 물어보고", "물어보고"), (17.58, 18.14, "만들어요", ""),
 (18.2, 19.66, "AI한테 끌려가면 안 된다고", "끌려가면"), (19.66, 20.82, "늘 말씀드리죠", ""), (20.82, 22.06, "이게 그걸 막아줍니다", "막아줍니다"),
 (24.0, 25.5, "클로드가 옛날 문서 보고", "옛날 문서"), (25.5, 27.18, "짜서 오류 내는 게 많거든요", "오류"),
 (27.26, 28.72, "이건 최신 문서를 보고", "최신 문서"), (28.72, 29.6, "짜게 됩니다", ""),
 (31.1, 32.42, "만들려는 거 말만 하면", "말만"), (32.42, 33.7, "맞는 스킬을 찾아서", "맞는 스킬"), (33.7, 35.0, "설치까지 해줘요", "설치까지"),
 (35.0, 36.52, "스킬이 뭔지 몰라도 됩니다", "몰라도"),
 (38.24, 39.8, "앤트로픽 공식이고요", "앤트로픽 공식", "serifD"), (39.8, 41.18, "AI로 만든 사이트", "", "serifD"), (41.18, 42.52, "다 비슷하게 생겼잖아요", "비슷하게", "serifD"),
 (42.52, 44.02, "이거 켜면 확 달라집니다", "확 달라집니다", "serifD"),
 (44.02, 45.26, "명령어 5개", "5개"), (45.26, 46.28, "정리해놨습니다", ""),
 (46.28, 46.68, "댓글에", ""), (46.68, 47.56, "\"플러그인\"", "\"플러그인\""), (47.56, DUR, "남겨주세요", ""),
]
def mode_at(t):
    m = CAM[0][1]
    for tt, mm, *_ in CAM:
        if tt <= t + 1e-6: m = mm
    return m
CAPS = []
for c in C_:
    s, e, txt, acc = c[:4]
    st = "sans"
    m = mode_at(s)
    y = 712 if m == "card" else 1373
    CAPS.append([s, round(e, 3), txt, st, y, acc])

scene_divs = "".join(f'<div id="{sid}" class="{"ovl" if sid in ("o02-free","o19-comment") else "scn"}" data-composition-id="{sid}" data-composition-src="scenes/{sid}.html" data-start="{st}" data-duration="{du}" data-track-index="{2 if sid in ("o02-free","o19-comment") else 0}" data-width="{W}" data-height="{H}"></div>\n' for sid, (st, du, _) in S.items())

HTML = f"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width={W},height={H}">
<title>클로드 코드 플러그인 5개 — Owen 스타일</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
{lib.FONTS}
body{{margin:0;background:#000;font-family:'Pretendard',sans-serif}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;background:{lib.C['light']}}}
#root *{{box-sizing:border-box}}
.scn{{position:absolute;inset:0;z-index:1}} .ovl{{position:absolute;inset:0;z-index:3}}
#camBox{{position:absolute;overflow:hidden;z-index:2;background:#111}}
#camZoom{{position:absolute;inset:0}}
#camImg{{position:absolute}}
#person{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#captions{{position:absolute;inset:0;z-index:4;pointer-events:none}}
.caption{{position:absolute;left:0;right:0;text-align:center;white-space:pre-line}}
.caption span{{display:inline-block;max-width:960px}}
.sans span{{font-family:'Pretendard';font-weight:800;font-size:60px;line-height:1.05;color:#fff;letter-spacing:-1px;white-space:nowrap;text-shadow:0 2px 8px #000,0 0 3px #000,0 0 3px #000}}
.sans b{{font-weight:inherit;color:#64d2ff}}
.sans b.warn{{color:#ff3b30}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{scene_divs}
<div id="camBox"><div id="camZoom"><div id="camImg"><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1" muted></video></div></div></div>
<div id="captions"></div>
<audio id="voice" src="assets/mix.m4a" data-start="0" data-duration="{DUR}" data-track-index="9"></audio>
</div>
<script>
const WARN=['끌려가면','옛날 문서','오류'];
const CAPS={json.dumps(CAPS, ensure_ascii=False)};
const host=document.getElementById('captions');
const esc=(t)=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;');
CAPS.forEach((c,i)=>{{const [s,e,text,style,y,acc]=c;const d=document.createElement('div');d.id='cap-'+i;d.className='clip caption '+style+(text.includes('플러그인')?' cta':'');
 d.dataset.start=s;d.dataset.duration=(e-s).toFixed(3);d.dataset.trackIndex=8;d.style.top=y+'px';
 let h=esc(text);if(acc)h=h.replace(esc(acc),'<b'+(WARN.includes(acc)?' class="warn"':'')+'>'+esc(acc)+'</b>');d.innerHTML='<span>'+h+'</span>';host.appendChild(d);const sp=d.firstChild;if(sp.scrollWidth>930)sp.style.fontSize=Math.floor(60*930/sp.scrollWidth)+'px'}});
const tl=gsap.timeline({{paused:true}});
CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');
 if(false)tl.fromTo(el,{{opacity:0,y:16,filter:'blur(8px)'}},{{opacity:1,y:0,filter:'blur(0px)',duration:.2,ease:'power2.out'}},c[0]);
 else tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);}});
{chr(10).join(cam_js)}
window.__timelines["main"]=tl;
</script></body></html>
"""
os.makedirs(os.path.join(ROOT, "scenes"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "scenes")):
    os.remove(os.path.join(ROOT, "scenes", f))
for sid, (st, du, html) in S.items():
    open(os.path.join(ROOT, "scenes", sid + ".html"), "w").write(html)
open(os.path.join(ROOT, "index.html"), "w").write(HTML)
print(f"wrote {len(S)} scenes, {len(CAPS)} captions, dur {DUR}s")
