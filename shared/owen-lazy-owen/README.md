# Owen / Lazy Owen — approved presenter editing handoff

This package preserves the session-owned Owen implementation approved on 2026-10-01 (episode 7 v3). It is a review branch, not a change to the team automation product. No other style is substituted.

## Entry points

- `videos/OWEN_PIPELINE.md`: current approved section takes precedence over historical rules below it.
- `videos/ep07-v3/build.py`: exact approved camera, captions, scene composition and first-frame hook implementation.
- `videos/ep07-v3/cut.py`: source-specific cuts with word-preserving handles.
- `videos/ep07-v3/mix.py`: original speech, ducked music and timed effects.
- `videos/check_owen_camera.py` and `videos/ep07-v3/qc/caption-audit.mjs`: layout regression guards, including actual font-load checks.
- `finalize_audio.py`: validates the source mix and remuxes it losslessly after rendering, preventing renderer-side attenuation observed with0.8.103.
- `run.sh`: portable entry point; sets `OWEN_AUDIO_DIR` without changing the original mixer.
- `SOURCE_MANIFEST.json`: copied-source hashes and original paths. Exported original scripts are byte-identical to their source files. Two documentation copies omit internal publishing destinations and an obsolete scratch path; their original and exported hashes are both recorded.

## Approved behavior

The presenter alternates between full screen and a reduced lower card as upper graphics appear. Full/card transitions use 0.3s `power2.inOut`; explicit scene layout and presenter-only beats prevent a fixed lower presenter layout. The opening contains the Korean hook, presenter and first spoken caption. Captions stay on the torso during size transitions, then move above the reduced presenter. First-frame hooks and full-screen CTA graphics must not cover the face.

1080×1920, 30fps; navy background and cyan emphasis; single-line Pretendard 800 captions, normally 60px. Detailed coordinates, audio cut criteria and checks remain in the original pipeline document.

## Installation

Use macOS or Linux, Node.js 22+ with npm, Python 3.10+, FFmpeg/ffprobe, and the native libraries required by headless Chromium. The source machine used Node26 and HyperFrames0.8.103. Windows requires an alternative to the included POSIX `fcntl` render lock; native Windows is unverified.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
bash run.sh build
```

`build` works without private footage using the included reference transcript and cut metadata. HyperFrames is pinned to0.8.103 and downloaded with npx. Rendering needs network access to npm, a first-run Chrome download, and the GSAP3.14.2 CDN. New-footage transcription also downloads a faster-whisper model. No account credentials are required by these local scripts.

For the original episode7 reproduction, supply the original69.611s episode7 recording as `videos/ep07-v3/src/source.mp4`, then run `bash run.sh render`. That private file is intentionally absent. The script is a source-timed example: replacing it with a different recording is not enough. For a new episode, duplicate the example outside the shared source, transcribe the new recording, update cuts, spoken captions, scene timing/content, face coordinates and explicit camera layout, then run all checks. Keep the actual recorded CTA.

## Validation and limitations

Run `python smoke.py` in the configured virtual environment to create a temporary isolated copy, generate synthetic grid/tone media and exercise the full build/mix/render/QC path. It never replaces the working episode media. See `VALIDATION.md` for this branch's real verification. A successful build is not a claim that missing private footage can be rendered. No direct human listening or Linux render performance is claimed. Review actual encoded frames, all camera transitions, source-word boundaries, final audio, decode integrity and caption geometry before accepting a new episode.

All source editing/style rules in the pipeline/brief are retained as historical context. Public copies omit internal publishing destination/account identifiers and one obsolete private scratch path; the working source documents are unchanged. The package does not authorize Notion, Cafe or YouTube actions. This entry point only builds, checks and locally renders.

## Included assets and exclusions

Included: original required font files, font licenses, the four official-product screenshots used by the current composition, source-timing JSON, and the six unmodified music/effect files used by the approved mixer. Assets are copied at original quality. The package does not grant new rights beyond the assets' existing licenses; font license texts are under `licenses/`.

Excluded: personal source video, presenter crops, final MP4s, rendered previews, credentials, tokens, session archives, caches, node_modules, virtual environments and publishing automation. **LTX2.5 / long-form style1 is explicitly excluded.** Jack Laydenn, Oren and contents auto_aimax are not owned or modified by this handoff.
