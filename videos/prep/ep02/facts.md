# 2편 팩트체크 — 클로드 코드 한도 걸리면 무료 모델로 넘기는 법

확인일: 2026-09-23 (GitHub API + 공식 README + 소스코드 직접 확인)

## 0. 프로젝트 정체

| 항목 | 값 |
|---|---|
| 이름 | Free Claude Code (줄여서 FCC) |
| 저장소 | https://github.com/Alishahryar1/free-claude-code |
| 만든 사람 | Alishahryar1 (개인 계정) |
| 별 | **55,728개** (2026-09-23 GitHub API 기준) |
| 라이선스 | MIT |
| 생성 / 최근 푸시 | 2026-01-28 / 2026-09-22 |
| 정체 | 내 컴퓨터에서 도는 중계 서버(프록시). 클로드 코드는 원래 Anthropic 서버로 요청을 보내는데, 이걸 FCC로 돌려서 다른 회사 모델이 대신 답하게 만듦 |
| 공식 문구 | "Independent open-source project. Not affiliated with or endorsed by Anthropic." |

헷갈리기 쉬운 비슷한 프로젝트: `diegosouzapw/OmniRoute`(별 69,433, 359곳), `decolua/9router`(별 29,649, 40곳 이상), `router-for-me/CLIProxyAPI`(별 52,964). 대본의 "53곳·5만 별" 조합에 맞는 건 FCC뿐임.

## 1. 대본 주장별 판정

| # | 대본 주장 | 판정 | 근거 / 다른 점 | 수정 제안 |
|---|---|---|---|---|
| 1 | 깃허브에 "프리 클로드 코드"가 있다 | ✅ | 저장소 위 링크 | — |
| 2 | 깃허브 별 5만 개 넘음 | ✅ | 55,728 (9/23) | "별이 5만 5천 개 넘습니다"도 가능 |
| 3 | 무료 모델을 **53곳** 모아놓음 | ⚠️ | README: "53 ToS-friendly providers". 53은 **연결할 수 있는 회사(제공처) 수**이고 전부 무료는 아님. Azure OpenAI·Amazon Bedrock·ChatGPT 구독·GitHub Copilot 같은 **유료·구독형도 포함**. README 공급처 표 행 수 직접 세어 봐도 53 | "무료·유료 합쳐서 AI 회사 53곳을 한 번에 붙일 수 있는 건데" |
| 4 | 구글·엔비디아 포함 | ✅ | 표에 Google AI Studio (Gemini), Google Vertex AI, NVIDIA NIM(기본값) 있음 | — |
| 5 | "그록" 포함 | ⚠️ | **Groq**(그로크, 추론 칩 회사, 무료 티어 있음)와 **xAI Grok**(일론 머스크 회사 모델, 유료 API) **둘 다** 목록에 있음. "무료로 열어놓은"에 맞는 건 Groq. 한글 "그록"은 보통 xAI Grok으로 들림 | "구글, 엔비디아, 오픈라우터 같은 회사들이" 로 바꾸면 헷갈릴 일이 없음. 꼭 넣으려면 자막에 영문 "Groq" 표기 |
| 6 | 무료로 열어놓은 모델 | ⚠️ | README 문구는 "1.3B+ free tokens every month" + "Free-tier availability and limits are controlled by each provider and may change." 무료 한도는 각 회사 마음대로 바뀜 | "무료 한도는 회사마다 달라요" 한 마디 추가 권장 |
| 7 | 한 모델 한도 끝나면 다음 모델로 알아서 넘어감 | ⚠️ | 기능은 실재함. README: "After retries are exhausted, FCC automatically tries your next configured model". 소스(`application/execution.py`)상 첫 응답이 나오기 전에 실패하면(한도 초과 포함) 다음 후보로 넘어감. **단, 관리 화면에서 "Fallback Models" 목록을 직접 순서대로 넣어야 켜짐(선택 기능)**. 답변이 이미 나오기 시작한 뒤 끊기면 넘어가지 않음. README 경고: 실패한 요청이 여러 회사 사용량을 같이 깎을 수 있음 | "예비 모델 순서를 정해두면, 한 곳 한도가 끝났을 때 다음 모델로 자동으로 넘어가요" |
| 8 | **클로드가 한도 걸려서 멈추면** 대신 일함 (도입부 전제) | ⚠️ (중요) | FCC는 클로드 한도를 감지해서 자동으로 바꿔주는 게 **아님**. 공급처 목록에 Anthropic(클로드)이 **없음**. 그냥 `claude` 대신 `fcc-claude`로 실행하면 처음부터 무료 모델이 클로드 코드 안에서 일하는 구조. 즉 "클로드 한도 걸리면 → 내가 fcc-claude로 갈아타서 실행" | "클로드 한도 걸리면, 클로드 코드는 그대로 두고 두뇌만 무료 모델로 갈아끼우는 거예요" |
| 9 | 맥은 명령어 한 줄 | ⚠️ | 설치는 한 줄(`curl ... | sh`) 맞음. 그런데 설치 뒤에 ① 앱 실행 ② NVIDIA 등에서 API 키 발급 ③ 관리 화면에 붙여넣고 Apply ④ `fcc-claude` 실행까지 해야 씀 | "설치는 명령어 한 줄이고, 키 하나만 붙여넣으면 돼요" |
| 10 | 윈도우도 됨 | ✅ | README에 Windows PowerShell 설치 명령 + 시작 메뉴 앱 있음 | — |
| 11 | 내 컴퓨터 올라마 모델도 붙일 수 있음 | ✅ | README "Local provider setup → Ollama", 설정값 `OLLAMA_BASE_URL`(기본 `http://localhost:11434`), 모델명 `ollama/<태그>`. LM Studio·llama.cpp도 됨. README 경고: 도구 사용 가능한 모델이어야 하고 컨텍스트가 충분해야 함 → 작은 로컬 모델은 코딩 품질 낮을 수 있음 | — |
| 12 | 클로드 모델이 무료가 되는 건 아님 | ✅ | 목록에 Anthropic 없음. README: "Not affiliated with or endorsed by Anthropic". 클로드 화면(인터페이스)만 쓰고 두뇌는 다른 모델 | — |
| 13 | 무료 모델은 넣은 내용을 학습에 쓸 수 있음 | ⚠️ | **회사마다 다름.** 구글 Gemini 무료: ✅ 학습·사람 검토에 씀, "민감·개인 정보 넣지 말라" 명시. OpenRouter: 학습하는 공급처가 섞여 있고 설정에서 끌 수 있음. Groq: 기본적으로 데이터를 보관하지 않는다고 명시(학습 여부는 문서에 명시 없음). NVIDIA 체험판: 운영(실서비스) 사용 금지 조건, 학습 여부는 확인 못 함 ❓ | "무료 모델 중엔 내가 넣은 내용을 학습에 쓰는 곳도 있어요. 구글 무료 버전이 그래요. 그러니까 고객 정보는 절대 넣지 마세요" |
| 14 | 무료 | ✅ (조건부) | 프로그램 자체는 MIT 무료. 모델 사용료는 고른 공급처의 무료 한도 안에서만 0원 | — |

### 학습 관련 원문 인용

- Google Gemini API 약관(무료 서비스): "Google uses the content you submit to the Services and any generated responses to provide, improve, and develop Google products and services and machine learning technologies." / "Human reviewers may read, annotate, and process your API input and output." / "Do not submit sensitive, confidential, or personal information to the Unpaid Services." — https://ai.google.dev/gemini-api/terms
- OpenRouter: "set whether you would like to allow routing to providers that may train on your data ... There are separate settings for paid and free models." — https://openrouter.ai/docs/features/privacy-and-logging
- Groq: "By default, Groq does not retain customer data for inference requests." — https://console.groq.com/docs/your-data
- NVIDIA API 체험 약관(PDF, 체험 목적·운영 사용 금지): https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf

## 2. 설치·연결 명령 (README 원문 그대로)

설치 — macOS/Linux:
```bash
curl -fsSL "https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.sh" | sh
```

설치 — Windows PowerShell:
```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.ps1")))
```
(설치 중 코딩 에이전트를 최소 1개 고르라고 물어봄. RTK는 선택)

실행 — macOS: 바탕화면이나 응용 프로그램 폴더에서 **Free Claude Code** 앱 열기 / Windows: 바탕화면·시작 메뉴 / Linux:
```bash
fcc-server
```
→ 관리 화면(Admin UI)이 자동으로 뜸.

NVIDIA NIM 연결 (README 3단계):
1. https://build.nvidia.com/settings/api-keys 에서 API 키 발급
2. 서버 로그에 나온 Admin UI 주소 열기
3. `NVIDIA_NIM_API_KEY` 칸에 키 붙여넣기
4. `MODEL`은 기본값 `nvidia_nim/nvidia/nemotron-3-super-120b-a12b` 그대로 두거나 드롭다운에서 선택
5. **Apply** 클릭

클로드 코드 실행:
```bash
fcc-claude
```
클로드 코드 안에서 `/model` 누르면 FCC 모델 목록이 뜸.

자동 넘김: Admin UI → **Model Config → Fallback Models**에 순서대로 모델 추가 (설정값 이름 `MODEL_FALLBACKS`).

올라마:
```bash
ollama pull llama3.1
ollama serve
```
모델명은 `ollama list`에 나온 태그 앞에 `ollama/` 붙이기.

### 환경변수(ANTHROPIC_BASE_URL 등)는 직접 안 넣어도 됨
`fcc-claude`가 알아서 넣어줌. 소스 `src/free_claude_code/harnesses/claude.py` 기준으로 넣는 값:
`ANTHROPIC_BASE_URL`(=FCC 로컬 주소), `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1`, `CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000`, `DISABLE_AUTOUPDATER=1` 등. 기존 `ANTHROPIC_*` 변수는 지움.
→ 영상에서 "환경변수 설정" 같은 설명은 불필요. 기본 포트 번호는 README에 적혀 있지 않아서 화면에 쓰지 말 것.

VS Code·Claude Desktop: Admin UI → **Integrations** → 해당 카드에서 **Connect**.

삭제: `curl -fsSL "https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/uninstall.sh" | sh`

직접 실행 여부: 설치 스크립트는 에이전트·uv·Python을 실제로 까는 스크립트라 **실행 안 함**. `--help`만 되는 가벼운 명령이 없어서 로컬 실행 검증은 **미검증**. 위 명령은 전부 README 원문 복사.

## 3. 화면에 띄울 실제 자료

| # | 자료 | URL | 쓸 자리 |
|---|---|---|---|
| 1 | 클로드 코드가 FCC로 도는 터미널 캡처 | https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/assets/pic.png | "클로드 코드에 연결하면" |
| 2 | 클로드 코드 `/model` 선택창에 FCC 모델 뜨는 캡처 | https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/assets/cc-model-picker.png | "다음 모델로 넘어가요" |
| 3 | Admin UI(키 붙여넣고 모델 고르는 관리 화면) | https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/assets/admin-page.png | "설치 방법 정리해 놨어요" |
| 4 | 작동 구조 그림 | https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/assets/how-it-works.svg | "무료 모델들이 대신 일하는 거예요" |
| 5 | 깃허브 저장소 첫 화면(별 55.7k 보이게 직접 캡처) | https://github.com/Alishahryar1/free-claude-code | "별이 5만 개" |
| (보너스) | 공급처 53곳 표 — README "Provider catalog" 펼쳐서 스크롤 캡처 | https://github.com/Alishahryar1/free-claude-code#choose-a-provider | "53곳" |

## 4. 촬영 전 꼭 고칠 것 (우선순위)

1. **도입부 전제**: "클로드가 한도 걸리면 자동으로 대신 일함" → FCC는 클로드 한도를 감지하지 않음. "클로드 한도 걸리면 두뇌만 무료 모델로 갈아끼우는 거"로.
2. **"무료 모델 53곳"** → 53곳엔 유료도 섞임. "AI 회사 53곳을 한 번에 붙일 수 있고, 그중 무료로 쓸 수 있는 곳이 많아요".
3. **"그록"** → Groq/Grok 혼동. 빼거나 자막에 "Groq" 영문 표기.
4. **자동 넘김** → 예비 모델 순서를 직접 정해둬야 켜짐.
5. **학습** → "무료 모델은 학습에 쓸 수 있다"를 "학습에 쓰는 곳도 있다(구글 무료 버전 등)"로.
