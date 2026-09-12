import pathlib,json,subprocess
r=pathlib.Path(__file__).resolve().parent
p=json.loads((r/'timeline.json').read_text());fps='60000/1001';d=r/'assets/staged';d.mkdir(exist_ok=True)
def run(name,args):
 with (r/(name+'.log')).open('w') as f:subprocess.run(['ffmpeg','-y','-hide_banner',*args],stdout=f,stderr=subprocess.STDOUT,check=True)
def probe(path):
 x=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,duration,r_frame_rate','-of','json',str(path)]))['streams'][0];print(path.name,x,flush=True);return int(x['nb_frames'])
flt="[0:v]format=gbrp,split=2[dark][key];[dark]eq=brightness=-0.022:gamma=0.98,format=gbrp[bg];[key]curves=all='0/0 0.12/0.13 0.35/0.40 0.65/0.70 0.9/0.92 1/1',format=gbrp[light];[1:v]format=gbrp[mask];[bg][light][mask]maskedmerge,format=yuv420p,setpts=N/(60000/1001*TB)[v]"
enc=['-r',fps,'-fps_mode','cfr','-c:v','h264_videotoolbox','-b:v','24M','-pix_fmt','yuv420p']
rel=d/'relit.mp4'
run('staged-relight',['-i',str(r/'assets/presenter-camera.mp4'),'-i',str(r/'assets/relight-mask.png'),'-filter_complex',flt,'-map','[v]','-an','-frames:v','12577',*enc,str(rel)])
assert probe(rel)==12577
sharp=r.parent/'20260911_175145-polish-v4/assets/presenter-sharp.mp4'
for name,start,n in [('pre',0,1303),('post',1348,11229)]:
 sec=start/(60000/1001);dur=n/(60000/1001)
 vf=f'trim=start_frame={start}:end_frame={start+n},setpts=N/(60000/1001*TB)'
 af=f'atrim=start={sec}:end={sec+dur},asetpts=PTS-STARTPTS,apad,atrim=duration={dur}'
 run('staged-'+name,['-i',str(rel),'-i',str(sharp),'-filter_complex',f'[0:v]{vf}[v];[1:a]{af}[a]','-map','[v]','-map','[a]',*enc,'-c:a','pcm_s16le','-ar','48000','-ac','2',str(d/(name+'.mov'))])
 assert probe(d/(name+'.mov'))==n
pd=2979/(60000/1001)
run('staged-promo',['-i',p['promo_path'],'-vf',f'fps={fps},trim=end_frame=2979,setpts=N/(60000/1001*TB)','-af',f'volume=1.258925412,afade=t=in:d=0.02,afade=t=out:st={pd-.12}:d=0.12,apad,atrim=duration={pd}',*enc,'-c:a','pcm_s16le','-ar','48000','-ac','2',str(d/'promo.mov')])
assert probe(d/'promo.mov')==2979
(d/'concat.txt').write_text("file 'pre.mov'\nfile 'promo.mov'\nfile 'post.mov'\n")
out=r/'assets/timeline-base.mp4'
if out.exists():out.rename(r/'assets/timeline-base.failed.mp4')
run('staged-concat',['-f','concat','-safe','0','-i',str(d/'concat.txt'),'-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out)])
assert probe(out)==15511
print('VERIFIED timeline frames',flush=True)
