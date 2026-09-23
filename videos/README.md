# Nick Saraev 릴스 모션그래픽 재구성 (HyperFrames)

인물 뒤에 연속으로 깔리는 화면(모션그래픽)을 전부 HTML+GSAP 씬으로 다시 만든 실험.
인물 레이어는 나민수 누끼 PNG로 대체(자리표시자), 음성은 원본 릴스 오디오(타이밍 맞춤용).

| 프로젝트 | 원본 | 길이 | 씬 | 자막 |
|---|---|---|---|---|
| `nick-plugins-mg/` | instagram.com/reel/DcwCCgivcIQ (4 plugins) | 49.6s | 19 서브컴포지션 | 영어 108개 |
| `nick-5plugins-ko/` | instagram.com/reel/Ddjfv-WP9yo (5 free plugins) | 57.5s | 21 서브컴포지션 | 한글 77개 |

## 구조

- `build.py` / `build2.py` — 씬 HTML + `index.html` 생성기. **수정은 여기서** 하고 다시 실행한다.
  - `build.py`는 라이브러리 겸용: 팔레트·폰트·`scene()` 래퍼·`host()`·`invader_html()` 등을 `build2.py`가 import해 재사용.
- `scenes/*.html` — 씬 하나 = 서브컴포지션 하나(`<template>` 안에 style/markup/script). 로컬 타임라인.
- `index.html` — 호스트. 트랙 0 씬, 트랙 1 인물, 트랙 8 자막(JS로 생성), 트랙 9 음성.
- 단어 타이밍: `../ref*/words.json` (faster-whisper small, 로컬).
- 원본 분석: `../ref*/sheets/sheet_*.png` (0.5초 간격 컨택트시트), `cuts.txt` (ffmpeg 장면 전환).

## 명령

```bash
python3 build.py            # (build2.py) 씬 재생성
npx hyperframes@0.8.62 check
npx hyperframes@0.8.62 snapshot --at 2.6,8.0,15.2
npx hyperframes@0.8.62 preview --background   # Studio
npx hyperframes@0.8.62 render                 # renders/*.mp4
```

## 씬 유형 (두 릴스 공통 문법)

- **th-dark / th-light** — 위 40%에 카드(터미널·차트·문서), 아래에 인물. 자막 sans 64px, y=860.
- **punch** — 인물 풀프레임 줌인, 자막 serif italic 하단(y=1300), 강조어 그라데이션.
- **풀그래픽** — 인물 없음. 제목 씬(`THE Nth` + 앱 아이콘 + 이름), 문서 스크린샷 재구성 + 주황/노랑 외곽선 드로우, 차트/그래프 성장, 프로그레스바+카운터.
- 반복 모티프: 픽셀 인베이더 마스코트(CSS grid), Silkscreen 픽셀 타이틀, 베이지/네이비/다크/화이트/탄 5색 배경 로테이션.
