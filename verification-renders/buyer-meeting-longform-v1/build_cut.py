from pathlib import Path
import json,re,math,subprocess,concurrent.futures
r=Path(__file__).resolve().parent;src=Path('/Users/apple/Downloads/원본_온라인 오프라인 바이어 미팅 노하우.mp4');fps=25
trans=json.loads((r/'transcript.json').read_text());words=[w for s in trans['segments'] for w in s.get('words',[]) if w['end']>w['start']]
dur=float(json.loads((r/'source-probe.json').read_text())['format']['duration']);log=(r/'qa/silence-safe.log').read_text();starts=list(map(float,re.findall(r'silence_start: ([\d.]+)',log)));ends=list(map(float,re.findall(r'silence_end: ([\d.]+)',log)))
if len(ends)<len(starts):ends.append(dur)
removed=[]
for a,b in zip(starts,ends):
 if b-a<.25:continue
 # Energy threshold is 18.5 dB below mean speech; leave 100 ms at each pause.
 # Whisper word spans often include the pause itself, so use measured quiet spans.
 l=a+.045;h=b-.055
 if h-l>.12:removed.append([math.ceil(l*fps)/fps,math.floor(h*fps)/fps,'below -42 dB pause; retain 100ms edge safety'])
if (r/'manual-removals.json').exists():removed+=json.loads((r/'manual-removals.json').read_text())
removed.sort();merged=[]
for a,b,why in removed:
 if b<=a:continue
 if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
 else:merged.append([a,b,why])
clips=[];cur=0;of=0
for a,b,_ in merged+[[math.floor(dur*fps)/fps,dur,'end']]:
 sf=round(cur*fps);ef=round(a*fps)
 if ef>sf:
  n=ef-sf;clips.append({'source_start':sf/fps,'source_end':ef/fps,'start':of/fps,'duration':n/fps,'frames':n});of+=n
 cur=b
plan={'source':str(src),'fps':fps,'source_duration':dur,'duration':of/fps,'frames':of,'removed':merged,'clips':clips}
(r/'edit-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
print('PLAN',len(clips),'clips',of/fps,'seconds',flush=True)
parts=r/'parts-tight';parts.mkdir(exist_ok=True)
def render(it):
 i,c=it;o=parts/f'{i:04}-{round(c["source_start"]*25)}-{c["frames"]}.mov'
 if o.exists():return o
 d=c['duration'];cmd=['ffmpeg','-y','-v','error','-ss',str(c['source_start']),'-i',str(src),'-t',str(d),'-map','0:v:0','-map','0:a:0','-vf','setpts=PTS-STARTPTS','-af',f'apad,atrim=duration={d},asetpts=PTS-STARTPTS,afade=t=in:d=0.004,afade=t=out:st={max(0,d-.004)}:d=0.004','-r','25','-c:v','h264_videotoolbox','-b:v','7M','-c:a','pcm_s16le',str(o)];subprocess.run(cmd,check=True,stderr=open(r/'qa'/f'cut-{i}.log','w'));return o
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:paths=list(pool.map(render,enumerate(clips)))
(r/'concat.txt').write_text(''.join("file '"+str(x)+"'\n" for x in paths))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(r/'concat.txt'),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(r/'cut-base.mp4')],check=True)
print('CUT_READY',flush=True)
