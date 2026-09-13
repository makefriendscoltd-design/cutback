# 실행 계약

## 입력과 의존성

Python 3, ffprobe/ffmpeg, HyperFrames CLI가 필요하다. 구절 전사와 꼬리물기 음성 마스터를 먼저 준비한다. 파일 경로는 plan 기준 상대 경로 또는 절대 경로다. 영상은 로컬 링크로 연결되므로 다른 컴퓨터에서는 재료 경로를 다시 연결해야 한다.

`edit-plan.json` 필수 입력:

- `duration`: 정리된 음성의 실제 길이(초). `width:1080`, `height:1920`, `fps:30`은 디자인 기준이다.
- `audio_path`, `captions_path`, `font_path`, `gsap_path`: 실제 로컬 파일. 폰트·GSAP은 원 프로젝트의 합법적인 설치본을 재사용한다.
- `shots`: `id`, `source`, `source_start`, `output_start`, `duration`, `focal_x`, `focal_y`. 화면 타임라인을 연속으로 덮고 소스의 유효 구간을 넘지 않는다.
- 자막 파일은 `{"captions":[{"start":0.04,"end":1.06,"text":"실제 발화"}]}` 구조다. 시간은 음성 마스터 기준이다.
- `caption_style`: 생략하면 production-profile 기본값. 필요한 경우 `center_y`, `font_size`, `text_shadow`를 재정의한다.
- `headline`: 생략하면 제목을 추가하지 않는다. 있으면 `lines`와 `font_path`를 제공한다. `design:"impact"`, `duration`, `font_size`, `last_line_font_size`는 프로필 기본값을 따른다. 두 줄 크기는 사용자가 달리 요청하지 않으면 동일하다.

4K 출력은 plan을 두 배 크기로 고쳐 자막만 작아지는 방식으로 만들지 않는다. 디자인 기준 1080×1920과 `--resolution portrait-4k`를 함께 사용한다.

## 알려진 실제 사례

저장소 기준 `videos/day1-sc-vlog/`:

- `edit-plan-v5.json`: 사용자 피드백 반영 완료. 촬영 12파일에서 23컷, 49.6초, 40구절.
- `audio-prep/captions.json`, `audio-prep/provenance.json`: 실제 발화와 기존 음성 마스터 연결.
- `source-inventory.json`: SC에서 받은 촬영 파일 목록과 해시. 파일 자체는 커밋하지 않는다.
- `tools/build_composition.py`: 이 스킬의 정본 생성기로 연결하는 호환 실행기.
- `verification/`: 실제 렌더 검사 기록. 기존 v5는1080p이며 `day1-sc-vlog-v5-4k.mp4`가 별도 4K 출력이다.

헤드카피 원문 근거: 사용자 발화 2026-09-12T17:11:08.090Z, 세션 `01a09167-f1fd-7441-9189-e46ae8fdcc69`, JSONL line6343. 이번 세션에서 재사용을 명시하고 두 줄 같은 크기를 추가 확정했다. 다른 작업에서는 최신 사용자 지시를 확인한다.
