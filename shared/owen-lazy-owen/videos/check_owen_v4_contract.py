#!/usr/bin/env python3
"""Check retained editorial inputs and the shared visual/audio timeline."""
import argparse
import ast
import hashlib
import json
import re
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def captions(path):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == 'C_SRC'
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError(f'Missing literal source captions: {path}')


parser = argparse.ArgumentParser()
parser.add_argument('original', type=Path)
parser.add_argument('revised', type=Path)
args = parser.parse_args()
old, new = args.original.resolve(), args.revised.resolve()
cuts = json.loads((new / 'cuts.json').read_text())
raw = (new / 'events.json').read_bytes()
events = json.loads(raw)
mix = json.loads((new / 'qc/audio/mix-report.json').read_text())


def output_time(source):
    for segment in cuts['segments']:
        if source < segment['src_start']:
            return segment['out_start']
        if source <= segment['src_end']:
            return round(segment['out_start'] + source - segment['src_start'], 3)
    return cuts['duration']


checks = {
    'cuts_identical': digest(old / 'cuts.json') == digest(new / 'cuts.json'),
    'source_captions_identical': captions(old / 'build.py') == captions(new / 'build.py'),
    'voice_identical': digest(old / 'assets/voice.m4a') == digest(new / 'assets/voice.m4a'),
    'presenter_identical': digest(old / 'assets/person.mp4') == digest(new / 'assets/person.mp4'),
    'mix_is_new_file': not (new / 'assets/mix.m4a').is_symlink(),
    'mix_differs_from_original': digest(old / 'assets/mix.m4a') != digest(new / 'assets/mix.m4a'),
    'event_audio_hash_matches': hashlib.sha256(raw).hexdigest() == mix['events_sha256'],
    'cue_count_matches': len(events['actions']) == mix['cue_count'],
}
font_paths = set(re.findall(r"assets/fonts/[^\s\)\"']+", (new / 'index.html').read_text()))
checks['declared_font_files_exist'] = bool(font_paths) and all((new / path).is_file() for path in font_paths)
failures = []
names = set()
for action in events['actions']:
    name = action['name']
    if name in names:
        failures.append([name, 'duplicate name'])
    names.add(name)
    if not 0 <= action['time'] < cuts['duration']:
        failures.append([name, 'outside video'])
    if action['scene'] == 'main':
        continue
    start, duration, *_ = events['scenes'][action['scene']]
    if not 0 <= action['local'] < duration:
        failures.append([name, 'outside scene'])
    if abs(start + action['local'] - action['time']) > .002:
        failures.append([name, 'local/output mismatch'])
    if action.get('source') is not None and abs(output_time(action['source']) - action['time']) > .002:
        failures.append([name, 'source/output mismatch'])
checks['event_timing_valid'] = not failures
report = {'checks': checks, 'event_failures': failures, 'actions': len(names),
          'scope': 'Input identity and timing only; does not establish visual quality or human listening.'}
(new / 'qc/parent-contract.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
raise SystemExit(0 if all(checks.values()) else 1)
