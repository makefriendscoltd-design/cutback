#!/usr/bin/env python3
"""Episode 11 source-specific cuts. Keep the later complete take and tighten pauses."""
from pathlib import Path
import json, subprocess

ROOT = Path(__file__).resolve().parent
START, END = 3.78, 56.12
# Word boundaries from non-VAD faster-whisper, cross-checked with RMS silence.
# 11.50-13.88 removes the false start "이메일이 보냈는데" and keeps the complete take.
GAPS = [
    (5.90, 6.26), (8.26, 8.80), (11.50, 13.88), (17.88, 18.30),
    (20.20, 20.74), (22.74, 23.20), (25.48, 25.92), (28.16, 28.74),
    (33.38, 33.96), (38.54, 39.20), (42.46, 43.02), (47.16, 47.74),
    (52.28, 52.88),
]
segments, cursor, out_t = [], START, 0.0
for a, b in GAPS + [(END + .06, END + .06)]:
    end = min(a + .06, END)
    if end > cursor:
        d = end - cursor
        segments.append(dict(src_start=round(cursor, 3), src_end=round(end, 3),
                             out_start=round(out_t, 3), out_end=round(out_t + d, 3)))
        out_t += d
    cursor = b - .06
(ROOT / 'cuts.json').write_text(json.dumps({
    'segments': segments, 'duration': round(out_t, 3), 'gaps': GAPS,
    'source_duration': 58.684,
}, indent=2))

filters = []
for i, seg in enumerate(segments):
    d = seg['src_end'] - seg['src_start']
    filters += [
        f"[0:v]trim={seg['src_start']}:{seg['src_end']},setpts=PTS-STARTPTS,fps=30[v{i}]",
        f"[0:a]atrim={seg['src_start']}:{seg['src_end']},asetpts=PTS-STARTPTS,"
        f"afade=t=in:d=0.008,afade=t=out:st={max(0,d-.008):.3f}:d=0.008[a{i}]",
    ]
filters.append(''.join(f'[v{i}][a{i}]' for i in range(len(segments))) +
               f'concat=n={len(segments)}:v=1:a=1[v][a]')
(ROOT / 'src/fg.txt').write_text(';'.join(filters))
subprocess.run([
    'ffmpeg', '-v', 'error', '-y', '-i', str(ROOT / 'src/source.mp4'),
    '-filter_complex_script', str(ROOT / 'src/fg.txt'), '-map', '[v]', '-map', '[a]',
    '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '256k', str(ROOT / 'src/person_cut.mp4')
], check=True)
for name, opts in [('person.mp4', ['-an', '-c:v', 'copy']),
                   ('voice.m4a', ['-vn', '-c:a', 'copy'])]:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(ROOT / 'src/person_cut.mp4'),
                    *opts, str(ROOT / 'assets' / name)], check=True)
print(f'{len(segments)} segments, {out_t:.3f}s from original 58.684s')
