from pathlib import Path
import json,subprocess,concurrent.futures
R=Path(__file__).resolve().parent
E=json.loads((R/'body-retime-edl.json').read_text());T=R/'segments';T.mkdir(exist_ok=True)
assert all(s['speed']==1 and s['output_frames']==s['source_end_frame']-s['source_start_frame'] for s in E['segments'])
def render(item):
 i,s=item;p=T/f'{i:03}.mkv'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(s['source_start_frame']/30),'-t',str(s['output_frames']/30),'-i',str(R/'original-source-52s.mp4'),'-an','-vf','setpts=PTS-STARTPTS,fps=30','-frames:v',str(s['output_frames']),'-c:v','h264_videotoolbox','-b:v','14000k','-pix_fmt','yuv420p',str(p)],check=True);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:files=list(pool.map(render,enumerate(E['segments'])))
cl=R/'concat.txt';cl.write_text(''.join(f"file '{p.resolve()}'\n"for p in files))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(cl),'-i',str(R/'assets/mix.wav'),'-map','0:v','-map','1:a','-vf','setpts=N/(30*TB)','-c:v','h264_videotoolbox','-b:v','14000k','-c:a','aac','-b:a','320k','-movflags','+faststart',str(R/'AI학교_01_자막검정그림자_v19.mp4')],check=True)
