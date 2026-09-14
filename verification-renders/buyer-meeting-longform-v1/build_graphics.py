#!/usr/bin/env python3
"""Build six self-contained HyperFrames overlay-card compositions."""
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parent
GRAPHICS = ROOT / "graphics"

EVENTS = [
    {"id":"01-interest-signal","source_start":7.28,"source_end":13.06,"duration":7,"title":"바이어 미팅 노하우","kind":"signal","labels":["온라인","오프라인","준비·진행"]},
    {"id":"02-interpreter-choice","source_start":75.18,"source_end":82.74,"duration":7,"title":"영어가 부담될 때","kind":"branch","labels":["영어 자신 없음","통역원 섭외","크몽·재능 사이트"]},
    {"id":"03-meeting-flow","source_start":213.02,"source_end":223.44,"duration":8,"title":"회사 소개 방법","kind":"steps","labels":["회사 소개서","3분 설명","대표님 회사"]},
    {"id":"04-offline-kit","source_start":367.80,"source_end":377.52,"duration":7,"title":"오프라인 준비","kind":"check","labels":["영문 명함","미리 준비","비즈니스 매너"]},
    {"id":"05-competition-signal","source_start":523.10,"source_end":541.44,"duration":8,"title":"체류 기간이 주는 신호","kind":"compare","labels":["2박 3일 이상","다른 업체 미팅","경쟁자 있음"]},
    {"id":"06-consulting-meeting","source_start":711.10,"source_end":728.76,"duration":8,"title":"수출상담회 구조","kind":"network","labels":["바이어","5~10개 업체","우리 브랜드"]},
]

PALETTE = {"navy":"#12233F","orange":"#AA5522","paper":"#FFFDF8","muted":"#667080","line":"#C9CFD9"}

def diagram(e):
    a,b,c=e["labels"]
    k=e["kind"]
    if k in ("signal","steps","compare"):
        return f'''<div class="flow"><div class="node n1"><b>01</b><span>{a}</span></div><div class="arrow">→</div><div class="node n2"><b>02</b><span>{b}</span></div><div class="arrow">→</div><div class="node n3 accent"><b>03</b><span>{c}</span></div></div>'''
    if k == "branch":
        return f'''<div class="origin">영어 회화</div><svg class="wires" viewBox="0 0 480 180"><path d="M240 18 V55 M240 55 H105 V90 M240 55 H375 V90"/></svg><div class="branch left"><i>✓</i><span>{a}</span></div><div class="branch right"><i>✓</i><span>{b}</span><small>{c}</small></div>'''
    if k == "check":
        return '<div class="checks">'+''.join(f'<div class="check"><i>✓</i><span>{x}</span></div>' for x in (a,b,c))+'</div>'
    return f'''<div class="hub">{a}</div><svg class="wires network" viewBox="0 0 480 160"><path d="M240 15 V58 M240 58 H85 V102 M240 58 H240 V102 M240 58 H395 V102"/></svg><div class="companies"><span>업체 1</span><span class="focus">{c}</span><span>{b}</span></div>'''

def html(e):
    ident=e['id']; dur=e['duration']
    template = '''<!doctype html><html><head><meta charset="utf-8"></head><body>
<div id="root" data-composition-id="{ident}" data-width="1920" data-height="1080" data-fps="25" data-duration="{dur}">
  <div id="overlay-card" class="clip" data-start="0" data-duration="{dur}" data-track-index="1"><section class="card">
    <div class="bar"></div><header><em>BUYER MEETING</em><h1>{e['title']}</h1></header>
    <div class="diagram">{diagram(e)}</div><div class="rule"></div><footer>핵심 포인트</footer>
  </section></div>
</div>
<style>
@font-face{{font-family:Pretendard;src:url('fonts/Pretendard-SemiBold.ttf')}}
*{{box-sizing:border-box}}html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:transparent}}#root{{position:relative;width:100%;height:100%;font-family:Pretendard,sans-serif;color:{PALETTE['navy']}}}.clip{{position:absolute;inset:0}}.card{{position:absolute;left:150px;top:330px;width:520px;height:390px;background:{PALETTE['paper']};border:2px solid rgba(18,35,63,.16);border-radius:24px;box-shadow:0 18px 48px rgba(10,24,48,.26);overflow:hidden;padding:35px 34px 25px}}.bar{{position:absolute;left:0;top:0;width:12px;height:100%;background:{PALETTE['orange']}}header em{{font-style:normal;font-size:15px;letter-spacing:2px;color:{PALETTE['orange']}}h1{{font-size:34px;line-height:1.15;margin:8px 0 22px;letter-spacing:-1.2px}}.diagram{{height:190px;position:relative}}.flow{{display:flex;align-items:center;justify-content:space-between;height:145px}}.node{{width:116px;height:112px;border:2px solid {PALETTE['line']};border-radius:16px;padding:15px 10px;background:white;display:flex;flex-direction:column;justify-content:center;gap:8px;text-align:center}}.node b{{color:{PALETTE['orange']};font-size:14px}}.node span{{font-size:20px;line-height:1.25}}.node.accent{{border-color:{PALETTE['orange']};background:#FFF3E9}}.arrow{{font-size:25px;color:{PALETTE['orange']}}.origin,.hub{{position:absolute;left:155px;top:0;width:140px;padding:13px;text-align:center;background:{PALETTE['navy']};color:white;border-radius:14px;font-size:20px}}.wires{{position:absolute;left:0;top:38px;width:100%;height:150px;fill:none;stroke:{PALETTE['orange']};stroke-width:4;stroke-linecap:round;stroke-linejoin:round}}.branch{{position:absolute;top:128px;width:180px;height:58px;border:2px solid {PALETTE['line']};background:white;border-radius:14px;padding:14px;font-size:19px}}.branch.left{{left:16px}}.branch.right{{right:16px;height:78px;top:118px}}.branch i,.check i{{font-style:normal;color:white;background:{PALETTE['orange']};border-radius:50%;display:inline-grid;place-items:center;width:25px;height:25px;margin-right:7px}}.branch small{{display:block;color:{PALETTE['muted']};font-size:14px;margin:6px 0 0 34px}}.checks{{display:grid;gap:12px;padding-top:2px}}.check{{height:49px;border:2px solid {PALETTE['line']};border-radius:14px;background:white;padding:10px 15px;font-size:20px}}.hub{{left:160px;width:130px}}.network{{top:36px;height:120px}}.companies{{position:absolute;left:4px;right:4px;bottom:3px;display:flex;justify-content:space-between}}.companies span{{width:135px;padding:12px 7px;border:2px solid {PALETTE['line']};background:white;border-radius:13px;text-align:center;font-size:17px}}.companies .focus{{border-color:{PALETTE['orange']};background:#FFF3E9}}.rule{{position:absolute;left:34px;right:34px;bottom:39px;height:1px;background:{PALETTE['line']}}footer{{position:absolute;right:34px;bottom:16px;color:{PALETTE['muted']};font-size:13px;letter-spacing:1px}}
</style><script src="assets/gsap.min.js"></script><script>
const card=document.querySelector('.card'), head=document.querySelector('header'), items=document.querySelectorAll('.node,.branch,.check,.hub,.companies span'), wires=document.querySelectorAll('.wires path'), arrows=document.querySelectorAll('.arrow');
const tl=gsap.timeline({{paused:true}});tl.fromTo(card,{{x:-46,opacity:0,scale:.96}},{{x:0,opacity:1,scale:1,duration:.48,ease:'power3.out'}},0).fromTo(head,{{y:14,opacity:0}},{{y:0,opacity:1,duration:.38}},.14).fromTo(items,{{y:18,opacity:0,scale:.93}},{{y:0,opacity:1,scale:1,duration:.42,stagger:.13,ease:'back.out(1.4)'}},.48).fromTo(arrows,{{opacity:0,x:-8}},{{opacity:1,x:0,duration:.25,stagger:.16}},.75);
wires.forEach(p=>{{const L=p.getTotalLength();gsap.set(p,{{strokeDasharray:L,strokeDashoffset:L}});tl.to(p,{{strokeDashoffset:0,duration:.7,ease:'power2.inOut'}},.55)}});tl.to(card,{{x:-24,opacity:0,duration:.42,ease:'power2.in'}},{dur-.45});window.__timelines['{ident}']=tl;
</script></body></html>'''
    replacements = {
        "{ident}": ident, "{dur}": str(dur), "{dur-.45}": str(dur-.45),
        "{e['title']}": e['title'], "{diagram(e)}": diagram(e),
        "{PALETTE['navy']}": PALETTE['navy'], "{PALETTE['orange']}": PALETTE['orange'],
        "{PALETTE['paper']}": PALETTE['paper'], "{PALETTE['muted']}": PALETTE['muted'],
        "{PALETTE['line']}": PALETTE['line'],
    }
    for key, value in replacements.items(): template = template.replace(key, value)
    return template.replace('{{', '{').replace('}}', '}')

def main():
    GRAPHICS.mkdir(parents=True,exist_ok=True)
    assets = GRAPHICS / "assets"
    assets.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT.parent / "20260911_175145-polish-v5" / "assets" / "gsap.min.js", assets / "gsap.min.js")
    for e in EVENTS:
        d=GRAPHICS/e['id']; d.mkdir(parents=True,exist_ok=True)
        (d/'assets').mkdir(exist_ok=True); (d/'fonts').mkdir(exist_ok=True)
        shutil.copy2(assets/'gsap.min.js', d/'assets'/'gsap.min.js')
        shutil.copy2(ROOT.parent.parent / 'auto_editor' / 'assets' / 'fonts' / 'Pretendard-SemiBold.ttf', d/'fonts'/'Pretendard-SemiBold.ttf')
        (d/'index.html').write_text(html(e),encoding='utf-8')
    (ROOT/'graphic-events-source.json').write_text(json.dumps({"coordinate_contract":{"canvas":[1920,1080],"card":{"x":150,"y":330,"max_width":520,"max_height":390},"source_crop":[72,46,1680,984],"source_placement":[115,0],"caption_bottom":1000},"events":EVENTS},ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

if __name__ == '__main__': main()
