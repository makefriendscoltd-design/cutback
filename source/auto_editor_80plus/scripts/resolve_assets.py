import argparse,html,json,re
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--plan',required=True); ap.add_argument('--out',required=True); ap.add_argument('--asset-dir',required=True); ap.add_argument('--no-assets',action='store_true'); a=ap.parse_args()
 plan=json.loads(Path(a.plan).read_text()); d=Path(a.asset_dir); d.mkdir(parents=True,exist_ok=True); manifest=[]
 for s in plan['scenes']:
  if not s.get('asset_query'): continue
  q=s['asset_query']; conf=.82 if len(q)>6 else .68; path=''
  if not a.no_assets:
   p=d/f"{s['id']}.svg"; title=html.escape(' '.join(q.split())[:90]);
   svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1200"><rect width="100%" height="100%" rx="48" fill="#111318"/><rect x="70" y="70" width="1460" height="1060" rx="36" fill="#1d222b" stroke="#3c4658" stroke-width="4"/><text x="120" y="180" fill="#8ea2c8" font-family="Arial" font-size="44">SEMANTIC VISUAL</text><foreignObject x="120" y="250" width="1360" height="800"><div xmlns="http://www.w3.org/1999/xhtml" style="font:700 72px Arial;color:white;line-height:1.15">{title}</div></foreignObject></svg>'''
   p.write_text(svg,encoding='utf-8'); path=f"assets/{p.name}"
  s['asset_path']=path
  manifest.append({'scene_id':s['id'],'source':'generated_semantic_card' if path else 'typography_fallback','query':q,'path':path,'confidence':conf})
 Path(a.plan).write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
 Path(a.out).write_text(json.dumps({'assets':manifest},ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps({'assets':len(manifest),'mean_confidence':sum(x['confidence'] for x in manifest)/max(1,len(manifest))},ensure_ascii=False))
if __name__=='__main__': main()
