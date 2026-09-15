"""AI 학교 6일차 — Kallaway 레퍼런스 + 관제탑 인트로 빌드 (7일차 승인 문법 이식).

3단 고정 레이아웃: 상단 무대(0~1130) / 자막(1150) / 인물 카드(60,1235,960x640 r28).
대본(메모 폴더 검색 -> 안내문 작성, 주제만 바꿔 재실행)에 맞춘 새 장면. 7일차 장면 문구 복사 없음.
모든 시각은 출력 타임라인 초(captions.json / edit-plan.json, 29.6초).
"""
from pathlib import Path
import json, html, os
PERSON_POS = os.environ.get('PERSON_POS', '50')

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
C = R / 'composition'
A = C / 'assets'
A.mkdir(parents=True, exist_ok=True)
plan = json.loads((R / 'edit-plan.json').read_text())
D = plan['duration']
caps = json.loads((R / 'captions.json').read_text())
V4 = ROOT / 'videos/day6-basic-mix-v4-20260915/assets'


def link(n, p):
    q = A / n
    if q.is_symlink() or q.exists():
        q.unlink()
    q.symlink_to(Path(p).resolve())


link('person.mp4', R / 'assets/person.mp4')
link('vlog-classroom.mp4', R / 'assets/vlog-classroom.mp4')
link('font.ttf', ROOT / 'verification-renders/20260911_180156-r01-v19/composition/assets/Pretendard-SemiBold.ttf')
link('black.ttf', ROOT / 'verification-renders/20260911_180156-r01-v7/composition/assets/Pretendard-Black.ttf')
link('gsap.min.js', ROOT / 'videos/day1-sc-vlog/composition/assets/vendor/gsap.min.js')
link('hud-intro.mp4', R / 'assets/hud-intro-1080x1130.mp4')
for i in range(1, 9):
    link(f'page-{i:02d}.png', V4 / f'generated/memo/page-{i:02d}.png')

# ---------------------------------------------------------------- chapter times (caption starts)
INTRO, SEARCH, STEP1, STEP2, STEP3, RERUN, CLASS, FACE, CTA, BOOK = (
    0.0, 4.608, 8.121, 9.708, 12.728, 16.855, 19.542, 23.035, 25.775, 27.415)
PUSH = 2.494  # "AI에 미쳐서"
DARK = [(INTRO, SEARCH), (STEP1, STEP2), (RERUN, CLASS)]
LIGHT = [(SEARCH, STEP1), (STEP2, RERUN), (CLASS, FACE), (CTA, D)]
FULL = [(FACE, CTA)]

css = '''
@font-face{font-family:Pretendard;src:url(assets/font.ttf);font-weight:600}
@font-face{font-family:Black;src:url(assets/black.ttf);font-weight:900}
*{box-sizing:border-box}
html,body{margin:0;background:#000;width:1080px;height:1920px;overflow:hidden}
#basic{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000;font-family:Pretendard,sans-serif}
.clip{position:absolute}
.bg{left:0;top:0;width:1080px;height:1920px;z-index:1}
.bg.light{background:#f1efe9} .bg.dark{background:#0b0b0d}
.stage{left:0;top:0;width:1080px;height:1130px;overflow:hidden;z-index:5;color:#171717}
.stage.dark{color:#fff}
#person-box{position:absolute;left:60px;top:1235px;width:960px;height:640px;z-index:10;overflow:hidden;border-radius:28px;box-shadow:0 26px 50px #0005;transform-origin:50% 45%}
#person-box video{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:50% PERSON_POS%}
.caption{left:30px;right:30px;top:1150px;z-index:20;font:900 58px/1.2 Black;letter-spacing:-1.5px;text-align:center;white-space:nowrap;color:#171717}
.caption.onfull{top:1340px;color:#fff;-webkit-text-stroke:5px #171d20;paint-order:stroke fill;text-shadow:0 5px 6px #000,0 0 12px #000e}
.caption.ondark{color:#fff}
.accent{color:#ff434b}
.pop{opacity:0}
.head{left:40px;right:40px;top:360px;z-index:30;text-align:center;font:900 122px/1.1 Black;letter-spacing:-5px;color:white;-webkit-text-stroke:7px black;paint-order:stroke fill;text-shadow:0 8px 9px #0009}
.head span{display:block}
.scrib{position:absolute;overflow:visible}
.scrib path{fill:none;stroke:#ff434b;stroke-width:9;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;opacity:0}
.scrib.green path{stroke:#3ddc84}
.num{position:absolute;left:66px;top:34px;font:900 150px/1 Black;color:#ff434b;letter-spacing:-8px}
.num small{display:block;font:600 30px/1 Pretendard;color:#171717;letter-spacing:6px;margin:-4px 0 0 10px}
.dark .num small{color:#ddd}
.memo{position:absolute;overflow:hidden;border-radius:12px;box-shadow:0 14px 26px #0003;background:#fff}
.memo img{width:100%;height:100%;object-fit:cover;object-position:top;display:block}
.pill{position:absolute;padding:14px 30px;border-radius:999px;background:#ff434b;color:#fff;font:900 36px/1 Black;box-shadow:0 12px 24px #0004;white-space:nowrap}
.pill.ink{background:#171717}
/* S1 search */
.search{position:absolute;left:90px;top:84px;width:900px;height:116px;border-radius:58px;background:#fff;border:5px solid #171717;box-shadow:0 20px 40px #0002;display:flex;align-items:center;padding:0 40px;font:600 46px/1 Pretendard;color:#171717;white-space:nowrap}
.mag{position:relative;width:46px;height:46px;border:7px solid #171717;border-radius:50%;margin-right:30px;flex:none}
.mag:after{content:"";position:absolute;left:36px;top:38px;width:22px;height:7px;background:#171717;transform:rotate(45deg);border-radius:4px}
.search .lbl{color:#9a9a9a;font-size:34px;margin-right:22px}
.hit{position:absolute;padding:10px 20px;border-radius:999px;background:#1fbf6a;color:#fff;font:900 28px/1 Black;white-space:nowrap}
/* S2 codex switch */
.tile{position:absolute;border-radius:22%;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 22px 40px #0006;font-family:Black}
.tile.codex{background:#111;color:#fff;border:6px solid #2e2e2e}
.tile.codex b{font:900 72px/1 Black;letter-spacing:-3px} .tile.codex i{font:600 30px/1 Pretendard;font-style:normal;color:#9aa;margin-bottom:14px;letter-spacing:5px}
.ring{position:absolute;border-radius:26%;border:6px solid #3ddc84;box-shadow:0 0 50px 12px #3ddc8466}
.switch{position:absolute;left:340px;top:640px;width:400px;height:160px;border-radius:80px;background:#2a2a2e;border:5px solid #444}
.knob{position:absolute;left:14px;top:14px;width:122px;height:122px;border-radius:50%;background:#fff;box-shadow:0 8px 16px #0008}
.swlbl{position:absolute;top:0;height:150px;line-height:150px;font:900 44px/150px Black;color:#888}
.strip{position:absolute;left:90px;top:870px;width:900px;height:150px;border-radius:24px;background:#16181d;border:3px solid #333;padding:0 44px;font:600 44px/150px "SF Mono",Menlo,monospace;color:#e6e6e6;white-space:pre}
.strip .p{color:#3ddc84}
.cur{display:inline-block;width:22px;height:46px;background:#e6e6e6;vertical-align:-8px;margin-left:6px}
/* S3 folder */
.fold{position:absolute;left:230px;top:560px;width:620px;height:440px}
.fold .back{position:absolute;left:0;top:40px;width:620px;height:400px;border-radius:26px;background:#e8a93a}
.fold .tab{position:absolute;left:0;top:0;width:240px;height:80px;border-radius:22px 22px 0 0;background:#e8a93a}
.fold .lid{position:absolute;left:0;top:120px;width:620px;height:320px;border-radius:26px;background:#ffc75a;box-shadow:0 -6px 0 #0001 inset;display:flex;align-items:center;justify-content:center;font:900 64px/1 Black;color:#5a3b00;transform-origin:50% 100%}
.counter{position:absolute;right:80px;top:70px;background:#171717;color:#fff;padding:14px 30px;border-radius:999px;font:900 38px/1 Black}
.cursor{position:absolute;width:70px;height:90px}
/* S4 prompt + nodes */
.prompt{position:absolute;left:80px;top:220px;width:920px;height:190px;border-radius:40px;background:#fff;border:5px solid #171717;box-shadow:0 24px 48px #0002;padding:40px 160px 40px 46px;font:600 42px/1.5 Pretendard;color:#171717}
.send{position:absolute;right:30px;bottom:30px;width:100px;height:100px;border-radius:50%;background:#ff434b;color:#fff;display:flex;align-items:center;justify-content:center;font:900 56px/1 Black}
.node{position:absolute;top:560px;width:400px;height:430px;border-radius:30px;background:#fff;border:5px solid #171717;box-shadow:12px 14px 0 #d9d6cf;padding:26px 30px;overflow:hidden}
.node h4{margin:0 0 20px;font:900 46px/1.1 Black;letter-spacing:-2px;color:#171717;white-space:nowrap}
.node h4 em{font-style:normal;color:#ff434b}
.node .th{position:absolute;border-radius:8px;overflow:hidden;box-shadow:0 6px 14px #0003}
.node .th img{width:100%;height:100%;object-fit:cover;object-position:top}
.ghost{position:absolute;top:560px;width:400px;height:430px;border-radius:30px;border:5px dashed #bdb9b0;display:flex;align-items:center;justify-content:center;font:900 90px/1 Black;color:#cfcbc2}
.scan{position:absolute;left:0;width:400px;height:14px;background:#3ddc84;box-shadow:0 0 26px 8px #3ddc8488;opacity:0}
/* S5 rerun */
.slbl{position:absolute;left:0;right:0;top:70px;text-align:center;font:600 38px/1 Pretendard;color:#aaa;letter-spacing:4px}
.slot{position:absolute;left:120px;top:130px;width:840px;height:170px;border-radius:32px;border:6px solid #fff;overflow:hidden;background:#15161a}
.slot div{position:absolute;left:0;right:0;top:0;height:158px;line-height:158px;text-align:center;font:900 80px/158px Black;letter-spacing:-3px;color:#fff;opacity:0}
.slot div em{font-style:normal;color:#ff434b}
.run{position:absolute;left:370px;top:350px;width:340px;height:120px;border-radius:60px;background:#ff434b;color:#fff;font:900 54px/120px Black;text-align:center;box-shadow:0 0 0 0 #ff434b88}
.ann{position:absolute;width:380px;height:500px;border-radius:20px;background:#fff;color:#171717;padding:30px 32px;box-shadow:0 26px 50px #000c}
.ann small{display:block;font:900 24px/1 Black;color:#ff434b;letter-spacing:3px}
.ann strong{display:block;font:900 52px/1.15 Black;letter-spacing:-2px;margin:18px 0 26px}
.ann i{display:block;height:16px;border-radius:8px;background:#e3e1db;margin:18px 0}
.mock{position:absolute;right:28px;top:1090px;font:600 22px/1 Pretendard;color:#777}
/* S6 class */
.vframe{position:absolute;left:80px;top:170px;width:540px;height:944px;border-radius:26px;background:#fff;box-shadow:0 30px 60px #0004}
.vlog{left:92px;top:182px;width:516px;height:920px;border-radius:18px;object-fit:cover;z-index:7}
/* CTA */
.cta{position:absolute;left:0;right:0;top:80px;text-align:center;font:900 96px/1.1 Black;letter-spacing:-4px}
.cta em{font-style:normal;color:#ff434b}
.thread{position:absolute;left:70px;top:300px;width:940px;border-radius:30px;background:#fff;border:4px solid #171717;padding:30px 40px 36px;box-shadow:0 24px 50px #0002;font:600 36px/1.4 Pretendard;color:#171717}
.thread .top{border-bottom:3px solid #eee;padding-bottom:16px;font-size:32px;color:#777}
.entry{display:flex;align-items:center;margin-top:30px;height:96px}
.avatar{display:inline-flex;flex:none;border-radius:50%;width:84px;height:84px;align-items:center;justify-content:center;background:#171717;color:#fff;margin-right:26px;font:900 36px/1 Black}
.entry b{color:#ff434b;font:900 76px/1 Black}
.entry .ph{color:#b5b5b5}
.post{margin-left:auto;padding:16px 36px;border-radius:999px;background:#171717;color:#fff;font:900 34px/1 Black}
.reply{position:absolute;left:170px;top:640px;width:840px;border-radius:30px;background:#fff;border:4px solid #171717;padding:26px 34px;box-shadow:12px 14px 0 #ff434b;font:600 34px/1.3 Pretendard;color:#171717}
.reply .tag{font:900 34px/1 Black;color:#ff434b}
.wbfile{display:flex;align-items:center;margin-top:24px;padding:22px 26px;border-radius:22px;background:#fff9e9;border:3px solid #e3d6c0}
.doc{position:relative;width:96px;height:124px;flex:none;border-radius:10px;background:#fff;border:4px solid #171717;margin-right:28px}
.doc:before,.doc:after{content:"";position:absolute;left:16px;right:16px;height:8px;border-radius:4px;background:#ddd;top:40px}
.doc:after{top:66px}
.wbfile strong{font:900 64px/1 Black;letter-spacing:-3px}
.stamp{position:absolute;right:40px;top:36px;padding:14px 26px;border:5px solid #ff434b;border-radius:12px;color:#ff434b;font:900 46px/1 Black;transform:rotate(-8deg);background:#fff}
'''

parts = []
anim = []
sfx = {'whoosh': [], 'click': [], 'pop': [], 'typing': []}


def r4(x):
    return round(x, 4)


def clip(html_, a, b, z, cls='', extra=''):
    parts.append(f'<div class="clip {cls}" style="z-index:{z};{extra}" data-start="{r4(a)}" data-duration="{r4(b-a)}" data-track-index="{z}">{html_}</div>')


def pop(sel, t, dur=.32, scale=.6, y=30, ease='back.out(1.7)', click=True, rot=None):
    r0 = f',rotation:{rot[0]}' if rot else ''
    r1 = f',rotation:{rot[1]}' if rot else ''
    anim.append(f'tl.fromTo("{sel}",{{opacity:0,scale:{scale},y:{y}{r0}}},{{opacity:1,scale:1,y:0{r1},duration:{dur},ease:"{ease}",immediateRender:false}},{r4(t)});')
    if click:
        sfx['click'].append(r4(t))


def rise(sel, t, dur=.3, y=60):
    anim.append(f'tl.fromTo("{sel}",{{opacity:0,y:{y},scale:.96}},{{opacity:1,y:0,scale:1,duration:{dur},ease:"power3.out",immediateRender:false}},{r4(t)});')


def draw(sel, t, dur=.35):
    anim.append(f'tl.set("{sel}",{{opacity:1}},{r4(t)});tl.to("{sel}",{{strokeDashoffset:0,duration:{dur},ease:"power2.inOut"}},{r4(t)});')


def bump(sel, t, y=-14, dur=.12):
    anim.append(f'tl.to("{sel}",{{y:{y},duration:{dur},yoyo:true,repeat:1,ease:"power2.inOut"}},{r4(t)});')


def pulse(sel, t, s=1.1, dur=.13):
    anim.append(f'tl.to("{sel}",{{scale:{s},duration:{dur},yoyo:true,repeat:1,ease:"power2.inOut"}},{r4(t)});')


def scrib(x, y, w, h, d, cls='', sid=''):
    return f'<svg class="scrib {cls}" id="{sid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px" viewBox="0 0 {w} {h}"><path pathLength="1" d="{d}"/></svg>'


def typed(text, sid):
    return ''.join(f'<span id="{sid}-{i}" style="opacity:0">{html.escape(ch)}</span>' for i, ch in enumerate(text))


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
for a, b in FULL:
    anim.append(f'tl.set("#person-box",{VFULL},{r4(a)});tl.set("#person",{{objectPosition:"50% 45%"}},{r4(a)});')
    anim.append(f'tl.set("#person-box",{VCARD},{r4(b)});tl.set("#person",{{objectPosition:"50% PERSON_POS%"}},{r4(b)});')
    anim.append(f'tl.fromTo("#person-box",{{scale:1.14}},{{scale:1.19,duration:{r4(b-a)},ease:"sine.out",immediateRender:false}},{r4(a)});')
    sfx['whoosh'] += [r4(a), r4(b)]

# ---------------------------------------------------------------- INTRO 0 ~ 4.608  관제탑 2.5배속(푸시인은 구워둠)
parts.append(f'<video id="hud-intro" class="clip" src="assets/hud-intro.mp4" data-start="0" data-duration="{r4(SEARCH)}" data-media-start="0" data-track-index="3" style="left:0;top:0;width:1080px;height:1130px;z-index:3;object-fit:cover" muted></video>')
# 승인 헤드카피(정본): "POV: AI 미친자가 / 저지른 일", 0~1초, 문구·서체·위치 변경 금지.
parts.append('<div id="head" class="clip head" data-start="0" data-duration="1" data-track-index="30"><span>POV: AI 미친자가</span><span>저지른 일</span></div>')
sfx['whoosh'] += [INTRO, PUSH]

# ---------------------------------------------------------------- S1 메모 검색 -> 안내문  4.608 ~ 8.121
a, b = SEARCH, STEP1
GRID = [1, 2, 3, 4, 5, 6]
HITS = [0, 3, 5]  # page-01 회의 메모 / 04 고객 질문 / 06 준비물 체크
qtxt = '시간 · 장소 · 준비물'
g = ''
for k, pg in enumerate(GRID):
    col, row = k % 3, k // 3
    g += f'<div class="memo pop" id="m{k}" style="left:{90+col*310}px;top:{260+row*420}px;width:280px;height:373px"><img src="assets/page-{pg:02d}.png"></div>'
hits = ''.join(f'<div class="hit pop" id="hit{j}" style="left:{90+(k%3)*310+150}px;top:{260+(k//3)*420-22}px">찾음</div>' for j, k in enumerate(HITS))
search = f'<div class="search pop" id="sbar"><span class="mag"></span><span class="lbl">메모 검색</span>{typed(qtxt, "q")}<span class="cur" id="scur" style="background:#171717"></span></div>'
ann = '<div class="memo pop" id="annc" style="left:330px;top:250px;width:470px;height:627px;box-shadow:0 40px 80px #0006"><img src="assets/page-08.png"></div>'
arrow1 = ''
under1 = scrib(350, 690, 300, 40, 'M8 26 C 90 6, 210 34, 322 10', '', 'u1')
clip(g + hits + search + ann + arrow1 + under1, a, b, 5, 'stage')
for k in range(6):
    pop(f'#m{k}', a + .06 + k * .16, scale=.7, y=40)
rise('#sbar', 5.908, .28, y=-40); sfx['click'].append(5.908)
type_in('q', len(qtxt), 5.98, 6.55)
anim.append(f'tl.fromTo("#scur",{{opacity:1}},{{opacity:0,duration:.25,yoyo:true,repeat:7}},{r4(5.95)});')
anim.append(f'tl.to("#m1,#m2,#m4",{{opacity:.28,duration:.2}},{r4(6.3)});')
for j, k in enumerate(HITS):
    t = 6.35 + j * .18
    anim.append(f'tl.set("#m{k}",{{boxShadow:"0 0 0 7px #3ddc84,0 0 44px 10px #3ddc84aa"}},{r4(t)});')
    pop(f'#hit{j}', t, scale=.4, y=10)
anim.append(f'tl.fromTo("#annc",{{opacity:0,y:500,rotation:12,scale:.8}},{{opacity:1,y:0,rotation:-3,scale:1,duration:.42,ease:"power3.out",immediateRender:false}},{r4(6.968)});'); sfx['pop'].append(6.968)
anim.append(f'tl.to("#m0,#m3,#m5",{{opacity:.55,duration:.2}},{r4(7.25)});')
draw('#u1 path', 7.62, .3)
bump('#annc', 7.9, y=-12)

# ---------------------------------------------------------------- S2 STEP 01 코덱스 켜기 (dark)  8.121 ~ 9.708
a, b = STEP1, STEP2
s2 = ('<div class="num pop" id="n1">01<small>STEP</small></div>'
      '<div class="ring pop" id="ring" style="left:375px;top:170px;width:330px;height:330px"></div>'
      '<div class="tile codex pop" id="tcx" style="left:390px;top:185px;width:300px;height:300px"><i>OPENAI</i><b>Codex</b></div>'
      '<div class="switch pop" id="sw"><span class="swlbl" id="swon" style="left:52px;color:#fff;opacity:0">ON</span><span class="swlbl" id="swoff" style="right:48px">OFF</span><div class="knob" id="knob"></div></div>'
      '<div class="strip pop" id="strip"><span class="p">$</span> ' + typed('codex', 'cx') + '<span class="cur" id="ccur"></span></div>')
clip(s2, a, b, 5, 'stage dark')
pop('#n1', a, y=-30)
pop('#tcx', a + .1, scale=.3, rot=(-30, 0), click=False); sfx['pop'].append(r4(a + .1))
pop('#sw', a + .3, scale=.8, y=30)
rise('#strip', a + .38)
type_in('cx', 5, 8.6, 8.95)
anim.append(f'tl.fromTo("#ccur",{{opacity:1}},{{opacity:0,duration:.22,yoyo:true,repeat:5}},{r4(a+.4)});')
pulse('#tcx', 9.02, 1.06)
anim.append(f'tl.to("#knob",{{x:240,duration:.22,ease:"back.out(1.6)"}},{r4(9.341)});tl.to("#sw",{{backgroundColor:"#1fbf6a",borderColor:"#3ddc84",duration:.18}},{r4(9.341)});tl.set("#swoff",{{opacity:0}},{r4(9.341)});tl.set("#swon",{{opacity:1}},{r4(9.43)});'); sfx['click'].append(9.341)
anim.append(f'tl.fromTo("#ring",{{opacity:0,scale:.9}},{{opacity:1,scale:1.06,duration:.25,ease:"power2.out",immediateRender:false}},{r4(9.38)});')

# ---------------------------------------------------------------- S3 STEP 02 메모 폴더 열기  9.708 ~ 12.728
a, b = STEP2, STEP3
FAN = [(1, 150, 290, -12), (2, 330, 250, -5), (4, 510, 235, 2), (6, 690, 250, 7), (7, 870, 290, 13)]
fan = ''.join(f'<div class="memo pop" id="fc{k}" style="left:{x-40}px;top:{y}px;width:180px;height:240px"><img src="assets/page-{pg:02d}.png"></div>' for k, (pg, x, y, r) in enumerate(FAN))
fold = '<div class="fold pop" id="fold"><div class="tab"></div><div class="back"></div><div class="lid" id="lid">메모 폴더</div></div>'
cursor = '<svg class="cursor pop" id="cur3" style="left:840px;top:980px" viewBox="0 0 70 90"><path d="M6 4 L6 74 L24 58 L36 86 L50 80 L38 53 L62 53 Z" fill="#fff" stroke="#171717" stroke-width="6" stroke-linejoin="round"/></svg>'
ring3 = scrib(180, 590, 720, 480, 'M90 70 C 330 -20, 690 20, 700 220 C 710 420, 380 480, 150 430 C -10 390, 0 190, 130 60', '', 'r3')
s3 = ('<div class="num pop" id="n2">02<small>STEP</small></div><div class="counter pop" id="mcount">메모 0장</div>'
      + fold + fan + ring3 + cursor)
clip(s3, a, b, 5, 'stage')
pop('#n2', a, y=-30)
rise('#fold', a + .08, .32, y=80)
pop('#mcount', a + .3, click=False)
anim.append(f'tl.fromTo("#cur3",{{opacity:0,x:120,y:80}},{{opacity:1,x:0,y:0,duration:.2,immediateRender:false}},{r4(10.05)});tl.to("#cur3",{{x:-300,y:-250,duration:.55,ease:"power2.inOut"}},{r4(10.3)});')
for t in (10.988, 11.12):
    anim.append(f'tl.to("#cur3",{{scale:.8,duration:.05,yoyo:true,repeat:1}},{r4(t)});'); sfx['click'].append(t)
draw('#r3 path', 10.95, .38)
anim.append(f'tl.to("#lid",{{scaleY:.42,skewX:-6,duration:.28,ease:"power2.out"}},{r4(11.25)});tl.to("#cur3",{{opacity:0,duration:.15}},{r4(11.25)});')
anim.append('const mc={n:0};')
for k, (pg, x, y, r) in enumerate(FAN):
    t = 11.35 + k * .14
    anim.append(f'tl.fromTo("#fc{k}",{{opacity:0,x:{540-x},y:{560-y},scale:.35,rotation:0}},{{opacity:1,x:0,y:0,scale:1,rotation:{r},duration:.36,ease:"power3.out",immediateRender:false}},{r4(t)});'); sfx['click'].append(r4(t))
anim.append(f'tl.to(mc,{{n:5,duration:.7,ease:"none",snap:"n",onUpdate:()=>{{document.getElementById("mcount").textContent="메모 "+mc.n+"장"}}}},{r4(11.35)});')
pulse('#mcount', 12.1, 1.16)
bump('#fc0,#fc2,#fc4', 12.3, y=-16)
bump('#fc1,#fc3', 12.48, y=-16)

# ---------------------------------------------------------------- S4 STEP 03 프롬프트 -> 검색+작성 연결  12.728 ~ 16.835
a, b = STEP3, RERUN
ptxt = '메모 폴더에서 찾아서 안내문 초안 써줘'
nodeA = ('<div class="node pop" id="nA" style="left:70px"><h4>① 메모 <em>검색</em></h4>'
         '<div class="th" style="left:30px;top:110px;width:160px;height:213px"><img src="assets/page-01.png"></div>'
         '<div class="th" style="left:205px;top:130px;width:160px;height:213px"><img src="assets/page-04.png"></div>'
         '<div class="scan" id="scanA" style="top:110px"></div></div>')
nodeB = ('<div class="node pop" id="nB" style="left:610px"><h4>② 안내문 <em>작성</em></h4>'
         '<div class="th" style="left:80px;top:100px;width:240px;height:320px"><img src="assets/page-08.png"></div></div>')
link4 = scrib(440, 640, 200, 180, 'M20 90 C 70 30, 130 150, 180 90 M180 90 L 140 70 M180 90 L 160 130', '', 'l4')
under4 = scrib(620, 1000, 380, 40, 'M10 20 C 120 36, 250 4, 370 24', '', 'u4')
s4 = ('<div class="num pop" id="n3" style="top:34px">03<small>STEP</small></div>'
      '<div class="prompt pop" id="prm">' + typed(ptxt, 'pt') + '<span class="cur" id="pcur" style="background:#171717;height:48px"></span><div class="send pop" id="send">↑</div></div>'
      + '<div class="ghost pop" id="gA" style="left:70px">?</div><div class="ghost pop" id="gB" style="left:610px">?</div>'
      + nodeA + nodeB + link4 + under4)
clip(s4, a, b, 5, 'stage', 'overflow:hidden')
anim.append(f'tl.set("#prm",{{top:250}},{r4(a)});')
pop('#n3', a, y=-30)
rise('#prm', a + .08)
type_in('pt', len(ptxt), 13.0, 14.25)
anim.append(f'tl.fromTo("#pcur",{{opacity:1}},{{opacity:0,duration:.25,yoyo:true,repeat:5}},{r4(a+.1)});')
pop('#send', 14.3, scale=.3, click=False); sfx['pop'].append(14.3)
pulse('#send', 14.5, 1.15)
pop('#gA', 13.25, scale=.85, y=30, click=False); pop('#gB', 13.55, scale=.85, y=30, click=False)
pulse('#gA', 13.95, 1.05); pulse('#gB', 14.25, 1.05)
anim.append(f'tl.set("#gA,#gB",{{opacity:0}},{r4(14.66)});')
pop('#nA', 14.66, scale=.8, y=60)
anim.append(f'tl.fromTo("#scanA",{{opacity:1,y:0}},{{opacity:1,y:240,duration:.5,ease:"sine.inOut",yoyo:true,repeat:1,immediateRender:false}},{r4(14.95)});')
pop('#nB', 15.35, scale=.8, y=60)
draw('#u4 path', 15.7, .3)
pulse('#nB', 16.0, 1.04)
draw('#l4 path', 16.208, .3)
anim.append(f'tl.set("#nA,#nB",{{borderColor:"#1fbf6a",boxShadow:"0 0 0 6px #3ddc84,0 0 40px 10px #3ddc8488"}},{r4(16.5)});'); sfx['pop'].append(16.5)
bump('#nA,#nB', 16.55, y=-12)

# ---------------------------------------------------------------- S5 주제만 바꿔 재실행 (dark)  16.855 ~ 19.542
a, b = RERUN, CLASS
TOPICS = ['준비물', '시작 시간', '신청 방법']
TT = [16.95, 17.655, 18.355]
slot = '<div class="slot pop" id="slot">' + ''.join(f'<div id="tp{i}"><em>{t}</em> 안내</div>' for i, t in enumerate(TOPICS)) + '</div>'
anns = ''.join(f'<div class="ann pop" id="an{i}" style="left:{350+(i-1)*190}px;top:560px"><small>안내문 초안</small><strong>{t}<br>안내</strong><i></i><i style="width:80%"></i><i></i><i style="width:60%"></i></div>' for i, t in enumerate(TOPICS))
cyc = scrib(330, 320, 420, 180, 'M60 150 C -20 90, 40 10, 210 12 C 380 14, 440 110, 360 160 M360 160 L 392 118 M360 160 L 318 140', '', 'cy')
s5 = '<div class="slbl pop" id="slbl">안내할 주제</div>' + slot + '<div class="run pop" id="run">↻ 실행</div>' + cyc + anns
clip(s5, a, b, 5, 'stage dark')
pop('#slbl', a, y=-20, click=False)
pop('#slot', a + .02, scale=.85, y=-20)
pop('#run', a + .15, scale=.6, click=False)
for i, t in enumerate(TT):
    if i:
        anim.append(f'tl.to("#tp{i-1}",{{y:-160,opacity:0,duration:.16,ease:"power2.in"}},{r4(t)});')
    anim.append(f'tl.fromTo("#tp{i}",{{y:160,opacity:0}},{{y:0,opacity:1,duration:.2,ease:"back.out(1.5)",immediateRender:false}},{r4(t+(.08 if i else 0))});'); sfx['click'].append(r4(t))
    pulse('#run', t + .22, 1.1)
    anim.append(f'tl.fromTo("#an{i}",{{opacity:0,y:-260,rotation:0,scale:.7}},{{opacity:1,y:0,rotation:{(i-1)*6},scale:1,duration:.3,ease:"power3.out",immediateRender:false}},{r4(t+.3)});'); sfx['pop'].append(r4(t + .3))
draw('#cy path', 18.9, .38)
bump('#an0,#an1,#an2', 19.3, y=-14)

# ---------------------------------------------------------------- S6 AI 학교 현장 + 내 기록  19.542 ~ 23.035  (실촬)
a, b = CLASS, FACE
s6 = ('<div class="pill pop" id="live" style="left:80px;top:70px">AI 학교 현장</div>'
      '<div class="vframe pop" id="vfr"></div>'
      '<div class="memo pop" id="r1" style="left:660px;top:190px;width:340px;height:453px"><img src="assets/page-03.png"></div>'
      '<div class="memo pop" id="r2" style="left:680px;top:640px;width:320px;height:427px"><img src="assets/page-05.png"></div>'
      '<div class="pill ink pop" id="rec" style="left:700px;top:96px">내 기록</div>'
      + scrib(560, 420, 160, 220, 'M140 30 C 60 40, 30 110, 40 190 M40 190 L 12 150 M40 190 L 78 162', '', 'a6'))
clip(s6, a, b, 5, 'stage')
parts.append(f'<video id="vlog" class="clip vlog pop" src="assets/vlog-classroom.mp4" data-start="{r4(a)}" data-duration="{r4(b-a)}" data-media-start="0" data-track-index="7" muted></video>')
pop('#live', a, y=-20, click=False)
rise('#vfr', a + .05); rise('#vlog', a + .05)
pop('#rec', 20.642, scale=.5, y=-10)
pop('#r1', 20.75, scale=.7, y=80, rot=(14, 4), click=False); sfx['pop'].append(20.75)
pop('#r2', 21.15, scale=.7, y=80, rot=(-14, -4))
draw('#a6 path', 21.982, .35)
anim.append(f'tl.to("#r1",{{x:-40,duration:.3,ease:"power2.out"}},{r4(22.35)});')
bump('#r2', 22.7, y=-14)

# ---------------------------------------------------------------- S8 CTA 댓글  25.775 ~ 27.415
a = CTA
thread = ('<div class="thread" id="thr"><div class="top">댓글</div><div class="entry"><span class="avatar">나</span>'
          '<span class="ph" id="cph">댓글 추가…</span><b id="cword" style="opacity:0">시작</b><span class="post" id="cpost">게시</span></div></div>')
s8 = ('<div class="cta pop" id="ct1">댓글에 <em>시작</em></div>'
      + scrib(270, 190, 540, 40, 'M8 26 C 150 6, 380 34, 532 10', '', 'u8')
      + '<div class="pop" id="thrwrap" style="position:absolute;left:0;top:180px;width:1080px;height:950px">' + thread + '</div>'
      + '<svg class="cursor pop" id="cur8" style="left:900px;top:960px" viewBox="0 0 70 90"><path d="M6 4 L6 74 L24 58 L36 86 L50 80 L38 53 L62 53 Z" fill="#fff" stroke="#171717" stroke-width="6" stroke-linejoin="round"/></svg>'
      + scrib(140, 560, 300, 180, 'M40 60 C 120 -10, 290 20, 280 100 C 270 170, 90 170, 40 120 C 10 90, 30 50, 70 36', '', 'c8'))
clip(s8, a, BOOK, 5, 'stage')
pop('#ct1', a, y=-20, click=False)
draw('#u8 path', a + .25, .3)
rise('#thrwrap', a + .12)
anim.append(f'tl.set("#cph",{{display:"none"}},{r4(26.3)});tl.fromTo("#cword",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.2,ease:"back.out(1.8)",immediateRender:false}},{r4(26.3)});'); sfx['pop'].append(26.3)
draw('#c8 path', 26.6, .35)
anim.append(f'tl.fromTo("#cur8",{{opacity:0,y:60}},{{opacity:1,y:0,duration:.2,immediateRender:false}},{r4(26.05)});tl.to("#cur8",{{x:-10,y:-330,duration:.5,ease:"power2.inOut"}},{r4(26.4)});tl.to("#cur8",{{scale:.8,duration:.05,yoyo:true,repeat:1}},{r4(27.0)});')
pulse('#cpost', 27.0, 1.15); sfx['click'].append(27.0)
bump('#thr', 27.2, y=-10)

# ---------------------------------------------------------------- S9 대댓글 무료 워크북  27.415 ~ end
a, b = BOOK, D
thread2 = thread.replace('id="thr"', 'id="thr2"').replace('id="cph"', 'id="cph2" style="display:none"').replace('id="cword" style="opacity:0"', 'id="cword2"').replace('id="cpost"', 'id="cpost2"')
reply = ('<div class="reply pop" id="rep"><span class="tag">↳ 대댓글</span>'
         '<div class="wbfile pop" id="wbf"><span class="doc"></span><strong>무료 워크북</strong></div>'
         '<div class="stamp pop" id="stamp">무료</div></div>')
s9 = ('<div class="cta" id="ct2"><em>대댓글</em>로 받기</div>' + '<div id="thr2w" style="position:absolute;left:0;top:0;width:1080px;height:1130px">' + thread2 + '</div>' + reply
      + scrib(80, 520, 120, 260, 'M40 10 C 20 90, 30 190, 100 230 M100 230 L 60 226 M100 230 L 86 192', '', 'a9'))
clip(s9, a, b, 5, 'stage')
pop('#ct2', a, y=-20, click=False)
anim.append(f'tl.fromTo("#thr2w",{{y:180}},{{y:0,duration:.3,ease:"power3.out",immediateRender:false}},{r4(a)});')
anim.append(f'tl.fromTo("#rep",{{opacity:0,x:260}},{{opacity:1,x:0,duration:.32,ease:"power3.out",immediateRender:false}},{r4(a+.1)});')
draw('#a9 path', 27.75, .3)
pop('#wbf', 28.235, scale=.7, y=40, click=False); sfx['pop'].append(28.235)
pop('#stamp', 28.75, scale=1.8, y=0, ease='power3.out', click=False); sfx['pop'].append(28.75)
bump('#rep', 29.15, y=-14)
pulse('#stamp', 29.4, 1.12)

# ---------------------------------------------------------------- captions
terms = ['미쳤나', 'AI 학교', '코덱스', '프롬프트', '안내문', '폴더', '메모', '검색', '주제', '기록', '막막', '대댓글', '댓글', '워크북']


def caption_cls(t):
    if any(x <= t < y for x, y in FULL):
        return 'caption onfull'
    if any(x <= t < y for x, y in DARK):
        return 'caption ondark'
    return 'caption'


for i, c in enumerate(caps):
    t = html.escape(c['text'])
    for w in terms:
        if w in t:
            t = t.replace(w, '<span class="accent">' + w + '</span>', 1); break
    parts.append(f'<div id="cap{i}" class="clip {caption_cls(c["start"])}" data-start="{c["start"]}" data-duration="{round(c["end"]-c["start"],6)}" data-track-index="20">{t}</div>')

sfx['whoosh'] += [SEARCH, STEP1, STEP2, STEP3, RERUN, CLASS, CTA]
(R / 'timing.json').write_text(json.dumps({k: sorted(set(round(x, 4) for x in v)) for k, v in sfx.items()}, indent=1, ensure_ascii=False))
(C / 'index.html').write_text(
    ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>' + css + '</style></head><body>'
     f'<div id="basic" data-composition-id="basic" data-width="1080" data-height="1920" data-start="0" data-duration="{D}">' + ''.join(parts) + '</div>'
     '<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});' + ''.join(anim) + 'window.__timelines.basic=tl;</script></body></html>').replace('PERSON_POS', PERSON_POS))
print('built', D, 'clips', len(parts), 'anims', len(anim), {k: len(set(v)) for k, v in sfx.items()})
