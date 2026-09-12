Output: /Users/apple/Downloads/20260911_175145_컷편집_v1.mp4
Source: /Users/apple/Downloads/20260911_175145_편집본.mp4
Canonical edit: edit-plan.json; regenerate with build-final.py.

Passed: full FFmpeg audio/video decode (0 errors), 1920x1080 60000/1001 fps, duration 234.70125 seconds, audio/video end difference 0.25ms; output ASR preserves intended complete sentences at all three stumble/retake edits; beginning/middle/end frames visually checked; composition lint 0 errors/warnings.

44 audio midpoint correlations locate the original at a consistent 5.5–5.75ms offset (original audio starts at 5.896ms). The exploratory raw waveform correlation threshold of .95 did not pass for 4 clips (minimum .721); this is not used as an audio quality pass. No further threshold adjustment. Full human listening remains unverified; next check: open output MP4 and listen through.

Intermediate source-selection error was fixed before delivery: changed two clips were rebuilt from the explicit original path. Final full ASR confirms restored middle sentences.
