"""Pace comparison v1 (../short01) vs v2 from each build's timing.json/events.json."""
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def stats(p):
    t=json.loads((p/'timing.json').read_text());e=json.loads((p/'events.json').read_text());dur=json.loads((p/'cuts.json').read_text())['duration']
    times=sorted({round(a['time'],2) for a in e['actions']}|{round(c[0],2) for c in e['cam']}|{round(v[0],2) for v in e['scenes'].values()})
    ch=[];last=-1
    for x in times:
        if x-last>=.15:ch.append(x);last=x
    gaps=[b-a for a,b in zip(ch,ch[1:]+[dur])]
    caps=t['captions'];txt=''.join(c[2] for c in caps)
    hangul=len(re.findall(r'[가-힣]',txt));latin=txt.count('GPT')*3+txt.count('AI')*3  # 지피티 / 에이아이
    return {'duration_s':dur,'visual_changes':len(ch),'mean_change_interval_s':round(sum(gaps)/len(gaps),3),'max_change_gap_s':round(max(gaps),3),
            'captions':len(caps),'mean_caption_s':round(sum(c[1]-c[0] for c in caps)/len(caps),3),'mean_caption_eojeol':round(sum(len(c[2].split()) for c in caps)/len(caps),2),
            'syllables':hangul+latin,'syllables_per_s':round((hangul+latin)/dur,2),
            'sfx_cues':len([a for a in e['actions'] if a.get('sound')])}
v1=stats(R.parent/'short01');v2=stats(R)
out={'v1':v1,'v2':v2,'duration_ratio':round(v2['duration_s']/v1['duration_s'],3),'tempo':json.loads((R/'cuts.json').read_text())['tempo'],
     'note':'visual change = named action, camera key or scene start, merged within 0.15s; syllables = Hangul + GPT/AI read as 3 each'}
(R/'qc/pace.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
