from pathlib import Path
import json,html,re
R=Path(__file__).parent;P=R/'composition';plan=json.loads((R/'edit-plan.json').read_text());D=plan['duration']
# Remove editorial headline/subheadline cards. UI labels exist only inside the depicted action.
scenes=[(0.0,12.766667,'face','dark'),(12.766667,18.766667,'lesson','light'),(18.766667,28.55,'try','dark'),(28.55,32.8,'face','dark'),(32.8,43.366667,'practice','dark'),(43.366667,45.466667,'face','dark'),(45.466667,52.533333,'book','light'),(52.533333,D,'comment','dark')]
css=(R/'base-style.css').read_text()+'''
.art{left:64px;top:175px;width:952px;height:700px}.graphic{margin:0;height:700px}.caption{top:920px;font-size:56px}.caption.face-cap{top:1040px}.browser{position:relative;width:920px;height:650px;margin:auto;border-radius:28px;border:2px solid #ffffff26;overflow:hidden;background:#102832;box-shadow:0 25px 85px #0005;color:#f5f9ff}.light .browser{background:#fffdfb;color:#1b2934;border-color:#dac9bf;box-shadow:0 25px 75px #875b3029}.chrome{height:60px;padding:17px 25px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #9bb9c433;font-size:21px}.dot{width:11px;height:11px;border-radius:100%;background:#fc7971}.dot:nth-child(2){background:#e9ba58}.dot:nth-child(3){background:#71d7bb}.chrome span{margin-left:22px;opacity:.75}.workspace{position:absolute;left:30px;right:30px;top:95px;bottom:30px}.ui-label{font-size:28px;font-weight:700}.player{height:230px;border-radius:16px;display:flex;align-items:center;justify-content:center;background:linear-gradient(140deg,#145f65,#263b77);font-size:68px;color:white}.playerbar{position:absolute;left:30px;right:30px;bottom:28px;height:7px;background:#ffffff40}.barfill{height:100%;width:100%;background:#80e1c1;transform-origin:left}.player-wrap{position:relative}.lesson-row{display:flex;justify-content:space-between;padding:18px 4px;border-bottom:1px solid #99847730;font-size:27px}.tick{color:#16836f}.pending{color:#a46b4d}.project-sheet{position:absolute;inset:0;padding:30px;background:var(--panel);border:1px solid var(--line);border-radius:16px}.sheet-lines{margin-top:30px}.sheet-lines i{display:block;width:90%;height:12px;background:#7db7b447;border-radius:8px;margin:20px 0}.sheet-lines i:nth-child(2){width:62%}.sheet-lines i:nth-child(3){width:77%}.btn{padding:14px 28px;border-radius:12px;background:#62d0b5;color:#102827;font-size:26px;font-weight:700;display:inline-block}.btn.muted{background:#405365;color:#dce8e9}.result-card{position:absolute;left:80px;right:80px;top:140px;background:#213b49;border:1px solid #719eac70;border-radius:24px;padding:42px}.result-card .tiles{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:25px}.tile{height:130px;border-radius:12px;background:linear-gradient(135deg,#398b91,#8e80b1)}.tile:last-child{background:linear-gradient(135deg,#aa8c57,#548c7b)}.stage{position:absolute;inset:0}.newinput{position:absolute;left:20px;right:20px;bottom:30px;height:100px;border:2px solid #6b909d;border-radius:18px;padding:28px;font-size:26px;color:#a8bec7}.caret{display:inline-block;width:3px;height:33px;background:#bdeedc;vertical-align:middle}.uicursor{position:absolute;left:625px;top:350px;width:48px;height:60px;filter:drop-shadow(0 3px 3px #0008)}.errorline{position:absolute;top:265px;left:25px;right:25px;padding:25px;border:1px solid #c96870;border-radius:14px;background:#562b37;color:#ffd7dd;font-size:29px}.terminal{background:#07151c;border:1px solid #496574;border-radius:14px;padding:26px;margin-top:28px;height:200px}.code-row{height:13px;border-radius:6px;background:#739ba780;margin:17px 0;width:85%}.code-row:nth-child(2){width:60%;background:#db888d}.code-row:nth-child(3){width:74%}.fixedline{position:absolute;left:28px;right:170px;top:126px;height:13px;background:#6bdfbf;border-radius:5px}.successbox{position:absolute;left:40px;right:40px;top:140px;border:1px solid #69bba4;background:#173e3a;border-radius:20px;padding:40px;font-size:35px;color:#c0f9e8}.successbox .sheet-lines{margin-top:20px}.checkbig{font-size:64px;color:#87eac8}.workbook{position:absolute;left:70px;top:35px;width:700px;height:560px;border-radius:10px;background:#fffdf5;color:#263933;box-shadow:18px 14px 0 #e6dfcc,27px 27px 55px #0003;padding:55px}.workbook .booktitle{font-size:52px;line-height:1.2;margin:45px 0 30px}.workbook .q{font-size:28px;margin:28px 0 13px}.rule{height:2px;background:#d7d5c8;margin:25px 0}.written{font-size:31px;color:#397366}.paper2{background:#fffef9}.chosen{position:absolute;left:42px;right:42px;bottom:45px;border:3px solid #5d9d88;border-radius:9px;height:64px}.comment-shell{top:370px;height:650px}.comment-box{margin:40px 28px;padding:25px;background:#172e3b;border-radius:20px;font-size:34px;display:flex;justify-content:space-between}.sent{margin:35px 30px;background:#4b568a;border-radius:18px;padding:24px 30px;font-size:35px;width:200px}.smallnote{font-size:20px;color:#748d8e;position:absolute;bottom:14px;right:20px}
'''
css += '\n.facecam{position:absolute;inset:0;width:1080px;height:1920px;transform-origin:50% 30%;z-index:4}.introhook{position:absolute;inset:0;z-index:60;background:linear-gradient(0deg,#0002,#0004)}.hookcopy{position:absolute;left:55px;right:55px;top:620px;text-align:center;font-size:190px;line-height:1.12;font-weight:900;letter-spacing:-7px;color:#fff;-webkit-text-stroke:6px #182022;paint-order:stroke fill;text-shadow:0 8px 14px #0009}.hookcopy span{display:block}.hookcopy span:first-child{color:#ffd6a8}.introhook~.caption{z-index:40}.cta-cap{top:210px!important}.ig-scene{position:absolute;inset:0;background:#080808}.ig-sheet{position:absolute;left:0;top:370px;width:1080px;height:1550px;border-radius:45px 45px 0 0;background:#252525;color:#fff;overflow:hidden}.ig-handle{width:100px;height:9px;background:#727272;margin:24px auto 35px;border-radius:8px}.ig-title{text-align:center;font-size:48px;font-weight:700;margin-bottom:28px}.ig-divider{height:1px;background:#444}.ig-bottom{position:absolute;left:0;right:0;bottom:0;background:#252525;padding:28px 30px 15px;border-top:1px solid #444}.ig-reactions{font-size:45px;display:flex;word-spacing:30px;margin:0 0 34px 18px}.ig-input-row{display:flex;gap:20px;align-items:center}.ig-avatar{width:76px;height:76px;flex-shrink:0;border-radius:50%;background:linear-gradient(145deg,#b56d4b,#5a5679);display:flex;align-items:center;justify-content:center;font-size:27px;color:white}.ig-input{height:98px;flex:1;border:2px solid #646464;border-radius:55px;position:relative;padding:25px 28px;font-size:33px}.ig-placeholder{color:#9d9d9d;position:absolute;left:28px;top:25px}.ig-input .typed{position:absolute;left:28px;top:25px}.ig-post-button{position:absolute;right:25px;top:24px;background:none;border:0;color:#3797f0;font-family:P;font-size:32px;font-weight:700}.ig-caret{height:36px;width:3px;background:#3797f0;position:absolute;left:99px;top:29px}.ig-home{width:300px;height:10px;background:#eee;border-radius:8px;margin:42px auto 0}.ig-post.sent{position:absolute;left:30px;right:30px;top:195px;background:none;width:auto;display:flex;gap:24px;margin:0;padding:24px 0}.ig-user{font-size:30px}.ig-user span{font-size:24px;color:#a7a7a7;margin-left:18px}.ig-post-text{font-size:35px;margin-top:12px}.ig-reply{font-size:24px;color:#aaa;margin-top:25px}.ig-heart{width:35px;height:35px;position:absolute;right:10px;top:50px;color:#ccc}.ig-empty{position:absolute;top:420px;width:100%;text-align:center;font-size:38px;color:#989898}#s7 .art{inset:0;width:1080px;height:1920px}.player{overflow:hidden}.player::after{content:"";position:absolute;inset:35px 170px;background:linear-gradient(125deg,#448d9966,#8490da77);border:1px solid #c9ffff50;border-radius:18px;z-index:0}.player{position:relative}.playerbar{z-index:1}.newinput::after{content:"";position:absolute;left:20px;bottom:18px;width:40%;height:3px;background:#65c9b5;transform-origin:left}.fixedline{top:166px}.practice-state .terminal{position:relative}.sweep{position:absolute;top:30px;bottom:30px;width:50px;background:#b1ffeb26;transform:skew(-12deg)}\n'
css += '\n#s2 .result-card{left:20px;right:20px;top:75px;padding:25px 22px 40px}#s2 .tiles{display:flex;gap:14px;perspective:1000px}#s2 .tile{position:relative;flex:1;height:270px;overflow:hidden;border:1px solid #c7efff44;box-shadow:0 14px 30px #0006}#s2 .tile span{position:absolute;left:15px;bottom:12px;font-size:23px;color:#fff;z-index:3}#s2 .tile-video{background:linear-gradient(160deg,#573e9b,#35aab0)}.thumb-sun{position:absolute;width:60px;height:60px;border-radius:50%;background:#ffd993;right:25px;top:35px}.thumb-hill{position:absolute;width:240px;height:180px;background:#23587b;transform:rotate(35deg);left:-10px;top:100px;border-radius:20px}.thumb-track{position:absolute;left:12px;right:12px;bottom:55px;display:flex;gap:6px}.thumb-track i{height:18px;flex:1;background:#bba0fa;border-radius:3px}#s2 .tile-page{background:#d5ddec}.mini-nav{position:absolute;left:16px;right:16px;top:22px;height:12px;background:#35496b;border-radius:8px}.mini-hero{position:absolute;left:16px;right:16px;top:55px;height:87px;border-radius:10px;background:linear-gradient(140deg,#ac8cec,#6b79bf)}.mini-columns{position:absolute;left:16px;right:16px;top:155px;display:flex;gap:9px}.mini-columns i{height:53px;flex:1;border-radius:6px;background:#8097b2}#s2 .tile-page span{color:#23395a}#s2 .tile-flow{background:linear-gradient(135deg,#153b40,#558474)}.tile-flow>i{position:absolute;left:80px;width:50px;height:45px;border:2px solid #a1ead2;background:#366b65;border-radius:10px;top:25px}.tile-flow>i:nth-of-type(2){top:95px}.tile-flow>i:nth-of-type(3){top:165px}.flow-line{position:absolute;left:104px;top:45px;width:3px;height:140px;background:#a1ead2;transform-origin:top}\n'
parts=[];anim=[];events=[]
def show(sel,start,end):
 anim.append(f'tl.set("{sel}",{{opacity:0}},0);')
 anim.append(f'tl.fromTo("{sel}",{{opacity:0}},{{opacity:1,duration:.10}},{start});')
 if end is not None:anim.append(f'tl.to("{sel}",{{opacity:0,duration:.10}},{end});tl.set("{sel}",{{opacity:0}},{end+.10});')
def cursor():return '<svg class="uicursor" viewBox="0 0 48 60"><path d="M4 2L42 35L25 37L34 53L24 58L16 41L4 52Z" fill="white" stroke="#162832" stroke-width="3"/></svg>'
def browser(title,body,cls=''):return f'<div class="browser {cls}"><div class="chrome"><i class="dot"></i><i class="dot"></i><i class="dot"></i><span>{title}</span></div><div class="workspace">{body}</div></div>'
for i,(a,b,k,theme) in enumerate(scenes):
 ident=f's{i}';dur=b-a
 if k=='face':
  parts.append(f'<section id="{ident}" class="clip scene {theme}" data-start="{a}" data-duration="{dur}" data-track-index="2"></section><div id="facecam{i}" class="facecam"><video id="face{i}" class="clip face-video" src="assets/base.mp4" data-start="{a}" data-duration="{dur}" data-media-start="{a}" data-track-index="4" muted></video></div>');continue
 if k=='lesson':
  body=browser('수업', '<div class="lesson-state stage"><div class="player-wrap"><div class="player">▶</div><div class="playerbar"><div class="barfill"></div></div></div><div class="lesson-row">수강 <span class="lesson-done tick">✓</span></div><div class="lesson-row">내 프로젝트 <span class="pending">제출 전</span></div></div><div class="project-state stage project-sheet"><div class="ui-label">내 프로젝트</div><div class="sheet-lines"><i></i><i></i><i></i></div><div class="btn" style="margin-top:35px">만들기</div></div>')
  show(f'#{ident} .lesson-state',a,None);anim.append(f'tl.fromTo("#{ident} .barfill",{{scaleX:.72}},{{scaleX:1,duration:1.5,ease:"none"}},14.05);');show(f'#{ident} .lesson-done',15.55,None);anim.append(f'tl.to("#{ident} .lesson-state",{{opacity:0,duration:.16}},17.5);');show(f'#{ident} .project-state',17.6,None)
 elif k=='try':
  body=browser('프로젝트','<div class="gallery-state stage"><div class="result-card"><div class="ui-label">프로젝트</div><div class="tiles"><div class="tile tile-video"><div class="thumb-sun"></div><div class="thumb-hill"></div><div class="thumb-track"><i></i><i></i><i></i></div><span>영상</span></div><div class="tile tile-page"><div class="mini-nav"></div><div class="mini-hero"></div><div class="mini-columns"><i></i><i></i></div><span>페이지</span></div><div class="tile tile-flow"><div class="flow-line"></div><i></i><i></i><i></i><span>자동화</span></div></div></div>'+cursor()+'</div><div class="blank-state stage"><div class="ui-label">새 프로젝트</div><div class="newinput"><span class="caret"></span></div></div><div class="error-state stage"><div class="ui-label">내 프로젝트</div><div class="terminal"><div class="code-row"></div><div class="code-row"></div><div class="code-row"></div></div><div class="errorline">실행 오류 <span style="float:right">×</span></div></div>')
  show(f'#{ident} .gallery-state',a,21.10);anim.append(f'tl.fromTo("#{ident} .uicursor",{{x:90,y:100}},{{x:-65,y:-80,duration:.55}},20.42);');show(f'#{ident} .blank-state',21.13,26.72);anim.append(f'tl.fromTo("#{ident} .caret",{{opacity:1}},{{opacity:0,duration:.35,yoyo:true,repeat:7}},23.63);');show(f'#{ident} .error-state',26.87,None);anim.append(f'tl.to("#{ident} .browser",{{scale:.85,opacity:0,duration:.22}},28.3);tl.set("#{ident} .browser",{{opacity:0}},28.55);')
 elif k=='practice':
  body=browser('내 프로젝트','<div class="practice-state stage"><div class="ui-label">만들기</div><div class="terminal"><div class="code-row"></div><div class="code-row"></div><div class="code-row"></div><div class="fixedline"></div></div><div class="btn muted" style="margin-top:24px">실행</div>'+cursor()+'</div><div class="success-state stage"><div class="successbox"><span class="checkbig">✓</span><div class="sheet-lines"><i></i><i></i></div><div class="btn" style="margin-top:24px">다시 실행</div></div></div>')
  show(f'#{ident} .practice-state',a,39.3);show(f'#{ident} .fixedline',37.8,None);anim.append(f'tl.fromTo("#{ident} .uicursor",{{x:100,y:70}},{{x:-300,y:10,duration:.4}},37.35);');show(f'#{ident} .success-state',39.45,None)
 elif k=='book':
  body='<div class="workbook coverpage"><div class="ui-label">워크북</div><div class="booktitle">내 첫 프로젝트</div><div class="rule"></div><div class="sheet-lines"><i></i><i></i></div></div><div class="workbook paper2"><div class="q">내가 만들고 싶은 것</div><div class="rule"></div><div class="rule"></div><div class="q">첫 번째로 해볼 일</div><div class="rule"></div><div class="rule"></div><div class="chosen"></div></div>'
  show(f'#{ident} .coverpage',a,48.95);show(f'#{ident} .paper2',49.1,None);anim.append(f'tl.fromTo("#{ident} .paper2",{{x:170,rotation:5}},{{x:0,rotation:0,duration:.42}},49.1);');show(f'#{ident} .chosen',50.5,None)
 else:
  body='<div class="ig-scene"><div class="ig-sheet"><div class="ig-handle"></div><div class="ig-title">댓글</div><div class="ig-divider"></div><div class="ig-empty">댓글을 남겨보세요</div><div class="sent ig-post"><div class="ig-avatar">나</div><div><div class="ig-user">나 <span>방금</span></div><div class="ig-post-text">시작</div><div class="ig-reply">답글 달기</div></div><svg class="ig-heart" viewBox="0 0 24 24"><path d="M12 21S2 15 2 8a5 5 0 0110-2 5 5 0 0110 2c0 7-10 13-10 13Z" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></div><div class="ig-bottom"><div class="ig-reactions">❤️ 🙌 🔥 👏 😍 😮 😂</div><div class="ig-input-row"><div class="ig-avatar">나</div><div class="ig-input"><span class="ig-placeholder">댓글 달기...</span><span class="typed">시작</span><span class="ig-caret"></span><button class="ig-post-button">게시</button></div></div><div class="ig-home"></div></div></div></div>'
  show(f'#{ident} .ig-empty',a,52.65);show(f'#{ident} .ig-placeholder',a,52.65)
  anim.append(f'tl.to("#{ident} .ig-post-button",{{scale:.88,duration:.07,yoyo:true,repeat:1}},53.52);')
  show(f'#{ident} .typed',52.7,53.6);show(f'#{ident} .sent',53.6,None);anim.append(f'tl.fromTo("#{ident} .sent",{{y:28}},{{y:0,duration:.2}},53.6);')
 parts.append(f'<section id="{ident}" class="clip scene {theme}" data-start="{a}" data-duration="{dur}" data-track-index="2"><div class="art">{body}</div></section>')
 anim.append(f'tl.fromTo("#{ident} .art",{{opacity:0,y:28}},{{opacity:1,y:0,duration:.26,ease:"power2.out"}},{a});')
 if k!='comment':
  parts.append(f'<div id="plate{i}" class="speaker-window"><video id="vplate{i}" class="clip" src="assets/base.mp4" data-start="{a}" data-duration="{dur}" data-media-start="{a}" muted></video></div><video id="person{i}" class="clip cutout" src="assets/person.webm" data-start="{a}" data-duration="{dur}" data-media-start="{a}" data-track-index="6" muted></video>')

# Human-camera rhythm: timed to clause changes, 1.00–1.15 crop range.
# Uneven phrase-led camera rhythm: hold, glide, hard punch and long release.
for selector,at,scale,dur,x,ease in [
 ('#facecam0',0,1.0,0,0,'none'),
 ('#facecam0',2.1,1.13,.09,-12,'power3.out'),
 ('#facecam0',3.3,1.16,1.2,-12,'sine.inOut'),
 ('#facecam0',4.77,1.015,.18,0,'power2.out'),
 ('#facecam0',5.85,1.075,1.2,9,'sine.inOut'),
 ('#facecam0',7.23,1.035,.07,0,'none'),
 ('#facecam0',8.4,1.07,.85,0,'sine.inOut'),
 ('#facecam0',9.43,1.155,.08,-10,'power3.out'),
 ('#facecam0',10.8,1.04,.75,0,'sine.inOut'),
 ('#facecam3',28.55,1.10,0,0,'none'),
 ('#facecam3',29.92,1.025,.55,0,'sine.inOut'),
 ('#facecam3',31.25,1.14,.10,-8,'power3.out'),
 ('#facecam5',43.366667,1.025,0,0,'none'),
 ('#facecam5',43.9,1.105,1.1,8,'sine.inOut')]:
 anim.append(f'tl.to("{selector}",{{scale:{scale},x:{x},duration:{dur},ease:"{ease}"}},{at});')
anim.append('tl.fromTo(".hookcopy",{scale:1,opacity:1},{scale:1.015,opacity:1,duration:.10,ease:"power2.out"},0);tl.to(".hookcopy",{scale:1.015,duration:1.62,ease:"none"},.18);')
# Short internal actions; meaningful state changes remain anchored to narration.
for selector,at,props in [('#s1 .browser',13.55,{'scale':1.06,'y':10}),('#s1 .browser',14.2,{'scale':1,'y':0}),('#s1 .browser',15.7,{'scale':1.10,'y':-20}),('#s1 .browser',16.55,{'scale':1,'y':0}),('#s2 .browser',19.4,{'scale':1.08}),('#s2 .browser',20.3,{'scale':1}),('#s2 .browser',22.2,{'scale':1.07}),('#s2 .browser',23.63,{'scale':1.13,'y':-50}),('#s2 .browser',25.45,{'scale':1,'y':0}),('#s4 .browser',33.65,{'scale':1.08,'y':-10}),('#s4 .browser',34.6,{'scale':1,'y':0}),('#s4 .browser',36.1,{'scale':1.08}),('#s4 .browser',37.5,{'scale':1}),('#s4 .browser',39.45,{'scale':1.08}),('#s4 .browser',42.2,{'scale':1}),('#s6 .coverpage',46.3,{'rotation':-4,'scale':1.06}),('#s6 .coverpage',47.2,{'rotation':2,'scale':1}),('#s6 .paper2',50.1,{'scale':1.08,'y':-18}),('#s6 .paper2',51.35,{'scale':1,'y':0})]:
 anim.append(f'tl.to("{selector}",'+json.dumps({**props,'duration':.22,'ease':'power2.out'})+f',{at});')
anim += [
 'tl.fromTo("#s1 .player",{scale:.75,rotation:-3},{scale:1,rotation:0,duration:.35},12.9);',
 'tl.fromTo("#s1 .lesson-row",{x:80,opacity:0},{x:0,opacity:1,duration:.2,stagger:.25},13.4);',
 'tl.fromTo("#s1 .project-state .sheet-lines i",{scaleX:0},{scaleX:1,duration:.2,stagger:.12,transformOrigin:"left"},17.6);',
 'tl.fromTo("#s2 .tile",{x:160,rotation:15,opacity:0},{x:0,rotation:0,opacity:1,duration:.35,stagger:.18},18.85);',
 'tl.to("#s2 .tile:first-child",{scale:1.1,y:-18,duration:.18},20.5);',
 'tl.to("#s2 .result-card",{scale:1.18,x:-30,duration:.25},20.85);',
 'tl.fromTo("#s2 .newinput",{x:45},{x:0,duration:.07,yoyo:true,repeat:5},24.3);',
 'tl.fromTo("#s2 .errorline",{x:-22},{x:0,duration:.06,yoyo:true,repeat:5},26.88);',
 'tl.fromTo("#s4 .terminal",{y:75,opacity:0},{y:0,opacity:1,duration:.25},32.95);',
 'tl.fromTo("#s4 .code-row",{scaleX:0},{scaleX:1,duration:.25,stagger:.3,transformOrigin:"left"},33.3);',
 'tl.to("#s4 .code-row:nth-child(2)",{backgroundColor:"#df707e",x:8,duration:.08,yoyo:true,repeat:3},34.4);',
 'tl.fromTo("#s4 .fixedline",{scaleX:0},{scaleX:1,duration:.25,transformOrigin:"left"},37.8);',
 'tl.to("#s4 .code-row:nth-child(2)",{opacity:0,duration:.1},37.8);',
 'tl.fromTo("#s4 .checkbig",{scale:.1,rotation:-50},{scale:1,rotation:0,duration:.25,ease:"back.out(1.5)"},39.45);',
 'tl.fromTo("#s4 .successbox .sheet-lines i",{scaleX:0},{scaleX:1,duration:.25,stagger:.17,transformOrigin:"left"},41.9);',
 'tl.fromTo("#s6 .paper2 .rule",{scaleX:0},{scaleX:1,duration:.22,stagger:.14,transformOrigin:"left"},49.3);',
 'tl.fromTo("#s7 .ig-sheet",{y:140},{y:0,duration:.25,ease:"power2.out"},52.54);',
 'tl.fromTo("#s7 .ig-caret",{opacity:1},{opacity:0,duration:.25,yoyo:true,repeat:3},52.65);',
 'tl.set("#s7 .ig-caret",{opacity:0},53.6);'
]

# v5 head copy: overhead, no dimming or face obstruction.
css += '.introhook{background:none;pointer-events:none}.hookcopy{top:60px;left:65px;right:65px;font-size:86px;line-height:1.05;letter-spacing:-3px;-webkit-text-stroke:4px #182022}.hookcopy span:first-child{color:white}.hookcopy span:last-child{font-size:100px;margin-top:12px}.hookcopy b{color:#ff515a}.caption.school-cap{top:1490px;font-size:62px}'
css += '@font-face{font-family:HeadlineBlack;src:url(assets/Pretendard-Black.ttf);font-weight:900}.hookcopy{font-family:HeadlineBlack;top:470px;left:75px;right:75px;font-size:122px;line-height:1.10;letter-spacing:-5px;-webkit-text-stroke:10px #0b0b0b;color:#fff;text-shadow:0 7px 0 #0b0b0b,0 10px 14px #0005}.hookcopy span:first-child,.hookcopy b{color:#fff}.hookcopy span:last-child{font-size:170px;margin-top:5px;letter-spacing:-5px}.hookline{opacity:1}.caption .accent{background:none;border-radius:0;padding:0;-webkit-text-stroke:5px #202127}'
# House structure transforms into a cafe below the narration; then AI school takes the frame.
css += '.renovation{position:absolute;left:320px;top:1160px;width:440px;height:420px;z-index:42;filter:drop-shadow(0 15px 12px #0007)}.building{position:absolute;left:65px;top:70px;width:310px;height:290px;background:linear-gradient(110deg,#ffe0a0,#e5aa69);border-radius:9px;box-shadow:15px 12px 0 #9d634c}.roof{position:absolute;left:25px;top:2px;border-left:195px solid transparent;border-right:195px solid transparent;border-bottom:90px solid #ba605c;filter:drop-shadow(0 7px 0 #793c45)}.house-window{position:absolute;width:70px;height:65px;top:105px;background:#76c5d4;border:10px solid #fff0c4;border-radius:5px;left:105px}.house-window.right{left:265px}.pillar{position:absolute;top:193px;left:104px;width:20px;height:145px;background:#efdeb3;box-shadow:6px 2px 0 #b6a57d}.pillar.right{left:316px}.door{position:absolute;left:187px;top:238px;width:68px;height:120px;background:#6496a9;border:10px solid #f9e6b0;border-bottom:none}.awning{position:absolute;left:50px;top:200px;width:340px;height:55px;background:repeating-linear-gradient(90deg,#74bea1 0 43px,#fff0cc 43px 86px);border-radius:5px 5px 20px 20px;transform-origin:left;box-shadow:0 8px 6px #0003}.cafe-sign{position:absolute;left:160px;top:156px;width:120px;padding:8px 0;border-radius:8px;background:#285951;color:#fff7df;font-size:29px;text-align:center}.coffee-accent{position:absolute;left:325px;top:253px;width:130px;height:130px}.school-reveal{position:absolute;inset:0;z-index:18;background:radial-gradient(ellipse at 50% 42%,#27555c,#0b1e2c 68%)}.school-art{position:absolute;left:380px;top:640px;width:320px;height:320px;filter:drop-shadow(0 24px 26px #0007)}.school-label{position:absolute;top:1040px;left:100px;right:100px;text-align:center;font-size:100px;font-weight:900;color:white;letter-spacing:-4px}.school-label b{color:#ff515a}.learning-node{position:absolute;width:150px;height:140px;border:2px solid #9cf0d680;border-radius:28px;background:#214c54;display:flex;align-items:center;justify-content:center;color:#b1f3d7;font-size:65px;box-shadow:0 20px 50px #0003}.node-video{left:150px;top:550px}.node-code{left:780px;top:630px}.node-check{left:465px;top:340px}.learning-link{position:absolute;left:265px;top:610px;width:550px;height:2px;background:#8de5ca70;transform:rotate(12deg);transform-origin:left}.learning-link.second{left:540px;top:460px;width:300px;transform:rotate(90deg)}'
parts.append('<div id="renovation" class="clip renovation" data-start="7.226667" data-duration="3.58" data-track-index="13"><div class="building"></div><div class="roof"></div><div class="house-window"></div><div class="house-window right"></div><div class="pillar"></div><div class="pillar right"></div><div class="door"></div><div class="awning"></div><div class="cafe-sign">카페</div><img class="coffee-accent" src="assets/stickers/fluent-hot-beverage-3d.png" alt=""></div>')
parts.append('<div id="school-reveal" class="clip school-reveal" data-start="10.806667" data-duration="1.96" data-track-index="8"><div class="learning-link"></div><div class="learning-link second"></div><div class="learning-node node-video">▶</div><div class="learning-node node-code">&lt;/&gt;</div><div class="learning-node node-check">✓</div><img class="school-art" src="assets/stickers/fluent-school-3d.png" alt=""><div class="school-label"><b>AI</b> 학교</div></div>')
anim += [
 'tl.fromTo("#renovation",{scale:.65,y:55,opacity:0},{scale:1,y:0,opacity:1,duration:.3,ease:"back.out(1.4)"},7.226667);',
 'tl.to("#renovation",{scale:1.06,duration:.55},8.366667);',
 'tl.to(".pillar",{y:100,x:-40,rotation:22,opacity:0,duration:.25,stagger:.08},9.426667);',
 'tl.to(".house-window",{opacity:0,scale:.7,duration:.15},9.48);',
 'tl.to(".roof",{y:78,duration:.3,ease:"power2.inOut"},9.48);',
 'tl.to(".building",{scaleY:.73,transformOrigin:"bottom",duration:.3},9.48);',
 'tl.fromTo(".awning",{scaleX:0,opacity:0},{scaleX:1,opacity:1,duration:.22},9.7);',
 'tl.fromTo(".cafe-sign",{scale:.4,opacity:0},{scale:1,opacity:1,duration:.2,ease:"back.out(1.4)"},9.88);',
 'tl.fromTo(".coffee-accent",{scale:0,rotation:-18},{scale:1,rotation:0,duration:.25,ease:"back.out(1.5)"},10.0);',
 'tl.to("#renovation",{scale:.9,opacity:0,duration:.1},10.706667);tl.set("#renovation",{opacity:0},10.806667);',
 'tl.fromTo(".school-art",{scale:.6,y:100,opacity:0},{scale:1,y:0,opacity:1,duration:.3,ease:"back.out(1.3)"},10.806667);',
 'tl.fromTo(".school-label",{y:35,opacity:0},{y:0,opacity:1,duration:.2},10.94);',
 'tl.fromTo(".learning-link",{scaleX:0},{scaleX:1,duration:.25,stagger:.1},11.08);',
 'tl.fromTo(".learning-node",{scale:.3,opacity:0,rotation:-10},{scale:1,opacity:1,rotation:0,duration:.23,stagger:.15,ease:"back.out(1.2)"},11.18);',
 'tl.to(".school-art",{scale:1.1,y:-12,duration:.6,ease:"sine.inOut"},11.6);',
 'tl.to(".node-check",{scale:1.13,duration:.15,yoyo:true,repeat:1},12.05);'
]

# Contextual accent stickers stay below the talking-head captions.
for ident,asset,a,b,kind in [
 ('school-sticker','fluent-graduation-cap-3d.png',3.24,4.62,'school'),
 ('money-sticker','fluent-money-bag-3d.png',31.253333,32.8,'money'),
 ('thinking-sticker','fluent-thinking-face-3d.png',43.9,45.32,'thinking')]:
 parts.append(f'<div id="{ident}" class="clip sticker" data-start="{a}" data-duration="{b-a}" data-track-index="12"><img src="assets/stickers/{asset}" alt=""></div>')
 anim.append(f'tl.fromTo("#{ident} img",{{scale:.35,y:45,rotation:-12,opacity:0}},{{scale:1,y:0,rotation:0,opacity:1,duration:.22,ease:"back.out(1.5)"}},{a});')
 if kind=='money':
  anim.append(f'tl.to("#{ident} img",{{rotation:9,y:-12,duration:.10,yoyo:true,repeat:3,ease:"sine.inOut"}},{a+.24});')
  anim.append(f'tl.to("#{ident} img",{{y:18,rotation:-8,duration:.38,ease:"power1.in"}},{a+.8});')
 elif kind=='thinking':
  anim.append(f'tl.to("#{ident} img",{{rotation:9,x:12,duration:.7,ease:"sine.inOut"}},{a+.3});')
 else:
  anim.append(f'tl.to("#{ident} img",{{y:-14,rotation:-4,duration:.8,ease:"sine.inOut"}},{a+.25});')
 anim.append(f'tl.to("#{ident} img",{{scale:.75,opacity:0,y:25,duration:.12}},{b-.12});tl.set("#{ident} img",{{opacity:0}},{b});')

def emphasize(text):
 escaped=html.escape(text)
 for term in sorted(plan['caption_emphasis'],key=len,reverse=True):
  if term in text:
   escaped=escaped.replace(html.escape(term),'<span class="accent">'+html.escape(term)+'</span>',1)
   break
 return escaped
css += '.caption .accent{color:#ff515a}.caption.face-cap{top:1030px;font-size:64px}.caption{white-space:nowrap}.sticker{position:absolute;left:425px;top:1170px;width:230px;height:230px;z-index:42}.sticker img{width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 10px 8px #0006)}'
for j,c in enumerate(plan['captions']):
 for i,(a,b,k,_) in enumerate(scenes):
  st=max(a,c['start'],0);en=min(b,c['end'])
  if en-st < 1/30:continue
  cl=('school-cap' if st>=10.806666 and en<=12.766668 else 'face-cap') if k=='face' else ('cta-cap' if k=='comment' else '')
  parts.append(f'<div id="cap{j}_{i}" class="clip caption {cl}" data-start="{st}" data-duration="{en-st}" data-track-index="10">{emphasize(c["text"])}</div>')
parts.append('<div id="cover" class="clip introhook" data-start="0" data-duration="2" data-track-index="20"><div class="hookcopy"><span class="hookline">AI에 미친자가</span><span class="hookline">저지른 일</span></div></div>')
parts.append(f'<audio id="mix" src="assets/mix.wav" data-start="0" data-duration="{D}" data-track-index="0"></audio>')

CUT_A=plan['frame_cut']['remove_start_frame']/plan['frame_cut']['fps'];CUT_B=plan['frame_cut']['remove_end_frame']/plan['frame_cut']['fps'];DELTA=CUT_B-CUT_A
def mapped(t):return t if t<=CUT_A else (CUT_A if t<CUT_B else t-DELTA)
def retime_tag(match):
 tag=match.group(0);a=re.search(r'data-start="([0-9.]+)"',tag);d=re.search(r'data-duration="([0-9.]+)"',tag)
 if not a:return tag
 old=float(a.group(1));tag=re.sub(r'data-start="[0-9.]+"',f'data-start="{mapped(old):.8f}"',tag)
 if d:tag=re.sub(r'data-duration="[0-9.]+"',f'data-duration="{mapped(old+float(d.group(1)))-mapped(old):.8f}"',tag)
 tag=re.sub(r'data-media-start="([0-9.]+)"',lambda m:f'data-media-start="{mapped(float(m.group(1))):.8f}"',tag)
 return tag
parts=[re.sub(r'<[^>]+data-start="[^>]+>',retime_tag,x)for x in parts]
# Remove zero-duration captions collapsed into the deleted attempt.
parts=[x for x in parts if 'data-duration="0.00000000"' not in x]
anim=[re.sub(r',([0-9]+(?:\.[0-9]+)?)\);',lambda m:f',{mapped(float(m.group(1))):.8f});',x)for x in anim]
D=plan['output_duration']
import math
for part in parts:
 if 'class="clip caption ' not in part and 'class="clip introhook"' not in part:continue
 ident=re.search(r'id="([^"]+)"',part).group(1)
 st=float(re.search(r'data-start="([^"]+)"',part).group(1))
 dur=float(re.search(r'data-duration="([^"]+)"',part).group(1))
 start_frame=math.ceil(st*30-1e-5);end_frame=math.ceil((st+dur)*30-1e-5)
 if ident=='cover':
  anim.append('tl.set("#cover",{opacity:0},2);')
  continue
 anim.append(f'tl.set("#{ident}",{{opacity:0}},0);tl.set("#{ident}",{{opacity:1}},{start_frame/30:.8f});tl.set("#{ident}",{{opacity:0}},{end_frame/30:.8f});')


page=f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>AI 학교 · 1번 수정본</title><script src="assets/gsap.min.js"></script><style>{css}</style></head><body><div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-duration="{D}">{"".join(parts)}</div><script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});{"".join(anim)}window.__timelines.main=tl;</script></body></html>'
(P/'index.html').write_text(page)
(R/'scene-plan.json').write_text(json.dumps({'duration':D,'scenes':[{'start':mapped(a),'end':mapped(b),'source_start':a,'source_end':b,'kind':k,'theme':t}for a,b,k,t in scenes],'fixed_headline':{'text':'AI에 미친자가 저지른 일','start':0,'duration':2},'retake_remove_source':[CUT_A,CUT_B],'removed':['Editorial tag/title/subheadline blocks','House and AI-school building icons','Percentage counter','Money receipt illustration','Repeated output cards and workflow summary'],'visual_status':'UI action illustrations tied to speech; not real application screenshots or exact original assets','source_reference':'Db5Ux9ZP0Br','reference_limits':'Specific editing adaptation, not verified full reference match'},ensure_ascii=False,indent=2))
print('Built v10: fixed 2s hook, action motion, subject poses, Instagram comments; 67-frame retake removed.')

output=P/"index.html"
output.write_text(output.read_text().replace("</style>","#cover{display:none!important}</style>"))

# Latest user instruction: no separate intro; fixed 1s two-line POV head on live footage.
output=P/"index.html"
s=output.read_text()
s=s.replace("</style>", ".pov-head{position:absolute;z-index:100;left:38px;right:38px;top:360px;text-align:center;font-family:P;font-weight:900;font-size:122px;line-height:1.16;letter-spacing:-4px;color:white;-webkit-text-stroke:7px #080808;paint-order:stroke fill;text-shadow:0 7px 7px #000,0 0 24px #000}.pov-head div{white-space:nowrap;font:inherit}</style>")
s=s.replace("</body>",'<div id="pov-head" class="pov-head"><div>POV: AI 미친자가</div><div>저지른 일</div></div><script>window.__timelines.main.set("#pov-head",{opacity:1},0);window.__timelines.main.set("#pov-head",{opacity:0},1);</script></body>')
output.write_text(s)

output=P/"index.html"
output.write_text(output.read_text().replace("</style>",".caption,.caption span{text-shadow:0 5px 6px #000,0 0 12px #000e!important}</style>"))
