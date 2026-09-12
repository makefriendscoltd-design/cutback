import pathlib,json,html
r=pathlib.Path(__file__).resolve().parent;v5=r.parent/'20260911_175145-polish-v5'
es=json.loads((r/'photo-events.json').read_text())+json.loads((r/'motion-events-refined.json').read_text());es.sort(key=lambda e:e['start'])
for i,e in enumerate(es):
 assert e['end']<=21.738383 or e['start']>=71.438033
 assert e['start']<e['end']
 if i:assert es[i-1]['end']<=e['start'],(es[i-1]['id'],e['id'])
 e['sfx_gain']=.95 if e['type']=='photo' else .65
(r/'events.json').write_text(json.dumps(es,ensure_ascii=False,indent=2))
s=(v5/'assemble.py').read_text().replace('20260911_175145_홍보삽입_줌_재조명_v5.mp4','20260911_175145_모션그래픽_사진개선_v6.mp4').replace('volume=0.95,adelay=','volume={e["sfx_gain"]},adelay=')
s=s.replace("r/'renders'","r/'renders-refined'")
(r/'assemble.py').write_text(s)
D=json.loads((r/'timeline.json').read_text())['duration'];els=[f'<video id="presenter" src="assets/timeline-base.mp4" data-start="0" data-duration="{D}" data-track-index="0" muted playsinline style="position:absolute;inset:0;width:1920px;height:1080px"></video>',f'<audio id="voice" src="assets/timeline-base.mp4" data-start="0" data-duration="{D}" data-track-index="1" data-volume=".891250938"></audio>']
for e in es:
 els.append(f'<video id="overlay-{e["id"]}" src="renders-refined/{e["id"]}.webm" data-start="{e["start"]}" data-duration="{e["duration"]}" data-track-index="2" muted playsinline style="position:absolute;left:{e["x"]}px;top:{e["y"]}px;width:{e["width"]}px;height:{e["height"]}px"></video>')
 els.append(f'<audio id="sfx-{e["id"]}" src="assets/soft-pop.wav" data-start="{e["start"]}" data-duration=".32" data-track-index="3" data-volume="{e["sfx_gain"]}"></audio>')
for i,c in enumerate(json.loads((r/'captions.json').read_text())):
 els.append(f'<div class="clip caption" id="caption-{i}" data-start="{c["start"]}" data-duration="{c["end"]-c["start"]}" data-track-index="4">{html.escape(c["text"])}</div>')
css="@font-face{font-family:Pretendard;src:url('assets/Pretendard-Bold.ttf')}html,body{margin:0;background:black}.caption{position:absolute;bottom:58px;left:100px;right:100px;text-align:center;font:700 62px Pretendard;white-space:nowrap;color:white;-webkit-text-stroke:3px black;paint-order:stroke fill;text-shadow:0 3px 4px #000a}"
(r/'index.html').write_text('<!doctype html><html><head><meta charset="utf-8"><style>'+css+'</style></head><body>'+f'<div data-composition-id="final" data-duration="{D}" data-width="1920" data-height="1080" data-fps="60000/1001" style="width:1920px;height:1080px;position:relative;overflow:hidden">'+''.join(els)+'</div><script src="assets/gsap.min.js"></script><script>window.__timelines={final:gsap.timeline({paused:true})};</script></body></html>')
print('assembled editable events',len(es))
