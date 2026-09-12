import pathlib,json,html,shutil,math,random,wave,array
r=pathlib.Path(__file__).resolve().parent
D=209.826483
rows=[('opening-study',0.12,4.10,'L','06-learning-workshop.jpg'),('opening-work',4.35,9.60,'R','05-coding.jpg'),('renovation',26.95,31.35,'L','01-renovation.jpg'),('cafe',31.8,39.14,'R','02-cozy-cafe.jpg'),('design',54.25,59.0,'L','03-logo-design.jpg'),('blog',59.5,64.45,'R','04-blogging-laptop.jpg'),('coding',80.4,87.7,'L','05-coding.jpg'),('learning',92.95,95.9,'R','06-learning-workshop.jpg'),('automation',125.7,131.8,'L','05-coding.jpg'),('meeting',139.2,147.95,'R','07-teamwork-meeting.jpg'),('cafe-recall',157.7,163.1,'L','02-cozy-cafe.jpg'),('together',178.9,184.9,'R','08-team-hands.jpg')]
events=[dict(id=id,start=a,end=b,duration=b-a,side=side,file=f,x=0 if side=='L' else 1240,y=170) for id,a,b,side,f in rows]
(r/'events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
# Original audio accent: seeded filtered noise plus decaying chirp; no sampled third-party audio.
sr=48000;n=int(sr*.32);rng=random.Random(175145);smooth=0;buf=[]
for i in range(n):
 t=i/sr;noise=rng.uniform(-1,1);smooth=.84*smooth+.16*noise
 air=(noise-smooth)*math.sin(math.pi*min(1,t/.25))**2*math.exp(-t*8)*.13 if t<.25 else 0
 u=max(0,t-.07);pop=math.sin(2*math.pi*(440*u-500*u*u))*math.exp(-u*38)*(1-math.exp(-u*350))*.72 if t>=.07 else 0
 buf.append(int(max(-1,min(1,air+pop))*32767))
with wave.open(str(r/'assets/soft-pop.wav'),'w') as f:f.setparams((1,2,sr,0,'NONE','not compressed'));f.writeframes(array.array('h',buf).tobytes())
(r/'assets/sfx-license.json').write_text(json.dumps({'asset':'soft-pop.wav','source':'Original procedural synthesis in build_visuals.py; seeded noise and sine chirp; no third-party samples','use':'unrestricted as part of this video','gain':0.95},indent=2))
fontcss="@font-face{font-family:Pretendard;src:url('assets/Pretendard-Bold.ttf')}"
for e in events:
 c=r/'cards'/e['id'];c.mkdir(parents=True,exist_ok=True)
 for target,source in [('photo.jpg',r/'assets/photos'/e['file']),('gsap.min.js',r/'assets/gsap.min.js'),('font.ttf',r/'assets/Pretendard-Bold.ttf')]:
  p=c/target
  if not p.exists():p.symlink_to(source)
 d=e['duration'];sgn=-1 if e['side']=='L' else 1
 # Hands-only crop for teamwork image to avoid implying endorsement by visible people.
 pos='center'
 cardh=500
 content=f'''<!doctype html><html><head><style>@font-face{{font-family:Pretendard;src:url('font.ttf')}}html,body{{margin:0;background:transparent}}#root{{position:relative;width:680px;height:620px}}.photo{{position:absolute;left:24px;top:28px;width:620px;height:{cardh+36}px;background:white;border:5px solid white;box-shadow:0 10px 22px #0005;transform-origin:center}}img{{display:block;width:620px;height:{cardh}px;object-fit:cover;object-position:{pos}}}.credit{{height:36px;display:flex;align-items:center;justify-content:center;font:19px Pretendard;color:#555;letter-spacing:.3px}}</style></head><body><div id="root" data-composition-id="card" data-duration="{d}" data-width="680" data-height="620" data-fps="30"><div class="photo"><img src="photo.jpg"><div class="credit">자료 이미지 · Pexels</div></div></div><script src="gsap.min.js"></script><script>const tl=gsap.timeline({{paused:true}});tl.fromTo('.photo',{{scale:.92,x:{sgn*20},y:10}},{{scale:1,x:0,y:0,duration:.25,ease:'back.out(1.25)'}},0);tl.fromTo('.photo',{{opacity:0}},{{opacity:1,duration:.10,ease:'power2.out'}},0);tl.to('.photo',{{opacity:0,x:{sgn*14},y:4,scale:.97,duration:.18,ease:'power2.in'}},{d-.18});window.__timelines={{card:tl}};</script></body></html>'''
 (c/'index.html').write_text(content)
# Main timeline uses rendered HyperFrames alpha-card assets, the enhanced original, and semantic captions.
def generate_main():
 caps=json.loads((r/'captions.json').read_text());els=[]
 els.append(f'<video id="presenter" src="assets/presenter-sharp.mp4" data-start="0" data-duration="{D}" data-media-start="0" data-track-index="0" muted playsinline style="position:absolute;inset:0;width:1920px;height:1080px;object-fit:contain"></video>')
 els.append(f'<audio id="voice" src="assets/presenter-sharp.mp4" data-start="0" data-duration="{D}" data-track-index="1" data-volume="0.891250938"></audio>')
 for e in events:
  els.append(f'<video id="card-{e["id"]}" class="clip" src="renders/{e["id"]}.webm" data-start="{e["start"]}" data-duration="{e["duration"]}" data-track-index="2" muted playsinline style="position:absolute;left:{e["x"]}px;top:{e["y"]}px;width:680px;height:620px"></video>')
  els.append(f'<audio id="sfx-{e["id"]}" src="assets/soft-pop.wav" data-start="{e["start"]}" data-duration=".32" data-track-index="3" data-volume=".95"></audio>')
 for i,c in enumerate(caps):
  lines=''.join('<div>'+html.escape(line)+'</div>' for line in c['lines'])
  els.append(f'<div class="clip subtitle" id="caption-{i}" data-start="{c["start"]}" data-duration="{c["end"]-c["start"]}" data-track-index="4">{lines}</div>')
 css=fontcss+'html,body{margin:0;background:#000}.subtitle{position:absolute;left:140px;right:140px;bottom:58px;text-align:center;font-family:Pretendard;font-weight:700;font-size:62px;line-height:1.28;color:white;-webkit-text-stroke:3px #000;paint-order:stroke fill;text-shadow:0 3px 5px #000b}.subtitle div{display:table;margin:0 auto;padding:1px 12px;white-space:nowrap}'
 (r/'index.html').write_text('<!doctype html><html><head><style>'+css+'</style></head><body>'+f'<div data-composition-id="polish" data-duration="{D}" data-width="1920" data-height="1080" data-fps="60000/1001" style="width:1920px;height:1080px;position:relative">'+''.join(els)+'</div><script src="assets/gsap.min.js"></script><script>window.__timelines={polish:gsap.timeline({paused:true})};</script></body></html>')
if (r/'captions.json').exists():generate_main()
print('generated',len(events),'photo events')
