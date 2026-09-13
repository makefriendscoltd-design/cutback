#!/usr/bin/env python3
"""Build a portrait vlog HyperFrames composition from an explicit edit plan.

The generator owns derived composition files only. It never rewrites the edit plan,
audio-prep sources, or acquired footage.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = SKILL_ROOT / "references/production-profile.json"


def fail(message: str) -> None:
    raise SystemExit(f"edit-plan error: {message}")


def number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        fail(f"{field} must be a number")
    return float(value)


def resolve_path(plan_dir: Path, raw: Any, field: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        fail(f"{field} must be a non-empty path")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = plan_dir / path
    path = path.resolve()
    if not path.is_file():
        fail(f"{field} does not exist: {path}")
    return path


def safe_id(raw: Any, index: int) -> str:
    value = str(raw or f"shot-{index + 1}").strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value).strip("-")
    if not value:
        value = f"shot-{index + 1}"
    if not re.match(r"^[a-z]", value):
        value = f"shot-{value}"
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def media_duration(path: Path, field: str) -> float:
    try:
        completed = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
            check=True, capture_output=True, text=True,
        )
        duration = float(completed.stdout.strip())
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        fail(f"could not probe {field}: {path}: {error}")
    if duration <= 0:
        fail(f"{field} has no positive duration: {path}")
    return duration


def json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def install_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    shutil.copyfile(source, temporary)
    os.replace(temporary, target)


def install_media_link(source: Path, target: Path) -> None:
    """Use a relative symlink so large acquired clips are not duplicated."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.resolve() == source:
            return
        target.unlink()
    target.symlink_to(os.path.relpath(source, target.parent))


def normalize_plan(raw: dict[str, Any], plan_path: Path, profile: dict[str, Any]) -> dict[str, Any]:
    plan_dir = plan_path.parent
    result: dict[str, Any] = {}
    layout = profile.get("layout", {}) if isinstance(profile.get("layout"), dict) else {}
    duration = number(raw.get("duration"), "duration")
    fps = number(raw.get("fps", layout.get("fps", 30)), "fps")
    if duration <= 0 or fps <= 0 or int(fps) != fps:
        fail("duration must be positive and fps must be a positive integer")
    width = int(number(layout.get("width", 1080), "profile.layout.width"))
    height = int(number(layout.get("height", 1920), "profile.layout.height"))
    if (width, height) != (1080, 1920):
        fail("composition layout must remain the 1080x1920 portrait base; use render.py for 4K export")
    if "width" in raw and number(raw["width"], "width") != width:
        fail(f"width must match the {width}px profile layout")
    if "height" in raw and number(raw["height"], "height") != height:
        fail(f"height must match the {height}px profile layout")
    result.update(duration=duration, fps=int(fps), width=width, height=height)
    result["composition_id"] = safe_id(raw.get("composition_id", "vlog"), 0)
    result["title"] = str(raw.get("title", "Vlog")).strip() or "Vlog"

    audio_raw = raw.get("audio_path", raw.get("audio-path"))
    captions_raw = raw.get("captions_path", raw.get("captions-path"))
    result["audio_path"] = resolve_path(plan_dir, audio_raw, "audio_path")
    result["captions_path"] = resolve_path(plan_dir, captions_raw, "captions_path")
    result["font_path"] = resolve_path(plan_dir, raw.get("font_path"), "font_path")
    result["gsap_path"] = resolve_path(plan_dir, raw.get("gsap_path"), "gsap_path")
    audio_duration = media_duration(result["audio_path"], "audio_path")
    if audio_duration + 1 / result["fps"] < result["duration"]:
        fail(f"audio_path is {audio_duration:.6f}s but timeline is {result['duration']:.6f}s")

    raw_shots = raw.get("shots")
    if not isinstance(raw_shots, list) or not raw_shots:
        fail("shots must be a non-empty array")
    shots = []
    seen_ids: set[str] = set()
    for index, shot in enumerate(raw_shots):
        if not isinstance(shot, dict):
            fail(f"shots[{index}] must be an object")
        shot_id = safe_id(shot.get("id"), index)
        if shot_id in seen_ids:
            fail(f"duplicate shot id after normalization: {shot_id}")
        seen_ids.add(shot_id)
        source_start = number(shot.get("source_start"), f"shots[{index}].source_start")
        output_start = number(shot.get("output_start"), f"shots[{index}].output_start")
        duration = number(shot.get("duration"), f"shots[{index}].duration")
        focal_x = number(shot.get("focal_x", 0.5), f"shots[{index}].focal_x")
        focal_y = number(shot.get("focal_y", 0.5), f"shots[{index}].focal_y")
        if source_start < 0 or output_start < 0 or duration <= 0:
            fail(f"shots[{index}] has a negative start or non-positive duration")
        if output_start + duration > result["duration"] + 1 / result["fps"]:
            fail(f"shots[{index}] ends outside the {result['duration']}s timeline")
        if not 0 <= focal_x <= 1 or not 0 <= focal_y <= 1:
            fail(f"shots[{index}] focal_x/focal_y must be normalized from 0 to 1")
        source = resolve_path(plan_dir, shot.get("source"), f"shots[{index}].source")
        source_duration = media_duration(source, f"shots[{index}].source")
        if source_start + duration > source_duration + 1 / result["fps"]:
            fail(f"shots[{index}] exceeds source duration {source_duration:.6f}s")
        shots.append({
            "id": shot_id,
            "source": source,
            "source_start": source_start,
            "output_start": output_start,
            "duration": duration,
            "focal_x": focal_x,
            "focal_y": focal_y,
        })
    shots.sort(key=lambda item: (item["output_start"], item["id"]))

    tolerance = 1 / result["fps"] + 1e-6
    cursor = 0.0
    for shot in shots:
        if shot["output_start"] < cursor - tolerance:
            fail(f"shot {shot['id']} overlaps the previous shot")
        if shot["output_start"] > cursor + tolerance:
            fail(f"uncovered timeline gap before {shot['id']}: {cursor:.6f}–{shot['output_start']:.6f}s")
        cursor = shot["output_start"] + shot["duration"]
    if abs(cursor - result["duration"]) > tolerance:
        fail(f"shots end at {cursor:.6f}s; expected {result['duration']:.6f}s")
    result["shots"] = shots

    try:
        caption_payload = json.loads(result["captions_path"].read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"could not read captions JSON: {error}")
    captions = caption_payload.get("captions") if isinstance(caption_payload, dict) else None
    if not isinstance(captions, list) or not captions:
        fail("captions JSON must contain a non-empty captions array")
    normalized_captions = []
    previous_end = 0.0
    for index, caption in enumerate(captions):
        if not isinstance(caption, dict):
            fail(f"caption {index} must be an object")
        start = number(caption.get("start"), f"captions[{index}].start")
        end = number(caption.get("end"), f"captions[{index}].end")
        text = caption.get("text")
        if not isinstance(text, str) or not text.strip():
            fail(f"captions[{index}].text must be non-empty")
        if start < previous_end - 1e-6 or end <= start or end > result["duration"] + 1e-6:
            fail(f"caption {index} overlaps, has invalid duration, or exceeds the timeline")
        normalized_captions.append({"id": index + 1, "start": start, "end": end, "text": text.strip()})
        previous_end = end
    caption_defaults = profile.get("caption_style", {}) if isinstance(profile.get("caption_style"), dict) else {}
    caption_override = raw.get("caption_style", {})
    if not isinstance(caption_override, dict):
        fail("caption_style must be an object")
    result["caption_style"] = {**caption_defaults, **caption_override}
    result["caption_style"].setdefault("center_y", .446)
    result["caption_style"].setdefault("font_size", 64)
    headline = raw.get("headline")
    if headline is not None:
        if not isinstance(headline, dict):
            fail("headline must be an object")
        headline_defaults = profile.get("headline_style", {}) if isinstance(profile.get("headline_style"), dict) else {}
        headline = {**headline_defaults, **headline}
        lines = headline.get("lines")
        if not isinstance(lines, list) or not lines or not all(isinstance(line, str) and line.strip() for line in lines):
            fail("headline.lines must be a non-empty string array")
        headline["lines"] = [line.strip() for line in lines]
        headline["duration"] = number(headline.get("duration", 1), "headline.duration")
        if headline["duration"] <= 0 or headline["duration"] > result["duration"]:
            fail("headline.duration must be positive and within the timeline")
        if headline.get("design") == "impact":
            headline["font_path"] = resolve_path(plan_dir, headline.get("font_path", raw.get("font_path")), "headline.font_path")
    result["headline"] = headline
    result["captions"] = normalized_captions
    return result


def fmt(value: float) -> str:
    rendered = f"{value:.6f}".rstrip("0").rstrip(".")
    return rendered or "0"


def build_html(plan: dict[str, Any], composition_dir: Path) -> tuple[str, list[dict[str, Any]]]:
    assets = composition_dir / "assets"
    install_file(plan["audio_path"], assets / "audio/voice.wav")
    font_suffix = plan["font_path"].suffix.lower() or ".ttf"
    install_file(plan["font_path"], assets / f"fonts/Pretendard-Medium{font_suffix}")
    install_file(plan["gsap_path"], assets / "vendor/gsap.min.js")

    source_assets: dict[Path, str] = {}
    provenance = []
    shot_tags = []
    for shot in plan["shots"]:
        source = shot["source"]
        if source not in source_assets:
            filename = f"source-{len(source_assets) + 1:02d}{source.suffix.lower()}"
            relative = f"assets/shots/{filename}"
            install_media_link(source, composition_dir / relative)
            source_assets[source] = relative
            provenance.append({"asset": relative, "source": str(source), "sha256": sha256(source)})
        source_attr = html.escape(source_assets[source], quote=True)
        shot_tags.append(
            f'''      <video id="{shot['id']}" class="clip footage" src="{source_attr}"
        data-start="{fmt(shot['output_start'])}" data-duration="{fmt(shot['duration'])}"
        data-media-start="{fmt(shot['source_start'])}" data-track-index="0"
        muted playsinline preload="auto"
        style="object-position:{shot['focal_x'] * 100:.3f}% {shot['focal_y'] * 100:.3f}%"></video>'''
        )

    caption_tags = []
    for caption in plan["captions"]:
        duration = caption["end"] - caption["start"]
        caption_tags.append(
            f'''      <div id="caption-{caption['id']:02d}" class="clip caption"
        data-start="{fmt(caption['start'])}" data-duration="{fmt(duration)}" data-track-index="2">{html.escape(caption['text'])}</div>'''
        )

    scale = plan["width"] / 1080
    caption_y = float(plan["caption_style"]["center_y"]) * 100
    caption_size = float(plan["caption_style"]["font_size"]) * scale
    caption_shadow = plan["caption_style"].get("text_shadow", "0 2px 4px rgba(0, 0, 0, 0.9), 0 0 8px rgba(0, 0, 0, 0.65)")
    headline = plan.get("headline")
    headline_tag = ""
    headline_css = ""
    if headline:
        headline_text = "<br>".join(html.escape(line) for line in headline["lines"])
        headline_tag = f'<div id="headline" class="clip headline" data-start="0" data-duration="{fmt(headline["duration"])}" data-track-index="3">{headline_text}</div>'
        headline_css = ".headline { position:absolute; top:220px; left:60px; width:960px; height:204px; box-sizing:border-box; padding:16px 20px; border-radius:12px; background:rgba(0,0,0,.72); display:block; text-align:center; color:white; font-family: \"Pretendard Local\",sans-serif; font-size:74px; font-weight:600; line-height:1.15; letter-spacing:-2px; z-index:20; text-shadow:0 3px 5px rgba(0,0,0,.9),0 0 16px rgba(0,0,0,.45); }"
    if headline and headline.get("design") == "impact":
        headline_size = float(headline.get("font_size", 108)) * scale
        headline_last_size = float(headline.get("last_line_font_size", 108)) * scale
        headline_font = headline["font_path"]
        install_file(headline_font, assets / "fonts/Headline-Black.ttf")
        headline_text = "".join('<span class="head-line">' + html.escape(line) + '</span>' for line in headline["lines"])
        headline_tag = f'<div id="headline" class="clip headline" data-start="0" data-duration="{fmt(headline["duration"])}" data-track-index="3">{headline_text}</div>'
        headline_css = '''@font-face {font-family:HeadlineBlack;src:url(assets/fonts/Headline-Black.ttf);font-weight:900;}
        .headline {position:absolute;top:18.75%;left:5.556%;width:88.889%;height:16.146%;z-index:20;text-align:center;font-family:HeadlineBlack,sans-serif;font-size:108px;line-height:1.15;letter-spacing:-0.278vw;font-weight:900;color:white;-webkit-text-stroke:.648vw #080808;paint-order:stroke fill;text-shadow:0 .648vw 0 #080808,0 .833vw 1.481vw #000;}
        .head-line {display:block;white-space:nowrap;}
        .head-line:last-child {font-size:150px;color:#fff;margin-top:8px;}
        '''
        headline_css = headline_css.replace("font-size:108px", f"font-size:{headline_size}px").replace("font-size:150px", f"font-size:{headline_last_size}px")
    font_format = "woff2" if font_suffix == ".woff2" else "opentype"
    document = f'''<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width={plan['width']}, height={plan['height']}">
    <title>{html.escape(plan['title'])}</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {{
        font-family: "Pretendard Local";
        src: url("assets/fonts/Pretendard-Medium{font_suffix}") format("{font_format}");
        font-style: normal;
        font-weight: 500;
        font-display: block;
      }}
      html, body {{
        width: {plan['width']}px;
        height: {plan['height']}px;
        margin: 0;
        overflow: hidden;
        background: #000;
      }}
      #{plan['composition_id']} {{
        position: relative;
        width: {plan['width']}px;
        height: {plan['height']}px;
        overflow: hidden;
        background: #000;
      }}
      .clip {{ position: absolute; }}
      .footage {{
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: 1;
      }}
      .caption {{
        left: 4.63%;
        right: 4.63%;
        top: calc({caption_y}% - {caption_size * .65625}px);
        height: {caption_size * 1.3125}px;
        z-index: 10;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        overflow: visible;
        white-space: nowrap;
        color: #fff;
        font-family: "Pretendard Local", sans-serif;
        font-size: {caption_size}px;
        font-style: normal;
        font-weight: 500;
        line-height: 1;
        letter-spacing: -1.35px;
        text-align: center;
        -webkit-text-stroke: 0.65px rgba(0, 0, 0, 0.65);
        text-shadow: {caption_shadow};
      }}
      {headline_css}
    </style>
  </head>
  <body>
    <div id="{plan['composition_id']}" data-composition-id="{plan['composition_id']}" data-start="0"
      data-width="{plan['width']}" data-height="{plan['height']}" data-duration="{fmt(plan['duration'])}">
{chr(10).join(shot_tags)}
{chr(10).join(caption_tags)}
{headline_tag}
      <audio id="vlog-voice" src="assets/audio/voice.wav" data-start="0"
        data-duration="{fmt(plan['duration'])}" data-track-index="10" data-volume="1"></audio>
    </div>
    <script>
      const timeline = gsap.timeline({{ paused: true }});
      window.__timelines["{plan['composition_id']}"] = timeline;
    </script>
  </body>
</html>
'''
    return document, provenance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--composition", type=Path, required=True)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    args = parser.parse_args()
    plan_path = args.plan.expanduser().resolve()
    if not plan_path.is_file():
        fail(f"plan does not exist: {plan_path}")
    try:
        raw = json.loads(plan_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"could not read plan: {error}")
    if not isinstance(raw, dict):
        fail("plan root must be an object")
    profile_path = args.profile.expanduser().resolve()
    profile: dict[str, Any] = {}
    if profile_path.is_file():
        try:
            profile = json.loads(profile_path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            fail(f"could not read production profile: {error}")
        if not isinstance(profile, dict):
            fail("production profile root must be an object")
    plan = normalize_plan(raw, plan_path, profile)
    plan["profile_path"] = profile_path if profile_path.is_file() else None
    composition_dir = args.composition.expanduser().resolve()
    composition_dir.mkdir(parents=True, exist_ok=True)
    document, source_provenance = build_html(plan, composition_dir)
    index_path = composition_dir / "index.html"
    temporary = index_path.with_name(".index.html.tmp")
    temporary.write_text(document)
    os.replace(temporary, index_path)
    build_record = {
        "schema_version": 1,
        "edit_plan": str(plan_path),
        "edit_plan_sha256": sha256(plan_path),
        "composition": str(index_path),
        "duration_seconds": plan["duration"],
        "fps": plan["fps"],
        "size": [plan["width"], plan["height"]],
        "shot_count": len(plan["shots"]),
        "caption_count": len(plan["captions"]),
        "profile": ({"source": str(plan["profile_path"]), "sha256": sha256(plan["profile_path"])}
                    if plan["profile_path"] else None),
        "caption_style": json_safe(plan["caption_style"]),
        "headline": json_safe(plan["headline"]),
        "audio": {"asset": "assets/audio/voice.wav", "source": str(plan["audio_path"]), "sha256": sha256(plan["audio_path"])},
        "font": {"source": str(plan["font_path"]), "sha256": sha256(plan["font_path"])},
        "gsap": {"source": str(plan["gsap_path"]), "sha256": sha256(plan["gsap_path"])},
        "shot_sources": source_provenance,
    }
    record_path = composition_dir / "build-provenance.json"
    record_path.write_text(json.dumps(build_record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"index": str(index_path), "duration": plan["duration"], "shots": len(plan["shots"]), "captions": len(plan["captions"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
