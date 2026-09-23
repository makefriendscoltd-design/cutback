# 3편 팩트체크 — 하이퍼프레임즈 (HyperFrames)

확인일: 2026-09-23 (KST). 확인 경로: GitHub API(`gh api repos/heygen-com/hyperframes`), README 원문, 공식 문서(hyperframes.heygen.com), npm, 로컬 CLI `npx hyperframes@latest` (v0.8.63).

## 1. 기본 사실

| 항목 | 확인값 | 출처 |
|---|---|---|
| 저장소 | github.com/heygen-com/hyperframes (HeyGen 조직) | https://github.com/heygen-com/hyperframes |
| 공개일 | 2026-03-10 저장소 생성 | GitHub API `created_at` |
| 라이선스 | Apache-2.0 | https://github.com/heygen-com/hyperframes/blob/main/LICENSE |
| GitHub 별(스타) | **52,521개** (2026-09-23 조회). 포크 4,793개 | GitHub API `stargazers_count` |
| 한 줄 소개 | "Write HTML. Render video. Built for agents." | README |
| 원리 | HTML·CSS·미디어·애니메이션을 결정적(같은 입력 = 같은 영상) MP4로 렌더. 헤드리스 크롬으로 프레임을 찍고 FFmpeg로 인코딩 | README 32, 232행 |
| 요구사항 | Node.js 22+, FFmpeg | README "Requirements" |
| 스킬 수 | 공개 스킬 **21개** (repo `skills/` 폴더 21개, README "ships 21 skills") | https://github.com/heygen-com/hyperframes/tree/main/skills |
| 기본 설치 시 | 전부가 아니라 **코어 세트**만 설치. 나머지 제작 워크플로는 필요할 때 라우터(`/hyperframes`)가 자동 설치 | README 44, 58~60행 |
| 이 맥 설치 현황 | ~/.claude/skills 에 14개 (코어 세트 + figma, general-video, motion-graphics, product-launch-video) | 로컬 `ls` |
| 최신 버전 | npm 0.8.63 (2026-09-23 배포. 브리프의 0.8.62보다 하나 올라감) | `npm view hyperframes` |
| 비용 | 오픈소스, 로컬 렌더 무료. 단 **HeyGen 클라우드 렌더(`hyperframes cloud render`)는 크레딧 유료**. AWS Lambda 렌더도 있음(AWS 비용 본인 부담) | skills/hyperframes-cli/references/cloud.md 3, 13행 |
| Studio | 브라우저 편집 화면. 타임라인에서 이동·트림·분할, 자막·오디오 편집 가능. 상태 "Available, evolving" | README Stack 표, https://hyperframes.heygen.com/studio/timeline |

21개 목록: embedded-captions, faceless-explainer, figma, general-video, hyperframes, hyperframes-animation, hyperframes-audio, hyperframes-cli, hyperframes-core, hyperframes-creative, hyperframes-keyframes, hyperframes-registry, hyperframes-studio, media-use, motion-graphics, music-to-video, pr-to-video, product-launch-video, remotion-to-hyperframes, slideshow, talking-head-recut.
참고: README 58행에 "`--all` installs all 20"이라는 오타성 문구가 한 곳 있음. 폴더 수와 README 다른 두 곳은 21.

## 2. 대본 문장별 판정

| # | 대본 문장 | 판정 | 근거 / 수정안 |
|---|---|---|---|
| 1 | 오늘 AI 직원 뽑았습니다. 영상 편집 담당이요. | ⚠️ | 비유라 괜찮음. 그대로 가도 됨 |
| 2 | 프리미어 안 켭니다. | ⚠️ | 주장이 아니라 연출. 다만 아래 7번처럼 "프리미어 완전 대체"로 들리지 않게 조심 |
| 3 | 하이퍼프레임즈라고, AI 아바타 만드는 헤이젠이 오픈소스로 풀었습니다. | ✅ | heygen-com 조직 저장소, Apache-2.0, 문서도 hyperframes.heygen.com. https://github.com/heygen-com/hyperframes |
| 4 | 깃허브 별이 벌써 4만 개가 넘어요. | ⚠️ | 틀린 말은 아니지만 너무 낮게 잡음. 현재 52,521개 → **"별이 벌써 5만 개가 넘어요"** 추천 (3월 공개라 "벌써"도 맞음). 업로드 직전 한 번 더 확인 |
| 5 | 영상을 웹페이지처럼 코드로 짜요. | ✅ | 영상 = HTML 파일 + data 속성. README "Define a video as HTML" |
| 6 | 클로드 코드한테 "…세로 영상 만들어…" 말하면 코드로 짜고 MP4로 뽑아줍니다. | ✅ | README "Use it … from AI coding agents with skills", `npx hyperframes render` → MP4. Claude Code 지원 명시 (README 52행). 단 렌더에 FFmpeg·Node 22+ 필요 |
| 6-a | (예시 프롬프트) "핵심 단어는 노란색" | 🚩 채널 메모 | 우리 채널 자막 강조색은 파랑(#64d2ff). 예시 문장이라 사실 오류는 아님. 화면 속 결과물이 파랑이면 말과 화면이 어긋나니 촬영 전 결정 필요 (수정은 안 함) |
| 7 | 그러니까 프리미어 켤 필요가 없어요. | ⚠️ | 아래 10번(촬영본 편집기는 아님)과 부딪힘. **"이런 영상은 프리미어 켤 필요가 없어요"**처럼 범위를 좁히는 게 안전 |
| 8 | 제 영상도 여기에 클립 넣고 "여기서 자르고 여기 제목 띄워" 하면 됩니다. | ✅ | 영상 클립 삽입·자르기 지원. 토킹헤드 재편집 전용 스킬 `talking-head-recut` 있음, Studio 타임라인에서 트림·분할 가능 |
| 9 | 스킬 21개가 같이 들어 있어서 그냥 깔면 클로드 코드가 알아서 씁니다. | ⚠️ | 21개는 맞음. 다만 기본 설치는 **코어 세트만** 깔리고 나머지는 필요할 때 자동으로 설치됨. 수정안: **"스킬이 21개라, 깔아두면 클로드 코드가 필요한 걸 알아서 꺼내 씁니다"** |
| 10 | 대신 촬영 영상을 손으로 만지는 편집기는 아니에요. | ⚠️ | Studio(브라우저 편집 화면)에 타임라인 트림·분할·자막 편집이 있음. 완전히 "손으로 못 만진다"는 틀림. 수정안: **"대신 프리미어처럼 촬영본을 손으로 다듬는 편집기는 아니에요"** |
| 11 | 자막, 모션그래픽, 설명 영상처럼 규칙이 있는 편집에 강합니다. | ✅ | 공식 스킬 구성이 embedded-captions, motion-graphics, faceless-explainer, slideshow 등. README "What You Can Build" |
| 12 | 무료고요. | ⚠️ | 오픈소스(Apache-2.0)라 로컬에서 쓰면 무료. HeyGen 클라우드 렌더는 크레딧 유료. 수정안: **"내 컴퓨터에서 돌리면 무료고요"** |
| 13 | 설치하는 법 정리해 놨어요. 댓글에 편집이라고 남겨주세요. | — | CTA. 사실 확인 대상 아님. 아래 설치 명령을 자료로 쓰면 됨 |

제목 "클로드 코드로 영상 편집하는 법" — ⚠️ 영상 "제작" 도구에 가까움. 10번 멘트와 균형 맞추려면 "영상 만드는 법"도 고려.

## 3. 공식 설치 명령 (README·Quickstart 원문 그대로)

Claude Code 같은 에이전트에서:

```bash
npx skills add heygen-com/hyperframes
```
- 선택 화면이 뜨면 **Core Skills** 그룹만 고르면 됨 (README 원문: "the Core Skills group is all you need").
- 에이전트·비대화형 실행은 README 권장:
```bash
npx hyperframes skills update
```
- 21개 전부 설치:
```bash
npx skills add heygen-com/hyperframes --all
# 또는
npx hyperframes skills
```

그다음 Claude Code에 이렇게 말하기 (README 예시 프롬프트):
> Using `/hyperframes`, create a 10-second product intro with a fade-in title, a background video, and subtle background music.

CLI로 직접:
```bash
npx hyperframes init my-video
cd my-video
npx hyperframes preview      # preview in browser with live reload
npx hyperframes render       # render to MP4
```
**Requirements:** Node.js 22+, FFmpeg

출처: https://github.com/heygen-com/hyperframes#readme , https://hyperframes.heygen.com/quickstart

## 4. 화면에 띄울 소스

| 소스 | URL | 쓸 곳 |
|---|---|---|
| GitHub 저장소 (별 개수 · HeyGen 로고) | https://github.com/heygen-com/hyperframes | 3~4번 "헤이젠이 풀었다 / 별 5만" |
| README 데모 GIF (왼쪽 HTML → 오른쪽 영상) | https://github.com/heygen-com/hyperframes/blob/main/docs/public/images/hyperframes-logo-motion-1280-trimmed.webp | 5번 "웹페이지처럼 코드로 짠다" |
| skills 폴더 (21개 목록) | https://github.com/heygen-com/hyperframes/tree/main/skills | 9번 "스킬 21개" |
| 공식 문서 첫 화면 | https://hyperframes.heygen.com/introduction | 도구 소개 |
| Quickstart | https://hyperframes.heygen.com/quickstart | 설치 CTA |
| Showcase (완성 영상 모음) | https://hyperframes.heygen.com/showcase | 11번 "자막·모션그래픽에 강함" B-roll |
| Catalog (블록·차트·전환 효과) | https://hyperframes.heygen.com/catalog/blocks/data-chart | 11번 보조 |
| Studio 타임라인 문서 | https://hyperframes.heygen.com/studio/timeline | 8번 "여기서 자르고" / 10번 |
| 플레이그라운드 | https://www.hyperframes.dev/ | 브라우저에서 바로 보는 장면 |
| 디자인 템플릿 갤러리 | https://www.hyperframes.dev/design | 스타일 예시 B-roll |
| 실제 Studio 화면 녹화 | 로컬 `npx hyperframes preview` | 가장 설득력 있는 화면. 자막 강조색 파랑(#64d2ff)으로 맞춰 녹화 추천 |
| 터미널 설치 장면 | 로컬 `npx skills add heygen-com/hyperframes` | 13번 CTA |

## 5. 미확인·주의

- 별 개수는 매일 늘어남. 업로드 직전 `gh api repos/heygen-com/hyperframes --jq .stargazers_count`로 재확인.
- HeyGen 클라우드 렌더 크레딧 단가는 확인 안 함 (대본에서 가격 언급 안 하므로 불필요).
- "AI 아바타 만드는 헤이젠"은 HeyGen의 대표 제품 설명으로 일반적으로 맞음. 이번 조사에서 별도 출처는 안 땄음 (https://www.heygen.com).
