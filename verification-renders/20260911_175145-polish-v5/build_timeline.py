import pathlib,json,subprocess,copy
r=pathlib.Path(__file__).resolve().parent;v4=r.parent/'20260911_175145-polish-v4';fps=60000/1001
cut=1303;resume=1348;promo_frames=2979;end=12577
pre=cut/fps;back=resume/fps;pd=promo_frames/fps;shift=(promo_frames-(resume-cut))/fps;total=(end+promo_frames-(resume-cut))/fps
promo='/Users/apple/orca/workspaces/family_pm/ai학교/aixschool-83s/renders/aixschool-83s_2026-09-11_11-30-44.mp4'
plan={'source_frames':end,'fps':fps,'intro_before_frame':cut,'intro_resume_source_frame':resume,'removed_breath_gap_seconds':back-pre,'promo_path':promo,'promo_frames_at_output_fps':promo_frames,'promo_start':pre,'promo_end':pre+pd,'downstream_shift':shift,'duration':total,'total_frames':end+promo_frames-(resume-cut),'reason':'insert existing HyperFrames promo after 이유입니다 and immediately before 안녕하세요'}
(r/'timeline.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
base=json.loads((r/'captions-base.json').read_text());caps=[]
for c in base:
 x=copy.deepcopy(c)
 if c['start']>=back:x['start']=round(x['start']+shift,6);x['end']=round(x['end']+shift,6)
 else:assert x['end']<=pre
 caps.append(x)
(r/'captions.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2))
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02d}:{n//60000%60:02d}:{n//1000%60:02d},{n%1000:03d}'
(r/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(caps))+'\n')
es=json.loads((v4/'events.json').read_text())
for e in es:
 if e['start']>=back:e['start']+=shift;e['end']+=shift
 else:assert e['end']<=pre
(r/'events.json').write_text(json.dumps(es,ensure_ascii=False,indent=2))
for name in ['renders']:
 p=r/name
 if not p.exists():p.symlink_to((v4/name).resolve())
# These are pixel masks, not face reconstruction or 3D scene relighting.
light={'method':'feathered directional 2D lighting correction','identity_geometry_changed':False,'mask':'assets/relight-mask.png','background':{'brightness':-.022,'gamma':.98},'key_curve':'0/0 0.12/0.13 0.35/0.40 0.65/0.70 0.9/0.92 1/1','comparison':'relight-color-compare.png','reference':'https://www.capcut.com/tools/relight-videos-with-ai','note':'CapCut-like soft lighting appearance; local masked correction, not use of CapCut proprietary Relight engine'}
(r/'relight.json').write_text(json.dumps(light,ensure_ascii=False,indent=2))

subprocess.run([__import__('sys').executable,str(r/'build_staged.py')],check=True)
