---
workflow: general-video
flow: companion
storyboard: no
message: "8일차 숏폼. 앞 2초 풀프레임 후킹 후 조직도 인트로. 인물 원본은 촬영 후 합성"
destination: reels
aspect: 1080x1920
language: ko
length: pending-source
---

## Intent

DaBDms5z83-의 2초 후킹(ECU→미디엄→펀치)과 DczH5_4ztdL의 5단 편집 레이어를 우리 릴스에 적용한다. POV 문구는 유지. 조직도 인트로는 2초 뒤에 붙인다. 인물 촬영본은 아직 없다.

정본: `.agents/skills/ai-school-video-edit/references/styles.json` → `day8_plus_edit_grammar`

## Assets

- videos/ai-employee-100/intro-wireframe/renders/org-intro-day08-1080x1130.mp4 — 조직도 인트로. 타임라인 2.0~7.0초.
- person.mp4 — 없음. 오늘 촬영 후 `assets/person.mp4`.

## Customizations

- 0~2초: 인물 풀프레임. 0.00 초근접 → 0.25 미디엄+POV → 1.15 펀치인. 조직도 없음.
- 2~7초: 3단(무대 0~1130 / 자막 y=1150 / 인물 카드 60,1235 960×640) + 조직도.
- 헤드카피: POV: AI 미친자가 / 저지른 일. 후킹 구간 0.25~2.00.
- 본편: 자막 키워드 확대, 제스처 펀치, 비트 스티커 1~3개, 기존 SFX.
- 음성은 꼬리물기 마스터 확정 후에만.

## Notes

- 원본 경로를 주면 tailbite → 2초 후킹 → 조직도 → 자막/스티커/프롬프트 → 4K.
- 인트로 재생성: `python3 videos/ai-employee-100/intro-wireframe/build_intro.py 8`
- 촬영: 턱 괴기·고개 돌리기·손가락 테이크, 하이앵글 자를 넓게.
