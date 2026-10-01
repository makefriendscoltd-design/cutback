# Validation — 2026-10-01

Status: shared-package build, headless composition checks and synthetic full-length rendering passed on the source Mac. Real source footage is deliberately not in this branch.

## Evidence

- Copied-source manifest:32 files, hash verification passed. Core approved builder/cutter/mixer/library are byte-identical to their source. Only two public documentation copies omit internal publishing destinations or an obsolete scratch interpreter path; both original and export hashes are recorded. Original working files were not edited by the export.
- Independent read-only reviewer ran the build in a separate temporary copy and checked Python/Node/bash syntax, local asset references, source hashes and excluded-file/secret patterns.
- `bash run.sh build`:17 scenes,40 captions,49.05s. Camera check:7 full beats, full19.19s/card29.86s.
- Headless caption audit:40/40 pass, actual Pretendard font loaded, no automatic font size below60px, all one-line and inside safe bounds.
- HyperFrames0.8.103 check ran against a temporary copy with synthetic media; lint/runtime/layout/contrast checks all passed with0 errors and0 warnings; actual final frames were inspected.
- Synthetic grid video and tone audio were generated in isolation. The original approved composition and audio mixer were exercised without a person's recording.
- Full-length rendered output after audio finalization:49.066667s,1080×1920,30fps,1472 frames,7.18MB; full FFmpeg decode errors0; -14.15LUFS/-1.06dBTP. Encoded scene contact sheet inspected.
- The first renderer output attenuated the mix from -14.15 to -21.09LUFS. `finalize_audio.py` now checks the source mix and copies the exact validated audio stream into the rendered video without re-encoding either stream. The resulting actual MP4 passed the complete validation. `run.sh render` and `smoke.py` include that step.
- Python AST, `bash -n`, `node --check`, source-hash audit and staged path/size/media/secret-pattern checks passed after the wrapper change.

## Boundaries

This is a portability test with synthetic grid/tone media, not a claim of listening to the original recording. The original speech/cuts and presenter composition were separately verified in the local approved episode7v3 workflow. New recordings require new source-specific timing, caption, scene and cut decisions.

Linux/Windows rendering and performance are unverified. Windows now requires the WSL2 entry described below; the original POSIX lock is preserved. No source videos, finished personal videos, screenshots of people, authentication files, tokens or session logs are tracked. LTX2.5/long-form style1 and all team automation product files are excluded from this branch's changes.

## Windows entry follow-up — 2026-10-01

Base: `f8ce3ac4ad60a2a7fcf4882ab614a737d5460f03`, same shared branch.

- Added `run-wsl.sh` and `WINDOWS.md`. Requires WSL2 and Linux Python 3.10+/Node 22+/npm/npx/FFmpeg/ffprobe, checks imports and `fcntl` locking, rejects Windows runtime paths. No untested native lock substitution.
- Added `run.sh prepare|smoke`. `check` and `render` now ensure the pinned HyperFrames Chrome is present before caption audit. The synthetic smoke uses these build/prepare entry points too.
- Original videos, assets and licenses are byte-identical to the base commit. All 32 source-manifest entries match their hashes, including the POSIX render lock. No scene, animation, timing, font, screenshot, music or effect changes.
- `bash -n` for both entry scripts, Python AST parsing, `git diff --check`: PASS.
- Actual non-WSL host guard on macOS: exit 2 with WSL2 instructions, before build/render. This is a rejection-path test, not a Windows run.
- Native Windows: UNSUPPORTED. WSL2/Ubuntu package installation, Windows launch and Linux browser/render execution: NOT RUN (no Windows/WSL host available). Target command: `bash run-wsl.sh smoke` after setup in WINDOWS.md. A simulated WSL environment is not accepted as runtime evidence.
- Direct `run.sh` also rejects native Windows shells and routes detected WSL through the mandatory preflight. Simulated `uname` rejection branches for Git Bash and WSL1 returned exit 2. These tests do not establish WSL runtime compatibility.
- First follow-up smoke aborted at 747/1472 frames with `render_cancelled_parent_exited`. The automation retry uses the renderer's `HYPERFRAMES_RENDER_DETACHED=1` environment setting for that command only, without changing shared renderer options or composition.
- Retry command `HYPERFRAMES_RENDER_DETACHED=1 bash run.sh smoke`: PASS on macOS arm64, Node 26.6.0 and system Python 3.9.6 with installed Pillow/NumPy. This is the existing Mac runtime, not validation of the documented fresh WSL Python 3.10+ setup. Exit 0 through build, mix, browser preparation, camera audit, caption audit, HyperFrames check, render, lossless audio finalization and encoded-output QC. The smoke uses pre-cut synthetic media; original private-source cutting/transcription is not tested.
- Final output: 1080x1920, 30fps, 49.066667s, 1472 frames, 7.18MB, -14.15 LUFS, -1.06 dBTP, zero full-decode errors, captions 40/40. Camera: 7 full beats, full 19.19s/card 29.86s. Final encoded contact sheet visually inspected.
- HyperFrames check: ok=true, zero errors/warnings, one informational layout occlusion at 40.875s (existing scene text behind the presenter). Composition was preserved; this is not reported as a zero-findings result.
- Render used original 0.8.103 with screenshot capture/hardware GPU. Render stage 98.3s on this Mac; no Windows performance inference. Synthetic output and detailed local logs remain outside Git.
