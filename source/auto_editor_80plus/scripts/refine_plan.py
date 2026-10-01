import argparse,json
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('--plan',required=True); ap.add_argument('--benchmark',required=True); ap.add_argument('--out',required=True); ap.add_argument('--pass-num',type=int,required=True); a=ap.parse_args()
p=json.loads(Path(a.plan).read_text()); b=json.loads(Path(a.benchmark).read_text()); p['pass']=a.pass_num; fixes=[]; style=p['style']
comp={'oren':{'talk':'TalkingHeadBase','overlay':'OrenUpperUiOverlay','cta':'ProfileCTA'},'jacklaydenn':{'talk':'TalkingHeadBase','overlay':'JackEvidenceOverlay','cta':'ProfileCTA'}}[style]
low=sorted(b['subscores'].items(), key=lambda kv: kv[1]/b['max_scores'][kv[0]])[:3]
for k,_ in low:
 fixes.append(k)
 if k=='talking_head_asset_ratio':
  for i,s in enumerate(p['scenes'][1:-1],1):
   if i%3==1 and s['scene_type']=='talk': s['scene_type']='overlay'; s['component']=comp['overlay']; s['asset_query']=s['dialogue']
 if k=='caption_behavior':
  for c in p.get('captions',[]):
   ws=c['text'].split(); c['text']=' '.join(ws[:max(2,min(4,len(ws)))])
 if k=='cta' and p['scenes']:
  p['scenes'][-1]['scene_type']='cta'; p['scenes'][-1]['component']=comp['cta']
p.setdefault('refinements',[]).append({'pass':a.pass_num,'based_on':fixes})
Path(a.out).write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps({'refined':fixes},ensure_ascii=False))
