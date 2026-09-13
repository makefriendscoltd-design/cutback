#!/usr/bin/env python3
"""Check a vlog composition, export with the approved profile, verify dimensions."""
import argparse
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--composition', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    composition = args.composition.resolve()
    output = args.output.resolve()
    if not (composition / 'index.html').is_file():
        parser.error('composition/index.html is missing; run build_composition.py first')
    profile = json.loads((Path(__file__).resolve().parents[1] / 'references/production-profile.json').read_text())
    export = profile['export']
    output.parent.mkdir(parents=True, exist_ok=True)
    cli = ['npx', '--yes', 'hyperframes@0.8.36']
    subprocess.run(cli + ['check'], cwd=composition, check=True)
    subprocess.run(cli + ['render', '--quality', export['quality'], '--resolution', export['resolution'],
                         '--fps', str(profile['layout']['fps']), '--output', str(output)], cwd=composition, check=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'quiet', '-show_format', '-show_streams', '-of', 'json', str(output)]))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    if (video['width'], video['height']) != (export['width'], export['height']):
        raise SystemExit('Export dimensions differ from the approved profile')
    num, den = map(int, video['r_frame_rate'].split('/'))
    if abs(num / den - profile['layout']['fps']) > 1e-6:
        raise SystemExit('Export frame rate differs from the approved profile')
    print(json.dumps({'output': str(output), 'width': video['width'], 'height': video['height'],
                      'fps': video['r_frame_rate'], 'duration': probe['format']['duration']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
