# Episode 12 production report

- Output: `renders/AI학교_12탄_Zev_Owen_v1.mp4`
- Duration: 43.500 seconds
- Source: 53.9364 seconds, 1920×1080 at 60fps
- Edit: complete take preserved; 11 measured sentence pauses shortened to about 0.12 seconds
- Camera: full 17.90s, card 25.60s, 6 full beats, 11 full/card transitions at 0.3s `power2.inOut`
- Captions: 32/32 passed real-font, one-line, punctuation-free, visibility, and safe-area checks
- Fonts: six font files copied; five declared families/styles explicitly loaded; `document.fonts.status=loaded`; all five `document.fonts.check(...)` calls passed
- HyperFrames: 0.8.103 check passed with 0 errors and 0 warnings
- Render: 1080×1920, 30fps, 1305 frames, 52.70MB
- Audio: -14.48 LUFS integrated, -3.07 dBTP
- Decode: full-file decode passed with 0 errors
- Independent ASR: complete narrative and recorded `판단` CTA recovered after render
- Visual review: first frame, scene samples, and encoded opening/branch/CTA/end frames inspected headlessly; hook and CTA preserve the presenter’s face

Limitation: direct speaker-listening was unavailable. Cut integrity was checked from non-VAD word timestamps, 50ms RMS analysis, source script agreement, and independent final-render ASR.
