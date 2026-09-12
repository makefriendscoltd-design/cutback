#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("draft_motion", ROOT / "build_motion.py")
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
BASE_CARDS = base.cards
MOTION = ROOT / "motion-refined"

BEATS = {
 "problem-flow":[2.52,3.40,4.84], "learning-loop":[0.0,3.50,7.0],
 "automation":[0.25,1.30,2.35], "overload":[0.0,6.02,10.34],
 "school-path":[4.32,6.30,7.30], "records":[0.0,2.40,4.60,6.20],
 "outcome":[3.04,5.12,10.86], "tracks":[0.0,4.14,9.46]
}

def refined_cards(scene):
    sid=scene['id']; labels=scene['labels']
    if sid in ('overload','records','tracks'):
        return BASE_CARDS(scene)
    if sid == 'learning-loop':
        return '''<div class="loopstage"><div class="card node n0" id="c0" data-layout-allow-occlusion><span class="ico">▶</span>영상</div><div class="card node n1" id="c1"><span class="ico">↗</span>따라 하기</div><div class="card node n2" id="c2"><span class="ico">◆</span>만들기</div><svg class="looppath" viewBox="0 0 500 390"><path id="loopline" d="M250 78 C430 78 430 305 250 305 C70 305 70 78 250 78"/></svg><div class="runner" id="runner" data-layout-allow-occlusion></div></div>'''
    nodes=[]
    icons=['?','✓','◆']
    for i,label in enumerate(labels):
        nodes.append(f'<div class="card vcard v{i}" id="c{i}"><span class="ico">{icons[i]}</span>{label}</div>')
        if i<len(labels)-1: nodes.append(f'<svg class="down d{i}" viewBox="0 0 60 76"><path d="M30 2 V61 M18 49 L30 62 L42 49"/></svg>')
    return '<div class="vflow">'+''.join(nodes)+'</div>'

def script_for(scene,duration):
    sid=scene['id']; b=BEATS[sid]
    head=f"const DURATION={duration}; const tl=gsap.timeline({{paused:true}});\ntl.fromTo('#panel',{{autoAlpha:0,scale:.97}},{{autoAlpha:1,scale:1,duration:.25,ease:'power3.out'}},0);\n"
    if sid in ('problem-flow','school-path','outcome','automation'):
        body="const cards=gsap.utils.toArray('.vcard'); const paths=gsap.utils.toArray('.down path');tl.set(cards.slice(1),{autoAlpha:0},0);tl.set(paths,{opacity:0},0);\n"
        body+="tl.fromTo(cards[0],{autoAlpha:0,y:20},{autoAlpha:.42,y:0,duration:.25,ease:'power3.out'},.25);\n"
        for i,t in enumerate(b):
            if i==0:
                body+=f"tl.to(cards[0],{{autoAlpha:1,backgroundColor:'#eaf1ff',duration:.28,ease:'power2.out'}},{t});\n"
            else:
                body+=f"tl.fromTo(cards[{i}],{{autoAlpha:0,y:28}},{{autoAlpha:1,y:0,duration:.25,ease:'power3.out',immediateRender:false}},{t});\n"
            if i:
                body+=f"{{const p=paths[{i-1}],len=p.getTotalLength();tl.fromTo(p,{{opacity:0,strokeDasharray:len,strokeDashoffset:len}},{{opacity:1,strokeDashoffset:0,duration:.48,ease:'power2.out',immediateRender:false}},{max(0,t-.46):.2f});}}\n"
        body+=f"tl.to(cards[2],{{backgroundColor:'#3564b6',color:'#fff',scale:1.04,duration:.32,ease:'back.out(1.7)'}},{min(duration-.8,b[-1]+.45):.2f});\n"
    elif sid=='records':
        body="""tl.set(['#c0','#c1','#c2','#c3','.merge'],{autoAlpha:0},0);
 tl.fromTo('.source',{autoAlpha:0,y:15},{autoAlpha:1,y:0,duration:.25,stagger:.3,immediateRender:false},.25)
 .fromTo('.merge',{autoAlpha:0},{autoAlpha:1,duration:.2,immediateRender:false},.65)
 .to('#c0',{x:140,y:155,autoAlpha:0,duration:.6,ease:'power2.inOut'},1.9)
 .to('#c1',{x:-140,y:155,autoAlpha:0,duration:.6,ease:'power2.inOut'},1.9)
 .to('.merge',{autoAlpha:0,duration:.25},2)
 .fromTo('#c2',{autoAlpha:0,scale:.82},{autoAlpha:1,scale:1,duration:.35,ease:'power3.out',immediateRender:false},2.4)
 .fromTo('#c3',{autoAlpha:0,y:25},{autoAlpha:1,y:0,duration:.35,ease:'power3.out',immediateRender:false},4.6)
 .to('#c3',{backgroundColor:'#3564b6',color:'#fff',duration:.3},5);"""
    elif sid=='learning-loop':
        body=f'''const path=document.querySelector('#loopline'); const len=path.getTotalLength();tl.set(['#c1','#c2','#runner'],{{autoAlpha:0}},0);
tl.fromTo('#c0',{{autoAlpha:0,y:22}},{{autoAlpha:1,y:0,duration:.25,ease:'power3.out'}},0)
 .fromTo('#loopline',{{strokeDasharray:len,strokeDashoffset:len}},{{strokeDashoffset:0,duration:.7,ease:'power2.out'}},.35)
 .fromTo('#c1',{{autoAlpha:0,y:22}},{{autoAlpha:1,y:0,duration:.25,ease:'power3.out',immediateRender:false}},3.5)
 .fromTo('#runner',{{autoAlpha:0}},{{autoAlpha:1,duration:.15,immediateRender:false}},3.5)
 .to('#runner',{{motionPath:{{path:'#loopline',align:'#loopline',alignOrigin:[.5,.5]}},duration:1.55,ease:'none'}},3.55)
 .to('#runner',{{motionPath:{{path:'#loopline',align:'#loopline',alignOrigin:[.5,.5]}},duration:1.55,ease:'none'}},5.15)
 .fromTo('#c2',{{autoAlpha:0,scale:.82}},{{autoAlpha:1,scale:1,duration:.32,ease:'back.out(1.8)',immediateRender:false}},7.0)
 .to('#c2',{{backgroundColor:'#3564b6',color:'#fff',duration:.3}},7.35);'''
        # Avoid MotionPathPlugin dependency: replace the two path travels with deterministic rectangular legs.
        cycle=".fromTo('#runner',{x:0,y:0},{x:185,y:112,duration:.4375,ease:'none',immediateRender:false},3.5).to('#runner',{x:0,y:225,duration:.4375,ease:'none'}).to('#runner',{x:-185,y:112,duration:.4375,ease:'none'}).to('#runner',{x:0,y:0,duration:.4375,ease:'none'}).to('#runner',{x:185,y:112,duration:.4375,ease:'none'}).to('#runner',{x:0,y:225,duration:.4375,ease:'none'}).to('#runner',{x:-185,y:112,duration:.4375,ease:'none'}).to('#runner',{x:0,y:0,duration:.4375,ease:'none'})"
        first=body.index(".to('#runner',{motionPath")
        end=body.index("\n .fromTo('#c2'", first)
        body=body[:first]+cycle+body[end:]
    elif sid=='overload':
        body="""tl.set(['#question','#result'],{autoAlpha:0},0);tl.fromTo('.mini',{autoAlpha:0,y:-28,rotation:-5},{autoAlpha:1,y:0,rotation:0,duration:.25,stagger:.55,ease:'power3.out'},.25)
 .to('#pile',{scale:.88,y:-78,duration:.5,ease:'power2.inOut'},5.50)
 .fromTo('#question',{autoAlpha:0,scale:.82},{autoAlpha:1,scale:1,duration:.34,ease:'back.out(1.8)',immediateRender:false},6.02)
 .to('.mini',{opacity:.25,duration:.3},10.05)
 .fromTo('#result',{autoAlpha:0,y:28},{autoAlpha:1,y:0,duration:.3,ease:'power3.out',immediateRender:false},10.34)
 .to('#result',{backgroundColor:'#3564b6',color:'#ffffff',scale:1.06,duration:.34,ease:'power2.out'},11.15);"""
    else:
        # Preserve the already effective draft choreography for compact/pile/merge/track scenes.
        old=base.html(scene)
        body=old.split("tl.fromTo('#panel'",1)[1].split("tl.to('#panel'",1)[0]
        body="tl.fromTo('#panel'"+body
        body=body.split(";\n",1)[1] if ";\n" in body else body
    return head+body+f"\ntl.to('#panel',{{autoAlpha:0,duration:.22,ease:'power2.in'}},DURATION-.22);\nwindow.__timelines['{sid}']=tl; tl.seek(0);"

def refined_html(scene):
    original_cards=base.cards; base.cards=refined_cards
    page=base.html(scene); base.cards=original_cards
    sid=scene['id']; duration=round(scene['end']-scene['start'],2)
    page=page.replace('<div class="flow">',f'<div class="flow {sid}">',1)
    extra='''<style>
.vflow{height:470px;width:100%;display:grid;grid-template-rows:115px 62px 115px 62px 115px;justify-items:center;align-items:center}.vcard{width:400px;height:105px;font-size:42px;gap:18px}.ico{display:inline-flex;width:52px;height:52px;border-radius:14px;align-items:center;justify-content:center;background:#eaf1ff;color:#3564b6;font-size:32px}.down{width:60px;height:76px}.loopstage{position:relative;width:500px;height:390px}.loopstage .node{position:absolute;width:230px;height:92px;font-size:36px;gap:12px;z-index:2}.loopstage .n0{left:135px;top:22px}.loopstage .n1{left:0;top:250px}.loopstage .n2{right:0;top:250px}.looppath{position:absolute;inset:0;width:500px;height:390px}.looppath path{fill:none;stroke:#9bb6e5;stroke-width:5}.runner{position:absolute;left:245px;top:73px;width:18px;height:18px;border-radius:50%;background:#3564b6;box-shadow:0 0 0 8px rgba(53,100,182,.16);z-index:3}
.loopstage .node{width:240px;font-size:34px;gap:10px;padding:16px 12px;white-space:nowrap}.loopstage .n0{left:130px}
</style>'''
    if sid=='records':
        extra+='<style>.flow.records{position:relative;height:436px;display:block}.records .card{position:absolute;min-height:95px;padding:18px 14px;white-space:nowrap}.records #c0{left:0;top:20px;width:220px}.records #c1{right:0;top:20px;width:220px}.records .merge{position:absolute;left:240px;top:37px;font-size:42px}.records #c2{left:123px;top:175px;width:270px}.records #c3{left:88px;top:326px;width:340px}.records #c3:before{content:"↓";position:absolute;top:-55px;left:147px;color:#3564b6;font-size:42px}</style>'
    page=page.replace('</head>',extra+'</head>')
    prefix=page.split('<script>')[0]+'<script>\n'
    return prefix+script_for(scene,duration)+'\n</script></body></html>'

def main():
    MOTION.mkdir(parents=True,exist_ok=True); assets=MOTION/'assets'; assets.mkdir(exist_ok=True)
    for name in ('Pretendard-Bold.ttf','gsap.min.js'):
        link=assets/name
        if not link.exists(): link.symlink_to(Path('../../../20260911_175145-polish-v5/assets')/name)
    events=[]
    for s in base.SCENES:
        d=MOTION/s['id']; d.mkdir(exist_ok=True); ca=d/'assets'
        if not ca.exists(): ca.symlink_to(Path('../assets'))
        (d/'index.html').write_text(refined_html(s),encoding='utf-8')
        events.append({"id":s['id'],"start":s['start'],"end":s['end'],"duration":round(s['end']-s['start'],2),"side":s['side'],"x":0 if s['side']=='L' else 1240,"y":170,"width":680,"height":620,"type":"motion","source_caption_indices":s['indices'],"beats":BEATS[s['id']],"beat_description":s['beat']})
    (ROOT/'motion-events-refined.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
