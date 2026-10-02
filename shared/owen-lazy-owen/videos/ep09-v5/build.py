#!/usr/bin/env python3
"""EP06 rebuilt from the original Owen source mechanisms, not the v3 panel template.
All editorial times are SOURCE seconds. Named actions drive both visuals and SFX.
Original speech, source cuts and approved hook remain unchanged.
"""
import os,sys,json,re,html
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'nick-plugins-mg'))
import build as lib
W,H=1080,1920
CUTS=json.loads((ROOT/'cuts.json').read_text());DUR=CUTS['duration'];SEGS=CUTS['segments']
TRANSCRIPT=json.loads((ROOT/'src/transcript.json').read_text())
WORDS=[w for s in TRANSCRIPT.get('raw',TRANSCRIPT.get('segments',[])) for w in s.get('words',[])]
def M(t):
    for s in SEGS:
        if t<s['src_start']:return s['out_start']
        if t<=s['src_end']:return round(s['out_start']+t-s['src_start'],3)
    return DUR
NAVY='linear-gradient(180deg,#07101c,#0d1b2e)'
lib.FONTS+="@font-face{font-family:'Nanum Myeongjo';src:url('assets/fonts/NanumMyeongjo-Bold.ttf');font-weight:700}"
lib.BASE='''
#root{position:absolute;inset:0;overflow:hidden;font-family:'Pretendard';color:#eef4ff;-webkit-font-smoothing:antialiased}#root *{box-sizing:border-box}.abs{position:absolute}
.gridbg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 35%,#16345088,transparent 65%),repeating-linear-gradient(0deg,#64d2ff08 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,#64d2ff08 0 1px,transparent 1px 48px)}
.cyan{color:#64d2ff}.red{color:#ff635e}.mono{font-family:'JetBrains Mono'}
.window{position:absolute;left:64px;top:300px;width:952px;height:520px;border:1px solid #385371;border-radius:24px;background:#0d1726;overflow:hidden;box-shadow:0 25px 65px #0008,0 0 35px #64d2ff0c}
.bar{height:48px;display:flex;align-items:center;gap:8px;background:#101b2c;padding:0 18px;border-bottom:1px solid #293f58}.bar i{display:block;width:10px;height:10px;border-radius:50%;background:#53657f}.bar i:first-child{background:#fe7771}.bar i:nth-child(2){background:#e7b454}.bar i:nth-child(3){background:#65bda6}.bar span{font-family:'JetBrains Mono';font-size:18px;color:#a0b5cd;margin-left:12px}
.vp{position:absolute;left:0;top:48px;width:950px;height:470px;overflow:hidden}.pan{position:absolute;left:0;top:0;transform-origin:0 0}.pan img{position:absolute;left:0;top:0}.source{position:absolute;right:18px;bottom:14px;padding:5px 10px;font-size:18px;color:#d1e1ef;background:#091424ed;border-radius:5px}.example{font-size:24px;color:#91a8bd;position:absolute;left:80px;top:1235px}.outline{fill:#64d2ff;fill-opacity:0;stroke:#64d2ff;stroke-width:7;stroke-dasharray:1;stroke-dashoffset:1}.outline.red{fill:#ff635e;stroke:#ff635e}
'''
S={};OVL=set();ACTIONS=[];CAM_SRC=[];SCENE_META={}
def bar(label):return '<div class="bar"><i></i><i></i><i></i><span>'+label+'</span></div>'
def add(sid,a,b,body,css='',js='',mode='card',cues=None):
    st=M(a);end=M(b);du=round(end-st,3)
    for name,(src,sound,gain) in (cues or {}).items():
        at=M(src);local=round(at-st,3)
        assert 0<=local<du,(sid,name,local,du)
        assert '@'+name in js,(sid,name,'unused cue')
        js=js.replace('@'+name,str(local))
        ACTIONS.append(dict(name=name,scene=sid,source=src,time=at,local=local,sound=sound,gain_db=gain))
    assert not re.search(r'@[A-Za-z]',js),(sid,'unresolved event')
    S[sid]=(st,du,lib.scene(sid,('' if mode=='full' else '<div class="gridbg"></div>')+body,css,js,NAVY if mode=='hide' else 'transparent'))
    if mode=='full':OVL.add(sid)
    SCENE_META[sid]={'source':[a,b],'mode':mode}
    CAM_SRC.append((a,mode,1.04 if mode=='full' else 1,0))
ENTER="tl.fromTo('.window',{opacity:0,y:-35},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);"
def presenter(sid,a,b):add(sid,a,b,'',mode='full')
def shot(sid,a,b,asset,url,keys,boxes,extra='',extra_css='',extra_js='',cues=None):
    """Adapted ep03 shot_card: image-coordinate poses/boxes, now keyed in source seconds."""
    iw,ih=Image.open(ROOT/'assets/shots'/asset).size
    def pose(cx,cy,z):return f'x:{475-cx*z:.3f},y:{235-cy*z:.3f},scale:{z}'
    js=[ENTER]
    for i,(src,cx,cy,z,d) in enumerate(keys):
        t=round(M(src)-M(a),3)
        js.append(f"tl.{'set' if i==0 else 'to'}('.pan',{{{pose(cx,cy,z)}"+('' if i==0 else f",duration:{d},ease:'{'none' if d>1.2 else 'power2.inOut'}'")+f'}},{t});')
    rects=[]
    for i,(name,x,y,w,h,red) in enumerate(boxes):
        rects.append(f'<rect class="outline b{i} {"red" if red else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" pathLength="1"/>')
        js.append(f"tl.fromTo('.b{i}',{{strokeDashoffset:1,fillOpacity:0}},{{strokeDashoffset:0,fillOpacity:.08,duration:.35,ease:'power2.inOut'}},@{name});")
    body=f'<div class="window">{bar(url)}<div class="vp"><div class="pan" style="width:{iw}px;height:{ih}px"><img src="assets/shots/{asset}" width="{iw}" height="{ih}"><svg style="position:absolute;inset:0" width="{iw}" height="{ih}" viewBox="0 0 {iw} {ih}">{"".join(rects)}</svg></div></div><div class="source">실제 공식 문서</div>{extra}</div>'
    add(sid,a,b,body,extra_css,'\n'.join(js)+extra_js,'card',cues)


EPISODE=9
C_SRC=[(1.2, '오늘도 AI 직원을', 'AI 직원'), (2.26, '뽑았습니다', ''), (4.7, '일마다 담당을', '담당'), (6.42, '따로 정했거든요', ''), (9.0, 'AI 하나로 다 하려니까', 'AI 하나'), (10.48, '피곤하잖아요', '피곤'), (11.96, '글은 클로드', '클로드'), (12.88, '기획안 초안은 여기 맡깁니다', '초안'), (15.9, '홈페이지는 클로드 디자인', '클로드 디자인'), (17.44, '말로 설명하면', ''), (18.88, '눌러볼 수 있는 시제품을', '시제품'), (20.18, '만들어줘요', ''), (21.82, '조사는 퍼플렉시티', '퍼플렉시티'), (23.04, '모델 카운슬 기능이 있는데', '모델 카운슬'), (25.08, '여러 AI한테 같은 질문을 던지고', '여러 AI'), (27.38, '답을 비교해줘요', '비교'), (28.4, '회의록은 파이어플라이즈', '파이어플라이즈'), (30.72, '한국어도 받아 적고요', '한국어'), (32.14, 'PPT는 캔바', '캔바'), (33.32, '이미지는 챗GPT', '챗GPT'), (34.7, '영상은 힉스필드', '힉스필드'), (36.3, '사진이나 글로 영상을 만드는', '영상'), (38.3, '작업을 맡기는 거예요', '맡기는'), (40.24, '이런 AI 활용법부터', 'AI 활용법'), (41.52, '최신 정보', '최신 정보'), (42.72, '수익화 방법까지', '수익화'), (43.68, '전자책으로 정리하고 있습니다', '전자책'), (45.62, '궁금하신 분들은', ''), (47.58, '댓글에 전자책이라고', '전자책'), (49.12, '남겨주세요', '')]
WARN=['피곤']
FACE=(1000, 340)

# Unmodified design and motion primitives from approved EP06.
HOOK_BODY='<div class="hook"><div class="hook-question">해커도 못 뚫는다고?</div><div class="hook-answer">구글이 만든 AI 스킬</div><div class="hook-line"></div></div>'
HOOK_CSS='.hook{position:absolute;left:64px;top:395px;width:952px;text-align:center;font-weight:900;letter-spacing:-3px;line-height:1.22}.hook-question{font-size:88px;color:#fff;white-space:nowrap}.hook-answer{font-size:82px;white-space:nowrap;color:#07101c;background:#64d2ff;border-radius:17px;margin-top:32px;padding:22px 10px;box-shadow:0 15px 50px #64d2ff20}.hook-line{height:5px;width:120px;margin:42px auto 0;background:#64d2ff;border-radius:5px}'
HOOK_JS="tl.fromTo('.hook-line',{scaleX:1},{scaleX:2.8,duration:1.8,ease:'power2.out'},.1);"
BADGE_BODY='<div class="idcard"><div class="lanyard"></div><div class="pic"><svg viewBox="0 0 100 100"><path d="M50 8L87 23V49Q85 76 50 94Q15 76 13 49V23Z"/><path class="check" d="M29 49L44 64L73 35"/></svg></div><div class="idtext"><small>AI EMPLOYEE / 06</small><strong>Security</strong><span>MANTIS</span></div><div class="stamp">HIRED</div></div>'
BADGE_CSS=".idcard{position:absolute;left:95px;top:1040px;width:760px;height:215px;background:#f0f3ef;color:#102437;border-radius:22px;display:flex;padding:27px 30px;gap:28px;box-shadow:0 18px 45px #0006;transform-origin:50% 0}.lanyard{position:absolute;left:340px;top:-12px;width:85px;height:15px;border-radius:8px;background:#244c60}.pic{width:135px;height:155px;background:#d7e6e8;border-radius:12px;padding:20px}.pic svg{width:95px;height:110px}.pic path{fill:none;stroke:#206275;stroke-width:6}.pic .check{stroke-dasharray:90;stroke-dashoffset:90}.idtext small{font-family:'JetBrains Mono';font-size:20px;color:#3e5661}.idtext strong{font-family:'Instrument Serif';font-size:69px;font-weight:400;display:block;line-height:1.1}.idtext span{font-family:'Silkscreen';color:#2d7389;font-size:27px}.stamp{position:absolute;right:30px;bottom:20px;color:#296e65;border:3px solid #296e65;font-family:'JetBrains Mono';font-size:25px;padding:5px 12px;transform:rotate(-12deg)}"
BADGE_JS="tl.fromTo('.idcard',{y:60,rotation:-8,opacity:0},{y:0,rotation:2,opacity:1,duration:.32,ease:'back.out(1.5)'},0);tl.to('.check',{strokeDashoffset:0,duration:.32},.15);tl.fromTo('.stamp',{scale:2,opacity:0},{scale:1,opacity:1,duration:.2,ease:'power3.in'},@hire);tl.to('.idcard',{rotation:-1,duration:.6,ease:'sine.inOut'},.65);"
COMMENT_BODY='<div class="comment"><div class="avatar">나</div><div class="field">댓글에 <b class="keyword"></b><span class="cursor">▍</span></div><div class="send">게시</div></div>'
COMMENT_CSS='.comment{position:absolute;left:64px;top:1100px;width:836px;height:123px;background:#fff;border-radius:60px;display:flex;align-items:center;gap:20px;padding:0 22px;box-shadow:0 24px 60px #0007}.avatar{width:75px;height:75px;border-radius:50%;background:#32788f;color:#fff;display:grid;place-items:center;font-size:30px;font-weight:800}.field{flex:1;color:#172e43;font-size:38px;font-weight:700}.keyword{color:#227a95}.cursor{color:#328ba0}.send{font-size:30px;color:#217896;font-weight:800;padding-right:12px}'
COMMENT_JS="tl.fromTo('.comment',{opacity:0,y:40,scale:.95},{opacity:1,y:0,scale:1,duration:.3,ease:'back.out(1.5)'},0);const kw=q('.keyword');tl.fromTo({n:0},{n:0},{n:2,duration:.35,ease:'steps(2)',onUpdate:function(){kw.textContent='보안'.slice(0,Math.round(this.targets()[0].n))}},@comment_type);tl.fromTo('.cursor',{opacity:1},{opacity:0,duration:.01,repeat:11,yoyo:true,repeatDelay:.17},0);tl.fromTo('.send',{scale:1},{scale:1.16,duration:.15,repeat:1,yoyo:true},@comment_send);"

def hook(a,b,question,answer):
    body=HOOK_BODY.replace('해커도 못 뚫는다고?',html.escape(question)).replace('구글이 만든 AI 스킬',html.escape(answer))
    # Exact6 box/type system; long original hooks must fit the same width.
    extra='.hook-question{font-size:'+str(min(88,int(1700/max(len(question),1))))+'px}.hook-answer{font-size:'+str(min(82,int(1600/max(len(answer),1))))+'px}'
    add('s01-hook',a,b,body,HOOK_CSS+extra,HOOK_JS)
def hire_badge(sid,a,b,role,code):
    body=BADGE_BODY.replace('Security',html.escape(role)).replace('MANTIS',html.escape(code)).replace('AI EMPLOYEE / 06','AI EMPLOYEE / '+str(EPISODE).zfill(2))
    cue='hire_'+sid
    add(sid,a,b,body,BADGE_CSS,BADGE_JS.replace('@hire','@'+cue),'full',{cue:(a+min(.35,(b-a)*.3),'soft-pop',-9)})
def comment(a,b,keyword):
    js=COMMENT_JS.replace("'보안'",repr(keyword)).replace('n:2','n:'+str(len(keyword))).replace('steps(2)','steps('+str(len(keyword))+')')
    matches=[s for s,txt,_ in C_SRC if a<=s<b and '댓글' in txt]
    src=matches[0] if matches else a+min(.4,(b-a)*.2)
    send=min(b-.15,src+max(.6,(b-src)*.65))
    add('s99-comment',a,b,COMMENT_BODY,COMMENT_CSS,js,'full',{'comment_type':(src,'ping-comment',-10),'comment_send':(send,'ui-tick',-11)})

exec(compile((ROOT/'storyboard.py').read_text(),str(ROOT/'storyboard.py'),'exec'),globals())
# Separate emphasis poses inside presenter beats, using actual caption source timestamps.
for sid,meta in SCENE_META.items():
    a,b=meta['source']
    if meta['mode']=='full' and sid!='s99-comment':
        candidates=[s for s,txt,acc in C_SRC if a+.35<s<b-.3 and acc]
        if candidates: CAM_SRC.append((candidates[0],'full',1.14,.24))
CAM_SRC.sort(key=lambda p:p[0])
# Face position measured from source frame (1920x1080); same framing as approved series.
CAM=[(0.0 if i==0 else M(t),m,z,tw if tw else (.32 if i and m in ('card','full') and CAM_SRC[i-1][1] in ('card','full') and m!=CAM_SRC[i-1][1] else 0)) for i,(t,m,z,tw) in enumerate(CAM_SRC)]

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
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:1}},{t});tl.to('#camBox',{{...{fmt(box)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camImg',{{...{fmt(img)},duration:{tw},ease:'power2.inOut'}},{t});tl.to('#camZoom',{{...{zo},duration:{tw},ease:'power2.inOut'}},{t});")
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
<title>맨티스 AI 보안팀 — Owen 스타일</title>
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
CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);tl.set(el,{{opacity:0}},c[1]);}});
{chr(10).join(cam_js)}
const CAMERA={json.dumps(CAM)};
CAMERA.forEach(([t,m,z,tw])=>{{tl.set('.caption',{{top:1345,width:836}},t);if(m==='card')tl.set('.caption',{{top:840,width:836}},t+tw);}});
window.__timelines["main"]=tl;
</script></body></html>
"""
os.makedirs(os.path.join(ROOT, "scenes"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "scenes")):
    os.remove(os.path.join(ROOT, "scenes", f))
for sid, (st, du, html) in S.items():
    open(os.path.join(ROOT, "scenes", sid + ".html"), "w").write(html)
open(os.path.join(ROOT, "index.html"), "w").write(HTML)


# This manifest is the only SFX timing input. No stale mix can silently survive a scene edit.
for i,(t,m,z,tw) in enumerate(CAM):
    if i and tw:
        ACTIONS.append(dict(name=f'camera_{i}',scene='main',source=CAM_SRC[i][0],time=t,local=t,sound='whoosh-down-cut' if m=='full' else 'whoosh-up-cut',gain_db=-16))
ACTIONS.append(dict(name='opening',scene='s01-hook',source=SEGS[0]['src_start'],time=0,local=0,sound='impact-low-hook',gain_db=-10))
# Sparse visual entrances; do not stack two generic SFX at every scene boundary.
for sid,(st,du,_) in S.items():
    mode=SCENE_META[sid]['mode']
    if mode!='full' and st>.05 and not any(abs(x['time']-st)<.12 for x in ACTIONS):
        ACTIONS.append(dict(name=sid+'_entrance',scene=sid,source=SCENE_META[sid]['source'][0],time=st,local=0,sound='ui-panel-appear' if mode=='card' else 'whoosh-short-cut',gain_db=-15))
ACTIONS.sort(key=lambda x:x['time'])
EV={'scenes':{sid:[st,du,'ovl' if sid in OVL else 'scn'] for sid,(st,du,_) in S.items()},'cam':CAM,'actions':ACTIONS}
(ROOT/'events.json').write_text(json.dumps(EV,ensure_ascii=False,indent=2))
(ROOT/'timing.json').write_text(json.dumps({'captions':CAPS,'camera':CAM,'scenes':EV['scenes'],'actions':ACTIONS},ensure_ascii=False,indent=2))
print(f'Built {len(S)} scenes, {len(CAPS)} captions, {len(ACTIONS)} visual/audio cues, {DUR}s')
