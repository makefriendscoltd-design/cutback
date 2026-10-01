# Architecture

## Agent-first runtime
사용자가 Codex/Claude Code에서 작업할 때는 에이전트 자체가 semantic planner 역할을 한다.
따라서 외부 LLM API가 없어도 transcript + SKILL + runtime profile을 보고 edit_plan을 만들고 수정한다.

## Optional standalone runtime
완전 독립 CLI가 필요하면 PlannerAdapter 인터페이스를 구현하고 OpenAI/Anthropic 등 사용자가 연결한 API를 optional로 붙인다.
API key가 없으면 설치/빌드가 실패하면 안 된다.

## Modules
- probe: ffprobe metadata
- transcribe: word timestamps
- segment: semantic beats
- planner: scene types + captions + asset queries
- resolver: local/web/generated assets
- renderer: Remotion compositions
- finisher: ffmpeg audio/video normalization
- evaluator: style benchmark
- refiner: low subscore correction
