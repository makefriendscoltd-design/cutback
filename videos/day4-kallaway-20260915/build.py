"""AI 학교 4일차 — Kallaway 레퍼런스 문법 + 관제탑 인트로 (day7 승인 방식 이식).

3단 고정 레이아웃: 상단 무대(0~1130) / 자막(1150) / 인물 카드(60,1235,960x640).
모든 시각은 출력 타임라인 초(captions.json / edit-plan.json 기준).
"""
from pathlib import Path
import json, re, html, os
PERSON_POS = os.environ.get('PERSON_POS', '55')

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
C = R / 'composition'
A = C / 'assets'
A.mkdir(parents=True, exist_ok=True)
plan = json.loads((R / 'edit-plan.json').read_text())
D = plan['duration']
caps = json.loads((R / 'captions.json').read_text())



def link(n, p):
    q = A / n
    if not q.exists():
        q.symlink_to(Path(p).resolve())


link('person.mp4', R / 'assets/person.mp4')
link('lecture-vlog.mp4', R / 'assets/lecture-vlog.mp4')
link('font.ttf', ROOT / 'verification-renders/20260911_180156-r01-v19/composition/assets/Pretendard-SemiBold.ttf')
link('black.ttf', ROOT / 'verification-renders/20260911_180156-r01-v7/composition/assets/Pretendard-Black.ttf')
link('gsap.min.js', ROOT / 'videos/day1-sc-vlog/composition/assets/vendor/gsap.min.js')
link('hud-intro.mp4', R / 'assets/hud-intro-1080x1130.mp4')
EB = ROOT / 'videos/day4-basic-mix-v4-20260915/assets/generated/ebook'
pages = sorted(EB.glob('page-*.png'))
assert len(pages) == 8, pages
for i, p in enumerate(pages):
    link(f'page-{i+1:02d}.png', p)
for n in ['cafe', 'class', 'hall', 'work']:
    link(f'photo-{n}.jpg', EB / f'photos/{n}.jpg')

# ---------------------------------------------------------------- chapter times (output seconds, captions.json)
HOOK, PUSH, EBOOK, TERM, FILES, PROMPT, LAYOUT, PDF, FACE, SCHOOL, NAME, CTA, INVITE = (
    0.0, 2.573333, 5.0, 8.233333, 9.873333, 13.1, 14.88, 16.36, 18.94, 21.06, 23.44, 26.42, 28.833333)
LIGHT = [(EBOOK, PDF), (NAME, D)]
DARK = [(HOOK, EBOOK), (PDF, FACE), (SCHOOL, NAME)]
FULL = [(FACE, SCHOOL)]

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


css += f'''
.drift{{position:absolute;left:0;top:0;width:1080px;height:1130px;transform-origin:50% 45%}}
.page{{position:absolute;overflow:hidden;border-radius:8px;box-shadow:0 18px 34px #0004;background:#fff}}
.page img{{width:100%;height:100%;object-fit:cover;display:block}}
.lbl{{position:absolute;padding:12px 26px;border-radius:999px;background:{INK};color:#fff;font:900 34px/1 Black;white-space:nowrap}}
.tpl{{position:absolute;background:#fff;border-radius:10px;box-shadow:0 26px 50px #0003;border:3px solid #d9d6cf;overflow:hidden}}
.slot{{position:absolute;border:4px dashed #b9b4aa;border-radius:10px}}
.tline{{position:absolute;height:18px;border-radius:9px;background:#2b2b2b}}
.pdf{{position:absolute;background:#fff;border-radius:18px;box-shadow:0 30px 60px #000a;overflow:hidden}}
.pdf img{{position:absolute;left:45px;top:26px;width:190px;height:220px;object-fit:cover;object-position:top;border-radius:4px;box-shadow:0 6px 14px #0003}}
.pdf .band{{position:absolute;left:0;right:0;bottom:0;height:100px;background:{RED};color:#fff;font:900 64px/100px Black;text-align:center;letter-spacing:-2px}}
.fname{{position:absolute;text-align:center;font:600 34px/1 "SF Mono",Menlo,monospace;color:#ddd;white-space:nowrap}}
.invite{{position:absolute;left:150px;top:390px;width:780px;height:640px;background:#fff9e9;border-radius:26px;border:4px solid {INK};box-shadow:14px 16px 0 {RED};padding:52px 56px;color:{INK};font:600 44px Pretendard}}
.invite small{{color:#a63837;font:900 36px/1 Black;letter-spacing:2px}}
.invite strong{{display:block;font:900 110px/1.06 Black;letter-spacing:-4px;margin:26px 0 24px}}
.invite .line{{height:5px;background:#e3d6c0;margin:24px 0}}
.invite b{{color:{RED};font:900 56px/1 Black}}
.vframe{{position:absolute;border-radius:30px;background:#fff;box-shadow:0 30px 60px #000a}}
.vid{{border-radius:22px;object-fit:cover}}
'''


def stage(html_, a, b, dark=False, dz=1.03):
    sid = f'dr{len(parts)}'
    clip(f'<div class="drift" id="{sid}">{html_}</div>', a, b, 5, 'stage dark' if dark else 'stage')
    if dz != 1:
        anim.append(f'tl.fromTo("#{sid}",{{scale:1}},{{scale:{dz},duration:{r4(b-a)},ease:"none",immediateRender:false}},{r4(a)});')


def glow(sel, t):
    anim.append(f'tl.set("{sel}",{{boxShadow:"0 0 0 6px #3ddc84,0 0 44px 10px #3ddc84aa"}},{r4(t)});')


# ---------------------------------------------------------------- backgrounds + person window
for a, b in LIGHT:
    clip('', a, b, 1, 'bg light')
for a, b in DARK:
    clip('', a, b, 1, 'bg dark')
parts.append(f'<div id="person-box"><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{D}" data-track-index="0" muted></video></div>')
VCARD = '{left:60,top:1235,width:960,height:640,scale:1,borderRadius:28}'
VFULL = '{left:0,top:0,width:1080,height:1920,borderRadius:0}'
for a, b in FULL:
    anim.append(f'tl.set("#person-box",{VFULL},{r4(a)});tl.set("#person",{{objectPosition:"50% 45%"}},{r4(a)});')
    anim.append(f'tl.set("#person-box",{VCARD},{r4(b)});tl.set("#person",{{objectPosition:"50% PERSON_POS%"}},{r4(b)});')
    anim.append(f'tl.fromTo("#person-box",{{scale:1.14}},{{scale:1.19,duration:{r4(b-a)},ease:"sine.out",immediateRender:false}},{r4(a)});')
    sfx['whoosh'] += [r4(a), r4(b)]

# ---------------------------------------------------------------- H0 intro: 관제탑 2.5x  0 ~ 5.0 (push-in to CORE baked from 2.573)
a, b = HOOK, EBOOK
parts.append(f'<video id="hud-intro" class="clip" src="assets/hud-intro.mp4" data-start="0" data-duration="{r4(b-a)}" data-media-start="0" data-track-index="3" style="left:0;top:0;width:1080px;height:1130px;z-index:3;object-fit:cover" muted></video>')
# 승인 헤드카피(정본 규칙): "POV: AI 미친자가 / 저지른 일", 1초, 같은 서체·위치. 문구 변경 금지.
parts.append('<div id="head" class="clip head" data-start="0" data-duration="1" data-track-index="30"><span>POV: AI 미친자가</span><span>저지른 일</span></div>')
sfx['whoosh'] += [HOOK, PUSH]

# ---------------------------------------------------------------- S1 내 글도 전자책도  5.0 ~ 8.23
a, b = EBOOK, TERM
h = '<div class="wordmark pop" id="wm1"><i></i>AI 학교 · 전자책</div>'
h += '<div class="page pop" id="e-mine" style="left:80px;top:230px;width:390px;height:520px;transform:rotate(-4deg)"><img src="assets/page-04.png"></div>'
h += '<div class="lbl pop" id="e-mine-l" style="left:205px;top:790px">내 글</div>'
h += scrib(455, 400, 140, 90, 'M10 50 C 40 10, 90 10, 128 46 M 104 26 L 128 46 L 102 64', '', 'e-arrow')
order = [2, 3, 5, 6, 7, 8, 1]
for k, pg in enumerate(order):
    h += f'<div class="page pop" id="e{k}" style="left:{580+k*20}px;top:{210+k*16}px;width:360px;height:480px;z-index:{k+2}"><img src="assets/page-{pg:02d}.png"></div>'
h += '<div class="pill green pop" id="e-badge" style="left:640px;top:880px">PDF 전자책</div>'
stage(h, a, b)
pop('#wm1', a, click=False)
rise('#e-mine', 5.55)
pop('#e-mine-l', 5.85, y=20)
draw('#e-arrow path', 6.3, .3)
for k in range(7):
    pop(f'#e{k}', 6.587 + k * .1, scale=.75, y=50)
glow('#e6', 7.38); sfx['pop'].append(7.38)
anim.append(f'tl.fromTo("#e6",{{scale:1}},{{scale:1.08,duration:.22,ease:"power2.out"}},{r4(7.38)});')
pop('#e-badge', 7.5, y=-20)
anim.append(f'tl.to("#e6",{{scale:1.03,duration:.2,yoyo:true,repeat:1}},{r4(7.85)});')

# ---------------------------------------------------------------- S2 STEP 01 코덱스  8.23 ~ 9.87
a, b = TERM, FILES
term = ('<div class="num pop" id="n1">01<small>STEP</small></div>'
        '<div class="win term pop" id="term" style="left:90px;top:300px;width:900px;height:520px"><div class="bar"><i></i><i></i><i></i><span>terminal</span></div>'
        '<div class="body"><span class="c">~/my-ebook</span>\n<span class="p">$</span> ' + typed('codex', 'tc') + '<span class="cur" id="cur"></span></div></div>'
        '<div class="tile codex pop" id="tile-codex" style="left:720px;top:660px;width:230px;height:230px"><i>OPENAI</i><b>Codex</b></div>')
stage(term, a, b)
pop('#n1', a, y=-30); rise('#term', a + .08)
type_in('tc', 5, 8.72, 9.15)
anim.append(f'tl.fromTo("#cur",{{opacity:1}},{{opacity:0,duration:.3,yoyo:true,repeat:4}},{r4(a+.1)});')
anim.append(f'tl.fromTo("#tile-codex",{{opacity:0,scale:.3,rotation:-40}},{{opacity:1,scale:1,rotation:-8,duration:.4,ease:"back.out(1.8)",immediateRender:false}},{r4(9.32)});'); sfx['pop'].append(9.32)

# ---------------------------------------------------------------- S3 STEP 02 원고와 사진  9.87 ~ 13.1
a, b = FILES, PROMPT
rowsd = [('원고-01.md', 'page-04.png'), ('원고-02.md', 'page-06.png'), ('원고-03.md', 'page-03.png'),
         ('cafe.jpg', 'photo-cafe.jpg'), ('class.jpg', 'photo-class.jpg'), ('hall.jpg', 'photo-hall.jpg'), ('work.jpg', 'photo-work.jpg')]
rows = ''.join(f'<div class="row pop" id="f{i}"><div class="th"><img src="assets/{im}"></div>{nm}<em>{"원고" if nm.endswith(".md") else "사진"}</em></div>' for i, (nm, im) in enumerate(rowsd))
files = ('<div class="num pop" id="n2">02<small>STEP</small></div>'
         '<div class="win pop" id="fwin" style="left:90px;top:300px;width:900px;height:590px"><div class="bar"><i></i><i></i><i></i><span>my-ebook/</span></div>' + rows + '</div>'
         '<div class="counter pop" id="fcount" style="top:212px;right:90px">0 files</div>'
         '<div class="page pop" id="fly1" style="left:520px;top:560px;width:210px;height:280px;transform:rotate(-6deg)"><img src="assets/page-04.png"></div>'
         '<div class="memo pop" id="fly2" style="left:740px;top:620px;width:260px;height:180px;transform:rotate(7deg)"><img src="assets/photo-cafe.jpg"></div>'
         + scrib(66, 580, 560, 330, 'M60 30 C 300 -6, 540 40, 540 170 C 540 300, 300 320, 90 290 C 10 270, 20 120, 80 40', '', 'f-ring'))
stage(files, a, b)
pop('#n2', a, y=-30); rise('#fwin', a + .08); pop('#fcount', a + .3, click=False)
anim.append(f'tl.fromTo("#fly1",{{opacity:0,y:460,rotation:18}},{{opacity:1,y:0,rotation:-6,duration:.42,ease:"power3.out",immediateRender:false}},{r4(10.3)});'); sfx['pop'].append(10.3)
anim.append(f'tl.fromTo("#fly2",{{opacity:0,y:460,rotation:-14}},{{opacity:1,y:0,rotation:7,duration:.42,ease:"power3.out",immediateRender:false}},{r4(10.72)});'); sfx['pop'].append(10.72)
bump('#fly1', 11.15, y=-18); bump('#fly2', 11.3, y=-18)
anim.append(f'tl.to("#fly1,#fly2",{{opacity:0,scale:.4,y:-260,duration:.3,ease:"power2.in",stagger:.06}},{r4(11.55)});')
anim.append('const fc={n:0};')
for i in range(7):
    pop(f'#f{i}', 11.69 + i * .15, scale=.9, y=20)
anim.append(f'tl.to(fc,{{n:7,duration:{r4(7*.15)},ease:"none",snap:"n",onUpdate:()=>{{document.getElementById("fcount").textContent=fc.n+" files"}}}},{r4(11.69)});')
draw('#f-ring path', 12.72, .35)
anim.append(f'tl.to("#fcount",{{scale:1.18,duration:.12,yoyo:true,repeat:1}},{r4(12.8)});')

# ---------------------------------------------------------------- S4 STEP 03 프롬프트  13.1 ~ 14.88
a, b = PROMPT, LAYOUT
ptxt = '원고랑 사진으로 PDF 전자책 만들어줘'
prompt = ('<div class="num pop" id="n3">03<small>STEP</small></div>'
          '<div class="prompt pop" id="prompt">' + typed(ptxt, 'pc') + '<span class="cur" id="cur2" style="background:#171717;height:50px"></span>'
          '<div class="send pop" id="send">↑</div></div>'
          + scrib(50, 400, 980, 330, 'M60 40 C 300 -10, 900 -10, 950 120 C 990 260, 700 320, 300 300 C 60 290, 20 200, 90 110', '', 'p-ring'))
stage(prompt, a, b)
pop('#n3', a, y=-30); rise('#prompt', a + .08)
type_in('pc', len(ptxt), 13.48, 14.28)
anim.append(f'tl.fromTo("#cur2",{{opacity:1}},{{opacity:0,duration:.3,yoyo:true,repeat:5}},{r4(a+.1)});')
pop('#send', 14.34, scale=.3, click=False); sfx['pop'].append(14.34)
draw('#p-ring path', 14.4, .4)
anim.append(f'tl.to("#send",{{scale:1.15,duration:.12,yoyo:true,repeat:1}},{r4(14.62)});')

# ---------------------------------------------------------------- S5 글과 사진을 배치  14.88 ~ 16.36
a, b = LAYOUT, PDF
lay = ('<div class="page pop" id="l-src1" style="left:40px;top:170px;width:210px;height:280px;transform:rotate(-5deg)"><img src="assets/page-04.png"></div>'
       '<div class="memo pop" id="l-src2" style="left:830px;top:180px;width:220px;height:160px;transform:rotate(5deg)"><img src="assets/photo-cafe.jpg"></div>'
       '<div class="tpl pop" id="tpl" style="left:285px;top:110px;width:510px;height:680px">'
       '<div class="slot" style="left:36px;top:36px;width:432px;height:380px"></div>'
       '<img class="pop" id="l-photo" src="assets/photo-cafe.jpg" style="position:absolute;left:38px;top:38px;width:428px;height:376px;object-fit:cover;border-radius:6px">'
       + ''.join(f'<div class="tline pop" id="tl{i}" style="left:36px;top:{454+i*46}px;width:{[400,432,360,280][i]}px"></div>' for i in range(4))
       + '<img id="l-final" src="assets/page-05.png" style="position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;opacity:0">'
       '</div>'
       + scrib(140, 460, 170, 150, 'M20 8 C 20 90, 70 130, 150 138 M 124 118 L 150 138 L 122 150', '', 'l-a1')
       + scrib(760, 350, 130, 130, 'M110 8 C 100 70, 60 96, 14 104 M 36 84 L 14 104 L 40 120', '', 'l-a2')
       + '<div class="pill green pop" id="l-badge" style="left:400px;top:850px">배치 완료</div>')
stage(lay, a, b)
pop('#l-src1', a, scale=.7); pop('#l-src2', a + .1, scale=.7, click=False)
rise('#tpl', a + .12)
draw('#l-a1 path', 15.25, .28)
for i in range(4):
    anim.append(f'tl.fromTo("#tl{i}",{{opacity:0,scaleX:0,transformOrigin:"0 50%"}},{{opacity:1,scaleX:1,duration:.16,ease:"power2.out",immediateRender:false}},{r4(15.4+i*.08)});')
draw('#l-a2 path', 15.74, .25)
pop('#l-photo', 15.84, scale=.8, y=0); 
anim.append(f'tl.fromTo("#l-final",{{opacity:0}},{{opacity:1,duration:.2,immediateRender:false}},{r4(16.08)});')
glow('#tpl', 16.08)
pop('#l-badge', 16.12, y=20, click=False); sfx['pop'].append(16.12)

# ---------------------------------------------------------------- S6 PDF로 저장 (dark)  16.36 ~ 18.94
a, b = PDF, FACE
pd = ''.join(f'<div class="page pop" id="p{i}" style="left:{105+(i%4)*230}px;top:{110+(i//4)*270}px;width:180px;height:240px"><img src="assets/page-{i+1:02d}.png"></div>' for i in range(8))
pd += '<div class="counter pop" id="pcount" style="top:34px;right:60px;background:#fff;color:#171717">0 pages</div>'
pd += '<div class="pdf pop" id="pdf" style="left:400px;top:330px;width:280px;height:360px"><img src="assets/page-01.png"><div class="band">PDF</div></div>'
pd += '<div class="fname pop" id="pname" style="left:340px;width:400px;top:770px">my-ebook.pdf</div>'
pd += '<div class="tile codex pop" id="p-codex" style="left:70px;top:400px;width:210px;height:210px"><i>OPENAI</i><b>Codex</b></div>'
pd += scrib(270, 440, 140, 90, 'M8 60 C 40 10, 90 10, 128 46 M 104 26 L 128 46 L 102 64', 'white', 'p-link')
pd += scrib(350, 290, 380, 470, 'M190 20 C 330 20, 370 150, 360 260 C 350 400, 250 450, 170 440 C 50 430, 10 320, 20 200 C 30 90, 110 30, 220 40', '', 'p-ring2')
pd += '<div class="pill green pop" id="p-badge" style="left:420px;top:870px">저장 완료</div>'
stage(pd, a, b, dark=True)
pop('#pcount', a, click=False)
anim.append('const pc={n:0};')
for i in range(8):
    pop(f'#p{i}', a + .04 + i * .09, scale=.7, y=30)
anim.append(f'tl.to(pc,{{n:8,duration:{r4(8*.09)},ease:"none",snap:"n",onUpdate:()=>{{document.getElementById("pcount").textContent=pc.n+" pages"}}}},{r4(a+.04)});')
for i in range(8):
    dx = 540 - (195 + (i % 4) * 230); dy = 510 - (230 + (i // 4) * 270)
    anim.append(f'tl.to("#p{i}",{{x:{dx},y:{dy},scale:.25,opacity:0,duration:.3,ease:"power2.in"}},{r4(17.08+i*.03)});')
anim.append(f'tl.fromTo("#pdf",{{opacity:0,scale:.4}},{{opacity:1,scale:1,duration:.34,ease:"back.out(1.7)",immediateRender:false}},{r4(17.3)});'); sfx['pop'].append(17.3)
glow('#pdf', 17.5)
pop('#pname', 17.5, y=16, click=False)
pop('#p-codex', 17.68, scale=.4)
draw('#p-link path', 17.9, .25)
draw('#p-ring2 path', 18.24, .4); sfx['pop'].append(18.24)
pop('#p-badge', 18.4, y=20)
bump('#pdf', 18.66, y=-14)

# ---------------------------------------------------------------- S7 AI 학교에서 함께 (dark, real lecture footage)  21.06 ~ 23.44
a, b = SCHOOL, NAME
sch = ('<div class="tile school pop" id="s-tile" style="left:730px;top:220px;width:270px;height:270px"><b>AI</b><small>학교</small></div>'
       '<div class="pill pop" id="s-pill" style="left:712px;top:620px">함께 만들기</div>'
       + scrib(640, 480, 200, 200, 'M150 10 C 150 90, 90 120, 14 150 M 40 128 L 14 150 L 44 164', 'white', 's-link')
       + scrib(700, 700, 320, 40, 'M8 26 C 100 6, 220 34, 312 12', '', 's-under'))
parts.append(f'<div id="vframe" class="clip vframe" data-start="{r4(a)}" data-duration="{r4(b-a)}" data-track-index="6" style="left:70px;top:110px;width:580px;height:920px;z-index:6"></div>')
parts.append(f'<video id="vlog" class="clip vid" src="assets/lecture-vlog.mp4" data-start="{r4(a)}" data-duration="{r4(b-a)}" data-media-start="0.2" data-track-index="7" style="left:84px;top:124px;width:552px;height:892px;z-index:7;object-position:50% 40%" muted></video>')
stage(sch, a, b, dark=True, dz=1)
pop('#s-tile', a + .1, scale=.4, click=False); sfx['pop'].append(r4(a + .1))
anim.append(f'tl.to("#s-tile",{{rotation:-6,duration:.18,yoyo:true,repeat:1,ease:"power2.inOut"}},{r4(21.7)});')
bump('#s-tile', 22.0, y=-16)
pop('#s-pill', 22.18, y=20)
draw('#s-link path', 22.35, .3)
draw('#s-under path', 22.7, .3)
bump('#s-tile', 23.05, y=-16)

# ---------------------------------------------------------------- S8 내 이름이 들어간 전자책  23.44 ~ 26.42
a, b = NAME, CTA
nm = ('<div class="page pop" id="n-cover" style="left:100px;top:110px;width:540px;height:720px;transform:rotate(-3deg)"><img src="assets/page-01.png"></div>'
      + scrib(105, 725, 230, 90, 'M120 10 C 200 8, 226 40, 212 62 C 196 86, 60 88, 20 66 C -4 50, 20 14, 140 16', '', 'n-ring')
      + '<div class="page pop" id="n-back" style="left:590px;top:290px;width:420px;height:560px;transform:rotate(5deg)"><img src="assets/page-08.png"></div>'
      + scrib(625, 530, 280, 50, 'M8 30 C 90 8, 180 40, 252 16', '', 'n-under'))
stage(nm, a, b)
rise('#n-cover', a)
draw('#n-ring path', 23.9, .4); sfx['pop'].append(23.9)
anim.append(f'tl.fromTo("#n-back",{{opacity:0,x:360,rotation:24}},{{opacity:1,x:0,rotation:5,duration:.4,ease:"power3.out",immediateRender:false}},{r4(24.54)});'); sfx['click'].append(24.54)
draw('#n-under path', 25.0, .3)
glow('#n-back', 25.64); sfx['pop'].append(25.64)
anim.append(f'tl.to("#n-back",{{scale:1.05,duration:.2,ease:"power2.out"}},{r4(25.64)});')
anim.append(f'tl.to("#n-cover",{{x:-24,duration:.3,ease:"power2.out"}},{r4(25.7)});')
bump('#n-back', 26.1, y=-14)
bump('#n-cover', 25.3, y=-12)
anim.append(f'tl.to("#n-cover",{{rotation:-5,duration:.18,yoyo:true,repeat:1}},{r4(24.2)});')

# ---------------------------------------------------------------- S9/S10 CTA 댓글에 학교 → 입시 설명회 초대  26.42 ~ end
a, b = CTA, D
cta = ('<div class="cta" id="cta"><span class="pop" id="c1">댓글에 <em>“학교”</em></span><span class="sub pop" id="c2">입시 설명회 초대</span></div>'
       + scrib(420, 262, 350, 36, 'M6 26 C 100 4, 240 30, 342 8', '', 'c-under')
       + '<div class="comment pop" id="comment"><div class="top">댓글</div><div class="entry"><span class="avatar">나</span><span class="ph" id="c-ph">댓글 달기…</span><b id="c-word" style="opacity:0">학교</b><span class="reply" id="c-reply">게시</span></div></div>'
       + '<div class="invite pop" id="inv"><small>AI 학교</small><strong>입시<br>설명회</strong><div class="line"></div><b>초대장</b><div class="stamp pop" id="stamp">초대</div></div>'
       + '<div class="chip pop" id="chip">↳ 댓글 남기면 초대드려요</div>')
stage(cta, a, b, dz=1.04)
pop('#c1', a, y=-20); pop('#c2', a + .14, y=-20)
draw('#c-under path', a + .38, .3)
rise('#comment', a + .22)
anim.append(f'tl.set("#c-ph",{{opacity:0}},{r4(27.3)});tl.fromTo("#c-word",{{opacity:0,x:16,scale:.8}},{{opacity:1,x:0,scale:1,duration:.18,ease:"back.out(1.7)",immediateRender:false}},{r4(27.3)});'); sfx['pop'].append(27.3)
anim.append(f'tl.to("#c-reply",{{scale:1.15,duration:.12,yoyo:true,repeat:1}},{r4(28.0)});'); sfx['click'].append(28.0)
bump('#comment', 28.4, y=-12)
bump('#c1', 27.62, y=-10)
anim.append(f'tl.to("#c-word",{{scale:1.12,duration:.12,yoyo:true,repeat:1}},{r4(27.72)});')
anim.append(f'tl.to("#comment",{{y:-60,opacity:0,duration:.22,ease:"power2.in"}},{r4(INVITE)});')
anim.append(f'tl.fromTo("#inv",{{opacity:0,y:120,rotation:-4,scale:.9}},{{opacity:1,y:0,rotation:0,scale:1,duration:.34,ease:"back.out(1.4)",immediateRender:false}},{r4(INVITE+.12)});')
anim.append(f'tl.fromTo("#stamp",{{opacity:0,scale:1.6,rotation:-8}},{{opacity:1,scale:1,rotation:-8,duration:.22,ease:"power3.out",immediateRender:false}},{r4(29.5)});'); sfx['pop'].append(29.5)
bump('#inv', 30.0, y=-16)
pop('#chip', 30.4, y=30); sfx['pop'].append(30.4)
anim.append(f'tl.to("#stamp",{{scale:1.1,duration:.13,yoyo:true,repeat:1}},{r4(30.75)});')

# ---------------------------------------------------------------- captions
terms = ['미쳤나', 'AI 학교', '전자책', '코덱스', '원고', '프롬프트', '사진', 'PDF', '막막', '내 이름', '댓글', '설명회']


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
sfx['whoosh'] += [EBOOK, TERM, FILES, PROMPT, LAYOUT, PDF, SCHOOL, NAME, CTA, INVITE]
(R / 'timing.json').write_text(json.dumps({k: sorted(set(round(x, 4) for x in v)) for k, v in sfx.items()}, indent=1, ensure_ascii=False))
(C / 'index.html').write_text(
    ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>' + css + '</style></head><body>'
    f'<div id="basic" data-composition-id="basic" data-width="1080" data-height="1920" data-start="0" data-duration="{D}">' + ''.join(parts) + '</div>'
    '<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});' + ''.join(anim) + 'window.__timelines.basic=tl;</script></body></html>').replace('PERSON_POS', PERSON_POS))
print('built', D, 'clips', len(parts), 'anims', len(anim), {k: len(v) for k, v in sfx.items()})
