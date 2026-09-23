# 나민수 채널 릴스 — Owen 스타일 제작 파이프라인

2026-09-23 첫 편(「클로드 코드 플러그인 5개」, `owen-new/`)으로 확정한 방식. 새 촬영본은 이 순서 그대로 간다.
상철 지시: 영상 완성 → 노션 업로드 확인 → 네이버 카페 정리글 게시까지 한 번에.

## 0. 대본 선행 준비 (촬영 전에 가능)
대본(`쇼츠-스크립트/scripts-transcribed/나민수AI_대본_*.txt`)이 있으면 촬영 전에 끝낸다.
- 문장별 씬 계획: 문장 → 씬 종류(카드 UI / 타이틀 / 풀 그래픽 / 인물 펀치) → 화면 내용
- 사실 확인: 별 개수·수치·가격·출시일·설치 명령어는 공식 출처에서 확인. 확인 못 하면 화면·카페에 넣지 않는다
- UI 카드·타이틀 씬 HTML 초안, 썸네일 카피, 캡션, 카페 정리글 초안
촬영 후 남는 일은 컷·타이밍 맞추기·렌더·업로드뿐이다.

## 1. 컷 (`cut.py`)
- faster-whisper small, 한국어, 단어 타임스탬프 (`src/transcript.json`)
- RMS 에너지로 0.28초 넘는 멈춤을 찾아 0.12초로 줄임. 촬영 시작 전 잡음 구간은 통째로 삭제
- 말 더듬기·재시작은 VAD 끄고 다시 받아써서 확인
- 결과: `cuts.json` + `assets/person.mp4`(무음) + `assets/voice.m4a`

## 2. 조립 (`build.py`, HyperFrames 0.8.62)
- 씬 1개 = 서브컴포지션 1개. 공용 씬 라이브러리는 `nick-plugins-mg/build.py`
- 카메라 `CAM` 목록: `card`(위 UI 카드 + 아래 인물 카드) / `full`(인물 풀프레임, 줌 1.1~1.2) / `hide`(풀 그래픽)
- 가로 원본은 얼굴 좌표(`FACE`) 기준으로 9:16 크롭
- 오프닝 1.6초: ASCII → 픽셀 "CLAUDE CODE" 헤드카피

## 3. 채널 디자인 토큰 (7일차 Lazy Owen 확정본 기준)
- 배경 패널 네이비 `#07101c → #0d1b2e`, 파란 테두리·그리드
- 자막 Pretendard 800 60px, 흰색 + 검은 그림자, **한 줄**(930px 넘으면 자동 축소)
- 핵심어 `#64d2ff`, 경고어 `#ff3b30`. 노란색 쓰지 않음
- 자막 위치: card → y 712(카드 이음새), full/그래픽 → y 1373

## 4. 사운드 (`mix.py`)
- 소스 `projects/cutback/videos/_assets/audio-eleven-20260920` (자체 ElevenLabs 라이브러리)
- 배경음 -2dB, 사이드체인(threshold .1, ratio 2)으로 말할 때만 살짝 내림
- 효과음: 장면 전환 whoosh, UI 등장음, 체크 틱, 숫자 팝, 댓글 알림, 오프닝 임팩트
- loudnorm -14 LUFS

## 5. 썸네일 (`cover/cover.html` → 헤드리스 Chrome 스크린샷)
- 레퍼런스(Nick Saraev) 구도: 상단 로고 크게 / 인물 누끼(`hyperframes remove-background`) / 양옆 기울어진 아이콘 타일 / 흰 굵은 제목 + 박스 제목 / 하단 여백
- 박스 기본 `#64d2ff`, 빨강 버전(`?box=%23FF3B30`)도 같이 뽑음

## 6. 검증
`npx hyperframes@0.8.62 check` 0 error → 스냅샷 확인 → `render` → 렌더본 프레임과 LUFS 확인

## 7. 노션 업로드
- 페이지: ai 학교 › 촬영본 표. 촬영본이 올라와 있는 행을 찾는다
- 완성본 칸: mp4 + 썸네일 png / 리틀리 칸: 캡션(첫 줄 CTA "댓글에 ‘키워드’ 남겨주세요…")
- Orca 내장 브라우저에서 `HTMLInputElement.prototype.click`을 가로채 `orca upload`, 리틀리는 mouse 클릭 후 `orca inserttext`
- 새로고침 후 행 내용이 남아 있는지 확인 → `notion-upload.json`

## 8. 네이버 카페
- 카페 26321967(westudyssat) · 게시판 **163 「AI 자동화&수익화 정보」** (AI 글은 항상 여기)
- `aside`로 게시(u0 크레딧 부족하면 `aside repl`). ccidacafe 스크립트는 Windows 전용
- 설치 명령어는 실제 실행으로 검증, humanize-korean 점검, 게시 후 실제 URL을 열어 확인
- `aimax-crm-track emit` 기록 → `cafe-post.json`
- 인스타 자동답장 문구: "댓글 감사해요! … 정리해뒀어요 👉 <카페 URL>"

## 커밋하지 않는 것
원본·렌더·레퍼런스 릴스(저작권), 폰트·오디오 에셋. `videos/.gitignore` 참고.
