#!/usr/bin/env python3
"""Short01 has no earlier cut to compare, so check_owen_v4_contract.py's identity checks (original vs revised)
do not apply. This runs its timeline/mix-binding checks unchanged in logic, plus full-mode panel guard."""
import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cuts=json.loads((R/'cuts.json').read_text());raw=(R/'events.json').read_bytes();ev=json.loads(raw)
mix=json.loads((R/'qc/audio/mix-report.json').read_text())
T=cuts.get('tempo',1.0)
def M(t):
    for s in cuts['segments']:
        if t<s['src_start']:return round(s['out_start']/T,3)
        if t<=s['src_end']:return round((s['out_start']+t-s['src_start'])/T,3)
    return cuts['duration']
checks={'mix_is_new_file':not (R/'assets/mix.m4a').is_symlink(),
 'event_audio_hash_matches':hashlib.sha256(raw).hexdigest()==mix['events_sha256'],
 'cue_count_matches':len([a for a in ev['actions'] if a.get('sound')])==mix['cue_count']}
fonts=set(re.findall(r"assets/fonts/[^\s\)\"']+",(R/'index.html').read_text()))
checks['declared_font_files_exist']=bool(fonts) and all((R/f).is_file() for f in fonts)
fail=[];names=set()
for a in ev['actions']:
    n=a['name']
    if n in names:fail.append([n,'duplicate'])
    names.add(n)
    if not 0<=a['time']<cuts['duration']:fail.append([n,'outside video'])
    if a['scene']=='main':continue
    st,du,*_=ev['scenes'][a['scene']]
    if not 0<=a['local']<du:fail.append([n,'outside scene'])
    if abs(st+a['local']-a['time'])>.002:fail.append([n,'local/output mismatch'])
    if a.get('source') is not None and abs(M(a['source'])-a['time'])>.002:fail.append([n,'source/output mismatch'])
checks['event_timing_valid']=not fail
# full-mode scenes: no explanatory panel; only the CTA comment field (y>=1080) is allowed
full_panels=[]
for sid,(st,du,kind) in ev['scenes'].items():
    if kind!='ovl':continue
    body=(R/'scenes'/f'{sid}.html').read_text().split('data-height="1920">',1)[1].split('</div>\n<script>')[0].strip()
    if body and 'class="comment"' not in body:full_panels.append(sid)
checks['full_scenes_have_no_panel']=not full_panels
# scenes tile the timeline without gaps/overlaps
sc=sorted(ev['scenes'].values());cover=all(abs(sc[i][0]+sc[i][1]-sc[i+1][0])<.002 for i in range(len(sc)-1)) and sc[0][0]==0 and abs(sc[-1][0]+sc[-1][1]-cuts['duration'])<.002
checks['scenes_cover_timeline']=cover
rep={'checks':checks,'event_failures':fail,'full_panels':full_panels,'actions':len(names),'scope':'timing/mix binding only; not visual quality or listening'}
(R/'qc/parent-contract.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks))
raise SystemExit(0 if all(checks.values()) else 1)
