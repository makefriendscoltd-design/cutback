#!/usr/bin/env python3
"""Resolve the pinned runtime and verify bundled approved font bytes."""
import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--gsap', type=Path, help='Use an existing local runtime instead of downloading; hash still checked')
    args = parser.parse_args()
    fonts = SKILL / 'assets/fonts'
    manifest = json.loads((fonts / 'provenance.json').read_text())
    for item in manifest['fonts']:
        path = fonts / item['file']
        if digest(path.read_bytes()) != item['sha256']:
            raise ValueError('Bundled font hash mismatch: ' + path.name)
    dep = next(x for x in manifest['unbundled_dependencies'] if x['name'] == 'GSAP')
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    target = output / 'gsap.min.js'
    if target.exists():
        data = target.read_bytes()
    elif args.gsap:
        data = args.gsap.expanduser().resolve().read_bytes()
    else:
        with urllib.request.urlopen(dep['url'], timeout=45) as response:
            data = response.read(2_000_000)
    if digest(data) != dep['sha256']:
        raise ValueError('GSAP hash mismatch; existing files were not changed')
    if not target.exists():
        with target.open('xb') as handle:
            handle.write(data)
    print(json.dumps({'font_dir': str(fonts), 'gsap': str(target), 'verified': True}))

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print('resolve_dependencies: ' + str(error), file=sys.stderr)
        sys.exit(2)
