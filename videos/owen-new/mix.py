#!/usr/bin/env python3
"""Pre-mix voice + music bed + SFX into assets/mix.m4a (reference loudness ≈ -14 LUFS).
Sounds: ../../../../projects/cutback/videos/_assets/audio-eleven-20260920 (in-house Lazy Owen library, ElevenLabs-generated).
Bed is ducked under voice with sidechain compression; SFX are placed on scene changes."""
import os, subprocess, json
ROOT = os.path.dirname(os.path.abspath(__file__))
LIB = "/Users/apple/orca/projects/cutback/videos/_assets/audio-eleven-20260920"
DUR = json.load(open(os.path.join(ROOT, "cuts.json")))["duration"]

SFX = [  # (time, file, gain_dB)
    (0.00, "impact-low-hook", -6),
    (1.58, "whoosh-short-cut", -8), *[(2.08 + i * .14, "soft-pop", -10) for i in range(5)],
    (3.78, "soft-pop", -4), (3.78, "whoosh-short-cut", -10),
    (6.06, "whoosh-up-cut", -9), (7.62, "ui-panel-appear", -8), (10.08, "whoosh-short-cut", -12),
    (12.18, "whoosh-up-cut", -9), (13.72, "ui-panel-appear", -8), (16.67, "ui-tick", -6), (17.57, "ui-tick", -6),
    (18.14, "whoosh-down-cut", -10), (20.82, "whoosh-short-cut", -12),
    (22.06, "whoosh-up-cut", -9), (23.82, "ui-panel-appear", -8), (25.72, "ui-tick", -4), (28.27, "soft-pop", -6),
    (29.60, "whoosh-up-cut", -9), (30.98, "ui-panel-appear", -8), (32.43, "ui-tick", -6), (34.68, "soft-pop", -6),
    (35.00, "whoosh-short-cut", -12), (36.52, "whoosh-up-cut", -9), (38.20, "impact-low-hook", -10),
    (39.80, "whoosh-short-cut", -9), (42.87, "whoosh-down-cut", -8),
    (44.02, "ui-panel-appear", -8), *[(44.32 + i * .2, "ui-tick", -7) for i in range(5)],
    (46.28, "ping-comment", -6),
]
inputs = ["-i", os.path.join(ROOT, "assets/voice.m4a"), "-stream_loop", "-1", "-i", os.path.join(LIB, "bed-ambient-tech-33s.wav")]
for _, f, _ in SFX:
    inputs += ["-i", os.path.join(LIB, f + ".wav")]
fc = ["[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[voice][sc]",
      f"[1:a]atrim=0:{DUR},aformat=sample_rates=48000:channel_layouts=stereo,volume=-2dB,afade=t=in:d=0.8,afade=t=out:st={DUR-1.5}:d=1.5[bed0]",
      "[bed0][sc]sidechaincompress=threshold=0.1:ratio=2:attack=20:release=300[bed]"]
labels = []
for i, (t, _, g) in enumerate(SFX):
    fc.append(f"[{i+2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={int(t*1000)}|{int(t*1000)}[s{i}]")
    labels.append(f"[s{i}]")
fc.append(f"[voice][bed]{''.join(labels)}amix=inputs={2+len(SFX)}:normalize=0:duration=first[m]")
fc.append("[m]loudnorm=I=-14:TP=-1.0:LRA=7[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[out]",
                "-t", str(DUR), "-ar", "48000", "-c:a", "aac", "-b:a", "256k", os.path.join(ROOT, "assets/mix.m4a")], check=True)
print("wrote assets/mix.m4a with", len(SFX), "sfx")
