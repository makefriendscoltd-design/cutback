"""AI 학교 7일차 — Kallaway(DaxdLQbOJXR) 레퍼런스 문법 테스트 빌드.

3단 고정 레이아웃: 상단 애셋 무대(0~1130) / 중간 1~3어절 자막(1150) / 하단 인물 카드(60,1250,960x600).
애셋 없는 대사는 얼굴 풀프레임 펀치인. 챕터 전환은 하드컷, 무대 안에서 요소를 쌓는다.
모든 시각은 출력 타임라인 초(captions.json / edit-plan.json 기준).
"""
from pathlib import Path
import json, re, html, os
PERSON_POS = os.environ.get('PERSON_POS', '62')

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
C = R / 'composition'
A = C / 'assets'
A.mkdir(parents=True, exist_ok=True)
plan = json.loads((R / 'edit-plan.json').read_text())
D = plan['duration']
caps = json.loads((R / 'captions.json').read_text())
TB = ROOT / 'videos/day7-tailbite-20260915/assets'


def link(n, p):
    q = A / n
    if not q.exists():
        q.symlink_to(Path(p).resolve())


link('person.mp4', TB / 'person.mp4')
link('vlog-discussion.mp4', TB / 'vlog-discussion.mp4')
link('font.ttf', ROOT / 'verification-renders/20260911_180156-r01-v19/composition/assets/Pretendard-SemiBold.ttf')
link('black.ttf', ROOT / 'verification-renders/20260911_180156-r01-v7/composition/assets/Pretendard-Black.ttf')
link('gsap.min.js', ROOT / 'videos/day1-sc-vlog/composition/assets/vendor/gsap.min.js')
link('hud-intro.mp4', R / 'assets/hud-intro-1080x1130.mp4')
link('hud-f03.png', ROOT / 'videos/_assets/hud-captures-20260915/f03-t6000.png')
pages = sorted((ROOT / 'videos/day7-basic-mix-v4-20260915/assets/generated/memo').glob('page-*.png'))
assert len(pages) == 8, pages
for i, p in enumerate(pages):
    link(f'page-{i+1:02d}.png', p)

# ---------------------------------------------------------------- chapter times (output seconds)
HOOK, FACE1, GRID, TERM, FILES, PROMPT, STRIKE, BOARD, DIAG, FACE2, CTA, BOOK = (
    0.0, 2.646667, 4.986667, 7.866667, 9.54, 12.873333, 14.873333, 16.753333, 18.4, 22.293333, 25.573333, 27.766667)
LIGHT = [(GRID, DIAG), (CTA, D)]
DARK = [(HOOK, GRID), (DIAG, FACE2)]
FULL = [(FACE2, CTA)]

RED = '#ff434b'
INK = '#171717'
PAPER = '#f1efe9'
NIGHT = '#0b0b0d'

css = f'''
@font-face{{font-family:Pretendard;src:url(assets/font.ttf);font-weight:600}}
@font-face{{font-family:Black;src:url(assets/black.ttf);font-weight:900}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:#000;width:1080px;height:1920px;overflow:hidden}}
#basic{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000;font-family:Pretendard,sans-serif}}
.clip{{position:absolute}}
.bg{{left:0;top:0;width:1080px;height:1920px;z-index:1}}
.bg.light{{background:{PAPER}}} .bg.dark{{background:{NIGHT}}}
.stage{{left:0;top:0;width:1080px;height:1130px;overflow:hidden;z-index:5;color:{INK}}}
.stage.dark{{color:#fff}}
#person-box{{position:absolute;left:60px;top:1235px;width:960px;height:640px;z-index:10;overflow:hidden;border-radius:28px;box-shadow:0 26px 50px #0005;transform-origin:50% 45%}}
#person-box video{{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:50% PERSON_POS%}}
.caption{{left:30px;right:30px;top:1150px;z-index:20;font:900 58px/1.2 Black;letter-spacing:-1.5px;text-align:center;white-space:nowrap;color:{INK}}}
.caption.onfull{{top:1340px;color:#fff;-webkit-text-stroke:5px #171d20;paint-order:stroke fill;text-shadow:0 5px 6px #000,0 0 12px #000e}}
.caption.ondark{{color:#fff}}
.accent{{color:{RED}}}
.pop{{opacity:0}}
/* headline */
.hl{{position:absolute;left:40px;right:40px;top:96px;text-align:center;font:900 96px/1.08 Black;letter-spacing:-4px}}
.hl span{{display:inline-block}} .hl .w{{margin:0 8px}}
.hl em{{font-style:normal;color:{RED}}}
.head{{left:40px;right:40px;top:360px;z-index:30;text-align:center;font:900 122px/1.1 Black;letter-spacing:-5px;color:white;-webkit-text-stroke:7px black;paint-order:stroke fill;text-shadow:0 8px 9px #0009}}
.head span{{display:block}}
.hl.white{{top:74px;font-size:86px;color:#fff;text-shadow:0 4px 18px #000c,0 0 40px #000a}}
.hud-shade{{position:absolute;left:0;top:0;width:1080px;height:420px;background:linear-gradient(#050a0fee,#050a0f00)}}
.scrib{{position:absolute;overflow:visible}}
.scrib path{{fill:none;stroke:{RED};stroke-width:9;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1}}
.scrib.ink path{{stroke:{INK}}} .scrib.white path{{stroke:#fff}}
/* tiles (logos) */
.tile{{position:absolute;border-radius:22%;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 22px 40px #0004;font-family:Black}}
.tile.school{{background:{RED};color:#fff}}
.tile.school b{{font:900 108px/1 Black;letter-spacing:-4px}} .tile.school small{{font:900 34px/1 Black;margin-top:10px;letter-spacing:2px}}
.tile.codex{{background:#111;color:#fff;border:6px solid #2a2a2a}}
.tile.codex b{{font:900 54px/1 Black;letter-spacing:-2px}} .tile.codex i{{font:600 28px/1 Pretendard;font-style:normal;color:#9aa;margin-bottom:12px;letter-spacing:4px}}
.wordmark{{position:absolute;left:0;right:0;top:62px;text-align:center;font:900 54px/1 Black;letter-spacing:-2px}}
.wordmark i{{display:inline-block;width:52px;height:52px;border-radius:14px;background:{RED};vertical-align:-10px;margin-right:16px}}
/* memo cards */
.memo{{position:absolute;overflow:hidden;border-radius:10px;box-shadow:0 14px 26px #0003;background:#fff}}
.memo img{{width:100%;height:100%;object-fit:cover;object-position:top;display:block}}
.memo.glow{{box-shadow:0 0 0 6px #3ddc84,0 0 44px 10px #3ddc84aa}}
.pill{{position:absolute;padding:14px 30px;border-radius:999px;background:{RED};color:#fff;font:900 36px/1 Black;box-shadow:0 12px 24px #0004;white-space:nowrap}}
.pill.green{{background:#1fbf6a}}
.num{{position:absolute;left:66px;top:34px;font:900 150px/1 Black;color:{RED};letter-spacing:-8px}}
.num small{{display:block;font:600 30px/1 Pretendard;color:{INK};letter-spacing:6px;margin:-4px 0 0 10px}}
/* windows */
.win{{position:absolute;border-radius:26px;background:#fff;box-shadow:0 30px 60px #0004;border:3px solid #d9d6cf;overflow:hidden}}
.win .bar{{height:64px;background:#ecebe6;border-bottom:2px solid #d9d6cf;display:flex;align-items:center;padding:0 26px;gap:12px;font:600 26px Pretendard;color:#666}}
.win .bar i{{width:20px;height:20px;border-radius:50%;background:#ff5f57}} .win .bar i:nth-child(2){{background:#febc2e}} .win .bar i:nth-child(3){{background:#28c840}}
.win .bar span{{margin-left:auto;background:#fff;border-radius:999px;padding:6px 22px;font-size:24px}}
.win.term{{background:#0f1115;border-color:#333}} .win.term .bar{{background:#1b1e24;border-color:#333;color:#aaa}}
.term .body{{padding:40px 44px;font:600 40px/1.6 "SF Mono",Menlo,monospace;color:#e6e6e6;white-space:pre}}
.term .body .p{{color:#3ddc84}} .term .body .c{{color:#9aa}}
.cur{{display:inline-block;width:22px;height:46px;background:#e6e6e6;vertical-align:-8px;margin-left:6px}}
.row{{display:flex;align-items:center;gap:22px;height:74px;padding:0 30px;border-bottom:2px solid #efede8;font:600 32px Pretendard;color:{INK}}}
.row .th{{width:44px;height:58px;border-radius:5px;overflow:hidden;box-shadow:0 3px 8px #0003;flex:none}} .row .th img{{width:100%;height:100%;object-fit:cover;object-position:top}}
.row em{{font-style:normal;color:#8a8a8a;margin-left:auto;font-size:26px}}
.counter{{position:absolute;right:40px;top:80px;background:{INK};color:#fff;padding:12px 26px;border-radius:999px;font:900 32px/1 Black;letter-spacing:0}}
/* prompt */
.prompt{{position:absolute;left:80px;top:440px;width:920px;height:250px;border-radius:44px;background:#fff;border:5px solid {INK};box-shadow:0 30px 60px #0003;padding:44px 170px 44px 48px;font:600 44px/1.5 Pretendard;color:{INK}}}
.prompt .ph{{color:#a5a5a5}}
.send{{position:absolute;right:34px;bottom:34px;width:110px;height:110px;border-radius:50%;background:{RED};color:#fff;display:flex;align-items:center;justify-content:center;font:900 60px/1 Black}}
/* strike scene */
.folder{{position:absolute;width:250px;height:150px;border-radius:18px;background:#fff;border:4px solid {INK};display:flex;align-items:center;justify-content:center;font:900 40px Black;box-shadow:8px 10px 0 #d9d6cf}}
.arrow{{position:absolute;width:6px;background:{INK};transform-origin:top}}
/* board */
.ttl{{position:absolute;left:0;right:0;top:64px;text-align:center;font:900 72px/1.1 Black;letter-spacing:-3px}}
.ttl em{{font-style:normal;color:{RED}}}
.frame{{position:absolute;left:50px;top:220px;width:980px;height:600px;border-radius:26px;overflow:hidden;background:#050a0f;box-shadow:0 30px 60px #0005;border:3px solid #333}}
.frame .bar{{height:60px;background:#1b1e24;display:flex;align-items:center;padding:0 26px;gap:12px;font:600 26px Pretendard;color:#aaa}}
.frame .bar i{{width:20px;height:20px;border-radius:50%;background:#ff5f57}} .frame .bar i:nth-child(2){{background:#febc2e}} .frame .bar i:nth-child(3){{background:#28c840}}
.frame .bar span{{margin-left:auto;background:#0f1115;border-radius:999px;padding:6px 22px;font-size:24px}}
.frame .view{{position:absolute;left:0;top:60px;width:980px;height:540px;overflow:hidden}}
.frame .view img{{position:absolute;left:0;top:0;width:3840px;height:2160px;transform-origin:0 0}}
.live{{display:inline-block;width:22px;height:22px;border-radius:50%;background:#3ddc84;margin-right:14px;vertical-align:4px;box-shadow:0 0 0 6px #3ddc8444}}
/* diagram */
.node-lbl{{position:absolute;text-align:center;font:600 30px/1 Pretendard;color:#bbb;white-space:nowrap}}
.post{{position:absolute;left:236px;top:726px;width:608px;height:352px;border-radius:22px;background:#fff;box-shadow:0 30px 60px #000a}}
.vlog{{left:246px;top:736px;width:588px;height:332px;border-radius:14px;object-fit:cover;z-index:7}}
/* cta */
.cta{{position:absolute;left:0;right:0;top:80px;text-align:center;font:900 92px/1.1 Black;letter-spacing:-4px}}
.cta em{{font-style:normal;color:{RED}}} .cta span{{display:block}} .cta .sub{{font:900 68px/1.1 Black;letter-spacing:-3px;margin-top:8px}}
.comment{{position:absolute;left:90px;top:400px;width:900px;border-radius:30px;background:#fff;border:4px solid {INK};padding:36px 44px;font:600 40px/1.5 Pretendard;color:{INK};box-shadow:12px 14px 0 #d9d6cf}}
.comment .top{{border-bottom:3px solid #eee;padding-bottom:18px;font-size:34px;color:#666}}
.entry{{display:flex;align-items:center;margin-top:28px}}
.avatar{{display:inline-flex;border-radius:50%;width:70px;height:70px;align-items:center;justify-content:center;background:{INK};color:#fff;margin-right:26px;font-family:Black}}
.entry b{{color:{RED};font:900 64px/1 Black}} .entry .ph{{color:#b5b5b5;font-size:40px}}
.reply{{margin-left:auto;padding:14px 34px;border-radius:999px;background:{INK};color:#fff;font:900 34px/1 Black}}
.workbook{{position:absolute;left:150px;top:380px;width:780px;height:660px;background:#fff9e9;border-radius:26px;border:4px solid {INK};box-shadow:14px 16px 0 {RED};padding:52px 56px;color:{INK};font:600 40px Pretendard}}
.workbook small{{color:#a63837;font-size:32px;letter-spacing:2px}}
.workbook strong{{display:block;font:900 96px/1.1 Black;letter-spacing:-4px;margin:22px 0 30px}}
.workbook .line{{height:5px;background:#e3d6c0;margin:30px 0}}
.workbook b{{color:{RED}}}
.stamp{{position:absolute;right:44px;bottom:44px;padding:20px 34px;border:5px solid {RED};border-radius:12px;color:{RED};font:900 54px/1 Black;transform:rotate(-8deg);background:#fff9e9}}
.chip{{position:absolute;left:120px;top:988px;padding:18px 36px;border-radius:999px;background:{INK};color:#fff;font:900 40px/1 Black;box-shadow:0 14px 30px #0004;white-space:nowrap}}
'''

parts = []
anim = []
sfx = {'whoosh': [], 'click': [], 'pop': [], 'typing': []}


def r4(x):
    return round(x, 4)


def clip(html_, a, b, z, cls='', extra=''):
    parts.append(f'<div class="clip {cls}" style="z-index:{z};{extra}" data-start="{r4(a)}" data-duration="{r4(b-a)}" data-track-index="{z}">{html_}</div>')


def pop(sel, t, dur=.32, scale=.6, y=30, ease='back.out(1.7)', click=True):
    anim.append(f'tl.fromTo("{sel}",{{opacity:0,scale:{scale},y:{y}}},{{opacity:1,scale:1,y:0,duration:{dur},ease:"{ease}",immediateRender:false}},{r4(t)});')
    if click:
        sfx['click'].append(r4(t))


def rise(sel, t, dur=.3, y=60):
    anim.append(f'tl.fromTo("{sel}",{{opacity:0,y:{y},scale:.96}},{{opacity:1,y:0,scale:1,duration:{dur},ease:"power3.out",immediateRender:false}},{r4(t)});')


def draw(sel, t, dur=.35):
    anim.append(f'tl.to("{sel}",{{strokeDashoffset:0,duration:{dur},ease:"power2.inOut"}},{r4(t)});')


def bump(sel, t, y=-14, dur=.12):
    anim.append(f'tl.to("{sel}",{{y:{y},duration:{dur},yoyo:true,repeat:1,ease:"power2.inOut"}},{r4(t)});')


def scrib(x, y, w, h, d, cls='', sid=''):
    return f'<svg class="scrib {cls}" id="{sid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px" viewBox="0 0 {w} {h}"><path pathLength="1" d="{d}"/></svg>'


def typed(text, sid):
    return ''.join(f'<span class="ch" id="{sid}-{i}" style="opacity:0">{html.escape(ch)}</span>' for i, ch in enumerate(text))


def type_in(sid, n, t0, t1):
    step = (t1 - t0) / max(n, 1)
    for i in range(n):
        anim.append(f'tl.set("#{sid}-{i}",{{opacity:1}},{r4(t0+i*step)});')
    sfx['typing'].append(r4(t0))


# ---------------------------------------------------------------- backgrounds + person window
for a, b in LIGHT:
    clip('', a, b, 1, 'bg light')
for a, b in DARK:
    clip('', a, b, 1, 'bg dark')
parts.append(f'<div id="person-box"><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{D}" data-track-index="0" muted></video></div>')
VCARD = '{left:60,top:1235,width:960,height:640,scale:1,borderRadius:28}'
VFULL = '{left:0,top:0,width:1080,height:1920,borderRadius:0}'
FULLG = '{left:0,top:0,width:1080,height:1920,borderRadius:0}'
for a, b in FULL:
    anim.append(f'tl.set("#person-box",{VFULL},{r4(a)});tl.set("#person",{{objectPosition:"50% 45%"}},{r4(a)});')
    anim.append(f'tl.set("#person-box",{VCARD},{r4(b)});tl.set("#person",{{objectPosition:"50% PERSON_POS%"}},{r4(b)});')
    anim.append(f'tl.fromTo("#person-box",{{scale:1.14}},{{scale:1.19,duration:{r4(b-a)},ease:"sine.out",immediateRender:false}},{r4(a)});')
    
    sfx['whoosh'] += [r4(a), r4(b)]

# ---------------------------------------------------------------- H0 hook  0 ~ 2.65
a, b = HOOK, GRID
parts.append(f'<video id="hud-intro" class="clip" src="assets/hud-intro.mp4" data-start="0" data-duration="{r4(b-a)}" data-media-start="0" data-track-index="3" style="left:0;top:0;width:1080px;height:1130px;z-index:3;object-fit:cover" muted></video>')
# 승인 헤드카피(정본 v19/day3 규칙): "POV: AI 미친자가 / 저지른 일", 1초, 같은 서체·위치. 문구 변경 금지.
parts.append('<div id="head" class="clip head" data-start="0" data-duration="1" data-track-index="30"><span>POV: AI 미친자가</span><span>저지른 일</span></div>')
sfx['whoosh'] += [HOOK, FACE1]

# ---------------------------------------------------------------- S2 memo grid  4.99 ~ 7.87
a, b = GRID, TERM
wm = '<div class="wordmark pop" id="wm2"><i></i>AI 학교 · 글감</div>'
grid = ''
for i in range(8):
    col, row = i % 4, i // 4
    grid += f'<div class="memo pop" id="g{i}" style="left:{84+col*234}px;top:{230+row*332}px;width:210px;height:280px"><img src="assets/page-{i+1:02d}.png"></div>'
badge = '<div class="pill green pop" id="g-badge" style="left:540px;top:180px">글감 후보 ↑</div>'
clip(wm + grid + badge, a, b, 5, 'stage')
pop('#wm2', a, click=False)
for i in range(8):
    pop(f'#g{i}', a + .12 + i * .13, scale=.7, y=40)
anim.append(f'tl.set("#g2",{{boxShadow:"0 0 0 6px #3ddc84,0 0 44px 10px #3ddc84aa"}},{r4(6.81)});tl.fromTo("#g2",{{scale:1}},{{scale:1.08,duration:.22,ease:"power2.out"}},{r4(6.81)});'); sfx['pop'].append(6.81)
anim.append(f'tl.to("#g2",{{scale:1.04,duration:.3,yoyo:true,repeat:2}},{r4(7.05)});')
pop('#g-badge', 7.29, y=-20)

# ---------------------------------------------------------------- S3 terminal  7.87 ~ 9.54
a, b = TERM, FILES
term = ('<div class="num pop" id="n1">01<small>STEP</small></div>'
        '<div class="win term pop" id="term" style="left:90px;top:300px;width:900px;height:520px"><div class="bar"><i></i><i></i><i></i><span>terminal</span></div>'
        '<div class="body"><span class="c">~/ai-school</span>\n<span class="p">$</span> ' + typed('codex', 'tc') + '<span class="cur" id="cur"></span></div></div>'
        '<div class="tile codex pop" id="tile-codex" style="left:720px;top:640px;width:230px;height:230px"><i>OPENAI</i><b>Codex</b></div>')
clip(term, a, b, 5, 'stage')
pop('#n1', a, y=-30); rise('#term', a + .08)
type_in('tc', 5, 8.46, 8.95)
anim.append(f'tl.fromTo("#cur",{{opacity:1}},{{opacity:0,duration:.35,yoyo:true,repeat:5}},{r4(a+.1)});')
anim.append(f'tl.fromTo("#tile-codex",{{opacity:0,scale:.3,rotation:-40}},{{opacity:1,scale:1,rotation:-8,duration:.4,ease:"back.out(1.8)",immediateRender:false}},{r4(9.12)});'); sfx['pop'].append(9.12)

# ---------------------------------------------------------------- S4 files  9.54 ~ 12.87
a, b = FILES, PROMPT
rows = ''.join(f'<div class="row pop" id="f{i}"><div class="th"><img src="assets/page-{i+1:02d}.png"></div>memo-{i+1:02d}.md<em>오늘</em></div>' for i in range(8))
files = ('<div class="num pop" id="n2">02<small>STEP</small></div>'
         '<div class="win pop" id="fwin" style="left:90px;top:300px;width:900px;height:690px"><div class="bar"><i></i><i></i><i></i><span>memos/</span></div>' + rows + '</div>'
         '<div class="counter pop" id="fcount" style="top:212px;right:90px">0 files</div>'
         '<div class="memo pop" id="fly" style="left:780px;top:760px;width:210px;height:280px;transform:rotate(8deg)"><img src="assets/page-08.png"></div>')
clip(files, a, b, 5, 'stage')
pop('#n2', a, y=-30); rise('#fwin', a + .08); pop('#fcount', a + .3, click=False)
anim.append('const fc={n:0};')
for i in range(8):
    pop(f'#f{i}', 9.98 + i * .16, scale=.9, y=20)
anim.append(f'tl.to(fc,{{n:8,duration:{r4(8*.16)},ease:"none",snap:"n",onUpdate:()=>{{document.getElementById("fcount").textContent=fc.n+" files"}}}},{r4(9.98)});')
anim.append(f'tl.fromTo("#fly",{{opacity:0,y:420,scale:.7,rotation:20}},{{opacity:1,y:0,scale:1,rotation:8,duration:.42,ease:"power3.out",immediateRender:false}},{r4(11.6)});'); sfx['pop'].append(11.6)
bump('#fwin', 11.98, y=-12)
anim.append(f'tl.to("#fcount",{{scale:1.18,duration:.12,yoyo:true,repeat:1}},{r4(12.0)});')

# ---------------------------------------------------------------- S5 prompt  12.87 ~ 14.87
a, b = PROMPT, STRIKE
ptxt = '메모 폴더 읽고 글감 목록 뽑아줘'
prompt = ('<div class="num pop" id="n3">03<small>STEP</small></div>'
          '<div class="prompt pop" id="prompt">' + typed(ptxt, 'pc') + '<span class="cur" id="cur2" style="background:#171717;height:50px"></span>'
          '<div class="send pop" id="send">↑</div></div>'
          + scrib(50, 400, 980, 330, 'M60 40 C 300 -10, 900 -10, 950 120 C 990 260, 700 320, 300 300 C 60 290, 20 200, 90 110', '', 'p-ring'))
clip(prompt, a, b, 5, 'stage')
pop('#n3', a, y=-30); rise('#prompt', a + .08)
type_in('pc', len(ptxt), 13.05, 14.1)
anim.append(f'tl.fromTo("#cur2",{{opacity:1}},{{opacity:0,duration:.3,yoyo:true,repeat:7}},{r4(a+.1)});')
pop('#send', 14.21, scale=.3, click=False); sfx['pop'].append(14.21)
anim.append(f'tl.to("#send",{{scale:1.15,duration:.14,yoyo:true,repeat:1}},{r4(14.6)});')
draw('#p-ring path', 14.3, .45)

# ---------------------------------------------------------------- S6a strike  14.87 ~ 16.75
a, b = STRIKE, BOARD
cards = ''.join(f'<div class="memo pop" id="s{i}" style="left:{150+i*300}px;top:150px;width:210px;height:280px"><img src="assets/page-{i+3:02d}.png"></div>' for i in range(3))
arrows = ''.join(f'<div class="arrow pop" id="ar{i}" style="left:{252+i*300}px;top:440px;height:150px"></div>' for i in range(3))
folders = ''.join(f'<div class="folder pop" id="fo{i}" style="left:{130+i*300}px;top:610px">{t}</div>' for i, t in enumerate(['주제 A', '주제 B', '주제 C']))
q = '<div class="pill pop" id="q-pill" style="left:420px;top:830px;background:#171717">직접 분류?</div>'
x = scrib(60, 60, 960, 780, 'M40 40 L 920 740 M 920 40 L 40 740', '', 'x-mark')
clip(cards + arrows + folders + q + x, a, b, 5, 'stage')
for i in range(3):
    pop(f'#s{i}', a + i * .1, scale=.8)
    anim.append(f'tl.fromTo("#ar{i}",{{opacity:0,scaleY:0}},{{opacity:1,scaleY:1,duration:.25,ease:"power2.out",immediateRender:false}},{r4(a+.4+i*.08)});')
    pop(f'#fo{i}', a + .6 + i * .1, scale=.8)
pop('#q-pill', 15.35, y=20)
draw('#x-mark path', 15.87, .38); sfx['pop'].append(15.87)
anim.append(f'tl.to("#s0,#s1,#s2,#fo0,#fo1,#fo2,#q-pill",{{x:14,duration:.06,yoyo:true,repeat:5}},{r4(15.95)});')

# ---------------------------------------------------------------- S6b board  16.75 ~ 18.4  (real F-03 capture)
a, b = BOARD, DIAG
board = ('<div class="ttl pop" id="b-ttl"><span class="live"></span>글감 목록 <em>실시간</em></div>'
         '<div class="frame pop" id="frame"><div class="bar"><i></i><i></i><i></i><span>SNS 자동화학부 관제</span></div>'
         '<div class="view"><img id="h-f03" src="assets/hud-f03.png" alt="SNS 자동화학부 관제"></div></div>')
clip(board, a, b, 5, 'stage')
pop('#b-ttl', a, y=-20, click=False); rise('#frame', a + .06)
VW, VH = 980., 540.
S0 = VW / 3840.


def hx(cx, cy, z):
    sc = S0 * z
    return round(VW / 2 - cx * sc, 2), round(VH / 2 - cy * sc, 2), round(sc, 5)


def hset(cx, cy, z, t):
    x_, y_, sc = hx(cx, cy, z); anim.append(f'tl.set("#h-f03",{{x:{x_},y:{y_},scale:{sc}}},{r4(t)});')


def hto(cx, cy, z, dur, t, ease='power2.inOut'):
    x_, y_, sc = hx(cx, cy, z); anim.append(f'tl.to("#h-f03",{{x:{x_},y:{y_},scale:{sc},duration:{dur},ease:"{ease}"}},{r4(t)});')


hset(1920, 1080, 1.0, a)
hto(760, 620, 2.4, .9, a + .15, 'power2.out')
hto(760, 1240, 2.4, r4(b - (a + 1.05)), a + 1.05, 'none')

# ---------------------------------------------------------------- D7 diagram (dark)  18.4 ~ 22.29
a, b = DIAG, FACE2
nodes = ''.join(f'<div class="memo pop" id="d{i}" style="left:{165+i*300}px;top:100px;width:150px;height:200px"><img src="assets/page-{i+1:02d}.png"></div>' for i in range(3))
lbls = ''.join(f'<div class="node-lbl pop" id="dl{i}" style="left:{165+i*300}px;width:150px;top:316px">{t}</div>' for i, t in enumerate(['강의 후', '카페', '지하철']))
conn = scrib(0, 352, 1080, 170, 'M240 12 C 240 120, 470 90, 520 160 M540 12 L 540 160 M840 12 C 840 120, 610 90, 560 160', 'white', 'c-up')
tile2 = '<div class="tile school pop" id="d-tile" style="left:430px;top:470px;width:220px;height:220px"><b>AI</b><small>학교</small></div>'
conn2 = scrib(0, 690, 1080, 50, 'M540 4 L 540 40', 'white', 'c-down')
post = '<div class="post pop" id="post"></div>'
clip(nodes + lbls + conn + tile2 + conn2 + post, a, b, 5, 'stage dark')
parts.append(f'<video id="vlog" class="clip vlog pop" src="assets/vlog-discussion.mp4" data-start="{r4(21.17)}" data-duration="{r4(b-21.17)}" data-media-start="0" data-track-index="7" muted></video>')
for i in range(3):
    pop(f'#d{i}', a + i * .12, scale=.6)
    anim.append(f'tl.fromTo("#dl{i}",{{opacity:0}},{{opacity:1,duration:.2}},{r4(a+.3+i*.08)});')
draw('#c-up path', 19.3, .5)
pop('#d-tile', 19.75, scale=.4, click=False); sfx['pop'].append(19.75)
draw('#c-down path', 20.5, .2)
pop('#post', 21.17, scale=.7, y=60, click=False); pop('#vlog', 21.17, scale=.7, y=60, click=False); sfx['pop'].append(21.17)

# ---------------------------------------------------------------- S9/S10 CTA  25.57 ~ end
a, b = CTA, D
cta = ('<div class="cta" id="cta"><span class="pop" id="c1">댓글에 <em>“시작”</em></span><span class="sub pop" id="c2">무료 워크북 받기</span></div>'
       + scrib(560, 190, 300, 36, 'M6 26 C 80 4, 200 30, 292 8', '', 'c-under')
       + '<div class="comment pop" id="comment"><div class="top">댓글</div><div class="entry"><span class="avatar">나</span><span class="ph" id="c-ph">댓글 달기…</span><b id="c-word" style="opacity:0">시작</b><span class="reply" id="c-reply">게시</span></div></div>'
       + '<div class="workbook pop" id="wb"><small>내 경험으로 글쓰기</small><strong>시작<br>워크북</strong><div class="line"></div>메모에서 뽑은 <b>글감 목록</b><div class="line"></div><div class="stamp pop" id="stamp">무료 워크북</div></div>'
       + '<div class="chip pop" id="chip">↳ 대댓글로 드려요</div>')
clip(cta, a, b, 5, 'stage')
pop('#c1', a, y=-20); pop('#c2', a + .14, y=-20)
draw('#c-under path', a + .35, .3)
rise('#comment', a + .2)
anim.append(f'tl.set("#c-ph",{{opacity:0}},{r4(26.2)});tl.fromTo("#c-word",{{opacity:0,x:16,scale:.8}},{{opacity:1,x:0,scale:1,duration:.18,ease:"back.out(1.7)",immediateRender:false}},{r4(26.2)});'); sfx['pop'].append(26.2)
anim.append(f'tl.to("#c-reply",{{scale:1.15,duration:.12,yoyo:true,repeat:1}},{r4(26.81)});')
anim.append(f'tl.to("#comment",{{y:-60,opacity:0,duration:.22,ease:"power2.in"}},{r4(BOOK)});')
anim.append(f'tl.fromTo("#wb",{{opacity:0,y:120,rotation:-4,scale:.9}},{{opacity:1,y:0,rotation:0,scale:1,duration:.34,ease:"back.out(1.4)",immediateRender:false}},{r4(BOOK+.12)});')
anim.append(f'tl.fromTo("#stamp",{{opacity:0,scale:1.6,rotation:-8}},{{opacity:1,scale:1,rotation:-8,duration:.22,ease:"power3.out",immediateRender:false}},{r4(28.3)});'); sfx['pop'].append(28.3)
bump('#wb', 28.9, y=-16)
pop('#chip', 29.65, y=30); sfx['pop'].append(29.65)
anim.append(f'tl.to("#stamp",{{scale:1.1,duration:.13,yoyo:true,repeat:1}},{r4(30.2)});')

# ---------------------------------------------------------------- captions
terms = ['미쳤나', 'AI 학교', '글감', '코덱스', '메모', '프롬프트', '콘텐츠', '경험', '댓글', '워크북', '시작']


def caption_cls(t):
    if any(a <= t < b for a, b in FULL):
        return 'caption onfull'
    if any(a <= t < b for a, b in DARK):
        return 'caption ondark'
    return 'caption'


for i, c in enumerate(caps):
    t = html.escape(c['text'])
    for w in terms:
        if w in t:
            t = t.replace(w, '<span class="accent">' + w + '</span>', 1); break
    parts.append(f'<div id="cap{i}" class="clip {caption_cls(c["start"])}" data-start="{c["start"]}" data-duration="{round(c["end"]-c["start"],6)}" data-track-index="20">{t}</div>')

# ---------------------------------------------------------------- sfx timing + hard cuts
sfx['whoosh'] += [GRID, TERM, FILES, PROMPT, STRIKE, BOARD, DIAG, CTA, BOOK]
(R / 'timing.json').write_text(json.dumps({k: sorted(set(round(x, 4) for x in v)) for k, v in sfx.items()}, indent=1, ensure_ascii=False))
(C / 'index.html').write_text(
    ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>' + css + '</style></head><body>'
    f'<div id="basic" data-composition-id="basic" data-width="1080" data-height="1920" data-start="0" data-duration="{D}">' + ''.join(parts) + '</div>'
    '<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});' + ''.join(anim) + 'window.__timelines.basic=tl;</script></body></html>').replace('PERSON_POS', PERSON_POS))
print('built', D, 'clips', len(parts), 'anims', len(anim), {k: len(v) for k, v in sfx.items()})
