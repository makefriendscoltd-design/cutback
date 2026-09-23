# 제목
클로드 코드 처음이면 이 무료 플러그인 5개부터 (설치 명령어 정리)

# 본문

[이미지: cafe-images/00_thumbnail.png]

릴스 보고 '플러그인' 댓글 남겨주신 분들 보시라고 정리했습니다.

클로드 코드 처음 쓰시면 이 5개부터 깔고 시작하세요.
전부 무료고 저도 매일 이렇게 씁니다.

명령어는 전부 각 공식 저장소에 적힌 그대로 옮겼습니다.
`/`로 시작하는 건 클로드 코드 채팅창에 치고,
`npx`로 시작하는 건 터미널에 치시면 됩니다.

설치가 끝나면 클로드 코드를 한 번 껐다 켜주세요.

---

## 1. claude-mem
[이미지: cafe-images/02_claude-mem.png]

어제 한 작업을 기억해요.
프로젝트를 매번 처음부터 다시 설명할 필요가 없습니다.

설치 (클로드 코드 채팅창)
```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

설치 확인
`/plugin` 입력 → 설치된 목록에 claude-mem이 보이면 끝.

이렇게 써요
다음 날 새 세션을 열고 "어제 하던 거 이어서 하자"라고만 말하면 됩니다.

참고: 터미널에서 `npx claude-mem install`로 깔면 로그인과 기억 방식을 고르는 단계가 나옵니다. 처음이면 위 플러그인 방식이 간단해요.
공식 저장소: github.com/thedotmack/claude-mem

---

## 2. superpowers
[이미지: cafe-images/03_superpowers.png]

바로 코드부터 짜지 않아요.
계획 세우고, 저한테 먼저 물어보고, 그다음에 만듭니다.

설치 (클로드 코드 채팅창)
```
/plugin install superpowers@claude-plugins-official
```

설치 확인
`/plugin` 입력 → 설치된 목록에 superpowers가 보이면 끝.

이렇게 써요
"로그인 기능 만들어줘"라고 하면 바로 안 짜고 질문부터 던집니다. 답하다 보면 계획이 나와요.

공식 저장소: github.com/obra/superpowers

---

## 3. Context7
[이미지: cafe-images/04_context7.png]

옛날 문서 말고 최신 문서를 보고 코드를 짭니다.
버전 오류가 확 줄어요.

설치 (클로드 코드 채팅창)
```
/plugin install context7@claude-plugins-official
```

설치 확인
`/plugin` 입력 → 설치된 목록에 context7이 보이면 끝.

이렇게 써요
"Next.js 최신 문서 보고 만들어줘"처럼 라이브러리 이름을 같이 말해주세요.

참고: 터미널에서 `npx ctx7 setup`으로 설정하는 방법도 있습니다. 이건 로그인 과정이 있어요.
공식 저장소: github.com/upstash/context7

---

## 4. find-skills
[이미지: cafe-images/05_find-skills.png]

만들고 싶은 걸 말만 하면
맞는 스킬을 찾아서 설치까지 해줍니다.

설치 (터미널)
```
npx skills add vercel-labs/skills --skill find-skills -g -a claude-code
```

설치 확인 (터미널)
```
npx skills ls -g
```
목록에 find-skills가 보이면 끝.

이렇게 써요
"PPT 만드는 스킬 있어?"라고 물어보세요. 맞는 스킬을 찾아서 설치까지 제안합니다.

공식 저장소: github.com/vercel-labs/skills

---

## 5. frontend-design
[이미지: cafe-images/06_frontend-design_card.png]

앤트로픽 공식 플러그인입니다.
다 비슷해 보이던 AI 사이트가 확 달라집니다.

설치 (클로드 코드 채팅창)
```
/plugin install frontend-design@claude-plugins-official
```

설치 확인
`/plugin` 입력 → 설치된 목록에 frontend-design이 보이면 끝.

이렇게 써요
"카페 랜딩페이지 만들어줘"처럼 평소대로 시키면 됩니다. 디자인 방향부터 잡고 들어가요.

공식 저장소: github.com/anthropics/claude-plugins-official

---

## 5개 한 번에 복붙
[이미지: cafe-images/07_summary.png]


클로드 코드 채팅창에 한 줄씩 입력하세요.
```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
/plugin install superpowers@claude-plugins-official
/plugin install context7@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
```

find-skills는 터미널에서 따로 설치합니다.
```
npx skills add vercel-labs/skills --skill find-skills -g -a claude-code
```

다 깔았으면 클로드 코드를 껐다 켜주세요.

---

## AI 학교 무료 입학설명회

클로드 코드로 뭘 만들 수 있는지 더 알고 싶으시면
AI 학교 무료 입학설명회에 오세요.

10월 6일(화) 오후 9시
신청: https://aixschool.kr/admission/
