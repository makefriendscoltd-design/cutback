# Episode 12 — EP06-based v5 revision

This revision uses the approved EP06 composition engine and turns the narration into a concrete support workflow: a sample double-payment ticket is extracted into structured fields, scored, routed to the human-review lane, and checked against forced-human rules. Original speech, cuts, captions, and presenter media remain unchanged.

- Final file: `renders/AI학교_12탄_Owen_v5.mp4`
- Encoded duration: 43.500000s; 1080×1920, 30fps; 1,305 frames; full decode errors: 0.
- Final decoded audio: -14.03 LUFS / -1.37 dBTP; decoded mix alignment: 0.0ms, correlation 1.0.
- The final MP4 uses lossless video stream-copy remux with the episode's own `assets/mix.m4a`; the renderer-attenuated file is preserved as `qc/renderer-attenuated.mp4`.
- Captions: 32/32 passed; HyperFrames: PASS with 0 warnings and 0 errors.
- Camera rhythm: card 17.40s, full presenter 16.60s, graphics-only 9.50s; 4 separate full beats and 5 in-scene emphasis camera keys.
- EP06 helper/timeline reference checks, continuous scene coverage, camera contract, source freshness, named-action timing, and action/mix event hash all passed.
- Actual final contact and action frames were inspected for blank frames, clipping, presenter obstruction, and state-change visibility; none were found.

Evidence: `qc/render-verification.json`, `qc/action-verification.json`, `qc/caption-audit.json`, `qc/reference-contract.json`, `qc/camera-contract.json`, `qc/final-check.json`, `qc/final-contact-sheet.jpg`, and `qc/action-review-*.jpg`.

The renderer attenuated the correct mix to -19.42 LUFS. `qc/remux_final.py` replaced only the audio with the verified own mix using stream copy; encoded video was preserved. The final checks above apply to the remuxed MP4. The attenuated render is retained locally in qc/renderer-attenuated.mp4.
