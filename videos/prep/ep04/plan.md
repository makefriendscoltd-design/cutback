# 4편 · 클로드로 만든 사이트 디자인 살리는 무료 도구 5개 — 선행 준비

CTA 키워드: **디자인** · 사실 확인·설치 검증: `facts.md` (5개 모두 임시 폴더에서 설치 확인, img2threejs 3D 생성만 미검증) · 실제 화면: `shots/`

## ⚠️ 촬영 전 대본 수정 제안
| 원래 대본 | 문제 | 바꿀 말 |
|---|---|---|
| 애플, 스트라이프, 노션 같은 회사 디자인 규칙을 73개 정리해 놓은 거예요 | 회사 공식 규칙이 아니라 공개 사이트를 분석한 파일. 개수도 73→74로 늘어나는 중 | 애플, 스트라이프, 노션 같은 회사 **사이트 디자인을 분석해서 70개 넘게** 정리해 놓은 거예요 |
| 자전거 사진 한 장 주면 클로드가 그걸 돌려볼 수 있는 3D를 코드로 만들어요 | 데모 원본은 실사 사진이 아니라 제품 이미지. 한 번에 나오지 않고 여러 번 맞춰 감 | 자전거 **이미지** 한 장 주면 클로드가 그걸 **코드로 3D로 다시 만들어요. 마우스로 돌려볼 수 있어요** |
나머지(테이스트·임페커블·UI UX 프로 맥스)는 그대로 찍어도 됨.
참고: 임페커블 "브라우저에서 보면서 고치기"는 내 컴퓨터에서 띄운 사이트 기준. UI UX 프로 맥스는 기본판 무료, 유료 Premium 별도.

## 씬 계획
| # | 대사 | 레이아웃 | 화면 | 자막 강조 |
|---|---|---|---|---|
| 1 | 오늘 AI 직원 뽑았습니다. 디자이너 다섯 명, 월급 0원 | 헤드카피 | 픽셀 "CLAUDE CODE" → 사원증 5장 부채꼴 + "월급 ₩0" | 다섯 명 / 0원 |
| 2 | 클로드로 만든 사이트 다 비슷하죠? | 풀 그래픽 | 1편 `o16-samey` 보라 그라데이션 사이트 6개 그리드 재사용 | 비슷하게 |
| 3 | 이 다섯이 그걸 고칩니다 | full 펀치 | 인물 | 고칩니다 |
| 4 | 첫 번째, 어썸 디자인 MD | 타이틀 → card | "첫 번째 · awesome-design-md" → `shots/awesome-design-md.png` 폴더 목록 스크롤, 카운터 0→70+ | 70개 넘게 |
| 5 | 파일 하나 넣고 "이거 따라 해" | card | 터미널: `DESIGN.md` 파일이 프로젝트에 떨어짐 → 프롬프트 "이거 따라 해" | 파일 하나 |
| 6 | 두 번째, 테이스트 | 타이틀 → card | `shots/taste.png` 배너 + 무난한 레이아웃 ✗ → 개성 레이아웃 ✓ 전환 | 무난한(빨강) |
| 7 | 세 번째, 임페커블 | 타이틀 → card | **실제 터미널 녹화**: `npx impeccable detect`가 보라 그라데이션·Inter 폰트·저대비 3건 잡는 장면 → `shots/impeccable-site.png` | 다듬어주는 |
| 8 | 네 번째, UI UX 프로 맥스 | 타이틀 → card | `shots/uiux-website.png` + 패턴 검색 결과("mobile e-commerce checkout") | 패턴 |
| 9 | 다섯 번째, 제일 신기한 img2threejs | 타이틀 | "다섯 번째 · img2threejs" | 제일 신기한 |
| 10 | 자전거 이미지 한 장 → 3D | 풀 그래픽 | 좌 `shots/bmx-reference.jpg` → 우 `shots/img2threejs-bmx.png` 3D 뷰어. **회전 녹화는 Orca 브라우저에서 드래그하며 따로 녹화 필요** | 3D |
| 11 | 마우스로 돌려볼 수 있어요 | full/그래픽 | 3D 자전거 회전 루프 | 돌려볼 수 |
| 12 | CTA · 댓글에 디자인 | full 펀치 | 댓글창 "디자인" + 5개 체크리스트 | 디자인 |

## 썸네일 카피
- 1줄: 클로드 사이트 디자인 / 박스: **살리는 무료 도구 5개**
- 아이콘 타일: 3D 자전거 + 픽셀 인베이더

## 인스타 캡션 초안
```
댓글에 ‘디자인’ 남겨주세요. 설치 방법 정리해서 보내드릴게요.

클로드로 만든 사이트, 다 비슷하게 생겼죠?
디자이너 다섯 명 뽑았습니다. 월급 0원.

1. awesome-design-md — 애플·스트라이프·노션 사이트 디자인을 분석한 파일 70개+
2. taste — 무난한 레이아웃만 뽑는 걸 막는 규칙집
3. impeccable — AI 티 나는 색·폰트를 잡아서 다듬어줌
4. UI UX Pro Max — 웹·앱 화면 배치 패턴 모음
5. img2threejs — 이미지 한 장을 코드로 3D로 다시 만듦

#클로드코드 #웹디자인 #바이브코딩 #AI디자인 #AI학교
```

## 카페 정리글 골격 (facts.md 설치 명령 = 임시 폴더에서 실제 실행 확인)
1. awesome-design-md: 설치 없음. 원하는 사이트 `DESIGN.md`를 프로젝트 루트에 복사 → "이거 따라 해"
2. taste: `npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"`
3. impeccable: `npx impeccable install` → 채팅창 `/impeccable init` (검사: `npx impeccable detect 파일.html`)
4. UI UX Pro Max: `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill` → `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill` (스킬 6개 같이 깔림 안내)
5. img2threejs: `git clone https://github.com/img2threejs/img2threejs.git ~/.claude/skills/img2threejs` → 이미지 첨부 후 `/img2threejs …` (Python 3.10+ 필요, 맥 기본 3.9는 안 됨)
6. 주의: 스킬은 에이전트 권한으로 돈다(README 경고)
