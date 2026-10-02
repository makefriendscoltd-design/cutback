#!/usr/bin/env python3
"""Owen episode 6. Source-timed semantic scenes; no stock episode text reused."""
import os,sys,json,re,html
ROOT=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(ROOT,'..','nick-plugins-mg'))
import build as lib
W,H=1080,1920
CUTS=json.load(open(os.path.join(ROOT,'cuts.json')));DUR=CUTS['duration'];SEGS=CUTS['segments']
TX=json.load(open(os.path.join(ROOT,'src/transcript.json')))['raw'];WORDS=[w for s in TX for w in s['words']]
def M(t):
 for s in SEGS:
  if t<s['src_start']:return s['out_start']
  if t<=s['src_end']:return round(s['out_start']+t-s['src_start'],3)
 return DUR
NAVY='linear-gradient(180deg,#07101c,#0d1b2e)'
lib.BASE += '''
#root{color:#f5f9ff}
.panel{position:absolute;left:64px;top:300px;width:952px;height:520px;border:2px solid #315776;border-radius:28px;background:#0b1728;overflow:hidden;box-shadow:0 25px 60px #0008}
.chrome{height:52px;background:#0c1726;border-bottom:1px solid #315776;display:flex;align-items:center;gap:9px;padding:0 22px;color:#bed2e9;font-size:20px;font-family:'JetBrains Mono'}
.chrome i{width:10px;height:10px;border-radius:100%;background:#64d2ff}.chrome em{font-style:normal;margin-left:15px}
.stage{position:absolute;left:0;right:0;top:52px;bottom:0;overflow:hidden}
.gridbg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 30%,#163450 0%,transparent 65%),repeating-linear-gradient(0deg,#64d2ff0b 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,#64d2ff0b 0 1px,transparent 1px 48px)}
.label{font-size:23px;letter-spacing:3px;color:#a9c4df;font-weight:700}.cyan{color:#64d2ff}.red{color:#ff3b30}.big{font-weight:900;font-size:62px;line-height:1.2}.small{font-size:27px;line-height:1.5;color:#d8e5f2}
.badge{display:inline-block;border:2px solid #64d2ff;border-radius:10px;padding:10px 22px;color:#64d2ff;font-weight:800;font-size:26px;background:#0b1c2d}.badge.warn{border-color:#ff3b30;color:#ff3b30}
.doc{position:absolute;left:0;top:0;transform-origin:0 0}.source{position:absolute;bottom:15px;right:18px;background:#07101cee;color:#eaf4ff;border:1px solid #38536f;padding:6px 12px;border-radius:7px;font-size:18px}
.example{position:absolute;right:22px;top:15px;font-size:19px;color:#aac1d7}
'''
S={};OVL=set();CAM_SRC=[];ACTIONS=[]
LAYOUT={'s01-hook':'card','s02-gemini':'full','s03-first':'card','s04-table':'full','s05-results':'card','s06-method':'full','s07-sources':'card','s08-mytask':'full','s09-tasks':'card','s10-same':'card','s11-warning':'card','s12-hire':'full','s13-guide':'full','s14-comment':'card'}
PRESENTER_ONLY={'s02-gemini','s04-table','s06-method','s08-mytask','s12-hire','s13-guide'}
def panel(title,body):return '<div class="panel"><div class="chrome"><i></i><i></i><i></i><em>'+title+'</em></div><div class="stage">'+body+'</div></div>'
SOUNDS={'opening':('impact-low-hook',-10),'model_reveal':('ui-panel-appear',-13),'score_argon':('ui-tick',-11),'score_gpt':('ui-tick',-11),'source_split':('ui-tick',-12),'task_mail':('ui-tick',-11),'task_data':('ui-tick',-11),'task_code':('ui-tick',-11),'same_material':('ui-panel-appear',-13),'same_job':('ui-panel-appear',-11),'warning':('impact-low-hook',-15),'comment_type':('ui-tick',-12)}
def scene(sid,a,b,body,css='',js='',mode='card',cues=()):
 mode=LAYOUT[sid]
 if sid in PRESENTER_ONLY: body,css,js='','',''
 if mode=='full': assert not body.strip(),(sid,'full presenter must remain unobstructed')
 st=M(a);du=round(M(b)-st,3)
 for name,src in cues:
  local=round(M(src)-st,3);assert 0<=local<du,(sid,name,local,du);assert '@'+name in js,(sid,name,'cue not bound')
  js=js.replace('@'+name,str(local));sound,gain=SOUNDS[name];ACTIONS.append({'name':name,'scene':sid,'source':src,'time':M(src),'local':local,'sound':sound,'gain_db':gain})
 assert '@' not in js,(sid,js)
 S[sid]=(st,du,lib.scene(sid,('' if mode=='full' else '<div class="gridbg"></div>')+body,css,js,NAVY if mode=='hide' else 'transparent'))
 if mode=='full':OVL.add(sid)
 CAM_SRC.append((a,mode,1.10 if mode=='full' else 1,0))
IN="tl.fromTo('.panel',{opacity:0,y:35,scale:.96},{opacity:1,y:0,scale:1,duration:.3,ease:'power3.out'},0);"

scene('s01-hook',4.78,8.58,'<div class="hook"><span>클로드가</span><strong>코딩 1위를 뺏겼다고?</strong></div>','.hook{position:absolute;left:64px;top:400px;width:952px;text-align:center;font-size:67px;line-height:1.15;font-weight:900;letter-spacing:-3px}.hook span{display:block;color:#f5f9ff}.hook strong{display:block;font-family:NanumMyeongjo;font-size:72px;color:#07101c;background:#64d2ff;border-radius:18px;padding:25px 10px;margin-top:25px}',"tl.set('.hook strong',{opacity:1,scale:1},@opening);",cues=[('opening',4.78)])
scene('s02-gemini',8.58,11.16,'')
scene('s03-first',11.16,14.62,panel('새 AI가 나올 때마다','<div class="rank"><span>또 1등?</span><strong>내 일도 잘할까</strong><small>한 가지 점수로 고르기 전에</small></div>'),'.rank{text-align:center;padding:36px}.rank span{font-size:94px;color:#64d2ff;font-weight:900}.rank strong{display:block;font-size:64px;margin-top:24px}.rank small{display:block;font-size:29px;color:#bdd3e6;margin-top:26px}',IN+"tl.fromTo('.rank span',{scale:.6,opacity:0},{scale:1,opacity:1,duration:.35,ease:'back.out(1.6)'},.1);tl.fromTo('.rank strong',{opacity:0,y:20},{opacity:1,y:0,duration:.3},.8);")
scene('s04-table',14.62,17.06,'')
scene('s05-results',17.06,24.54,panel('구글 공개 평가표에서 볼 것','<div class="results"><div><span>코딩 테스트마다</span><strong>앞서는 모델이 달라요</strong></div><section><b>Argon</b><b>GPT</b><b>Claude</b></section><div class="cursor"></div><small>한 평가의 1등 ≠ 모든 업무의 1등</small></div>'),'.results{text-align:center;padding:28px}.results span{font-size:31px;color:#b8ccdf}.results strong{display:block;font-family:NanumMyeongjo;font-size:52px;margin:17px 0 26px}.results section{display:flex;gap:18px;justify-content:center}.results b{font-family:JetBrains Mono;padding:23px 27px;border:2px solid #64d2ff;border-radius:15px;background:#17344a;font-size:38px;color:#64d2ff}.results small{display:block;font-size:29px;margin-top:31px;color:#c3d8e7}.cursor{position:absolute;top:260px;left:188px;width:180px;height:78px;border:4px solid #fff;border-radius:16px}',IN+"tl.fromTo('.results b',{opacity:0,scale:.8},{opacity:1,scale:1,stagger:.35,duration:.3},@score_argon);tl.to('.cursor',{x:207,duration:.7,ease:'power2.inOut'},@score_gpt);tl.to('.cursor',{x:414,duration:.7,ease:'power2.inOut'},@score_gpt+.8);",cues=[('score_argon',20.38),('score_gpt',22.02)])
scene('s06-method',24.54,26.12,'')
scene('s07-sources',26.12,32.42,panel('공개 평가표 · 출처 행 초점','<div class="origins"><div><b>직접 계산</b><span>구글이 낸 결과</span></div><i>+</i><div><b>비교 자료</b><span>다른 회사의 공개값</span></div></div><div class="rowfocus"></div><div class="note">수치 생략 · 계산한 곳과 조건 확인</div>'),'.origins{display:flex;gap:22px;align-items:center;padding:56px 33px}.origins div{flex:1;text-align:center;padding:28px 14px;border:2px solid #446e8c;border-radius:17px;background:#163047}.origins b{display:block;color:#64d2ff;font-size:43px}.origins span{display:block;font-size:26px;margin-top:25px}.origins i{font-size:45px;font-style:normal}.note{text-align:center;font-size:29px;color:#d0e2ef}.rowfocus{position:absolute;left:55px;top:105px;width:390px;height:150px;border:4px solid #64d2ff;border-radius:18px}',IN+"tl.fromTo('.origins div',{opacity:0,x:-30},{opacity:1,x:0,stagger:.5,duration:.3},0);tl.to('.rowfocus',{x:450,duration:.65,ease:'power2.inOut'},@source_split);tl.fromTo('.note',{opacity:0},{opacity:1,duration:.3},@source_split+.4);",cues=[('source_split',27.92)])
scene('s08-mytask',32.42,34.98,'')
scene('s09-tasks',34.98,38.04,panel('내가 맡길 일로 비교','<div class="tasks"><div><b>01</b>메일 초안 쓰기</div><div><b>02</b>자료 정리하기</div><div><b>03</b>코드 고치기</div></div>'),'.tasks{padding:27px 40px}.tasks div{background:#173249;border-radius:13px;padding:21px 25px;margin-bottom:15px;font-size:40px;font-weight:800}.tasks b{font-family:JetBrains Mono;font-size:33px;color:#64d2ff;margin-right:35px}',IN+"tl.fromTo('.tasks div:nth-child(1)',{opacity:0,x:-30},{opacity:1,x:0,duration:.28},@task_mail);tl.fromTo('.tasks div:nth-child(2)',{opacity:0,x:-30},{opacity:1,x:0,duration:.28},@task_data);tl.fromTo('.tasks div:nth-child(3)',{opacity:0,x:-30},{opacity:1,x:0,duration:.28},@task_code);",cues=[('task_mail',34.98),('task_data',35.94),('task_code',36.90)])
scene('s10-same',38.04,42.38,panel('같은 입력 → 결과 비교','<div class="input">동일 자료 · 동일 업무</div><div class="outputs"><div>A 결과</div><div>B 결과</div><div>C 결과</div></div><div class="select">사람이 실제 쓸 결과 선택</div>'),'.input{text-align:center;margin:28px auto;width:520px;padding:18px;border:2px solid #64d2ff;border-radius:13px;font-size:34px}.outputs{display:flex;gap:14px;padding:25px 35px}.outputs div{flex:1;padding:35px 5px;background:#173249;border-radius:13px;text-align:center;font-family:JetBrains Mono;font-size:28px}.select{text-align:center;margin:18px auto;padding:16px;width:600px;background:#64d2ff;color:#07101c;border-radius:13px;font-size:34px;font-weight:900}',IN+"tl.fromTo('.input',{opacity:0,scale:.8},{opacity:1,scale:1,duration:.28},@same_material);tl.fromTo('.outputs div',{opacity:0,y:25},{opacity:1,y:0,stagger:.18,duration:.25},@same_material+.35);tl.fromTo('.select',{opacity:0,scale:.85},{opacity:1,scale:1,duration:.3},@same_job);",cues=[('same_material',38.04),('same_job',40.20)])
scene('s11-warning',42.38,46.02,'<div class="warning">성적표 1등 ≠ 내 일 1등</div>','.warning{position:absolute;left:64px;top:470px;width:952px;text-align:center;font-size:53px;line-height:1.15;font-weight:900;color:#64d2ff}',"tl.fromTo('.warning',{opacity:0,scale:.92},{opacity:1,scale:1,duration:.3},@warning);",cues=[('warning',43.80)])
scene('s12-hire',46.02,48.62,'')
scene('s13-guide',48.62,51.10,panel('내 업무에 맞는 AI 고르는 법','<div class="guide"><strong>AI 비교 기준</strong><div>내 자료 → 같은 업무 → 결과 확인</div><small>이름보다 내가 시킬 일부터</small></div>'),'.guide{text-align:center;padding:45px 20px}.guide strong{font-size:70px;color:#64d2ff}.guide div{font-size:38px;margin-top:42px}.guide small{display:block;font-size:29px;color:#b9d1e5;margin-top:36px}',IN+"tl.fromTo('.guide div',{opacity:0,y:20},{opacity:1,y:0,duration:.3},.3);")
scene('s14-comment',51.10,53.49,'<div class="cta">댓글에 <b>비교</b></div>','.cta{position:absolute;left:64px;top:1080px;width:836px;text-align:center;font-size:66px;font-weight:900;text-shadow:0 2px 12px #000}.cta b{background:#64d2ff;color:#07101c;padding:12px 25px;border-radius:12px;text-shadow:none}',"tl.fromTo('.cta',{opacity:0,scale:.85},{opacity:1,scale:1,duration:.3,ease:'back.out(1.5)'},@comment_type);",cues=[('comment_type',51.10)])
CAM=[]
for i,(t,m,z,_) in enumerate(CAM_SRC):
 tw=.3 if i and CAM_SRC[i-1][1]!=m else 0
 CAM.append((0.0 if i==0 else M(t),m,z,tw))
FACE=(1000,340)
C_SRC=[(4.78,'오늘은 AI 직원 뽑기 전에','AI 직원'),(6.36,'성적표부터 봤습니다','성적표'),(8.58,'자 구글','구글'),(9.04,'제미나이 4 아르곤인데요','제미나이 4 아르곤'),(11.16,'새 AI가 나왔다 하면','새 AI'),(12.40,'무조건 1등이라고 하잖아요','1등'),(14.62,'근데 구글이 공개한 표를','구글'),(16.34,'끝까지 보면','끝까지'),(17.06,'코딩 테스트마다','테스트마다'),(18.16,'앞서는 모델이 다릅니다','다릅니다'),(20.38,'아르곤이 앞선 것도 있고요','아르곤'),(22.02,'GPT나 클로드가','GPT나 클로드'),(23.04,'앞선 것도 있습니다',''),(24.54,'평가 방식도 봐야 돼요','평가 방식'),(26.12,'구글이 직접 계산한 결과랑','직접 계산'),(27.92,'다른 회사 자료에서','다른 회사'),(29.84,'가져온 비교값이','비교값'),(31.02,'섞여 있거든요','섞여'),(32.42,'그러니까 내가 시킬 일로','내가 시킬 일'),(33.84,'비교하세요','비교'),(34.98,'메일 초안 쓰기나','메일 초안'),(35.94,'자료 정리하기','자료 정리'),(36.90,'코드 고치기','코드'),(38.04,'같은 자료를 주고','같은 자료'),(40.20,'같은 일을 시켜보는 겁니다','같은 일'),(42.38,'성적표에서는 잘해도','성적표'),(43.80,'내 일은 못할 수 있잖아요','내 일'),(46.02,'내 일을 잘하는 직원을','내 일'),(47.38,'뽑아야겠죠',''),(48.62,'내 업무에 맞는','내 업무'),(49.22,'AI 고르는 법이','AI 고르는 법'),(50.32,'궁금하시다면',''),(51.10,'댓글에 비교라고','비교'),(52.58,'남겨주세요','')]
WARN=[]
def geo(mode):
    if mode == "card":   # person card 1000x1040 at (40,880)
        box = dict(left=40, top=880, width=1000, height=1040, borderRadius="80px 80px 0 0")
        s = 1040 / 1080; img = dict(width=1920 * s, height=1040, left=500 - FACE[0] * s, top=0)
        org = (500, FACE[1] * s)
    else:
        box = dict(left=0, top=0, width=1080, height=1920, borderRadius="0px")
        s = 1920 / 1080; img = dict(width=1920 * s, height=1920, left=540 - FACE[0] * s, top=-40)
        org = (540, FACE[1] * s - 40)
    return box, img, org
cam_js = []
fmt = lambda d: "{" + ",".join(f"{k}:{json.dumps(round(v,1) if isinstance(v,float) else v)}" for k, v in d.items()) + "}"
for t, mode, z, tw in CAM:
    if mode == "hide":
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:0}},{t});"); continue
    box, img, org = geo(mode)
    zo = f"{{scale:{z},transformOrigin:'{org[0]:.0f}px {org[1]:.0f}px'}}"
    if tw:
        cam_js.append(f"tl.to('#camBox',{{...{fmt(box)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camImg',{{...{fmt(img)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camZoom',{{...{zo},duration:{tw},ease:'power2.inOut'}},{t});")
    else:
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:1,...{fmt(box)}}},{t});tl.set('#camImg',{fmt(img)},{t});tl.set('#camZoom',{zo},{t});")
for i, (t, mode, z, tw) in enumerate(CAM):
    if mode == "hide": continue
    nxt = CAM[i + 1][0] if i + 1 < len(CAM) else DUR
    if nxt - t > .8 and not (i + 1 < len(CAM) and CAM[i + 1][3]):
        cam_js.append(f"tl.to('#camZoom',{{scale:{z*1.035:.3f},duration:{nxt-t-max(tw,0)-.05:.2f},ease:'none'}},{t+max(tw,0)+.01:.2f});")


def mode_at(t):
    m = CAM[0][1]
    for tt, mm, *_ in CAM:
        if tt <= t + 1e-6: m = mm
    return m
CAPS = []
for i, (s, txt, acc) in enumerate(C_SRC):
    nxt = C_SRC[i + 1][0] if i + 1 < len(C_SRC) else 1e9
    last_end = max([w["end"] for w in WORDS if s - .01 <= w["start"] < nxt] or [s + .5])
    a = 0.0 if i == 0 else M(s)
    e = min(M(nxt) if nxt < 1e8 else DUR, M(last_end) + .35)
    if i + 1 < len(C_SRC) and M(nxt) - e < .25: e = M(nxt)
    m = mode_at(a)
    CAPS.append([a, round(e, 3), txt, m, acc])


scene_divs = "".join(f'<div id="{sid}" class="{"ovl" if sid in OVL else "scn"}" data-composition-id="{sid}" data-composition-src="scenes/{sid}.html" data-start="{st}" data-duration="{du}" data-track-index="{2 if sid in OVL else 0}" data-width="{W}" data-height="{H}"></div>\n' for sid, (st, du, _) in S.items())

initial_box, initial_img, initial_org = geo(CAM[0][1])
def css_geometry(values):
    return ';'.join(re.sub(r'([A-Z])',lambda m:'-'+m[1].lower(),k)+':'+(str(v)+'px' if isinstance(v,(int,float)) else v) for k,v in values.items())
HTML = f"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width={W},height={H}">
<title>AI 성적표와 업무 비교 — Owen 스타일</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
{lib.FONTS}
body{{margin:0;background:#000;font-family:'Pretendard',sans-serif}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;background:#07101c}}
#root *{{box-sizing:border-box}}
.scn{{position:absolute;inset:0;z-index:1}} .ovl{{position:absolute;inset:0;z-index:3}}
#camBox{{position:absolute;overflow:hidden;z-index:2;background:#111;opacity:1;visibility:visible;{css_geometry(initial_box)}}}
#camZoom{{position:absolute;inset:0}}
#camImg{{position:absolute;{css_geometry(initial_img)}}}
#person{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#captions{{position:absolute;inset:0;z-index:4;pointer-events:none}}
.caption{{position:absolute;text-align:center;white-space:nowrap}}
.caption.card{{left:64px;width:952px}}
.caption.full{{left:64px;width:836px}}  /* y>=1000 → x<=900 (IG safe zone) */
.caption span{{display:inline-block;font-family:'Pretendard';font-weight:800;font-size:60px;line-height:1.05;color:#fff;letter-spacing:-1px;white-space:nowrap;text-shadow:0 2px 8px #000,0 0 3px #000,0 0 3px #000}}
.caption b{{font-weight:inherit;color:#64d2ff}}
.caption b.warn{{color:#ff3b30}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{scene_divs}
<div id="camBox"><div id="camZoom" data-layout-allow-overflow><div id="camImg" data-layout-allow-overflow><video id="person" class="clip" src="assets/person.mp4" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="1" muted></video></div></div></div>
<div id="captions"></div>
<audio id="voice" src="assets/mix.m4a" data-start="0" data-duration="{DUR}" data-track-index="9"></audio>
</div>
<script>
const WARN={json.dumps(WARN, ensure_ascii=False)};
const CAPS={json.dumps(CAPS, ensure_ascii=False)};
const CAMERA={json.dumps(CAM)};
const host=document.getElementById('captions');
const strip=(t)=>t.replace(/[.,?!"'…“”‘’]/g,'');
const esc=(t)=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;');
CAPS.forEach((c,i)=>{{const [s,e,text,mode,acc]=c;const d=document.createElement('div');d.id='cap-'+i;
 const m=(mode==='card')?'card':'full';d.className='clip caption '+m;
 d.dataset.start=s;d.dataset.duration=(e-s).toFixed(3);d.dataset.trackIndex=8;d.style.top=(m==='card'?840:1345)+'px';
 let h=esc(strip(text));const a=strip(acc||'');if(a)h=h.replace(esc(a),'<b'+(WARN.includes(a)?' class="warn"':'')+'>'+esc(a)+'</b>');
 d.innerHTML='<span>'+h+'</span>';host.appendChild(d);}});
function fit(){{CAPS.forEach((c,i)=>{{const d=document.getElementById('cap-'+i);const sp=d.firstChild;const max=(c[3]==='card')?930:836;sp.style.fontSize='60px';if(sp.scrollWidth>max)sp.style.fontSize=Math.floor(60*max/sp.scrollWidth)+'px'}})}}
fit();if(document.fonts)document.fonts.ready.then(fit);
const tl=gsap.timeline({{paused:true}});
CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');if(i===0)tl.set(el,{{opacity:1,scale:1}},0);else tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);tl.set(el,{{opacity:0}},c[1]);}});
CAPS.forEach((c,i)=>{{const j=CAMERA.findIndex(k=>Math.abs(k[0]-c[0])<.001&&k[3]>0);if(j>0){{const oldY=CAMERA[j-1][1]==='card'?840:1345;const newY=CAMERA[j][1]==='card'?840:1345;const textNode=document.getElementById('cap-'+i).firstChild;tl.set(textNode,{{y:1345-newY}},c[0]);tl.set(textNode,{{y:0}},c[0]+CAMERA[j][3]);}}}});
{chr(10).join(cam_js)}
window.__timelines["main"]=tl;
</script></body></html>
"""
os.makedirs(os.path.join(ROOT, "scenes"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "scenes")):
    if os.path.isfile(os.path.join(ROOT, "scenes", f)): os.remove(os.path.join(ROOT, "scenes", f))
for sid, (st, du, html) in S.items():
    open(os.path.join(ROOT, "scenes", sid + ".html"), "w").write(html)
open(os.path.join(ROOT, "index.html"), "w").write(HTML)

EV={'scenes':{sid:[st,du,'ovl' if sid in OVL else 'scn'] for sid,(st,du,_) in S.items()},'cam':CAM,'ticks':[M(t) for t in [9.04,17.06,20.38,22.02,26.12,27.92,34.98,35.94,36.9,40.2,51.86]],'actions':ACTIONS}
json.dump(EV,open(os.path.join(ROOT,'events.json'),'w'),indent=2)
json.dump({'captions':CAPS,'camera':CAM,'scenes':EV['scenes']},open(os.path.join(ROOT,'timing.json'),'w'),ensure_ascii=False,indent=2)
print(f'wrote {len(S)} scenes, {len(CAPS)} captions, {DUR}s')
