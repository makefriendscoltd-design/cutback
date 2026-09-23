#!/usr/bin/env python3
"""Tight jump-cut edit: drop intro noise, collapse pauses >0.28s to 0.12s. Writes cuts.json + src/person_cut.mp4."""
import json, subprocess, os
ROOT=os.path.dirname(os.path.abspath(__file__))
START, END = 11.80, 64.56
GAPS=[(17.8,18.3),(19.74,20.14),(21.66,21.96),(24.76,25.28),(26.7,27.0),(31.3,31.7),(35.5,35.98),(37.62,37.92),
      (41.16,41.44),(43.74,44.1),(45.36,45.88),(51.3,51.82),(53.38,54.16),(59.86,60.28)]
PAD=0.06
keep=[]; cur=START
for a,b in GAPS:
    keep.append((round(cur,3), round(a+PAD,3))); cur=b-PAD
keep.append((round(cur,3), END))
t=0; segs=[]
for a,b in keep:
    segs.append({"src_start":a,"src_end":b,"out_start":round(t,3),"out_end":round(t+b-a,3)}); t+=b-a
json.dump({"segments":segs,"duration":round(t,3)},open(os.path.join(ROOT,"cuts.json"),"w"),indent=1)
print(f"{len(segs)} segments, out {t:.2f}s (from {END-START:.2f}s)")
# filtergraph concat with short audio crossfades avoided: use trim+concat, 10ms audio fades at edges to kill clicks
f=[]; n=len(segs)
for i,s in enumerate(segs):
    d=s["src_end"]-s["src_start"]
    f.append(f"[0:v]trim={s['src_start']}:{s['src_end']},setpts=PTS-STARTPTS,fps=30[v{i}]")
    f.append(f"[0:a]atrim={s['src_start']}:{s['src_end']},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{i}]")
f.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[v][a]")
open("/tmp/owen_fg.txt","w").write(";".join(f))
subprocess.run(["ffmpeg","-v","error","-y","-i",os.path.join(ROOT,"src/source.mp4"),"-filter_complex_script","/tmp/owen_fg.txt",
  "-map","[v]","-map","[a]","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
  os.path.join(ROOT,"src/person_cut.mp4")],check=True)
