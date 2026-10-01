# Reusable short-form style packages

These packages contain the portable decision rules and small machine-readable
profiles needed to reproduce two short-form editing styles on another machine.

## Codex entry points

- Jack Laydenn: read `jacklaydenn/AGENTS.md`, then
  `jacklaydenn/SKILL.md`.
- Oren: read `oren/AGENTS.md`, then `oren/SKILL.md`.

Keep each package directory intact. The JSON profiles and schemas are addressed
relative to the package documentation. Oren also provides
`scripts/probe_video.py` for generating the source-video technical report used
by `prompts/generate_edit_plan.md`.

Reference video/audio, private source media, rendered outputs, dependencies,
and machine-local secrets are intentionally not included.

## Runnable engine

The sibling `../auto_editor_80plus` package is the executable path for these
two styles. See `../auto_editor_80plus/README.md` for dependency installation
and the `npm run edit` entry point.
