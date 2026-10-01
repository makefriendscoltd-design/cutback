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

Linux/Windows rendering and performance are unverified. Windows additionally needs an alternative to the POSIX render lock. No source videos, finished personal videos, screenshots of people, authentication files, tokens or session logs are tracked. LTX2.5/long-form style1 and all team automation product files are excluded from this branch's changes.
