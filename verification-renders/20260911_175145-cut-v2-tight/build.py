import pathlib,json,re,subprocess,concurrent.futures,math
r=pathlib.Path(__file__).resolve().parent
src=pathlib.Path('/Users/apple/Downloads/20260911_175145_편집본.mp4')
fps=60000/1001; duration=263.079483
# The edit plan is authoritative. All rendered assets derive from it.
remove=[(149.46,150.51,'stumbled onset before 쌓아온; keep completed word'),(0,8.50,'opening preparation'),(259.00,duration,'ending wait'),(205.76,207.58,'abandoned 이미 일하시는; keep 이미 일하고 있는'),(221.69,225.24,'abandoned 변화 앞에서 무엇보다 배워나가길; keep completed retake')]
s=(r/'silence.log').read_text()
a=list(map(float,re.findall(r'silence_start: ([\d.]+)',s)));b=list(map(float,re.findall(r'silence_end: ([\d.]+)',s)))
for x,y in zip(a,b):
 if y-x>=.18:remove.append((x+.02,y-.02,'tight silence cut, retain 40ms phoneme safety only'))
# Remove breath/noise pauses where two source transcripts agree on boundaries.
prior=r.parent/'20260911_175145-cut-v1'
turbo=json.loads((prior/'transcript.json').read_text())['segments']
small=json.loads((prior/'audit-small.json').read_text())['segments']
for left,right in zip(turbo,turbo[1:]):
 if right['start']-left['end']<.25:continue
 le=[x['end'] for x in small if abs(x['end']-left['end'])<.5]
 rs=[x['start'] for x in small if abs(x['start']-right['start'])<.5]
 if not le or not rs:continue
 a=max([left['end']]+le)+.02;b=min([right['start']]+rs)-.03
 if b-a>.10:remove.append((a,b,'speech boundary agreement: remove breath/noise pause'))
remove.sort();merged=[]
for a,b,why in remove:
 if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1]);merged[-1][2]+='; '+why
 else:merged.append([a,b,why])
keep=[];cursor=0
for a,b,why in merged:
 if a>cursor+.02:keep.append([round(cursor*fps),round(a*fps)])
 cursor=max(cursor,b)
if cursor<duration:keep.append([round(cursor*fps),round(duration*fps)])
clips=[];outf=0
for a,b in keep:
 if b>a:
  clips.append(dict(source_start=a/fps,source_end=b/fps,frames=b-a,start=outf/fps,duration=(b-a)/fps));outf+=b-a
plan=dict(source=str(src),fps=fps,source_duration=duration,duration=outf/fps,removed=merged,clips=clips)
(r/'edit-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
# Editable HyperFrames timeline mirrors the authoritative source ranges.
c=r/'composition';c.mkdir(exist_ok=True)
(c/'source.mp4').symlink_to(src) if not (c/'source.mp4').exists() else None
els=[]
for i,x in enumerate(clips):
 attrs=f'data-start="{x["start"]:.9f}" data-duration="{x["duration"]:.9f}" data-media-start="{x["source_start"]:.9f}"'
 els.append(f'<video id="v{i}" class="clip" src="source.mp4" {attrs} data-track-index="0" muted playsinline></video><audio id="a{i}" class="clip" src="source.mp4" {attrs} data-track-index="{i+1}"></audio>')
(c/'index.html').write_text('<!doctype html><html><head><style>html,body{margin:0}video{position:absolute;width:1920px;height:1080px;object-fit:contain}</style></head><body>'+f'<div data-composition-id="cut" data-width="1920" data-height="1080" data-duration="{plan["duration"]:.9f}" style="position:relative;width:1920px;height:1080px">'+''.join(els)+'</div><script src="gsap.min.js"></script><script>window.__timelines={cut:gsap.timeline({paused:true})};</script></body></html>')
(r/'BRIEF.md').write_text('workflow: general-video\nflow: automation\nstoryboard: no\n\nUser requests no empty time between speech. Tighten gaps >=180ms to 40ms phoneme safety, preserve complete syllables and existing retake edits. Preserve framing, voice, sequence, and source. edit-plan.json is the source of truth; composition and physical MP4 derive from it.\n')
parts=r/'parts';parts.mkdir(exist_ok=True)
def render(ix):
 i,x=ix;p=parts/f'src-{round(x["source_start"]*fps)}-{x["frames"]}.mov'
 if p.exists():return p
 cmd=['ffmpeg','-y','-v','error','-ss',str(x['source_start']),'-i',str(src),'-t',str(x['duration']),'-map','0:v:0','-map','0:a:0','-vf','setpts=PTS-STARTPTS','-af','asetpts=PTS-STARTPTS,afade=t=in:d=0.004,afade=t=out:st='+str(max(0,x['duration']-.004))+':d=0.004','-r','60000/1001','-c:v','h264_videotoolbox','-b:v','16M','-pix_fmt','yuv420p','-c:a','pcm_s16le',str(p)]
 subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=open(parts/f'{i:03}.log','w'))
 return p
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for i,p in enumerate(pool.map(render,enumerate(clips))):print(f'{i+1}/{len(clips)}',flush=True)
(r/'concat.txt').write_text(''.join("file '"+str(parts/f'src-{round(x["source_start"]*fps)}-{x["frames"]}.mov')+"'\n" for x in clips))
out=pathlib.Path('/Users/apple/Downloads/20260911_175145_컷편집_v2_타이트.mp4')
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(r/'concat.txt'),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)],check=True)
print(json.dumps(dict(output=str(out),duration=plan['duration'],clips=len(clips)),ensure_ascii=False),flush=True)
