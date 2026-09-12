import json,pathlib,subprocess
r=pathlib.Path(__file__).resolve().parent;old=r.parent/'20260911_175145-polish-v4'
a=r/'assets';a.mkdir(exist_ok=True)
for name in ['photos','Pretendard-Bold.ttf','gsap.min.js','soft-pop.wav']:
 p=a/name
 if not p.exists():p.symlink_to((old/'assets'/name).resolve())
src=(old/'assets/presenter-sharp.mp4').resolve();fps=60000/1001
poses=[(0,1),(10,1.025),(20,1.045),(22.4891333333333,1.045),(22.4891333333333,1),(32.4891333333333,1.045),(45,1.045),(55,1.075),(65,1.03),(80,1.03),(90,1.085),(100,1.045),(118,1.045),(128,1.075),(138,1.03),(160,1.03),(170,1.06),(180,1.09),(190,1.04),(209.826283333333,1.04)]
data={'subject':'presenter only; captions and side images fixed','anchor_normalized':[.495,.34],'ease':'sine.inOut','poses':[{'time':t,'scale':z} for t,z in poses],'source':str(src),'fps':fps,'zoom_range':[1,1.09],'reset_reason':'new shot following inserted promotional video'}
(r/'camera-keyframes.json').write_text(json.dumps(data,indent=2))
c=r/'camera-composition';c.mkdir(exist_ok=True)
for n,p in [('source.mp4',src),('gsap.min.js',a/'gsap.min.js')]:
 q=c/n
 if not q.exists():q.symlink_to(p)
js="const tl=gsap.timeline({paused:true});"
for (t,z),(t2,z2) in zip(poses,poses[1:]):
 if t2==t:js+=f"tl.set('#subject',{{scale:{z2}}},{t2});"
 elif z!=z2:js+=f"tl.fromTo('#subject',{{scale:{z}}},{{scale:{z2},duration:{t2-t},ease:'sine.inOut',immediateRender:false}},{t});"
js+="window.__timelines={camera:tl};"
(c/'index.html').write_text('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0}#root{width:1920px;height:1080px;overflow:hidden;position:relative}#subject{width:1920px;height:1080px;transform-origin:950.4px 367.2px}video{width:1920px;height:1080px}</style></head><body><div id="root" data-composition-id="camera" data-duration="209.826283333333" data-width="1920" data-height="1080"><div id="subject"><video id="source" src="source.mp4" data-start="0" data-duration="209.826283333333" data-track-index="0" muted playsinline></video></div></div><script src="gsap.min.js"></script><script>'+js+'</script></body></html>')
# Piecewise easing is generated from the same pose contract used by the GSAP timeline.
expr=str(poses[-1][1])
for (t,z),(t2,z2) in reversed(list(zip(poses,poses[1:]))):
 if t2==t:continue
 value=str(z) if z==z2 else f'({z}+({z2-z})*(1-cos(PI*clip((on/{fps}-{t})/{t2-t},0,1)))/2)'
 expr=f'if(lt(on/{fps},{t2}),{value},{expr})'
vf=f"scale=3840:2160:flags=bicubic,zoompan=z='{expr}':x='iw*.495-iw/zoom*.495':y='ih*.34-ih/zoom*.34':d=1:s=1920x1080:fps=60000/1001"
(r/'camera-filter.txt').write_text(vf)
cmd=['ffmpeg','-y','-hide_banner','-i',str(src),'-vf',vf,'-frames:v','12577','-c:v','h264_videotoolbox','-b:v','22M','-an','-movflags','+faststart',str(a/'presenter-camera.mp4')]
(r/'camera-command.json').write_text(json.dumps(cmd,indent=2))
with open(r/'camera-render.log','w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
print('camera render complete',flush=True)
