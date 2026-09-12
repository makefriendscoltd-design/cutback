import pathlib,json,time,os,subprocess
r=pathlib.Path(__file__).resolve().parent
while '"output":' not in (r/'render.log').read_text():time.sleep(3)
p=json.load(open(r/'edit-plan.json'))
for i,x in enumerate(p['clips']):
 a=r/'parts'/f'{i:03}.mov';b=r/'parts'/f'src-{round(x["source_start"]*p["fps"])}-{x["frames"]}.mov'
 if not b.exists():os.link(a,b)
subprocess.run(['python3',str(r/'build-final.py')],check=True)
