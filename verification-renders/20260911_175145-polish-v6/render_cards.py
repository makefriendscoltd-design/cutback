import pathlib,json,subprocess,concurrent.futures
r=pathlib.Path(__file__).resolve().parent;es=json.loads((r/'photo-events.json').read_text());logs=r/'logs';logs.mkdir(exist_ok=True)
def one(e):
 out=r/'renders'/f'{e["id"]}.mov'
 if not out.exists():
  with open(logs/f'{e["id"]}.log','w') as log:
   subprocess.run(['npx','hyperframes','render',str(r/'cards'/e['id']),'--format','mov','--fps','30','--workers','2','--output',str(out)],stdout=log,stderr=subprocess.STDOUT,check=True)
 webm=out.with_suffix('.webm')
 if not webm.exists():subprocess.run(['ffmpeg','-v','error','-i',str(out),'-c:v','libvpx-vp9','-pix_fmt','yuva420p','-b:v','0','-crf','22','-deadline','good','-cpu-used','4','-auto-alt-ref','0',str(webm)],check=True)
 print(e['id'],'done',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(one,es))
