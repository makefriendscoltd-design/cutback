#!/usr/bin/env python3
"""Short01 v2 (faster pace, chunk captions, denser state changes; v1 = ../short01).\nShort01 (watermark text-cleaning tool) on the approved EP06 v4 engine (ep12-v5 build).
Vertical 2160x3840 selfie source (pre-scaled 1080x1920 by cut.py) -> vertical camera geometry.
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
TEMPO=CUTS.get('tempo',1.0)
def M(t):
    """Source seconds -> output seconds (cut, then whole-programme atempo)."""
    for s in SEGS:
        if t<s['src_start']:return round(s['out_start']/TEMPO,3)
        if t<=s['src_end']:return round((s['out_start']+t-s['src_start'])/TEMPO,3)
    return DUR
NAVY='linear-gradient(180deg,#07101c,#0d1b2e)'
lib.BASE='''
#root{position:absolute;inset:0;overflow:hidden;font-family:'Pretendard';color:#eef4ff;-webkit-font-smoothing:antialiased}#root *{box-sizing:border-box}.abs{position:absolute}
.gridbg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 35%,#16345088,transparent 65%),repeating-linear-gradient(0deg,#64d2ff08 0 1px,transparent 1px 48px),repeating-linear-gradient(90deg,#64d2ff08 0 1px,transparent 1px 48px)}
.cyan{color:#64d2ff}.red{color:#ff635e}.mono{font-family:'JetBrains Mono'}
.window{position:absolute;left:64px;top:300px;width:952px;height:600px;border:1px solid #385371;border-radius:24px;background:#0d1726;overflow:hidden;box-shadow:0 25px 65px #0008,0 0 35px #64d2ff0c}
.bar{height:48px;display:flex;align-items:center;gap:8px;background:#101b2c;padding:0 18px;border-bottom:1px solid #293f58}.bar i{display:block;width:10px;height:10px;border-radius:50%;background:#53657f}.bar i:first-child{background:#fe7771}.bar i:nth-child(2){background:#e7b454}.bar i:nth-child(3){background:#65bda6}.bar span{font-family:'JetBrains Mono';font-size:18px;color:#a0b5cd;margin-left:12px}
.vp{position:absolute;left:0;top:48px;width:950px;height:550px;overflow:hidden}.pan{position:absolute;left:0;top:0;transform-origin:0 0}.pan img{position:absolute;left:0;top:0}.source{position:absolute;right:18px;bottom:14px;padding:5px 10px;font-size:18px;color:#d1e1ef;background:#091424ed;border-radius:5px}.example{font-size:24px;color:#91a8bd;position:absolute;left:80px;top:1235px}.outline{fill:#64d2ff;fill-opacity:0;stroke:#64d2ff;stroke-width:7;stroke-dasharray:1;stroke-dashoffset:1}.outline.red{fill:#ff635e;stroke:#ff635e}
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
        ACTIONS.append(dict(name=f"{sid}_{name}",scene=sid,source=src,time=at,local=local,sound=sound,gain_db=gain))
    assert not re.search(r'@[A-Za-z]',js),(sid,'unresolved event')
    S[sid]=(st,du,lib.scene(sid,('' if mode=='full' else '<div class="gridbg"></div>')+body,css,js,NAVY if mode=='hide' else 'transparent'))
    if mode=='full':OVL.add(sid)
    SCENE_META[sid]={'source':[a,b],'mode':mode}
    CAM_SRC.append((a,mode,1.04 if mode=='full' else 1,0))
ENTER="tl.fromTo('.window',{opacity:0,y:-35},{opacity:1,y:0,duration:.3,ease:'power3.out'},0);"
def presenter(sid,a,b):add(sid,a,b,'',mode='full')
def shot(sid,a,b,asset,url,keys,boxes,extra='',extra_css='',extra_js='',cues=None,label='실제 공식 문서'):
    """Adapted ep03 shot_card: image-coordinate poses/boxes, now keyed in source seconds."""
    iw,ih=Image.open(ROOT/'assets/shots'/asset).size
    def pose(cx,cy,z):return f'x:{475-cx*z:.3f},y:{275-cy*z:.3f},scale:{z}'
    js=[ENTER]
    for i,(src,cx,cy,z,d) in enumerate(keys):
        t=round(M(src)-M(a),3)
        js.append(f"tl.{'set' if i==0 else 'to'}('.pan',{{{pose(cx,cy,z)}"+('' if i==0 else f",duration:{d},ease:'{'none' if d>1.2 else 'power2.inOut'}'")+f'}},{t});')
    rects=[]
    for i,(name,x,y,w,h,red) in enumerate(boxes):
        rects.append(f'<rect class="outline b{i} {"red" if red else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" pathLength="1"/>')
        js.append(f"tl.fromTo('.b{i}',{{strokeDashoffset:1,fillOpacity:0}},{{strokeDashoffset:0,fillOpacity:.08,duration:.35,ease:'power2.inOut'}},@{name});")
    body=f'<div class="window">{bar(url)}<div class="vp"><div class="pan" style="width:{iw}px;height:{ih}px"><img src="assets/shots/{asset}" width="{iw}" height="{ih}"><svg style="position:absolute;inset:0" width="{iw}" height="{ih}" viewBox="0 0 {iw} {ih}">{"".join(rects)}</svg></div></div><div class="source">{label}</div>{extra}</div>'
    add(sid,a,b,body,extra_css,'\n'.join(js)+extra_js,'card',cues)


EPISODE=1
# Source-second caption starts. Sentence starts use RMS onsets (qc/cut-rms.txt); others ASR word starts.
# Text = actual speech with ASR typos corrected (챗GPT, 워터마크, 복사해서 붙여넣어도, 정리해 뒀습니다 per medium re-ASR).
# v2: 1~3-eojeol chunks on word timestamps (source s). Sentence starts = RMS onsets; rest = ASR word starts.
C_SRC=[(1.56,'챗GPT가','챗GPT'),(2.20,'칼을 갈았습니다','칼을'),(3.58,'이제 AI가','AI'),(4.42,'쓴 글에','글'),
(5.10,'눈에 안 보이는','안 보이는'),(5.96,'워터마크를','워터마크'),(6.94,'넣기 시작했는데요','시작'),
(8.90,'복사해서','복사'),(9.40,'붙여넣어도','붙여넣어도'),(9.98,'따라갑니다','따라갑니다'),
(11.26,'그래서 이 글을','글'),(12.18,'검사하고','검사'),(12.96,'다시 다듬는','다듬는'),
(13.98,'무료 도구가','무료'),(14.74,'나왔어요','나왔어요'),
(15.77,'설치하고','설치'),(16.46,'내 글을','내 글'),(17.10,'넣은 다음','넣은'),
(17.74,'내용은 그대로','그대로'),(18.86,'두고','두고'),(19.50,'숨은 문자와','숨은 문자'),(20.50,'어색한 표현을','어색한 표현'),(21.46,'정리해줘','정리'),
(22.32,'이렇게','이렇게'),(22.60,'시키면 됩니다','시키면'),
(24.13,'블로그 글이나','블로그'),(25.10,'상품 소개에','상품 소개'),(26.10,'올리기 전에','올리기 전에'),(26.70,'한번 써보세요','써보세요'),
(28.20,'바뀐 부분까지','바뀐 부분'),(28.96,'받아서','받아서'),(29.52,'비교할 수 있습니다','비교'),
(31.52,'설치 방법부터','설치 방법'),(32.64,'복사해서 쓸','복사'),(33.86,'한글 명령까지','한글 명령'),(35.38,'정리해 뒀습니다','정리'),
(36.81,'자료 궁금하신 분들은','자료'),(38.08,'댓글에','댓글'),(38.80,'정리','정리'),(39.66,'남겨 주세요','남겨')]
WARN=['안 보이는']
FACE=(560, 880)   # face centre in the upright 1080x1920 presenter frame (measured from source frames)
CHIN_Y=1300        # full-mode zoom origin: zoom grows upward so the chin never drops under the y1345 caption

# Unmodified design and motion primitives from approved EP06.
HOOK_BODY='<div class="hook"><div class="hook-question">해커도 못 뚫는다고?</div><div class="hook-answer">구글이 만든 AI 스킬</div><div class="hook-line"></div></div>'
HOOK_CSS='.hook{position:absolute;left:64px;top:395px;width:952px;text-align:center;font-weight:900;letter-spacing:-3px;line-height:1.22}.hook-question{font-size:88px;color:#fff;white-space:nowrap}.hook-answer{font-size:82px;white-space:nowrap;color:#07101c;background:#64d2ff;border-radius:17px;margin-top:32px;padding:22px 10px;box-shadow:0 15px 50px #64d2ff20}.hook-line{height:5px;width:120px;margin:42px auto 0;background:#64d2ff;border-radius:5px}'
HOOK_JS="tl.fromTo('.hook-line',{scaleX:1},{scaleX:2.8,duration:1.8,ease:'power2.out'},.1);"
BADGE_BODY='<div class="idcard"><div class="lanyard"></div><div class="pic"><svg viewBox="0 0 100 100"><path d="M50 8L87 23V49Q85 76 50 94Q15 76 13 49V23Z"/><path class="check" d="M29 49L44 64L73 35"/></svg></div><div class="idtext"><small>AI EMPLOYEE / 06</small><strong>Security</strong><span>MANTIS</span></div><div class="stamp">HIRED</div></div>'
BADGE_CSS=".idcard{position:absolute;left:95px;top:1040px;width:760px;height:215px;background:#f0f3ef;color:#102437;border-radius:22px;display:flex;padding:27px 30px;gap:28px;box-shadow:0 18px 45px #0006;transform-origin:50% 0}.lanyard{position:absolute;left:340px;top:-12px;width:85px;height:15px;border-radius:8px;background:#244c60}.pic{width:135px;height:155px;background:#d7e6e8;border-radius:12px;padding:20px}.pic svg{width:95px;height:110px}.pic path{fill:none;stroke:#206275;stroke-width:6}.pic .check{stroke-dasharray:90;stroke-dashoffset:90}.idtext small{font-family:'JetBrains Mono';font-size:20px;color:#3e5661}.idtext strong{font-family:'Instrument Serif';font-size:69px;font-weight:400;display:block;line-height:1.1}.idtext span{font-family:'Silkscreen';color:#2d7389;font-size:27px}.stamp{position:absolute;right:30px;bottom:20px;color:#296e65;border:3px solid #296e65;font-family:'JetBrains Mono';font-size:25px;padding:5px 12px;transform:rotate(-12deg)}"
BADGE_JS="tl.fromTo('.idcard',{y:60,rotation:-8,opacity:0},{y:0,rotation:2,opacity:1,duration:.32,ease:'back.out(1.5)'},0);tl.to('.check',{strokeDashoffset:0,duration:.32},.15);tl.fromTo('.stamp',{scale:2,opacity:0},{scale:1,opacity:1,duration:.2,ease:'power3.in'},@hire);tl.to('.idcard',{rotation:-1,duration:.6,ease:'sine.inOut'},.65);"
COMMENT_BODY='<div class="comment"><div class="avatar">나</div><div class="field">댓글에 <b class="keyword"></b><span class="cursor">▍</span></div><div class="send">게시</div></div>'
COMMENT_CSS='.comment{position:absolute;left:64px;top:1185px;width:836px;height:120px;background:#0d1b2e;border:2px solid #64d2ff;border-radius:60px;display:flex;align-items:center;gap:20px;padding:0 22px;box-shadow:0 24px 60px #0007}.avatar{width:75px;height:75px;border-radius:50%;background:#32788f;color:#fff;display:grid;place-items:center;font-size:30px;font-weight:800}.field{flex:1;color:#eef4ff;font-size:38px;font-weight:700;white-space:nowrap}.keyword{color:#64d2ff;font-size:70px;font-weight:900;vertical-align:-6px;display:inline-block}.cursor{color:#64d2ff}.send{font-size:30px;color:#07101c;background:#64d2ff;border-radius:30px;padding:10px 20px;font-weight:800;padding-right:12px}'
COMMENT_JS="tl.fromTo('.comment',{opacity:0,y:40,scale:.95},{opacity:1,y:0,scale:1,duration:.3,ease:'back.out(1.5)'},0);const kw=q('.keyword');tl.fromTo({n:0},{n:0},{n:2,duration:.35,ease:'steps(2)',onUpdate:function(){kw.textContent='보안'.slice(0,Math.round(this.targets()[0].n))}},@comment_type);tl.fromTo('.cursor',{opacity:1},{opacity:0,duration:.01,repeat:11,yoyo:true,repeatDelay:.17},0);tl.fromTo('.keyword',{scale:.6},{scale:1,duration:.3,ease:'back.out(2.5)'},@comment_type);tl.fromTo('.send',{scale:1},{scale:1.16,duration:.15,repeat:1,yoyo:true},@comment_send);"

def hook(a,b,question,answer):
    body=HOOK_BODY.replace('해커도 못 뚫는다고?',html.escape(question)).replace('구글이 만든 AI 스킬',html.escape(answer))
    # Exact6 box/type system; long original hooks must fit the same width.
    extra='.hook-question{font-size:'+str(min(88,int(1700/max(len(question),1))))+'px}.hook-answer{font-size:'+str(min(82,int(1600/max(len(answer),1))))+'px}'
    add('s01-hook',a,b,body,HOOK_CSS+extra,HOOK_JS)
def hire_badge(sid,a,b,role,code):
    body=BADGE_BODY.replace('Security',html.escape(role)).replace('MANTIS',html.escape(code)).replace('AI EMPLOYEE / 06','AI EMPLOYEE / '+str(EPISODE).zfill(2))
    add(sid,a,b,body,BADGE_CSS,BADGE_JS,'full',{'hire':(a+min(.35,(b-a)*.3),'soft-pop',-9)})
def comment(a,b,keyword):
    js=COMMENT_JS.replace("'보안'",repr(keyword)).replace('n:2','n:'+str(len(keyword))).replace('steps(2)','steps('+str(len(keyword))+')')
    matches=[s for s,txt,_ in C_SRC if a<=s<b and txt==keyword]
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
# A source timestamp can collapse onto the same output timestamp after cutting.
# Keep the last authored pose so one visual transition produces one camera cue/SFX.
_cam_by_out={}
for _pose in CAM_SRC:_cam_by_out[M(_pose[0])]=_pose
CAM_SRC=sorted(_cam_by_out.values(),key=lambda p:(M(p[0]),p[0]))
# Face position measured from source frame (1920x1080); same framing as approved series.
CAM=[(0.0 if i==0 else M(t),m,z,tw if tw else (.32 if i and m in ('card','full') and CAM_SRC[i-1][1] in ('card','full') and m!=CAM_SRC[i-1][1] else 0)) for i,(t,m,z,tw) in enumerate(CAM_SRC)]

def geo(mode, z=1.0):
    """Vertical source: person.mp4 is already 1080x1920 upright."""
    if mode == "card":
        # v3: zoomed-out presenter card (no background removal). Source head 590px wide / hair-top..chin 910px
        # (measured on the 1080x1920 frame) x0.66 -> head 389px = 36% of width, 31% of height, shoulders visible.
        # v4 (user decision "인물은 꽉 채우는 게 낫다"): full source width again (x0.926, head ~50% of width)
        # under the v3 y300~900 material card. Eyes (src y880) at 40% of the 940px card; forehead..chin uncropped.
        box = dict(left=40, top=980, width=1000, height=940, borderRadius="44px 44px 0 0", borderColor="#64d2ff66")
        s = 1000 / 1080; top = -439
        img = dict(width=1080 * s, height=1920 * s, left=0, top=top)
        org = (500 * s, 880 * s + top)
    else:
        box = dict(left=0, top=0, width=1080, height=1920, borderRadius="0px", borderColor="#64d2ff00")
        img = dict(width=1080, height=1920, left=0, top=0)
        # CTA close-up (z>=1.25) zooms from the bottom edge so the face rises above the y>=1180 comment field.
        org = (FACE[0], 1880 if z >= 1.25 else CHIN_Y)
    return box, img, org
cam_js = []
fmt = lambda d: "{" + ",".join(f"{k}:{json.dumps(round(v,1) if isinstance(v,float) else v)}" for k, v in d.items()) + "}"
for t, mode, z, tw in CAM:
    if mode == "hide":
        cam_js.append(f"tl.set('#camBox',{{autoAlpha:0}},{t});"); continue
    box, img, org = geo(mode, z)
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
    e = min(M(nxt) if nxt < 1e8 else DUR, M(last_end) + .2)
    if i + 1 < len(C_SRC) and M(nxt) - e < .3: e = M(nxt)
    m = mode_at(a)
    CAPS.append([a, round(e, 3), txt, m, acc])


scene_divs = "".join(f'<div id="{sid}" class="{"ovl" if sid in OVL else "scn"}" data-composition-id="{sid}" data-composition-src="scenes/{sid}.html" data-start="{st}" data-duration="{du}" data-track-index="{2 if sid in OVL else 0}" data-width="{W}" data-height="{H}"></div>\n' for sid, (st, du, _) in S.items())

initial_box, initial_img, initial_org = geo(CAM[0][1])
def css_geometry(values):
    return ';'.join(re.sub(r'([A-Z])',lambda m:'-'+m[1].lower(),k)+':'+(str(v)+'px' if isinstance(v,(int,float)) else v) for k,v in values.items())
HTML = f"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width={W},height={H}">
<title>숏폼 1회차 워터마크 도구 — Owen 스타일</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
{lib.FONTS}
body{{margin:0;background:#000;font-family:'Pretendard',sans-serif}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;background:#07101c}}
#root *{{box-sizing:border-box}}
.scn{{position:absolute;inset:0;z-index:1}} .ovl{{position:absolute;inset:0;z-index:3}}
#camBox{{position:absolute;overflow:hidden;z-index:2;background:#111;opacity:1;visibility:visible;border:2px solid transparent;box-shadow:0 0 36px #64d2ff26,0 24px 60px #000b;{css_geometry(initial_box)}}}
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
const CARD_CAP_Y=920;  // v3/v4: seam under the y300~900 material card, above the y1000 presenter card
const WARN={json.dumps(WARN, ensure_ascii=False)};
const CAPS={json.dumps(CAPS, ensure_ascii=False)};
const host=document.getElementById('captions');
const strip=(t)=>t.replace(/[.,?!"'…“”‘’]/g,'');
const esc=(t)=>t.replace(/&/g,'&amp;').replace(/</g,'&lt;');
CAPS.forEach((c,i)=>{{const [s,e,text,mode,acc]=c;const d=document.createElement('div');d.id='cap-'+i;
 const m=(mode==='card')?'card':'full';d.className='clip caption '+m;
 d.dataset.start=s;d.dataset.duration=(e-s).toFixed(3);d.dataset.trackIndex=8;d.style.top=(m==='card'?CARD_CAP_Y:1345)+'px';
 let h=esc(strip(text));const a=strip(acc||'');if(a)h=h.replace(esc(a),'<b'+(WARN.includes(a)?' class="warn"':'')+'>'+esc(a)+'</b>');
 d.innerHTML='<span>'+h+'</span>';host.appendChild(d);}});
function fit(){{CAPS.forEach((c,i)=>{{const d=document.getElementById('cap-'+i);const sp=d.firstChild;const max=(c[3]==='card')?930:836;sp.style.fontSize='60px';if(sp.scrollWidth>max)sp.style.fontSize=Math.floor(60*max/sp.scrollWidth)+'px'}})}}
fit();if(document.fonts)document.fonts.ready.then(fit);
const tl=gsap.timeline({{paused:true}});
CAPS.forEach((c,i)=>{{const el=document.querySelector('#cap-'+i+' span');tl.fromTo(el,{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:.13,ease:'back.out(2.6)'}},c[0]);tl.set(el,{{opacity:0}},c[1]);}});
{chr(10).join(cam_js)}
const CAMERA={json.dumps(CAM)};
CAMERA.forEach(([t,m,z,tw])=>{{tl.set('.caption',{{top:1345,width:836}},t);if(m==='card')tl.set('.caption',{{top:CARD_CAP_Y,width:836}},t+tw);}});
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
    if i and tw and m!=CAM[i-1][1]:  # in-beat emphasis zooms stay silent
        ACTIONS.append(dict(name=f'camera_{i}',scene='main',source=CAM_SRC[i][0],time=t,local=t,sound='whoosh-down-cut' if m=='full' else 'whoosh-up-cut',gain_db=-19))
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
