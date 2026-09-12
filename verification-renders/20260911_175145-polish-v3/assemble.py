import pathlib,json,subprocess
r=pathlib.Path(__file__).resolve().parent
caps=json.loads((r/'captions.json').read_text());ev=json.loads((r/'events.json').read_text())
def ass_time(t):
 n=round(t*100);return f'{n//360000}:{n//6000%60:02d}:{n//100%60:02d}.{n%100:02d}'
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Pretendard,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H60000000,-1,0,0,0,100,100,0,0,1,3,1.5,2,140,140,58,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for c in caps:
 assert len(c['lines'])<=2
 text='\\N'.join(c['lines']).replace('{','').replace('}','')
 ass+=f'Dialogue: 0,{ass_time(c["start"])},{ass_time(c["end"])},Default,,0,0,0,,{{\\q2}}{text}\n'
(r/'captions.ass').write_text(ass)
cmd=['ffmpeg','-y','-hide_banner','-i',str(r/'assets/presenter-sharp.mp4')]
for e in ev:cmd+=['-itsoffset',str(e['start']),'-i',str(r/'renders'/f'{e["id"]}.mov')]
cmd+=['-i',str(r/'assets/soft-pop.wav')]
flt=[];prev='0:v'
for i,e in enumerate(ev,1):
 v=f'ov{i}';flt.append(f'[{prev}][{i}:v]overlay=x={e["x"]}:y={e["y"]}:eof_action=pass:repeatlast=0:format=auto[{v}]');prev=v
flt.append(f'[{prev}]ass={r}/captions.ass:fontsdir={r}/assets,format=yuv420p[v]')
flt.append('[0:a]volume=0.891250938[voice]')
flt.append(f'[{len(ev)+1}:a]asplit={len(ev)}'+''.join(f'[a{i}]' for i in range(len(ev))))
for i,e in enumerate(ev):flt.append(f'[a{i}]volume=0.6,adelay={round(e["start"]*1000)}:all=1[s{i}]')
flt.append('[voice]'+''.join(f'[s{i}]' for i in range(len(ev)))+f'amix=inputs={len(ev)+1}:duration=first:normalize=0,alimiter=limit=0.97:level=disabled:latency=1[a]')
(r/'final-filter.txt').write_text(';\n'.join(flt))
out=pathlib.Path('/Users/apple/Downloads/20260911_175145_선명보정_이미지_자막_v3.mp4')
cmd+=['-filter_complex_script',str(r/'final-filter.txt'),'-map','[v]','-map','[a]','-c:v','h264_videotoolbox','-b:v','24M','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out)]
(r/'assembly-command.json').write_text(json.dumps(cmd,ensure_ascii=False,indent=2))
if '--prepare' not in __import__('sys').argv:
 with open(r/'assembly.log','w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
 print(out,flush=True)
