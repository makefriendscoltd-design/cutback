# AI 학교 6일차 — Kallaway 레퍼런스 + 관제탑 인트로 (2026-09-15)

workflow: reel-reference-edit
flow: companion
status: 재편집본. 유튜브 예약본(`day6-basic-mix-v4-20260915/renders/AI학교_06_기본형_메모안내문믹스_v4_4K.mp4`)은 교체하지 않음. 발행(노션·유튜브) 안 함.

정본 예시: `videos/day7-kallaway-ref-20260915` (7일차 승인 "Kallaway 레퍼런스 + 관제탑 인트로" v5).

## 그대로 가져온 것 (변경 없음)
- 컷/음성: `day6-tailbite-20260915` voice-cut·person.mp4, `edit-plan.json` 29.6초/888프레임. 재컷 없음.
- 자막 26청크 문구·타이밍: `day6-basic-mix-v4-20260915/captions.json` 그대로.
- 오디오 레시피: day7 `prepare.py` 그대로(BGM −23.1dBFS, whoosh 피크 0.206, click 0.12 / pop 0.16 / typing 0.08). 효과음 시점만 이 편 `timing.json`.
- 헤드카피: "POV: AI 미친자가 / 저지른 일" 0~1초, day7 `.head` CSS 그대로.

## 7일차 문법
3단 레이아웃(무대 0~1130 / 자막 y=1150 / 인물 카드 60,1235 960×640 r28, object-position 50% 50%), 풀프레임 자막 y=1340, 강조 #ff434b, 배경 종이색↔검정 하드컷, STEP 번호, UI 목업, 카운터, 초록 글로우, 빨간 낙서선. 인물 세로 위치는 이 편 소스에서 얼굴이 더 위에 있어 50%(스냅샷으로 결정, 7일차 62%).

## 챕터
| 구간 | 대사 | 무대 |
|---|---|---|
| 0~4.608 | 여러분 제가 정말 미쳤나 봅니다 / AI에 미쳐서 AI 학교까지 만들고 있습니다 | 관제탑 2.5배속 실녹화, 2.494초부터 CORE 푸시인 (0~1초 헤드카피) |
| 4.608~8.121 | 여기서는 AI가 내 메모를 찾아 안내문을 씁니다 | 메모 6장 그리드 → 검색창 "시간·장소·준비물" 타이핑 → 3장 초록 글로우+찾음 → 안내문 카드(page-08) 등장+밑줄 |
| 8.121~9.708 (검정) | 첫 번째 코덱스를 켭니다 | STEP 01, Codex 타일, OFF→ON 스위치(초록), `$ codex` 입력줄 |
| 9.708~12.728 | 두 번째 메모를 모아둔 폴더를 열어주세요 | STEP 02, 메모 폴더 아이콘, 커서 더블클릭+빨간 동그라미, 뚜껑 열리며 메모 5장 부채, 카운터 0→5장 |
| 12.728~16.835 | 세 번째 이 프롬프트로 메모 검색과 안내문 작성을 연결합니다 | STEP 03, 프롬프트 입력창 타이핑+전송, 점선 빈 노드 2개(13.25~14.66), ① 메모 검색 노드(스캔 바) → ② 안내문 작성 노드, 빨간 연결 화살표, 초록 글로우 |
| 16.855~19.542 (검정) | 다음에는 안내할 주제만 바꿔서 실행합니다 | "안내할 주제" 슬롯 준비물→시작 시간→신청 방법, ↻ 실행 버튼 펄스, 안내문 초안 카드 3장 적층, 순환 화살표 |
| 19.542~23.035 | AI 학교의 첫 준비도 내 기록을 꺼내 쓰는 것부터입니다 | 교실 실촬(AI 학교 현장) + 내 기록 메모 03/05 + 화살표 |
| 23.035~25.775 | 쌓아둔 메모로 뭘 만들지 막막하다면 | 얼굴 풀프레임 |
| 25.775~27.415 | 댓글에 시작 남겨주세요 | 댓글 목업에 "시작" 입력 + 빨간 동그라미 + 커서 게시 |
| 27.415~29.6 | 무료 워크북을 대댓글로 드릴게요 | 대댓글 카드 + 무료 워크북 파일칩 + 무료 도장 |

목업은 제작 UI다. 실제 화면은 관제탑 녹화와 교실 실촬 두 가지뿐이며, 목업을 실제 화면으로 표기하지 않았다. 워크북 내용·수치는 넣지 않았다(캡션에 없는 약속 금지).

## 빌드
```
python3 build.py; /Users/apple/.venvs/cutback-mlx-video/bin/python prepare.py
cd /Users/apple/orca/projects/cutback
npx hyperframes@0.8.36 render videos/day6-kallaway-20260915/composition --quality high --resolution portrait-4k --fps 30 --workers 1 --no-best-effort --output videos/day6-kallaway-20260915/renders/picture-4k.mp4
cd videos/day6-kallaway-20260915
ffmpeg -y -i renders/picture-4k.mp4 -i assets/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest "renders/AI학교_06_기본형_관제탑인트로믹스_4K.mp4"
/Users/apple/.venvs/cutback-mlx-video/bin/python verify_output.py "renders/AI학교_06_기본형_관제탑인트로믹스_4K.mp4"
/Users/apple/.venvs/cutback-mlx-video/bin/python scan_holds.py renders/<file>.mp4 4.608 23.035   # 무대 정지 0.5초 검사
```
관제탑 인트로 굽기: `ffmpeg -i day7.../hud-main-2_5x-source.mp4 -t 4.64 -vf "crop=2064:2160:100:0,zoompan=z='1+0.58*P':x='1032-iw/zoom/2':y='(1080-100*P)-ih/zoom/2':d=1:s=1080x1130:fps=30"` (P = 2.494초부터 power2.out 2.3초).

## 검증 (2026-09-15)
- `renders/AI학교_06_기본형_관제탑인트로믹스_4K.verification.json`: 2160×3840, 888프레임, 29.6초, 디코드 통과, 믹스 상관 0.99987, passed.
- 무대 정지 검사(`renders/holds-4.608-23.035.json`, `holds-25.775-29.6.json`): 최장 0.3초, 통과.
- 2fps 전수 시트: `renders/sheet-4k_01.jpg`(최종), `renders/sheet-1080_01.jpg`(수정 전 미리보기).
- 수정 이력: 인물 object-position 40→50%(입·마이크 보이게), S1 화살표 제거, S3 부채 카드 STEP 라벨 겹침 해소, CTA 동그라미 위치, 그리지 않은 낙서선 끝 점 노출 수정(opacity), STEP 03 빈 무대에 점선 빈 노드 추가.
- 미검증: 실제 청취(효과음 체감), 상철 승인.
