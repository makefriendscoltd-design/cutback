---
workflow: general-video
flow: companion
storyboard: no
message: "빈 회사 조직도가 오늘 출근할 AI 직원 자리로 펀치인된다"
destination: reels
aspect: 1080x1130
language: ko
length: 5s
---

## Intent

3~7일차 관제탑 인트로를 대체하는 상단 무대(1080×1130, 5초). 리빌딩된 AI 직원 양성학교 컨셉을 6팀 24자리 출근부 도면으로 보여 주고, 오늘 직무 자리로 카메라가 들어간다. 인물 촬영본은 아직 없다. 이 클립만 먼저 붙인다.

## Assets

- frames/01.png, 02.png, 03.png — 승인된 와이어프레임 3컷. 모션의 끝 상태.
- landing-video-broll/public/fonts/Pretendard-*.woff2 — 학교 정본 폰트.
- videos/ai-employee-100/assets/vendor/gsap.min.js — GSAP 3.14.2.

## Customizations

- 카메라: viewport-change (world scale+x+y). 2.57초에 오늘 자리로 펀치인.
- 디자인팀 4자리는 이미 출근한 상태로 팝. 오늘 자리는 펀치 직전 종이색.
- 프롬프트 첫 두 줄만 인트로에서 타이핑. 전문은 3단계 구간.
- LIVE 같은 오버레이 문구 없음.

## Notes

- 8일차 인물 원본 없음. person.mp4는 촬영 후 합성.
- 음성/BGM/SFX 믹스는 꼬리물기 마스터가 생긴 뒤에. timing.json에 시점만 적음.
- 정지 0.5초 이상 금지. 검증은 인코딩된 MP4.
