# Portable Jack Laydenn / Oren auto editor

This directory packages the existing `auto_editor_80plus` execution path for
the two shared styles. It performs local transcription, deterministic edit-plan
generation, semantic-card asset resolution, 4K Remotion rendering, original
audio muxing, benchmark QA, and up to the requested number of refinement passes.

## Requirements

- Node.js and npm
- Python 3.9 or newer
- FFmpeg and FFprobe on `PATH`
- A locally cached faster-whisper `small` model

Install dependencies from this directory:

```bash
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')"
.venv/bin/python scripts/audit_env.py
```

On Windows, use `.venv\\Scripts\\python.exe` instead of `.venv/bin/python`.
The renderer also supports `AUTO_EDITOR_PYTHON` as an explicit interpreter
path. No API key is required.

The one-time model command downloads the faster-whisper `small` weights into
the machine's local model cache. The weights are intentionally not stored in
Git. `scripts/transcribe.py` uses `local_files_only=True`, so editing stops with
`TRANSCRIBE_MODEL_ERROR` when that cache is absent.

## Entry point

Run from any directory; the input path is resolved from the current directory.

```bash
cd source/auto_editor_80plus
npm run edit -- --input /absolute/path/to/input.mp4 --style oren
npm run edit -- --input /absolute/path/to/input.mp4 --style jacklaydenn
```

Outputs are written to `output/`; temporary Remotion assets are written below
`public/`. Both paths are ignored by Git. Style rules and runtime profiles are
loaded from the sibling `../styles` directory through
`config/style_registry.json`.

Use `--target-score`, `--max-passes`, `--no-assets`, `--dry-plan`,
`--retranscribe`, or `--keep-intermediates` as needed.

Reference videos, source media, rendered outputs, model weights, virtual
environments, `node_modules`, secrets, unrelated styles, and team automation
are not part of this package.

## Verified path

On 2026-10-01, a generated 360x640 H.264/AAC talking sample completed local
faster-whisper transcription, style-plan generation, semantic-card resolution,
2160x3840 Remotion rendering, original-audio muxing, and benchmark QA for both
styles. Oren scored 92.17 and Jack Laydenn scored 87.64; both passed with no
hard-gate failures. This smoke test used macOS; Windows path selection is
implemented but has not been run on Windows.
