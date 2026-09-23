#!/usr/bin/env python3
"""Making-of for AI학교_새로운영상1탄 (클로드 코드 플러그인 5개).
Right: finished reel. Left: NLE-style timeline + live wireframe + build log, all driven by the
real edit data in ../owen-new (cuts.json, index.html CAPS/scenes, build.py CAM, mix.py SFX).
Run: python3 build.py"""
import os, re, json, html
ROOT = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(ROOT, "..", "owen-new")
W, H = 1920, 1080
T0 = 2.4                    # reel starts here
CUTS = json.load(open(os.path.join(O, "cuts.json")))
RD = CUTS["duration"]
DUR = round(T0 + RD + 2.8, 2)

idx = open(os.path.join(O, "index.html")).read()
CAPS = json.loads(re.search(r"const CAPS=(\[.*?\]);\n", idx).group(1))
SCENES = [(m.group(1), float(m.group(2)), float(m.group(3))) for m in re.finditer(r'<div id="(o[\w-]+)"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"', idx)]
bsrc = open(os.path.join(O, "build.py")).read()
CAM = eval(re.search(r"\nCAM = (\[.*?\])\n", bsrc, re.S).group(1))
msrc = open(os.path.join(O, "mix.py")).read()
SFX = eval(re.search(r"\nSFX = (\[.*?\n\])", msrc, re.S).group(1))
WORDS = len(json.load(open(os.path.join(O, "src/transcript.json")))["words"])

KIND = {"o00": "HEAD COPY", "o01": "INSTALLER", "o02": "OVERLAY ₩0", "o19": "OVERLAY 댓글"}
def kind(sid):
    if sid[:3] in KIND: return KIND[sid[:3]]
    if "title" in sid: return "TITLE CARD"
    return {"o15": "LOGO", "o16": "GRID 6", "o17": "BEFORE/AFTER", "o18": "CHECKLIST"}.get(sid[:3], "UI CARD")
SCOL = {"TITLE CARD": "#8ea2c8", "UI CARD": "#64d2ff", "HEAD COPY": "#E8845A", "INSTALLER": "#E8845A"}

# ---------------------------------------------------------------- timeline geometry
TL_X, TL_W = 170, 1030      # track area inside panel
px = lambda t: TL_X + t / RD * TL_W
tracks = [("자막", 0), ("씬", 1), ("인물", 2), ("효과음", 3), ("배경음", 4)]
TRY = lambda i: 70 + i * 50
blocks = []                 # (x, y, w, h, color, label, reveal_time)
for i, s in enumerate(CUTS["segments"]):
    blocks.append((px(s["out_start"]), TRY(2), px(s["out_end"]) - px(s["out_start"]) - 2, 34, "#2f4a6b" if i % 2 else "#3a5a80", "", s["out_start"]))
for sid, st, du in SCENES:
    k = kind(sid); c = SCOL.get(k, "#4FC29A")
    blocks.append((px(st), TRY(1), max(px(st + du) - px(st) - 2, 3), 34, c, sid[:3], st))
for c in CAPS:
    blocks.append((px(c[0]), TRY(0), max(px(c[1]) - px(c[0]) - 2, 3), 34, "#d6f3ff", "", c[0]))
sfx_marks = [(px(t), f) for t, f, g in SFX]

# ---------------------------------------------------------------- log lines (time in reel seconds; negative = intro)
LOG = [
 (-2.2, "dim", "$ hyperframes making-of · AI학교_새로운영상1탄"),
 (-2.0, "", "[load]    src/20260923_151826.mp4 · 1920×1080 · 59.94fps · 66.7s"),
 (-1.7, "", f"[stt]     faster-whisper small · ko · {WORDS} words · word timestamps"),
 (-1.4, "", "[scan]    intro noise 0.0–11.8s dropped · 14 pauses > 0.28s"),
 (-1.1, "ok", f"[cut]     cut.py → person_cut.mp4 · {len(CUTS['segments'])} segments · 66.7s → {RD}s"),
 (-0.8, "", f"[build]   build.py → {len(SCENES)} scenes · {len(CAPS)} captions · {len(CAM)} camera keys"),
 (-0.5, "", f"[mix]     mix.py → bed + {len(SFX)} sfx · loudnorm −14 LUFS"),
 (-0.2, "ok", "[check]   hyperframes check ✓ 0 errors → render 1080×1920"),
]
def cam_desc(m, z, tw):
    return {"card": "card · UI 위 / 인물 아래", "full": "full · 인물 풀프레임", "hide": "hide · 풀 그래픽"}[m] + (f" · zoom {z}" if m != "hide" and z != 1 else "") + (f" · tween {tw}s" if tw else "")
for sid, st, du in SCENES:
    LOG.append((st, "scn", f"▶ scene  {sid:<16} {kind(sid):<12} {st:5.2f}–{st+du:5.2f}s"))
for t, m, z, tw in CAM:
    LOG.append((t + .01, "cam", f"◧ camera {cam_desc(m, z, tw)}"))
for c in CAPS:
    acc = f"  accent {c[5]}" if c[5] else ""
    LOG.append((c[0] + .02, "cap", f"✎ caption “{c[2]}”{acc}"))
for t, f, g in SFX:
    if f in ("soft-pop", "ui-tick") and any(abs(t - x[0]) < .15 and x[1] == f for x in SFX if x[0] < t): continue
    LOG.append((t + .03, "sfx", f"♪ sfx    {f} {g}dB"))
LOG.sort(key=lambda x: x[0])
LOG += [(RD + .3, "ok", f"[render]  renders/AI학교_새로운영상1탄_클로드코드플러그인5개.mp4 · {RD}s"),
        (RD + .9, "ok", "[notion]  ai 학교 › 촬영본 › 새로운 영상 1탄 · 완성본 + 썸네일 + 리틀리 ✓"),
        (RD + 1.5, "ok", "[cafe]    AI 자동화&수익화 정보 · westudyssat/6211 ✓"),
        (RD + 2.1, "dim", "done.")]
LH, NVIS = 27, 14

STEPS = [("원본", -2.0), ("받아쓰기", -1.7), ("컷 편집", -1.1), ("씬·카메라", 0), ("자막", .02), ("사운드", -.5), ("렌더", RD + .3), ("업로드", RD + .9)]

# ---------------------------------------------------------------- wireframe states at each camera key / scene
WF_W, WF_H = 270, 480; sc = WF_W / 1080
def box(cls, x, y, w, h, label):
    return f'<div class="wb {cls}" style="left:{x*sc:.0f}px;top:{y*sc:.0f}px;width:{w*sc:.0f}px;height:{h*sc:.0f}px"><span>{html.escape(label)}</span></div>'
wf_states = []   # (time, inner_html)
def scene_at(t):
    cur = None
    for sid, st, du in SCENES:
        if st <= t + 1e-3 < st + du and not sid.startswith(("o02", "o19")): cur = sid
    return cur
def ovl_at(t):
    for sid, st, du in SCENES:
        if sid.startswith(("o02", "o19")) and st <= t + 1e-3 < st + du: return sid
keys = sorted(set([t for t, *_ in CAM] + [st for _, st, _ in SCENES]))
for t in keys:
    m = [c for c in CAM if c[0] <= t + 1e-3][-1][1]
    sid = scene_at(t) or ""
    parts = []
    if m == "card":
        parts += [box("ui", 50, 150, 980, 540, f"{kind(sid)} · {sid}"), box("per", 40, 760, 1000, 1160, "PERSON · card"), box("cap", 140, 712, 800, 70, "CAPTION")]
    elif m == "full":
        parts += [box("per", 0, 0, 1080, 1920, "PERSON · full"), box("cap", 140, 1373, 800, 70, "CAPTION")]
    else:
        parts += [box("gfx", 0, 0, 1080, 1920, f"{kind(sid)} · {sid}"), box("cap", 140, 1373, 800, 70, "CAPTION")]
    o = ovl_at(t)
    if o: parts.append(box("ovl", 120, 230, 840, 330, kind(o)))
    wf_states.append((t, "".join(parts)))

# ---------------------------------------------------------------- HTML
def b_html():
    out = []
    for i, (x, y, w, h, c, lab, rt) in enumerate(blocks):
        out.append(f'<div class="blk" id="b{i}" style="left:{x:.1f}px;top:{y}px;width:{w:.1f}px;height:{h}px;background:{c}">{lab}</div>')
    for i, (x, f) in enumerate(sfx_marks):
        out.append(f'<div class="sm" id="m{i}" style="left:{x:.1f}px;top:{TRY(3)}px"></div>')
    return "".join(out)
ruler = "".join(f'<div class="tick" style="left:{px(s):.1f}px"><span data-layout-allow-overflow>{s}s</span></div>' for s in range(0, int(RD) + 1, 5))
log_html = "".join(f'<div class="ln {c}" id="l{i}">{html.escape(t)}</div>' for i, (_, c, t) in enumerate(LOG))
wf_html = "".join(f'<div class="wfs" id="w{i}">{h}</div>' for i, (_, h) in enumerate(wf_states))
steps_html = "".join(f'<div class="st" id="s{i}"><i>{i+1}</i>{n}</div>' for i, (n, _) in enumerate(STEPS))

js = [f"const T0={T0},RD={RD};"]
for i, (x, y, w, h, c, lab, rt) in enumerate(blocks):
    js.append(f"tl.fromTo('#b{i}',{{opacity:0,scaleX:0}},{{opacity:1,scaleX:1,duration:.25,ease:'power2.out'}},{max(T0 + rt - .6, .1):.2f});")
for i, (t, f, g) in enumerate(SFX):
    js.append(f"tl.fromTo('#m{i}',{{opacity:0,scaleY:0}},{{opacity:1,scaleY:1,duration:.15}},{max(T0 + t - .6, .1):.2f});")
for i, (t, c, _) in enumerate(LOG):
    at = T0 + t
    js.append(f"tl.fromTo('#l{i}',{{opacity:0,x:-8}},{{opacity:1,x:0,duration:.12}},{at:.2f});")
    if i >= NVIS: js.append(f"tl.to('#logcol',{{y:{-(i-NVIS+1)*LH},duration:.12,ease:'power1.out'}},{at:.2f});")
for i, (t, _) in enumerate(wf_states):
    js.append(f"tl.set('#w{i}',{{autoAlpha:1}},{T0 + t:.2f});")
    if i: js.append(f"tl.set('#w{i-1}',{{autoAlpha:0}},{T0 + t:.2f});")
    js.append(f"tl.fromTo('#w{i} .wb',{{opacity:0,scale:.96}},{{opacity:1,scale:1,duration:.2,stagger:.05}},{T0 + t:.2f});")
for i, (n, t) in enumerate(STEPS):
    js.append(f"tl.set('#s{i}',{{attr:{{class:'st on'}}}},{T0 + t:.2f});")
js.append(f"tl.fromTo('#ph',{{x:0}},{{x:{TL_W},duration:RD,ease:'none'}},T0);")
js.append(f"const tc=document.getElementById('tc');tl.fromTo({{v:0}},{{v:0}},{{v:RD,duration:RD,ease:'none',onUpdate:function(){{const v=this.targets()[0].v;tc.textContent=v.toFixed(2)+'s / '+RD.toFixed(2)+'s'}}}},T0);")
js.append("tl.fromTo('#src',{opacity:1},{opacity:0,duration:.3},T0-.3);tl.fromTo('#srcl',{opacity:1},{opacity:0,duration:.3},T0-.3);")
js.append("tl.fromTo('#srcimg',{scale:1},{scale:1.08,duration:T0,ease:'none'},0);")
js.append("tl.fromTo('#cutfx',{scaleX:1},{scaleX:0.726,duration:.6,ease:'power2.inOut'},T0-1.3);")
js.append(f"tl.fromTo('#done',{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4,ease:'power3.out'}},{T0+RD+.3:.2f});")
js.append("tl.fromTo('#hdr, #tlp, #wfp, #logp, #phone',{opacity:0,y:16},{opacity:1,y:0,duration:.4,stagger:.08,ease:'power3.out'},0);")

HTML = f"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width={W},height={H}">
<title>Making-of — 클로드 코드 플러그인 5개</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:'Pretendard';src:url('assets/fonts/pretendard.woff2') format('woff2');font-weight:100 900}}
@font-face{{font-family:'JetBrains Mono';src:url('assets/fonts/JetBrainsMono[wght].ttf') format('truetype');font-weight:100 800}}
body{{margin:0;background:#000}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;font-family:'Pretendard',sans-serif;color:#d6e2f5;
 background:radial-gradient(50% 60% at 78% 50%,rgba(100,210,255,.10),transparent 70%),repeating-linear-gradient(0deg,rgba(100,210,255,.04) 0 1px,transparent 1px 40px),repeating-linear-gradient(90deg,rgba(100,210,255,.04) 0 1px,transparent 1px 40px),linear-gradient(180deg,#07101c,#0d1b2e)}}
#root *{{box-sizing:border-box}}
.pnl{{position:absolute;background:rgba(10,20,36,.85);border:1px solid rgba(100,210,255,.22);border-radius:16px;box-shadow:0 20px 50px rgba(0,0,0,.4)}}
.ph-t{{position:absolute;left:18px;top:12px;font:700 14px 'JetBrains Mono';letter-spacing:2px;color:#64d2ff}}
#hdr{{position:absolute;left:60px;top:34px;width:1170px;height:70px}}
#hdr h1{{margin:0;font-size:32px;font-weight:800;color:#fff;letter-spacing:-.5px}}#hdr h1 b{{color:#64d2ff}}
#steps{{position:absolute;left:0;top:48px;display:flex;gap:8px}}
.st{{display:flex;align-items:center;gap:7px;font-size:15px;font-weight:700;color:#5b6f8f;padding:5px 12px 5px 6px;border-radius:20px;border:1px solid #1d2a3e}}
.st i{{font-style:normal;display:grid;place-items:center;width:22px;height:22px;border-radius:50%;background:#1d2a3e;color:#8ea2c8;font-size:12px}}
.st.on{{color:#07101c;background:#64d2ff;border-color:#64d2ff}}.st.on i{{background:#07101c;color:#64d2ff}}
#tlp{{left:60px;top:132px;width:1230px;height:340px}}
.trk{{position:absolute;left:18px;font-size:15px;font-weight:700;color:#8ea2c8}}
.lane{{position:absolute;left:{TL_X}px;width:{TL_W}px;height:34px;background:rgba(29,42,62,.55);border-radius:6px}}
.blk{{position:absolute;border-radius:5px;transform-origin:left center;font:700 10px 'JetBrains Mono';color:#07101c;padding:10px 3px 0;overflow:hidden;white-space:nowrap}}
.sm{{position:absolute;width:3px;height:34px;margin-left:-1px;background:#FFD60A;border-radius:2px;transform-origin:bottom}}
.bed{{position:absolute;left:{TL_X}px;top:{TRY(4)+8}px;width:{TL_W}px;height:18px;border-radius:9px;background:linear-gradient(90deg,rgba(79,194,154,.25),rgba(79,194,154,.55) 10%,rgba(79,194,154,.45) 90%,rgba(79,194,154,.2))}}
.tick{{position:absolute;top:44px;height:{5*50+20}px;border-left:1px dashed rgba(142,162,200,.18)}}.tick span{{position:absolute;top:-4px;left:4px;font:600 11px 'JetBrains Mono';color:#5b6f8f}}
#ph{{position:absolute;left:{TL_X}px;top:40px;width:2px;height:{5*50+30}px;background:#ff3b30;box-shadow:0 0 10px #ff3b30}}
#ph::before{{content:'';position:absolute;left:-6px;top:-4px;border:7px solid transparent;border-top-color:#ff3b30}}
#tc{{position:absolute;right:20px;top:10px;font:700 15px 'JetBrains Mono';color:#fff}}
#wfp{{left:60px;top:494px;width:360px;height:552px}}
#wf{{position:absolute;left:45px;top:46px;width:{WF_W}px;height:{WF_H}px;border:1px dashed rgba(100,210,255,.35);border-radius:10px}}
.wfs{{position:absolute;inset:0;visibility:hidden;opacity:0}}
.wb{{position:absolute;border:2px solid;border-radius:6px;display:flex;align-items:flex-start;padding:4px 6px;font:700 10px 'JetBrains Mono';letter-spacing:.5px}}
.wb span{{background:rgba(7,16,28,.85);padding:1px 4px;border-radius:3px;white-space:nowrap}}
.wb.ui{{border-color:#64d2ff;color:#64d2ff;background:rgba(100,210,255,.08)}}.wb.per{{border-color:#8ea2c8;color:#c9d6ee;background:repeating-linear-gradient(45deg,rgba(142,162,200,.08) 0 8px,transparent 8px 16px)}}
.wb.gfx{{border-color:#4FC29A;color:#7be3b5;background:rgba(79,194,154,.08)}}.wb.cap{{border-color:#fff;color:#fff;border-style:dashed;align-items:center;justify-content:center}}
.wb.ovl{{border-color:#FFD60A;color:#FFD60A;background:rgba(255,214,10,.08)}}
#logp{{left:440px;top:494px;width:850px;height:552px;overflow:hidden}}
#logwin{{position:absolute;left:20px;right:20px;top:44px;height:{NVIS*LH}px;overflow:hidden}}
#logcol{{position:absolute;left:0;right:0;top:0}}
.ln{{height:{LH}px;font:500 15.5px/{LH}px 'JetBrains Mono','Pretendard';color:#c9d6ee;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.ln.dim{{color:#5b6f8f}}.ln.ok{{color:#4FC29A}}.ln.scn{{color:#64d2ff;font-weight:700}}.ln.cam{{color:#8ea2c8}}.ln.cap{{color:#fff}}.ln.sfx{{color:#FFD60A}}
#phone{{position:absolute;left:1345px;top:28px;width:540px;height:960px;border-radius:44px;background:#000;padding:14px;box-shadow:0 0 0 2px rgba(100,210,255,.35),0 30px 80px rgba(0,0,0,.6),0 0 90px rgba(100,210,255,.18)}}
#scr{{position:absolute;inset:14px;border-radius:32px;overflow:hidden;background:#000}}
#reel{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#src{{position:absolute;inset:0;background:#000;display:flex;align-items:center;overflow:hidden}}
#srcimg{{width:100%;display:block}}
#cutfx{{position:absolute;left:0;right:0;bottom:120px;height:10px;background:#ff3b30;transform-origin:left;border-radius:5px}}
#srcl{{position:absolute;left:0;right:0;bottom:60px;text-align:center;font:700 20px 'JetBrains Mono';color:#fff}}
#plabel{{position:absolute;left:1345px;top:1004px;width:540px;text-align:center;font:700 16px 'JetBrains Mono';color:#8ea2c8;letter-spacing:2px}}
#done{{position:absolute;left:1345px;top:430px;width:540px;display:flex;justify-content:center;opacity:0;z-index:5}}
#done span{{background:#64d2ff;color:#07101c;font-weight:900;font-size:30px;padding:14px 30px;border-radius:16px;box-shadow:0 20px 50px rgba(0,0,0,.5)}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
<div id="hdr"><h1>MAKING OF · <b>클로드 코드 플러그인 5개</b></h1><div id="steps">{steps_html}</div></div>
<div class="pnl" id="tlp"><div class="ph-t">TIMELINE</div><div id="tc">0.00s / {RD:.2f}s</div>{ruler}
 {''.join(f'<div class="trk" style="top:{TRY(i)+8}px">{n}</div><div class="lane" style="top:{TRY(i)}px"></div>' for n, i in tracks)}
 <div class="bed"></div>{b_html()}<div id="ph"></div></div>
<div class="pnl" id="wfp"><div class="ph-t">FRAME LAYOUT</div><div id="wf">{wf_html}</div></div>
<div class="pnl" id="logp"><div class="ph-t">BUILD LOG</div><div id="logwin"><div id="logcol">{log_html}</div></div></div>
<div id="phone"><div id="scr">
 <video id="reel" class="clip" src="assets/reel_silent.mp4" data-start="{T0}" data-duration="{RD}" data-media-start="0" data-track-index="1" muted></video>
 <div id="src"><img id="srcimg" src="assets/source_frame.jpg" alt=""><div id="cutfx"></div></div><div id="srcl">원본 66.7s → 컷 {RD}s</div>
</div></div>
<div id="plabel">FINAL · 1080×1920 · {RD}s</div>
<div id="done"><span>✓ 렌더 · 노션 · 카페 완료</span></div>
<audio id="voice" src="assets/reel_audio.m4a" data-start="{T0}" data-duration="{RD}" data-track-index="9"></audio>
</div>
<script>
const tl=gsap.timeline({{paused:true}});
{chr(10).join(js)}
window.__timelines["main"]=tl;
</script></body></html>
"""
open(os.path.join(ROOT, "index.html"), "w").write(HTML)
print(f"blocks={len(blocks)} sfx={len(sfx_marks)} log={len(LOG)} wf={len(wf_states)} dur={DUR}")
