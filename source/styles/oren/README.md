# Oren Reels Editor Skill v1

This package is a style/decision layer for Codex or Claude Code.

## Claude Code
Copy the folder `oren-reels-editor` to:
`.claude/skills/oren-reels-editor/`
Then keep `style_profile.json` and `schemas/` accessible to the project.

## Codex / coding agent
Keep `AGENTS.md` at project root and keep `SKILL.md` next to the project. Tell the agent to edit the supplied raw MP4 according to the skill.

## What still needs to be implemented for one-click raw-video editing
The skill defines decisions. A renderer/orchestrator must be connected:
1. Transcription with word timestamps (recommended: faster-whisper)
2. Asset provider (user library / licensed stock / generated assets / approved search workflow)
3. Renderer (recommended: Remotion + FFmpeg)
4. Optional subject segmentation for UI-behind-speaker tutorial shots

Once those are connected, the intended command is conceptually:
`edit-reel input.mp4 --style oren_reels_v1 --out output.mp4`

The important architectural rule is:
`raw MP4 -> transcript -> semantic edit plan JSON -> assets -> render -> QA -> final MP4`
