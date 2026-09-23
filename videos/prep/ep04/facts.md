# 4편 팩트체크: 클로드 사이트 디자인 무료 도구 5개

확인일 2026-09-23 · 스타 수는 GitHub API로 이날 조회한 값 · 설치 테스트 경로는 `/private/tmp/ep04-install`(HOME을 격리해서 실제 `~/.claude`는 건드리지 않음)

## 1. 한눈에 보기

| # | 대본 이름 | 정확한 저장소 | 만든 곳 | 라이선스 | ⭐ (9/23) | 무료? | 판정 |
|---|---|---|---|---|---|---|---|
| 1 | 어썸 디자인 MD | [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) · [getdesign.md](https://getdesign.md) | VoltAgent | MIT | 117,427 | 무료 | ⚠️ 숫자와 "규칙"이라는 표현 수정 |
| 2 | 테이스트 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) · [tasteskill.dev](https://tasteskill.dev) | Leonxlnx | MIT | 89,451 | 무료 | ✅ |
| 3 | 임페커블 | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) · [impeccable.style](https://impeccable.style) | Paul Bakaus | Apache-2.0 | 70,034 | 무료 | ✅ (조건 하나 있음) |
| 4 | UI UX 프로 맥스 | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) · [uupm.cc](https://www.uupm.cc/) | nextlevelbuilder | MIT | 130,006 | 기본판 무료, 유료 Premium 따로 있음 | ✅ |
| 5 | img2threejs | [img2threejs/img2threejs](https://github.com/img2threejs/img2threejs) · [img2threejs.io](https://img2threejs.io/) | img2threejs | Apache-2.0 | 16,610 | 무료 | ⚠️ "사진"은 "이미지"로 |

이름이 헷갈리는 도구: 테이스트는 비슷한 이름의 저장소가 있음(codeswithroh/tastemaker ⭐409, senlindesign/taste-skill ⭐366). 스타 수와 "anti-slop(뻔한 AI 디자인 방지)"이라는 설명을 보면 Leonxlnx/taste-skill이 맞음. 어썸 디자인 MD도 파생 저장소(VoltAgent/awesome-claude-design ⭐3,857, 68개)가 있지만 73개짜리 원본은 awesome-design-md임. 나머지 셋은 이름이 겹치는 저장소가 없음.

## 2. 대본 주장별 판정

| 대본 문장 | 판정 | 근거 | 수정 제안 |
|---|---|---|---|
| "무료 도구 5개", "월급 0원" | ✅ | 5개 모두 오픈소스(MIT/Apache). 단, UUPM(UI UX 프로 맥스)은 유료 Premium판이 따로 있음(README "Basic vs. Premium"). 클로드를 쓰는 비용은 별도 | 그대로 써도 됨 |
| 어썸 디자인 MD: "애플, 스트라이프, 노션 같은 회사 디자인 규칙을 73개" | ⚠️ | README 배지와 목록은 73개([README](https://github.com/VoltAgent/awesome-design-md)), `design-md/` 폴더는 오늘 기준 74개. 계속 늘어남. Apple·Stripe·Notion 모두 있음. 다만 회사가 공식으로 낸 규칙은 아님. 공개된 웹사이트를 분석한 파일임(파일 이름이 `Apple-design-analysis`, Stripe는 `Stripi-Inspired…`, "An inspired interpretation"이라고 적혀 있음) | "애플, 스트라이프, 노션 같은 회사 사이트 디자인을 분석해서 **70개 넘게** 정리해 놓은 거예요." |
| "파일 하나 프로젝트에 넣고 '이거 따라 해' 하면 끝" | ✅ | README: "Copy a DESIGN.md into your project, tell your AI agent 'build me a page that looks like this'" | 그대로 |
| 테이스트: "클로드가 자꾸 무난한 레이아웃만 뽑는 걸 막아주는 규칙집" | ✅ | README: "stops the AI from generating boring, generic slop". SKILL.md에서 가운데 정렬 히어로, 똑같은 카드 3개, 보라색 그라데이션, Inter 폰트를 기본값으로 쓰지 말라고 막고 있음(ANTI-CENTER BIAS). 레이아웃뿐 아니라 폰트·색·모션까지 다룸 | 그대로 써도 되고, 넓히려면 "무난한 **디자인**" |
| 임페커블: "디자인 다듬어주는 건데, 브라우저에서 바로 보면서 고칠 수 있어요" | ✅ | README: "live browser iteration", `/impeccable live` = "iterate on elements in the browser". 명령 24개(polish, audit, critique 등)와 자동 검사 규칙 61개가 있음. 조건: live 모드는 **내 컴퓨터에서 개발 서버로 띄운 사이트에서만** 됨. 배포된 사이트는 검사만 가능 | 그대로 |
| UI UX 프로 맥스: "웹이랑 앱 화면 만들 때 어디에 뭘 놔야 되는지 그 패턴을 다 알고 있어요" | ✅ | 랜딩페이지 패턴 34개, UX 가이드 119개, 업종별 추론 규칙 192개. 지원 스택 22개에 웹(React, Next.js, Vue 등)과 앱(SwiftUI, React Native, Flutter, Jetpack Compose)이 모두 들어 있음 | "다 알고"는 과장된 느낌. 원하면 "패턴을 **수백 개** 갖고 있어요" |
| img2threejs: "자전거 사진 한 장 주면 클로드가 그걸 돌려볼 수 있는 3D를 코드로 만들어요" | ⚠️ | README: "one reference image → code-only procedural Three.js model". 데모에 "BMX Endurance Bike"가 있음([Live](https://img2threejs.io/#/demo/bmx-endurance)). 마우스로 돌려볼 수 있음. 하지만 그 데모의 참조 이미지는 실사 사진이 아니라 3D 렌더에 가까운 제품 이미지임. 한 번에 끝나지 않고 여러 번 비교하면서 맞춰 감. 안 보이는 면은 추정함("Honesty about limits") | "자전거 **이미지** 한 장 주면 클로드가 그걸 코드로 3D를 다시 만들어요. 마우스로 돌려볼 수 있어요." |
| "클로드로 만든 사이트" | ✅ | 5개 모두 Claude Code를 지원함(Codex, Cursor 등도 지원) | 그대로 |

## 3. Claude Code 설치 명령 (README 원문) + 실제로 돌려본 결과

| 도구 | README 명령(원문 그대로) | 실제 실행 결과 |
|---|---|---|
| 어썸 디자인 MD | 설치 없음. "1. Copy a site's `DESIGN.md` into your project root 2. Tell your AI agent to use it." 파일 본문은 이제 getdesign.md에 있음(예: https://getdesign.md/stripe/design-md) | `curl`로 저장소의 `design-md/stripe/DESIGN.md` 받아 봄. 487줄 받음. HTTP 200 ✅ |
| 테이스트 | `npx skills add https://github.com/Leonxlnx/taste-skill` / 하나만: `npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"` | `npx -y skills@latest add https://github.com/Leonxlnx/taste-skill --skill design-taste-frontend -a claude-code -y` 실행. "Installed 1 skill → ./.claude/skills/design-taste-frontend" ✅. 스킬 이름은 `design-taste-frontend`임 |
| 임페커블 | `npx impeccable install` 후 AI 채팅창에서 `/impeccable init`. 플러그인으로 설치: `/plugin marketplace add pbakaus/impeccable` 실행 후 `/plugin` 목록에서 설치 | `npx -y impeccable install --providers=claude --project -y` 실행. 스킬, 에이전트 4개, 훅이 `.claude`에 설치됨 ✅(엔진 v0.1.5 darwin-arm64). 추가로 `npx impeccable detect t.html`로 보라 그라데이션+Inter 테스트 파일을 검사함. low-contrast, overused-font, ai-color-palette 3건 잡음 ✅ |
| UI UX 프로 맥스 | `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill` → `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill` / CLI: `npm install -g ui-ux-pro-max-cli` → `uipro init --ai claude` | `npx -y -p ui-ux-pro-max-cli uipro init --ai claude` 실행. "installed successfully" ✅. `search.py "mobile e-commerce checkout" --domain ux` 결과 3건 ✅. 주의: ui-ux-pro-max 말고도 banner-design, brand, design, design-system, slides, ui-styling 스킬 6개가 **같이 깔림** |
| img2threejs | `git clone https://github.com/img2threejs/img2threejs.git ~/.claude/skills/img2threejs` → Claude Code에서 이미지 첨부 후 `/img2threejs Rebuild this object as a Three.js model, keep the proportions, angles, and colours.` | 임시 폴더에 clone ✅. `forge/state.py init` 정상 실행(Homebrew Python 3.14). 주의: README는 **Python 3.10 이상**을 요구하는데 맥 기본 `/usr/bin/python3`은 3.9.6임. 실제 3D 생성은 클로드 대화가 필요해서 미검증 |

설치 소개에서 알려 줄 점:
- impeccable은 `.claude/settings.local.json`에 훅(작업 때마다 자동으로 도는 검사)을 등록함.
- `npx skills add`는 설치가 끝나면 "Review skills before use; they run with full agent permissions"라고 경고함. 스킬이 에이전트 권한을 그대로 갖고 돈다는 뜻임.

## 4. 화면에 쓸 소재 아이디어

| 도구 | 소재 | URL |
|---|---|---|
| 어썸 디자인 MD | getdesign.md 브랜드 목록 스크롤, Apple·Stripe·Notion 상세 페이지(색 견본, 폰트 크기 미리보기, 다크모드) | https://getdesign.md · https://getdesign.md/apple/design-md · https://getdesign.md/stripe/design-md · https://getdesign.md/notion/design-md |
| 어썸 디자인 MD | README 상단 "DESIGN.md count 73" 배지 화면 녹화 | https://github.com/VoltAgent/awesome-design-md |
| 테이스트 | README 배너, 예시 결과물 이미지 floria-top/bottom | https://github.com/Leonxlnx/taste-skill/blob/main/assets/readme-banner.webp · https://github.com/Leonxlnx/taste-skill/tree/main/examples |
| 테이스트 | SKILL.md의 "Do not default to: AI-purple gradients, centered hero…" 줄 확대. "무난한 거 금지"가 한눈에 보임 | https://github.com/Leonxlnx/taste-skill/blob/main/skills/taste-skill/SKILL.md |
| 임페커블 | Neo Mirai 전후 비교 사례 | https://impeccable.style/cases/neo-mirai |
| 임페커블 | 터미널 녹화: `npx impeccable detect`가 "Purple/violet accent colors detected" 같은 경고를 잡는 장면. 직접 재현했으니 그대로 찍으면 됨 | 로컬 녹화 |
| UI UX 프로 맥스 | README 대표 이미지 screenshots/website.png, 3D 데모 gif(harness-village) | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/screenshots/website.png · https://cdn.nextlevelbuilder.io/skills/3dviz/harness-village.gif |
| UI UX 프로 맥스 | 공식 사이트 스크롤 | https://www.uupm.cc/ |
| img2threejs | **BMX 자전거 라이브 데모를 마우스로 돌리는 화면 녹화**. 대본의 "자전거"와 딱 맞음 | https://img2threejs.io/#/demo/bmx-endurance |
| img2threejs | 참조 이미지와 3D 결과를 좌우로 나란히 배치 | 참조: https://github.com/img2threejs/img2threejs-showcase/blob/main/public/references/bmx-endurance.jpg · 코드: https://github.com/img2threejs/img2threejs-showcase/blob/main/src/demos/bmx-endurance/createBmxEnduranceBikeModel.ts |
| img2threejs | 데모 갤러리 전체(Sony 이어버드, 칼, 도라에몽 집 등) | https://img2threejs.io/ |

## 5. 대본 수정본 (바뀐 곳만)

- 첫 번째: "애플, 스트라이프, 노션 같은 회사 사이트 디자인을 분석해서 70개 넘게 정리해 놓은 거예요."
- 다섯 번째: "자전거 이미지 한 장 주면 클로드가 그걸 코드로 3D를 다시 만들어요. 마우스로 돌려볼 수 있어요."
- (선택) 네 번째: "다 알고 있어요" → "패턴을 수백 개 갖고 있어요"
