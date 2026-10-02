#!/usr/bin/env python3
"""Render approved Owen compositions headlessly, sharing the local GPU lock."""
import argparse
import fcntl
import os
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--project', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--version', default='0.8.107')
args = parser.parse_args()
project = Path(args.project).resolve()
log = project / 'qc' / 'render.log'
log.parent.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, HYPERFRAMES_RENDER_DETACHED='1')
lock = Path(tempfile.gettempdir()) / 'owen-hyperframes-render.lock'
with lock.open('a') as slot:
    print(f'Waiting for render slot: {project.name}', flush=True)
    fcntl.flock(slot, fcntl.LOCK_EX)
    print(f'Rendering {project.name}; log: {log}', flush=True)
    with log.open('w') as output:
        result = subprocess.run([
            'npx', '--yes', f'hyperframes@{args.version}', 'render',
            '--quality', 'looks', '--fps', '30', '--workers', '2',
            '--output', args.output,
        ], cwd=project, env=env, stdout=output, stderr=subprocess.STDOUT)
    print(f'Render exit {result.returncode}: {project / args.output}', flush=True)
    raise SystemExit(result.returncode)
