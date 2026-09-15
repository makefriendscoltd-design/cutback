# AI 학교 3일차 — Kallaway 레퍼런스 + 관제탑 인트로 (2026-09-15)

workflow: reel-reference-edit
flow: companion
status: 재편집본(미발행). 입력 `day3-basic-mix-20260915`(유튜브 예약본 기준)은 수정하지 않았다(심볼릭 링크로만 참조). 노션·유튜브 발행 안 함.
정본 방식: `day7-kallaway-ref-20260915`(v5 관제탑인트로믹스) build.py/prepare.py/verify_output.py 이식.

## 그대로 쓴 것 (변경 금지 항목)
- 음성·컷: day3 edit-plan.json 32.333초(970프레임), assets/voice-cut.wav, person.mp4. 음성 재컷 없음.
- 자막: captions.json 22청크 문구 그대로. 강조 단어 #ff434b.
- 헤드카피: "POV: AI 미친자가 / 저지른 일" 0~1초, Black 122px, 흰색+검정 스트로크 7px, top 360 (day7 .head CSS 그대로).
- 오디오: audio-settings.json(BGM dark-fast-128BPM −23.1dBFS RMS, whoosh 피크 0.206), click 0.12 / pop 0.16 / typing 0.08. prepare.py는 day7 것 그대로, 효과음 시점만 timing.json(이 편).

## 레이아웃
무대 0~1130 / 자막 y=1150 / 인물 카드 (60,1235) 960×640 radius 28, 카드 안 인물 object-position 50% 44%(스냅샷으로 찾음, `PERSON_POS=44`). 풀프레임 구간 자막 y=1340 흰색+스트로크.

## 관제탑 인트로 (0~5.647)
인트로가 5.647초로 day7 소스(5.0초)보다 길어서 새로 녹화했다: `_assets/hud-captures-20260915/main/index.html`을 day7 `record-main-all.js`로 22초 녹화 → `source-materials/hud-main-live-all-raw.webm`. 0~14.3초를 2.5배속 → `assets/hud-main-2_5x-source.mp4`(3840×2160, 5.73초, 정지·루프 없음). ffmpeg crop 2064×2160 → zoompan으로 `assets/hud-intro-1080x1130.mp4` 굽기. 0~2.9초 넓게, 2.9초("AI에 미쳐서")부터 CORE로 1.58배 푸시인(power2.out, 2.3초).

## 챕터
| 구간 | 대사 | 무대 |
|---|---|---|
| 0~5.65 | 여러분 제가 정말 미쳤나 봅니다 / AI에 미쳐서 AI 학교까지 만들고 있습니다 | 관제탑 2.5배속 + 헤드카피(0~1) + 2.9 CORE 푸시인 (검정) |
| 5.65~8.18 | 여기서는 카드뉴스도 자동으로 만들거든요 | 실제 카드뉴스 8장 4×2 순차 조립 + 카운터 0→8장 + 1장 초록 글로우 + "자동으로 완성 ✓" + 빨간 밑줄 |
| 8.18~10.38 | 첫 번째 코덱스를 켭니다 | STEP 01 + 터미널 목업 `$ codex` 타이핑 + Codex 타일 회전 진입 + 빨간 동그라미 |
| 10.38~13.18 | 두 번째 카드뉴스로 바꿀 글을 넣으세요 | STEP 02 + 원고 종이 날아들기 → 내 글.txt 창 4줄 + 글자 카운터 + 빨간 밑줄 |
| 13.18~15.05 | 이 프롬프트를 붙여넣습니다 | 프롬프트창 + ⌘V 키 누름 → 붙여넣기 하이라이트 + 전송 버튼 + 빨간 동그라미 |
| 15.05~17.27 | 세 번째로 글을 장마다 나누고 | STEP 03 + 첫 문장/핵심 내용/다음 행동 바가 빨간 컷선으로 갈라짐 → 화살표 → 실제 카드 3장(CARD 01~03) |
| 17.27~20.45 | 이미지로 저장하는 작업까지 시킵니다 | "이미지로 저장" + card-news/ 파일창 8행(실제 카드 썸네일) + 0→8 PNG 카운터 + 초록 글로우 + 빨간 동그라미 |
| 20.45~22.85 | AI 학교에서는 여러분들이 쓴 글로 | 검정 무대 하드컷 + 교실 실촬(vlog-classroom) + "AI 학교 수업" 라벨 + 흰 밑줄 |
| 22.85~24.49 | 카드뉴스를 만듭니다 | 검정. 내 글 → AI 학교 타일 → 실제 카드 3장 부채 (흰 연결선, 가운데 초록 글로우) |
| 24.49~27.01 | 내가 올릴 첫 콘텐츠부터 정해보고 싶다면 | 얼굴 풀프레임 |
| 27.01~29.39 | 댓글에 시작 남겨주세요 | "댓글에 “시작” / 남겨주세요" + 댓글 목업 "시작" 입력 + 게시 + 빨간 화살표 |
| 29.39~32.33 | 무료 워크북을 대댓글로 드리도록 하겠습니다 | 실제 card-08(댓글에 "시작" / 무료 워크북 받기) + "무료 워크북" 도장 + "↳ 대댓글로 드립니다" 칩 |

모든 무대는 챕터 동안 scale 1→1.035 드리프트로 계속 움직여 그래픽 정지 0.5초 초과가 없다.
목업(터미널·내 글.txt·프롬프트창·⌘V 키·파일창·댓글)은 제작 UI이고 실제 화면이라고 표기하지 않았다. 실제 소스는 관제탑 녹화, 카드뉴스 PNG 8장, 교실 실촬 3가지.

## 빌드
```
python3 build.py
/Users/apple/.venvs/cutback-mlx-video/bin/python prepare.py
cd /Users/apple/orca/projects/cutback
npx hyperframes@0.8.36 render videos/day3-kallaway-20260915/composition --quality standard --fps 30 --workers 1 --no-best-effort --output videos/day3-kallaway-20260915/renders/preview-1080.mp4
npx hyperframes@0.8.36 render videos/day3-kallaway-20260915/composition --quality high --resolution portrait-4k --fps 30 --workers 1 --no-best-effort --output videos/day3-kallaway-20260915/renders/picture-4k.mp4
cd videos/day3-kallaway-20260915
ffmpeg -y -i renders/picture-4k.mp4 -i assets/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest "renders/AI학교_03_기본형_관제탑인트로믹스_4K.mp4"
/Users/apple/.venvs/cutback-mlx-video/bin/python verify_output.py "renders/AI학교_03_기본형_관제탑인트로믹스_4K.mp4"
```

## 검증
- `renders/AI학교_03_기본형_관제탑인트로믹스_4K.verification.json`: 2160×3840, 970프레임, 32.333초, 디코드 통과, 믹스 상관 0.9998, passed=true.
- 1080 미리보기 2fps 전수 시트 `renders/sheet-1080_01.jpg`, `_02.jpg` 육안 확인(인물 얼굴·겹침·빈 무대·글자 잘림). 4K 헤드카피/STEP 03 프레임(`renders/q4k-head.jpg`, `q4k-split.jpg`) 확인.
- 미검증: 실제 청취(효과음 타이밍 체감), 상철 승인.
