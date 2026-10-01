import argparse,json,math,statistics,subprocess
from pathlib import Path
import cv2
import numpy as np

def load(p): return json.loads(Path(p).read_text())
def clamp(v,a,b): return max(a,min(b,v))
def score_match(value,target,maxscore,tol_full=.15,tol_partial=.45):
    if target<=0:return maxscore*.8
    err=abs(value-target)/target
    if err<=tol_full:return maxscore
    if err>=tol_partial:return maxscore*.35
    return maxscore*(1-(err-tol_full)/(tol_partial-tol_full)*.65)
def probe(v):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',v],text=True))
def stream_duration(s,d):
    try:return float(s.get('duration') or d.get('format',{}).get('duration') or 0)
    except:return 0.0
def visual_hard_gates(video):
    cap=cv2.VideoCapture(video); fps=cap.get(cv2.CAP_PROP_FPS) or 30.0; step=max(1,int(round(fps/4.0)))
    idx=0; prev=None; black_run=0; freeze_run=0; max_black=0; max_freeze=0; samples=0
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES,idx); ok,fr=cap.read()
        if not ok: break
        small=cv2.resize(fr,(180,320)); gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY); samples+=1
        black = float(gray.mean()) < 3.0
        black_run=black_run+1 if black else 0; max_black=max(max_black,black_run)
        if prev is not None:
            diff=float(np.mean(cv2.absdiff(gray,prev)))
            frozen=diff < .12
            freeze_run=freeze_run+1 if frozen else 0; max_freeze=max(max_freeze,freeze_run)
        prev=gray; idx+=step
    cap.release()
    sample_sec=step/fps
    return {'black_run_sec':max_black*sample_sec,'freeze_run_sec':max_freeze*sample_sec,'samples':samples}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--video',required=True); ap.add_argument('--style',required=True); ap.add_argument('--plan',required=True); ap.add_argument('--profile',required=True); ap.add_argument('--tokens',required=True); ap.add_argument('--manifest',required=True); ap.add_argument('--out',required=True); ap.add_argument('--target',type=float,default=80); a=ap.parse_args()
    plan,prof,tok,mani=load(a.plan),load(a.profile),load(a.tokens),load(a.manifest); maxs={'cut_rhythm':15,'talking_head_asset_ratio':15,'caption_behavior':10,'typography_layout':15,'asset_relevance':15,'scene_pattern':10,'motion_transition':10,'cta':5,'technical':5}
    hard=[]
    try:
        d=probe(a.video); subprocess.run(['ffmpeg','-v','error','-i',a.video,'-f','null','-'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    except Exception: d={}; hard.append('unplayable_or_decode_error')
    vs=[s for s in d.get('streams',[]) if s.get('codec_type')=='video']; au=[s for s in d.get('streams',[]) if s.get('codec_type')=='audio']
    if not vs: hard.append('no_video')
    else:
        w,h=int(vs[0]['width']),int(vs[0]['height'])
        if abs(w/h-9/16)>.015: hard.append('not_9_16')
    if not au: hard.append('no_audio')
    if vs and au:
        vd,ad=stream_duration(vs[0],d),stream_duration(au[0],d)
        if vd and ad and abs(vd-ad)>.08: hard.append(f'av_sync_duration_delta_{abs(vd-ad):.3f}s')
    if Path(a.video).exists() and vs:
        vh=visual_hard_gates(a.video)
        if vh['black_run_sec']>=.5: hard.append(f'black_frame_run_{vh["black_run_sec"]:.2f}s')
        if vh['freeze_run_sec']>=.5: hard.append(f'frozen_frame_run_{vh["freeze_run_sec"]:.2f}s')
    else: vh={'black_run_sec':0,'freeze_run_sec':0,'samples':0}
    if plan.get('style')!=a.style: hard.append('style_mixed')
    prefix={'oren':'Oren','jacklaydenn':'Jack'}[a.style]; other=[x for x in ['Oren','Jack'] if x!=prefix]
    mixed=[s['component'] for s in plan.get('scenes',[]) if any(str(s.get('component','')).startswith(o) for o in other)]
    if mixed: hard.append('style_component_mixed')
    canvas=tok.get('canvas',{}); cap=tok.get('caption',{}); safe_ok=canvas.get('safeX',0)>0 and canvas.get('safeTop',0)>0 and canvas.get('safeBottom',0)>0 and cap.get('maxWords',99)<=6
    if not safe_ok: hard.append('caption_safe_margin_invalid')
    scenes=plan['scenes']; ints=[s['end']-s['start'] for s in scenes]; med=statistics.median(ints) if ints else 0; refmed=float(prof['scene_interval']['median'] or med)
    cut=score_match(med,refmed,15)
    totaldur=sum(ints) or 1; talk=sum(s['end']-s['start'] for s in scenes if s['scene_type']=='talk')/totaldur; reft=float(prof['ratios'].get('talking_head',talk)); ratio=score_match(talk,reft,15,.2,.55)
    caps=plan.get('captions',[]); avgwords=statistics.mean([max(1,len(str(c.get('text','')).split())) for c in caps]) if caps else 1; mw=int(cap['maxWords']); caption=10 if avgwords<=mw else clamp(10-(avgwords-mw)*2,3,10)
    specific=sum(1 for s in scenes if str(s['component']).startswith(prefix)); typo=9+min(6,specific/max(1,len(scenes))*8); typo=min(15,typo) if safe_ok else min(8,typo)
    assets=mani.get('assets',[]); conf=statistics.mean([x.get('confidence',0) for x in assets]) if assets else .72; relevance=clamp(conf*15,0,15)
    diversity=len(set(s['scene_type'] for s in scenes)); pattern=clamp(5+diversity,0,10)
    hardshare=sum(1 for s in scenes if s.get('transition')=='hard_cut')/max(1,len(scenes)); target=float(tok.get('motion',{}).get('hardCutBias',.85)); motion=score_match(hardshare,target,10,.18,.5)
    cta=5 if scenes and scenes[-1]['scene_type']=='cta' else 2
    technical=5 if not hard else 0
    subs={'cut_rhythm':round(cut,2),'talking_head_asset_ratio':round(ratio,2),'caption_behavior':round(caption,2),'typography_layout':round(typo,2),'asset_relevance':round(relevance,2),'scene_pattern':round(pattern,2),'motion_transition':round(motion,2),'cta':round(cta,2),'technical':round(technical,2)}
    total=round(sum(subs.values()),2); passed=(not hard and total>=a.target and subs['asset_relevance']>=9 and subs['typography_layout']>=9 and subs['technical']>=4)
    fixes=[k for k,v in sorted(subs.items(),key=lambda kv:kv[1]/maxs[kv[0]])[:3]] if not passed else []
    out={'total':total,'target':a.target,'passed':passed,'hard_gate_failures':hard,'hard_gate_metrics':vh,'subscores':subs,'max_scores':maxs,'metrics':{'scene_interval_median':med,'talking_head_ratio':talk,'caption_avg_words':avgwords,'asset_confidence_mean':conf,'style_specific_components':specific},'fixes':fixes}
    Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps({'total':total,'passed':passed,'hard':hard,'fixes':fixes},ensure_ascii=False))
if __name__=='__main__': main()
