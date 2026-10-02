#!/usr/bin/env python3
"""Reference contracts are necessary; actual MP4 comparison remains mandatory."""
from pathlib import Path
import argparse,ast,json,re,hashlib
p=argparse.ArgumentParser();p.add_argument('project',type=Path);a=p.parse_args();r=a.project.resolve();base=r.parent/'ep06-v4';s=(r/'build.py').read_text();ref=(base/'build.py').read_text();t=json.loads((r/'timing.json').read_text());e=json.loads((r/'events.json').read_text());dur=json.loads((r/'cuts.json').read_text())['duration']
def literal(text,name):
 for n in ast.parse(text).body:
  if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets):return ast.literal_eval(n.value)
def refcall(name,index):
 for n in ast.walk(ast.parse(ref)):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='add' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value==name:return ast.literal_eval(n.args[index])
checks={
 'reference_comment_body':literal(s,'COMMENT_BODY')==refcall('s20-comment',3),
 'reference_comment_css':literal(s,'COMMENT_CSS')==refcall('s20-comment',4),
 'reference_comment_motion':literal(s,'COMMENT_JS')==refcall('s20-comment',5),
 'reference_badge_css':literal(s,'BADGE_CSS')==refcall('s02-security',4),
 'reference_badge_motion':literal(s,'BADGE_JS')==refcall('s02-security',5),
 'reference_hook_css':literal(s,'HOOK_CSS')==refcall('s01-hook',4),
 'reference_drift':"z*1.035" in s,
 'native_comment_used':'s99-comment' in t['scenes'],
 'has_camera_audio':any(x['scene']=='main' for x in e['actions']),
}
cam=t['camera'];sc=t['scenes'];full_graphics=sum((cam[i+1][0] if i+1<len(cam) else dur)-x for i,(x,m,*_) in enumerate(cam) if m=='hide');inside=[x for x in cam if not any(abs(x[0]-z[0])<.002 for z in sc.values())];gaps=[round(sc[b][0]-sc[c][0]-sc[c][1],3) for c,b in zip(sc,list(sc)[1:]) if abs(sc[b][0]-sc[c][0]-sc[c][1])>.035]
card_seconds=sum((cam[i+1][0] if i+1<len(cam) else dur)-x for i,(x,m,*_) in enumerate(cam) if m=='card')
checks.update(three_way_layout=card_seconds>=dur*.25 and full_graphics<=dur*.45,graphics_have_room=full_graphics>=dur*.18,emphasis_camera_inside_scenes=len(inside)>=2,no_composition_gaps=not gaps)
report={'checks':checks,'graphic_seconds':round(full_graphics,3),'intrascene_camera_keys':len(inside),'scene_gaps':gaps,'scenes':len(sc),'duration':dur,'mean_scene_seconds':round(dur/len(sc),3),'cues':len(e['actions']),'reference_build_sha256':hashlib.sha256(ref.encode()).hexdigest(),'scope':'Code fidelity and timing guard only. Does not establish visual fidelity without actual MP4 side-by-side review.'}
(r/'qc/reference-contract.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert all(checks.values()),report
