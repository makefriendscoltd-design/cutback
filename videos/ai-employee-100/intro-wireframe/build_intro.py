"""8~27일차 관제탑 대체 인트로. 1080x1130, 5초. 사용: python3 build_intro.py 8"""
import html
from pathlib import Path

R = Path(__file__).resolve().parent
day = 8
try:
    import sys
    if len(sys.argv) > 1:
        day = int(sys.argv[1])
except ValueError:
    day = 8

TEAMS = [
    ('콘텐츠팀', ['콘텐츠 기획자', '영상편집자', '숏폼 영상편집자', '유튜브 채널 관리자']),
    ('글쓰기팀', ['콘텐츠 에디터', '블로그 마케터', '카페 바이럴 마케터', '출판 편집자']),
    ('홍보팀', ['SNS 마케터', '릴스 PD', '네이버 카페 관리자', '카카오톡 채널 관리자']),
    ('디자인팀', ['그래픽 디자이너', 'SNS 콘텐츠 디자이너', 'PPT 디자이너', '상세페이지 디자이너']),
    ('고객지원팀', ['쇼핑몰 CS 담당자', '쇼핑몰 운영 관리자', '퍼포먼스 마케터', '출고·배송 관리 담당자']),
    ('경영지원팀', ['비서', '운영 매니저', '시스템 모니터링 요원', 'IT 운영 담당자']),
]
# 8~27일차 = 콘텐츠팀부터 순서. 디자인팀은 1~7일차에서 이미 출근한 자리로 둔다.
SERIES = []
for ti, (tname, jobs) in enumerate(TEAMS):
    if tname == '디자인팀':
        continue
    for job in jobs:
        SERIES.append((tname, job))
today_team, today_job = SERIES[day - 8]
already = {SERIES[i][1] for i in range(0, max(0, day - 8))}
DESIGN = set(TEAMS[3][1])

PROMPT = {
    8: ['이 폴더에 콘텐츠 기획자', 'AI 직원을 만들어줘.'],
}

prompt_lines = PROMPT.get(day, [f'이 폴더에 {today_job}', 'AI 직원을 만들어줘.'])
prompt_text = '\n'.join(prompt_lines)
chars = list(prompt_text)

C = R / 'composition'
A = C / 'assets'
A.mkdir(parents=True, exist_ok=True)
for name, src in {
    'gsap.min.js': R.parent / 'assets/vendor/gsap.min.js',
    'Pretendard-Bold.woff2': R / 'assets/Pretendard-Bold.woff2',
    'Pretendard-SemiBold.woff2': R / 'assets/Pretendard-SemiBold.woff2',
    'Pretendard-Medium.woff2': R / 'assets/Pretendard-Medium.woff2',
    'Pretendard-ExtraBold.woff2': R / 'assets/Pretendard-ExtraBold.woff2',
}.items():
    dst = A / name
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    dst.symlink_to(src.resolve())

seats_html = []
hire_ids = []
today_id = None
n = 0
for ti, (tname, jobs) in enumerate(TEAMS):
    bay_cls = 'bay'
    if tname == today_team:
        bay_cls += ' today'
    if tname == '디자인팀' or tname == today_team:
        bay_cls += ' focus'
    rows = []
    for ji, job in enumerate(jobs):
        n += 1
        sid = f's{n:02d}'
        is_today = job == today_job
        is_hired = job in DESIGN or job in already
        if is_today:
            today_id = sid
            is_hired = False
        if is_hired:
            hire_ids.append(sid)
        paper_cls = 'paper today' if is_today else 'paper'
        rows.append(
            f'<div class="seat" id="{sid}">'
            f'<div class="ghost" id="{sid}g"><i></i></div>'
            f'<div class="{paper_cls}" id="{sid}p"><i></i><b>{html.escape(job)}</b><em>{n:02d}</em></div>'
            f'</div>'
        )
    seats_html.append(f'<div class="{bay_cls}" id="bay{ti}"><div class="t">{html.escape(tname)}</div>{"".join(rows)}</div>')

typed = ''.join(
    f'<span class="ch" id="ch{i}">{html.escape(ch) if ch != chr(10) else "<br>"}</span>'
    if ch != '\n' else f'<br id="ch{i}">'
    for i, ch in enumerate(chars)
)
# newlines as <br> break the span count; keep spans for non-newline only
typed = []
for i, ch in enumerate(chars):
    if ch == '\n':
        typed.append('<br>')
    else:
        typed.append(f'<span class="ch" id="ch{i}">{html.escape(ch)}</span>')
typed = ''.join(typed)
type_ids = [i for i, ch in enumerate(chars) if ch != '\n']

# Camera: world origin 50% 50% = (540, 565). Seat 01 center ~ (109, 352) for day 8.
# Later days: column index * 172.
team_index = next(i for i, (n, _) in enumerate(TEAMS) if n == today_team)
job_index = TEAMS[team_index][1].index(today_job)
# CSS: bays left 28, width 1024, gap 10, 6 cols → colW 162.333
col_w = (1024 - 50) / 6
wx = 28 + team_index * (col_w + 10) + col_w / 2
# bay top 228 + pad 10 + title ~42 + seat 148 * job_index + 74
wy = 228 + 10 + 42 + job_index * 158 + 74
S = 1.78
sx, sy = 250.0, 310.0
cam_x = round(sx - 540 - (wx - 540) * S, 1)
cam_y = round(sy - 565 - (wy - 565) * S, 1)

hire_n = len(hire_ids) + 1  # after today clocks in
pre_n = len(hire_ids)

html_out = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:P;src:url(assets/Pretendard-Medium.woff2);font-weight:500}}
@font-face{{font-family:P;src:url(assets/Pretendard-SemiBold.woff2);font-weight:600}}
@font-face{{font-family:P;src:url(assets/Pretendard-Bold.woff2);font-weight:700}}
@font-face{{font-family:P;src:url(assets/Pretendard-ExtraBold.woff2);font-weight:800}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1130px;overflow:hidden;background:#0b1726}}
#orgintro{{position:relative;width:1080px;height:1130px;overflow:hidden;background:#0b1726;font-family:P,sans-serif;color:#d7e3f0}}
.clip{{position:absolute;inset:0;overflow:hidden}}
.scene{{position:absolute;inset:0;overflow:hidden;background:#0b1726}}
.scene:before{{content:"";position:absolute;inset:0;background-image:radial-gradient(#1a3350 1px,transparent 1px);background-size:28px 28px;opacity:.35;pointer-events:none;z-index:0}}
.chrome{{position:absolute;left:36px;right:36px;top:28px;height:72px;display:flex;align-items:flex-end;justify-content:space-between;border-bottom:1px solid #1e3a58;padding-bottom:14px;z-index:6}}
.chrome .school{{font:800 22px/1 P;letter-spacing:-.04em;color:#8fb4e8}}
.chrome .meta{{position:relative;height:22px;min-width:280px}}
.chrome .meta b{{position:absolute;left:0;right:0;top:0;text-align:center;font:600 18px/1 P;color:#6d8aaa;opacity:0;white-space:nowrap}}
.chrome .count{{position:relative;width:90px;height:28px}}
.chrome .count b{{position:absolute;right:0;top:0;font:800 22px/1 P;color:#f5f7fa;opacity:0}}
.world{{position:absolute;inset:0;transform-origin:50% 50%;will-change:transform;z-index:2}}
#org{{position:absolute;inset:0;transform-origin:50% 45%;will-change:transform}}
.hub{{position:absolute;left:330px;top:118px;width:420px;height:86px;border:1.5px solid #3d6aa3;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0b1726;z-index:3}}
.hub b{{font:800 28px/1 P;letter-spacing:-.05em;color:#f5f7fa}}
.hub span{{margin-top:8px;font:600 15px/1 P;color:#9cb6d0}}
svg.leads{{position:absolute;left:0;top:118px;width:1080px;height:180px;z-index:1}}
.bays{{position:absolute;left:28px;right:28px;top:228px;display:grid;grid-template-columns:repeat(6,1fr);gap:10px;z-index:2}}
.bay{{border:1px solid #23486c;padding:10px 8px 12px}}
.bay .t{{font:800 17px/1 P;color:#8fb4e8;text-align:center;padding:6px 0 12px;border-bottom:1px dashed #23486c;margin-bottom:12px}}
.seat{{position:relative;height:148px;margin:0 0 10px}}
.ghost,.paper{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px 8px}}
.ghost{{border:1.5px dashed #5b8def}}
.ghost i,.paper i{{width:34px;height:34px;border-radius:50%;display:block;margin-bottom:10px}}
.ghost i{{border:1.5px dashed #5b8def}}
.paper b{{font:700 16px/1.2 P;letter-spacing:-.04em;text-align:center;word-break:keep-all}}
.paper em{{font:600 12px/1 P;margin-top:6px;font-style:normal;color:#122940}}
.paper{{border:1.5px solid #d7e0ea;background:#f5f7fa;color:#122940;opacity:0;transform-origin:50% 50%;will-change:transform}}
.paper i{{background:#122940;border:0}}
.paper.today{{border:2.5px solid #2563eb;box-shadow:0 0 0 6px #2563eb33}}
.paper.today i{{background:#2563eb}}
.paper em{{color:#5b6b7c}}
.scan{{position:absolute;left:40px;top:250px;width:8px;height:720px;background:#2563eb;opacity:0;z-index:4;will-change:transform}}
.log{{position:absolute;left:36px;right:36px;bottom:28px;height:86px;border:1px solid #23486c;z-index:6;background:#0b1726ee;overflow:hidden}}
.log p{{position:absolute;left:22px;right:22px;top:26px;font:600 20px/1.3 P;letter-spacing:-.04em;color:#c5d4e4;opacity:0}}
.log strong{{color:#f5f7fa;font-weight:800}}
.prompt{{position:absolute;left:500px;top:200px;width:532px;height:430px;border:1.5px solid #3d7ad0;background:#071018;padding:28px 26px;z-index:7;opacity:0;transform-origin:0% 50%;will-change:transform}}
.prompt .bar{{display:flex;gap:8px;margin-bottom:18px}}
.prompt .bar u{{width:12px;height:12px;border-radius:50%;background:#2a5078;display:block;text-decoration:none}}
.prompt .path{{font:600 18px/1 P;color:#9cb6d0;margin-bottom:22px}}
.prompt .body{{font:800 32px/1.4 P;letter-spacing:-.05em;color:#f5f7fa;word-break:keep-all}}
.ch{{font-size:0;opacity:0}}
.cur{{display:inline-block;width:16px;height:34px;background:#2563eb;margin-left:4px;vertical-align:-4px;opacity:0}}
</style>
</head>
<body>
<div id="orgintro" data-composition-id="orgintro" data-width="1080" data-height="1130" data-start="0" data-duration="5">
  <div id="scene" class="clip scene" data-start="0" data-duration="5" data-track-index="0">
    <div class="chrome">
      <div class="school" id="school">AI 직원 양성학교</div>
      <div class="meta">
        <b id="m0">조직도 · 도면</b>
        <b id="m1">디자인팀 출근</b>
        <b id="m2">{day}일차 · {html.escape(today_job)}</b>
      </div>
      <div class="count">
        <b id="c0">0 / 24</b>
        <b id="cN">{pre_n} / 24</b>
        <b id="cT">{hire_n} / 24</b>
      </div>
    </div>
    <div class="world" id="world">
      <div id="org">
        <div class="hub" id="hub"><b>우리 회사</b><span>6팀 · 24명 자리</span></div>
        <svg class="leads" viewBox="0 0 1080 180">
          <path d="M540 86 V118" stroke="#3d6aa3" stroke-width="1.5" fill="none"/>
          <path d="M118 118 H962" stroke="#3d6aa3" stroke-width="1.5" fill="none"/>
          <path d="M118 118 V162 M286 118 V162 M454 118 V162 M622 118 V162 M790 118 V162 M958 118 V162" stroke="#3d6aa3" stroke-width="1.5" fill="none"/>
        </svg>
        <div class="bays">{''.join(seats_html)}</div>
        <div class="scan" id="scan"></div>
      </div>
    </div>
    <div class="log">
      <p id="l0">빈 자리 24. <strong>지금부터 AI 직원을 만듭니다.</strong></p>
      <p id="l1">디자인팀 4명 출근. <strong>다음 자리는 {html.escape(today_team)}.</strong></p>
      <p id="l2"><strong>{html.escape(today_job)} 출근.</strong></p>
    </div>
    <div class="prompt" id="prompt">
      <div class="bar"><u></u><u></u><u></u></div>
      <div class="path">{html.escape(today_job.replace(' ', ''))}/</div>
      <div class="body">{typed}<span class="cur" id="cur"></span></div>
    </div>
  </div>
</div>
<script>
const tl = gsap.timeline({{paused:true}});
const pop = (sel, t, dur=0.42) => {{
  tl.fromTo(sel, {{scale:0.86, opacity:0, y:18}}, {{scale:1, opacity:1, y:0, duration:dur, ease:"power3.out", immediateRender:false}}, t);
}};
pop("#school", 0.04, 0.32);
pop("#m0", 0.10, 0.28);
pop("#c0", 0.12, 0.28);
pop("#hub", 0.16, 0.40);
document.querySelectorAll(".bay").forEach((el, i) => pop(el, 0.22 + i * 0.05, 0.36));
pop("#l0", 0.30, 0.30);

tl.fromTo("#scan", {{opacity:0, x:0}}, {{opacity:0.55, x:980, duration:1.32, ease:"none", immediateRender:false}}, 0.42);
tl.to("#scan", {{opacity:0, duration:0.10}}, 1.74);

tl.to("#org", {{scale:1.025, duration:5, ease:"none"}}, 0);

const hires = {hire_ids!r};
hires.forEach((id, i) => {{
  const t = 1.80 + i * 0.11;
  tl.to("#"+id+"g", {{opacity:0, duration:0.16}}, t);
  tl.fromTo("#"+id+"p", {{scale:0.72, opacity:0, y:16}}, {{scale:1, opacity:1, y:0, duration:0.28, ease:"power3.out", immediateRender:false}}, t);
}});
tl.to("#c0", {{opacity:0, duration:0.12}}, 1.80);
tl.fromTo("#cN", {{opacity:0}}, {{opacity:1, duration:0.18, immediateRender:false}}, 1.84);
tl.to("#l0", {{opacity:0, duration:0.12}}, 1.80);
tl.fromTo("#l1", {{opacity:0, y:10}}, {{opacity:1, y:0, duration:0.22, immediateRender:false}}, 1.86);
tl.to("#m0", {{opacity:0, duration:0.12}}, 1.80);
tl.fromTo("#m1", {{opacity:0}}, {{opacity:1, duration:0.18, immediateRender:false}}, 1.84);

tl.to("#{today_id}g", {{opacity:0, duration:0.16}}, 2.48);
tl.fromTo("#{today_id}p", {{scale:0.7, opacity:0, y:18}}, {{scale:1, opacity:1, y:0, duration:0.32, ease:"power3.out", immediateRender:false}}, 2.48);

tl.to("#world", {{scale:{S}, x:{cam_x}, y:{cam_y}, duration:0.88, ease:"power2.inOut"}}, 2.57);

tl.to("#cN", {{opacity:0, duration:0.12}}, 3.10);
tl.fromTo("#cT", {{opacity:0}}, {{opacity:1, duration:0.18, immediateRender:false}}, 3.14);
tl.to("#l1", {{opacity:0, duration:0.12}}, 3.10);
tl.fromTo("#l2", {{opacity:0, y:8}}, {{opacity:1, y:0, duration:0.20, immediateRender:false}}, 3.16);
tl.to("#m1", {{opacity:0, duration:0.10}}, 3.10);
tl.fromTo("#m2", {{opacity:0}}, {{opacity:1, duration:0.16, immediateRender:false}}, 3.14);

tl.fromTo("#prompt", {{scale:0.84, opacity:0, x:40}}, {{scale:1, opacity:1, x:0, duration:0.36, ease:"power3.out", immediateRender:false}}, 3.18);
const ids = {type_ids!r};
const t0 = 3.34, t1 = 4.72;
const step = (t1 - t0) / Math.max(ids.length, 1);
ids.forEach((id, i) => tl.set("#ch"+id, {{opacity:1, fontSize:"32px"}}, t0 + i * step));
tl.fromTo("#cur", {{opacity:1}}, {{opacity:0, duration:0.28, yoyo:true, repeat:6, ease:"none"}}, 3.34);
window.__timelines["orgintro"] = tl;
</script>
</body>
</html>
'''

(C / 'index.html').write_text(html_out)
timing = {
    'day': day,
    'duration': 5.0,
    'today': {'team': today_team, 'job': today_job},
    'hired_before': pre_n,
    'camera': {'scale': S, 'x': cam_x, 'y': cam_y, 'target': [round(wx, 1), round(wy, 1)]},
    'sfx': {
        'whoosh': [0.16, 1.80, 2.57],
        'pop': [1.80 + i * 0.11 for i in range(len(hire_ids))] + [2.48, 3.18],
        'typing': [3.34],
    },
}
import json
(R / 'timing.json').write_text(json.dumps(timing, ensure_ascii=False, indent=2))
print(f'wrote {C / "index.html"} day={day} today={today_job} cam=({cam_x},{cam_y}) scale={S}')
