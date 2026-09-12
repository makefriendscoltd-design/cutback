import pathlib,json,shutil
r=pathlib.Path(__file__).resolve().parent;v5=r.parent/'20260911_175145-polish-v5'
for name in ['photos','Pretendard-Bold.ttf','gsap.min.js','soft-pop.wav','timeline-base.mp4']:
 p=r/'assets'/name
 if not p.exists():p.symlink_to((v5/'assets'/name).resolve())
for name in ['captions.json','captions.srt','timeline.json','camera-keyframes.json','relight.json']:
 shutil.copy2(v5/name,r/name)
keep={'opening-study':-5.2,'opening-work':4.3,'renovation':6.1,'cafe':-3.8,'design':-6.4,'blog':3.3,'meeting':-4.7,'together':5.6}
events=[]
for e in json.loads((v5/'events.json').read_text()):
 if e['id'] not in keep:continue
 e.update(type='photo',rotation=keep[e['id']],width=740,height=680,x=-15 if e['side']=='L' else 1195,y=145)
 events.append(e);c=r/'cards'/e['id'];c.mkdir(exist_ok=True)
 for target,src in [('photo.jpg',r/'assets/photos'/e['file']),('font.ttf',r/'assets/Pretendard-Bold.ttf'),('gsap.min.js',r/'assets/gsap.min.js')]:
  p=c/target
  if not p.exists():p.symlink_to(src)
 d=e['duration'];a=e['rotation'];sgn=1 if a>0 else -1
 doc=f'''<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:transparent}}#root{{position:relative;width:740px;height:680px}}.photo{{position:absolute;left:55px;top:65px;width:620px;height:500px;border:5px solid white;border-radius:3px;box-shadow:0 10px 18px #0006;transform-origin:center}}img{{display:block;width:620px;height:500px;object-fit:cover}}</style></head><body><div id="root" data-composition-id="card" data-duration="{d}" data-width="740" data-height="680" data-fps="30"><div class="photo"><img src="photo.jpg"></div></div><script src="gsap.min.js"></script><script>const tl=gsap.timeline({{paused:true}});tl.fromTo('.photo',{{scale:.93,x:{sgn*18},y:18,rotation:{a-sgn*2}}},{{scale:1,x:0,y:0,rotation:{a},duration:.32,ease:'power3.out'}},0);tl.fromTo('.photo',{{opacity:0}},{{opacity:1,duration:.12}},0);tl.to('.photo',{{rotation:{a+sgn*.7},y:-5,duration:{d-.60},ease:'sine.inOut'}},.32);tl.to('.photo',{{opacity:0,y:9,scale:.98,duration:.22,ease:'power2.in'}},{d-.22});window.__timelines={{card:tl}};</script></body></html>'''
 (c/'index.html').write_text(doc)
assert len({e['file'] for e in events})==len(events)==8
(r/'photo-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
(r/'BRIEF.md').write_text('workflow: general-video\nflow: automation\nstoryboard: no\n\nV6: eight unique photos without visible credit strips; individually frozen photo tilts 3.3–6.4 degrees and gentle drift. Eight explanatory motion graphics synchronized to existing semantic subtitles. Preserve v5 timeline, promo, voice, captions, camera and relighting. Use source captions for graphic labels; add no new factual claims. events.json is the assembled event source; photo-events.json and motion-events.json are editable authoring inputs.\n')
print('8 unique photo compositions authored')
