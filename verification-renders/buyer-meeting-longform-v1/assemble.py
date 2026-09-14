from pathlib import Path
import json,subprocess,sys,html,shutil
r=Path(__file__).resolve().parent;plan=json.loads((r/'edit-plan.json').read_text());raw=json.loads((r/'graphic-events-source.json').read_text())['events'];duration=plan['duration']
def tm(t):
 for c in plan['clips']:
  if c['source_start']<=t<=c['source_end']:return c['start']+t-c['source_start']
  if t<c['source_start']:return c['start']
 return duration
events=[]
for e in raw:
 x=dict(e);x['start']=round(tm(e['source_start']),3);x['end']=round(min(duration,x['start']+e['duration']),3);x['overlay_y']=-160 if e['id'].startswith('01-') else 0;x['file']=str(r/'renders-graphics'/f'{e["id"]}.mov');events.append(x)
(r/'graphic-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
a=r/'assets';shutil.copy2(r.parent/'20260911_175145-polish-v5/assets/soft-pop.wav',a/'soft-pop.wav')
# Preserve full slide and large lecturer cutout; omit the duplicate tiny meeting tile.
# Remove the unrelated English template placeholder on the opening slide only.
vf="crop=1680:984:72:46,scale=1690:990:flags=lanczos,unsharp=3:3:0.22:3:3:0,pad=1920:1080:115:0:color=0x20252c,drawbox=x=150:y=722:w=1390:h=55:color=0xffc000:t=fill:enable='lt(t,6.8)'"
filters=[f'[0:v]{vf}[v0]'];cmd=['ffmpeg','-y','-hide_banner','-i',str(r/'cut-base.mp4')]
for i,e in enumerate(events,1):
 cmd+=['-i',e['file']];filters += [f'[{i}:v]setpts=PTS-STARTPTS+{e["start"]}/TB[g{i}]',f'[v{i-1}][g{i}]overlay=0:{e["overlay_y"]}:eof_action=pass:repeatlast=0:enable=\'between(t,{e["start"]},{e["end"]})\'[v{i}]']
cmd+=['-i',str(a/'soft-pop.wav')];si=len(events)+1
filters.append(f'[v{len(events)}]subtitles={r/"captions.ass"}:fontsdir={a}[v]')
filters.append('[0:a]acompressor=threshold=0.12:ratio=2:attack=10:release=100:makeup=1.5[voice]')
filters.append(f'[{si}:a]asplit={len(events)}'+''.join(f'[s{i}]' for i in range(len(events))))
for i,e in enumerate(events):filters.append(f'[s{i}]volume=0.2,adelay={round(e["start"]*1000)}:all=1[sfx{i}]')
filters.append('[voice]'+''.join(f'[sfx{i}]' for i in range(len(events)))+f'amix=inputs={len(events)+1}:normalize=0:duration=first,alimiter=limit=0.89:level=0[a]')
(r/'final-filter.txt').write_text(';\n'.join(filters))
preview='--preview' in sys.argv;out=r/'qa/preview-15s.mp4' if preview else Path('/Users/apple/Downloads/바이어_온라인_오프라인_미팅_롱폼_편집_v1.mp4')
cmd+=['-filter_complex_script',str(r/'final-filter.txt'),'-map','[v]','-map','[a]','-t',str(15 if preview else duration),'-c:v','h264_videotoolbox','-b:v','7M','-pix_fmt','yuv420p','-r','25','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True);print('OUTPUT',out,flush=True)
# Editable HyperFrames composition mirrors final crop, caption style, timing and overlays.
shutil.copy2(r.parent/'20260911_175145-polish-v5/assets/gsap.min.js',a/'gsap.min.js')
style=json.loads((r/'caption-style.json').read_text());caps=json.loads((r/'captions.json').read_text())
base=f'<div style="position:absolute;left:115px;top:0;width:1690px;height:990px;overflow:hidden"><video id="lecture" src="cut-base.mp4" data-start="0" data-duration="{duration}" muted playsinline style="position:absolute;width:1931.429px;height:1086.585px;left:-72.429px;top:-46.28px"></video></div><audio id="voice" src="cut-base.mp4" data-start="0" data-duration="{duration}" data-volume="1"></audio>'
base+='<div class="clip" data-start="0" data-duration="6.8" style="position:absolute;left:150px;top:722px;width:1390px;height:55px;background:#ffc000"></div>'
for e in events:
 webm=f'renders-graphics/{e["id"]}.webm';base+=f'<video id="g-{e["id"]}" class="clip" src="{webm}" data-start="{e["start"]}" data-duration="{e["duration"]}" muted playsinline style="position:absolute;left:0;top:{e["overlay_y"]}px;width:1920px;height:1080px"></video>'
for i,c in enumerate(caps):base+=f'<div class="clip caption" data-start="{c["start"]}" data-duration="{c["end"]-c["start"]}"><span>{html.escape(c["text"])}</span></div>'
doc=f'''<!doctype html><html><head><meta charset="utf-8"><style>@font-face{{font-family:PS;src:url('assets/Pretendard-SemiBold.ttf')}}html,body{{margin:0;background:#20252c}}.caption{{position:absolute;bottom:22px;left:0;width:1920px;text-align:center;color:white;font:30px PS;line-height:1.2}}.caption span{{display:inline-block;background:rgba(0,0,0,.68);padding:8px;white-space:nowrap}}</style></head><body><div data-composition-id="buyer" data-width="1920" data-height="1080" data-duration="{duration}" data-fps="25" style="position:relative;width:1920px;height:1080px;overflow:hidden">{base}</div><script src="assets/gsap.min.js"></script><script>window.__timelines={{buyer:gsap.timeline({{paused:true}})}};</script></body></html>'''
(r/'index.html').write_text(doc)
