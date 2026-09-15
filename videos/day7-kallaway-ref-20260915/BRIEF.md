# AI 학교 7일차 — Kallaway 레퍼런스 문법 테스트 v3 (2026-09-15)

**v3 변경(상철 지적 "헤드카피를 왜 마음대로 바꿨나")**: 무대 안 제목 "AI 학교에 / 글감 뇌가 생겼다"를 삭제하고 승인 헤드카피 "POV: AI 미친자가 / 저지른 일"을 정본 규칙(1초, Black 122px, 흰색+검정 스트로크 7px, top 360) 그대로 복원. 헤드카피는 어떤 스타일 실험에서도 바꾸지 않는다. 결과: `renders/AI학교_07_레퍼런스테스트_Kallaway_v3_관제탑인트로_승인헤드카피_4K.mp4`.


**v2 변경(상철 피드백 "맨 처음이 약함, 관제탑 2.5배속으로 와우포인트")**: 0~4.99초 상단 무대를 제목+타일+메모 부채 대신 실제 AI 학교 관제탑 녹화(`assets/hud-main-2_5x-source.mp4`, 2.5배속, 3840×2160)로 교체. ffmpeg zoompan으로 세로 1080×1130 클립(`assets/hud-intro-1080x1130.mp4`)을 미리 구워 넣었다. 0~2.65초 넓게 → 2.65초("AI에 미쳐서")부터 CORE로 1.58배 푸시인(power2.out, 2.3초). 흰 제목 "AI 학교에 / 글감 뇌가 생겼다"는 상단 그라데이션 위에 유지. 2.65~4.99 얼굴 풀프레임은 제거(관제탑 유지). 결과: `renders/AI학교_07_레퍼런스테스트_Kallaway_v2_관제탑인트로_4K.mp4`. v1 결과물은 같은 폴더에 남김.


workflow: reel-reference-edit
flow: companion
status: 테스트본. 정본 계보(day3 → day7 v4)와 별도. 노션 7일차 완성본을 교체하지 않는다.

레퍼런스: `reference-styles/2026-09-15/DaxdLQbOJXR/ANALYSIS.md` (Kallaway, 66초). 상철 지시: "노션 마지막 컨텐츠(7일차)로 테스트".

## 그대로 가져온 것
- 음성/컷: `day7-tailbite-20260915` voice-cut 30.933초, person.mp4 30fps, edit-plan.json. 음성 재컷 없음.
- 자막 35청크(1~3어절, `#ff434b` 강조 단어), 오디오 레시피(BGM dark-fast-128BPM −23.1dBFS, whoosh 피크 0.206, 클릭 0.12).
- 애셋 원본: 메모 카드 8장(`day7-basic-mix-v4/assets/generated/memo`), SNS 자동화학부 관제 캡처(`_assets/hud-captures-20260915/f03-t6000.png`), 교실 실촬 `vlog-discussion.mp4`.

## 레퍼런스에서 가져온 문법 (v4와 다른 점)
1. 3단 고정 레이아웃: 무대 0~1130 / 자막 y=1150 / 인물 카드 (60,1235) 960×640 둥근 카드. 카드 안 인물은 고정 크롭(object-position 50% 62%).
2. 애셋 없는 대사는 얼굴 풀프레임 펀치인(2.65~4.99, 22.29~25.57). 풀프레임 자막은 y=1340 흰색+스트로크.
3. 무대 배경이 챕터마다 종이색 ↔ 검정(18.4~22.29)으로 하드컷.
4. 애셋은 실제 화면 캡처 + 로고 타일 + UI 목업 + 빨간 낙서선. 스톡 영상 0.
5. 헤드카피는 승인 문구 "POV: AI 미친자가 / 저지른 일" 1초 오버레이 그대로(v3에서 복원).
6. 강조 소품: 카운터(0→8 files), 초록 글로우(글감 후보), 빨간 낙서선(밑줄·동그라미·X), 팝인 back.out(1.7).

## 챕터별 애셋
| 구간 | 대사 | 무대 |
|---|---|---|
| 0~2.65 | 여러분 제가 정말 미쳤나 봅니다 | 제목 타이포 + AI 학교 타일 팝 + 메모 3장 부채 |
| 2.65~4.99 | AI에 미쳐서 AI 학교까지 만들고 있습니다 | 얼굴 풀프레임 |
| 4.99~7.87 | 여기서는 글감도 AI가 메모에서 뽑아줍니다 | 메모 4×2 그리드 순차 조립 → 한 장 초록 글로우 → "글감 후보" 배지 |
| 7.87~9.54 | 첫 번째 코덱스를 켭니다 | STEP 01 + 터미널 목업(`$ codex` 타이핑) + Codex 타일 회전 진입 |
| 9.54~12.87 | 두 번째 글감으로 쓸 메모를 파일에 넣습니다 | STEP 02 + memos/ 파일창 8행 순차 + 카운터 + 메모 카드 날아들기 |
| 12.87~14.87 | 세 번째 이 프롬프트를 붙여 넣으세요 | STEP 03 + 프롬프트 입력창 타이핑 + 전송 버튼 + 빨간 동그라미 |
| 14.87~16.75 | 메모마다 직접 분류하지 않고 | 메모 3장 → 주제 A/B/C 폴더 도표에 빨간 X |
| 16.75~18.4 | 글감 목록을 뽑는 거예요 | "글감 목록 실시간" 제목 + 브라우저 프레임 안 실제 관제 캡처 펀치인·팬 |
| 18.4~22.29 | AI 학교에서는 여러분들이 적어둔 메모에서 콘텐츠를 찾습니다 | 검정 무대. 메모 3장 → 연결선 → AI 학교 타일 → 게시물 카드(교실 실촬) |
| 22.29~25.57 | 내 경험으로 어떤 글을 쓸지 정해보고 싶다면 | 얼굴 풀프레임 |
| 25.57~27.77 | 댓글에 시작 남겨두세요 | CTA 제목 + 댓글 목업("시작" 입력) |
| 27.77~30.93 | 무료 워크북을 대댓글로 드릴게요 | 워크북 카드 + "무료 워크북" 도장 + "대댓글로 드려요" 칩 |

목업(터미널·파일창·프롬프트·댓글·워크북)은 제작 UI다. 실제 화면은 관제 캡처와 교실 실촬 두 가지뿐이며, 목업을 실제 화면인 것처럼 표기하지 않았다.

## 빌드
```
python3 build.py            # composition/index.html + timing.json
/Users/apple/.venvs/cutback-mlx-video/bin/python prepare.py   # assets/mix.wav
cd /Users/apple/orca/projects/cutback
npx hyperframes@0.8.36 render videos/day7-kallaway-ref-20260915/composition --quality high --resolution portrait-4k --fps 30 --workers 1 --no-best-effort --output videos/day7-kallaway-ref-20260915/renders/picture-4k.mp4
cd videos/day7-kallaway-ref-20260915
ffmpeg -y -i renders/picture-4k.mp4 -i assets/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest "renders/AI학교_07_레퍼런스테스트_Kallaway_v1_4K.mp4"
/Users/apple/.venvs/cutback-mlx-video/bin/python verify_output.py "renders/AI학교_07_레퍼런스테스트_Kallaway_v1_4K.mp4"
```
`PERSON_POS=62 python3 build.py` 로 카드 안 인물 세로 위치(%)를 바꿀 수 있다.

## 런타임 메모
hyperframes 0.8.36은 video의 부모 박스 `top`/`transform`/`clip-path` 오프셋을 무시하고 보이는 영역 기준으로 그린다. 카드 크롭은 반드시 `object-position`으로 잡는다 (0%=원본 위, 62%=얼굴). 4일차 v4 분할창 방식과 같다.

## 검증
- `renders/AI학교_07_레퍼런스테스트_Kallaway_v1_4K.mp4.verification.json`: 2160×3840, 928프레임, 30.933초, 디코드 통과, 믹스 상관 0.9999.
- 1080 미리보기 2fps 전수 시트(`renders/sheet-1080_01.jpg`)와 4K 무대 크롭 2장 육안 확인.
- 미검증: 실제 청취(효과음 타이밍 체감), 상철 승인.
