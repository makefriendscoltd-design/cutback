# Agent Instructions — jacklaydenn_reels_v1

When asked to edit a 9:16 talking-head reel using this style:

1. Read `SKILL.md` completely.
2. Obtain or create a timestamped transcript.
3. Split speech into semantic units, not arbitrary fixed-length chunks.
4. Label each unit with a rhetorical role.
5. Select EXPLAINER / HYBRID / STORY_MONTAGE per segment.
6. Produce `edit_plan.json` that conforms to `edit_plan.schema.json` before rendering.
7. Verify that every B-roll request has a semantic reason.
8. Prefer hard cuts; avoid decorative transitions.
9. Preserve the speaker as the visual anchor and return to the speaker after dense montage sequences.
10. Do not fabricate exact people, profiles, screenshots, metrics, posts, documents, or brands. Mark them `requires_exact_asset=true` when unavailable.
11. Do not use one constant cut frequency across the entire video. Increase visual density only when the rhetoric/story warrants it.
12. Before render, run the checklist in section 12 of `SKILL.md`.

Recommended render stack if code-based:
- transcription/alignment: timestamped ASR of choice
- composition: Remotion or equivalent frame compositor
- trim/audio/final encode: FFmpeg

The Skill defines editorial judgment. Rendering implementation should remain separate from the style rules.
