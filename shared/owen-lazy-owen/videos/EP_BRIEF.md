# 편집 브리프 — 나민수 AI 학교 릴스 2~5탄 (공통)

너는 한 편(epNN)만 맡는다. 폴더: `videos/epNN/` (원본 `src/source.mp4` 이미 있음, 가로 1920×1080).
완성 기준 = 1편 `videos/owen-new/` (상철 승인본). 방법 정본 = `videos/OWEN_PIPELINE.md`. 이 편 준비물 = `videos/prep/epNN/` (`plan.md` 씬 계획·캡션·카페 골격, `facts.md` 사실 확인, `shots/` 실제 화면 캡처).

## 해야 할 것 (순서)
1. 받아쓰기: scratch venv `.venv/bin/python` (faster-whisper small, ko, word timestamps, vad on + 의심 구간은 vad off 재확인). `src/transcript.json`.
2. 컷: `owen-new/cut.py` 복사·수정. 촬영 전 잡음·NG·재시작·말 더듬은 구간 삭제, 0.28초 넘는 멈춤은 0.12초로. 같은 문장을 두 번 말했으면 **나중 테이크**를 쓴다. `cuts.json`, `assets/person.mp4`, `assets/voice.m4a`.
3. 사실 대조: 실제 발화와 `prep/epNN/plan.md`의 "촬영 전 대본 수정"을 비교. 틀린 사실을 그대로 말했으면 발화는 못 바꾸니 **자막은 발화대로, 화면 그래픽에는 틀린 수치를 쓰지 말고 facts.md의 확인값만** 쓴다. 대조 결과를 `REPORT.md`에 표로.
4. 조립: `owen-new/build.py`를 `build.py`로 복사해 이 편 내용으로 다시 짠다(`../nick-plugins-mg/build.py`를 lib로 import하는 구조 유지). `plan.md` 씬 계획을 따르되 **실제 화면 캡처(`prep/epNN/shots/`)를 UI 카드·풀 그래픽에 적극 사용**(스크롤·줌·파란 외곽선 드로우). 레퍼런스처럼 1.5~2.3초마다 화면 변화, 카드가 뜬 뒤에도 천천히 스크롤/줌.
5. 사운드: `owen-new/mix.py` 복사, SFX 시각을 이 편 씬 전환에 맞게. -14 LUFS.
6. 썸네일: `owen-new/cover/cover.html` 복사, `plan.md` 썸네일 카피로. 인물 누끼는 `npx hyperframes@0.8.62 remove-background`. 파란 박스판 + 빨간 박스판.
7. 캡션 `caption.md`: plan.md 초안을 실제 발화에 맞게 다듬고 **첫 줄은 CTA**("댓글에 ‘키워드’ 남겨주세요…"). 끝나면 humanize-korean 스킬 quick-rules(`~/.claude/skills/humanize-korean/references/quick-rules.md`)로 점검.
8. 카페 정리글 `cafe-post-final.md`: plan.md 골격 + facts.md의 **README 원문 명령어만**. **``` 코드펜스·줄 첫머리 #·--- 구분선·인라인 백틱 금지**(네이버에서 백틱이 그대로 보임) — 명령어는 빈 줄로 감싼 별도 문단. 이미지 자리는 `[이미지: 경로]`. humanize-korean 점검. (게시는 하지 마 — 메인이 한다)
9. `npx hyperframes@0.8.62 check` 0 error → 스냅샷 눈으로 확인 → render → `renders/AI학교_새로운영상N탄_<짧은영문슬러그>.mp4`로 복사.

## 절대 규칙 (상철 반복 지적)
- **자막은 무조건 한 줄.** nowrap + 930px 넘으면 자동 축소, 그래도 길면 단어 경계에서 카드 둘로 쪼갬. **렌더 후 실제 줄 수를 측정해서** REPORT에 적어라.
- **자막에 문장부호 없음**: . , ? ! " ' … 모두 렌더 단계에서 제거(그래픽 속 숫자 55,728 같은 건 예외).
- **자막은 첫 단어부터** 나온다(오프닝 헤드카피 중에도).
- 채널 토큰: 네이비 패널 `#07101c→#0d1b2e`, 강조 `#64d2ff`, 경고 `#ff3b30`, 자막 Pretendard 800 60px 흰색+검은 그림자. **노란색 금지.**
- **인스타 안전영역**: 글자·그래픽은 x 64~1016, y 300~1440, y≥1000에서는 x≤900. 1편은 UI 카드가 y150에서 시작해 위반이었으니 **UI 카드 top ≥ 300**으로 내려라(카드 300~820, 인물 카드 880~, card 모드 자막 y≈840 이음새, full 모드 자막 y≈1345). 댓글창 오버레이도 y≥300. 내용 덩어리 세로 중심 y≈830~880.
- 화면에 나오는 숫자·명령어·이름은 facts.md 확인값만. 지어낸 터미널 기록은 "예시"가 티 나게 일반적으로(구체 날짜·사람 이름 금지).
- 직장인 대상 예시 파일명은 실생활처럼(`기획안_최종.hwp` 등). "메모"라는 표현 금지.
- 업로드·게시·발송 금지. 원본 파일 삭제 금지.

## 마지막 보고 (10줄 이내)
렌더 경로·길이·LUFS, 컷 전후 길이, 발화 vs 사실 대조에서 걸린 것, 자막 줄 수 측정 결과, 안전영역 검사 결과, 남은 문제.
