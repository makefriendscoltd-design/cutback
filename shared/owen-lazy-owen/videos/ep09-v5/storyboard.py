# EP09 — concrete AI staff workflow, source seconds only.
hook(1.20,4.70,'이 일엔 무슨 AI?','업무별로 딱 골라줌')
hire_badge('s02-hire',4.70,9.00,'AI Staff','ROLE ROUTER')
presenter('s03-fatigue',9.00,11.96)

shot('s04-claude',11.96,15.90,'claude.png','claude.ai',[(11.96,540,960,.50,0),(13.05,560,1010,.86,.75)],
 [('claude_title',180,920,760,180,False)],
 extra='<div class="draft">기획안 초안 작성 중<span></span><span></span><span></span></div>',
 extra_css='.draft{position:absolute;right:28px;bottom:28px;width:365px;padding:20px;background:#fff;color:#183047;border-radius:16px;font-size:25px;font-weight:800}.draft span{display:block;height:9px;background:#dbe4ec;margin-top:12px;border-radius:8px}',
 extra_js="tl.fromTo('.draft span',{scaleX:0,transformOrigin:'0 50%'},{scaleX:1,stagger:.17,duration:.3},@draft_type);",
 cues={'claude_title':(12.88,'ui-tick',-11),'draft_type':(14.10,'ui-tick',-12)})

shot('s05-design',15.90,18.88,'claude-design.png','claude.ai/design',[(15.90,540,380,.48,0),(16.55,585,225,.92,.55)],
 [('design_title',230,160,710,130,False)],cues={'design_title':(17.44,'ui-tick',-11)})

prototype='''<div class="proto"><div class="protohead">CLAUDE DESIGN <b>PREVIEW</b></div><div class="form"><label>프로젝트 이름<input value="신제품 소개 페이지"></label><label>설명<input value="버튼을 눌러 결과 확인"></label><button>시제품 만들기</button></div><div class="page"><small>LIVE PROTOTYPE</small><h2>신제품을 만나보세요</h2><button>지금 확인하기</button><em>✓ 클릭 가능</em></div></div>'''
prototype_css='.proto{position:absolute;left:90px;top:340px;width:900px;height:825px;background:#f7f4ed;color:#172538;border-radius:30px;padding:38px;box-shadow:0 35px 90px #0009}.protohead{font:26px JetBrains Mono;border-bottom:2px solid #d6d0c5;padding-bottom:22px}.protohead b{float:right;color:#257a93}.form{padding:34px 16px}.form label{display:block;font-size:26px;margin-bottom:24px}.form input{display:block;width:100%;margin-top:9px;padding:17px;border:2px solid #b9c5cd;border-radius:11px;font-size:25px;background:#fff}.form button,.page button{background:#1e708a;color:#fff;border:0;border-radius:12px;padding:18px 30px;font-size:28px}.page{position:absolute;inset:28px;background:#fff;border-radius:22px;padding:62px;text-align:center}.page small{font:21px JetBrains Mono;color:#39788c}.page h2{font:62px Nanum Myeongjo;margin:100px 0 55px}.page em{display:block;color:#24704f;font-size:23px;margin-top:35px}'
prototype_js="tl.set('.page',{opacity:0,scale:.94},0);tl.to('.form button',{scale:.9,duration:.12},@proto_click);tl.to('.page',{opacity:1,scale:1,duration:.38,ease:'back.out(1.4)'},@proto_click+.14);tl.fromTo('.page em',{opacity:0,y:15},{opacity:1,y:0,duration:.25},@proto_live);"
add('s06-prototype',18.88,21.82,prototype,prototype_css,prototype_js,'hide',{'proto_click':(20.18,'soft-pop',-9),'proto_live':(20.75,'soft-pop',-10)})

shot('s07-perplexity',21.82,25.08,'perplexity-council.png','perplexity.ai/model-council',[(21.82,540,380,.48,0),(22.45,650,305,.92,.65)],
 [('council_title',300,155,720,315,False)],cues={'council_title':(23.04,'ui-tick',-11)})

council='''<div class="council"><header>MODEL COUNCIL <span>같은 질문</span></header><div class="question">“이 기획안에서 가장 먼저 고칠 점은?”</div><div class="drafts"><article><b>MODEL 01</b><h3>고객 문제부터 선명하게</h3><p>첫 문단에서 누구의 어떤 문제인지 먼저 보여주세요.</p></article><article><b>MODEL 02</b><h3>증거를 앞쪽으로 이동</h3><p>사례와 결과를 주장 바로 다음에 배치하세요.</p></article><article><b>MODEL 03</b><h3>행동 단계를 하나로</h3><p>마지막 요청을 한 문장과 한 버튼으로 줄이세요.</p></article></div><footer>세 답변을 나란히 비교</footer></div>'''
council_css='.council{position:absolute;left:70px;top:340px;width:940px;height:825px;background:#fbfaf7;color:#13253a;border-radius:28px;padding:35px}.council header{font:25px JetBrains Mono}.council header span{float:right;color:#277a92}.question{font-size:34px;font-weight:800;margin:32px 0;padding:24px;background:#e7f1f4;border-radius:14px}.drafts{display:flex;gap:15px}.drafts article{flex:1;height:410px;padding:24px;background:#fff;border:2px solid #d9e0e4;border-radius:15px}.drafts b{font:18px JetBrains Mono;color:#277a92}.drafts h3{font-size:30px;line-height:1.25;margin:26px 0}.drafts p{font-size:23px;line-height:1.55;color:#4b5b68}.council footer{text-align:center;font-size:30px;font-weight:900;margin-top:28px;color:#226d82}'
council_js="tl.fromTo('.drafts article',{opacity:0,y:35},{opacity:1,y:0,stagger:.22,duration:.3},@answers);tl.fromTo('.council footer',{opacity:0,scale:.8},{opacity:1,scale:1,duration:.3},@compare);"
add('s08-council',25.08,28.40,council,council_css,council_js,'hide',{'answers':(25.35,'ui-panel-appear',-12),'compare':(27.38,'soft-pop',-10)})

shot('s09-fireflies',28.40,30.72,'fireflies-korean.png','fireflies.ai/languages',[(28.40,540,760,.48,0),(29.05,380,745,1.08,.6)],
 [('korean_row',60,700,630,90,False)],cues={'korean_row':(29.25,'ui-tick',-11)})

minutes='''<div class="minutes"><header>FIREFLIES · LIVE MEETING</header><div class="wave">▂▅▃▇▂▆▃▅▂▇▃▆</div><div class="transcript"><p><b>00:18</b> 이번 주에는 상세페이지 초안을 먼저 봅니다.</p><p><b>00:31</b> 디자인 시안은 금요일까지 공유할게요.</p></div><div class="summary"><b>회의록</b><span>① 상세페이지 초안 검토</span><span>② 금요일 디자인 공유</span></div></div>'''
minutes_css='.minutes{position:absolute;left:75px;top:340px;width:930px;height:825px;background:#f8fafb;color:#17283a;border-radius:28px;padding:35px}.minutes header{font:25px JetBrains Mono}.wave{font:68px JetBrains Mono;color:#2b849c;letter-spacing:7px;margin:45px 0}.transcript p{font-size:28px;padding:18px;border-bottom:1px solid #d9e2e7}.transcript b{font:20px JetBrains Mono;color:#2b849c;margin-right:20px}.summary{position:absolute;left:35px;right:35px;bottom:35px;padding:28px;background:#dff1ee;border-radius:17px}.summary b{font-size:32px}.summary span{display:block;font-size:25px;margin-top:14px}'
minutes_js="tl.to('.wave',{scaleX:1.06,duration:.4,ease:'sine.inOut'},0);tl.fromTo('.transcript p',{opacity:0,x:-20},{opacity:1,x:0,stagger:.2,duration:.25},@transcribe);tl.fromTo('.summary',{opacity:0,y:35},{opacity:1,y:0,duration:.35},@minutes);"
add('s10-minutes',30.72,32.14,minutes,minutes_css,minutes_js,'hide',{'transcribe':(30.78,'ui-tick',-12),'minutes':(31.52,'soft-pop',-10)})

shot('s11-canva',32.14,33.32,'canva-ppt.png','canva.com/presentations',[(32.14,540,470,.48,0),(32.36,540,430,.78,.35)],
 [('slide_focus',120,260,840,260,False)],cues={'slide_focus':(32.42,'ui-tick',-11)})
presenter('s12-image',33.32,34.70)
shot('s13-higgsfield',34.70,36.30,'higgsfield-home.png','higgsfield.ai',[(34.70,540,500,.48,0),(34.95,540,390,.72,.45)],
 [('video_focus',120,180,840,300,False)],cues={'video_focus':(35.05,'ui-tick',-11)})

timeline='''<div class="editor"><header>VIDEO PROJECT <span>00:00:04:12</span></header><div class="preview"><div class="image">PRODUCT</div><b>사진과 글이 영상으로</b></div><div class="tracks"><label>VIDEO</label><i></i><i></i><i></i><label>TEXT</label><i class="text"></i><label>AUDIO</label><i class="audio"></i></div><button>▶ PREVIEW</button></div>'''
timeline_css='.editor{position:absolute;left:75px;top:340px;width:930px;height:860px;background:#101722;border-radius:28px;padding:28px}.editor header{font:23px JetBrains Mono}.editor header span{float:right;color:#64d2ff}.preview{height:430px;margin-top:25px;background:linear-gradient(135deg,#203b52,#0c1928);display:grid;place-items:center;border-radius:14px}.preview .image{font:72px Instrument Serif;color:#64d2ff}.preview b{font-size:36px}.tracks{display:grid;grid-template-columns:90px repeat(3,1fr);gap:10px;margin-top:26px}.tracks label{font:17px JetBrains Mono}.tracks i{height:48px;background:#34728b;border-radius:6px}.tracks .text{grid-column:2/5;background:#815f9c}.tracks .audio{grid-column:2/5;background:#39775d}.editor button{position:absolute;right:28px;bottom:24px;padding:14px 23px;background:#64d2ff;border:0;border-radius:9px;font:20px JetBrains Mono}'
timeline_js="tl.fromTo('.tracks i',{scaleX:0,transformOrigin:'0 50%'},{scaleX:1,stagger:.14,duration:.28},@tracks);tl.to('.preview',{scale:1.025,duration:.25,yoyo:true,repeat:1},@preview);"
add('s14-videoeditor',36.30,40.24,timeline,timeline_css,timeline_js,'hide',{'tracks':(36.55,'ui-panel-appear',-12),'preview':(38.30,'soft-pop',-10)})
presenter('s15-guide',40.24,43.68)
hire_badge('s16-book',43.68,45.62,'AI Playbook','E-BOOK')
presenter('s17-ask',45.62,47.58)
comment(47.58,49.94,'전자책')
