# Generate edit_plan.json
Read `SKILL.md`, `style_profile.json`, the transcript, and the source-video technical report.

1. Decide `ESSAY_STORY` or `TUTORIAL`.
2. Segment the transcript into semantic beats, not arbitrary fixed-length chunks.
3. Classify each beat into one scene type.
4. For every B-roll/evidence scene, write a concrete `asset_query` describing exactly what should be shown.
5. Use large hero typography only for hook/thesis/contrast/step pivots.
6. Calculate expected pacing metrics before render.
7. If metrics are outside the soft target, revise the plan only when it improves meaning.
8. Output JSON only, conforming to `schemas/edit_plan.schema.json`.
