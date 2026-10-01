#!/usr/bin/env python3
"""Serialize local GPU renders; authoring and source review may run concurrently."""
import argparse,fcntl,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--output',required=True);p.add_argument('--version',default='0.8.103');a=p.parse_args()
r=Path(a.project).resolve();lock=Path(tempfile.gettempdir())/'owen-hyperframes-render.lock'
with lock.open('w') as f:
 print('Waiting for local render slot',flush=True);fcntl.flock(f,fcntl.LOCK_EX)
 print('Rendering '+r.name,flush=True)
 subprocess.run(['npx','--yes','hyperframes@'+a.version,'render','--quality','looks','--fps','30','--workers','2','--output',a.output],cwd=r,check=True)
