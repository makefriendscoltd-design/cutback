"""AI 학교 3일차 — Kallaway(DaxdLQbOJXR) 문법 + 관제탑 인트로 (day7-kallaway-ref 방식 이식, 카드뉴스 대본).

3단 고정 레이아웃: 상단 애셋 무대(0~1130) / 중간 1~3어절 자막(1150) / 하단 인물 카드(60,1250,960x600).
애셋 없는 대사는 얼굴 풀프레임 펀치인. 챕터 전환은 하드컷, 무대 안에서 요소를 쌓는다.
모든 시각은 출력 타임라인 초(captions.json / edit-plan.json 기준).
"""
from pathlib import Path
import json, re, html, os
PERSON_POS = os.environ.get('PERSON_POS', '44')

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
C = R / 'composition'
A = C / 'assets'
A.mkdir(parents=True, exist_ok=True)
plan = json.loads((R / 'edit-plan.json').read_text())
D = plan['duration']
caps = json.loads((R / 'captions.json').read_text())
I3 = ROOT / 'videos/day3-basic-mix-20260915'


def link(n, p):
    q = A / n
    if not q.exists():
        q.symlink_to(Path(p).resolve())


link('person.mp4', I3 / 'assets/person.mp4')
link('vlog-classroom.mp4', I3 / 'assets/vlog-classroom.mp4')
link('font.ttf', ROOT / 'verification-renders/20260911_180156-r01-v19/composition/assets/Pretendard-SemiBold.ttf')
link('black.ttf', ROOT / 'verification-renders/20260911_180156-r01-v7/composition/assets/Pretendard-Black.ttf')
link('gsap.min.js', ROOT / 'videos/day1-sc-vlog/composition/assets/vendor/gsap.min.js')
link('hud-intro.mp4', R / 'assets/hud-intro-1080x1130.mp4')
for i in range(1, 9):
    link(f'card-{i:02d}.png', I3 / f'assets/generated/card-news/card-{i:02d}.png')

# ---------------------------------------------------------------- chapter times (output seconds, captions.json 기준)
INTRO, PUSH, CARDS, TERM, TEXT, PROMPT, SPLIT, SAVE, DK, MAKE, FACE, CTA, BOOK = (
    0.0, 2.9, 5.646667, 8.18, 10.38, 13.18, 15.053333, 17.273333, 20.446667, 22.846667, 24.486667, 27.006667, 29.386667)
LIGHT = [(CARDS, DK), (CTA, D)]
DARK = [(INTRO, CARDS), (DK, FACE)]
FULL = [(FACE, CTA)]

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
.drift{{position:absolute;left:0;top:0;width:1080px;height:1130px;transform-origin:50% 45%}}
.cline{{position:absolute;left:0;right:0;text-align:center}}
.pill.inl{{position:relative;display:inline-block}}
.doc{{padding:36px 50px}} .doc p{{margin:0;height:80px;font:600 44px/80px Pretendard;color:{INK};white-space:nowrap}}
.sheet{{position:absolute;width:190px;height:240px;background:#fff;border:4px solid {INK};border-radius:12px;padding:34px 26px;box-shadow:10px 12px 0 {RED};transform:rotate(-8deg)}}
.sheet i{{display:block;height:12px;background:#d9d6cf;border-radius:6px;margin-bottom:26px}} .sheet i:nth-child(2){{width:70%}}
.key{{position:absolute;width:300px;height:140px;border-radius:26px;background:#fff;border:5px solid {INK};box-shadow:0 14px 0 {INK};display:flex;align-items:center;justify-content:center;font:900 70px/1 Black;color:{INK};letter-spacing:-2px}}
.hilite{{background:#ffd3d5;border-radius:6px}}
.segbar{{position:absolute;left:60px;top:250px;width:960px;height:150px}}
.seg{{position:absolute;top:0;width:316px;height:150px;background:#fff;border:5px solid {INK};display:flex;align-items:center;justify-content:center;font:900 50px/1 Black;color:{INK};letter-spacing:-2px}}
.seg b{{color:{RED};font-size:30px;margin-right:12px}}
.clabel{{position:absolute;width:300px;text-align:center;font:900 34px/1 Black;color:{INK};letter-spacing:1px}}
.docnode{{position:absolute;background:#fff;border-radius:18px;padding:30px 34px;box-shadow:0 20px 40px #000a}}
.docnode b{{display:block;font:900 54px/1 Black;color:{INK};margin-bottom:26px;letter-spacing:-2px}}
.docnode i{{display:block;height:14px;background:#d9d6cf;border-radius:7px;margin-bottom:22px}} .docnode i:nth-child(3){{width:75%}} .docnode i:nth-child(5){{width:55%}}
.vclass{{border-radius:26px;object-fit:cover;object-position:50% 55%}}
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

def stage(inner, a, b, sid, cls='stage'):
    # 무대 전체가 챕터 내내 아주 천천히 밀려 들어가 그래픽 정지 구간을 없앤다.
    clip(f'<div class="drift" id="{sid}">{inner}</div>', a, b, 5, cls)
    anim.append(f'tl.fromTo("#{sid}",{{scale:1}},{{scale:1.035,duration:{r4(b-a)},ease:"none",immediateRender:false}},{r4(a)});')


def count(sel_id, var, to, t, dur, suffix):
    anim.append(f'const {var}={{n:0}};tl.to({var},{{n:{to},duration:{r4(dur)},ease:"none",snap:"n",onUpdate:()=>{{document.getElementById("{sel_id}").textContent={var}.n+"{suffix}"}}}},{r4(t)});')


# ---------------------------------------------------------------- 0 intro  0 ~ 5.65  (실제 AI 학교 관제탑 2.5배속)
a, b = INTRO, CARDS
parts.append(f'<video id="hud-intro" class="clip" src="assets/hud-intro.mp4" data-start="0" data-duration="{r4(b-a)}" data-media-start="0" data-track-index="3" style="left:0;top:0;width:1080px;height:1130px;z-index:3;object-fit:cover" muted></video>')
# 승인 헤드카피: "POV: AI 미친자가 / 저지른 일", 1초, Black 122px, top 360. 문구 변경 금지.
parts.append('<div id="head" class="clip head" data-start="0" data-duration="1" data-track-index="30"><span>POV: AI 미친자가</span><span>저지른 일</span></div>')
sfx['whoosh'] += [INTRO, PUSH]

# ---------------------------------------------------------------- 1 cards  5.65 ~ 8.18  여기서는 카드뉴스도 자동으로 만들거든요
a, b = CARDS, TERM
h = '<div class="wordmark pop" id="wm1"><i></i>AI 학교 · 카드뉴스</div>'
h += ''.join(f'<div class="memo pop" id="g{i}" style="left:{44+(i%4)*252}px;top:{200+(i//4)*252}px;width:236px;height:236px"><img src="assets/card-{i+1:02d}.png"></div>' for i in range(8))
h += '<div class="counter pop" id="gcount" style="top:130px;right:44px">0장</div>'
h += '<div class="cline" style="top:760px"><span class="pill green inl pop" id="g-pill">자동으로 완성 ✓</span></div>'
h += scrib(330, 850, 420, 40, 'M6 28 C 110 6, 290 34, 414 10', '', 'g-und')
stage(h, a, b, 'dr1')
pop('#wm1', a, click=False)
pop('#gcount', a + .1, click=False)
for i in range(8):
    pop(f'#g{i}', a + .1 + i * .13, scale=.7, y=40)
count('gcount', 'c1', 8, a + .1, 8 * .13, '장')
anim.append('tl.set("#g0",{boxShadow:"0 0 0 6px #3ddc84,0 0 44px 10px #3ddc84aa"},6.87);tl.fromTo("#g0",{scale:1},{scale:1.1,duration:.22,ease:"power2.out",immediateRender:false},6.87);tl.to("#g0",{scale:1.05,duration:.28,yoyo:true,repeat:2},7.1);'); sfx['pop'].append(6.87)
pop('#g-pill', 7.05, y=20)
draw('#g-und path', 7.45, .35)

# ---------------------------------------------------------------- 2 STEP 01 terminal  8.18 ~ 10.38  첫 번째 코덱스를 켭니다
a, b = TERM, TEXT
h = ('<div class="num pop" id="n1">01<small>STEP</small></div>'
     '<div class="win term pop" id="term" style="left:90px;top:300px;width:900px;height:520px"><div class="bar"><i></i><i></i><i></i><span>terminal</span></div>'
     '<div class="body"><span class="c">~/card-news</span>\n<span class="p">$</span> ' + typed('codex', 'tc') + '<span class="cur" id="cur"></span></div></div>'
     '<div class="tile codex pop" id="tile-codex" style="left:730px;top:690px;width:230px;height:230px"><i>OPENAI</i><b>Codex</b></div>'
     + scrib(110, 445, 380, 120, 'M40 20 C 160 -8, 350 8, 364 56 C 376 104, 200 118, 80 104 C 10 96, 0 50, 60 24', '', 't-ring'))
stage(h, a, b, 'dr2')
pop('#n1', a, y=-30); rise('#term', a + .08)
type_in('tc', 5, 8.72, 9.2)
anim.append(f'tl.fromTo("#cur",{{opacity:1}},{{opacity:0,duration:.35,yoyo:true,repeat:5}},{r4(a+.1)});')
anim.append('tl.fromTo("#tile-codex",{opacity:0,scale:.3,rotation:-40},{opacity:1,scale:1,rotation:-8,duration:.4,ease:"back.out(1.8)",immediateRender:false},9.35);'); sfx['pop'].append(9.35)
draw('#t-ring path', 9.75, .4)
bump('#tile-codex', 10.1, y=-14)

# ---------------------------------------------------------------- 3 STEP 02 text  10.38 ~ 13.18  두 번째 카드뉴스로 바꿀 글을 넣으세요
a, b = TEXT, PROMPT
lines = ['AI가 낯설다면', '무엇부터 시작해야 할까요?', '내가 쓴 글에서 첫 메시지를 고르고,', '한 장에 하나씩 나누면 됩니다.']
h = ('<div class="num pop" id="n2">02<small>STEP</small></div>'
     '<div class="win pop" id="dwin" style="left:90px;top:300px;width:900px;height:470px"><div class="bar"><i></i><i></i><i></i><span>내 글.txt</span></div><div class="doc">'
     + ''.join(f'<p class="pop" id="dl{i}">{html.escape(l)}</p>' for i, l in enumerate(lines)) + '</div></div>'
     '<div class="counter pop" id="dcount" style="top:212px;right:90px">0자</div>'
     '<div class="sheet pop" id="sheet" style="left:445px;top:820px"><i></i><i></i><i></i><i></i></div>'
     + scrib(130, 612, 740, 40, 'M6 26 C 200 6, 520 34, 734 12', '', 'd-und'))
stage(h, a, b, 'dr3')
pop('#n2', a, y=-30); rise('#dwin', a + .08); pop('#dcount', a + .3, click=False)
anim.append('tl.fromTo("#sheet",{opacity:0,y:300,rotation:10},{opacity:1,y:0,rotation:-8,duration:.36,ease:"power3.out",immediateRender:false},10.86);tl.to("#sheet",{y:-330,scale:.4,opacity:0,duration:.3,ease:"power2.in"},11.3);'); sfx['pop'].append(10.86)
for i in range(4):
    pop(f'#dl{i}', 11.5 + i * .2, scale=.95, y=16)
count('dcount', 'c2', sum(len(l.replace(' ', '')) for l in lines), 11.5, .8, '자')
draw('#d-und path', 12.35, .4)
bump('#dwin', 12.8, y=-12)

# ---------------------------------------------------------------- 4 STEP 02 prompt paste  13.18 ~ 15.05  이 프롬프트를 붙여넣습니다
a, b = PROMPT, SPLIT
h = ('<div class="num" id="n2b">02<small>STEP</small></div>'
     '<div class="prompt pop" id="prompt" style="top:300px;height:320px"><span id="ptxt" style="opacity:0"><span class="hilite" id="phl">이 글을 카드뉴스로 나누고<br>장마다 이미지로 저장해줘</span></span>'
     '<span class="ph" id="pph">프롬프트 입력…</span><div class="send pop" id="send">↑</div></div>'
     '<div class="key pop" id="kv" style="left:390px;top:760px">⌘ V</div>'
     + scrib(780, 480, 240, 180, 'M40 30 C 120 -6, 236 30, 224 104 C 212 170, 70 176, 26 120 C -4 80, 20 40, 70 22', '', 's-ring'))
stage(h, a, b, 'dr4')
rise('#prompt', a + .02)
pop('#kv', 13.35, y=40)
anim.append('tl.to("#kv",{y:12,boxShadow:"0 2px 0 #171717",duration:.08,yoyo:true,repeat:1},13.72);'); sfx['click'].append(13.72)
anim.append('tl.set("#pph",{display:"none"},13.8);tl.fromTo("#ptxt",{opacity:0,scale:.96},{opacity:1,scale:1,duration:.14,immediateRender:false},13.8);tl.to("#phl",{backgroundColor:"rgba(255,211,213,0)",duration:.4},14.2);'); sfx['pop'].append(13.8)
pop('#send', 14.3, scale=.3, click=False); sfx['pop'].append(14.3)
draw('#s-ring path', 14.45, .35)
anim.append('tl.to("#send",{scale:1.15,duration:.13,yoyo:true,repeat:1},14.75);')

# ---------------------------------------------------------------- 5 STEP 03 split  15.05 ~ 17.27  세 번째로 글을 장마다 나누고
a, b = SPLIT, SAVE
segs = ['첫 문장', '핵심 내용', '다음 행동']
imgs = [1, 2, 4]
h = '<div class="num pop" id="n3">03<small>STEP</small></div><div class="segbar pop" id="sbar">'
h += ''.join(f'<div class="seg" id="sg{i}" style="left:{i*322}px;border-radius:{"26px 0 0 26px" if i==0 else ("0 26px 26px 0" if i==2 else "0")}"><b>0{i+1}</b>{t}</div>' for i, t in enumerate(segs)) + '</div>'
h += scrib(0, 220, 1080, 210, 'M381 8 L 381 200 M703 8 L 703 200', '', 'cuts')
h += scrib(0, 412, 1080, 130, 'M220 8 L 210 118 M540 8 L 540 118 M860 8 L 870 118', 'ink', 'arrows')
h += ''.join(f'<div class="memo pop" id="sc{i}" style="left:{60+i*330}px;top:560px;width:300px;height:300px"><img src="assets/card-{n:02d}.png"></div>' for i, n in enumerate(imgs))
h += ''.join(f'<div class="clabel pop" id="cl{i}" style="left:{60+i*330}px;top:890px">CARD 0{i+1}</div>' for i in range(3))
stage(h, a, b, 'dr5')
pop('#n3', a, y=-30); rise('#sbar', a + .08)
anim.append('tl.set("#cuts path",{strokeDasharray:"1"},15.0);')
draw('#cuts path', 15.62, .25); sfx['pop'].append(15.62)
anim.append('tl.to("#sg0",{x:-26,duration:.25,ease:"power2.out"},15.8);tl.to("#sg2",{x:26,duration:.25,ease:"power2.out"},15.8);')
draw('#arrows path', 15.95, .3)
for i in range(3):
    pop(f'#sc{i}', 16.2 + i * .15, scale=.6, y=50)
    pop(f'#cl{i}', 16.3 + i * .15, y=10, click=False)
bump('#sc1', 16.9, y=-16)

# ---------------------------------------------------------------- 6 save PNG  17.27 ~ 20.45  이미지로 저장하는 작업까지 시킵니다
a, b = SAVE, DK
rows = ''.join(f'<div class="row pop" id="f{i}"><div class="th" style="height:44px"><img src="assets/card-{i+1:02d}.png"></div>card-{i+1:02d}.png<em>PNG</em></div>' for i in range(8))
h = ('<div class="ttl pop" id="sv-ttl" style="top:48px">이미지로 <em>저장</em></div>'
     '<div class="win pop" id="swin" style="left:90px;top:230px;width:900px;height:660px"><div class="bar"><i></i><i></i><i></i><span>card-news/</span></div>' + rows + '</div>'
     '<div class="counter pop" id="scount" style="top:156px;right:90px">0 PNG</div>'
     '<div class="cline" style="top:930px"><span class="pill green inl pop" id="sv-pill">저장까지 한 번에 ✓</span></div>'
     + scrib(800, 128, 250, 110, 'M30 30 C 110 -4, 240 20, 232 60 C 224 104, 60 110, 16 74 C -8 52, 20 30, 60 18', '', 'sv-ring'))
stage(h, a, b, 'dr6')
pop('#sv-ttl', a, y=-20); rise('#swin', a + .06); pop('#scount', a + .2, click=False)
for i in range(8):
    pop(f'#f{i}', 17.5 + i * .15, scale=.9, y=20)
count('scount', 'c3', 8, 17.5, 8 * .15, ' PNG')
anim.append('tl.to("#swin",{boxShadow:"0 0 0 6px #3ddc84,0 0 50px 12px #3ddc8488",duration:.2},18.63);'); sfx['pop'].append(18.63)
pop('#sv-pill', 18.75, y=20)
draw('#sv-ring path', 19.25, .35)
bump('#swin', 19.8, y=-12)

# ---------------------------------------------------------------- 7a dark classroom  20.45 ~ 22.85  AI 학교에서는 여러분들이 쓴 글로
a, b = DK, MAKE
h = ('<div class="pill pop" id="v-pill" style="left:60px;top:44px">AI 학교 수업</div>'
     + scrib(60, 128, 330, 30, 'M4 18 C 90 4, 220 26, 326 8', 'white', 'v-und'))
stage(h, a, b, 'dr7', 'stage dark')
parts.append(f'<video id="vclass" class="clip vclass" src="assets/vlog-classroom.mp4" data-start="{r4(a)}" data-duration="{r4(b-a)}" data-media-start="0" data-track-index="6" style="left:60px;top:170px;width:960px;height:930px;z-index:6" muted></video>')
pop('#v-pill', a + .05, y=-20)
rise('#vclass', a, .3, 80)
draw('#v-und path', 21.3, .3)

# ---------------------------------------------------------------- 7b dark diagram  22.85 ~ 24.49  카드뉴스를 만듭니다
a, b = MAKE, FACE
h = ('<div class="docnode pop" id="dn" style="left:420px;top:30px;width:240px;height:280px"><b>내 글</b><i></i><i></i><i></i><i></i></div>'
     + scrib(0, 320, 1080, 80, 'M540 6 L 540 72', 'white', 'm-c1')
     + '<div class="tile school pop" id="m-tile" style="left:440px;top:405px;width:200px;height:200px"><b>AI</b><small>학교</small></div>'
     + scrib(0, 612, 1080, 110, 'M540 6 C 540 60, 240 40, 240 100 M540 6 L 540 100 M540 6 C 540 60, 840 40, 840 100', 'white', 'm-c2')
     + ''.join(f'<div class="memo pop" id="mf{i}" style="left:{90+i*300}px;top:730px;width:300px;height:300px;z-index:{2 if i==1 else 1}"><img src="assets/card-{n:02d}.png"></div>' for i, n in enumerate([4, 7, 1])))
stage(h, a, b, 'dr8', 'stage dark')
pop('#dn', a, scale=.6)
draw('#m-c1 path', a + .18, .2)
pop('#m-tile', a + .35, scale=.4, click=False); sfx['pop'].append(r4(a + .35))
draw('#m-c2 path', a + .62, .28)
for i, rot in enumerate([-6, 0, 6]):
    anim.append(f'tl.fromTo("#mf{i}",{{opacity:0,scale:.5,y:80,rotation:0}},{{opacity:1,scale:1,y:0,rotation:{rot},duration:.3,ease:"back.out(1.6)",immediateRender:false}},{r4(a+.85+i*.12)});')
    sfx['click'].append(r4(a + .85 + i * .12))
anim.append(f'tl.to("#mf1",{{boxShadow:"0 0 0 6px #3ddc84,0 0 44px 10px #3ddc84aa",scale:1.06,duration:.2}},{r4(a+1.3)});')

# ---------------------------------------------------------------- 9 CTA  27.01 ~ 29.39  댓글에 시작 남겨주세요
a, b = CTA, D
h = ('<div class="cta" id="cta"><span class="pop" id="c1">댓글에 <em>“시작”</em></span><span class="sub pop" id="c2" style="margin-top:34px">남겨주세요</span></div>'
     + scrib(560, 190, 300, 36, 'M6 26 C 80 4, 200 30, 292 8', '', 'c-under')
     + '<div class="comment pop" id="comment"><div class="top">댓글</div><div class="entry"><span class="avatar">나</span><span class="ph" id="c-ph">댓글 달기…</span><b id="c-word" style="opacity:0">시작</b><span class="reply" id="c-reply">게시</span></div></div>'
     + scrib(200, 700, 300, 170, 'M270 160 C 210 130, 150 90, 110 16 M110 16 L 92 70 M110 16 L 160 46', '', 'c-arrow')
     + '<div class="memo pop" id="wb" style="left:190px;top:120px;width:700px;height:700px"><img src="assets/card-08.png"></div>'
     + '<div class="stamp pop" id="stamp" style="right:auto;bottom:auto;left:600px;top:760px">무료 워크북</div>'
     + '<div class="cline" style="top:960px"><span class="chip pop" id="chip" style="position:relative;left:0;top:0;display:inline-block">↳ 대댓글로 드립니다</span></div>')
stage(h, a, b, 'dr9')
pop('#c1', a, y=-20); pop('#c2', a + .14, y=-20)
draw('#c-under path', a + .35, .3)
rise('#comment', a + .2)
anim.append('tl.set("#c-ph",{display:"none"},27.9);tl.fromTo("#c-word",{opacity:0,x:16,scale:.8},{opacity:1,x:0,scale:1,duration:.18,ease:"back.out(1.7)",immediateRender:false},27.9);'); sfx['pop'].append(27.9)
draw('#c-arrow path', 28.15, .3)
anim.append('tl.to("#c-reply",{scale:1.15,duration:.12,yoyo:true,repeat:1},28.6);'); sfx['click'].append(28.6)
# 10 book  29.39 ~ end  무료 워크북을 대댓글로 드리도록 하겠습니다
anim.append(f'tl.to("#cta,#comment,#c-under,#c-arrow",{{y:-60,opacity:0,duration:.22,ease:"power2.in"}},{r4(BOOK)});')
anim.append(f'tl.fromTo("#wb",{{opacity:0,y:140,rotation:-6,scale:.85}},{{opacity:1,y:0,rotation:-3,scale:1,duration:.36,ease:"back.out(1.4)",immediateRender:false}},{r4(BOOK+.1)});')
anim.append('tl.fromTo("#stamp",{opacity:0,scale:1.6,rotation:-8},{opacity:1,scale:1,rotation:-8,duration:.22,ease:"power3.out",immediateRender:false},29.95);'); sfx['pop'].append(29.95)
pop('#chip', 30.45, y=30, click=False); sfx['pop'].append(30.45)
bump('#wb', 31.1, y=-16)
anim.append('tl.to("#stamp",{scale:1.1,duration:.13,yoyo:true,repeat:1},31.6);')


# ---------------------------------------------------------------- captions
terms = ['미쳤나', 'AI 학교', '카드뉴스', '코덱스', '프롬프트', '장마다', '이미지', '첫 콘텐츠', '대댓글', '댓글', '워크북', '시작']


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
sfx['whoosh'] += [CARDS, TERM, TEXT, PROMPT, SPLIT, SAVE, DK, MAKE, CTA, BOOK]
(R / 'timing.json').write_text(json.dumps({k: sorted(set(round(x, 4) for x in v)) for k, v in sfx.items()}, indent=1, ensure_ascii=False))
(C / 'index.html').write_text(
    ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>' + css + '</style></head><body>'
    f'<div id="basic" data-composition-id="basic" data-width="1080" data-height="1920" data-start="0" data-duration="{D}">' + ''.join(parts) + '</div>'
    '<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});' + ''.join(anim) + 'window.__timelines.basic=tl;</script></body></html>').replace('PERSON_POS', PERSON_POS))
print('built', D, 'clips', len(parts), 'anims', len(anim), {k: len(v) for k, v in sfx.items()})
