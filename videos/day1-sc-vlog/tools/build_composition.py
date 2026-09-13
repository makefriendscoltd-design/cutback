#!/usr/bin/env python3
"""Compatibility entrypoint; reusable implementation lives in the vlog skill."""
from pathlib import Path
import runpy
import sys

job = Path(__file__).resolve().parents[1]
project = Path(__file__).resolve().parents[3]
if '--plan' not in sys.argv:
    sys.argv += ['--plan', str(job / 'edit-plan.json')]
if '--composition' not in sys.argv:
    sys.argv += ['--composition', str(job / 'composition')]
runpy.run_path(str(project / '.agents/skills/vlog-reference-edit/scripts/build_composition.py'), run_name='__main__')
