"""Episode 8 source-specific cuts. Keep every spoken word; shorten measured silence only."""
from pathlib import Path
import json, subprocess

ROOT = Path(__file__).resolve().parent
START, END = 1.16, 82.30
# Candidate gaps are 50 ms RMS valleys cross-checked against raw/VAD word
# boundaries; the CTA boundary uses the independent 70–85 s re-transcription.
GAPS = [(3.360,3.700),(7.180,7.600),(9.040,9.440),(11.560,12.080),
        (21.660,22.000),(26.880,27.440),(28.860,29.340),(34.600,35.140),
        (39.340,39.940),(43.500,44.260),(47.540,48.040),(51.640,52.380),
        (57.860,58.540),(60.540,61.140),(66.400,67.060),(70.040,70.580),
        (76.200,76.880)]
segments, cursor, out_t = [], START, 0.0
for a, b in GAPS + [(END + .06, END + .06)]:
    end = min(a + .06, END)
    if end > cursor:
        d = end - cursor
        segments.append(dict(src_start=round(cursor, 3), src_end=round(end, 3), out_start=round(out_t, 3), out_end=round(out_t + d, 3)))
        out_t += d
    cursor = b - .06
(ROOT / "cuts.json").write_text(json.dumps(dict(segments=segments, duration=round(out_t, 3), gaps=GAPS), indent=2))
filters = []
for i, s in enumerate(segments):
    d = s["src_end"] - s["src_start"]
    filters += [f"[0:v]trim={s['src_start']}:{s['src_end']},setpts=PTS-STARTPTS,fps=30[v{i}]", f"[0:a]atrim={s['src_start']}:{s['src_end']},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={max(0,d-.008):.3f}:d=0.008[a{i}]"]
filters.append("".join(f"[v{i}][a{i}]" for i in range(len(segments))) + f"concat=n={len(segments)}:v=1:a=1[v][a]")
(ROOT / "src/fg.txt").write_text(";".join(filters))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "src/source.mp4"), "-filter_complex_script", str(ROOT / "src/fg.txt"), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", str(ROOT / "src/person_cut.mp4")], check=True)
for name, opts in [("person.mp4", ["-an", "-c:v", "copy"]), ("voice.m4a", ["-vn", "-c:a", "copy"])]:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "src/person_cut.mp4"), *opts, str(ROOT / "assets" / name)], check=True)
print(f"{len(segments)} segments, {out_t:.3f}s")
