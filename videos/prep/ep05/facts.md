# 5편 팩트체크: 제브(Jev, TypeSafe AI)
확인일: 2026-09-23 · 판정: ✅ 맞음 / ⚠️ 표현 수정 필요 / ❌ 틀림 / ❓ 출처 못 찾음

## 0. 정체
| 항목 | 확인 결과 | 출처 |
|---|---|---|
| 제품명 | **Jev** (제브). TypeSafe AI의 첫 "System One" 모델. 버전 `jev-1.13.0`, 별칭 `jev-latest` | https://docs.typesafe.ai/models |
| 회사 | **TypeSafe AI** (typesafe.ai). 공동창업: Diogo Almeida, Erik Gafni, Sasha Sheng. 시드 4천만 달러(DCVC 리드) | https://finance.yahoo.com/technology/ai/articles/typesafe-ai-emerges-stealth-40m-190000776.html |
| 공식 발표 글 | "Introducing System One Models & Jev" (Diogo Almeida). 블로그 페이지 표시 날짜는 9/22(수정일로 보임) | https://typesafe.ai/blog/introducing-system-one-models-and-jev |
| 문서 | https://docs.typesafe.ai (색인: https://docs.typesafe.ai/llms.txt) | |
| 출시일 | **2026-09-15(미국 기준)**. 스텔스를 끝내고 투자 유치와 함께 공개. 한국 시간으로는 9/16 새벽. 일부 매체는 9/16로 적음 | Yahoo Finance(위), https://techstartups.com/2026/09/16/typesafe-ai-an-ai-startup-founded-by-chatgpt-co-inventor-emerges-from-stealth-with-40m-to-build-ai-thats-100x-faster-and-cheaper/ |

## 1. 대본 문장별 판정
| # | 대본 | 판정 | 근거 / 수정안 |
|---|---|---|---|
| 1 | "말을 안 해요. 판단만 합니다" | ✅ | 문서 원문: "returns a typed choice rather than free-form text". 글 생성은 아예 못 함 |
| 2 | "1인 사업자한텐 챗GPT보다 쓸모 있을 수 있어요" | 의견 | 사실 확인 대상은 아님. "분류·판단 일에 한해서"를 붙이면 안전함 |
| 3 | "챗GPT 만드는 방법 논문을 같이 쓴 디오고" | ✅ | **Diogo Almeida**. InstructGPT 논문 "Training language models to follow instructions with human feedback"(arXiv 2203.02155, 2022)의 저자 4번째. 사람 피드백으로 AI를 길들이는 방법(RLHF)을 다룬, 챗GPT의 바탕이 된 논문. 본인은 X에서 "After co-inventing ChatGPT"라고 씀. https://arxiv.org/abs/2203.02155 |
| 4 | "9월 15일에 나왔습니다" | ✅ | 미국 기준 9/15. (한국 시간으로는 9/16 새벽) |
| 5 | "예 아니오, 분류, 점수. 세 가지만" | ✅ | 문서의 질문 유형 3개: **Noul**(예/아니오 → '예'일 확률), **Choice**(보기 중 하나 고르기), **Score**(등급 매기기). https://docs.typesafe.ai/primitives |
| 6 | "얼마나 확신하는지도 같이 줍니다" | ✅ | 모든 답에 confidence(확신도)가 붙음. "so you can decide when to act and when to escalate" https://docs.typesafe.ai/confidence |
| 7 | "최대 200배 빠르고 400배 쌉니다(회사 발표)" | ⚠️ | 회사 표기가 여러 가지임. 홈페이지: **"193.6x Faster, 444.6x Cheaper."**(회사가 돌린 업무 테스트 평균, GPT-6 Astra·Fable 5.1과 비교). 발표 글: "40x-200x faster". 출시 트윗/보도: "20–200x faster, 40–400x cheaper". 모두 **회사 자체 측정**임. 수정안: "회사 발표로는 **최대 약 200배** 빠르고 **400배 넘게** 싸대요" 또는 "평균 193배 빠르고 444배 싸대요". https://typesafe.ai |
| 8 | "해외 유튜버가 이메일 천 개 분류, 7초에 9센트" | ❌/❓ | **유튜버 영상은 찾지 못함.** 숫자가 가장 비슷한 출처는 MindStudio 블로그: 이메일 1,000개에 분류 규칙 7개를 돌려서 순차 처리 약 70초, 병렬 처리 **약 6초, 9센트**. **7초가 아니라 6초.** https://www.mindstudio.ai/blog/jev-use-cases-automation (X 요약 글도 "6 seconds for $0.09": https://x.com/yuhasbeentaken/status/2101428662125854819) |
| 9 | "챗GPT 최신 모델은 같은 거 5분에 62센트" | ❌ | 같은 블로그 원문은 "A comparable **single-category** run on a **GPT 5.6-class model** took roughly 5 minutes and cost 62 cents". ① **최신 모델이 아님**: GPT-6 Astra가 이미 나와 있음(회사 비교 대상). ② **같은 작업이 아님**: 제브는 7개 규칙, GPT는 1개 카테고리. 수정안: "GPT-5.6급 모델로 분류 하나만 돌려도 5분에 62센트 나왔대요" |
| 10 | "카페 댓글·문자를 구매/환불/스팸으로 분류, 급한 거 1~5 점수" | ✅ (방식) | Choice(분류)와 Score(점수)로 그대로 할 수 있음. 공식 퀵스타트 예제도 "urgency"(급한가)와 "department"(어느 팀 담당인가) 분류임 |
| 11 | "급한 것만 제 폰으로 오게" | ⚠️ | 제브는 판단만 하고 **알림은 못 보냄**. 폰으로 보내는 건 Zapier(앱끼리 자동으로 이어주는 서비스)나 코드로 따로 연결해야 함. 실사례: Creator Magic 영상의 "two-step Zap" https://www.youtube.com/watch?v=3lBmrYFREZU . 수정안: "자동화 툴이랑 엮으면 급한 것만 폰으로 오게 할 수 있어요" |
| 12 | "한국어는 아직 완벽하지 않다고 문서에 써 있어요" | ✅ | 원문: "English is the primary training language… Other languages, including CJK scripts, are handled but not equally well; test on your own content before relying on Jev for a non-English workload". CJK는 한중일 문자. https://docs.typesafe.ai/models (Language support) |
| 13 | "꼭 내 데이터로 먼저 테스트" | ✅ | 위 문서가 직접 권고하는 내용 |
| 14 | "직접 가입은 아직 대기 명단" | ❌ | **9/20에 대기 명단 폐지.** TypeSafe 공식 X: "Jev is now available to everyone. No waitlist." 가입하면 5달러 무료 크레딧. https://x.com/typesafeai/status/2101786156572823624 , https://cryptobriefing.com/typesafe-jev-ai-public-access/ . 수정안: "지금은 누구나 바로 가입돼요. 5달러 무료 크레딧도 줘요" |
| 15 | "오픈라우터에서는 바로 쓸 수 있습니다" | ✅ | OpenRouter(여러 AI를 키 하나로 쓰게 해주는 중개 서비스) 공식 문서에 Jev 가이드가 있음. 모델 ID `typesafe/jev-1.13`, 별칭 `~typesafe/jev-latest`. https://openrouter.ai/docs/guides/community/typesafe-sdk |

## 2. 가격·스펙
| 항목 | 값 | 판정 | 출처 |
|---|---|---|---|
| 공식 가격 | 입력 100만 토큰당 **$0.042**, 출력 **무료** | ✅ | https://docs.typesafe.ai/models |
| 컨텍스트(한 번에 읽는 양) | 64k 토큰(state+질문 전부), state+가장 긴 질문은 32k | ✅ | 같은 곳 |
| 응답 속도 | 70ms~500ms(회사 발표) | ✅ | 발표 글 |
| OpenRouter 가격 | $0.042/M 입력, $0 출력, 9/18 등록 | ❓ | 3자 사이트에서만 확인함: https://jevaiguide.com/channels/openrouter/ . OpenRouter 모델 페이지가 우리 쪽 조회에서 404로 떴으니 **촬영 전에 브라우저로 직접 확인** |

## 3. 써보는 법 (문서 원문 그대로)
**A. 공식 API** (https://docs.typesafe.ai/introduction/quickstart, 키 발급: https://console.typesafe.ai/keys)
```bash
curl -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
  {
    "state": "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
    "model": "jev-latest",
    "questions": {
      "urgency": {
        "type": "noul",
        "instructions": "Does this message express urgency?"
      }
    }
  }
EOF
```
**B. OpenRouter** (https://openrouter.ai/docs/guides/community/typesafe-sdk). 주의: 일반 채팅 주소가 아니라 `/api/v1/systemone`로 보냄
```bash
curl https://openrouter.ai/api/v1/systemone \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "jev-1.13",
    "state": "I was charged twice for my subscription.",
    "questions": {
      "refund": {
        "type": "noul",
        "instructions": "Is the customer asking for money back?"
      }
    }
  }'
```
문서 예시 응답: `"answers": {"refund": {"type": "noul", "noul": 0.98}}`, `"usage": {... "cost": 0.00003}`
SDK: JS `@typesafe-ai/sdk`, Python `typesafe_sdk`. 기존 SDK는 `TYPESAFE_BASE_URL=https://openrouter.ai/api`만 바꾸면 OpenRouter로 감.

## 4. 화면 소스 아이디어
| 장면 | 소스 | URL |
|---|---|---|
| 오프닝 "말 안 하는 AI" | TypeSafe 홈 히어로 + "193.6x Faster, 444.6x Cheaper." 문구 | https://typesafe.ai |
| 만든 사람 | InstructGPT 논문 첫 장, 저자 줄의 "Diogo Almeida" 강조 | https://arxiv.org/abs/2203.02155 |
| 세 가지 출력 | 문서 Primitives 페이지(Choice / Score / Noul 카드) | https://docs.typesafe.ai/primitives |
| 확신도 | Confidence 문서 | https://docs.typesafe.ai/confidence |
| 속도·비용 그래프 | 홈페이지 "Workflow Intelligence vs. Cost" 차트, 회사 평가 사이트 | https://typesafe.ai , https://evals.typesafe.ai/ |
| 한국어 주의 | models 문서의 Language support 문단 캡처(CJK 줄 강조) | https://docs.typesafe.ai/models |
| 가입 | 콘솔 로그인 화면 + "No waitlist" 공식 트윗 | https://console.typesafe.ai , https://x.com/typesafeai/status/2101786156572823624 |
| 오픈라우터 | TypeSafe 제공사 페이지, Jev Lab 데모 | https://openrouter.ai/typesafe , https://openrouter.ai/labs/jev |
| 이메일 분류 실사례(B-roll) | Creator Magic "Jev Sorted 250 Emails for 1 Cent"(9/21, 인박스 게이트 + Zapier) | https://www.youtube.com/watch?v=3lBmrYFREZU |

## 5. 대본 수정 요약 (필수 3곳)
1. 이메일 테스트: "해외 유튜버" → **"해외 AI 블로그 테스트"**, **7초 → 6초**, "챗GPT 최신 모델" → **"GPT-5.6급 모델로 분류 하나만"**. 원래 유튜버 영상이라는 출처를 다시 찾지 못하면 이 표현을 써야 함
2. "직접 가입은 아직 대기 명단" → **"9/20부터 대기 없이 누구나 가입, 5달러 무료"**
3. "최대 200배/400배" → "회사 발표로 최대 약 200배 빠르고 400배 넘게 싸다" (자체 측정이라고 밝히기)

## 추가 확인 (메인 세션, 2026-09-23)
- OpenRouter 모델 페이지 `https://openrouter.ai/typesafe/jev-1.13` 헤드리스 캡처 성공(`shots/openrouter.png`): 가격 **$0.042/M input · $0/M output**, 컨텍스트 32K, OpenRouter 등록일 **Sep 16, 2026**. → 앞의 ❓(OpenRouter 가격) ✅로 전환.
