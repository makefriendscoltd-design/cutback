#!/usr/bin/env python3
"""Check explicit camera placements against the user-approved episode 7 v3 rhythm.
Metrics are a guard against a mostly static template, not proof of visual quality.
"""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('project');a=p.parse_args();r=Path(a.project)
t=json.loads((r/'timing.json').read_text());duration=json.loads((r/'cuts.json').read_text())['duration'];camera=t['camera'];seconds={};transitions=[];full_beats=0
for i,(start,mode,zoom,tween) in enumerate(camera):
 end=camera[i+1][0] if i+1<len(camera) else duration
 assert end>start,(start,end)
 seconds[mode]=seconds.get(mode,0)+end-start
 if mode=='full' and (i==0 or camera[i-1][1]!='full'):full_beats+=1
 if i and mode!=camera[i-1][1]:transitions.append({'time':start,'from':camera[i-1][1],'to':mode,'duration':tween})
report={'duration':duration,'seconds':seconds,'full_beats':full_beats,'transitions':transitions,'full_fraction':seconds.get('full',0)/duration}
if duration>=25:
 assert full_beats>=3,'Need repeated full-presenter beats, not a fixed lower card'
 assert report['full_fraction']>=.25,'Full-presenter exposure below approved rhythm guard'
 assert len(transitions)>=6,'Too few layout changes for this duration'
(r/'qc').mkdir(exist_ok=True);(r/'qc/camera-contract.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='transitions'},ensure_ascii=False))
