#!/usr/bin/env python3
"""Prepare a raw reel for a reference-style editing session."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import re
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
PROFILE_PATH = (
    PROJECT_ROOT
    / "reference-styles/2026-09-13/memo-vs-yellow-title/style-profile.json"
)


class PreparationError(RuntimeError):
    pass


def parse_srt(path: Path) -> list[dict]:
    cues = []
    for block in re.split(r"\r?\n\s*\r?\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        timing = next((line for line in lines if "-->" in line), None)
        if not timing:
            continue
        def stamp(value: str) -> float:
            h, m, s, ms = map(int, re.split(r"[:,]", value.strip()))
            return h * 3600 + m * 60 + s + ms / 1000
        start, end = [stamp(value) for value in timing.split("-->")]
        text = " ".join(lines[lines.index(timing) + 1:]).strip()
        if text:
            cues.append({"start": start, "end": end, "text": text, "verbatim": True})
    if not cues:
        raise PreparationError(f"captions file has no readable cues: {path}")
    return cues


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_video(source: Path) -> dict:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of",
        "json",
        str(source),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        payload = json.loads(result.stdout)
    except FileNotFoundError as exc:
        raise PreparationError("ffprobe is required but was not found") from exc
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise PreparationError("input is not a readable media file") from exc

    streams = payload.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    try:
        duration = float(payload.get("format", {}).get("duration", 0))
    except (TypeError, ValueError) as exc:
        raise PreparationError("input has no valid duration") from exc
    if video is None or duration <= 0:
        raise PreparationError("input must contain a video stream with positive duration")

    return {
        "duration_seconds": round(duration, 6),
        "video": {
            key: video[key]
            for key in ("codec_name", "width", "height", "r_frame_rate")
            if key in video
        },
        "audio": (
            {
                key: audio[key]
                for key in ("codec_name", "sample_rate", "channels")
                if key in audio
            }
            if audio
            else None
        ),
    }


def probe_duration(source: Path) -> float:
    try:
        value = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(source)], capture_output=True, text=True, check=True).stdout.strip()
        duration = float(value)
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError) as exc:
        raise PreparationError(f"cannot read media duration: {source}") from exc
    if duration <= 0:
        raise PreparationError(f"media duration must be positive: {source}")
    return duration


def extract_frames(source: Path, output: Path, duration: float) -> list[dict]:
    timestamps = [duration * fraction for fraction in (0.1, 0.5, 0.9)]
    frames = []
    for index, timestamp in enumerate(timestamps, start=1):
        destination = output / f"representative-{index:02d}.jpg"
        command = [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-ss",
            f"{timestamp:.6f}",
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(destination),
        ]
        try:
            subprocess.run(command, check=True)
        except FileNotFoundError as exc:
            raise PreparationError("ffmpeg is required but was not found") from exc
        except subprocess.CalledProcessError as exc:
            raise PreparationError(f"failed to extract representative frame {index}") from exc
        if not destination.is_file() or destination.stat().st_size == 0:
            raise PreparationError(f"representative frame {index} was not created")
        frames.append({"path": destination.name, "source_time_seconds": round(timestamp, 6)})
    return frames


def write_brief(output: Path, source: Path, requested_style: str, has_audio: bool) -> None:
    style_value = requested_style if requested_style != "auto" else "pending_content_selection"
    audio_note = (
        "Transcribe and verify the source audio before editing."
        if has_audio
        else "No audio stream was detected; obtain a transcript or narration before editing."
    )
    brief = f"""---
workflow: general-video
flow: companion
status: prepared_not_rendered
style: {style_value}
---

# Reel reference edit

Source: `{source}`

Style profile: `{PROFILE_PATH}`

Requested style: `{requested_style}`. {"Select memo or yellow from the actual content before authoring." if requested_style == "auto" else "Use the matching profile mode."}

{audio_note}

## Required production path

1. Finish and verify the transcription or supplied narration.
2. Follow project AGENTS: locate and verify the already tail-edited audio master first. Lock its order, gaps, duration and speed; do not recut audio. Use an identity time map for overlays.
3. Plan semantic headings and assets against spoken referents using the profile. Freshly author each job's motion composition or functioning visual from its verified subtitles; reuse only fonts, geometry, template mechanics and production tools. Do not seed a new job with prior video assets or demo content.
4. Build the edit through HyperFrames using the `general-video` workflow and the profile as style truth.
5. Render the actual video, preserve the locked master audio (stream copy where possible), and compare audio hashes and duration. Verify full-resolution frames, transitions, first and last syllables before marking complete.

This directory is prepared only. It does not contain a completed or verified render.
"""
    (output / "BRIEF.md").write_text(brief, encoding="utf-8")


def prepare(source_arg: str, style: str, output_arg: str, audio_master_arg: str | None = None, captions_arg: str | None = None) -> Path:
    source = Path(source_arg).expanduser().resolve()
    output = Path(output_arg).expanduser().resolve()

    if not source.is_file():
        raise PreparationError(f"input file does not exist: {source}")
    if output.exists():
        raise PreparationError(f"output already exists; refusing to overwrite: {output}")
    if not PROFILE_PATH.is_file():
        raise PreparationError(f"style profile does not exist: {PROFILE_PATH}")

    probe = probe_video(source)
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    output_defaults = profile["output_defaults"]
    design_canvas = profile["production_layout"]["design_canvas"]
    audio_master = Path(audio_master_arg).expanduser().resolve() if audio_master_arg else None
    captions = Path(captions_arg).expanduser().resolve() if captions_arg else None
    if audio_master and not audio_master.is_file():
        raise PreparationError(f"audio master does not exist: {audio_master}")
    if captions and not captions.is_file():
        raise PreparationError(f"captions file does not exist: {captions}")
    master_duration = probe_duration(audio_master) if audio_master else probe["duration_seconds"]
    if audio_master and abs(master_duration - probe["duration_seconds"]) > 0.05:
        raise PreparationError(f"source video and audio master durations differ ({probe['duration_seconds']:.3f}s vs {master_duration:.3f}s); align them before declaring identity mapping")
    profile_hash = sha256_file(PROFILE_PATH)
    source_stat = source.stat()

    output.mkdir(parents=True)
    try:
        frames = extract_frames(source, output, probe["duration_seconds"])
        selected_style = style if style != "auto" else "pending_content_selection"
        intake = {
            "schema_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "prepared_not_rendered",
            "source": {
                "path": str(source),
                "size_bytes": source_stat.st_size,
                "mtime_ns": source_stat.st_mtime_ns,
            },
            "requested_style": style,
            "selected_style": selected_style,
            "style_profile": {"path": str(PROFILE_PATH), "sha256": profile_hash},
            "probe": probe,
            "representative_frames": frames,
            "needs_transcript_or_narration": probe["audio"] is None,
        }
        (output / "intake.json").write_text(
            json.dumps(intake, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        caption_cues = parse_srt(captions) if captions else []
        manifest = {
            "schema_version": 1,
            "job_id": output.name,
            "status": "ready_to_author" if captions and audio_master else ("pending_audio_master" if captions else "pending_captions"),
            "composition": {"width": output_defaults["width"], "height": output_defaults["height"], "design_width": design_canvas["width"], "design_height": design_canvas["height"], "fps": output_defaults["fps"], "duration": round(master_duration, 6)},
            "source_video": {"path": str(source), "media_start": 0},
            "duration": round(master_duration, 6),
            "profile_path": str(PROFILE_PATH),
            "profile_sha256": profile_hash,
            "output_settings": {"width": output_defaults["width"], "height": output_defaults["height"], "fps": output_defaults["fps"]},
            "audio_master": {"path": str(audio_master), "mapping": "identity"} if audio_master else None,
            "caption_source": {"status": "supplied", "path": str(captions)} if captions else {"status": "pending", "path": None},
            "captions": caption_cues,
            "captions_verbatim": bool(captions),
            "layout": {"style_profile": str(PROFILE_PATH), "pointer": "#/production_layout", "sha256": profile_hash},
            "upper_beats": [],
            "assets": [],
            "production_policy": {
                "preferred": "author an editable motion composition or functioning visual prototype for each explanatory beat",
                "secondary": "use sourced screenshots only when they explain the spoken referent better",
                "audio_locked": audio_master is not None,
                "no_fake_completion_claim": True,
                "asset_reuse": "Only fonts, geometry, template mechanics and production tools may be reused. Visual assets must be freshly authored from this job's verified subtitles.",
            },
        }
        (output / "edit-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_brief(output, source, style, probe["audio"] is not None)
    except Exception:
        shutil.rmtree(output)
        raise
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and prepare a raw reel for memo or yellow reference-style editing."
    )
    parser.add_argument("--input", required=True, help="Path to the raw input video")
    parser.add_argument(
        "--style", choices=("memo", "yellow", "auto"), default="auto",
        help="Reference style; auto leaves content-based selection pending",
    )
    parser.add_argument("--output", required=True, help="New preparation directory")
    parser.add_argument("--audio-master", help="Optional already edited audio master; recorded as locked input")
    parser.add_argument("--captions", help="Optional supplied SRT captions; missing captions remain explicitly pending")
    args = parser.parse_args()
    try:
        destination = prepare(args.input, args.style, args.output, args.audio_master, args.captions)
    except PreparationError as exc:
        print(f"prepare: error: {exc}", file=sys.stderr)
        return 2
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
