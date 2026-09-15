"""AI 학교 5일차 — Kallaway 레퍼런스 + 관제탑 인트로 (day7-kallaway-ref 문법 이식).

3단 레이아웃: 무대 0~1130 / 자막 y=1150 / 인물 카드 (60,1235) 960x640.
음성·자막·컷은 day5-basic-mix-v5 그대로. 모든 시각은 출력 타임라인 초(captions.json 기준).
"""
from pathlib import Path
import json, html, os
PERSON_POS = os.environ.get('PERSON_POS', '40')

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
C = R / 'composition'
A = C / 'assets'
A.mkdir(parents=True, exist_ok=True)
plan = json.loads((R / 'edit-plan.json').read_text())
D = plan['duration']
caps = json.loads((R / 'captions.json').read_text())
V5 = ROOT / 'videos/day5-basic-mix-v5-20260915'
HUD = ROOT / 'videos/_assets/hud-captures-20260915'


def link(n, p):
    q = A / n
    if q.is_symlink() or q.exists():
        q.unlink()
    q.symlink_to(Path(p).resolve())


link('person.mp4', R / 'assets/person.mp4')
link('vlog-records.mp4', R / 'assets/vlog-records.mp4')
link('vlog-files.mp4', R / 'assets/vlog-files.mp4')
link('font.ttf', ROOT / 'verification-renders/20260911_180156-r01-v19/composition/assets/Pretendard-SemiBold.ttf')
link('black.ttf', ROOT / 'verification-renders/20260911_180156-r01-v7/composition/assets/Pretendard-Black.ttf')
link('gsap.min.js', ROOT / 'videos/day1-sc-vlog/composition/assets/vendor/gsap.min.js')
link('hud-intro.mp4', R / 'assets/hud-intro-1080x1130.mp4')
link('hud-main.png', HUD / 'main-t6000.png')
link('hud-boot.png', HUD / 'main-t1500.png')
pages = sorted((V5 / 'assets/generated/archive').glob('page-*.png'))
assert len(pages) == 8, pages
for i, p in enumerate(pages):
    link(f'page-{i+1:02d}.png', p)

# ---------------------------------------------------------------- chapter times (output seconds, caption starts)
INTRO, PUSH = 0.0, 2.77
C1, C2, C3, F1, C4, C5, C6, C7, F2, C8, C9, C10 = (
    5.45, 9.29, 14.99, 19.29, 22.302, 25.122, 30.662, 32.992, 36.722, 38.842, 40.482, 41.982)
DARK = [(INTRO, C1), (C3, F1), (C5, C7)]
LIGHT = [(C1, C3), (C4, C5), (C7, F2), (C8, D)]
FULL = [(F1, C4), (F2, C8)]

RED = '#ff434b'
INK = '#171717'
PAPER = '#f1efe9'
NIGHT = '#0b0b0d'
GREEN = '#3ddc84'

css = f'''
@font-face{{font-family:Pretendard;src:url(assets/font.ttf);font-weight:600}}
@font-face{{font-family:Black;src:url(assets/black.ttf);font-weight:900}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:#000;width:1080px;height:1920px;overflow:hidden}}
#basic{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000;font-family:Pretendard,sans-serif}}
.clip{{position:absolute}}
.bg{{left:0;top:0;width:1080px;height:1920px;z-index:1}}
.bg.light{{background:{PAPER}}} .bg.dark{{background:{NIGHT}}}
.stage{{left:0;top:0;width:1080px;height:1130px;overflow:hidden;z-index:5;color:{INK};transform-origin:50% 50%}}
.stage.dark{{color:#fff}}
#person-box{{position:absolute;left:60px;top:1235px;width:960px;height:640px;z-index:10;overflow:hidden;border-radius:28px;box-shadow:0 26px 50px #0005;transform-origin:50% 45%}}
#person-box video{{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:50% PERSON_POS%}}
.caption{{left:30px;right:30px;top:1150px;z-index:20;font:900 58px/1.2 Black;letter-spacing:-1.5px;text-align:center;white-space:nowrap;color:{INK}}}
.caption.onfull{{top:1340px;color:#fff;-webkit-text-stroke:5px #171d20;paint-order:stroke fill;text-shadow:0 5px 6px #000,0 0 12px #000e}}
.caption.ondark{{color:#fff}}
.accent{{color:{RED}}}
.pop{{opacity:0}}
.head{{left:40px;right:40px;top:360px;z-index:30;text-align:center;font:900 122px/1.1 Black;letter-spacing:-5px;color:white;-webkit-text-stroke:7px black;paint-order:stroke fill;text-shadow:0 8px 9px #0009}}
.head span{{display:block}}
.scrib{{position:absolute;overflow:visible}}
.scrib path{{fill:none;stroke:{RED};stroke-width:9;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1}}
.scrib.white path{{stroke:#fff}} .scrib.green path{{stroke:{GREEN}}}
.wordmark{{position:absolute;left:0;right:0;top:60px;text-align:center;font:900 54px/1 Black;letter-spacing:-2px}}
.wordmark i{{display:inline-block;width:52px;height:52px;border-radius:14px;background:{RED};vertical-align:-10px;margin-right:16px}}
.memo{{position:absolute;overflow:hidden;border-radius:10px;box-shadow:0 14px 26px #0003;background:#fff}}
.memo img{{width:100%;height:100%;object-fit:cover;object-position:top;display:block}}
.pill{{position:absolute;padding:14px 30px;border-radius:999px;background:{RED};color:#fff;font:900 36px/1 Black;box-shadow:0 12px 24px #0004;white-space:nowrap}}
.pill.ink{{background:{INK}}} .pill.green{{background:#1fbf6a}}
.counter{{position:absolute;background:{INK};color:#fff;padding:12px 26px;border-radius:999px;font:900 34px/1 Black}}
/* checklist */
.card{{position:absolute;border-radius:26px;background:#fff;border:4px solid {INK};box-shadow:12px 14px 0 #d9d6cf;padding:34px 36px;color:{INK}}}
.ck-h{{font:900 60px/1 Black;letter-spacing:-2px;margin-bottom:26px}}
.ck-row{{display:flex;align-items:center;gap:20px;height:96px;border-top:3px solid #eeebe4}}
.box{{width:46px;height:46px;border:5px solid {INK};border-radius:10px;flex:none;display:flex;align-items:center;justify-content:center;font:900 34px/1 Black;color:#fff}}
.skel{{height:22px;border-radius:11px;background:#e4e0d7}}
.ck-row b{{font:900 44px/1 Black;letter-spacing:-1.5px}}
.ck-row.hit .box{{background:#1fbf6a;border-color:#1fbf6a}}
/* bin */
.bin{{position:absolute;width:250px;height:300px}}
.bin .lid{{position:absolute;left:-14px;top:0;width:278px;height:34px;border-radius:12px;background:{INK}}}
.bin .lid:after{{content:"";position:absolute;left:100px;top:-22px;width:78px;height:26px;border:8px solid {INK};border-bottom:0;border-radius:12px 12px 0 0}}
.bin .body{{position:absolute;left:12px;top:48px;width:226px;height:252px;border-radius:0 0 30px 30px;background:#fff;border:8px solid {INK};display:flex;justify-content:space-evenly;padding-top:28px}}
.bin .body i{{width:12px;height:170px;border-radius:6px;background:{INK}}}
/* category */
.lbl{{position:absolute;text-align:center;font:900 44px/1 Black;letter-spacing:-1.5px;white-space:nowrap}}
.chip-n{{position:absolute;width:74px;height:74px;border-radius:50%;background:{RED};color:#fff;display:flex;align-items:center;justify-content:center;font:900 36px/1 Black;box-shadow:0 8px 16px #0004}}
.frow{{position:absolute;left:60px;width:960px;height:84px;border-radius:18px;background:#fff;border:3px solid #d9d6cf;display:flex;align-items:center;gap:24px;padding:0 30px;font:600 36px Pretendard;color:{INK}}}
.frow .ic{{width:40px;height:50px;border-radius:6px;background:{INK};position:relative;flex:none}}
.frow .ic:after{{content:"";position:absolute;right:0;top:0;border-left:14px solid #fff;border-bottom:14px solid #fff;border-color:#fff #fff transparent transparent;border-style:solid;border-width:0 14px 14px 0;border-right-color:{PAPER}}}
.frow em{{font-style:normal;margin-left:auto;font:900 30px Black;color:{RED}}}
/* ask */
.vcard{{border-radius:24px;object-fit:cover;box-shadow:0 30px 60px #000a}}
.askbox{{position:absolute;left:530px;top:380px;width:490px;height:150px;border-radius:36px;background:#1b1e24;border:4px solid #3a3f47;padding:44px 36px;font:600 46px/1.3 Pretendard;color:#eee;white-space:nowrap}}
.askbox .cur{{display:inline-block;width:6px;height:52px;background:#eee;vertical-align:-10px;margin-left:6px}}
.q{{position:absolute;font:900 230px/1 Black;color:{RED}}}
.q.s{{font-size:90px}}
.folderbig{{position:absolute;left:560px;top:790px;width:420px;height:260px}}
.folderbig .tab{{position:absolute;left:0;top:0;width:170px;height:60px;border-radius:18px 18px 0 0;background:#e8b93a}}
.folderbig .front{{position:absolute;left:0;top:40px;width:420px;height:220px;border-radius:0 22px 22px 22px;background:#ffcc38;z-index:3;display:flex;align-items:center;justify-content:center;font:900 44px Black;color:{INK}}}
/* repeat */
.bubble{{position:absolute;padding:30px 40px;border-radius:34px 34px 34px 8px;background:#fff;border:4px solid {INK};font:600 42px/1.2 Pretendard;color:{INK};white-space:nowrap;box-shadow:8px 10px 0 #d9d6cf}}
.bubble small{{display:block;font:900 26px/1 Black;color:#8a8a8a;margin-bottom:12px;letter-spacing:1px}}
.bubble.glow{{box-shadow:0 0 0 6px {GREEN},0 0 40px 8px #3ddc8488}}
/* brain diagram */
.node-lbl{{position:absolute;text-align:center;font:600 32px/1 Pretendard;color:#ccc;white-space:nowrap}}
.ainode{{position:absolute;left:430px;top:470px;width:220px;height:220px;border-radius:50%;background:#111;border:6px solid #444;display:flex;align-items:center;justify-content:center;font:900 90px/1 Black;color:#fff}}
.ring{{position:absolute;left:410px;top:450px;width:260px;height:260px;border-radius:50%;border:8px solid transparent;border-top-color:{GREEN};border-right-color:{GREEN}}}
.brain{{position:absolute;left:260px;top:820px;width:560px;height:230px;border-radius:40px;background:{RED};color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 26px 50px #000a}}
.brain b{{font:900 96px/1 Black;letter-spacing:-4px}} .brain small{{font:900 38px/1 Black;margin-top:12px;letter-spacing:2px;opacity:.9}}
.memo.glow{{box-shadow:0 0 0 6px {GREEN},0 0 44px 10px #3ddc84aa}}
/* HUD frame */
.ttl{{position:absolute;left:0;right:0;top:64px;text-align:center;font:900 72px/1.1 Black;letter-spacing:-3px}}
.ttl em{{font-style:normal;color:{RED}}}
.frame{{position:absolute;left:50px;top:220px;width:980px;height:600px;border-radius:26px;overflow:hidden;background:#050a0f;box-shadow:0 30px 60px #0005;border:3px solid #333}}
.frame .bar{{height:60px;background:#1b1e24;display:flex;align-items:center;padding:0 26px;gap:12px;font:600 26px Pretendard;color:#aaa}}
.frame .bar i{{width:20px;height:20px;border-radius:50%;background:#ff5f57}} .frame .bar i:nth-child(2){{background:#febc2e}} .frame .bar i:nth-child(3){{background:#28c840}}
.frame .bar span{{margin-left:auto;background:#0f1115;border-radius:999px;padding:6px 22px;font-size:24px}}
.frame .view{{position:absolute;left:0;top:60px;width:980px;height:540px;overflow:hidden}}
.frame .view img{{position:absolute;left:0;top:0;width:3840px;height:2160px;transform-origin:0 0}}
.live{{display:inline-block;width:22px;height:22px;border-radius:50%;background:{GREEN};margin-right:14px;vertical-align:4px;box-shadow:0 0 0 6px #3ddc8444}}
/* files -> 준비물 */
.stamp{{position:absolute;padding:20px 34px;border:6px solid {RED};border-radius:12px;color:{RED};font:900 60px/1 Black;background:{PAPER}}}
/* workbook + CTA */
.cta{{position:absolute;left:0;right:0;top:60px;text-align:center;font:900 92px/1.1 Black;letter-spacing:-4px}}
.cta em{{font-style:normal;color:{RED}}} .cta span{{display:block}} .cta .sub{{font:900 68px/1.1 Black;letter-spacing:-3px;margin-top:34px}}
.comment{{position:absolute;left:90px;top:420px;width:900px;border-radius:30px;background:#fff;border:4px solid {INK};padding:36px 44px;font:600 40px/1.5 Pretendard;color:{INK};box-shadow:12px 14px 0 #d9d6cf}}
.comment .top{{border-bottom:3px solid #eee;padding-bottom:18px;font-size:34px;color:#666}}
.entry{{display:flex;align-items:center;margin-top:28px}}
.avatar{{display:inline-flex;border-radius:50%;width:70px;height:70px;align-items:center;justify-content:center;background:{INK};color:#fff;margin-right:26px;font-family:Black}}
.entry b{{color:{RED};font:900 64px/1 Black}} .entry .ph{{color:#b5b5b5;font-size:40px}}
.reply{{margin-left:auto;padding:14px 34px;border-radius:999px;background:{INK};color:#fff;font:900 34px/1 Black}}
.workbook{{position:absolute;left:150px;width:780px;height:640px;background:#fff9e9;border-radius:26px;border:4px solid {INK};box-shadow:14px 16px 0 {RED};padding:52px 56px;color:{INK};font:600 40px Pretendard}}
.workbook small{{color:#a63837;font-size:34px;letter-spacing:1px}}
.workbook strong{{display:block;font:900 110px/1.05 Black;letter-spacing:-5px;margin:22px 0 26px}}
.workbook .line{{height:5px;background:#e3d6c0;margin:26px 0;transform-origin:0 50%}}
.workbook .stamp{{right:44px;bottom:44px;transform:rotate(-8deg);background:#fff9e9;font-size:54px}}
.chip{{position:absolute;left:150px;top:1010px;padding:18px 36px;border-radius:999px;background:{INK};color:#fff;font:900 40px/1 Black;box-shadow:0 14px 30px #0004;white-space:nowrap}}
'''

parts = []
anim = []
sfx = {'whoosh': [], 'click': [], 'pop': [], 'typing': []}
chapters = []


def r4(x):
    return round(x, 4)


def clip(html_, a, b, z, cls='', sid=None, drift=True):
    sid = sid or f'st{len(parts)}'
    parts.append(f'<div id="{sid}" class="clip {cls}" style="z-index:{z}" data-start="{r4(a)}" data-duration="{r4(b-a)}" data-track-index="{z}">{html_}</div>')
    if drift and 'stage' in cls:
        anim.append(f'tl.fromTo("#{sid}",{{scale:1}},{{scale:1.018,duration:{r4(b-a)},ease:"none",immediateRender:false}},{r4(a)});')


def pop(sel, t, dur=.32, scale=.6, y=30, rot=0, ease='back.out(1.7)', click=True):
    anim.append(f'tl.fromTo("{sel}",{{opacity:0,scale:{scale},y:{y},rotation:{rot}}},{{opacity:1,scale:1,y:0,rotation:{rot},duration:{dur},ease:"{ease}",immediateRender:false}},{r4(t)});')
    if click:
        sfx['click'].append(r4(t))


def rise(sel, t, dur=.3, y=60):
    anim.append(f'tl.fromTo("{sel}",{{opacity:0,y:{y},scale:.96}},{{opacity:1,y:0,scale:1,duration:{dur},ease:"power3.out",immediateRender:false}},{r4(t)});')


def draw(sel, t, dur=.35):
    anim.append(f'tl.fromTo("{sel}",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{dur},ease:"power2.inOut",immediateRender:false}},{r4(t)});')


def bump(sel, t, s=1.08, dur=.12):
    anim.append(f'tl.to("{sel}",{{scale:{s},duration:{dur},yoyo:true,repeat:1,ease:"power2.inOut"}},{r4(t)});')


def out(sel, t, dur=.2, y=-40):
    anim.append(f'tl.to("{sel}",{{opacity:0,y:{y},duration:{dur},ease:"power2.in"}},{r4(t)});')


def scrib(x, y, w, h, d, cls='', sid=''):
    return f'<svg class="scrib {cls}" id="{sid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px" viewBox="0 0 {w} {h}"><path pathLength="1" d="{d}"/></svg>'


def ring(w, h):
    return f'M{w*.08:.0f} {h*.3:.0f} C {w*.25:.0f} {-h*.05:.0f}, {w*.95:.0f} {-h*.02:.0f}, {w*.97:.0f} {h*.45:.0f} C {w:.0f} {h*.95:.0f}, {w*.3:.0f} {h*1.02:.0f}, {w*.06:.0f} {h*.7:.0f} C {-w*.02:.0f} {h*.45:.0f}, {w*.1:.0f} {h*.2:.0f}, {w*.3:.0f} {h*.08:.0f}'


def typed(text, sid):
    return ''.join(f'<span id="{sid}-{i}" style="opacity:0">{html.escape(ch)}</span>' for i, ch in enumerate(text))


def type_in(sid, n, t0, t1):
    step = (t1 - t0) / max(n, 1)
    for i in range(n):
        anim.append(f'tl.set("#{sid}-{i}",{{opacity:1}},{r4(t0+i*step)});')
    sfx['typing'].append(r4(t0))


def counter(sel, var, n0, n1, t, dur, fmt):
    anim.append(f'const {var}={{n:{n0}}};tl.to({var},{{n:{n1},duration:{r4(dur)},ease:"none",snap:"n",onUpdate:()=>{{document.querySelector("{sel}").textContent={fmt}}}}},{r4(t)});')


# ---------------------------------------------------------------- backgrounds + person card
for a, b in LIGHT:
    clip('', a, b, 1, 'bg light', drift=False)
for a, b in DARK:
    clip('', a, b, 1, 'bg dark', drift=False)
parts.append(f'<div id="person-box"><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{D}" data-track-index="0" muted></video></div>')
VCARD = '{left:60,top:1235,width:960,height:640,scale:1,borderRadius:28}'
VFULL = '{left:0,top:0,width:1080,height:1920,borderRadius:0}'
for a, b in FULL:
    anim.append(f'tl.set("#person-box",{VFULL},{r4(a)});tl.set("#person",{{objectPosition:"50% 45%"}},{r4(a)});')
    anim.append(f'tl.set("#person-box",{VCARD},{r4(b)});tl.set("#person",{{objectPosition:"50% PERSON_POS%"}},{r4(b)});')
    anim.append(f'tl.fromTo("#person-box",{{scale:1.14}},{{scale:1.19,duration:{r4(b-a)},ease:"sine.out",immediateRender:false}},{r4(a)});')
    sfx['whoosh'] += [r4(a), r4(b)]

# ---------------------------------------------------------------- INTRO 0 ~ 5.45 : 관제탑 2.5배속 + 승인 헤드카피
parts.append(f'<video id="hud-intro" class="clip" src="assets/hud-intro.mp4" data-start="0" data-duration="{r4(C1)}" data-media-start="0" data-track-index="3" style="left:0;top:0;width:1080px;height:1130px;z-index:3;object-fit:cover" muted></video>')
# 승인 헤드카피: "POV: AI 미친자가 / 저지른 일", 0~1초, Black 122px, 흰색+검정 스트로크 7px, top 360. 변경 금지.
parts.append('<div id="head" class="clip head" data-start="0" data-duration="1" data-track-index="30"><span>POV: AI 미친자가</span><span>저지른 일</span></div>')
sfx['whoosh'] += [INTRO, PUSH]
chapters.append((INTRO, C1, '여러분 제가 정말 미쳤나 봅니다 / AI에 미쳐서 AI 학교까지 만들고 있어요', '실제 AI 학교 관제탑 녹화 2.5배속, 2.77초부터 CORE 1.58배 푸시인'))

# ---------------------------------------------------------------- C1 5.45 ~ 9.29 : 준비물 중 버리기 아까워 쌓아둔 파일
a, b = C1, C2
rows = ''.join(f'<div class="ck-row pop" id="ck{i}"><span class="box"></span><span class="skel" style="width:{w}px"></span></div>' for i, w in enumerate([230, 180, 250]))
rows += '<div class="ck-row pop" id="ck3"><span class="box" id="ckbox">✓</span><b>쌓아둔 파일</b></div>'
check = f'<div class="card pop" id="ck" style="left:60px;top:200px;width:440px;height:600px"><div class="ck-h">준비물</div>{rows}</div>'
bin_ = '<div class="bin pop" id="bin" style="left:680px;top:560px"><div class="lid" id="lid"></div><div class="body"><i></i><i></i><i></i></div></div>'
flyer = '<div class="memo pop" id="flyer" style="left:690px;top:200px;width:220px;height:293px"><img src="assets/page-05.png"></div>'
xbin = scrib(630, 530, 350, 360, 'M20 20 L 330 340 M 330 20 L 20 340', '', 'x-bin')
rots = [-9, 6, -3, 10, -6, 3, -11, 5]
pile = ''.join(f'<div class="memo pop" id="pl{i}" style="left:{600+(i%3)*40}px;top:{260+i*34}px;width:300px;height:400px"><img src="assets/page-{i+1:02d}.png"></div>' for i in range(8))
cnt = '<div class="counter pop" id="plc" style="left:830px;top:190px">파일 0</div>'
pring = scrib(540, 210, 520, 900, ring(520, 900), '', 'pl-ring')
clip('<div class="wordmark pop" id="wm1"><i></i>AI 학교 · 준비물</div>' + check + bin_ + flyer + xbin + pile + cnt + pring, a, b, 5, 'stage')
pop('#wm1', a, click=False)
rise('#ck', 5.62)
for i in range(4):
    pop(f'#ck{i}', 5.95 + i * .2, scale=.9, y=16)
pop('#bin', 6.83, scale=.5)
anim.append(f'tl.fromTo("#flyer",{{opacity:0,x:-420,y:-40,rotation:-30,scale:.8}},{{opacity:1,x:0,y:170,rotation:14,scale:1,duration:.45,ease:"power2.out",immediateRender:false}},{r4(6.95)});')
anim.append(f'tl.to("#lid",{{rotation:-24,x:-10,y:-20,duration:.18,yoyo:true,repeat:1}},{r4(7.1)});')
draw('#x-bin path', 7.35, .3); sfx['pop'].append(7.35)
anim.append(f'tl.to("#flyer",{{y:40,rotation:-6,duration:.3,ease:"back.out(2)"}},{r4(7.6)});')
out('#bin,#x-bin,#flyer', 7.82, .12, y=30)
for i in range(8):
    pop(f'#pl{i}', 7.89 + i * .09, scale=.8, y=-160, rot=rots[i], dur=.26, ease='power3.out')
pop('#plc', 7.89, click=False)
counter('#plc', 'k1', 0, 8, 7.89, 8 * .09, '"파일 "+k1.n')
draw('#pl-ring path', 8.87, .4); sfx['pop'].append(8.87)
anim.append(f'tl.set("#ckbox",{{backgroundColor:"#1fbf6a",borderColor:"#1fbf6a"}},{r4(8.87)});')
bump('#ck3', 8.9, 1.06)
bump('#plc', 9.05, 1.15)
chapters.append((a, b, '이 학교 준비물 중에 버리기 아까워서 쌓아둔 파일이 있습니다', '준비물 체크리스트 목업 + 휴지통에 빨간 X + 실제 아카이브 페이지 8장 낙하 더미·카운터 0→8 + 빨간 동그라미'))

# ---------------------------------------------------------------- C2 9.29 ~ 14.99 : 예전에 쓴 글 / 고객 답변 / 메모
a, b = C2, C3
cols = [60, 395, 730]
cards = (f'<div class="memo pop" id="k0" style="left:{cols[0]}px;top:150px;width:290px;height:386px"><img src="assets/page-01.png"></div>'
         f'<div class="memo pop" id="k1" style="left:{cols[1]}px;top:150px;width:290px;height:386px"><img src="assets/page-02.png"></div>'
         f'<div class="memo pop" id="k1b" style="left:{cols[1]}px;top:150px;width:290px;height:386px"><img src="assets/page-04.png"></div>'
         f'<div class="memo pop" id="k2" style="left:{cols[2]}px;top:150px;width:290px;height:386px"><img src="assets/page-03.png"></div>')
lbls = ''.join(f'<div class="lbl pop" id="kl{i}" style="left:{cols[i]}px;width:290px;top:566px">{t}</div>' for i, t in enumerate(['예전에 쓴 글', '고객 답변', '적어둔 메모']))
nums = ''.join(f'<div class="chip-n pop" id="kn{i}" style="left:{cols[i]-14}px;top:118px">{i+1}</div>' for i in range(3))
unders = ''.join(scrib(cols[i] + 10, 616, 270, 30, 'M6 20 C 80 4, 190 28, 264 10', '', f'ku{i}') for i in range(3))
frows = ''.join(f'<div class="frow pop" id="fr{i}" style="top:{700+i*100}px"><span class="ic"></span>{n}<em>{c}</em></div>' for i, (n, c) in enumerate([('글_초안_모음.txt', '38개'), ('고객_답변_정리.docx', '112개'), ('메모_아무거나.md', '240개')]))
kring = scrib(700, 100, 350, 500, ring(350, 500), '', 'k-ring')
clip(cards + nums + lbls + unders + frows + kring, a, b, 5, 'stage')
pop('#k0', a, rot=-3); pop('#kn0', a + .1, scale=.3, click=False); pop('#kl0', a + .2, click=False)
bump('#k0', 9.8, 1.05); bump('#kl0', 10.05, 1.1)
draw('#ku0 path', 10.29, .3); rise('#fr0', 10.45)
pop('#k1', 10.6, rot=2); pop('#kn1', 10.7, scale=.3, click=False); pop('#kl1', 10.8, click=False)
anim.append(f'tl.fromTo("#k1b",{{opacity:0,x:120,rotation:12}},{{opacity:1,x:0,rotation:3,duration:.3,ease:"power3.out",immediateRender:false}},{r4(11.51)});'); sfx['pop'].append(11.51)
draw('#ku1 path', 12.0, .3); rise('#fr1', 12.2)
bump('#k1b', 12.75, 1.05)
bump('#kl1', 11.12, 1.12); bump('#kn1', 11.3, 1.2)
pop('#k2', 13.27, rot=-2); pop('#kn2', 13.37, scale=.3, click=False); pop('#kl2', 13.47, click=False)
draw('#ku2 path', 13.9, .3); rise('#fr2', 14.05)
draw('#k-ring path', 14.51, .35); sfx['pop'].append(14.51)
bump('#fr0,#fr1,#fr2', 14.7, 1.03)
chapters.append((a, b, '예전에 쓴 글 고객한테 답했던 내용 생각나서 적어둔 메모요', '실제 페이지 01·02→04(실사진)·03 3열 + 번호 + 빨간 밑줄 + 파일 행(페이지 06의 파일명·개수) + 동그라미'))

# ---------------------------------------------------------------- C3 14.99 ~ 19.29 : AI한테 뭘 시킬지 모르면 그걸 먼저 꺼내
a, b = C3, F1
ask = ('<div class="askbox pop" id="ask">' + typed('뭘 시키지…', 'ak') + '<span class="cur" id="akc"></span></div>'
       '<div class="pill ink pop" id="ai-pill" style="left:530px;top:290px;background:#2a2e35">AI한테</div>'
       '<div class="q pop" id="q0" style="left:760px;top:70px">?</div>'
       '<div class="q s pop" id="q1" style="left:600px;top:110px">?</div>'
       '<div class="q s pop" id="q2" style="left:940px;top:300px">?</div>'
       '<div class="q s pop" id="q3" style="left:640px;top:560px">?</div>')
folder = ('<div class="folderbig pop" id="fold"><div class="tab"></div>'
          + ''.join(f'<div class="memo" id="fp{i}" style="left:{40+i*120}px;top:30px;width:150px;height:200px;z-index:2;opacity:0"><img src="assets/page-{p:02d}.png"></div>' for i, p in enumerate([1, 4, 3]))
          + '<div class="front">내 파일</div></div>')
arrow = scrib(600, 520, 300, 290, 'M150 270 C 120 180, 180 110, 150 20 M 110 60 L 150 18 L 192 58', 'green', 'f-arrow')
clip(ask + folder + arrow, a, b, 5, 'stage dark')
parts.append(f'<video id="vrec" class="clip vcard pop" src="assets/vlog-records.mp4" data-start="{r4(a)}" data-duration="{r4(b-a)}" data-media-start="0.35" data-track-index="7" style="left:60px;top:90px;width:440px;height:960px;z-index:7;object-position:50% 50%" muted></video>')
rise('#vrec', a, y=80)
pop('#ai-pill', a + .1, click=False); rise('#ask', a + .2)
type_in('ak', 6, 15.2, 15.75)
anim.append(f'tl.fromTo("#akc",{{opacity:1}},{{opacity:0,duration:.25,yoyo:true,repeat:15}},{r4(a+.2)});')
pop('#q0', 15.79, scale=.2, rot=8, click=False); sfx['pop'].append(15.79)
anim.append(f'tl.to("#q0",{{rotation:-10,duration:.25,yoyo:true,repeat:5,ease:"sine.inOut"}},{r4(16.12)});')
for i, t in enumerate([16.33, 16.63, 16.93]):
    pop(f'#q{i+1}', t, scale=.2, rot=(-14 if i % 2 else 12))
pop('#fold', 17.59, y=80)
out('#q0,#q1,#q2,#q3', 17.75, .18, y=-30)
for i in range(3):
    anim.append(f'tl.fromTo("#fp{i}",{{opacity:0,y:60}},{{opacity:1,y:{-150-i*10},rotation:{(-8,2,9)[i]},duration:.3,ease:"back.out(1.6)",immediateRender:false}},{r4(17.85+i*.2)});')
    sfx['click'].append(r4(17.85 + i * .2))
anim.append(f'tl.set("#fold .front",{{boxShadow:"0 0 0 6px {GREEN},0 0 40px 8px #3ddc8488"}},{r4(18.51)});')
bump('#fold', 18.51, 1.05)
draw('#f-arrow path', 18.7, .35)
chapters.append((a, b, 'AI한테 뭘 시켜야 할지 모르겠으면 그걸 먼저 꺼내 보려고요', '실촬 vlog-records 세로 카드 + 입력창 목업 "뭘 시키지…" 타이핑 + 빨간 물음표 + 폴더에서 실제 페이지 3장 꺼내기 + 초록 글로우'))
chapters.append((F1, C4, '내가 어떤 일을 했는지 어떤 이야기를', '얼굴 풀프레임 (자막 y=1340)'))

# ---------------------------------------------------------------- C4 22.302 ~ 25.122 : 반복했는지, 거기에 재료
a, b = C4, C5
bub = ''.join(f'<div class="bubble pop" id="bb{i}" style="left:{60+i*40}px;top:{130+i*170}px"><small>질문</small>처음엔 뭘 준비해야 하나요</div>' for i in range(3))
bcnt = '<div class="counter pop" id="bbc" style="left:820px;top:60px">×1</div>'
brk = scrib(20, 110, 60, 520, 'M50 10 C 10 10, 14 250, 14 260 C 14 270, 10 510, 50 510', '', 'bb-brk')
mat = '<div class="memo pop" id="mat" style="left:600px;top:560px;width:400px;height:533px"><img src="assets/page-08.png"></div>'
mring = scrib(560, 520, 480, 610, ring(480, 610), '', 'm-ring')
mpill = '<div class="pill pop" id="mpill" style="left:300px;top:720px;font-size:72px;padding:22px 50px">재료</div>'
clip(bub + bcnt + brk + mat + mring + mpill, a, b, 5, 'stage')
for i in range(3):
    pop(f'#bb{i}', a + .05 + i * .3, scale=.8, y=20)
pop('#bbc', a + .05, click=False)
counter('#bbc', 'k2', 1, 3, a + .35, .3, '"×"+k2.n')
anim.append(f'tl.set("#bb0,#bb1,#bb2",{{boxShadow:"0 0 0 6px {GREEN},0 0 40px 8px #3ddc8488"}},{r4(23.2)});'); sfx['pop'].append(23.2)
draw('#bb-brk path', 23.3, .35)
bump('#bbc', 23.55, 1.18)
pop('#mat', 23.882, scale=.7, y=80, rot=4)
draw('#m-ring path', 24.25, .35)
pop('#mpill', 24.582, scale=.4, click=False); sfx['pop'].append(24.582)
bump("#mpill", 24.96, 1.12)
chapters.append((a, b, '반복했는지 거기에 재료가 있을 수 있거든요', '같은 질문 말풍선 목업 ×3 카운터 + 초록 글로우 + 빨간 괄호 → 실제 페이지 08(여기에 재료가 있습니다) + 동그라미 + "재료" 배지'))

# ---------------------------------------------------------------- C5 25.122 ~ 30.662 : 첫 달, 내 기록을 AI가 찾아 쓰게, 제2의 뇌 과정 (검정)
a, b = C5, C6
first = '<div class="pill pop" id="first" style="left:450px;top:40px">첫 달</div>'
nx = [125, 455, 785]
nodes = ''.join(f'<div class="memo pop" id="d{i}" style="left:{nx[i]}px;top:140px;width:170px;height:226px"><img src="assets/page-{p:02d}.png"></div>' for i, p in enumerate([1, 4, 3]))
nl = ''.join(f'<div class="node-lbl pop" id="dl{i}" style="left:{nx[i]-40}px;width:250px;top:384px">{t}</div>' for i, t in enumerate(['글', '고객 답변', '메모']))
conn = scrib(0, 420, 1080, 60, 'M210 4 C 210 40, 500 20, 540 56 M540 4 L 540 56 M870 4 C 870 40, 580 20, 540 56', 'white', 'c-up')
ai = '<div class="ring pop" id="ring"></div><div class="ainode pop" id="ainode">AI</div>'
conn2 = scrib(0, 700, 1080, 110, 'M540 6 L 540 104', 'white', 'c-down')
brain = '<div class="brain pop" id="brain"><b>제2의 뇌</b><small>과정</small></div>'
bund = scrib(300, 1060, 480, 40, 'M8 26 C 120 4, 330 34, 472 10', '', 'br-under')
clip(first + nodes + nl + conn + ai + conn2 + brain + bund, a, b, 5, 'stage dark')
pop('#first', a, scale=.4)
for i in range(3):
    pop(f'#d{i}', 25.3 + i * .15, scale=.6, click=True)
    anim.append(f'tl.fromTo("#dl{i}",{{opacity:0}},{{opacity:1,duration:.2,immediateRender:false}},{r4(25.48+i*.15)});')
bump('#first', 25.95, 1.15); bump('#dl0,#dl1,#dl2', 26.2, 1.12)
draw('#c-up path', 26.422, .45)
pop('#ainode', 26.9, scale=.4, click=False); pop('#ring', 26.9, scale=.4, click=False); sfx['pop'].append(26.9)
anim.append(f'tl.to("#ring",{{rotation:1080,duration:{r4(b-27.3)},ease:"none"}},{r4(27.3)});')
for i in range(3):
    anim.append(f'tl.set("#d{i}",{{boxShadow:"0 0 0 6px {GREEN},0 0 44px 10px #3ddc84aa"}},{r4(27.602+i*.2)});')
    bump(f'#d{i}', 27.602 + i * .2, 1.08)
    sfx['click'].append(r4(27.602 + i * .2))
draw('#c-down path', 28.202, .2)
pop('#brain', 28.35, scale=.5, y=60, click=False); sfx['pop'].append(28.35)
bump('#brain', 28.95, 1.05)
bump('#ainode', 29.4, 1.1)
draw('#br-under path', 29.882, .35)
bump('#brain', 30.3, 1.06)
chapters.append((a, b, '그래서 첫 달에 내 기록을 AI가 찾아 쓰게 준비하는 제2의 뇌 과정을', '검정 무대: "첫 달" 배지 → 실제 페이지 3장 노드 → 흰 연결선 → AI 노드(초록 회전 링) → 노드 초록 글로우 → "제2의 뇌 과정" 타일 + 빨간 밑줄'))

# ---------------------------------------------------------------- C6 30.662 ~ 32.992 : 여기 학교 과정에 넣었습니다 (실제 관제 캡처)
a, b = C6, C7
board = ('<div class="ttl pop" id="h-ttl"><span class="live"></span>여기 <em>학교 과정</em></div>'
         '<div class="frame pop" id="frame"><div class="bar"><i></i><i></i><i></i><span>AI 학교 자동화 관제</span></div>'
         '<div class="view"><img id="h-main" src="assets/hud-main.png" alt="AI 학교 자동화 관제"><img id="h-boot" src="assets/hud-boot.png" alt="SECOND BRAIN MOUNTED" style="opacity:0"></div></div>'
         '<div class="pill green pop" id="h-pill" style="left:170px;top:880px">✓ 제2의 뇌 과정 · 학교 관제에 탑재</div>')
clip(board, a, b, 5, 'stage dark')
pop('#h-ttl', a, y=-20, click=False); rise('#frame', a + .06)
VW, VH = 980., 540.
S0 = VW / 3840.


def hx(cx, cy, z):
    sc = S0 * z
    return round(VW / 2 - cx * sc, 2), round(VH / 2 - cy * sc, 2), round(sc, 5)


def hset(sel, cx, cy, z, t):
    x_, y_, sc = hx(cx, cy, z); anim.append(f'tl.set("{sel}",{{x:{x_},y:{y_},scale:{sc}}},{r4(t)});')


def hto(sel, cx, cy, z, dur, t, ease='power2.inOut'):
    x_, y_, sc = hx(cx, cy, z); anim.append(f'tl.to("{sel}",{{x:{x_},y:{y_},scale:{sc},duration:{dur},ease:"{ease}"}},{r4(t)});')


hset('#h-main', 1920, 1080, 1.0, a)
hto('#h-main', 1140, 980, 1.9, .6, a + .15, 'power2.out')
hset('#h-boot', 1880, 1010, 2.2, a)
anim.append(f'tl.fromTo("#h-boot",{{opacity:0}},{{opacity:1,duration:.22,immediateRender:false}},{r4(31.3)});')
hto('#h-boot', 1920, 1005, 4.6, .5, 31.3, 'power2.out')
hto('#h-boot', 1990, 1010, 4.6, r4(b - 31.8), 31.8, 'none')
pop('#h-pill', 31.942, scale=.5, click=False); sfx['pop'].append(31.942)
bump('#h-pill', 32.45, 1.06)
chapters.append((a, b, '여기 학교 과정에 넣었습니다', '실제 관제 캡처 main-t6000 CORE 펀치인 → main-t1500 "SECOND BRAIN ... MOUNTED" 3배 펀치인·팬 + v5 승인 배지'))

# ---------------------------------------------------------------- C7 32.992 ~ 36.722 : 정리 못해서 남겨둔 파일이 이번엔 준비물이 됐네요
a, b = C7, F2
sc_pos = [(70, 120, -14), (380, 90, 8), (700, 150, -6), (160, 520, 11), (520, 470, -9), (800, 560, 6)]
scat = ''.join(f'<div class="memo pop" id="sc{i}" style="left:{x}px;top:{y}px;width:250px;height:333px"><img src="assets/page-{(i%8)+1:02d}.png"></div>' for i, (x, y, r) in enumerate(sc_pos))
tangle = scrib(80, 140, 920, 800, 'M40 400 C 200 60, 420 760, 560 300 C 660 20, 880 120, 780 460 C 700 720, 300 700, 420 420 C 520 200, 820 640, 880 720', '', 'tangle')
lpill = '<div class="pill ink pop" id="lpill" style="left:330px;top:950px">남겨둔 파일</div>'
stamp = '<div class="stamp pop" id="stamp1" style="left:640px;top:880px">준비물</div>'
chk = '<div class="pill green pop" id="gchk" style="left:90px;top:905px">✓ 수업 준비물</div>'
clip(scat + tangle + lpill + stamp + chk, a, b, 5, 'stage')
for i, (x, y, r) in enumerate(sc_pos):
    pop(f'#sc{i}', 33.022 + i * .1, scale=.7, rot=r, dur=.25)
draw('#tangle path', 33.55, .45)
pop('#lpill', 33.922, click=False); sfx['pop'].append(33.922)
anim.append(f'tl.to("#basic #sc0,#basic #sc1,#basic #sc2,#basic #sc3,#basic #sc4,#basic #sc5",{{x:12,duration:.07,yoyo:true,repeat:5}},{r4(34.3)});')
bump('#lpill', 34.75, 1.08)
out('#sc0,#sc1,#sc2,#sc3,#sc4,#sc5,#tangle,#lpill', 35.0, .14, y=-60)
parts.append(f'<video id="vfiles" class="clip vcard pop" src="assets/vlog-files.mp4" data-start="{r4(35.062)}" data-duration="{r4(b-35.062)}" data-media-start="1.0" data-track-index="7" style="left:70px;top:110px;width:940px;height:720px;z-index:7;object-position:50% 42%" muted></video>')
pop('#vfiles', 35.062, scale=.8, y=60, click=False); sfx['pop'].append(35.062)
anim.append(f'tl.fromTo("#stamp1",{{opacity:0,scale:1.7,rotation:-8}},{{opacity:1,scale:1,rotation:-8,duration:.22,ease:"power3.out",immediateRender:false}},{r4(35.6)});'); sfx['pop'].append(35.6)
pop('#gchk', 35.95, y=20)
bump('#stamp1', 36.342, 1.12)
chapters.append((a, b, '정리 못해서 남겨둔 파일이 이번엔 준비물이 됐네요', '실제 페이지 6장 흩어짐 + 빨간 엉킨 낙서선 + "남겨둔 파일" → 실촬 vlog-files(교실) 카드 + "준비물" 도장 + 초록 체크'))
chapters.append((F2, C8, '내 자료로 뭘 만들지 찾아보는', '얼굴 풀프레임 (자막 y=1340)'))

# ---------------------------------------------------------------- C8~C10 38.842 ~ end : 워크북 / 댓글 CTA / 무료 워크북 대댓글
a = C8
wb = ('<div class="workbook pop" id="wb" style="top:250px"><small>내 자료로 뭘 만들지</small><strong>시작<br>워크북</strong>'
      '<div class="line" id="wl0"></div>찾아보는 워크북<div class="line" id="wl1"></div>'
      '<div class="stamp pop" id="stamp2">무료</div></div>')
wund = scrib(200, 590, 360, 40, 'M8 26 C 110 4, 250 34, 352 10', '', 'wb-under')
cta = ('<div class="cta" id="cta"><span class="pop" id="c1">댓글에 <em>“시작”</em></span><span class="sub pop" id="c2">남겨주세요</span></div>'
       + scrib(560, 142, 300, 36, 'M6 26 C 80 4, 200 30, 292 8', '', 'c-under')
       + '<div class="comment pop" id="comment"><div class="top">댓글</div><div class="entry"><span class="avatar">나</span><span class="ph" id="c-ph">댓글 달기…</span><b id="c-word" style="opacity:0">시작</b><span class="reply" id="c-reply">게시</span></div></div>'
       + '<div class="chip pop" id="chip">↳ 대댓글로 드려요</div>')
clip(wb + wund + cta, a, D, 5, 'stage')
rise('#wb', C8 + .02, y=120)
anim.append(f'tl.fromTo("#wl0,#wl1",{{scaleX:0}},{{scaleX:1,duration:.3,stagger:.15,ease:"power2.out",immediateRender:false}},{r4(39.15)});'); sfx['click'].append(39.15)
bump('#wb', 39.1, 1.025); bump('#stamp2', 39.3, 1.0)
draw('#wb-under path', 39.562, .3)
bump('#wb', 40.05, 1.03)
# C9 댓글 CTA
out('#wb,#wb-under', C9 - .02, .16, y=120)
pop('#c1', C9 + .02, y=-20); pop('#c2', C9 + .14, y=-20, click=False)
rise('#comment', C9 + .2)
anim.append(f'tl.set("#c-ph",{{opacity:0}},{r4(40.95)});tl.fromTo("#c-word",{{opacity:0,x:16,scale:.8}},{{opacity:1,x:0,scale:1,duration:.18,ease:"back.out(1.7)",immediateRender:false}},{r4(40.95)});'); sfx['pop'].append(40.95)
draw('#c-under path', 41.302, .3)
bump('#c-reply', 41.6, 1.15)
# C10 무료 워크북 + 대댓글
out('#comment', C10 - .02, .18, y=-60)
anim.append(f'tl.fromTo("#wb",{{opacity:0,y:140,rotation:-4,scale:.9}},{{opacity:1,y:80,rotation:0,scale:1,duration:.34,ease:"back.out(1.4)",immediateRender:false}},{r4(C10+.1)});')
anim.append(f'tl.fromTo("#stamp2",{{opacity:0,scale:1.7,rotation:-8}},{{opacity:1,scale:1,rotation:-8,duration:.22,ease:"power3.out",immediateRender:false}},{r4(42.5)});'); sfx['pop'].append(42.5)
pop('#chip', 43.002, y=30, click=False); sfx['pop'].append(43.002)
bump('#stamp2', 43.6, 1.12)
bump('#chip', 44.1, 1.08)
bump('#stamp2', 44.55, 1.1)
chapters.append((C8, C9, '워크북부터 해보셔도 됩니다', '워크북 카드 목업(내 자료로 뭘 만들지 / 시작 워크북) + 빨간 밑줄'))
chapters.append((C9, C10, '댓글에 시작 남겨주세요', 'CTA 제목 + 댓글 목업 "시작" 입력'))
chapters.append((C10, D, '무료 워크북을 대댓글로 드리도록 하겠습니다', '워크북 카드 복귀 + "무료" 도장 + "↳ 대댓글로 드려요" 칩'))

# ---------------------------------------------------------------- captions
terms = ['미쳤나', '미쳐서', 'AI 학교', '준비물', '파일', '고객', '메모', 'AI한테', '꺼내', '했는지', '반복', '재료', '기록을', '제2의', '뇌', '학교', '워크북', '댓글', '시작']


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

sfx['whoosh'] += [C1, C2, C3, C5, C6, C7, C9, C10]
(R / 'timing.json').write_text(json.dumps({k: sorted(set(round(x, 4) for x in v)) for k, v in sfx.items()}, indent=1, ensure_ascii=False))
(R / 'chapters.json').write_text(json.dumps([{'start': r4(a), 'end': r4(b), 'line': l, 'stage': s} for a, b, l, s in chapters], indent=1, ensure_ascii=False))
(C / 'index.html').write_text(
    ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>' + css + '</style></head><body>'
     f'<div id="basic" data-composition-id="basic" data-width="1080" data-height="1920" data-start="0" data-duration="{D}">' + ''.join(parts) + '</div>'
     '<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});' + ''.join(anim) + 'window.__timelines.basic=tl;</script></body></html>').replace('PERSON_POS', PERSON_POS))
print('built', D, 'clips', len(parts), 'anims', len(anim), {k: len(v) for k, v in sfx.items()})
