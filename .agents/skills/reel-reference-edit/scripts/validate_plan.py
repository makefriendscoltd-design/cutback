#!/usr/bin/env python3
"""Validate a reel edit plan before rendering."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


VIDEO_KINDS = {"video", "clip", "prerender"}
MOTION_KINDS = {"html", "motion", "composition"}


class ValidationError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"expected a JSON object: {path}")
    return value


def resolve(base: Path, value: str, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} must be a non-empty path")
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    try:
        raw = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
            check=True, capture_output=True, text=True,
        ).stdout
        return json.loads(raw)
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot probe media: {path}") from exc


def media_duration(path: Path) -> float:
    data = probe(path)
    try:
        duration = float(data["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError(f"media has no valid duration: {path}") from exc
    if duration <= 0:
        raise ValidationError(f"media duration must be positive: {path}")
    return duration


def composition_base(path: Path) -> Path:
    path = path.expanduser().resolve()
    if not path.exists():
        raise ValidationError(f"composition does not exist: {path}")
    return path if path.is_dir() else path.parent


def expected_settings(plan: dict, profile: dict) -> dict:
    source = dict(profile.get("output_defaults", {}))
    source.update(plan.get("output_settings", plan.get("settings", {})))
    try:
        return {"width": int(source["width"]), "height": int(source["height"]), "fps": float(source["fps"])}
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError("width, height and fps must come from profile or plan settings") from exc


def validate(plan_path: Path, composition: Path) -> dict:
    plan_path = plan_path.expanduser().resolve()
    plan = load_json(plan_path)
    job_id = plan.get("job_id")
    if not isinstance(job_id, str) or not job_id.strip():
        raise ValidationError("job_id is required to trace newly authored supporting assets")
    base = composition_base(composition)
    profile_path = resolve(plan_path.parent, plan.get("profile_path"), "profile_path")
    if not profile_path.is_file():
        raise ValidationError(f"profile does not exist: {profile_path}")
    profile = load_json(profile_path)
    profile_hash = sha256_file(profile_path)
    if plan.get("profile_sha256") and plan["profile_sha256"] != profile_hash:
        raise ValidationError("profile_sha256 does not match the profile file")

    audio = plan.get("audio_master")
    if not isinstance(audio, dict):
        raise ValidationError("audio_master object is required")
    master_path = resolve(plan_path.parent, audio.get("path"), "audio_master.path")
    if not master_path.is_file():
        raise ValidationError(f"audio master does not exist: {master_path}")
    master_duration = media_duration(master_path)

    assets = plan.get("assets")
    if not isinstance(assets, list):
        raise ValidationError("assets must be an array")
    by_id, asset_rows = {}, []
    for item in assets:
        if not isinstance(item, dict) or not item.get("id"):
            raise ValidationError("every asset needs an id")
        if item["id"] in by_id:
            raise ValidationError(f"duplicate asset id: {item['id']}")
        path = resolve(base, item.get("path"), f"asset {item['id']} path")
        if not path.is_file():
            raise ValidationError(f"asset does not exist: {path}")
        kind = item.get("kind") or ("html" if path.suffix.lower() in {".html", ".htm"} else "video" if path.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"} else "image")
        if kind in MOTION_KINDS and path.suffix.lower() not in {".html", ".htm"}:
            raise ValidationError(f"motion asset must point to authored HTML: {item['id']}")
        row = {"id": item["id"], "kind": kind, "path": str(path), "sha256": sha256_file(path)}
        if kind in VIDEO_KINDS:
            row["duration_seconds"] = media_duration(path)
        by_id[item["id"]] = row
        asset_rows.append(row)

    beats = plan.get("beats", plan.get("upper_beats", []))
    if not isinstance(beats, list):
        raise ValidationError("beats must be an array")
    slots = []
    caption_count = len(plan.get("captions", [])) if isinstance(plan.get("captions"), list) else 0
    for index, beat in enumerate(beats):
        try:
            start, end = float(beat["start"]), float(beat["end"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationError(f"beat {index} needs numeric start/end") from exc
        if start < 0 or end <= start or end > master_duration + 0.05:
            raise ValidationError(f"beat {index} is outside the audio timeline")
        asset_id = beat.get("asset")
        if asset_id:
            if asset_id not in by_id:
                raise ValidationError(f"beat {index} references unknown asset: {asset_id}")
            asset = by_id[asset_id]
            source_item = next(item for item in assets if item["id"] == asset_id)
            provenance = source_item.get("provenance", {})
            created_for_job = source_item.get("created_for_job", provenance.get("created_for_job") if isinstance(provenance, dict) else None)
            if created_for_job != job_id:
                raise ValidationError(f"asset {asset_id} must declare created_for_job matching job_id")
            authored_value = source_item.get("authored_source", provenance.get("authored_source") if isinstance(provenance, dict) else None)
            authored_source = resolve(base, authored_value, f"asset {asset_id} authored_source")
            if not authored_source.is_file():
                raise ValidationError(f"authored source does not exist for asset {asset_id}: {authored_source}")
            evidence = source_item.get("spoken_evidence", beat.get("spoken_evidence"))
            if not isinstance(evidence, dict):
                raise ValidationError(f"asset {asset_id} needs structured spoken_evidence")
            if not isinstance(source_item.get("explanatory_purpose"), str) or not source_item["explanatory_purpose"].strip():
                raise ValidationError(f"asset {asset_id} needs explanatory_purpose")
            if "caption_index" in evidence:
                try:
                    evidence_index = int(evidence["caption_index"])
                except (TypeError, ValueError) as exc:
                    raise ValidationError(f"asset {asset_id} has invalid spoken_evidence caption_index") from exc
                if evidence_index < 0 or evidence_index >= caption_count:
                    raise ValidationError(f"asset {asset_id} spoken_evidence caption_index is out of range")
            elif not all(key in evidence for key in ("start", "end")):
                raise ValidationError(f"asset {asset_id} spoken_evidence needs caption_index or start/end")
            else:
                try:
                    evidence_start, evidence_end = float(evidence["start"]), float(evidence["end"])
                except (TypeError, ValueError) as exc:
                    raise ValidationError(f"asset {asset_id} has invalid spoken_evidence timing") from exc
                if evidence_start < 0 or evidence_end <= evidence_start or evidence_end > master_duration + 0.05:
                    raise ValidationError(f"asset {asset_id} spoken_evidence is outside the audio timeline")
            media_start = float(beat.get("media_start", 0))
            if media_start < 0:
                raise ValidationError(f"beat {index} has negative media_start")
            if asset["kind"] in VIDEO_KINDS and media_start + end - start > asset["duration_seconds"] + 0.05:
                raise ValidationError(f"asset is too short for beat {index}: {asset_id}")
            slots.append({"index": index, "asset": asset_id, "start": start, "end": end, "media_start": media_start, "authored_source": str(authored_source), "spoken_evidence": evidence})

    used_video = [by_id[row["asset"]] for row in slots if by_id[row["asset"]]["kind"] in VIDEO_KINDS]
    if len({row["path"] for row in used_video}) != len(used_video):
        raise ValidationError("support video realpaths must be unique across slots")
    if len({row["sha256"] for row in used_video}) != len(used_video):
        raise ValidationError("support video file hashes must be unique across slots")

    captions = plan.get("captions")
    if not isinstance(captions, list) or not captions:
        raise ValidationError("captions must be a non-empty array")
    global_verbatim = plan.get("captions_verbatim") is True
    prior_end = -1.0
    for index, cue in enumerate(captions):
        try:
            start, end = float(cue["start"]), float(cue["end"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationError(f"caption {index} needs numeric output start/end") from exc
        if not isinstance(cue.get("text"), str) or not cue["text"].strip():
            raise ValidationError(f"caption {index} needs verbatim text")
        if cue.get("verbatim") is not True and not global_verbatim:
            raise ValidationError(f"caption {index} must be marked verbatim after transcript comparison")
        source_start = cue.get("source_start")
        source_end = cue.get("source_end")
        if source_start is None or source_end is None:
            if not (audio.get("mapping") == "identity" or any(c.get("mapping") == "identity" for c in plan.get("cuts", []))):
                raise ValidationError(f"caption {index} needs source_start/source_end or an explicit identity mapping")
            source_start, source_end = start, end
        if start < 0 or end <= start or start < prior_end - 0.001 or end > master_duration + 0.05:
            raise ValidationError(f"caption {index} has invalid output timing")
        if float(source_start) < 0 or float(source_end) <= float(source_start):
            raise ValidationError(f"caption {index} has invalid source timing")
        prior_end = end

    declared_duration = plan.get("duration")
    if declared_duration is not None and abs(float(declared_duration) - master_duration) > 0.05:
        raise ValidationError("plan duration differs from actual audio master duration")
    return {
        "status": "plan_valid",
        "plan": str(plan_path),
        "job_id": job_id,
        "composition": str(base),
        "profile": {"path": str(profile_path), "sha256": profile_hash},
        "settings": expected_settings(plan, profile),
        "timeline_duration_seconds": master_duration,
        "audio_master": str(master_path),
        "assets": asset_rows,
        "slots": slots,
        "caption_count": len(captions),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--composition", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="Write the JSON report to a new path")
    args = parser.parse_args()
    try:
        report = validate(args.plan, args.composition)
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            output = args.output.expanduser().resolve()
            if output.exists():
                raise ValidationError(f"output already exists: {output}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(encoded, encoding="utf-8")
            print(output)
        else:
            print(encoded, end="")
        return 0
    except ValidationError as exc:
        print(f"validate_plan: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
