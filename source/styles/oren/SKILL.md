# Oren-style Reels Editing Skill v1

## Goal
Turn a raw 9:16 talking-head recording into a high-retention vertical reel using the recurring editing grammar extracted from 5 high-performing reference reels from the same creator.

This is not an instruction to copy any single reference frame-for-frame. Reproduce the recurring editing grammar: pacing, information hierarchy, visual evidence, editorial typography, B-roll cadence, and talking-head/B-roll alternation.

## Inputs
Required:
- One raw vertical talking-head video (9:16 preferred; 1080x1920 or 720x1280 accepted)

Optional:
- Transcript or script
- Brand fonts/colors
- B-roll asset folder
- Screenshots / evidence / product UI / documents
- CTA text

## Output
- `edit_plan.json` conforming to `schemas/edit_plan.schema.json`
- Final 9:16 MP4
- Optional captions SRT/VTT
- Optional asset manifest with source/origin for every external visual

## Non-negotiable pipeline
Never render immediately from the raw file. Always perform:
1. Ingest and technical probe
2. Speech transcription with word timestamps
3. Dead-air/filler cleanup plan
4. Semantic beat segmentation
5. Mode classification: ESSAY_STORY or TUTORIAL
6. Visual-role classification for every beat
7. Asset plan / asset retrieval
8. `edit_plan.json`
9. Render
10. Automated QA against pacing/style metrics

## Mode classifier
### ESSAY_STORY
Use when the speaker is explaining an idea, story, opinion, social pattern, lifestyle topic, business idea, cultural observation, or narrative.

Targets:
- Full-screen external B-roll / image / screenshot: 55-65% of runtime
- Talking head: 35-45% of runtime
- Major visual change average: 1.4-1.8 sec
- Do not leave the same information structure unchanged for >3.2 sec unless intentionally emphasizing a thesis.

### TUTORIAL
Use when the speaker teaches software, AI, steps, workflow, how-to, or demonstrates a tool.

Targets:
- Talking head including UI/graphic overlays: 65-80%
- Full-screen evidence/demo: 20-35%
- Major visual change average: 2.1-2.8 sec
- A new step should create a clear chapter-title event.

## Core visual grammar
The default rhythm is:
`talking head -> visual evidence/B-roll -> talking head thesis -> B-roll burst -> talking head -> proof/screenshot -> talking head`

Do not create movement only for the sake of movement. The creator's pace comes primarily from changing information, not constant zooming.

## Beat classification
Classify every semantic beat into exactly one primary scene type:
- `TALKING_HEAD`
- `TALKING_HEAD_KEYPHRASE`
- `FULLSCREEN_BROLL`
- `BROLL_BURST`
- `TALKING_HEAD_WITH_UI`
- `FULLSCREEN_EVIDENCE`
- `NUMBER_STAT`
- `BEFORE_AFTER`
- `OBJECT_CUTOUT`
- `CHAPTER_TITLE`
- `CTA`

### TALKING_HEAD
Use for interpretation, opinion, bridge sentences, rhetorical questions, conclusions, or when no useful visual evidence exists.

### TALKING_HEAD_KEYPHRASE
Use for thesis statements, contrasts, surprising reframes, memorable short phrases, or chapter pivots.
- Add large editorial serif text.
- Do not use on every sentence.
- Typical frequency in ESSAY_STORY: every 7-15 sec, plus the opening hook and final thesis when appropriate.
- Text length: ideally 2-7 words, max 10.

### FULLSCREEN_BROLL
Use when the speech contains a concrete visual noun or location: place, object, behavior, food, clothing, vehicle, house, person archetype, lifestyle scene, historical reference, etc.
- Prefer a literal or strongly associative visual.
- Typical duration 0.8-2.2 sec.
- Hard cut by default.

### BROLL_BURST
Use when several examples are listed or a concept benefits from rapid accumulation.
- 2-5 assets.
- Each 0.55-1.2 sec.
- Use hard cuts.
- Preserve narration continuously underneath.

### TALKING_HEAD_WITH_UI
Use in tutorial mode when discussing software, interfaces, files, timelines, audio meters, AI tools, or screen-based workflows.
- Keep the speaker visible.
- Put UI behind/around the speaker when subject segmentation is available.
- Otherwise place UI in upper safe zone without covering face.

### FULLSCREEN_EVIDENCE
Use for proof, source screenshots, actual results, social posts, documents, charts, book covers, real tool output, or "this actually happened" moments.
- Prefer fullscreen over picture-in-picture when evidence is the point of the sentence.
- Typical duration 1.3-3.2 sec.

### NUMBER_STAT
Use for strong numeric claims, price, percentage, multiple, date, or count.
- Display the number large in editorial serif.
- Pair with contextual B-roll/evidence when possible.

### BEFORE_AFTER
Use when the line explicitly compares before/after, wrong/right, old/new, raw/corrected, baseline/result.
- Make the contrast visual, not only textual.

### OBJECT_CUTOUT
Use when one object itself is the joke/example/anchor.
- Isolate the object on a simple contrasting background.
- Keep duration short, normally 0.8-1.8 sec.

### CHAPTER_TITLE
Tutorial: every numbered step.
Essay: only for major section pivot.
- Large editorial serif.
- White by default.
- 1-3 lines.
- Place top/center or wrap around the subject without covering the face.

### CTA
Keep the call to action visually simpler than the body.
- Speaker returns to camera unless CTA itself is a visual asset.
- Show only the action keyword / offer / destination.

## Hook rules: first 0-3 seconds
1. Show the speaker immediately unless a stronger concrete establishing visual is essential.
2. Place a large topic/thesis label in editorial serif.
3. The first visual promise must be understandable with sound off.
4. If the first line contains a concrete example, cut to B-roll within roughly 2-4 sec.
5. Avoid logo intros, long fades, empty establishing shots, or generic decorative animation.

## B-roll sourcing rules
B-roll must explain, prove, or emotionally sharpen the spoken idea.
Priority:
1. User-provided original footage
2. User-provided screenshots/evidence
3. Licensed/approved stock assets
4. Generated visuals when appropriate
5. Web references only if the workflow has a permitted retrieval method and usage rights are respected

Never use random B-roll just to satisfy a timing quota.

If assets cannot be sourced, fall back to TALKING_HEAD_KEYPHRASE rather than irrelevant stock.

## Caption rules
- Always-on dialogue captions unless the user disables them.
- Small white sans-serif.
- Centered.
- Usually 1 line, max 2.
- Keep within vertical safe area; baseline approximately 72-82% of frame height depending on platform UI.
- Avoid large karaoke-style captions as the default.
- Large editorial typography is separate from dialogue captions.

## Editorial title rules
- High-contrast editorial serif / fashion-magazine feeling.
- White by default.
- Mix Roman + italic when it improves hierarchy.
- Use tight line spacing.
- Subtle shadow/stroke only when needed for legibility.
- Never cover eyes, mouth, or essential UI.
- Prefer phrase composition over single-word bouncing captions.

## Composition
- Maintain face in the central safe region.
- Keep platform controls/right-side UI clear.
- B-roll is normally full-frame vertical crop.
- Slight slow crop/scale motion may be used on still images (roughly 102-108%), but do not animate every still identically.

## Transitions
Default distribution:
- Hard cuts: dominant, ~85-95%
- Simple scale/pop/slide used sparingly for UI/cards
- Cross dissolves are exceptional, not default
- Avoid flashy preset transitions

## Talking-head cleanup
- Remove obvious false starts and filler when meaning is preserved.
- Compress long pauses.
- Preserve natural rhetorical micro-pauses.
- Prefer J/L-style audio continuity across B-roll.
- Do not create jump cuts more frequently than needed if B-roll can hide the edit.

## Audio
- Dialogue is always dominant.
- Normalize final loudness to a social-video-friendly level; avoid clipping.
- If music is used, keep it clearly below dialogue.
- SFX are optional and sparse; use for meaningful title/UI events, not every cut.

## QA metrics
Before final render, calculate/report:
- mode
- runtime
- major visual-change count
- average visual-change interval
- talking-head runtime ratio
- full-screen B-roll/evidence ratio
- keyphrase-title count
- longest unchanged visual-structure duration

Pass targets:
ESSAY_STORY:
- avg visual change: 1.4-1.8 sec (soft range 1.2-2.1)
- talking head: 35-45% (soft range 30-50%)
- B-roll/evidence: 55-65% (soft range 50-70%)

TUTORIAL:
- avg visual change: 2.1-2.8 sec (soft range 1.8-3.2)
- talking head/overlay: 65-80%
- fullscreen evidence/demo: 20-35%

Quality overrides metrics. Never insert irrelevant imagery merely to hit a ratio.

## Rendering recommendation
Preferred programmable stack:
- FFmpeg: ingest, trims, audio, normalization, final encode
- faster-whisper or equivalent: word timestamps
- Remotion: typography, overlays, B-roll, screenshots, transitions, captions
- Optional subject segmentation: for UI-behind-speaker tutorial compositions

DaVinci Resolve scripting can be used as an alternate renderer, but keep `edit_plan.json` renderer-agnostic.

## Required agent behavior
When given a raw MP4:
1. Read this skill.
2. Probe the file.
3. Generate transcript.
4. Produce `edit_plan.json` before rendering.
5. Validate plan against mode metrics.
6. Render.
7. Inspect representative frames and final technical metadata.
8. If QA fails, revise once automatically before presenting the result.
