#!/usr/bin/env python3
"""Bind the delivery inventory to the actual final renders and current QC files."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


deliveries = []
for number in range(7, 13):
    project = ROOT / f'ep{number:02}-v5'
    qc = project / 'qc'
    videos = list((project / 'renders').glob('*v5.mp4'))
    assert len(videos) == 1, (project.name, 'expected one delivery MP4', videos)
    video = videos[0]
    check = json.loads((qc / 'final-check.json').read_text())
    contract = json.loads((qc / 'parent-contract.json').read_text())
    camera = json.loads((qc / 'camera-contract.json').read_text())
    encoded = json.loads((qc / 'render-verification.json').read_text())
    reference = json.loads((qc / 'reference-contract.json').read_text())
    assert all(reference['checks'].values()), (project.name, reference)
    assert json.loads((qc / 'action-verification.json').read_text())['mix_hash_matches']
    assert check['ok'], (project.name, 'HyperFrames check failed')
    assert all(contract['checks'].values()), (project.name, contract)
    assert camera['full_beats'] >= 3 and camera['full_fraction'] >= .25
    assert len(camera['transitions']) >= 6
    assert encoded['decode_errors'] == 0
    for source in [project / 'storyboard.py', project / 'build.py', project / 'index.html', project / 'assets/mix.m4a']:
        assert video.stat().st_mtime >= source.stat().st_mtime, (project.name, 'render predates source', source.name)
    assert (qc / 'render-verification.json').stat().st_mtime >= video.stat().st_mtime, (project.name, 'stale encoded verification')
    for name in ['final-check.json', 'caption-audit.json']:
        assert (qc / name).stat().st_mtime >= (project / 'index.html').stat().st_mtime, (project.name, 'stale composition check', name)
    assert (qc / 'final-contact-sheet.jpg').stat().st_mtime >= video.stat().st_mtime, (project.name, 'stale contact sheet')
    deliveries.append({
        'episode': number,
        'video': str(video.relative_to(ROOT)),
        'duration': encoded['probe']['format']['duration'],
        'bytes': video.stat().st_size,
        'lufs': encoded['audio']['input_i'],
        'true_peak': encoded['audio']['input_tp'],
        'full_seconds': camera['seconds']['full'],
        'full_beats': camera['full_beats'],
        'video_sha256': sha(video),
        'build_sha256': sha(project / 'build.py'),
        'storyboard_sha256': sha(project / 'storyboard.py'),
        'events_sha256': sha(project / 'events.json'),
        'mix_sha256': sha(project / 'assets/mix.m4a'),
        'contact_sheet_sha256': sha(qc / 'final-contact-sheet.jpg'),
        'report': str((project / 'REPORT.md').relative_to(ROOT)),
    })
target = ROOT / 'owen-v5-delivery.json'
target.write_text(json.dumps({'reference': 'ep06-v4', 'deliveries': deliveries,
                             'direct_listening': 'not performed',
                             'video_publishing': 'not performed'}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'episodes': len(deliveries), 'inventory': str(target),
                  'total_bytes': sum(row['bytes'] for row in deliveries)}))
