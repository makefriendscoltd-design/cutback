# jacklaydenn Reels Editor Skill v1

3개의 동일 크리에이터 레퍼런스를 분석해 만든 편집 Skill 패키지입니다.

## 파일
- `SKILL.md` — 실제 편집 판단 규칙
- `REFERENCE_ANALYSIS.md` — 3개 레퍼런스 비교 분석
- `style_profile.json` — 기계가 읽기 쉬운 스타일 파라미터
- `edit_plan.schema.json` — 편집 설계 JSON 스키마
- `AGENTS.md` — Codex/Claude Code 계열 에이전트 실행 지침

## 권장 사용 순서
1. 원본 9:16 영상을 프로젝트에 넣습니다.
2. 타임코드 transcript를 만듭니다.
3. `SKILL.md`를 기준으로 `edit_plan.json`을 생성합니다.
4. 사람이 edit plan을 한 번 검수합니다.
5. B-roll/스크린샷 자산을 확보합니다.
6. Remotion/FFmpeg 등의 렌더러로 최종 MP4를 생성합니다.

## 핵심
이 패키지는 특정 레퍼런스 한 편의 모양을 복사하는 것이 아니라, 세 영상에서 반복되는 '편집 판단법'을 재사용하도록 설계했습니다.
