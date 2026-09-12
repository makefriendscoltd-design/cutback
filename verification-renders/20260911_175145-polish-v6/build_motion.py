#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MOTION = ROOT / "motion"

SCENES = [
    dict(id="problem-flow", start=10.12, end=18.50, side="L", indices=[3,4,5], labels=["문제 발견","직접 해결","결과"], beat="문제 카드가 들어오고 해결 카드와 연결된 뒤 결과 카드가 선택됩니다."),
    dict(id="learning-loop", start=122.15, end=131.89, side="L", indices=[31,32,33,34,35,36], labels=["영상","따라 하기","만들기"], beat="영상과 따라 하기 카드가 순환하고 만들기 카드로 조립됩니다."),
    dict(id="automation", start=132.25, end=136.85, side="R", indices=[37,38], labels=["반복하던 일","AI","자동화"], beat="반복 업무 카드가 AI 처리 단계를 지나 자동화 결과로 바뀝니다."),
    dict(id="overload", start=139.05, end=153.73, side="R", indices=[40,41,42,43,44,45,46], labels=["도구","강의","영상","어디서부터?","내 일"], beat="도구·강의·영상 카드가 쌓인 뒤 어디서부터 질문으로 정리되고 내 일이 선택됩니다."),
    dict(id="school-path", start=154.19, end=164.13, side="L", indices=[47,48,49,50,51], labels=["무엇을 할지","직접 만들기","내 일에 쓰기"], beat="무엇을 할지 정한 뒤 직접 만들고 내 일에 쓰는 경로가 이어집니다."),
    dict(id="records", start=173.25, end=180.95, side="L", indices=[56,57,58], labels=["경험","기록","AI 자료","직접 만들기"], beat="경험과 기록 카드가 합쳐져 AI 자료가 되고 직접 만들기로 연결됩니다."),
    dict(id="outcome", start=197.73, end=212.23, side="L", indices=[67,68,69,70,71,72], labels=["내 문제","AI 서비스","내 결과물"], beat="내 문제를 선택하고 AI 서비스로 연결해 내 결과물 카드를 완성합니다."),
    dict(id="tracks", start=212.81, end=227.25, side="R", indices=[73,74,75,76,77,78,79], labels=["취업 준비","결과물","일하는 분","도구","창업 준비","첫 서비스"], beat="세 대상 카드가 차례로 선택되며 각각 결과물·도구·첫 서비스와 연결됩니다.", beats=[0.0,4.14,9.46]),
]

def cards(scene):
    labels = scene["labels"]
    if scene["id"] == "overload":
        return '''<div class="pile" id="pile" data-layout-allow-occlusion><div class="mini">도구</div><div class="mini">강의</div><div class="mini">영상</div></div><div class="question" id="question">어디서부터?</div><div class="result" id="result">내 일</div>'''
    if scene["id"] == "records":
        return ''.join(f'<div class="card source" id="c{i}" data-layout-allow-occlusion>{x}</div>' for i,x in enumerate(labels[:2])) + '<div class="merge">＋</div>' + ''.join(f'<div class="card target" id="c{i+2}">{x}</div>' for i,x in enumerate(labels[2:]))
    if scene["id"] == "tracks":
        rows=[]
        for i in range(0,6,2): rows.append(f'<div class="trackrow" id="r{i//2}"><div class="card">{labels[i]}</div><svg viewBox="0 0 90 24"><path d="M2 12 H78 M70 4 L78 12 L70 20"/></svg><div class="card target">{labels[i+1]}</div></div>')
        return ''.join(rows)
    return ''.join(f'<div class="card" id="c{i}">{x}</div>' + (f'<svg class="arrow" id="a{i}" viewBox="0 0 90 34"><path d="M3 17 H76 M67 8 L76 17 L67 26"/></svg>' if i < len(labels)-1 else '') for i,x in enumerate(labels))

def html(scene):
    duration=round(scene['end']-scene['start'],2)
    sid=scene['id']
    tracks = sid == 'tracks'
    overload = sid == 'overload'
    records = sid == 'records'
    markup=cards(scene)
    if tracks:
        anim='''
  gsap.utils.toArray('.trackrow').forEach((row,i)=>{
    const t=[0,4.14,9.46][i]; const path=row.querySelector('path'); const len=path.getTotalLength();
    tl.fromTo(row,{autoAlpha:0,y:24},{autoAlpha:1,y:0,duration:.25,ease:'power3.out'},t+.25)
      .fromTo(path,{strokeDasharray:len,strokeDashoffset:len},{strokeDashoffset:0,duration:.62,ease:'power2.out'},t+.75)
      .fromTo(row.querySelector('.target'),{scale:.84,backgroundColor:'#ffffff'},{scale:1,backgroundColor:'#eaf1ff',duration:.34,ease:'back.out(1.8)'},t+1.3);
  });'''
    elif overload:
        anim='''
  tl.fromTo('.mini',{autoAlpha:0,y:-28,rotation:-5},{autoAlpha:1,y:0,rotation:0,duration:.25,stagger:.55,ease:'power3.out'},.25)
    .to('#pile',{scale:.88,y:-78,duration:.5,ease:'power2.inOut'},3.1)
    .fromTo('#question',{autoAlpha:0,scale:.82},{autoAlpha:1,scale:1,duration:.34,ease:'back.out(1.8)'},3.45)
    .to('.mini',{opacity:.25,duration:.3},6.2)
    .fromTo('#result',{autoAlpha:0,y:28},{autoAlpha:1,y:0,duration:.3,ease:'power3.out'},6.25)
    .to('#result',{backgroundColor:'#3564b6',color:'#ffffff',scale:1.06,duration:.34,ease:'power2.out'},8.0);'''
    elif records:
        anim='''
  tl.fromTo('.source',{autoAlpha:0,x:-36},{autoAlpha:1,x:0,duration:.25,stagger:.35,ease:'power3.out'},.25)
    .fromTo('.merge',{autoAlpha:0,scale:.4},{autoAlpha:1,scale:1,duration:.3,ease:'back.out(2)'},1.25)
    .to('#c0',{x:108,y:92,opacity:.2,duration:.55,ease:'power2.inOut'},2.0)
    .to('#c1',{x:-108,y:18,opacity:.2,duration:.55,ease:'power2.inOut'},2.0)
    .fromTo('#c2',{autoAlpha:0,scale:.78},{autoAlpha:1,scale:1,duration:.35,ease:'back.out(1.8)'},2.45)
    .fromTo('#c3',{autoAlpha:0,y:30},{autoAlpha:1,y:0,duration:.3,ease:'power3.out'},4.1)
    .to('#c3',{backgroundColor:'#3564b6',color:'#fff',duration:.3},4.75);'''
    else:
        anim='''
  const cards=gsap.utils.toArray('.card'); const arrows=gsap.utils.toArray('.arrow path');
  cards.forEach((card,i)=>tl.fromTo(card,{autoAlpha:0,y:28,scale:.92},{autoAlpha:1,y:0,scale:1,duration:.25,ease:'power3.out'},.25+i*1.05));
  arrows.forEach((path,i)=>{const len=path.getTotalLength();tl.fromTo(path,{strokeDasharray:len,strokeDashoffset:len},{strokeDashoffset:0,duration:.58,ease:'power2.out'},.88+i*1.05);});
  tl.to(cards[cards.length-1],{backgroundColor:'#3564b6',color:'#fff',scale:1.06,duration:.34,ease:'back.out(1.7)'},Math.min(DURATION-1.2,3.05));'''
    page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Pretendard;src:url('../assets/Pretendard-Bold.ttf')}}*{{box-sizing:border-box}}html,body{{margin:0;width:680px;height:620px;background:transparent;overflow:hidden}}body{{font-family:Pretendard,sans-serif;color:#15304d}}#root{{position:relative;width:680px;height:620px}}.panel{{position:absolute;left:35px;top:45px;width:600px;height:520px;border-radius:20px;background:rgba(255,255,255,.96);box-shadow:0 18px 46px rgba(21,48,77,.16);display:flex;align-items:center;justify-content:center;padding:42px;overflow:hidden}}.flow{{width:100%;display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap}}.card,.question,.result,.mini{{display:flex;align-items:center;justify-content:center;text-align:center;font-size:40px;line-height:1.14;letter-spacing:-.04em;background:#fff;border:3px solid #dce7f8;border-radius:18px;padding:22px 24px;min-width:150px;min-height:100px;box-shadow:0 10px 22px rgba(21,48,77,.10)}}.target{{border-color:#9bb6e5}}svg.arrow{{width:76px;height:34px}}svg path{{fill:none;stroke:#3564b6;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}.pile{{position:absolute;top:80px;width:410px;height:180px}}.mini{{position:absolute;width:250px;min-height:82px;left:80px;font-size:42px}}.mini:nth-child(1){{top:0;left:20px}}.mini:nth-child(2){{top:36px;left:80px}}.mini:nth-child(3){{top:72px;left:140px}}.question{{position:absolute;top:270px;font-size:46px}}.result{{position:absolute;top:390px;min-width:240px}}.source{{width:220px}}.merge{{font-size:48px;color:#3564b6}}.trackrow{{width:100%;display:grid;grid-template-columns:1fr 80px 1fr;align-items:center;gap:10px}}.trackrow .card{{font-size:34px;min-height:92px;padding:16px 10px}}.trackrow svg{{width:80px}}.flow:has(.trackrow){{gap:24px}} 
</style></head><body><div id="root" class="clip" data-composition-id="{sid}" data-width="680" data-height="620" data-duration="{duration}" data-fps="30"><div class="panel" id="panel"><div class="flow">{markup}</div></div></div><script src="../assets/gsap.min.js"></script><script>
const DURATION={duration}; const tl=gsap.timeline({{paused:true}});
tl.fromTo('#panel',{{autoAlpha:0,scale:.97}},{{autoAlpha:1,scale:1,duration:.25,ease:'power3.out'}},0);
{anim}
tl.to('#panel',{{autoAlpha:0,duration:.22,ease:'power2.in'}},DURATION-.22);
window.__timelines['{sid}']=tl; tl.seek(0);
</script></body></html>'''
    return page.replace("../assets/", "assets/")

def main():
    MOTION.mkdir(parents=True, exist_ok=True)
    assets=MOTION/'assets'; assets.mkdir(exist_ok=True)
    for name in ('Pretendard-Bold.ttf','gsap.min.js'):
        link=assets/name
        if not link.exists(): link.symlink_to(Path('../../../20260911_175145-polish-v5/assets')/name)
    events=[]
    for s in SCENES:
        d=MOTION/s['id']; d.mkdir(exist_ok=True)
        comp_assets=d/'assets'
        if not comp_assets.exists(): comp_assets.symlink_to(Path('../assets'))
        (d/'index.html').write_text(html(s),encoding='utf-8')
        events.append({"id":s['id'],"start":s['start'],"end":s['end'],"duration":round(s['end']-s['start'],2),"side":s['side'],"x":0 if s['side']=='L' else 1240,"y":170,"width":680,"height":620,"type":"motion","source_caption_indices":s['indices'],"beats":s.get('beats',[]),"beat_description":s['beat']})
    (ROOT/'motion-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__': main()
