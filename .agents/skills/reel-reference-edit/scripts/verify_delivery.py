#!/usr/bin/env python3
"""Verify a rendered reel against its plan, profile, assets, and audio donor."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from validate_plan import ValidationError, load_json, probe, resolve, validate


def run(command: list[str], *, capture: bool = True) -> str:
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=capture)
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise ValidationError(f"command failed: {command[0]}") from exc
    return (result.stdout or "").strip()


def audio_hash(path: Path, packet_copy: bool) -> str:
    command = ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0"]
    if packet_copy:
        command += ["-c:a", "copy"]
    command += ["-f", "hash", "-hash", "sha256", "-"]
    return run(command)


def fps_value(value: str) -> float:
    try:
        numerator, denominator = value.split("/", 1)
        return float(numerator) / float(denominator)
    except (AttributeError, ValueError, ZeroDivisionError) as exc:
        raise ValidationError(f"invalid frame rate: {value}") from exc


def make_qa_dir(final: Path, requested: Path | None) -> Path:
    if requested:
        output = requested.expanduser().resolve()
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = final.parent / f"{final.stem}-qa-{stamp}"
    if output.exists():
        raise ValidationError(f"QA output already exists: {output}")
    output.mkdir(parents=True)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--composition", required=True, type=Path)
    parser.add_argument("--final", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="New QA directory; existing paths are refused")
    parser.add_argument("--visual-reviewed", action="store_true", help="Reviewer inspected generated frames")
    parser.add_argument("--direct-listened", action="store_true", help="Reviewer listened to the rendered audio")
    parser.add_argument("--source-audited", action="store_true", help="Reviewer confirmed fresh authored sources and permitted ingredients")
    args = parser.parse_args()
    try:
        plan_path = args.plan.expanduser().resolve()
        plan = load_json(plan_path)
        plan_report = validate(plan_path, args.composition)
        final = args.final.expanduser().resolve()
        if not final.is_file():
            raise ValidationError(f"final media does not exist: {final}")
        meta = probe(final)
        videos = [stream for stream in meta.get("streams", []) if stream.get("codec_type") == "video"]
        audios = [stream for stream in meta.get("streams", []) if stream.get("codec_type") == "audio"]
        if len(videos) != 1 or not audios:
            raise ValidationError("final must contain one video stream and at least one audio stream")
        video = videos[0]
        settings = plan_report["settings"]
        duration = float(meta["format"]["duration"])
        fps = fps_value(video.get("r_frame_rate"))
        tolerance = max(0.05, 1 / settings["fps"])
        checks = {
            "dimensions_match_plan": [int(video["width"]), int(video["height"])] == [settings["width"], settings["height"]],
            "fps_matches_plan": abs(fps - settings["fps"]) < 0.001,
            "duration_matches_audio_master": abs(duration - plan_report["timeline_duration_seconds"]) <= tolerance,
        }
        if not all(checks.values()):
            raise ValidationError(f"final media contract failed: {checks}")
        run(["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"], capture=False)
        checks["full_decode"] = True

        audio = plan["audio_master"]
        donor_value = audio.get("final_donor", audio.get("path"))
        donor = resolve(plan_path.parent, donor_value, "audio donor")
        if not donor.is_file():
            raise ValidationError(f"audio donor does not exist: {donor}")
        donor_packet, donor_pcm = audio_hash(donor, True), audio_hash(donor, False)
        final_packet, final_pcm = audio_hash(final, True), audio_hash(final, False)
        declared = audio.get("hashes", audio.get("donor_hash", {}))
        declared_packet = declared.get("packets", declared.get("packet_sha256")) if isinstance(declared, dict) else None
        declared_pcm = declared.get("pcm", declared.get("decoded_pcm_sha256")) if isinstance(declared, dict) else None
        if declared_packet and declared_packet != donor_packet:
            raise ValidationError("declared donor packet hash does not match donor")
        if declared_pcm and declared_pcm != donor_pcm:
            raise ValidationError("declared donor PCM hash does not match donor")
        checks["audio_packet_hash_matches_donor"] = final_packet == donor_packet
        checks["audio_pcm_hash_matches_donor"] = final_pcm == donor_pcm
        if not checks["audio_pcm_hash_matches_donor"]:
            raise ValidationError("final decoded audio differs from donor")

        qa = make_qa_dir(final, args.output)
        sample_times = sorted(set(max(0.0, min(duration - tolerance, duration * ratio)) for ratio in (0.02, 0.25, 0.5, 0.75, 0.98)))
        frames = []
        for index, timestamp in enumerate(sample_times, 1):
            path = qa / f"frame-{index:02d}-{timestamp:.3f}s.jpg"
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{timestamp:.6f}", "-i", str(final), "-frames:v", "1", "-q:v", "2", str(path)], capture=False)
            frames.append({"path": str(path), "time_seconds": round(timestamp, 6), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        review = {"visual": "verified" if args.visual_reviewed else "pending_visual_review", "direct_listening": "verified" if args.direct_listened else "pending_direct_listening", "source_audit": "verified" if args.source_audited else "pending_manual_source_audit"}
        status = "verified" if all(value == "verified" for value in review.values()) else "machine_verified_review_pending"
        report = {
            "verified_utc": datetime.now(timezone.utc).isoformat(), "status": status,
            "final": str(final), "plan": plan_report, "checks": checks,
            "audio": {"donor": str(donor), "donor_packet_sha256": donor_packet, "donor_pcm_sha256": donor_pcm, "final_packet_sha256": final_packet, "final_pcm_sha256": final_pcm},
            "review": review, "qa_frames": frames,
        }
        report_path = qa / "delivery-verification.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(report_path)
        return 0
    except (ValidationError, KeyError, TypeError, ValueError) as exc:
        print(f"verify_delivery: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
