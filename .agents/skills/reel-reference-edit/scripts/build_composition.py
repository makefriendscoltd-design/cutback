#!/usr/bin/env python3
"""Build a renderable HyperFrames composition from an edit-manifest scaffold."""
from __future__ import annotations
import argparse, hashlib, html, json, os, re, shutil, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL / "assets/template.html"
FONT_ROOT = SKILL / "assets/fonts"

def fail(message: str): raise RuntimeError(message)
def seconds(stamp: str) -> float:
    h,m,s,ms=map(int,re.split(r"[:,]",stamp)); return h*3600+m*60+s+ms/1000
def parse_srt(path: Path):
    cues=[]
    for block in re.split(r"\r?\n\s*\r?\n",path.read_text(encoding="utf-8-sig").strip()):
        lines=block.splitlines(); timing=next((x for x in lines if "-->" in x),None)
        if not timing: continue
        a,b=[x.strip() for x in timing.split("-->")]; i=lines.index(timing)
        cues.append({"start":seconds(a),"end":seconds(b),"text":" ".join(lines[i+1:]).strip()})
    if not cues: fail(f"no readable SRT cues: {path}")
    return cues
def srt_stamp(value: float) -> str:
    ms=round(value*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
def link(src: Path,dst: Path):
    if dst.exists() or dst.is_symlink(): dst.unlink()
    os.symlink(src.resolve(),dst)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--manifest",required=True);ap.add_argument("--output",required=True);ap.add_argument("--resolution",choices=("1080","2160"),default="2160",help="Output width; default is a true 2160x3840 DOM render");ap.add_argument("--font-dir",default=str(FONT_ROOT));ap.add_argument("--gsap",required=True,help="Verified local gsap.min.js path; see assets/fonts/provenance.json for dependency evidence");a=ap.parse_args()
    manifest_path=Path(a.manifest).expanduser().resolve(); out=Path(a.output).expanduser().resolve()
    j=json.loads(manifest_path.read_text()); c=j["composition"]; duration=float(c["duration"]);layout_ref=j.get("layout") or {};profile_path=Path(layout_ref.get("style_profile","")).expanduser();
    if not profile_path.is_file(): fail("manifest layout.style_profile is missing or unreadable")
    profile_bytes=profile_path.read_bytes();expected_hash=j.get("profile_sha256") or layout_ref.get("sha256");actual_hash=hashlib.sha256(profile_bytes).hexdigest()
    if expected_hash and expected_hash!=actual_hash: fail("style profile hash differs from the prepared manifest; review and re-prepare before building")
    profile=json.loads(profile_bytes); layout=profile["production_layout"];design_w=int(layout["design_canvas"]["width"]);design_h=int(layout["design_canvas"]["height"]);output_w=int(a.resolution);scale=output_w/design_w;output_h=round(design_h*scale)
    caption_source=j.get("caption_source") or {}
    cues=j.get("captions") or []
    if not cues and caption_source.get("status")=="supplied" and caption_source.get("path"): cues=parse_srt(Path(caption_source["path"]).expanduser())
    if not cues: fail("captions are pending; supply and verify an SRT before building")
    if max(x["end"] for x in cues)>duration+.05: fail("caption timing exceeds composition duration")
    if out.exists(): fail(f"output already exists; refusing to overwrite: {out}")
    (out/"assets").mkdir(parents=True)
    source=Path(j["source_video"]["path"]); link(source,out/"assets/source-video.mp4")
    audio=j.get("audio_master"); audio_tag=""
    if not audio or not audio.get("path"): fail("audio master is pending; supply the locked master before building")
    audio_name="audio-master"+Path(audio["path"]).suffix
    link(Path(audio["path"]),out/"assets"/audio_name)
    audio_tag=f'<audio id="audio-master" class="clip" data-start="0" data-duration="{duration}" src="assets/{audio_name}"></audio>'
    font_dir=Path(a.font_dir).expanduser(); gsap=Path(a.gsap).expanduser()
    for font in ("EastSeaDokdo.ttf","Pretendard-SemiBold.ttf","Pretendard-Bold.ttf"):
        src=font_dir/font
        if not src.is_file(): fail(f"required font missing: {src}")
        link(src,out/"assets"/font)
    if not gsap.is_file(): fail(f"GSAP missing: {gsap}")
    link(gsap,out/"assets/gsap.min.js")
    assets={x["id"]:x for x in j.get("assets",[])}; tags=[]
    for n,b in enumerate(j.get("upper_beats",[])):
        if b["kind"] in ("html","motion","composition"):
            fail(f"beat {n} is authored motion source; render it to a fresh local video first, then declare the prerendered asset")
        if b["kind"] not in ("video","image"): continue
        asset=assets.get(b.get("asset"));
        if not asset: fail(f"missing asset declaration: {b.get('asset')}")
        for field in ("authored_source","spoken_evidence","explanatory_purpose"):
            if not asset.get(field): fail(f"asset {asset.get('id')} missing required {field}")
        if asset.get("created_for_job") != j.get("job_id"): fail(f"asset {asset.get('id')} created_for_job must match job_id")
        src=Path(asset["path"]).expanduser(); suffix=src.suffix or (".mp4" if b["kind"]=="video" else ".png"); name=f"beat-{n:02d}{suffix}";link(src,out/"assets"/name)
        dur=float(b["end"])-float(b["start"]); common=f'id="media-{n}" class="clip screen" data-start="{b["start"]}" data-duration="{dur:.3f}"'
        tags.append(f'<video {common} data-media-start="{b.get("media_start",0)}" src="assets/{name}" muted playsinline></video>' if b["kind"]=="video" else f'<img {common} src="assets/{name}">')
    j["captions"]=cues;j["captions_verbatim"]=True;j["output_settings"]={"width":output_w,"height":output_h,"fps":float(c["fps"])};j["composition"].update({"width":output_w,"height":output_h,"design_width":design_w,"design_height":design_h})
    payload={"manifest":j,"captions":cues}; geom=json.dumps(layout,ensure_ascii=False).replace("<","\\u003c");payload_json=json.dumps(payload,ensure_ascii=False).replace("<","\\u003c")
    page=TEMPLATE.read_text().replace("{{WIDTH}}",str(output_w)).replace("{{HEIGHT}}",str(output_h)).replace("{{DESIGN_WIDTH}}",str(design_w)).replace("{{DESIGN_HEIGHT}}",str(design_h)).replace("{{SCALE}}",str(scale)).replace("{{FPS}}",str(c["fps"])).replace("{{DURATION}}",str(duration)).replace("{{MEDIA_TAGS}}","".join(tags)+audio_tag).replace("{{PAYLOAD}}",payload_json).replace("{{GEOMETRY}}",geom)
    (out/"index.html").write_text(page); (out/"edit-plan.json").write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
    (out/"captions.srt").write_text("\n".join(f"{i+1}\n{srt_stamp(float(x['start']))} --> {srt_stamp(float(x['end']))}\n{x['text']}\n" for i,x in enumerate(cues)),encoding="utf-8")
    (out/"hyperframes.json").write_text(json.dumps({"entry":"index.html"},indent=2)+"\n")
    print(out)
if __name__=="__main__":
    try: main()
    except (RuntimeError,KeyError,FileNotFoundError,ValueError) as e: print(f"build_composition: error: {e}",file=sys.stderr);sys.exit(2)
