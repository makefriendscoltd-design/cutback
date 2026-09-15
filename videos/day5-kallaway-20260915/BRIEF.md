# AI 학교 5일차 — Kallaway 레퍼런스 + 관제탑 인트로 (2026-09-15)

workflow: reel-reference-edit · flow: companion · 상태: 렌더 완료, 발행 안 함(노션·유튜브 X)

정본 문법: `videos/day7-kallaway-ref-20260915` (build.py/prepare.py/verify_output.py). 레퍼런스 분석: `reference-styles/2026-09-15/DaxdLQbOJXR/ANALYSIS.md`.

## 기준 입력 (예약본 = day5-basic-mix-v5)
- 예약본 `day5-basic-mix-v5-20260915/renders/AI학교_05_기본형_제2의뇌믹스_v5_4K.mp4`: 44.933333초 1348프레임 = edit-plan.json duration 44.9333 / frames 1348. v5 verification 믹스 상관 0.9998.
- edit-plan.json, captions.json(49청크), captions.srt, audio-settings.json 은 v5에서 복사(수정 없음). 음성 `assets/voice-cut.wav` → `day5-tailbite-20260915/assets/voice.wav`(v5 링크와 동일 파일, cmp 일치), 인물 `person.mp4` → `day5-tailbite-20260915/assets/person.mp4`.
- v6 captions.json 은 v5와 바이트 동일. 참고만 하고 파일은 쓰지 않음.

## 인트로 관제탑
- 인트로 0~5.45초(첫 설명 캡션 "이 학교" 시작)라 day7 소스 5.0초로는 부족. 기존 raw webm도 12.53초(2.5배속 5.01초)라 모자라서, 같은 녹화 스크립트(`day7-kallaway-v2/source-materials/record-main-all.js`, 3초 부팅 뒤 ALL 탭)로 관제탑 HTML(`_assets/hud-captures-20260915/main/index.html`)을 16.2초 새로 녹화 → `source-materials/hud-main-live-all-raw.webm`.
- `assets/hud-main-2_5x-source.mp4`: raw 0~14초 2.5배속 → 5.6초 3840x2160 30fps (정지·루프 없음).
- `assets/hud-intro-1080x1130.mp4`: crop 2064x2160+108+0(CORE 중심 x=1140,y=980) → zoompan. 2.77초("AI에 미쳐서")부터 2.3초 power2.out 1→1.58배 푸시인.
- 헤드카피 "POV: AI 미친자가 / 저지른 일" 0~1초, day7 .head CSS 그대로.

## 레이아웃
무대 0~1130 / 자막 y=1150(58px Black) / 인물 카드 (60,1235) 960x640 r28, object-position 50% 40%(스냅샷으로 결정 — 62%는 이마가 잘림). 풀프레임 구간 자막 y=1340 흰색+스트로크. 강조 #ff434b. 챕터마다 무대 1.018배 느린 드리프트.

## 챕터
| 구간(초) | 대사 | 무대 |
|---|---|---|
| 0.00~5.45 | 여러분 제가 정말 미쳤나 봅니다 / AI에 미쳐서 AI 학교까지 만들고 있어요 | 실제 AI 학교 관제탑 녹화 2.5배속, 2.77초부터 CORE 1.58배 푸시인 |
| 5.45~9.29 | 이 학교 준비물 중에 버리기 아까워서 쌓아둔 파일이 있습니다 | 준비물 체크리스트 목업 + 휴지통에 빨간 X + 실제 아카이브 페이지 8장 낙하 더미·카운터 0→8 + 빨간 동그라미 |
| 9.29~14.99 | 예전에 쓴 글 고객한테 답했던 내용 생각나서 적어둔 메모요 | 실제 페이지 01·02→04(실사진)·03 3열 + 번호 + 빨간 밑줄 + 파일 행(페이지 06의 파일명·개수) + 동그라미 |
| 14.99~19.29 | AI한테 뭘 시켜야 할지 모르겠으면 그걸 먼저 꺼내 보려고요 | 실촬 vlog-records 세로 카드 + 입력창 목업 "뭘 시키지…" 타이핑 + 빨간 물음표 + 폴더에서 실제 페이지 3장 꺼내기 + 초록 글로우 |
| 19.29~22.30 | 내가 어떤 일을 했는지 어떤 이야기를 | 얼굴 풀프레임 (자막 y=1340) |
| 22.30~25.12 | 반복했는지 거기에 재료가 있을 수 있거든요 | 같은 질문 말풍선 목업 ×3 카운터 + 초록 글로우 + 빨간 괄호 → 실제 페이지 08(여기에 재료가 있습니다) + 동그라미 + "재료" 배지 |
| 25.12~30.66 | 그래서 첫 달에 내 기록을 AI가 찾아 쓰게 준비하는 제2의 뇌 과정을 | 검정 무대: "첫 달" 배지 → 실제 페이지 3장 노드 → 흰 연결선 → AI 노드(초록 회전 링) → 노드 초록 글로우 → "제2의 뇌 과정" 타일 + 빨간 밑줄 |
| 30.66~32.99 | 여기 학교 과정에 넣었습니다 | 실제 관제 캡처 main-t6000 CORE 펀치인 → main-t1500 "SECOND BRAIN ... MOUNTED" 3배 펀치인·팬 + v5 승인 배지 |
| 32.99~36.72 | 정리 못해서 남겨둔 파일이 이번엔 준비물이 됐네요 | 실제 페이지 6장 흩어짐 + 빨간 엉킨 낙서선 + "남겨둔 파일" → 실촬 vlog-files(교실) 카드 + "준비물" 도장 + 초록 체크 |
| 36.72~38.84 | 내 자료로 뭘 만들지 찾아보는 | 얼굴 풀프레임 (자막 y=1340) |
| 38.84~40.48 | 워크북부터 해보셔도 됩니다 | 워크북 카드 목업(내 자료로 뭘 만들지 / 시작 워크북) + 빨간 밑줄 |
| 40.48~41.98 | 댓글에 시작 남겨주세요 | CTA 제목 + 댓글 목업 "시작" 입력 |
| 41.98~44.93 | 무료 워크북을 대댓글로 드리도록 하겠습니다 | 워크북 카드 복귀 + "무료" 도장 + "↳ 대댓글로 드려요" 칩 |

목업(체크리스트·휴지통·말풍선·입력창·폴더·AI 노드·댓글·워크북)은 제작 UI이며 실제 화면 표기를 달지 않았다. 실제 화면은 관제탑 녹화, 관제 캡처 2장, 실촬 vlog-records/vlog-files, 실사진 기반 아카이브 페이지 8장(v5 승인 애셋). C2 파일 행의 파일명·개수는 v5 page-06 에 이미 있는 문구 그대로.

## 오디오
day7 prepare.py 그대로: BGM dark-fast-128BPM −23.1dBFS RMS, whoosh 피크 0.2060(audio-settings), click 0.12 / pop 0.16 / typing 0.08. 시점은 build.py가 쓴 timing.json(whoosh 14, click 43, pop 16, typing 1).

## 빌드
```
python3 build.py; /Users/apple/.venvs/cutback-mlx-video/bin/python prepare.py
cd /Users/apple/orca/projects/cutback
npx hyperframes@0.8.36 render videos/day5-kallaway-20260915/composition --quality high --resolution portrait-4k --fps 30 --workers 1 --no-best-effort --output videos/day5-kallaway-20260915/renders/picture-4k.mp4
cd videos/day5-kallaway-20260915
ffmpeg -y -i renders/picture-4k.mp4 -i assets/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest "renders/AI학교_05_기본형_관제탑인트로믹스_4K.mp4"
/Users/apple/.venvs/cutback-mlx-video/bin/python verify_output.py "renders/AI학교_05_기본형_관제탑인트로믹스_4K.mp4"
/Users/apple/.venvs/cutback-mlx-video/bin/python scan_holds.py "renders/AI학교_05_기본형_관제탑인트로믹스_4K.mp4" 0 44.93
```

## 검증
- verification.json: 2160x3840, 1348프레임, 44.933333초, decode_pass True, 믹스 상관 0.9998, passed True.
- 무대 정지 스캔(0~1130px): 최장 0.47초, pass.
- 2fps 전수 시트 `renders/sheet-4k-2fps_01.jpg`, `_02.jpg` 확인. hyperframes check 런타임 에러 0.
- 미검증: 실제 청취(효과음 타이밍 체감), 상철 승인.
