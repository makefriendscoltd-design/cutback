#!/usr/bin/env python3
"""Generate index.html + scenes/*.html for the nick_saraev "4 plugins" reel remake.

Every non-person element of the reference reel is rebuilt as HyperFrames motion graphics.
Person layer = 나민수 cut-out (placeholder). Voice = original reel audio for timing only.
Run: python3 build.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
DUR = 49.62

# ---------- palette / fonts ----------
C = dict(orange="#E8845A", navy="#1B2130", dark="#0E0F13", beige="#EAE3D4", light="#F4F3EF",
         tan="#D6A877", green="#4FC29A", yellow="#F5C542", ink="#111318", cyan="#7FE3E8")

FONTS = """
@font-face{font-family:'Pretendard';src:url('assets/fonts/pretendard.woff2') format('woff2');font-weight:100 900}
@font-face{font-family:'Instrument Serif';font-style:italic;src:url('assets/fonts/InstrumentSerif-Italic.ttf') format('truetype')}
@font-face{font-family:'Instrument Serif';font-style:normal;src:url('assets/fonts/InstrumentSerif-Regular.ttf') format('truetype')}
@font-face{font-family:'Silkscreen';src:url('assets/fonts/Silkscreen-Bold.ttf') format('truetype');font-weight:700}
@font-face{font-family:'JetBrains Mono';src:url('assets/fonts/JetBrainsMono[wght].ttf') format('truetype');font-weight:100 800}
"""

BASE = """
#root{position:absolute;inset:0;overflow:hidden;font-family:'Pretendard',sans-serif;-webkit-font-smoothing:antialiased}
#root *{box-sizing:border-box}
.abs{position:absolute}
.mono{font-family:'JetBrains Mono',monospace}
.serif{font-family:'Instrument Serif',serif;font-style:italic}
.palm{position:absolute;inset:0;background:
 radial-gradient(60% 40% at 20% 10%,rgba(0,0,0,.06),transparent 70%),
 radial-gradient(50% 45% at 85% 20%,rgba(0,0,0,.05),transparent 70%),
 radial-gradient(40% 30% at 70% 90%,rgba(0,0,0,.04),transparent 70%)}
.card{position:absolute;left:60px;right:60px;top:180px;height:520px;border-radius:28px;background:#14161c;
 box-shadow:0 30px 80px rgba(0,0,0,.28);overflow:hidden}
.grad{background:linear-gradient(180deg,#F3A784 0%,#E8845A 45%,#fff 110%);-webkit-background-clip:text;background-clip:text;color:transparent}
"""

def scene(sid, body, css, js, bg):
    """Wrap a sub-composition file."""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><title>{sid}</title></head>
<body><template>
<style>
{FONTS}
{BASE}
#root{{background:{bg}}}
{css}
</style>
<div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
{body}
</div>
<script>
(function(){{
const R=document.querySelector('[data-composition-id="{sid}"]');
const q=(s)=>R.querySelector(s), qa=(s)=>[...R.querySelectorAll(s)];
const rng=(seed)=>{{let a=seed>>>0;return()=>{{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}}};
const tl=gsap.timeline({{paused:true}});
{js}
window.__timelines["{sid}"]=tl;
}})();
</script>
</template></body></html>
"""

SCENES = {}   # sid -> (start, dur, html)
def add(sid, start, dur, body, css, js, bg):
    SCENES[sid] = (start, dur, scene(sid, body, css, js, bg))

# =====================================================================
# S01  0.00–1.60  dark navy card: ASCII scramble → CLAUDE CODE (pixel)
# =====================================================================
add("s01-claude", 0.0, 1.6, """
<div class="abs top"><div id="s01-scr" class="mono"></div>
 <div id="s01-word" class="pix"><div>CLAUDE</div><div>CODE</div></div></div>
""", """
.top{left:0;right:0;top:0;height:900px}
#s01-scr{position:absolute;left:90px;right:90px;top:250px;height:420px;color:#E8845A;font-size:26px;line-height:1.35;
 white-space:pre;letter-spacing:1px;opacity:.9;overflow:hidden}
#s01-scr span{display:block;position:absolute;inset:0;opacity:0}
.pix{position:absolute;left:0;right:0;top:250px;text-align:center;font-family:'Silkscreen';font-weight:700;font-size:150px;
 line-height:.95;color:#E8845A;letter-spacing:-2px}
.pix div{clip-path:inset(0 0 100% 0)}
""", """
// 8 deterministic scramble frames, stepped (seek-safe)
const chars='|<>29GNU:!~18FMT_3AHOVcjq%^)/07ELSZgnu@\\\\(;?bi=+.,-Yfm$';
const r=rng(7); const scr=q('#s01-scr');
for(let f=0;f<8;f++){let s='';for(let l=0;l<11;l++){let line='';for(let c=0;c<34;c++){line+=r()<.72?chars[Math.floor(r()*chars.length)]:' ';}s+=line+'\\n';}
 const sp=document.createElement('span');sp.textContent=s;scr.appendChild(sp);}
const frames=qa('#s01-scr span');
frames.forEach((sp,i)=>{tl.fromTo(sp,{opacity:0},{opacity:1,duration:.001},i*.075).to(sp,{opacity:0,duration:.001},(i+1)*.075-.001)});
tl.fromTo(scr,{opacity:.9},{opacity:0,duration:.25},.55);
tl.fromTo('.pix div',{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)',duration:.35,ease:'steps(6)',stagger:.18},.5);
tl.fromTo('.pix',{x:0},{x:3,duration:.05,repeat:5,yoyo:true},.5);
""", C["navy"])

# =====================================================================
# S02  1.60–3.53  beige plugin installer + numbers 1-4
# =====================================================================
add("s02-installer", 1.6, 1.93, """
<div class="abs box">
 <svg class="ico" viewBox="0 0 120 130" fill="none" stroke="#111" stroke-width="5" stroke-linejoin="round">
  <path d="M30 20h50l22 22v76H30z" fill="#F7F3EA"/><path d="M80 20v22h22"/>
  <path d="M18 34h0v78h62" opacity=".9"/><path d="M52 62l-12 12 12 12M72 62l12 12-12 12" stroke-width="6"/></svg>
 <div class="ttl">Claude Code</div><div class="sub">PLUGIN INSTALLER</div>
 <div class="bar"><div class="fill"></div></div>
 <div class="stat mono"><span class="msg"></span><span class="pct">0%</span></div>
</div>
<div class="abs nums serif">
 <div class="n" style="left:220px;top:300px">1<svg viewBox="0 0 100 100"><path d="M20 20 L80 85" /><path d="M62 82 L80 85 L78 66"/></svg></div>
 <div class="n" style="left:380px;top:250px">2<svg viewBox="0 0 100 100"><path d="M40 15 L60 88"/><path d="M45 76 L60 88 L70 72"/></svg></div>
 <div class="n" style="left:600px;top:250px">3<svg viewBox="0 0 100 100"><path d="M60 15 L40 88"/><path d="M30 72 L40 88 L55 76"/></svg></div>
 <div class="n" style="left:780px;top:300px">4<svg viewBox="0 0 100 100"><path d="M80 20 L20 85"/><path d="M22 66 L20 85 L38 82"/></svg></div>
</div>
""", """
.box{left:0;right:0;top:520px;text-align:center}
.ico{width:170px;height:184px}
.ttl{font-size:60px;font-weight:800;color:#111;margin-top:12px;letter-spacing:-1px}
.sub{font-size:22px;letter-spacing:5px;color:#6a655b;margin-top:6px}
.bar{width:640px;height:14px;background:#cfc6b4;border-radius:8px;margin:70px auto 0;overflow:hidden}
.fill{width:100%;height:100%;background:#111;transform-origin:left center;transform:scaleX(0)}
.stat{display:flex;justify-content:space-between;width:640px;margin:16px auto 0;font-size:20px;color:#555}
.nums .n{position:absolute;font-size:120px;color:#BE6C4A;width:220px;height:220px;line-height:1}
.nums .n svg{position:absolute;left:40px;top:80px;width:150px;height:150px;fill:none;stroke:#111;stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round}
""", """
tl.fromTo('.box',{opacity:0,y:30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.fill',{scaleX:0},{scaleX:1,duration:1.5,ease:'power1.inOut'},.15);
const pct=q('.pct'),msg=q('.msg');const msgs=['Downloading Claude Code plugins…','Installing plugin files…','Configuring agent instructions…','Done'];
for(let i=0;i<=100;i+=4){tl.call(()=>{},[],0)}
tl.fromTo({v:0},{v:0},{v:100,duration:1.5,ease:'power1.inOut',onUpdate:function(){const v=Math.round(this.targets()[0].v);pct.textContent=v+'%';msg.textContent=msgs[v<40?0:v<80?1:v<100?2:3]}},.15);
qa('.nums .n').forEach((n,i)=>{tl.fromTo(n,{opacity:0,scale:.6,y:20},{opacity:1,scale:1,y:0,duration:.22,ease:'back.out(2)'},.55+i*.16);
 tl.fromTo(n.querySelectorAll('path'),{strokeDasharray:200,strokeDashoffset:200},{strokeDashoffset:0,duration:.3,ease:'power2.out'},.65+i*.16)});
""", C["beige"])

# =====================================================================
# S03  3.53–4.77  Ponytail card (dark)
# =====================================================================
add("s03-ponytail", 3.53, 1.24, """
<div class="abs wrap">
 <div class="logo"><svg viewBox="0 0 200 200"><g fill="none" stroke="#111" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">
  <ellipse cx="100" cy="95" rx="62" ry="58" fill="#fff"/><path d="M50 70q50-50 100 0"/><path d="M155 110q30 30 10 70"/>
  <circle cx="80" cy="100" r="14"/><circle cx="120" cy="100" r="14"/><path d="M94 100h12M66 96l-14-6M134 96l14-6"/><path d="M85 130q15 8 30 0"/></g></svg></div>
 <div class="name">Ponytail</div>
 <div class="tag serif">He says nothing. He writes one line. It works.</div>
 <div class="chips mono"><span>stars <b>73k</b></span><span>release <b>v4.8.4</b></span><span>npm <b>v4.8.4</b></span><span>works with <b>16 agents</b></span><span>license <b>MIT</b></span></div>
 <div class="badges"><div class="bd">🏆 <em>TRENDSHIFT</em><br>#1 Repository Of The Day</div><div class="bd">🏆 <em>TRENDSHIFT</em><br>#1 Repository Of The Week</div></div>
 <div class="stats">~54% less code (up to 94%) · ~20% cheaper · ~27% faster · 100% safe</div>
</div>
""", """
.wrap{left:0;right:0;top:470px;text-align:center;color:#fff}
.logo{width:300px;height:300px;margin:0 auto;filter:drop-shadow(0 12px 30px rgba(0,0,0,.6))}
.logo svg{width:100%;height:100%}
.name{font-size:52px;font-weight:700;margin-top:10px}
.tag{font-size:28px;color:#cfd2da;margin-top:14px}
.chips{display:flex;justify-content:center;gap:10px;margin-top:26px;font-size:17px;color:#9aa0ad}
.chips span{background:#1f2229;border-radius:6px;padding:6px 10px}.chips b{color:#fff;font-weight:600;margin-left:4px}
.badges{display:flex;justify-content:center;gap:16px;margin-top:26px}
.bd{background:#fff;color:#111;border-radius:14px;padding:14px 22px;font-size:20px;font-weight:700;line-height:1.35;text-align:left}
.bd em{font-style:normal;font-size:12px;letter-spacing:3px;color:#666}
.stats{margin-top:26px;font-size:22px;color:#c7cbd4}
""", """
tl.fromTo('.logo',{opacity:0,scale:.7,rotation:-8},{opacity:1,scale:1,rotation:0,duration:.35,ease:'back.out(1.6)'},0);
['.name','.tag','.chips','.badges','.stats'].forEach((s,i)=>tl.fromTo(s,{opacity:0,y:26},{opacity:1,y:0,duration:.3,ease:'power3.out'},.12+i*.11));
tl.fromTo('.bd',{scale:.85},{scale:1,duration:.3,ease:'back.out(2)',stagger:.08},.5);
""", C["dark"])

# =====================================================================
# S04  4.77–6.47  light talking-head card: terminal (typing)
# =====================================================================
TERM_ROWS = """
<div class="sec">Needs input</div>
<div class="row"><i>●</i> dark-mode <span>system theme vs explicit toggle — your call</span><em>4m</em></div>
<div class="row"><i>●</i> release-notes <span>draft ready — which feature leads?</span><em>11m</em></div>
<div class="row hl"><i>●</i> load-test <span>+ to return</span><em>3m</em></div>
<div class="sec">Working</div>
<div class="row"><i>○</i> pr-review <span>+ to return</span><em>1s</em></div>
<div class="row"><i>○</i> perf-audit <span>events_org_ts index live — p95 38ms</span><em>2m</em></div>
<div class="row"><i>○</i> payment-migration <span>porting billing to the new processor — 12/14</span><em>2m</em></div>
<div class="sec">Completed</div>
<div class="row"><i>✓</i> test-coverage <span>billing/ from 61% → 92% — PR #468 merged</span><em>9m</em></div>
"""
add("s04-terminal", 4.77, 1.7, """
<div class="palm"></div>
<div class="card mono"><div class="rows">""" + TERM_ROWS + """</div>
 <div class="reply"><span class="tag">3m</span> p95 613ms — /export isn't rate-limited. Intentional?</div>
 <div class="input">› <span class="typed">no — add /export to the limiter</span><span class="cur">▍</span></div>
 <div class="hint">enter to open · space to reply · ctrl+x to delete</div></div>
""", """
.card{padding:26px 34px;font-size:17px;color:#cfd3dc;line-height:1.6}
.sec{color:#8f95a3;margin-top:8px}.row{display:flex;gap:12px;white-space:nowrap}.row i{font-style:normal;color:#E8845A}
.row span{color:#8f95a3;flex:1;overflow:hidden;text-overflow:ellipsis}.row em{font-style:normal;color:#666}
.row.hl{background:#22252d;margin:0 -12px;padding:0 12px;border-radius:6px}
.reply{margin-top:14px;border:1px solid #3a3d46;border-radius:8px;padding:8px 12px;color:#e6e8ee}
.reply .tag{background:#E8845A;color:#111;border-radius:4px;padding:1px 6px;font-size:13px;margin-right:8px}
.input{margin-top:10px;border:1px solid #3a3d46;border-radius:8px;padding:8px 12px;color:#fff;background:#0f1116}
.typed{display:inline-block;clip-path:inset(0 100% 0 0)}.cur{color:#E8845A}
.hint{color:#666;font-size:14px;margin-top:8px}
""", """
tl.fromTo('.card',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.reply',{opacity:0,x:-20},{opacity:1,x:0,duration:.25},.3);
tl.fromTo('.typed',{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.9,ease:'steps(30)'},.55);
tl.fromTo('.cur',{opacity:1},{opacity:0,duration:.001,repeat:11,yoyo:true,repeatDelay:.14},0);
""", C["light"])

# =====================================================================
# S05  6.47–8.85  dark grouped bar chart + ↓ 50% ↓
# =====================================================================
bars = ""
groups = [("Loss", [92, 78, 60, 48]), ("Tokens", [100, 82, 66, 52]), ("Cost", [96, 80, 70, 40]), ("Time", [90, 70, 50, 38])]
cols = ["#B8BCC6", "#F0A045", "#8B7CF6", "#4FC29A"]
for gi, (gn, vals) in enumerate(groups):
    bars += f'<div class="g"><div class="bars">' + "".join(f'<div class="b" style="height:{v*3.2}px;background:{cols[i]}"></div>' for i, v in enumerate(vals)) + f'</div><div class="gl">{gn}</div></div>'
add("s05-chart", 6.47, 2.38, """
<div class="abs big serif">↓ <b>50%</b> ↓</div>
<div class="abs chart"><div class="ct">Every metric vs the no-skill baseline (Claude Code, Haiku 4.5, 12 tasks)</div>
 <div class="lg"><span style="--c:#B8BCC6">baseline</span><span style="--c:#F0A045">ponytail</span><span style="--c:#8B7CF6">+ skills</span><span style="--c:#4FC29A">page-native</span></div>
 <div class="axis"></div><div class="groups">""" + bars + """</div></div>
""", """
.big{left:0;right:0;top:250px;text-align:center;font-size:170px;color:#c9ccd4;font-style:normal;font-family:'Pretendard';font-weight:300;letter-spacing:-4px}
.big b{font-weight:800;color:#e9ebf0}
.chart{left:80px;right:80px;top:640px;height:640px}
.ct{color:#8f95a3;font-size:16px;text-align:center}
.lg{display:flex;justify-content:center;gap:22px;margin-top:8px;font-size:14px;color:#9aa0ad}
.lg span::before{content:'';display:inline-block;width:10px;height:10px;background:var(--c);margin-right:6px;border-radius:2px}
.axis{position:absolute;left:0;right:0;top:80px;height:420px;background:repeating-linear-gradient(180deg,#1e2129 0 1px,transparent 1px 84px)}
.groups{position:absolute;left:0;right:0;top:80px;height:420px;display:flex;justify-content:space-around;align-items:flex-end}
.g{display:flex;flex-direction:column;align-items:center}.bars{display:flex;gap:6px;align-items:flex-end;height:420px}
.b{width:32px;border-radius:4px 4px 0 0;transform-origin:bottom center}
.gl{color:#9aa0ad;font-size:15px;margin-top:10px}
""", """
tl.fromTo('.chart',{opacity:0},{opacity:1,duration:.25},0);
tl.fromTo('.axis',{scaleX:0},{scaleX:1,duration:.5,ease:'power2.out',transformOrigin:'left'},0);
qa('.b').forEach((b,i)=>tl.fromTo(b,{scaleY:0},{scaleY:1,duration:.5,ease:'power3.out'},.15+(i%4)*.06+Math.floor(i/4)*.12));
tl.fromTo('.big',{opacity:0,y:30,filter:'blur(14px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.6,ease:'power2.out'},1.0);
""", C["dark"])

# =====================================================================
# S06  9.80–11.40  white: THE SECOND / 🚀 / OMNI ROUTE
# =====================================================================
add("s06-omni-title", 9.8, 1.6, """
<div class="abs t1 serif grad">THE SECOND</div>
<div class="abs rocket">🚀</div>
<div class="abs t2 serif"><span class="w1">OMNI</span> <span class="w2">ROUTE</span></div>
""", """
.t1{left:0;right:0;top:400px;text-align:center;font-size:120px;letter-spacing:-2px}
.rocket{left:0;right:0;top:480px;text-align:center;font-size:520px;line-height:1;transform-origin:center}
.t2{left:0;right:0;top:1000px;text-align:center;font-size:150px;letter-spacing:-3px;
 background:linear-gradient(180deg,#F3A784,#E8845A 50%,#9a9a9a 110%);-webkit-background-clip:text;background-clip:text;color:transparent}
.t2 span{display:inline-block}
""", """
tl.fromTo('.t1',{opacity:0,y:40,filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.45,ease:'power2.out'},0);
tl.fromTo('.rocket',{opacity:0,scale:.3,rotation:-30,y:120},{opacity:1,scale:1,rotation:0,y:0,duration:.6,ease:'back.out(1.4)'},.05);
tl.fromTo('.rocket',{y:0},{y:-12,duration:.5,yoyo:true,repeat:1,ease:'sine.inOut'},.7);
tl.fromTo('.w1',{opacity:0,y:40,filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.4,ease:'power2.out'},.55);
tl.fromTo('.w2',{opacity:0,y:40,filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.4,ease:'power2.out'},.95);
""", "#ffffff")

# pixel invader mascot (OmniRoute logo stand-in) as CSS grid
INVADER = [
"..1......1..",
"...1....1...",
"..11111111..",
".11.1111.11.",
"111111111111",
"1.11111111.1",
"1.1......1.1",
"...11..11...",
]
def invader_html(cls="inv", color="#E8845A", cell=18):
    cells = ""
    for y, row in enumerate(INVADER):
        for x, ch in enumerate(row):
            if ch == "1":
                cells += f'<i style="left:{x*cell}px;top:{y*cell}px;width:{cell}px;height:{cell}px;background:{color}"></i>'
    return f'<div class="{cls}" style="width:{12*cell}px;height:{8*cell}px">{cells}</div>'
INV_CSS = ".inv{position:relative}.inv i{position:absolute;display:block}"

# =====================================================================
# S07  11.40–13.57  white: mascot + terminal with dotted infinity loop
# =====================================================================
add("s07-omni-loop", 11.4, 2.17, """
<div class="abs mas">""" + invader_html(cell=22) + """</div>
<div class="abs term"><div class="tb"><span></span><span></span><span></span><em class="mono">claude-code — zsh</em></div>
 <svg viewBox="0 0 800 380"><path id="s07-inf" d="M400 190 C400 110 300 60 220 110 C140 160 140 220 220 270 C300 320 400 270 400 190 C400 110 500 60 580 110 C660 160 660 220 580 270 C500 320 400 270 400 190" fill="none" stroke="#E8845A" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 16"/></svg>
 <div class="mono tag">$ omniroute --providers 353 --free 154 ∞</div></div>
""", """
.mas{left:0;right:0;top:330px;display:flex;justify-content:center}
.term{left:90px;right:90px;top:560px;height:520px;background:#0e0f13;border-radius:22px;box-shadow:0 40px 90px rgba(0,0,0,.35);overflow:hidden}
.tb{height:44px;display:flex;align-items:center;gap:8px;padding:0 16px;background:#16181e}.tb span{width:12px;height:12px;border-radius:50%;background:#3a3d46}
.tb em{font-style:normal;color:#666;font-size:13px;margin-left:auto}
.term svg{position:absolute;left:50px;right:50px;top:60px;width:800px;height:380px}
.tag{position:absolute;left:30px;bottom:22px;color:#E8845A;font-size:16px;opacity:.85}
""" + INV_CSS, """
tl.fromTo('.mas',{opacity:0,y:-80},{opacity:1,y:0,duration:.4,ease:'bounce.out'},0);
tl.fromTo('.term',{opacity:0,y:40,scale:.96},{opacity:1,y:0,scale:1,duration:.35,ease:'power3.out'},.1);
const L=q('#s07-inf').getTotalLength();
tl.fromTo('#s07-inf',{strokeDashoffset:0},{strokeDashoffset:-L*0.6,duration:2.1,ease:'none'},.2);
tl.fromTo('#s07-inf',{opacity:0},{opacity:1,duration:.3},.2);
tl.fromTo('.tag',{opacity:0},{opacity:.85,duration:.3},.6);
tl.fromTo('.mas .inv',{y:0},{y:-10,duration:.35,yoyo:true,repeat:3,ease:'sine.inOut'},.5);
""", "#ffffff")

# =====================================================================
# S08  13.57–16.45  dark: provider docs + orange outline
# =====================================================================
PROV = [("OpenAI","#fff","◎"),("Anthropic","#E8845A","✳"),("Gemini","#7aa7ff","✦"),("xAI Grok","#ddd","∅"),("DeepSeek","#5b8cff","◔"),
        ("Qwen","#9b7bff","✹"),("Meta Llama","#2f7cf6","∞"),("Groq","#ffb347","g"),("NVIDIA","#76b900","▣"),("MiniMax","#ff5c8a","≋"),
        ("Perplexity","#20b8cd","✵"),("HuggingFace","#ffd21e","☺"),("Together","#a06bff","❋"),("Fireworks","#ff7b3d","✺"),("Cloudflare","#f38020","☁")]
grid = "".join(f'<div class="p"><b style="color:{c}">{g}</b><span>{n}</span></div>' for n, c, g in PROV)
add("s08-providers", 13.57, 2.88, """
<div class="abs page">
 <div class="blur mono">--dry-run previews the exact env/args without executing, and --api-key-env<br>keeps secrets out of your shell history. → CLI Integrations</div>
 <div class="pill">🌐 <b>353 AI Providers</b> — 154 Catalog-Marked Free</div>
 <p><b>353 registered providers</b> across the canonical chat, media, search, local, cloud-agent and system collections, including <b>154 carrying</b> <code>hasFree: true</code> discovery metadata. The chat model registry covers <b>268 providers / 2,566</b> distinct provider-model pairs / <b>1,312 raw model IDs</b>; the separate free-budget catalog has <b>455 per-model rows, 40 recurring pools and 56</b> recurring/keyless free-forever providers.</p>
 <div class="h2">🏛 Every major lab — through one endpoint</div>
 <div class="gridw"><div class="grid">""" + grid + """</div><svg class="outline" viewBox="0 0 900 520"><rect x="4" y="4" width="892" height="512" rx="22" fill="none" stroke="#E8845A" stroke-width="7"/></svg></div>
 <div class="more">…and 330+ more — every icon resolves live from the dashboard's provider catalog. <u>Provider Reference</u></div>
 <div class="blur2"><span></span><span></span><span></span><span></span><span></span><span></span></div>
</div>
""", """
.page{left:70px;right:70px;top:150px;color:#c9ccd4;font-size:15px;line-height:1.55}
.blur{filter:blur(4px);color:#8f95a3;font-size:12px;margin-bottom:60px}
.pill{display:inline-block;background:#E8845A;color:#111;border-radius:8px;padding:6px 14px;font-size:20px;font-weight:600}
.pill b{font-weight:800}
p{margin:22px 0 0;color:#c9ccd4}p b{color:#fff}code{font-family:'JetBrains Mono';background:#1f2229;padding:1px 5px;border-radius:4px;font-size:13px}
.h2{margin-top:30px;font-size:20px;font-weight:700;color:#fff}
.gridw{position:relative;margin-top:18px;height:520px}
.grid{position:absolute;inset:20px;display:grid;grid-template-columns:repeat(5,1fr);gap:14px}
.p{background:#181a20;border:1px solid #262930;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;font-size:13px;color:#aeb3bf}
.p b{font-size:34px;font-weight:400;line-height:1}
.outline{position:absolute;inset:0;width:100%;height:100%}
.more{margin-top:16px;font-size:14px;color:#8f95a3}.more u{color:#7aa7ff}
.blur2{margin-top:40px;display:flex;gap:18px;filter:blur(8px)}.blur2 span{flex:1;height:120px;background:#1b1e26;border-radius:10px}
""", """
tl.fromTo('.page',{opacity:0,y:60},{opacity:1,y:0,duration:.4,ease:'power3.out'},0);
tl.fromTo('.page',{scale:1,y:0},{scale:1.06,y:-60,duration:2.5,ease:'power1.inOut',transformOrigin:'50% 40%'},.35);
qa('.p').forEach((p,i)=>tl.fromTo(p,{opacity:0,scale:.8},{opacity:1,scale:1,duration:.25,ease:'back.out(1.8)'},.15+i*.03));
const rc=q('.outline rect'),L2=rc.getTotalLength();
tl.fromTo(rc,{strokeDasharray:L2,strokeDashoffset:L2},{strokeDashoffset:0,duration:.6,ease:'power2.inOut'},.85);
tl.fromTo('.pill',{backgroundColor:'#E8845A'},{backgroundColor:'#F3A784',duration:.3,yoyo:true,repeat:1},1.5);
""", C["dark"])

# =====================================================================
# S09  16.45–18.43  dark: usage limit terminal, bar drains, screen tints red
# =====================================================================
add("s09-limit", 16.45, 1.98, """
<div class="abs glow"></div>
<div class="abs tint"></div>
<div class="abs term mono"><div class="tb"><span></span><span></span><span></span><em>claude-code — usage</em></div>
 <div class="ub"><div class="ul">USAGE REMAINING</div><div class="ubar"><div class="uf"></div></div><div class="un">3,696</div></div>
 <div class="code"><div>› refactor auth middleware</div><div class="c">✓ reading src/auth/*.ts</div><div class="c">✓ planning 4 edits</div><div class="c">… writing tests</div><div class="c">… running suite</div><div class="c">✓ 42 passed</div><div class="c">› fix rate limiter</div><div class="c">… reading</div><div class="err">✗ usage limit reached — resets in 4h 12m</div></div>
 <div class="mas">""" + invader_html(cell=9) + """</div></div>
""", """
.glow{left:-200px;right:-200px;top:-300px;height:700px;background:radial-gradient(50% 60% at 50% 40%,rgba(79,194,154,.55),transparent 70%);filter:blur(40px)}
.tint{inset:0;background:#7a2416;opacity:0}
.term{left:110px;right:110px;top:560px;height:560px;background:#0b0c10;border-radius:22px;box-shadow:0 40px 90px rgba(0,0,0,.5);color:#aeb3bf;font-size:16px}
.tb{height:42px;display:flex;align-items:center;gap:8px;padding:0 16px;background:#14161c;border-radius:22px 22px 0 0}.tb span{width:11px;height:11px;border-radius:50%;background:#3a3d46}.tb em{font-style:normal;color:#666;font-size:12px;margin-left:auto}
.ub{display:flex;align-items:center;gap:16px;padding:26px 30px 10px}.ul{font-size:11px;letter-spacing:2px;color:#666}
.ubar{flex:1;height:10px;background:#1f2229;border-radius:6px;overflow:hidden}.uf{height:100%;width:100%;background:#4FC29A;transform-origin:left}
.un{color:#4FC29A;font-weight:700;font-size:22px;min-width:90px;text-align:right}
.code{padding:10px 30px;line-height:1.7}.c{color:#6b7080}.err{color:#ff5c5c;opacity:0}
.mas{position:absolute;right:26px;bottom:20px}
""" + INV_CSS, """
tl.fromTo('.term',{opacity:0,y:40},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
qa('.code div').forEach((d,i)=>tl.fromTo(d,{opacity:0},{opacity:1,duration:.05},.2+i*.1));
const uf=q('.uf'),un=q('.un');
tl.fromTo(uf,{scaleX:1,backgroundColor:'#4FC29A'},{scaleX:.44,backgroundColor:'#F0A045',duration:.6,ease:'power2.inOut'},.35);
tl.fromTo({v:3696},{v:3696},{v:1630,duration:.6,ease:'power2.inOut',onUpdate:function(){un.textContent=Math.round(this.targets()[0].v).toLocaleString()}},.35);
tl.to(un,{color:'#F0A045',duration:.3},.5);
tl.fromTo('.glow',{opacity:1},{opacity:.7,duration:.6},.35).to('.glow',{background:'radial-gradient(50% 60% at 50% 40%,rgba(240,160,69,.55),transparent 70%)',duration:.01},.5);
tl.to(uf,{scaleX:0.02,backgroundColor:'#ff5c5c',duration:.4,ease:'power3.in'},1.0);
tl.fromTo({v:1630},{v:1630},{v:0,duration:.4,ease:'power3.in',onUpdate:function(){un.textContent=Math.round(this.targets()[0].v).toLocaleString()}},1.0);
tl.to(un,{color:'#ff5c5c',duration:.2},1.2);
tl.fromTo('.err',{opacity:0},{opacity:1,duration:.1},1.25);
tl.fromTo('.tint',{opacity:0},{opacity:.85,duration:.35,ease:'power2.out'},1.05);
tl.fromTo('.term',{x:0},{x:6,duration:.04,repeat:7,yoyo:true},1.05);
""", C["dark"])

# =====================================================================
# S10  18.43–20.63  light th card: Switching model… carousel
# =====================================================================
MODELS = [("Gemini","✦","#8B7CF6"),("GLM-5.0","Z","#111"),("Kimi","K","#333"),("Claude Code","✳","#E8845A"),("Gemini","✦","#8B7CF6"),("GLM-5.0","Z","#111"),("Kimi","K","#333"),("Claude Code","✳","#E8845A")]
cards = "".join(f'<div class="mc"><div class="mi" style="background:{c}">{g}</div><span>{n}</span></div>' for n, g, c in MODELS)
add("s10-switch", 18.43, 2.2, """
<div class="palm"></div>
<div class="card light"><div class="k mono">CLAUDE CODE · SWITCH MODEL</div><div class="t">Switching model<span class="dots">…</span></div>
 <div class="strip">""" + cards + """</div><div class="focus"></div></div>
""", """
.card.light{background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.12)}
.k{text-align:center;color:#999;font-size:12px;letter-spacing:3px;margin-top:38px}
.t{text-align:center;color:#111;font-size:36px;font-weight:800;margin-top:10px}
.strip{position:absolute;left:0;top:190px;display:flex;gap:40px;padding-left:390px}
.mc{width:180px;height:210px;border-radius:22px;background:#fff;border:1px solid #e6e6e6;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;flex:none}
.mi{width:76px;height:76px;border-radius:18px;color:#fff;font-size:38px;display:grid;place-items:center;font-weight:700}
.mc span{font-size:16px;color:#333;font-weight:600}
.focus{position:absolute;left:50%;top:170px;width:220px;height:250px;margin-left:-110px;border:5px solid #E8845A;border-radius:28px;box-shadow:0 0 0 8px rgba(232,132,90,.15)}
""", """
tl.fromTo('.card',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
// steps of one card (220px) every ~0.55s
const step=220;
tl.fromTo('.strip',{x:-step*1},{x:-step*1,duration:.01},0);
[1,2,3].forEach((i)=>tl.to('.strip',{x:-step*(i+1),duration:.35,ease:'power3.inOut'},.35+i*.55-.35));
tl.fromTo('.focus',{scale:1},{scale:1.06,duration:.15,yoyo:true,repeat:5,ease:'sine.inOut'},.35);
tl.fromTo('.mc:nth-child(3) ',{filter:'blur(0px)'},{filter:'blur(0px)',duration:.01},0);
tl.fromTo('.dots',{opacity:0},{opacity:1,duration:.001,repeat:7,yoyo:true,repeatDelay:.25},0);
""", C["light"])

# =====================================================================
# S11  20.40–22.93  dark: Free-Tier Budget card
# =====================================================================
ROWS = [("Kiro","#8B7CF6",78,"50 cr"),("Qoder","#FF5C8A",64,"∞"),("LongCat","#4FC29A",58,"50M/day"),("Cerebras","#F0A045",44,"1M/day"),("NVIDIA","#76b900",50,"40 rpm"),("Pollinations","#7aa7ff",36,"no key")]
rows = "".join(f'<div class="r"><span class="rn">{n}</span><div class="rb"><div class="rf" style="width:{w}%;background:{c}"></div></div><span class="rv">{v}</span></div>' for n, c, w, v in ROWS)
add("s11-budget", 20.63, 2.3, """
<div class="abs wrap"><div class="bc"><div class="bh"><b>Free-Tier Budget</b><span><em>1.4B</em> / 1.6B this month</span></div>
 <div class="tb2"><div class="tf"></div></div><div class="rows">""" + rows + """</div>
 <div class="ft">Pool-deduped & honest — no inflated multi-⊗ claims.</div></div>
 <svg class="outline" viewBox="0 0 900 470"><rect x="5" y="5" width="890" height="460" rx="20" fill="none" stroke="#E8845A" stroke-width="8"/></svg></div>
""", """
.wrap{left:90px;right:90px;top:400px;height:470px}
.bc{position:absolute;inset:14px;background:#14161c;border-radius:16px;padding:26px 30px;color:#c9ccd4;font-size:16px}
.bh{display:flex;justify-content:space-between;align-items:baseline}.bh b{font-size:24px;color:#fff}.bh em{font-style:normal;color:#FF5C8A;font-weight:800;font-size:22px}
.tb2{height:12px;background:#22252d;border-radius:6px;margin-top:14px;overflow:hidden}.tf{width:88%;height:100%;background:linear-gradient(90deg,#8B7CF6,#FF5C8A);transform-origin:left}
.rows{margin-top:22px;display:flex;flex-direction:column;gap:12px}
.r{display:flex;align-items:center;gap:16px}.rn{width:120px;font-weight:700;color:#fff}.rb{flex:1;height:10px;background:#22252d;border-radius:5px;overflow:hidden}.rf{height:100%;transform-origin:left}
.rv{width:90px;text-align:right;color:#8f95a3;font-size:14px}
.ft{margin-top:20px;color:#666;font-size:12px}
.outline{position:absolute;inset:0;width:100%;height:100%}
""", """
tl.fromTo('.wrap',{opacity:0,scale:.9,y:40},{opacity:1,scale:1,y:0,duration:.4,ease:'back.out(1.4)'},0);
tl.fromTo('.tf',{scaleX:0},{scaleX:1,duration:.7,ease:'power2.out'},.2);
qa('.rf').forEach((f,i)=>tl.fromTo(f,{scaleX:0},{scaleX:1,duration:.5,ease:'power3.out'},.3+i*.08));
qa('.r').forEach((r,i)=>tl.fromTo(r,{opacity:0,x:-14},{opacity:1,x:0,duration:.25},.25+i*.08));
const rc=q('.outline rect'),L2=rc.getTotalLength();
tl.fromTo(rc,{strokeDasharray:L2,strokeDashoffset:L2},{strokeDashoffset:0,duration:.6,ease:'power2.inOut'},.55);
tl.fromTo('.bh em',{scale:1},{scale:1.25,duration:.18,yoyo:true,repeat:1,transformOrigin:'center'},.7);
""", C["dark"])

# =====================================================================
# S12  23.63–24.77  beige: THIRD + Graphify card
# =====================================================================
GRAPHIFY_SVG = """<svg viewBox="0 0 100 100" fill="none" stroke="#111" stroke-width="3" stroke-linejoin="round"><path d="M20 30L50 15L80 30L80 70L50 85L20 70Z"/><path d="M20 30L50 50L80 30M50 50V85M20 70L50 50L80 70"/><circle cx="50" cy="15" r="5" fill="#111"/><circle cx="80" cy="30" r="5" fill="#111"/><circle cx="20" cy="30" r="5" fill="#111"/><circle cx="50" cy="50" r="5" fill="#111"/><circle cx="20" cy="70" r="5" fill="#111"/><circle cx="80" cy="70" r="5" fill="#111"/><circle cx="50" cy="85" r="5" fill="#111"/></svg>"""
add("s12-graphify-title", 23.63, 1.14, """
<div class="abs t serif grad">THIRD</div>
<div class="abs gc">""" + GRAPHIFY_SVG + """<span>Graphify</span></div>
""", """
.t{left:0;right:0;top:520px;text-align:center;font-size:150px}
.gc{left:140px;right:140px;top:730px;height:230px;background:#4FC29A;border-radius:22px;display:flex;align-items:center;justify-content:center;gap:24px;box-shadow:0 30px 60px rgba(0,0,0,.18)}
.gc svg{width:120px;height:120px}.gc span{font-size:70px;font-weight:600;color:#111;letter-spacing:-1px}
""", """
tl.fromTo('.t',{opacity:0,y:40,filter:'blur(12px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.45,ease:'power2.out'},0);
tl.fromTo('.gc',{opacity:0,scale:1.15,filter:'blur(16px)'},{opacity:1,scale:1,filter:'blur(0px)',duration:.5,ease:'power3.out'},.25);
""", C["beige"])

# =====================================================================
# S13  24.77–27.67  dark navy: knowledge-graph app UI
# =====================================================================
def graph_nodes(seed=11):
    import random
    r = random.Random(seed)
    clusters = [(300, 380, "#F0A045"), (520, 300, "#4FC29A"), (700, 420, "#7aa7ff"), (420, 520, "#FF5C8A"), (620, 560, "#F5C542")]
    nodes, edges = [], []
    for ci, (cx, cy, col) in enumerate(clusters):
        idx0 = len(nodes)
        for i in range(34):
            a = r.random() * 6.283; d = r.random() ** .6 * 120
            nodes.append((cx + d * __import__("math").cos(a), cy + d * __import__("math").sin(a) * .7, col, ci))
        for i in range(30):
            a, b = r.randrange(34), r.randrange(34)
            edges.append((idx0 + a, idx0 + b))
    circ = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{3 + (i%3)}" fill="{c}" data-c="{ci}"/>' for i, (x, y, c, ci) in enumerate(nodes))
    lines = "".join(f'<line x1="{nodes[a][0]:.0f}" y1="{nodes[a][1]:.0f}" x2="{nodes[b][0]:.0f}" y2="{nodes[b][1]:.0f}" stroke="{nodes[a][2]}" stroke-opacity=".25" data-c="{nodes[a][3]}"/>' for a, b in edges)
    return f'<svg class="gsvg" viewBox="0 0 1000 800"><g class="edges">{lines}</g><g class="nodes">{circ}</g></svg>'
COMM = [("APIRouter","#7aa7ff",94),("FastAPI","#4FC29A",46),("SecurityBase","#FF5C8A",71),("BaseModelWithConfig","#F0A045",44),("v2","#8B7CF6",56),("Scope","#F5C542",31),("FastAPIDeprecationWarning","#7aa7ff",49),("HTTPException","#FF5C8A",38)]
comm = "".join(f'<div class="ci"><i style="background:{c}"></i>{n}<em>{v}</em></div>' for n, c, v in COMM)
add("s13-graph", 24.77, 2.9, """
<div class="abs app"><div class="ab"><span class="lg"><b>G</b> Graphify</span><span class="mono ct"><b>170</b> NODES · <b>228</b> EDGES</span></div>
 <div class="halo"></div>""" + graph_nodes() + """
 <div class="panel"><div class="ph">COMMUNITIES <span>5/5</span></div><div class="ci sel">☑ Select All</div>""" + comm + """</div></div>
""", """
.app{inset:0;background:#0b0e16;color:#c9ccd4}
.ab{position:absolute;left:60px;right:60px;top:170px;display:flex;justify-content:space-between;font-size:14px;color:#8f95a3}
.lg b{display:inline-grid;place-items:center;width:22px;height:22px;background:#4FC29A;color:#0b0e16;font-weight:900;border-radius:5px;margin-right:6px}
.ct b{color:#fff}
.halo{position:absolute;left:140px;top:300px;width:800px;height:640px;border-radius:50%;background:radial-gradient(circle,rgba(70,90,160,.35),transparent 70%);filter:blur(30px)}
.gsvg{position:absolute;left:40px;top:250px;width:1000px;height:800px}
.gsvg circle{transform-origin:center;transform-box:fill-box}
.panel{position:absolute;left:60px;right:60px;top:1160px;background:#111520;border:1px solid #1e2331;border-radius:14px;padding:18px 22px;display:grid;grid-template-columns:1fr 1fr;gap:8px 30px;font-size:14px}
.ph{grid-column:1/3;letter-spacing:2px;font-size:12px;color:#8f95a3;display:flex;justify-content:space-between}
.ci{display:flex;align-items:center;gap:8px;color:#dfe2ea}.ci i{width:10px;height:10px;border-radius:2px}.ci em{margin-left:auto;font-style:normal;color:#666}
.sel{grid-column:1/3;color:#8f95a3}
""", """
tl.fromTo('.app',{opacity:0},{opacity:1,duration:.2},0);
tl.fromTo('.halo',{scale:.4,opacity:0},{scale:1,opacity:1,duration:1.2,ease:'power2.out'},0);
qa('.nodes circle').forEach((c,i)=>{const k=+c.dataset.c;tl.fromTo(c,{scale:0,opacity:0},{scale:1,opacity:1,duration:.35,ease:'back.out(2)'},.15+k*.28+(i%34)*.008)});
qa('.edges line').forEach((l,i)=>{const k=+l.dataset.c;tl.fromTo(l,{opacity:0},{opacity:1,duration:.3},.35+k*.28+(i%30)*.006)});
qa('.panel .ci').forEach((r,i)=>tl.fromTo(r,{opacity:0,x:-10},{opacity:1,x:0,duration:.25},.3+i*.12));
tl.fromTo('.gsvg',{scale:1},{scale:1.08,duration:2.6,ease:'power1.inOut',transformOrigin:'50% 50%'},.2);
""", "#0b0e16")

# =====================================================================
# S14  27.67–30.77  light th card: two-pane terminal + hard-hat mascot
# =====================================================================
add("s14-agent", 27.67, 3.1, """
<div class="palm"></div>
<div class="abs hat"><div class="helmet"></div>""" + invader_html(cell=14) + """</div>
<div class="card mono"><div class="pane l"><div class="pt">● ● ● &nbsp; agent</div>
 <div class="ln">$ graphify query "router" --depth 2</div><div class="ln c">… loading graph (170 nodes)</div><div class="ln c">✓ resolved APIRouter → 3 callers</div><div class="ln c">✓ context: 1,240 tokens (was 18,900)</div><div class="ln ok">✓ no re-read needed</div></div>
 <div class="pane r"><div class="pt">graph</div><svg viewBox="0 0 440 300">
  <g class="e" stroke="#4FC29A" stroke-width="2" fill="none"><line x1="60" y1="200" x2="200" y2="120"/><line x1="200" y1="120" x2="330" y2="80"/><line x1="200" y1="120" x2="300" y2="220"/><line x1="300" y1="220" x2="400" y2="240"/></g>
  <g class="n"><circle cx="60" cy="200" r="9" fill="#4FC29A"/><circle cx="200" cy="120" r="12" fill="#F5C542"/><circle cx="330" cy="80" r="9" fill="#4FC29A"/><circle cx="300" cy="220" r="9" fill="#7aa7ff"/><circle cx="400" cy="240" r="9" fill="#FF5C8A"/></g>
  <g class="t" fill="#c9ccd4" font-size="12" font-family="JetBrains Mono"><text x="30" y="230">router</text><text x="170" y="100">APIRouter</text><text x="300" y="60">include</text><text x="270" y="250">get_handler</text><text x="380" y="270">v2</text></g>
 </svg></div></div>
""", """
.hat{left:0;right:0;top:60px;display:flex;justify-content:center;flex-direction:column;align-items:center}
.helmet{width:110px;height:52px;background:#F5C542;border-radius:60px 60px 8px 8px;margin-bottom:-6px;box-shadow:inset 0 -8px 0 #d9a92a}
.card{top:190px;height:400px;display:flex;background:#0f1a16}
.pane{padding:22px 24px;color:#b9c4bd;font-size:15px;line-height:1.7}.l{flex:1.1;border-right:1px solid #1e2b25}.r{flex:1;position:relative}
.pt{color:#5f6d66;font-size:12px;margin-bottom:8px}.c{color:#7c8a83}.ok{color:#4FC29A}
.r svg{position:absolute;left:10px;right:10px;top:50px;width:440px;height:300px}
.n circle{transform-origin:center;transform-box:fill-box}
""" + INV_CSS, """
tl.fromTo('.hat',{opacity:0,y:-60},{opacity:1,y:0,duration:.4,ease:'bounce.out'},0);
tl.fromTo('.card',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},.05);
qa('.l .ln').forEach((l,i)=>tl.fromTo(l,{opacity:0},{opacity:1,duration:.05},.3+i*.35));
qa('.n circle').forEach((c,i)=>tl.fromTo(c,{scale:0},{scale:1,duration:.3,ease:'back.out(2)'},.5+i*.3));
qa('.e line').forEach((l,i)=>{const L=l.getTotalLength();tl.fromTo(l,{strokeDasharray:L,strokeDashoffset:L},{strokeDashoffset:0,duration:.3},.65+i*.3)});
qa('.t text').forEach((t,i)=>tl.fromTo(t,{opacity:0},{opacity:1,duration:.2},.6+i*.3));
tl.fromTo('.hat .inv',{y:0},{y:-8,duration:.3,yoyo:true,repeat:5,ease:'sine.inOut'},.6);
""", C["light"])

# =====================================================================
# S15  30.77–31.90  white: number four / Agent Skills / pills
# =====================================================================
add("s15-skills-title", 30.77, 1.13, """
<div class="abs k">number four</div>
<div class="abs big"><div class="l1">Agent</div><div class="l2">Skills</div></div>
<div class="abs pills"><span style="background:#2f7cf6">Spec</span><span style="background:#E8845A;color:#111">Plan</span><span style="background:#F5C542;color:#111">Build</span><span style="background:#4FC29A;color:#111">Test</span><span style="background:#7aa7ff;color:#111">Review</span><span style="background:#ffb3a7;color:#111">Simplify</span></div>
""", """
.k{left:0;right:0;top:440px;text-align:center;font-size:60px;color:#9a9a9a;font-weight:500}
.big{left:0;right:0;top:620px;text-align:center;font-size:190px;font-weight:900;color:#111;letter-spacing:-8px;line-height:.92}
.l1{transform:translateX(-90px)}.l2{transform:translateX(60px)}
.big div{display:block}
.pills{left:0;right:0;top:1060px;display:flex;justify-content:center;gap:14px}
.pills span{padding:8px 18px;border-radius:30px;color:#fff;font-size:22px;font-weight:700}
""", """
tl.fromTo('.k',{opacity:0,filter:'blur(8px)'},{opacity:1,filter:'blur(0px)',duration:.35},0);
tl.fromTo('.l1',{opacity:0,y:60},{opacity:1,y:0,duration:.4,ease:'power4.out'},.1);
tl.fromTo('.l2',{opacity:0,y:60},{opacity:1,y:0,duration:.4,ease:'power4.out'},.2);
qa('.pills span').forEach((p,i)=>tl.fromTo(p,{opacity:0,scale:.5,y:20},{opacity:1,scale:1,y:0,duration:.25,ease:'back.out(2)'},.55+i*.06));
""", "#ffffff")

# =====================================================================
# S16  31.90–34.60  dark: skills doc with yellow outline (scrolls)
# =====================================================================
SKILL_ROWS = [("using-agent-skills","Maps incoming work to the right skill workflow and defines shared operating rules","Starting a session or deciding which skill applies"),
              ("interview-me","One-question-at-a-time interview that extracts what the user actually wants instead of what they think they should want, until ~95% confidence","The ask is underspecified, or the user invokes \"interview me\" / \"grill me\""),
              ("idea-refine","Structured divergent/convergent thinking to turn vague ideas into concrete proposals","You have a rough concept that needs exploration"),
              ("spec-driven-development","Write a PRD covering objectives, commands, structure, code style, testing, and boundaries before any significant change","Starting a new project, feature, or significant change"),
              ("planning-and-task-breakdown","Decompose specs into small, verifiable tasks with acceptance criteria and dependency","You have a spec and need implementable tasks")]
def table(rows):
    return '<table><tr><th>Skill</th><th>What It Does</th><th>Use When</th></tr>' + "".join(f'<tr><td class="lk">{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in rows) + '</table>'
add("s16-skills-doc", 31.9, 2.7, """
<div class="abs bg"><div class="ghost"></div></div>
<div class="abs doc"><div class="in">
 <h3>All 24 Skills</h3><p>The commands above are entry points. The pack includes 24 skills total — 23 lifecycle skills plus the <code>using-agent-skills</code> meta-skill. Each skill is a structured workflow with steps, verification gates, and anti-rationalization tables. You can also reference any skill directly.</p>
 <h4>Meta - Discover which skill applies</h4>""" + table(SKILL_ROWS[:1]) + """
 <h4>Define - Clarify what to build</h4>""" + table(SKILL_ROWS[1:4]) + """
 <h4>Plan - Break it down</h4>""" + table(SKILL_ROWS[4:]) + """
</div><svg class="outline" viewBox="0 0 900 1200" preserveAspectRatio="none"><rect x="5" y="5" width="890" height="1190" rx="18" fill="none" stroke="#F5C542" stroke-width="8"/></svg></div>
""", """
.bg{inset:0;background:#0b0c10}.ghost{position:absolute;inset:-40px;background:
 repeating-linear-gradient(180deg,rgba(255,255,255,.05) 0 14px,transparent 14px 34px);filter:blur(10px);opacity:.6}
.doc{left:90px;right:90px;top:340px;height:1200px}
.in{position:absolute;inset:14px;background:#111318;border-radius:12px;padding:26px 30px;color:#c9ccd4;font-size:13px;line-height:1.5;overflow:hidden}
h3{margin:0;font-size:20px;color:#fff}h4{margin:18px 0 8px;font-size:16px;color:#fff}p{margin:10px 0 0}code{font-family:'JetBrains Mono';background:#1f2229;padding:1px 4px;border-radius:4px;font-size:11px}
table{width:100%;border-collapse:collapse;font-size:12px}th{text-align:left;color:#fff;padding:6px 8px;border-bottom:1px solid #2a2d36}td{padding:8px;border-bottom:1px solid #1f2229;vertical-align:top;width:40%}td.lk{color:#7aa7ff;text-decoration:underline;width:20%}
.outline{position:absolute;inset:0;width:100%;height:100%}
""", """
tl.fromTo('.doc',{opacity:0,y:80},{opacity:1,y:0,duration:.4,ease:'power3.out'},0);
tl.to('.in > *',{y:-260,duration:2.4,ease:'power1.inOut'},.3);
const rc=q('.outline rect'),L2=rc.getTotalLength();
tl.fromTo(rc,{strokeDasharray:L2,strokeDashoffset:L2},{strokeDashoffset:0,duration:.7,ease:'power2.inOut'},.35);
tl.fromTo('.ghost',{y:0},{y:-120,duration:2.7,ease:'none'},0);
""", C["dark"])

# =====================================================================
# S17  36.00–38.33  tan: 나민수 portrait + "made by"
# =====================================================================
add("s17-namin", 36.0, 2.33, """
<div class="abs k serif">made by 나민수</div>
<div class="abs ph"><img src="assets/namin_photo.jpg" alt=""><div class="fade"></div></div>
""", """
.k{left:0;right:0;top:400px;text-align:center;font-size:56px;color:rgba(90,60,30,.35);font-style:normal;font-family:'Pretendard';font-weight:700}
.ph{left:190px;top:480px;width:700px;height:760px;overflow:hidden}
.ph img{width:100%;height:100%;object-fit:cover;object-position:center top;display:block;
 -webkit-mask-image:linear-gradient(180deg,#000 55%,transparent 100%);mask-image:linear-gradient(180deg,#000 55%,transparent 100%)}
.fade{position:absolute;inset:0;background:linear-gradient(180deg,transparent 60%,#D6A877 100%)}
""", """
tl.fromTo('.ph',{opacity:0,scale:.92},{opacity:1,scale:1,duration:.5,ease:'power2.out'},0);
tl.fromTo('.ph img',{scale:1},{scale:1.06,duration:2.3,ease:'none'},0);
tl.fromTo('.k',{opacity:0,y:10,filter:'blur(6px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.5},.2);
""", C["tan"])

# =====================================================================
# S18  38.33–41.40  light th card: build-skills table (scrolls)
# =====================================================================
BUILD_ROWS = [("incremental-implementation","Thin vertical slices - implement, test, verify, commit. Feature flags, safe defaults, rollback-friendly changes","Any change touching more than one file"),
              ("test-driven-development","Red-Green-Refactor, test pyramid (80/15/5), test sizes, DAMP over DRY, Beyoncé Rule, browser testing","Implementing logic, fixing bugs, or changing behavior"),
              ("context-engineering","Feed agents the right information at the right time - rules files, context packing, MCP integrations","Starting a session, switching tasks, or when output quality drops"),
              ("source-driven-development","Ground every framework decision in official documentation - verify, cite","You want authoritative, source-cited code for")]
add("s18-table", 38.33, 3.07, """
<div class="palm"></div>
<div class="card doc2"><div class="in"><h4>Build - Write the code</h4>""" + table(BUILD_ROWS) + """</div></div>
""", """
.card.doc2{top:120px;height:470px;background:#111318}
.in{position:absolute;inset:0;padding:22px 26px;color:#c9ccd4;font-size:13px;line-height:1.5}
h4{margin:0 0 8px;font-size:16px;color:#fff}
table{width:100%;border-collapse:collapse;font-size:12px}th{text-align:left;color:#fff;padding:6px 8px;border-bottom:1px solid #2a2d36}td{padding:8px;border-bottom:1px solid #1f2229;vertical-align:top;width:40%}td.lk{color:#7aa7ff;text-decoration:underline;width:22%}
""", """
tl.fromTo('.card',{opacity:0,y:-30},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);
tl.fromTo('.in',{y:0},{y:-150,duration:2.7,ease:'power1.inOut'},.3);
qa('tr').forEach((r,i)=>tl.fromTo(r,{opacity:0},{opacity:1,duration:.2},.1+i*.12));
""", C["light"])

# =====================================================================
# S19  41.40–45.97  white: agent activates one skill
# =====================================================================
SKILLS16 = [("Writing","✎"),("Design","◐"),("SEO","⌕"),("Email","✉"),("Research","⌕"),("Data","▤"),("Translate","⇄"),("Voice","♪"),("Video","▶"),("Legal","⚖"),("Finance","◎"),("Marketing","◉"),("Security","⛨"),("DevOps","⚙"),("Analytics","∿"),("Coding","<>")]
cells = "".join(f'<div class="sk" data-i="{i}"><b>{g}</b><span>{n}</span></div>' for i, (n, g) in enumerate(SKILLS16))
add("s19-activate", 41.4, 4.57, """
<div class="abs top"><div class="brand"><b>◆</b> Agent Skills</div>
 <div class="task"><span class="t1">🐞 Task: Fix the login bug</span><span class="t2">✓ Bug fixed</span></div>
 <div class="line"></div>
 <div class="bot"><div class="face"><i></i><i></i></div><div class="body"></div></div>
 <div class="line"></div>
 <div class="scan"><span class="s1">⟳ Scanning 16 skills…</span><span class="s2">✓ Coding skill selected</span></div></div>
<div class="abs grid">""" + cells + """</div>
""", """
.top{left:0;right:0;top:250px;display:flex;flex-direction:column;align-items:center;gap:10px;color:#111}
.brand{font-size:20px;font-weight:700}.brand b{display:inline-grid;place-items:center;width:24px;height:24px;background:#4FC29A;color:#fff;border-radius:6px;font-size:12px;margin-right:6px}
.task{position:relative;height:40px;font-size:16px;font-weight:600}.task span{position:absolute;left:50%;transform:translateX(-50%);white-space:nowrap;border-radius:20px;padding:8px 16px}
.t1{background:#fde8e8;color:#c0392b}.t2{background:#e3f7ee;color:#1f8a5b;opacity:0}
.line{width:2px;height:24px;background:#ddd}
.bot{width:84px;height:96px;position:relative}.face{width:84px;height:50px;border:3px solid #111;border-radius:22px;display:flex;justify-content:center;gap:12px;align-items:center}.face i{width:12px;height:12px;background:#111;border-radius:50%}
.body{width:60px;height:26px;border:3px solid #111;border-radius:8px;margin:8px auto 0}
.scan{position:relative;height:40px;font-size:15px;font-weight:600}.scan span{position:absolute;left:50%;transform:translateX(-50%);white-space:nowrap;border-radius:20px;padding:8px 16px;background:#4FC29A;color:#fff}
.s2{background:#1f8a5b;opacity:0}
.grid{left:110px;right:110px;top:720px;display:grid;grid-template-columns:repeat(4,1fr);gap:22px}
.sk{height:150px;border:2px solid #e6e6e6;border-radius:18px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:#333;font-size:16px;font-weight:600;position:relative}
.sk b{font-size:34px;font-weight:400;color:#E8845A}
.sk::after{content:'';position:absolute;inset:-2px;border:3px solid #4FC29A;border-radius:18px;opacity:0}
.sk .chk{position:absolute;right:10px;top:10px;width:22px;height:22px;border-radius:50%;background:#4FC29A;color:#fff;font-size:14px;display:grid;place-items:center;opacity:0}
""", """
tl.fromTo('.top > *',{opacity:0,y:-16},{opacity:1,y:0,duration:.3,stagger:.08,ease:'power3.out'},0);
qa('.sk').forEach((c,i)=>tl.fromTo(c,{opacity:0,scale:.7},{opacity:1,scale:1,duration:.3,ease:'back.out(1.6)'},.5+i*.05));
// scan: highlight cells in a deterministic order 1.2→3.2s
const order=[1,5,6,9,10,3,12,7,2,14,4,8,0,11,13,15];
order.forEach((idx,i)=>{const c=qa('.sk')[idx];tl.fromTo(c,{'--o':0},{duration:.001},1.2+i*.125);
 tl.fromTo(c,{boxShadow:'0 0 0 0 rgba(79,194,154,0)'},{boxShadow:'0 0 0 4px rgba(79,194,154,1)',duration:.06},1.2+i*.125).to(c,{boxShadow:'0 0 0 0 rgba(79,194,154,0)',duration:.1},1.2+i*.125+.12)});
// select Coding
const coding=qa('.sk')[15];const chk=document.createElement('span');chk.className='chk';chk.textContent='✓';coding.appendChild(chk);
tl.to(qa('.sk').filter(c=>c!==coding),{opacity:.12,duration:.4,ease:'power2.out'},3.35);
tl.fromTo(coding,{boxShadow:'0 0 0 0 rgba(79,194,154,0)'},{boxShadow:'0 0 0 4px rgba(79,194,154,1)',duration:.2},3.35);
tl.fromTo(chk,{opacity:0,scale:.4},{opacity:1,scale:1,duration:.25,ease:'back.out(2)'},3.4);
tl.fromTo('.s1',{opacity:1},{opacity:0,duration:.2},3.4).fromTo('.s2',{opacity:0},{opacity:1,duration:.25},3.5);
tl.fromTo('.t1',{opacity:1},{opacity:0,duration:.2},3.9).fromTo('.t2',{opacity:0},{opacity:1,duration:.25},4.0);
tl.fromTo('.bot',{y:0},{y:-6,duration:.15,yoyo:true,repeat:9,ease:'sine.inOut'},1.2);
""", "#ffffff")

# =====================================================================
# HOST index.html
# =====================================================================
# person segments: (start, end, mode) mode: th-dark | th-light | punch
PERSON = [(0.0, 1.6, "th-dark"), (4.77, 6.47, "th-light"), (8.85, 9.8, "punch"), (18.43, 20.63, "th-light"), (22.93, 23.63, "punch"),
          (27.67, 30.77, "th-light"), (34.6, 36.0, "punch"), (38.33, 41.4, "th-light"), (45.97, 49.62, "punch")]

# captions: (start, end, text, style, y, accent)
# style: sans | sansD (dark text) | serif | serifD | script
S = "sans"; SD = "sansD"; SE = "serif"; SED = "serifD"; SC = "script"
CAPS = [
 (0.0,0.36,"Don't start",S,860),(0.36,0.92,"vibe coding",S,860),(0.92,1.26,"with Claude",S,860),(1.26,1.6,"Code",S,860),
 (1.6,1.96,"unless",SD,1300),(1.96,2.26,"installed",SD,1300),(2.26,2.6,"THESE",SED,1300),(2.6,3.53,"THESE\n4 PLUGINS",SED,1300,"4 PLUGINS"),
 (3.6,4.12,"THE FIRST",SE,1330),(4.12,4.77,"THE FIRST\nPONYTAIL",SE,1330,"PONYTAIL"),
 (4.9,5.4,"optimizes",S,860),(5.4,5.7,"Claude",S,860),(5.7,6.0,"Code's",S,860),(6.0,6.44,"output",S,860),
 (6.44,6.64,"cuts",S,1300),(6.64,6.82,"your",S,1300),(6.82,7.02,"token",S,1300),(7.02,7.6,"usage by",S,1300),(8.36,8.85,"without losing",S,1300),
 (9.14,9.8,"any accuracy",SE,1300),
 (11.48,11.72,"which gives",SC,1220),(11.72,12.32,"which gives\nClaude Code",SC,1220),(12.58,13.02,"UNLIMITED",SE,1260,"UNLIMITED"),(13.02,13.57,"UNLIMITED\nUSAGE",SE,1260,"UNLIMITED\nUSAGE"),
 (13.74,14.42,"CONNECTING IT",SE,1330),(14.56,15.42,"300",SE,1330),(15.42,15.74,"FREE",SE,1330),(15.74,16.45,"AI PROVIDERS",SE,1330),
 (16.68,16.92,"SO THE",SE,1330),(16.92,17.14,"MOMENT",SE,1330),(17.14,17.3,"THAT",SE,1330),(17.3,17.62,"YOUR USAGE",SE,1330),(17.62,17.88,"LIMIT",SE,1330),(17.88,18.43,"RUNS OUT",SE,1330),
 (18.66,19.02,"automatically",S,860),(19.02,19.34,"switch",S,860),(19.34,19.62,"you to",S,860),(19.62,19.98,"the next",S,860),(19.98,20.22,"best",S,860),(20.22,20.4,"model",S,860),
 (20.7,20.88,"GIVE YOU",SE,1180),(20.88,21.02,"UP TO",SE,1180),(21.02,21.6,"1.6",SE,1180),(21.6,22.02,"BILLION",SE,1180),(22.02,22.36,"FREE",SE,1180),(22.36,22.93,"TOKENS",SE,1180),
 (22.93,23.32,"every single",SE,1300),(23.32,23.63,"month",SE,1300),
 (24.9,25.14,"TURNS",SE,1360),(25.14,25.3,"YOUR",SE,1360),(25.3,25.5,"ENTIRE",SE,1360),(25.5,26.02,"CODE",SE,1360),(26.02,26.44,"INTO A",SE,1360),(26.44,26.76,"KNOWLEDGE",SE,1360),(26.76,27.67,"GRAPH",SE,1360),
 (27.76,28.04,"your agent",S,860),(28.04,28.5,"doesn't",S,860),(28.5,28.68,"waste",S,860),(28.68,29.0,"tokens",S,860),(29.0,29.26,"by",S,860),(29.26,29.74,"re-reading",S,860),(29.74,30.02,"files",S,860),(30.02,30.32,"again",S,860),(30.32,30.77,"and again",S,860),
 (32.32,32.56,"WHICH IS",SE,1300),(32.56,32.82,"A PACK",SE,1300),(32.82,33.04,"OF 24",SE,1300),(33.04,33.52,"SKILLS",SE,1300),(33.52,33.94,"THAT",SE,1300),(33.94,34.24,"VIBE",SE,1300),(34.24,34.6,"CODE",SE,1300),
 (34.6,34.84,"like a",SE,1300,"like a"),(34.84,35.44,"real senior",SE,1300),(35.44,36.0,"real senior\nengineer",SE,1300,"engineer"),
 (36.0,36.3,"built by",SD,1300),(36.3,36.64,"the former",SD,1300),(36.64,37.28,"AI engineering",SD,1300),(37.28,37.76,"director",SD,1300),(37.76,38.33,"at Google",SD,1300),
 (38.36,38.54,"It has",S,860),(38.54,38.84,"dedicated",S,860),(38.84,39.48,"skills",S,860),(39.48,40.1,"planning",S,860),(40.1,40.66,"coding",S,860),(40.66,41.16,"testing",S,860),(41.16,41.4,"publishing",S,860),
 (41.7,41.84,"AND IT",SED,1420),(41.84,42.4,"ACTIVATES",SED,1420),(42.4,42.58,"THE RIGHT",SED,1420),(42.58,42.84,"ONE",SED,1420),(42.84,43.24,"AT THE",SED,1420),(43.24,43.62,"SPECIFIC",SED,1420),(43.62,44.06,"STAGES",SED,1420),(44.06,44.6,"OF CODING",SED,1420),(44.6,45.24,"IT NEEDS",SED,1420),(45.24,45.54,"ALL",SED,1420),(45.54,45.97,"ON ITS OWN",SED,1420),
 (46.0,46.18,"So if you",S,1300),(46.18,46.36,"want",S,1300),(46.36,46.52,"to try",S,1300),(46.52,46.68,"them",S,1300),(46.68,46.92,"all out",S,1300),(46.92,47.04,"for",S,1300),(47.04,47.56,"yourselves",S,1300),
 (47.64,47.86,"comment",SE,1300),(47.86,48.44,"comment\n\"Coding\"",SE,1300,"\"Coding\""),(48.54,49.0,"send the link",S,1300),(49.0,49.62,"to you directly",S,1300),
]


HOST_CSS = """
body{margin:0;background:#000;font-family:'Pretendard',sans-serif}
#root{position:relative;width:100%;height:100%;overflow:hidden;background:#111}
#root *{box-sizing:border-box}
.clip{position:absolute;inset:0}
/* ---- person layer (placeholder: 나민수 cut-out) ---- */
.person .pbg{position:absolute;left:40px;right:40px;top:760px;bottom:0;border-radius:80px 80px 0 0;background:#cfd8d6}
.person.th-dark .pbg{background:#c8d0d0}
.person .pbg.full{inset:0;border-radius:0;background:radial-gradient(70% 60% at 50% 35%,#5f6f6e,#2f3a3a 100%)}
.person .pwrap{position:absolute;left:0;right:0;bottom:0;height:1000px;display:flex;justify-content:center;align-items:flex-end;overflow:hidden}
.person .pwrap img{width:960px;display:block;transform-origin:50% 30%}
.person.punch .pwrap{height:1920px;align-items:center}
.person.punch .pwrap img{width:1500px;transform-origin:50% 35%}
/* ---- captions ---- */
.caption{position:absolute;left:0;right:0;text-align:center;white-space:pre-line;pointer-events:none}
.caption span{display:inline-block}
.sans span,.sansD span{font-family:'Pretendard';font-weight:800;font-size:64px;line-height:1.15;color:#fff;text-shadow:0 4px 20px rgba(0,0,0,.45),0 0 2px rgba(0,0,0,.5)}
.sansD span{color:#111;text-shadow:none}
.serif span,.serifD span{font-family:'Instrument Serif';font-style:italic;font-size:120px;line-height:.95;color:#fff;letter-spacing:-2px;text-shadow:0 6px 30px rgba(0,0,0,.5)}
.serifD span{color:#111;text-shadow:none}
.script span{font-family:'Instrument Serif';font-style:italic;font-size:76px;line-height:1;color:#E8845A;text-shadow:none}
.caption b{font-weight:inherit;background:linear-gradient(180deg,#F3A784,#E8845A 55%,#fff 120%);-webkit-background-clip:text;background-clip:text;color:transparent}
.caption.sans b,.caption.serif.cy b{background:none;color:#7FE3E8}
.caption.serifD b,.caption.sansD b{background:none;color:#BE6C4A}
"""

def host(scenes, person, caps, dur, title="reel remake", extra_css="", cy_words=('like a','engineer','"Coding"')):
    person_tweens = "".join(f"tl.fromTo('#person-{i} img',{{scale:{1.55 if m=='punch' else 1}}},{{scale:{1.62 if m=='punch' else 1.03},duration:{b-a:.3f},ease:'sine.inOut'}},{a});\n" for i,(a,b,m) in enumerate(person))
    subs = ""
    for sid, (st, du, _) in scenes.items():
        subs += f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="scenes/{sid}.html" data-start="{st}" data-duration="{du}" data-track-index="0" data-width="{W}" data-height="{H}"></div>\n'
    persons = ""
    for i, (a, b, mode) in enumerate(person):
        bg = '<div class="pbg"></div>' if mode != "punch" else '<div class="pbg full"></div>'
        persons += f'<div id="person-{i}" class="clip person {mode}" data-start="{a}" data-duration="{b-a:.3f}" data-track-index="1">{bg}<div class="pwrap"><img src="assets/namin_cut.png" alt="나민수" data-layout-allow-overflow></div></div>\n'
    caps_json = json.dumps(caps, ensure_ascii=False)
    cy = json.dumps(list(cy_words), ensure_ascii=False)
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width={W},height={H}">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
{FONTS}
{HOST_CSS}
{extra_css}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}">
{subs}
{persons}
<div id="captions"></div>
<audio id="voice" src="assets/voice.m4a" data-start="0" data-duration="{dur}" data-track-index="9"></audio>
</div>
<script>
const CAPS={caps_json};
const host=document.getElementById('captions');
const CY=new Set({cy});
CAPS.forEach((c,i)=>{{const [s,e,text,style,y,acc]=c;const d=document.createElement('div');d.id='cap-'+i;d.className='clip caption '+style+(acc&&CY.has(acc)?' cy':'');
 d.dataset.start=s;d.dataset.duration=(e-s).toFixed(3);d.dataset.trackIndex=8;d.style.top=y+'px';d.style.bottom='auto';
 const esc=(t)=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;');let html=esc(text);if(acc)html=html.replace(esc(acc),'<b>'+esc(acc)+'</b>');
 d.innerHTML='<span>'+html+'</span>';host.appendChild(d)}});
const tl=gsap.timeline({{paused:true}});
CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');const serif=c[3].startsWith('serif')||c[3]==='script';
 if(serif)tl.fromTo(el,{{opacity:0,y:18,filter:'blur(8px)'}},{{opacity:1,y:0,filter:'blur(0px)',duration:.22,ease:'power2.out'}},c[0]);
 else tl.fromTo(el,{{opacity:0,scale:.82}},{{opacity:1,scale:1,duration:.14,ease:'back.out(2.5)'}},c[0]);}});
{person_tweens}
window.__timelines["main"]=tl;
</script></body></html>
"""

def write_all(root, scenes, host_html):
    os.makedirs(os.path.join(root, "scenes"), exist_ok=True)
    for sid, (st, du, html) in scenes.items():
        with open(os.path.join(root, "scenes", sid + ".html"), "w") as f:
            f.write(html)
    with open(os.path.join(root, "index.html"), "w") as f:
        f.write(host_html)

if __name__ == "__main__":
    write_all(ROOT, SCENES, host(SCENES, PERSON, CAPS, DUR, title="4 plugins reel — motion graphics remake"))
    print(f"wrote {len(SCENES)} scenes + index.html; captions={len(CAPS)}; persons={len(PERSON)}")
