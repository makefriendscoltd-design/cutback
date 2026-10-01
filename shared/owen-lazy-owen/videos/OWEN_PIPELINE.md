# 나민수 채널 릴스 — Owen 스타일 제작 파이프라인

## 현재 승인 포맷 — 2026-10-01, 7탄 v3

이 절이 아래 과거 수치·오프닝 규칙보다 우선한다. 실행 예제 정본은 `videos/ep07-v3/`의 `build.py`, `cut.py`, `mix.py`다. 사용자 승인: “굿 이런 포맷 커밋하고 다음 영상 제작해 쭉”.

- **인물 전체화면 → 축소하며 상단 자료 등장 → 다시 인물 확대**를 내용에 맞게 반복한다. 카메라 함수를 복사하는 것만으로 적용했다고 판단하지 않는다. 각 장면의 `LAYOUT`을 명시하고 `PRESENTER_ONLY` 구간을 둔다. 승인본은 49.05초 중 full 19.19초, 13회 전환이다.
- 기존 Owen의 `camBox`/`camImg`/`camZoom` 기하 전환을 사용한다. full/card 전환은 0.3초 `power2.inOut`, full 줌은 1.1 정도. 설명·강조는 인물 단독, 실물 자료가 필요할 때 card로 축소한다. 레퍼런스 릴스의 다른 디자인으로 갈아끼우지 않는다.
- 첫 프레임부터 한국어 후킹과 인물, 첫 대사 자막을 표시한다. 외부 원본의 후킹 취지를 살려 번역하되, 실제 발화와 확인된 사실에 맞춘다. 영어 픽셀 로고만 띄우며 인물을 숨기는 도입으로 되돌리지 않는다.
- card 자료는 x64~1016/y300~820, 인물 card는 (40,880)/1000×1040. 자막은 card y840, full y1345, 한 줄 Pretendard800/60px. y1000 아래 텍스트는 x900 안쪽. 전환 중에는 자막을 y1345에 유지하고 축소가 끝난 뒤 y840으로 옮겨 얼굴을 가로지르지 않게 한다. 시안/네이비 토큰 유지.
- 컷은 ASR 시작 시각만 믿지 않는다. 뒤의 완성 테이크를 선택하고 음절 경계·파형·재전사를 대조한다. 0.28초 넘는 쉼은 발화 손상 없이 약0.12초로 줄이되, 단어 내부 쉼도 확인한다. 클릭 방지 페이드는 말끝을 자르지 않는 범위로 둔다. 재전사에 문장이 있다는 이유만으로 청취 품질 통과라 보고하지 않는다.
- 실제 촬영본의 대사와 CTA가 우선한다. 1편에 CTA 두 버전을 중복 제작하지 않는다. 원본·기존 렌더는 보존한다.
- 검증: `python3 videos/check_owen_camera.py videos/epNN` → 실제 폰트 자막 검사 → HyperFrames check → 장면/전환 중간 스냅샷 → 렌더 → 실제 MP4의 전환 전·중·후 프레임/전체 디코딩/음량 확인. full 노출·전환 숫자는 고정 화면 회귀를 막는 보조값이고, 실제 화면 검수를 대신하지 않는다.
- 음성 직접 청취가 불가능하면 파형/독립 ASR 범위와 청취 미검증을 구분한다. 렌더는 `python3 videos/render_serial.py --project videos/epNN --output renders/<파일>.mp4`로 GPU 동시 실행을 막는다. 원본 다운로드·조사·빌드는 별도 편에서 병행 가능하다.
- 이번 “쭉 제작”의 범위는 촬영본이 있는 후속편 MP4 제작이다. 외부 게시·노션 업로드·카페·유튜브 발행은 별도 요청을 기다린다. 창을 열지 않고 헤드리스로 작업한다.


2026-09-23 첫 편(「클로드 코드 플러그인 5개」, `owen-new/`)으로 확정한 방식. 새 촬영본은 이 순서 그대로 간다.
Public handoff scope: local editing and rendering only; historical publishing destinations are omitted.

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

## Publishing integrations — excluded from public handoff

Internal destination/account identifiers and posting commands are not part of this style package. The original local document is unchanged. All editing, composition, sound and validation sections above are retained.

## 커밋하지 않는 것
원본·렌더·레퍼런스 릴스(저작권), 폰트·오디오 에셋. `videos/.gitignore` 참고.
