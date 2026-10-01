import argparse,hashlib,json,math,re
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())
def text_at(segs,s,e):
    parts=[x['text'] for x in segs if float(x['end'])>s and float(x['start'])<e]
    return ' '.join(parts).strip()
def all_words(segs):
    rows=[]
    for s in segs:
        ws=s.get('words') or []
        if ws:
            for w in ws:
                if w.get('word'): rows.append({'start':float(w.get('start',s['start'])),'end':float(w.get('end',s['end'])),'word':str(w['word']).strip()})
        else:
            toks=str(s.get('text','')).split(); dur=max(.01,float(s['end'])-float(s['start']))
            for i,w in enumerate(toks): rows.append({'start':float(s['start'])+dur*i/max(1,len(toks)),'end':float(s['start'])+dur*(i+1)/max(1,len(toks)),'word':w})
    return [x for x in rows if x['word']]
def caption_chunks(words,maxw,style):
    minw=2 if style!='jacklaydenn' else 1; chunks=[]; cur=[]
    for w in words:
        cur.append(w)
        punctuation=bool(re.search(r'[.!?。！？]$',w['word']))
        if len(cur)>=maxw or (punctuation and len(cur)>=minw):
            txt=' '.join(x['word'] for x in cur); hi=next((x['word'] for x in cur if re.search(r'\d',x['word'])),max((x['word'] for x in cur),key=len,default=''))
            chunks.append({'start':round(cur[0]['start'],3),'end':round(cur[-1]['end'],3),'text':txt,'highlight':hi}); cur=[]
    if cur:
        txt=' '.join(x['word'] for x in cur); chunks.append({'start':round(cur[0]['start'],3),'end':round(cur[-1]['end'],3),'text':txt,'highlight':max((x['word'] for x in cur),key=len,default='')})
    return chunks
def component(style,kind):
    m={'oren':{'talk':'TalkingHeadBase','title':'OrenSerifChapterTitle','asset':'OrenEvidenceFullscreen','overlay':'OrenUpperUiOverlay','burst':'OrenReferenceBurst','cta':'ProfileCTA'},'jacklaydenn':{'talk':'TalkingHeadBase','title':'JackBigKeyword','asset':'JackEvidenceOverlay','overlay':'JackBigKeyword','burst':'JackStoryMontage','cta':'ProfileCTA'}}
    return m[style][kind]
def semantic_kind(style,text,index,n):
    t=text.lower(); nums=bool(re.search(r'\d|%|\$|원|만원|배|개|명',t)); tools=bool(re.search(r'ai|tool|app|software|website|dashboard|prompt|클로드|claude|챗gpt|chatgpt|노션|suno|캡컷|도구|툴|앱|기능|설치|클릭',t)); evidence=bool(re.search(r'proof|result|example|data|report|screenshot|실제|결과|사례|자료|증거|화면',t)); story=bool(re.search(r'when i|then|finally|story|experience|처음|그때|결국|경험|여행|실패|문제',t))
    if index==0:return 'title'
    if index==n-1:return 'cta'
    if style=='jacklaydenn':
        if nums:return 'title'
        if story:return 'burst'
        if evidence:return 'asset'
        return 'talk'
    if nums or evidence:return 'asset'
    if tools:return 'overlay'
    if story:return 'burst'
    return 'talk'
def enforce_ratio(kinds,talk_ratio):
    n=len(kinds); target=max(1,min(n-2,round(n*talk_ratio))); current=sum(k=='talk' for k in kinds)
    if current<target:
        for i in range(1,n-1):
            if kinds[i] not in {'talk','title','cta'}: kinds[i]='talk'; current+=1
            if current>=target:break
    elif current>target:
        for i in range(1,n-1):
            if kinds[i]=='talk': kinds[i]=['asset','overlay','burst'][i%3]; current-=1
            if current<=target:break
    return kinds
def detect_candidates(segs):
    out=[]; fillers={'um','uh','like','you know','음','어','그니까','그러니까'}
    for a,b in zip(segs,segs[1:]):
        gap=float(b['start'])-float(a['end'])
        if gap>=.55: out.append({'type':'silence','start':round(float(a['end']),3),'end':round(float(b['start']),3),'duration':round(gap,3),'action':'record_only_audio_master_locked'})
    for s in segs:
        txt=str(s.get('text','')).strip().lower()
        if txt in fillers: out.append({'type':'filler','start':s['start'],'end':s['end'],'text':s.get('text',''),'action':'record_only_audio_master_locked'})
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--transcript',required=True); ap.add_argument('--style',required=True); ap.add_argument('--profile',required=True); ap.add_argument('--tokens',required=True); ap.add_argument('--skill',required=True); ap.add_argument('--out',required=True); ap.add_argument('--pass-num',type=int,default=1); a=ap.parse_args()
    tr=load(a.transcript); segs=tr['segments']; prof=load(a.profile); tok=load(a.tokens); skill_text=Path(a.skill).read_text(encoding='utf-8'); skill_sha=hashlib.sha256(skill_text.encode()).hexdigest(); duration=max(float(x['end']) for x in segs)
    med=float(prof['scene_interval']['median'] or 2.0); target=max(.55,min(3.5,med)); n=max(2,math.ceil(duration/target)); step=duration/n; talk=max(.25,min(.8,float(prof['ratios'].get('talking_head',.55))))
    texts=[text_at(segs,i*step,duration if i==n-1 else (i+1)*step) or segs[min(i,len(segs)-1)]['text'] for i in range(n)]; kinds=enforce_ratio([semantic_kind(a.style,t,i,n) for i,t in enumerate(texts)],talk)
    scenes=[]
    for i,(txt,k) in enumerate(zip(texts,kinds)):
        s=i*step; e=duration if i==n-1 else (i+1)*step; query=txt if k in {'asset','overlay','burst'} else ''
        scenes.append({'id':f's{i+1:02d}','start':round(s,3),'end':round(e,3),'scene_type':k,'component':component(a.style,k),'dialogue':txt,'asset_query':query,'transition':'hard_cut'})
    captions=caption_chunks(all_words(segs),int(tok['caption']['maxWords']),a.style)
    out={'style':a.style,'pass':a.pass_num,'duration':duration,'profile_scene_interval':prof['scene_interval'],'reference_ratios':prof['ratios'],'skill_source':str(Path(a.skill)),'skill_sha256':skill_sha,'planner_mode':'deterministic_semantic_agent_fallback','scenes':scenes,'captions':captions,'audio_policy':'preserve_master_no_recut','silence_flub_candidates':detect_candidates(segs)}
    Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps({'style':a.style,'scenes':len(scenes),'captions':len(captions),'duration':duration,'target_interval':step,'skill_sha256':skill_sha[:12]},ensure_ascii=False))
if __name__=='__main__': main()
