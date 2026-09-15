# AI 학교 4일차 — Kallaway 레퍼런스 + 관제탑 인트로 (2026-09-15)

workflow: reel-reference-edit
flow: companion
status: 재편집본. 발행(노션·유튜브) 안 함. 유튜브 예약본(`day4-basic-mix-v4-20260915/renders/AI학교_04_기본형_전자책믹스_v4_4K.mp4`)은 건드리지 않았다.

정본 방식: `day7-kallaway-ref-20260915` (v5 관제탑인트로믹스). 레퍼런스: `reference-styles/2026-09-15/DaxdLQbOJXR/ANALYSIS.md`.

## 그대로 가져온 것 (변경 금지 항목)
- 음성/컷: `day4-tailbite-20260915` voice-cut + person-source(30fps), edit-plan.json 31.0667초/932프레임. 음성 재컷 없음.
- 자막: `day4-basic-mix-v4-20260915/captions.json` 38청크, 문구 그대로. 강조 `#ff434b`.
- 헤드카피: "POV: AI 미친자가 / 저지른 일" 0~1초, day7 `.head` CSS 그대로(Black 122px, 흰색+검정 스트로크 7px, top 360).
- 오디오: day7 prepare.py 그대로. BGM dark-fast-128BPM −23.1dBFS, whoosh 피크 = audio-settings `sfx_target_peak`(0.206), click 0.12 / pop 0.16 / typing 0.08. 시점만 이 편 timing.json.
- 애셋: 전자책 페이지 8장·실사진 4장(`day4-basic-mix-v4/assets/generated/ebook`), 강의 실촬 `lecture-vlog.mp4`, 관제탑 2.5배속 녹화(day7 assets).

## 레이아웃
- 무대 0~1130 / 자막 y=1150 / 인물 카드 (60,1235) 960×640 radius 28, 카드 안 인물 `object-position: 50% 55%` (스냅샷으로 얼굴 위치 확인). 풀프레임 구간 자막 y=1340 흰색+스트로크.
- 인트로 0~5.0초("여기서는" 캡션 start): 관제탑 2.5배속 녹화를 ffmpeg로 1080×1130으로 구운 `assets/hud-intro-1080x1130.mp4`. 2.573초("AI에 미쳐서")부터 CORE로 1.58배 푸시인(power2.out 2.3초). 소스 5.0초 = 인트로 길이라 루프·정지 이음새 없음.
- 무대 요소는 `.drift` 래퍼에 챕터 길이만큼 scale 1→1.03 선형 드리프트(강의 실촬 장면 제외: 영상이 움직임) + 0.1~0.5초 간격 팝·낙서·카운터 이벤트.

## 챕터
| 구간 | 대사 | 무대 |
|---|---|---|
| 0~5.0 | 여러분 제가 정말 미쳤나 봅니다 / AI에 미쳐서 AI 학교까지 만들고 있는데요 | 관제탑 2.5배속 실녹화, 2.573부터 CORE 푸시인. 헤드카피 0~1 |
| 5.0~8.23 | 여기서는 내 글도 전자책도 만들 수 있어요 | 종이색. "AI 학교 · 전자책" 워드마크 → 원고 페이지(page-04)+"내 글" → 화살표 → 전자책 페이지 7장 스택 → 표지 초록 글로우 + "PDF 전자책" 배지 |
| 8.23~9.87 | 첫 번째 코덱스를 켭니다 | STEP 01 + 터미널 목업(`~/my-ebook $ codex` 타이핑) + Codex 타일 회전 진입 |
| 9.87~13.1 | 두 번째 전자책으로 묶을 원고와 사진을 넣어요 | STEP 02 + `my-ebook/` 파일창. 원고 페이지·실사진 카드가 날아와 창으로 빨려 들어감 → 원고 3행+사진 4행 순차, 카운터 0→7 files, 사진 행 빨간 동그라미 |
| 13.1~14.88 | 세 번째 이 프롬프트를 넣어보세요 | STEP 03 + 프롬프트창 "원고랑 사진으로 PDF 전자책 만들어줘" 타이핑 + 전송 버튼 + 빨간 동그라미 |
| 14.88~16.36 | 글과 사진을 배치하고 | 원고(page-04)·사진(cafe) 소스 → 점선 슬롯 페이지 템플릿에 텍스트 줄·사진 채움 → 실제 완성 페이지(page-05) 교체 + 초록 글로우 + "배치 완료" |
| 16.36~18.94 | PDF로 저장하는 작업까지 맡기는 거예요 | 검정 하드컷. 페이지 8장 4×2 조립 + 카운터 0→8 pages → PDF 타일로 빨려 들어감 → my-ebook.pdf → Codex 타일 + 연결 화살표 → 빨간 동그라미 + "저장 완료" |
| 18.94~21.06 | 책으로 묶는 방법이 막막했다면 | 얼굴 풀프레임 펀치인(1.14→1.19) |
| 21.06~23.44 | AI 학교에서 함께 만들어 보세요 | 검정. 강의 실촬 영상(흰 프레임) + AI 학교 타일 + "함께 만들기" 칩 + 연결선·밑줄 |
| 23.44~26.42 | 내 이름이 들어간 전자책을 만들고 싶다면 | 종이색. 표지(page-01) + "내 이름 지음" 빨간 동그라미 → 뒤표지(page-08 "내 이름이 들어간 첫 전자책") 날아듦 + 밑줄 + 초록 글로우 |
| 26.42~28.83 | 댓글에 학교 남겨주세요 | CTA 제목 "댓글에 “학교” / 입시 설명회 초대" + 댓글 목업("학교" 입력, 게시 버튼) |
| 28.83~31.07 | AI 학교 입시 설명회에 초대드리겠습니다 | 초대장 카드("AI 학교 / 입시 설명회 / 초대장") + "초대" 도장 + "↳ 댓글 남기면 초대드려요" 칩 |

목업(터미널·파일창·프롬프트·템플릿·PDF 타일·댓글·초대장)은 제작 UI다. 실제 화면은 관제탑 녹화와 강의 실촬뿐이며 실제 화면이라고 표기하지 않았다. 날짜·가격·인원 등 캡션에 없는 수치나 약속은 넣지 않았다(카운터 7 files / 8 pages는 화면에 보이는 애셋 수).

## 빌드
```
PY=/Users/apple/.venvs/cutback-mlx-video/bin/python
python3 build.py            # composition/index.html + timing.json
$PY prepare.py              # assets/mix.wav + audio-plan.json
cd /Users/apple/orca/projects/cutback
npx hyperframes@0.8.36 render videos/day4-kallaway-20260915/composition --quality standard --fps 30 --workers 1 --no-best-effort --output videos/day4-kallaway-20260915/renders/preview-1080.mp4
npx hyperframes@0.8.36 render videos/day4-kallaway-20260915/composition --quality high --resolution portrait-4k --fps 30 --workers 1 --no-best-effort --output videos/day4-kallaway-20260915/renders/picture-4k.mp4
cd videos/day4-kallaway-20260915
ffmpeg -y -i renders/picture-4k.mp4 -i assets/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest "renders/AI학교_04_기본형_관제탑인트로믹스_4K.mp4"
$PY verify_output.py "renders/AI학교_04_기본형_관제탑인트로믹스_4K.mp4"
$PY scan_holds.py "renders/AI학교_04_기본형_관제탑인트로믹스_4K.mp4" 5.0 31.0
```
관제탑 인트로 클립 재생성:
```
ffmpeg -i assets/hud-main-2_5x-source.mp4 -vf "crop=2064:2160:0:0,scale=4128:4320:flags=lanczos,zoompan=z='1+0.58*E':x='(1032+48*E)*2-iw/zoom/2':y='(1080-120*E)*2-ih/zoom/2':d=1:s=1080x1130:fps=30" -frames:v 150 -c:v libx264 -crf 12 -preset slow -pix_fmt yuv420p assets/hud-intro-1080x1130.mp4
# E = 1-(1-clip((t-2.573)/2.3,0,1))^2 , t = on/30
```
`PERSON_POS=55 python3 build.py` 로 카드 안 인물 세로 위치(%) 조정.

## 런타임 메모
hyperframes 0.8.36은 video 부모의 transform/top/clip-path 오프셋을 무시한다. 인트로 크롭은 ffmpeg로 굽고, 인물 카드는 object-position, 강의 실촬은 video 요소에 직접 left/top을 준다(드리프트 래퍼 밖).

## 검증
- `renders/AI학교_04_기본형_관제탑인트로믹스_4K.verification.json`: 2160×3840, 30fps, 932프레임, 31.0667초, 디코드 통과, 믹스 상관 0.99986, passed=true.
- 정지 스캔(`...4K.holds.json`, 5.0~31.0 무대 영역): 최장 12프레임(0.40초, 23.67) → 통과. 1차 4K에서 27.4초 0.6초 정지 발견 → CTA 드리프트 1.04 + 제목/댓글 펄스, 표지 흔들기 추가 후 재렌더.
- 인물 카드 위치: 42%·38%는 얼굴이 카드 아래로 밀려 입이 잘림 → 55%로 확정(스냅샷 2·11·26.1초 확인).
- 2fps 전수 시트: `renders/sheet-4k-2fps.jpg`(최종 4K에서 추출).
- 미검증: 실제 청취(효과음 타이밍 체감), 상철 승인. 발행 안 함.
