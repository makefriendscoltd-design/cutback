#!/usr/bin/env python3
"""Korean remake of nick_saraev reel Ddjfv-WP9yo ("5 free Claude Code plugins").
All non-person graphics rebuilt as HyperFrames scenes; captions translated to Korean.
Shares the scene library of ../nick-plugins-mg/build.py.  Run: python3 build2.py
"""
import os, sys, json
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "nick-plugins-mg"))
import build as lib

W, H = lib.W, lib.H
DUR = 57.52
NANUM = "@font-face{font-family:'Nanum Myeongjo';src:url('assets/fonts/NanumMyeongjo-Bold.ttf') format('truetype');font-weight:700}\n"
lib.FONTS = lib.FONTS + NANUM
lib.BASE = lib.BASE + "\n.kserif{font-family:'Nanum Myeongjo','Instrument Serif',serif;font-style:italic;font-weight:700}\n"
INV = lib.invader_html
INV_CSS = lib.INV_CSS

S = {}  # sid -> (start, dur, html)
def add(sid, start, dur, body, css, js, bg):
    S[sid] = (start, dur, lib.scene(sid, body, css, js, bg))
def reuse(new_sid, old_sid, start, dur, patch=()):
    html = lib.SCENES[old_sid][2].replace(old_sid, new_sid)
    for a, b in patch:
        assert a in html, (new_sid, a[:40])
        html = html.replace(a, b)
    S[new_sid] = (start, dur, html)

# ---------------------------------------------------------------- k01 0–1.13 dark: mascot + scramble → CLAUDE CODE
add("k01-claude", 0.0, 1.13, """
<div class="abs mas">""" + INV(cell=14) + """<div class="sign"></div></div>
<div class="abs top"><div id="k01-scr" class="mono"></div>
 <div id="k01-word" class="pix"><div>CLAUDE</div><div>CODE</div></div></div>
""", """
.mas{left:0;right:0;top:100px;display:flex;justify-content:center}
.sign{position:absolute;right:calc(50% - 120px);top:-20px;width:6px;height:60px;background:#E8845A;transform:rotate(20deg)}
.top{left:0;right:0;top:0;height:900px}
#k01-scr{position:absolute;left:90px;right:90px;top:280px;height:400px;color:#E8845A;font-size:26px;line-height:1.35;white-space:pre;letter-spacing:1px;opacity:.9;overflow:hidden}
#k01-scr span{display:block;position:absolute;inset:0;opacity:0}
.pix{position:absolute;left:0;right:0;top:270px;text-align:center;font-family:'Silkscreen';font-weight:700;font-size:150px;line-height:.95;color:#E8845A;letter-spacing:-2px}
.pix div{clip-path:inset(0 0 100% 0)}
""" + INV_CSS, """
const chars='|<>29GNU:!~18FMT_3AHOVcjq%^)/07ELSZgnu@\\\\(;?bi=+.,-Yfm$';
const r=rng(3); const scr=q('#k01-scr');
for(let f=0;f<7;f++){let s='';for(let l=0;l<10;l++){let line='';for(let c=0;c<34;c++){line+=r()<.72?chars[Math.floor(r()*chars.length)]:' ';}s+=line+'\\n';}
 const sp=document.createElement('span');sp.textContent=s;scr.appendChild(sp);}
qa('#k01-scr span').forEach((sp,i)=>{tl.fromTo(sp,{opacity:0},{opacity:1,duration:.001},i*.07).to(sp,{opacity:0,duration:.001},(i+1)*.07-.001)});
tl.fromTo(scr,{opacity:.9},{opacity:0,duration:.15},.3);
tl.fromTo('.pix div',{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)',duration:.22,ease:'steps(6)',stagger:.1},.3);
tl.fromTo('.mas',{opacity:0,y:-60},{opacity:1,y:0,duration:.35,ease:'bounce.out'},0);
""", lib.C["navy"])

# ---------------------------------------------------------------- k02 1.13–3.07 beige installer with mascot + 5 numbers
nums = ""
pos = [(150, 300), (330, 230), (520, 200), (700, 230), (880, 300)]
paths = ["M20 20 L80 85", "M40 15 L60 88", "M50 12 L50 88", "M60 15 L40 88", "M80 20 L20 85"]
heads = ["M62 82 L80 85 L78 66", "M45 76 L60 88 L70 72", "M36 74 L50 88 L64 74", "M30 72 L40 88 L55 76", "M22 66 L20 85 L38 82"]
for i, (x, y) in enumerate(pos):
    nums += f'<div class="n" style="left:{x}px;top:{y}px">{i+1}<svg viewBox="0 0 100 100"><path d="{paths[i]}"/><path d="{heads[i]}"/></svg></div>'
add("k02-installer", 1.13, 1.94, """
<div class="abs box">
 <div class="masw">""" + INV(cell=24) + """<div class="sd"><i></i><span>Plugin</span></div></div>
 <div class="pix">CLAUDE<br>CODE</div><div class="tag mono">PLUGIN</div>
 <div class="stat mono"><span class="msg">DOWNLOADING</span><span class="pct">0%</span></div>
 <div class="bar"><div class="fill"></div></div>
</div>
<div class="abs nums serif">""" + nums + """</div>
""", """
.box{left:0;right:0;top:560px;text-align:center}
.masw{position:relative;width:288px;height:192px;margin:0 auto}
.sd{position:absolute;left:-150px;top:10px;width:150px;height:110px;background:#fff;border:3px solid #111;border-radius:10px 10px 10px 10px;clip-path:polygon(0 0,80% 0,100% 20%,100% 100%,0 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;transform:rotate(-8deg)}
.sd i{width:40px;height:40px;border-radius:50%;background:radial-gradient(circle,#E8845A 30%,transparent 32%),conic-gradient(#E8845A 0 10%,transparent 10% 20%,#E8845A 20% 30%,transparent 30% 40%,#E8845A 40% 50%,transparent 50% 60%,#E8845A 60% 70%,transparent 70% 80%,#E8845A 80% 90%,transparent 90%)}
.sd span{font-size:16px;font-weight:700;color:#111}
.pix{font-family:'Silkscreen';font-size:68px;line-height:.95;color:#E8845A;margin-top:26px}
.tag{display:inline-block;background:#111;color:#EAE3D4;font-size:12px;letter-spacing:3px;padding:3px 10px;margin-top:10px}
.stat{display:flex;justify-content:space-between;width:640px;margin:70px auto 0;font-size:16px;letter-spacing:3px;color:#6a655b}
.bar{width:640px;height:10px;background:#cfc6b4;border-radius:6px;margin:12px auto 0;overflow:hidden}
.fill{width:100%;height:100%;background:#E8845A;transform-origin:left center;transform:scaleX(0)}
.nums .n{position:absolute;font-size:110px;color:#BE6C4A;width:200px;height:200px;line-height:1}
.nums .n svg{position:absolute;left:30px;top:80px;width:150px;height:150px;fill:none;stroke:#111;stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round}
""" + INV_CSS, """
tl.fromTo('.box',{opacity:0,y:30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.masw .inv',{y:0},{y:-8,duration:.3,yoyo:true,repeat:5,ease:'sine.inOut'},.2);
tl.fromTo('.fill',{scaleX:0},{scaleX:1,duration:1.5,ease:'power1.inOut'},.15);
const pct=q('.pct'),msg=q('.msg');
tl.fromTo({v:0},{v:0},{v:100,duration:1.5,ease:'power1.inOut',onUpdate:function(){const v=Math.round(this.targets()[0].v);pct.textContent=v+'%';msg.textContent=v<55?'DOWNLOADING':v<100?'INSTALLING':'INSTALLED'}},.15);
qa('.nums .n').forEach((n,i)=>{tl.fromTo(n,{opacity:0,scale:.6,y:20},{opacity:1,scale:1,y:0,duration:.22,ease:'back.out(2)'},.5+i*.14);
 tl.fromTo(n.querySelectorAll('path'),{strokeDasharray:200,strokeDashoffset:200},{strokeDashoffset:0,duration:.3,ease:'power2.out'},.6+i*.14)});
""", lib.C["beige"])

# ---------------------------------------------------------------- generic "THE Nth + app icon + name" white title scene
SUN = """<svg viewBox="0 0 100 100"><g stroke="#E8845A" stroke-width="5" stroke-linecap="round">""" + "".join(f'<line x1="50" y1="50" x2="{50+38*__import__("math").cos(a*3.14159/6):.1f}" y2="{50+38*__import__("math").sin(a*3.14159/6):.1f}"/>' for a in range(12)) + """</g><circle cx="50" cy="50" r="9" fill="#E8845A"/></svg>"""
OCTO = """<svg viewBox="0 0 100 100"><path fill="#111" d="M50 6C25 6 5 26 5 51c0 20 13 37 31 43 2 0 3-1 3-2v-8c-13 3-15-6-15-6-2-5-5-7-5-7-4-3 0-3 0-3 5 0 7 5 7 5 4 7 11 5 13 4 0-3 2-5 3-6-10-1-21-5-21-23 0-5 2-9 5-12-1-1-2-6 0-12 0 0 4-1 13 5 4-1 8-2 12-2s8 1 12 2c9-6 13-5 13-5 2 6 1 11 0 12 3 3 5 7 5 12 0 18-11 22-21 23 2 2 3 4 3 8v12c0 1 1 2 3 2 18-6 31-23 31-43C95 26 75 6 50 6z"/></svg>"""
def title_scene(sid, start, dur, kicker, icon_html, icon_css, names, name_style="gray", kicker_at=0.0):
    """names: list of (local_time, text) shown cumulatively (last replaces)."""
    spans = "".join(f'<div class="nm n{i}">{t}</div>' for i, (_, t) in enumerate(names))
    js = f"tl.fromTo('.k',{{opacity:0,y:40,filter:'blur(10px)'}},{{opacity:1,y:0,filter:'blur(0px)',duration:.45,ease:'power2.out'}},{kicker_at});\n"
    js += "tl.fromTo('.ic',{opacity:0,scale:.6,y:60},{opacity:1,scale:1,y:0,duration:.5,ease:'back.out(1.5)'},.1);\n"
    for i, (t, _) in enumerate(names):
        js += f"tl.fromTo('.n{i}',{{opacity:0,y:40,filter:'blur(10px)'}},{{opacity:1,y:0,filter:'blur(0px)',duration:.4,ease:'power2.out'}},{t});\n"
        if i > 0:
            js += f"tl.to('.n{i-1}',{{opacity:0,duration:.15}},{t});\n"
    grad = "background:linear-gradient(180deg,#e0e0e0,#9a9a9a 50%,#333 110%)" if name_style == "gray" else "background:linear-gradient(180deg,#F3A784,#E8845A 50%,#c98b6d 110%)"
    add(sid, start, dur, f"""
<div class="abs k kserif grad">{kicker}</div>
<div class="abs ic">{icon_html}</div>
<div class="abs nmw">{spans}</div>
""", f"""
.k{{left:0;right:0;top:420px;text-align:center;font-size:110px;letter-spacing:-2px}}
.ic{{left:0;right:0;top:560px;display:flex;justify-content:center}}
.nmw{{left:0;right:0;top:1000px;height:200px}}
.nm{{position:absolute;left:0;right:0;text-align:center;font-family:'Instrument Serif';font-style:italic;font-size:130px;letter-spacing:-3px;{grad};-webkit-background-clip:text;background-clip:text;color:transparent}}
{icon_css}
""", js, "#ffffff")

APP_CSS = ".app{width:420px;height:420px;border-radius:96px;background:#fff;box-shadow:0 40px 90px rgba(0,0,0,.18),0 0 0 1px #eee;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px}.app svg{width:150px;height:150px}.app span{font-size:40px;color:#111}"
title_scene("k03-title-mem", 4.37, 1.2, "첫 번째", f'<div class="app">{SUN}<span class="mono">claude-mem</span></div>', APP_CSS, [(0.55, "CLAUDE MEM")])
title_scene("k06-title-find", 11.1, 1.67, "두 번째", f'<div class="app gh">{OCTO}<span>GitHub</span></div>', APP_CSS + ".gh span{font-weight:800;font-size:56px}.gh svg{width:170px;height:170px}", [(0.6, "FIND"), (1.0, "FIND-SKILLS")])
title_scene("k09-title-anydoc", 19.5, 1.13, "세 번째", f'<div class="app gh">{OCTO}<span>GitHub</span></div>', APP_CSS + ".gh span{font-weight:800;font-size:56px}.gh svg{width:170px;height:170px}", [(0.5, "ANYDOC")])
title_scene("k13-title-setup", 28.93, 1.07, "네 번째", '<div class="app dark"><div class="pix">CLAUDE<br>CODE</div></div>', APP_CSS + ".dark{background:#1b1d22;box-shadow:0 40px 90px rgba(0,0,0,.35)}.pix{font-family:'Silkscreen';font-size:64px;line-height:.95;color:#E8845A;text-align:center}", [(0.45, "Claude Code Setup")], name_style="orange")

# ---------------------------------------------------------------- k04 5.57–7.57 dark: claude-mem README
LANGS = "zh 中文 · ja 日本語 · pt Português · es Español · de Deutsch · fr Français · ko 한국어 · ru Русский · it Italiano · hi हिन्दी · tr Türkçe · vi Tiếng Việt · nl Nederlands · pl Polski · id Indonesia · ar العربية · sv Svenska · uk Українська · da Dansk · no Norsk"
add("k04-readme", 5.57, 2.0, """
<div class="abs page">
 <div class="tabs"><span class="on">README</span><span>Apache-2.0 license</span><span>Security</span><em>≡</em></div>
 <div class="banner">""" + SUN + """<span class="mono">claude-mem</span></div>
 <div class="langs">""" + LANGS + """</div>
 <div class="desc">Persistent memory compression system built for <u>Claude Code</u>.</div>
 <div class="chips"><span>license Apache-2.0</span><span class="g">build passing</span><span class="b">npm v10.4</span><span class="p">bun ready</span></div>
 <div class="badge">🏆 <em>TRENDSHIFT</em><br>#1 Repository Of The Day</div>
 <div class="imgs"><div class="im term mono"><div>› claude-mem: restoring context</div><div class="c">✓ 3 sessions · 41 observations</div><div class="c">✓ project: agency-site</div><div class="c">✓ files: 12 remembered</div></div>
  <div class="im chart"><svg viewBox="0 0 300 160"><path class="ln" d="M10 150 C60 148 90 140 120 120 S180 70 220 50 S280 20 290 15" fill="none" stroke="#E8845A" stroke-width="3"/></svg></div></div>
 <div class="links"><u>Quick Start</u> · <u>How It Works</u> · <u>Search Tools</u> · <u>Documentation</u> · <u>Configuration</u> · <u>Troubleshooting</u> · <u>License</u></div>
 <p>Claude-Mem seamlessly preserves context across sessions by automatically capturing tool usage, generating semantic summaries and injecting them back.</p>
</div>
""", """
.page{left:70px;right:70px;top:200px;background:#0d1117;border:1px solid #232830;border-radius:14px;padding:22px 28px;color:#c9ccd4;font-size:13px;text-align:center;line-height:1.5}
.tabs{display:flex;gap:22px;font-size:13px;color:#8f95a3;border-bottom:1px solid #232830;padding-bottom:10px;text-align:left}.tabs .on{color:#fff;border-bottom:2px solid #E8845A;padding-bottom:10px;margin-bottom:-11px}.tabs em{margin-left:auto;font-style:normal}
.banner{margin:24px auto 0;width:520px;height:110px;border-radius:12px;background:#5b7fc7;display:flex;align-items:center;justify-content:center;gap:18px;font-size:40px;color:#fff}.banner svg{width:64px;height:64px}
.langs{margin-top:16px;font-size:10px;color:#7aa7ff;line-height:1.7;text-decoration:underline}
.desc{margin-top:16px;font-weight:700;color:#fff;font-size:15px}.desc u{color:#7aa7ff}
.chips{margin-top:12px;display:flex;justify-content:center;gap:6px}.chips span{background:#2b2f36;border-radius:4px;padding:2px 8px;font-size:11px;color:#ddd}.chips .g{background:#2e7d32}.chips .b{background:#1565c0}.chips .p{background:#6a1b9a}
.badge{margin:16px auto 0;width:280px;background:#fff;color:#111;border-radius:10px;padding:8px 14px;font-weight:700;font-size:14px;line-height:1.3}.badge em{font-style:normal;font-size:9px;letter-spacing:2px;color:#666}
.imgs{margin-top:18px;display:flex;gap:14px}.im{flex:1;height:200px;border-radius:8px;background:#161b22;border:1px solid #232830;overflow:hidden}
.term{padding:14px;text-align:left;font-size:11px;color:#fff;line-height:1.8}.term .c{color:#8f95a3}
.chart svg{width:100%;height:100%}
.links{margin-top:16px;font-size:11px;color:#7aa7ff}
p{margin:12px 0 0;font-size:11px;color:#8f95a3}
""", """
tl.fromTo('.page',{opacity:0,y:60},{opacity:1,y:0,duration:.4,ease:'power3.out'},0);
tl.fromTo('.page',{scale:1},{scale:1.05,y:-30,duration:1.8,ease:'power1.inOut',transformOrigin:'50% 30%'},.3);
const ln=q('.ln'),L=ln.getTotalLength();tl.fromTo(ln,{strokeDasharray:L,strokeDashoffset:L},{strokeDashoffset:0,duration:1.2,ease:'power2.out'},.4);
qa('.term div').forEach((d,i)=>tl.fromTo(d,{opacity:0},{opacity:1,duration:.1},.4+i*.25));
tl.fromTo('.badge',{scale:.8},{scale:1,duration:.3,ease:'back.out(2)'},.5);
""", "#0b0d12")

# ---------------------------------------------------------------- k05 7.57–10.33 light th: Star History chart card
add("k05-star", 7.57, 2.76, """
<div class="palm"></div>
<div class="card white"><div class="t">✳ Star History</div><div class="lg"><i></i> Thedotmack/claude-mem</div>
 <svg viewBox="0 0 900 360"><g class="ax" stroke="#333" stroke-width="2"><line x1="90" y1="20" x2="90" y2="300"/><line x1="90" y1="300" x2="870" y2="300"/></g>
  <g class="yl" fill="#666" font-size="16"><text x="40" y="60">80k</text><text x="40" y="130">60k</text><text x="40" y="200">40k</text><text x="40" y="270">20k</text></g>
  <g class="xl" fill="#666" font-size="16"><text x="140" y="330">October</text><text x="450" y="330">2026</text><text x="720" y="330">April</text><text x="440" y="352" font-size="12">Date</text></g>
  <text class="yt" x="20" y="180" fill="#666" font-size="12" transform="rotate(-90 20 180)">GitHub Stars</text>
  <path class="ln" d="M110 298 L200 296 L280 292 L340 280 L400 250 L450 210 L500 170 L540 150 L600 120 L660 100 L720 80 L780 66 L840 58" fill="none" stroke="#E8845A" stroke-width="3"/>
  <g class="dots" fill="#E8845A">""" + "".join(f'<circle cx="{x}" cy="{y}" r="4"/>' for x, y in [(110,298),(200,296),(280,292),(340,280),(400,250),(450,210),(500,170),(540,150),(600,120),(660,100),(720,80),(780,66),(840,58)]) + """</g>
 </svg><div class="src">★ star-history.com</div></div>
""", """
.card.white{background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.12);padding:20px 26px}
.t{text-align:center;font-weight:700;color:#111;font-size:18px}.t::first-letter{color:#E8845A}
.lg{position:absolute;left:70px;top:70px;font-size:12px;color:#333;border:1px solid #ddd;padding:4px 10px;border-radius:4px}.lg i{display:inline-block;width:8px;height:8px;border-radius:50%;background:#E8845A;margin-right:6px}
svg{position:absolute;left:40px;top:90px;width:900px;height:360px}
.src{position:absolute;right:30px;bottom:14px;font-size:12px;color:#888}
.dots circle{transform-origin:center;transform-box:fill-box}
""", """
tl.fromTo('.card',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.ax line',{scaleX:0,scaleY:0},{scaleX:1,scaleY:1,duration:.4,ease:'power2.out',transformOrigin:'left bottom'},.2);
const ln=q('.ln'),L=ln.getTotalLength();tl.fromTo(ln,{strokeDasharray:L,strokeDashoffset:L},{strokeDashoffset:0,duration:1.8,ease:'power1.inOut'},.6);
qa('.dots circle').forEach((c,i)=>tl.fromTo(c,{scale:0},{scale:1,duration:.2,ease:'back.out(2)'},.6+i*.14));
""", lib.C["light"])

# ---------------------------------------------------------------- k07 12.77–16.97 & k08 18.07–19.5 light th: find-skills terminal
TERM_HEAD = '<div class="tb"><span></span><span></span><span></span><em class="mono">agent</em></div>'
add("k07-search", 12.77, 4.2, """
<div class="palm"></div>
<div class="card mono term">""" + TERM_HEAD + """
 <div class="l cmd"><b>$</b> <span class="typed">Build a SaaS website for the agency</span><span class="cur">▍</span></div>
 <div class="l ok">✓ Agent started</div>
 <div class="l scan">⟳ Scanning skill library <span class="bar"><i></i></span><span class="cnt">0 / 100,000</span></div>
 <div class="l chk">[ checking: <span class="nm">copy-rewriter</span> ]</div>
 <div class="l hit">● Match found: saas-website-builder</div>
</div>
""", """
.card.term{top:150px;height:330px;background:#141519;padding:0 0 10px;font-size:19px;color:#c9ccd4;line-height:1.9}
.tb{height:40px;display:flex;align-items:center;gap:8px;padding:0 16px}.tb span{width:11px;height:11px;border-radius:50%;background:#3a3d46}.tb span:nth-child(1){background:#E8845A}.tb span:nth-child(2){background:#F5C542}.tb span:nth-child(3){background:#4FC29A}.tb em{font-style:normal;color:#666;font-size:12px;margin-left:8px}
.l{padding:0 28px;white-space:nowrap}.cmd b{color:#E8845A}.cmd{color:#fff;font-weight:600}
.typed{display:inline-block;clip-path:inset(0 100% 0 0)}.cur{color:#E8845A}
.ok{color:#c9ccd4}.scan{color:#c9ccd4;display:flex;align-items:center;gap:14px}
.bar{display:inline-block;width:360px;height:6px;background:#2a2d36;border-radius:3px;overflow:hidden}.bar i{display:block;height:100%;width:100%;background:#E8845A;transform-origin:left;transform:scaleX(0)}
.cnt{color:#b3b9c4;font-size:15px}.chk{color:#9096a1;font-size:15px}.hit{color:#E8845A;font-weight:600}
""", """
tl.fromTo('.card',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.typed',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.9,ease:'steps(34)'},.1);
tl.fromTo('.cur',{opacity:1},{opacity:0,duration:.001,repeat:15,yoyo:true,repeatDelay:.13},0);
tl.fromTo('.ok',{opacity:0},{opacity:1,duration:.05},1.2);
tl.fromTo('.scan',{opacity:0},{opacity:1,duration:.05},1.5);
tl.fromTo('.bar i',{scaleX:0},{scaleX:1,duration:2.2,ease:'power1.inOut'},1.6);
const cnt=q('.cnt');tl.fromTo({v:0},{v:0},{v:100000,duration:2.2,ease:'power1.inOut',onUpdate:function(){cnt.textContent=Math.round(this.targets()[0].v).toLocaleString()+' / 100,000'}},1.6);
const names=['copy-rewriter','pdf-invoice-generator','domain-checker','landing-hero','seo-audit','stripe-checkout','saas-website-builder'];const nm=q('.nm');
tl.fromTo('.chk',{opacity:0},{opacity:1,duration:.05},1.7);
names.forEach((n,i)=>tl.call(()=>{},[],1.7+i*.3));
tl.fromTo({i:0},{i:0},{i:names.length-1,duration:2.1,ease:'none',onUpdate:function(){nm.textContent=names[Math.round(this.targets()[0].i)]}},1.7);
tl.fromTo('.hit',{opacity:0,x:-10},{opacity:1,x:0,duration:.2},3.85);
""", lib.C["light"])
add("k08-install", 18.07, 1.43, """
<div class="palm"></div>
<div class="card mono term">""" + TERM_HEAD + """
 <div class="l cmd"><b>$</b> Build a SaaS website for the agency</div>
 <div class="l ok">✓ Agent started</div>
 <div class="l scan">✓ Scanning skill library <span class="bar"><i></i></span><span class="cnt">100,000 / 100,000</span></div>
 <div class="l hit">● Match found: saas-website-builder</div>
 <div class="l inst">⤓ Installing skill: saas-website-builder <span class="bar b2"><i></i></span><span class="cnt pc">0%</span></div>
 <div class="l chk"><span class="st">[ Downloading package (1.6 MB)… ]</span></div>
</div>
""", """
.card.term{top:130px;height:370px;background:#141519;padding:0 0 10px;font-size:19px;color:#c9ccd4;line-height:1.9}
.tb{height:40px;display:flex;align-items:center;gap:8px;padding:0 16px}.tb span{width:11px;height:11px;border-radius:50%;background:#3a3d46}.tb span:nth-child(1){background:#E8845A}.tb span:nth-child(2){background:#F5C542}.tb span:nth-child(3){background:#4FC29A}.tb em{font-style:normal;color:#666;font-size:12px;margin-left:8px}
.l{padding:0 28px;white-space:nowrap}.cmd b{color:#E8845A}.cmd{color:#fff;font-weight:600}
.scan,.inst{display:flex;align-items:center;gap:14px}
.bar{display:inline-block;width:300px;height:6px;background:#2a2d36;border-radius:3px;overflow:hidden}.bar i{display:block;height:100%;width:100%;background:#E8845A;transform-origin:left}
.b2 i{transform:scaleX(0)}
.cnt{color:#b3b9c4;font-size:15px}.chk{color:#9096a1;font-size:15px}.hit{color:#E8845A;font-weight:600}
""", """
tl.fromTo('.card',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.inst',{opacity:0},{opacity:1,duration:.05},.2);
tl.fromTo('.b2 i',{scaleX:0},{scaleX:1,duration:1.1,ease:'power1.inOut'},.3);
const pc=q('.pc');tl.fromTo({v:0},{v:0},{v:100,duration:1.1,ease:'power1.inOut',onUpdate:function(){pc.textContent=Math.round(this.targets()[0].v)+'%'}},.3);
const st=q('.st');tl.fromTo('.chk',{opacity:0},{opacity:1,duration:.05},.3);
tl.fromTo({i:0},{i:0},{i:1,duration:.01,onUpdate:function(){st.textContent=this.progress()>.5?'[ Extracting files… ]':'[ Downloading package (1.6 MB)… ]'}},.9);
""", lib.C["light"])

# ---------------------------------------------------------------- k10/k11 anydoc diagram (th card, then full)
def anydoc_body(scale_cls):
    return f"""
<div class="abs dg {scale_cls}">
 <div class="pills"><div class="pl p1"><i style="background:#d04a1c">P</i>PowerPoint</div><div class="pl p2"><i style="background:#1e7145">X</i>Excel</div><div class="pl p3"><i style="background:#2b5797">W</i>Word</div></div>
 <svg class="cv" viewBox="0 0 600 180"><path class="c1" d="M90 0 C90 90 300 60 300 180" stroke="#d04a1c"/><path class="c2" d="M300 0 L300 180" stroke="#1e7145"/><path class="c3" d="M510 0 C510 90 300 60 300 180" stroke="#2b5797"/></svg>
 <div class="doc"><div class="dh mono">report.md <em>MARKDOWN</em></div><div class="dc mono">
  <div># Q3 review</div><div>&nbsp;</div><div>## Highlights</div><div>- Revenue up 12%</div><div>- 3 new accounts</div><div>&nbsp;</div><div>| Region | Revenue |</div><div>| --- | --- |</div><div>| EMEA | $1.2M |</div></div></div>
</div>"""
ANYDOC_CSS = """
.dg{left:0;right:0;display:flex;flex-direction:column;align-items:center}
.pills{display:flex;gap:40px}.pl{display:flex;align-items:center;gap:8px;border:1.5px solid #333;border-radius:8px;padding:8px 16px;font-size:20px;font-weight:600;color:#111;background:#fff}
.pl i{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:5px;color:#fff;font-size:14px;font-style:normal;font-weight:800}
.cv{width:600px;height:180px}.cv path{fill:none;stroke-width:2.5;stroke-dasharray:8 6}
.doc{width:360px;min-height:300px;border:1.5px solid #333;border-radius:14px;background:#fff;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.08)}
.dh{display:flex;justify-content:space-between;align-items:center;padding:8px 14px;font-size:14px;color:#111;border-bottom:1px solid #eee}.dh em{font-style:normal;background:#111;color:#fff;font-size:9px;letter-spacing:2px;padding:2px 6px;border-radius:3px}
.dc{padding:14px;font-size:15px;color:#111;line-height:1.7}.dc div{clip-path:inset(0 100% 0 0)}
"""
ANYDOC_JS = """
const at=(t)=>Math.max(0,START+t);
qa('.pl').forEach((p,i)=>tl.fromTo(p,{opacity:0,y:-20,scale:.8},{opacity:1,y:0,scale:1,duration:.3,ease:'back.out(2)'},at(i*.25)));
qa('.cv path').forEach((p,i)=>{const L=p.getTotalLength();tl.fromTo(p,{strokeDasharray:'8 6',strokeDashoffset:L},{strokeDashoffset:0,duration:.6,ease:'power2.inOut'},at(.5+i*.2))});
tl.fromTo('.doc',{opacity:0,scale:.9},{opacity:1,scale:1,duration:.3,ease:'power3.out'},at(1.0));
qa('.dc div').forEach((d,i)=>tl.fromTo(d,{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.25,ease:'steps(12)'},at(1.2+i*.15)));
"""
add("k10-anydoc-th", 20.63, 2.64, '<div class="palm"></div>' + anydoc_body("th"), ANYDOC_CSS + ".dg.th{top:150px;transform:scale(.8);transform-origin:top center}", "const START=0.4;" + ANYDOC_JS, lib.C["light"])
add("k11-anydoc-full", 23.27, 2.16, anydoc_body("full"), ANYDOC_CSS + ".dg.full{top:480px}", "const START=-1.3;\n" + ANYDOC_JS + "\ntl.fromTo('.dg',{scale:.92,opacity:0},{scale:1,opacity:1,duration:.35,ease:'power3.out'},0);", "#ffffff")

# ---------------------------------------------------------------- k12 25.43–27.17 light th: mascot READING + report.md highlight
add("k12-reading", 25.43, 1.74, """
<div class="palm"></div>
<div class="abs row"><div class="masw">""" + INV(cell=18) + """<div class="rd mono">READING<span class="d">...</span></div></div>
 <div class="doc"><div class="dh mono">report.md <em>MARKDOWN</em></div><div class="dc mono">
  <div># Q3 review</div><div>&nbsp;</div><div>## Highlights</div><div>- Revenue up 12%</div><div>- 3 new accounts</div><div>&nbsp;</div><div>| Region | Revenue |</div><div>| --- | --- |</div><div>| EMEA | $1.2M |</div></div></div></div>
""", """
.row{left:0;right:0;top:230px;display:flex;justify-content:center;align-items:flex-start;gap:60px}
.masw{display:flex;flex-direction:column;align-items:center;gap:26px;padding-top:40px}
.rd{font-size:14px;letter-spacing:4px;color:#666}
.doc{width:360px;border:1.5px solid #333;border-radius:14px;background:#fff;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.08)}
.dh{display:flex;justify-content:space-between;align-items:center;padding:8px 14px;font-size:14px;color:#111;border-bottom:1px solid #eee}.dh em{font-style:normal;background:#111;color:#fff;font-size:9px;letter-spacing:2px;padding:2px 6px;border-radius:3px}
.dc{padding:14px;font-size:15px;color:#111;line-height:1.7}.dc div{border-radius:3px;padding:0 4px;margin:0 -4px}
""" + INV_CSS, """
tl.fromTo('.row',{opacity:0,y:-20},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.masw .inv',{y:0},{y:-8,duration:.3,yoyo:true,repeat:5,ease:'sine.inOut'},.2);
tl.fromTo('.d',{opacity:0},{opacity:1,duration:.001,repeat:7,yoyo:true,repeatDelay:.2},0);
const rows=qa('.dc div');rows.forEach((r,i)=>{tl.fromTo(r,{backgroundColor:'rgba(232,132,90,0)',color:'#111'},{backgroundColor:'rgba(232,132,90,.35)',color:'#BE6C4A',duration:.08},.3+i*.15).to(r,{backgroundColor:'rgba(232,132,90,0)',color:'#111',duration:.15},.3+i*.15+.14)});
""", lib.C["light"])

# ---------------------------------------------------------------- k14 30.0–31.77 white: Anthropic logo
add("k14-anthropic", 30.0, 1.77, """
<div class="abs lg"><svg viewBox="0 0 200 120"><path class="a1" d="M60 10 L20 110 H40 L48 88 H92 L100 110 H120 L80 10Z M70 32 L86 72 H54Z" fill="#111"/><path class="a2" d="M120 10 H142 L182 110 H160Z" fill="#111"/></svg></div>
<div class="abs wm">ANTHROP\\C</div>
""", """
.lg{left:0;right:0;top:560px;display:flex;justify-content:center}.lg svg{width:560px;height:340px}
.wm{left:0;right:0;top:900px;text-align:center;font-size:38px;letter-spacing:10px;font-weight:600;color:#111}
""", """
tl.fromTo('.a1',{opacity:0,scale:.6},{opacity:1,scale:1,duration:.45,ease:'back.out(1.6)',transformOrigin:'center'},0);
tl.fromTo('.a2',{opacity:0,x:40},{opacity:1,x:0,duration:.4,ease:'power3.out'},.2);
tl.fromTo('.wm',{opacity:0,letterSpacing:'30px'},{opacity:1,letterSpacing:'10px',duration:.5,ease:'power2.out'},1.2);
""", "#ffffff")

# ---------------------------------------------------------------- k15 31.77–33.13 light th: codebase scan terminal
add("k15-scan", 31.77, 1.36, """
<div class="palm"></div>
<div class="card mono term">""" + TERM_HEAD + """<div class="body">
 <div class="l h">High priority:</div>
 <div class="l">1. Hard-parametize CORS (src/index.ts) — origin '*' allows requests from any origin</div>
 <div class="l">2. Unhandled async errors — empty catch {} blocks hide errors</div>
 <div class="l">3. Missing input validation — no email format or password strength checks</div>
 <div class="l h">Medium:</div>
 <div class="l">4. Hardcoded JWT secret fallback — risks using a weak default in production</div>
 <div class="l">5. No request correlation IDs for debugging</div>
 <div class="l">6. Possible orphaned files if DB update fails after file write</div>
 <div class="l q">Would you like me to fix any of these?</div>
 <div class="l cmd"><b>$</b> <span class="cur">▍</span></div></div></div>
""", """
.card.term{top:150px;height:420px;background:#141519;font-size:14px;color:#c9ccd4;line-height:1.8}
.tb{height:36px;display:flex;align-items:center;gap:8px;padding:0 16px}.tb span{width:10px;height:10px;border-radius:50%;background:#3a3d46}.tb span:nth-child(1){background:#E8845A}.tb span:nth-child(2){background:#F5C542}.tb span:nth-child(3){background:#4FC29A}.tb em{font-style:normal;color:#666;font-size:12px;margin-left:8px}
.body{padding:6px 26px}.l{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.h{color:#E8845A;font-weight:600;margin-top:4px}.q{color:#fff;margin-top:8px}.cmd b{color:#E8845A}.cur{color:#E8845A}
""", """
tl.fromTo('.card',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
qa('.body .l').forEach((l,i)=>tl.fromTo(l,{opacity:0},{opacity:1,duration:.05},.15+i*.1));
tl.fromTo('.cur',{opacity:1},{opacity:0,duration:.001,repeat:9,yoyo:true,repeatDelay:.13},0);
""", lib.C["light"])

# ---------------------------------------------------------------- k16 35.73–38.17 blurred light: MCP connectors card
CONN = [("Asana","#f06a6a"),("Atlassian","#2684ff"),("Canva","#00c4cc"),("Figma","#a259ff"),("Gmail","#ea4335"),("Linear","#5e6ad2"),("Sharehunt","#1db954")]
conn = "".join(f'<div class="cn"><i style="background:{c}"></i>{n}<span class="tg"><b></b></span></div>' for n, c in CONN)
add("k16-mcp", 35.73, 2.44, """
<div class="abs bg"><div class="gh1"></div><div class="gh2"></div></div>
<div class="abs cardw"><div class="mc"><div class="hd">✳ Welcome, Chelsea</div><div class="ask">How can I help you today?<span>Opus 4.5 ▾</span></div>
 <div class="sec">⚙ Connectors</div><div class="list">""" + conn + """</div></div>
 <svg class="outline" viewBox="0 0 900 540"><rect x="5" y="5" width="890" height="530" rx="20" fill="none" stroke="#E8845A" stroke-width="8"/></svg>
 <div class="cursor">☞</div></div>
""", """
.bg{inset:0;background:#e9e7e3}
.gh1,.gh2{position:absolute;left:80px;right:80px;height:300px;background:#f6f4f0;border-radius:20px;filter:blur(18px);opacity:.9}.gh1{top:120px}.gh2{top:1420px;background:#dfe3ea}
.cardw{left:90px;right:90px;top:640px;height:540px}
.mc{position:absolute;inset:14px;background:#faf5ef;border-radius:14px;padding:26px 30px;color:#333;font-size:14px}
.hd{text-align:center;font-family:'Instrument Serif';font-style:normal;font-size:30px;color:#111}.hd::first-letter{color:#E8845A}
.ask{margin:16px auto 0;width:520px;border:1px solid #ddd;border-radius:10px;padding:10px 14px;background:#fff;display:flex;justify-content:space-between;color:#777}.ask span{color:#333;font-size:12px}
.sec{margin-top:16px;font-size:12px;color:#777}
.list{margin-top:8px;display:grid;grid-template-columns:1fr 1fr;gap:6px 30px}
.cn{display:flex;align-items:center;gap:8px;font-size:14px;color:#111}.cn i{width:14px;height:14px;border-radius:3px}
.tg{margin-left:auto;width:34px;height:18px;border-radius:9px;background:#ccc;position:relative}.tg b{position:absolute;left:2px;top:2px;width:14px;height:14px;border-radius:50%;background:#fff}
.outline{position:absolute;inset:0;width:100%;height:100%}
.cursor{position:absolute;left:420px;top:150px;font-size:40px;color:#111;filter:drop-shadow(0 4px 6px rgba(0,0,0,.3))}
""", """
tl.fromTo('.cardw',{opacity:0,rotation:-8,x:-80,scale:.9},{opacity:1,rotation:0,x:0,scale:1,duration:.5,ease:'power3.out'},0);
const rc=q('.outline rect'),L2=rc.getTotalLength();tl.fromTo(rc,{strokeDasharray:L2,strokeDashoffset:L2},{strokeDashoffset:0,duration:.6,ease:'power2.inOut'},.4);
tl.fromTo('.cursor',{x:0,y:0},{x:-120,y:40,duration:.4,ease:'power2.inOut'},.3);
qa('.cn').forEach((c,i)=>{tl.fromTo(c,{opacity:0,x:-8},{opacity:1,x:0,duration:.2},.2+i*.08)});
qa('.tg').forEach((t,i)=>{tl.to('.cursor',{x:-120+(i%2)*430,y:120+Math.floor(i/2)*24,duration:.18,ease:'power2.inOut'},.8+i*.2);
 tl.to(t,{backgroundColor:'#4FC29A',duration:.1},.95+i*.2);tl.to(t.querySelector('b'),{x:16,duration:.1},.95+i*.2)});
tl.fromTo('.cardw',{y:0},{y:-30,duration:2.4,ease:'none'},0);
""", "#e9e7e3")

# ---------------------------------------------------------------- k17 38.17–40.7 light th: agent_prompt.md fluff removal
add("k17-fluff", 38.17, 2.53, """
<div class="palm"></div>
<div class="card mono term"><div class="tb"><span></span><span></span><span></span><em>agent_prompt.md</em></div><div class="body">
 <div class="l h"># Agent Prompt</div>
 <div class="l h2">## Summary</div>
 <div class="l">You are an autonomous coding agent with access to the file system, terminal, and browser.</div>
 <div class="l fl">Work through the user's request end-to-end, verifying each step before moving on.</div>
 <div class="l h2">## Instructions</div>
 <div class="l">- Read relevant files before editing</div>
 <div class="l fl">- Prefer minimal, targeted changes</div>
 <div class="l fl">- Ask before destructive actions</div>
 <div class="l">- Verify work before reporting done</div>
 <div class="l fl">- Explain reasoning in plain language</div>
 <div class="l fl">- Ask when requirements are unclear</div>
 <div class="l h2">## Constraints</div>
 <div class="l">- Never expose secrets or credentials</div>
 <div class="l fl">- Run tests before marking complete</div>
 <div class="l fl">- Stay within the current request's scope</div></div></div>
""", """
.card.term{top:130px;height:470px;background:#161311;font-size:14px;color:#d8cfc7;line-height:1.75}
.tb{height:36px;display:flex;align-items:center;gap:8px;padding:0 16px}.tb span{width:10px;height:10px;border-radius:50%;background:#3a3d46}.tb em{font-style:normal;color:#8a7f77;font-size:12px;margin-left:8px}
.body{padding:4px 26px}.l{white-space:nowrap;overflow:hidden;height:24px}.h{color:#E8845A;font-weight:700}.h2{color:#E8845A;margin-top:4px}
.fl{position:relative}.fl::after{content:'';position:absolute;left:0;right:0;top:12px;height:2px;background:#E8845A;transform:scaleX(0);transform-origin:left}
""", """
tl.fromTo('.card',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
const fl=qa('.fl');
fl.forEach((l,i)=>{tl.fromTo(l,{color:'#d8cfc7'},{color:'#8a5a44',duration:.15},.6+i*.14);});
tl.fromTo('.fl',{'--s':0},{duration:.01},0);
fl.forEach((l,i)=>{tl.to(l,{height:0,opacity:0,duration:.3,ease:'power2.inOut'},1.6+i*.1)});
""", lib.C["light"])

# ---------------------------------------------------------------- reused scenes from project 1
reuse("k18-title-skills", "s15-skills-title", 40.7, 1.47, [
    ('<div class="abs k">number four</div>', '<div class="abs k kserif grad">다섯 번째</div>'),
    ('.k{left:0;right:0;top:440px;text-align:center;font-size:60px;color:#9a9a9a;font-weight:500}', '.k{left:0;right:0;top:430px;text-align:center;font-size:110px}'),
    ('<span style="background:#ffb3a7;color:#111">Simplify</span>', '<span style="background:#ffb3a7;color:#111">Simplify</span><span style="background:#8fd3b3;color:#111">Ship</span>'),
])
reuse("k19-skills-doc", "s16-skills-doc", 42.17, 2.46)
reuse("k20-namin", "s17-namin", 45.8, 2.1)
reuse("k21-table", "s18-table", 47.9, 5.9, [("tl.fromTo('.in',{y:0},{y:-150,duration:2.7,ease:'power1.inOut'},.3);", "tl.fromTo('.in',{y:0},{y:-40,duration:2.0,ease:'power1.inOut'},.3);tl.to('.in',{y:-170,duration:3.2,ease:'power1.inOut'},2.4);tl.fromTo('.card',{scale:1},{scale:.97,duration:.15,yoyo:true,repeat:1},2.15);")])

# ---------------------------------------------------------------- host: person + Korean captions
PERSON = [(0.0, 1.13, "th-dark"), (3.07, 4.37, "punch"), (7.57, 10.33, "th-light"), (10.33, 11.1, "punch"), (12.77, 16.97, "th-light"),
          (16.97, 18.07, "punch"), (18.07, 19.5, "th-light"), (20.63, 23.27, "th-light"), (25.43, 27.17, "th-light"), (27.17, 28.93, "punch"),
          (31.77, 33.13, "th-light"), (33.13, 35.73, "punch"), (38.17, 40.7, "th-light"), (44.63, 45.8, "punch"), (47.9, 53.8, "th-light"), (53.8, 57.52, "punch")]

S_, SD, SE, SED = "sans", "sansD", "serif", "serifD"
CAPS = [
 (0.0,0.7,"클로드 코드",S_,860),(0.7,1.13,"처음이면",S_,860),
 (1.2,1.74,"필수로",SED,1300),(1.74,2.26,"깔아야 하는",SED,1300),(2.26,2.58,"무료 플러그인",SED,1300),(2.58,3.07,"무료 플러그인\n5개",SED,1300,"5개"),
 (3.16,3.54,"세팅이",SE,1300),(3.54,3.94,"세팅이\n10배",SE,1300,"10배"),(3.94,4.37,"세팅이\n10배 좋아짐",SE,1300,"10배 좋아짐"),
 (5.7,6.22,"클로드에",S_,1300),(6.22,6.5,"기억을",S_,1300),(6.5,7.12,"세션마다",S_,1300),(7.12,7.57,"심어줌",S_,1300),
 (7.84,8.62,"내 프로젝트랑",S_,860),(8.62,9.3,"파일을",S_,860),(9.3,9.92,"기억해서",S_,860),(9.92,10.33,"다시 설명",S_,860),
 (10.44,10.76,"할 필요가",SE,1300),(10.76,11.1,"할 필요가\n없음",SE,1300,"없음"),
 (12.94,13.42,"뭘 만들지",S_,860),(13.42,14.0,"말만 하면",S_,860),(14.0,14.76,"라이브러리",S_,860),(14.76,15.22,"전체를",S_,860),
 (15.44,15.94,"24,585",S_,860),(15.94,16.44,"100,000",S_,860),(16.44,16.97,"100,000\n개 스킬",S_,860,"개 스킬"),
 (17.12,17.7,"제일 좋은 걸",S_,1300),(17.7,18.07,"찾아서",S_,1300),
 (18.2,18.8,"설치까지",S_,860),(18.8,19.5,"알아서 해줌",S_,860),
 (21.24,21.96,"PPT",SD,860),(21.96,22.6,"엑셀",SD,860),(22.6,23.27,"워드까지",SD,860),
 (23.48,24.04,"전부",SED,1400),(24.04,24.62,"깔끔한",SED,1400),(24.62,24.94,"마크다운",SED,1400),(24.94,25.43,"파일로",SED,1400),
 (25.66,26.0,"AI가",SD,860),(26.24,27.17,"바로 읽음",SD,860),
 (27.26,27.54,"토큰은",S_,1300),(27.54,28.14,"훨씬",S_,1300),(28.14,28.93,"적게 씀",S_,1300),
 (30.6,30.86,"앤트로픽",SED,1150),(30.86,31.42,"공식",SED,1150),(31.42,31.77,"플러그인",SED,1150),
 (31.88,32.5,"내 코드베이스",S_,860),(32.5,33.13,"전체를 스캔",S_,860),
 (33.22,33.74,"제일 맞는",S_,1300),(33.94,34.52,"훅",S_,1300),(34.52,35.02,"스킬",S_,1300),(35.06,35.73,"서브에이전트",S_,1300),
 (35.98,36.72,"MCP 서버까지",SED,1330),(37.02,37.46,"내 프로젝트에",SED,1330),(37.46,38.17,"딱 맞게",SED,1330),
 (38.28,38.76,"추천해주고",S_,860),(38.94,39.62,"쓸데없는 건",S_,860),(39.62,40.7,"다 걷어냄",S_,860),
 (42.42,42.96,"24개 스킬",SE,1300),(42.96,43.44,"묶음인데",SE,1300),(43.6,44.16,"바이브 코딩을",SE,1300),(44.16,44.63,"시니어처럼",SE,1300),
 (44.7,45.22,"진짜 시니어",SE,1300),(45.22,45.8,"진짜 시니어\n엔지니어처럼",SE,1300,"엔지니어처럼"),
 (45.9,46.62,"구글 AI 엔지니어링",SD,1300),(46.62,47.3,"디렉터 출신이",SD,1300),(47.3,47.9,"만든 거",SD,1300),
 (48.0,48.94,"개발 전 과정을",S_,860),(49.22,49.72,"처음부터",S_,860),(49.72,50.18,"끝까지",S_,860),(50.52,51.16,"단계마다",S_,860),(51.16,51.82,"맞는 스킬을",S_,860),(51.82,52.66,"알아서",S_,860),(52.66,53.8,"켜줌",S_,860),
 (53.88,54.46,"써보고 싶으면",S_,1300),(55.02,55.3,"댓글에",SE,1300),(55.3,56.12,"댓글에\n\"클로드\"",SE,1300,"\"클로드\""),(56.38,57.52,"링크 보내드림",S_,1300),
]
EXTRA_CSS = NANUM + """
.serif span,.serifD span{font-family:'Nanum Myeongjo','Instrument Serif',serif;font-weight:700;font-size:96px;letter-spacing:-1px;line-height:1.15}
.sans span,.sansD span{font-size:62px}
.caption.serif,.caption.serifD{transform:skewX(-7deg)}
.caption.serif.cy b,.caption.sans b{background:linear-gradient(180deg,#FFD37A,#F0A045 60%,#E8845A 120%);-webkit-background-clip:text;background-clip:text;color:transparent}
"""
lib.write_all(ROOT, S, lib.host(S, PERSON, CAPS, DUR, title="5 free plugins reel — 한글 리메이크", extra_css=EXTRA_CSS,
              cy_words=("10배", "10배 좋아짐", "없음", "개 스킬", "엔지니어처럼", '"클로드"')))
print(f"wrote {len(S)} scenes + index.html; captions={len(CAPS)}; persons={len(PERSON)}")
