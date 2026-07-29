# Cutback - CapCut AI 편집 어시스턴트

> **한국어 숏폼/광고 편집에 최적화된 AI 자동화 툴**
> Cutback/Premiere Assistant를 넘어서는 한국어 특화 편집 경험

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![Electron](https://img.shields.io/badge/Electron-28-47848F.svg)](https://www.electronjs.org/)

## 🎯 핵심 기능

### ✅ Mode A: 단일 영상 편집 (MVP Phase 1)
- ✨ **자동 무음 제거**: ffmpeg + Silero VAD 기반 정밀 감지
- 🗣️ **한국어 말버릇 제거**: "어", "음", "약간", "사실" 등 한국어 전용 사전
- 📝 **자동 자막 생성**: Whisper STT + 한국어 호흡 단위 최적화
- 🎨 **브랜드 프리셋**: 광고형/정보형/브이로그형 + 커스텀 스타일
- 📊 **Transcript 검수 UI**: 텍스트 기반 편집, 컷 되돌리기
- 📤 **EDL/SRT 내보내기**: CapCut import 가능

### 🎥 Mode B: 보이스오버 + B-roll 자동 조합 (v0.2.0+)
- 🎙️ **보이스오버 처리**: STT 또는 스크립트 텍스트를 문장 단위 타임라인으로 변환
- 📹 **B-roll 자동 인덱싱**: 여러 클립의 메타데이터 추출 및 키워드 태깅
- 🤖 **자동 매칭**: 문장과 B-roll 클립을 키워드 기반으로 자동 매칭
- ⏱️ **스마트 조정**: 트리밍, 속도 조정, 반복, 프리즈 프레임 전략 자동 선택
- 🔄 **검수 & 교체**: 낮은 confidence 클립 검수 및 대체 후보로 교체
- 📤 **EDL 내보내기**: 러프컷 타임라인을 EDL 형식으로 내보내기

### 🚧 Phase 2 (예정)
- 🔄 Retake 자동 감지 및 최선 선택 (Mode A)
- 🎬 강조 단어 자동 줌인/아웃 (Mode A)
- 🤖 자연스러움 점수 시스템 (Mode A)
- 🖱️ CapCut UI 완전 자동화 (Both)
- 🎞️ 샷 경계 감지 (Mode B)
- 📝 OCR 텍스트 추출 (Mode B)
- 🧠 CLIP 임베딩 기반 시맨틱 매칭 (Mode B)

---

## 📦 일반 사용자용: .exe 다운로드

> **개발 환경 일절 불필요.** 더블클릭으로 설치하고 사용 후 자동 업데이트.

1. https://github.com/makefriendscoltd-design/cutback/releases 에서 최신 `Cutback-Setup-x.x.x.exe` 다운로드
2. 더블클릭 → 설치 위치 선택 → 완료
3. 바탕화면 `Cutback` 아이콘 실행

**자동 업데이트**: 앱이 실행 중일 때 새 버전이 GitHub Releases 에 올라오면:
- 자동 백그라운드 다운로드
- 다운로드 완료 시 알림
- "지금 재시작" 클릭하거나 다음 실행 때 자동 적용

---

## 🚀 개발자용 빠른 시작 (다른 PC 에서도 동일)

> **목표:** 새 PC 에서 저장소를 받은 직후, 두 줄만 실행하면 모든 게 동작한다.

### 1. 사전 요구사항 (3 가지만)

- **Node.js**: 18.0.0 이상 ([nodejs.org](https://nodejs.org/))
- **pnpm**: 8.0.0 이상 (`npm install -g pnpm`)
- **Python**: 3.9 이상 ([python.org](https://www.python.org/downloads/) — 설치 시 *Add to PATH* 체크)
- **CapCut Desktop**: 선택 사항 (없으면 EDL/SRT/MP4 export 만 사용)

> **ffmpeg 는 직접 설치할 필요 없습니다.** `pnpm install` 시 `ffmpeg-static` 이 OS 별
> 바이너리를 자동 다운로드합니다. 시스템에 이미 설치돼 있으면 그것을 우선 사용합니다.

### 2. 한 번에 설정

```bash
# 저장소 받은 후
cd cutback

# 1) Node 의존성 + ffmpeg 자동 다운로드
pnpm install

# 2) Python venv 생성 + faster-whisper / pyzmq 설치 (idempotent, 재실행 안전)
pnpm run setup:python
```

`setup:python` 스크립트는 다음을 자동으로 수행합니다.

- `py -3` / `python` / `python3` 중 사용 가능한 인터프리터 자동 탐색
- Python 3.9+ 버전 검증
- `python/stt_service/venv` 생성 (이미 있으면 재사용)
- `pip install --prefer-binary -r requirements.txt`
- `import faster_whisper, zmq, requests` sanity check
- `ffmpeg-static` / 시스템 ffmpeg 검출
- 마지막에 무엇이 OK / WARN / FAIL 인지 표 형태로 요약

또는 위 두 단계를 한 줄로:

```bash
pnpm setup    # = pnpm install + pnpm run setup:python
```

### 3. 실행

```bash
pnpm dev
```

Electron 메인 프로세스가 부팅 시:

1. **Preflight Health Check** — ffmpeg / Python venv / 사전 / 프리셋 / CapCut 5개 항목 검증
2. **Python STT 서비스 자동 시작** (별도 터미널 불필요)
3. **Vite + React UI** 로드

검증 결과는 IPC `health:get` 으로 노출되어 UI 가 사용자에게 무엇을 고쳐야 하는지 안내합니다.

---

## 📁 프로젝트 구조

```
cutback/
├── apps/
│   └── desktop/              # Electron 메인 앱
│       ├── src/
│       │   ├── main/         # Electron main process
│       │   ├── renderer/     # React UI
│       │   └── preload/      # IPC bridge
├── packages/
│   ├── core/                 # 작업 관리, 파이프라인
│   ├── audio-engine/         # 무음 감지 (ffmpeg)
│   ├── transcript-engine/    # STT, filler 감지
│   ├── capcut-controller/    # CapCut 자동화 (Phase 2)
│   ├── preset-manager/       # 프리셋 시스템
│   ├── voiceover-engine/     # Mode B: 보이스오버/스크립트 처리
│   ├── asset-indexer/        # Mode B: B-roll 에셋 인덱싱
│   ├── clip-matcher/         # Mode B: 문장-클립 매칭
│   ├── crosscut-planner/     # Mode B: 러프컷 타임라인 생성
│   └── shared/               # 공통 타입, 유틸
├── python/
│   ├── stt_service/          # Whisper STT 서비스
│   └── vad_service/          # VAD 서비스 (Phase 2)
├── presets/
│   ├── types/                # 기본 프리셋
│   │   ├── ad-short-form.json        # Mode A: 광고형
│   │   ├── info-talking-head.json    # Mode A: 정보형
│   │   ├── vlog-style.json           # Mode A: 브이로그형
│   │   ├── ad-product-broll.json     # Mode B: 제품 광고
│   │   ├── info-broll.json           # Mode B: 정보 전달형
│   │   └── ugc-review.json           # Mode B: UGC 리뷰
│   ├── brands/               # 브랜드별 프리셋
│   └── custom/               # 사용자 커스텀 프리셋
├── PRD.md                    # Mode A 제품 요구사항 문서
├── MODE_B_PRD.md             # Mode B 제품 요구사항 문서
├── PRESET_DESIGN.md          # 프리셋 설계 문서
├── ARCHITECTURE.md           # 시스템 아키텍처
└── README.md                 # (이 파일)
```

---

## 🎨 프리셋 시스템

### Mode A 프리셋 (단일 영상 편집)

#### 1. 광고형 숏폼 (`ad-short-form`)
- **타겟**: 15~60초 제품 광고
- **특징**: 빠른 템포 (170 WPM), aggressive filler 제거, 짧은 자막 (15자)
- **사용 예**: 인스타 릴스, 유튜브 쇼츠 광고

```json
{
  "editMode": "mode-a",
  "audio": { "silence_threshold_db": -35, "min_silence_duration_ms": 400 },
  "filler_words": { "removal_strength": "aggressive" },
  "pacing": { "target_tempo": 170, "allow_jump_cuts": true }
}
```

#### 2. 정보형 토킹헤드 (`info-talking-head`)
- **타겟**: 3~10분 설명/강의 영상
- **특징**: 이해 중심 (140 WPM), balanced filler 제거, 문장 단위 자막 (20자)
- **사용 예**: 교육 콘텐츠, 제품 리뷰

#### 3. 브이로그형 (`vlog-style`)
- **타겟**: 1~5분 일상 브이로그
- **특징**: 자연스러움 (130 WPM), conservative filler 제거, 시간 기반 자막 (18자)
- **사용 예**: 일상 브이로그, 여행 영상

### Mode B 프리셋 (보이스오버 + B-roll)

#### 1. 제품 광고 (`ad-product-broll`)
- **타겟**: 보이스오버 내레이션 + 제품 B-roll 조합
- **특징**: 빠른 컷 전환, 키워드 매칭 최소 0.3, 속도 조정 0.8~1.3배
- **사용 예**: 제품 광고, 쇼핑몰 영상

```json
{
  "editMode": "mode-b",
  "modeBParams": {
    "matchConfig": {
      "keywordMatching": { "enabled": true, "minScore": 0.3 },
      "speedAdjustment": { "min": 0.8, "max": 1.3 },
      "allowRepeat": false,
      "allowFreeze": true
    },
    "transitionStyle": "cut"
  }
}
```

#### 2. 정보 전달형 (`info-broll`)
- **타겟**: 설명 콘텐츠 + B-roll 조합
- **특징**: 안정적 템포, 키워드 매칭 최소 0.4 (보수적), crossfade 전환
- **사용 예**: 교육 콘텐츠, 튜토리얼

#### 3. UGC 리뷰 (`ugc-review`)
- **타겟**: 사용자 리뷰 + 제품/경험 B-roll
- **특징**: 유연한 편집, 넓은 속도 조정 범위 (0.85~1.4배), 반복/freeze 허용
- **사용 예**: 제품 리뷰, 경험 후기

### 프리셋 커스터마이징

```typescript
// 커스텀 프리셋 생성 예시
import { presetLoader } from '@cutback/preset-manager';

const myPreset = await presetLoader.load('ad-short-form'); // 베이스 로드
myPreset.style.text_color = '#FF6B6B'; // 브랜드 색상
myPreset.captions.emphasis_words = ['신제품', '특가']; // 강조 단어

await presetLoader.save('my-brand', myPreset);
```

---

## 🛠️ 사용 방법

### 기본 워크플로우

1. **영상 업로드**
   - 앱에서 영상 파일 선택 또는 폴더에 드롭
   - 프리셋 선택 (광고형/정보형/브이로그형)

2. **자동 분석** (2~5분 소요)
   - 무음 구간 감지
   - STT로 transcript 생성
   - 한국어 filler word 감지
   - 자막 세그먼트 생성

3. **검수 및 수정**
   - Transcript 뷰어에서 제거될 구간 확인
   - 회색 표시된 구간 클릭하여 되돌리기
   - 자막 스타일 조정

4. **내보내기**
   - **Option 1**: EDL/XML 파일 생성 → CapCut에서 수동 import
   - **Option 2** (Phase 2): CapCut 자동 적용

### 예시: Mode A - 광고형 숏폼 편집

```typescript
// 1. 작업 생성
const job = await jobManager.createJob({
  videoPath: 'D:/videos/product-ad.mp4',
  presetId: 'ad-short-form',
  editMode: 'mode-a',
});

// 2. 자동 처리 (내부적으로 파이프라인 실행)
await jobManager.processJob(job.id);

// 3. 결과 확인
const result = await jobManager.getJobResult(job.id);
console.log(`무음 제거: ${result.statistics.silence_removed}개`);
console.log(`말버릇 제거: ${result.statistics.fillers_removed}개`);
console.log(`자연스러움 점수: ${result.statistics.naturalness_score}`);

// 4. EDL 내보내기
await exportEDL(result.cutDecisions, 'output.edl');
```

### 예시: Mode B - 보이스오버 + B-roll 자동 조합

```typescript
import { VoiceoverEngine } from '@cutback/voiceover-engine';
import { AssetIndexer } from '@cutback/asset-indexer';
import { ClipMatcher } from '@cutback/clip-matcher';
import { CrosscutPlanner } from '@cutback/crosscut-planner';

// 1. 보이스오버 STT 처리
const voEngine = new VoiceoverEngine();
const transcript = await sttService.transcribe('voiceover.mp3');
const sentenceTimeline = voEngine.fromTranscript(transcript);

// 또는 스크립트 텍스트로 시작
// const sentenceTimeline = voEngine.fromScript(scriptText, 'ko');

// 2. B-roll 클립 인덱싱
const indexer = new AssetIndexer();
const assetIndex = await indexer.indexAssets([
  'clips/product-shot1.mp4',
  'clips/product-shot2.mp4',
  'clips/hands-demo.mp4',
], {
  keywordMap: new Map([
    ['product-shot1.mp4', ['제품', '패키징']],
    ['product-shot2.mp4', ['제품', '디자인']],
    ['hands-demo.mp4', ['사용', '데모']],
  ]),
});

// 3. 러프컷 자동 생성
const planner = new CrosscutPlanner();
const roughCut = await planner.generateRoughCut(
  sentenceTimeline,
  assetIndex,
  {
    keywordMatching: { enabled: true, minScore: 0.3 },
    speedAdjustment: { min: 0.8, max: 1.3 },
    allowRepeat: false,
    allowFreeze: true,
  }
);

// 4. 결과 확인
console.log(`문장 수: ${roughCut.metadata.sentenceCount}`);
console.log(`평균 confidence: ${roughCut.metadata.averageConfidence}`);
console.log(`검수 필요 클립: ${roughCut.metadata.reviewRequiredCount}`);

// 5. EDL 내보내기
const edl = planner.exportToEDL(roughCut, assetIndex);
await fs.writeFile('roughcut.edl', edl);
```

---

## 📊 한국어 Filler Word 사전

### High Confidence (항상 제거 권장)
`어`, `음`, `어어`, `음음`, `에에`, `으`, `으음`

### Medium Confidence (문맥 고려)
`약간`, `뭔가`, `좀`, `되게`, `진짜`, `완전`, `엄청`, `막`, `뭐`

### Context Dependent (맥락 중요)
`사실`, `그니까`, `근데`, `이제`, `그래서`, `그럼`, `일단`

**예시**:
- ❌ "어... 이 제품은 진짜 좋아요" → "이 제품은 진짜 좋아요"
- ❌ "음... 약간 그런 느낌?" → "그런 느낌?"
- ⚠️ "사실 이건 중요해요" → 문맥상 '사실'은 의미 있으므로 보존 (balanced/conservative)

---

## 🔧 개발 가이드

### 패키지 구조 (Monorepo)

```bash
# 특정 패키지 빌드
pnpm --filter @cutback/core build

# 모든 패키지 빌드
pnpm -r build

# 타입 체크
pnpm type-check

# 린트
pnpm lint
```

### 새 프리셋 추가

1. `presets/types/` 또는 `presets/brands/`에 JSON 파일 생성
2. 스키마는 `packages/shared/src/types/index.ts`의 `Preset` 참조
3. 앱 재시작 또는 캐시 초기화

```json
{
  "name": "내 브랜드",
  "type": "brand",
  "base_preset": "ad-short-form",
  "overrides": {
    "style": {
      "text_color": "#FF6B6B",
      "font_family": "Pretendard"
    }
  }
}
```

### Python 서비스 개발

```bash
# STT 서비스 단독 테스트
cd python/stt_service
python main.py

# 다른 터미널에서 테스트 요청
python -c "
import zmq
import json
ctx = zmq.Context()
sock = ctx.socket(zmq.REQ)
sock.connect('tcp://127.0.0.1:5555')
sock.send_string(json.dumps({'action': 'health'}))
print(sock.recv_string())
"
```

---

## 📈 로드맵

### ✅ Phase 1 (MVP) - 4주
- [x] 프로젝트 구조 생성
- [x] 무음 감지 엔진
- [x] Whisper STT 통합
- [x] 한국어 filler word 감지
- [x] 프리셋 시스템
- [ ] Electron UI (진행 중)
- [ ] EDL 내보내기

### 🚧 Phase 2 - 8주
- [ ] Retake 자동 감지
- [ ] CapCut UI 자동화 (Windows Automation)
- [ ] 자동 줌/키프레임
- [ ] 브랜드 프리셋 관리 UI
- [ ] 배치 처리

### 🔮 Phase 3 - 12주 이후
- [ ] Premiere Pro 플러그인
- [ ] 클라우드 동기화
- [ ] 협업 기능
- [ ] AI 기반 후킹 구간 강조

---

## 📤 .exe 빌드 & GitHub Releases 배포

> 코드를 바꾼 후 사용자에게 새 버전을 자동으로 내려보내려면 이 흐름을 따른다.
> 사용자는 다음 앱 실행 시 자동으로 새 버전을 받는다 (electron-updater).

### 사전 준비 (한 번만)

1. **GitHub Personal Access Token 발급** — `repo` 권한
   - https://github.com/settings/tokens/new
2. **환경변수에 토큰 등록**
   ```bash
   # Windows (PowerShell, 영구 저장)
   setx GH_TOKEN "ghp_여기에토큰"
   # 새 터미널 열어야 적용됨
   ```
   `GH_TOKEN` 또는 `GITHUB_TOKEN` 어느 쪽이든 OK.
3. **`apps/desktop/build/icon.ico` 준비** (선택, 없어도 빌드는 됨)
   - 256×256 ICO 권장. 자세한 건 [apps/desktop/build/README.md](apps/desktop/build/README.md)

### 매번 릴리스할 때

```bash
# 1) 버전 올리기 (apps/desktop/package.json 의 "version")
#    semver 따라 0.1.0 → 0.1.1 (patch) / 0.2.0 (minor) / 1.0.0 (major)

# 2) 빌드 (TS 컴파일 → PyInstaller 로 STT 번들링 → Electron NSIS installer)
pnpm dist
#    → release/Cutback-Setup-0.1.1.exe 가 생김

# 3) 검증: 로컬에서 한 번 설치해서 동작 확인
#    release/Cutback-Setup-0.1.1.exe 더블클릭

# 4) GitHub Releases 에 업로드 + 사용자 자동 업데이트 트리거
pnpm release
#    → release/* 가 GitHub Releases 에 자동 푸시됨
#    → 기존 사용자 앱이 1시간 안에 새 버전 감지 → 백그라운드 다운로드
```

### 무엇이 어떻게 번들링되는가

| 항목 | 어디로 | 용량 (대략) |
|---|---|---|
| Electron + Node | `app.asar` | ~150MB |
| React UI | `app.asar` | ~200KB |
| `cutback-stt.exe` (PyInstaller) | `resources/cutback-stt/` | ~800MB (torch + faster-whisper) |
| `presets/` (한국어 사전 등) | `resources/presets/` | ~50KB |
| **총 installer 크기** | | **~1.2GB** |
| Whisper 모델 (large-v3) | 첫 실행 시 사용자 PC 로 다운로드 | 1.5GB |

### 릴리스 워크플로 자세히

- **`pnpm dist`** = `pnpm -r build` + `pnpm run build:python-exe` + `electron-builder`
- **`pnpm release`** = 위 + `--publish always` (GitHub Releases 업로드)
- 사용자 앱은 부팅 5초 후 + 그 후 1시간마다 `latest.yml` 폴링
- 새 버전 감지 → 백그라운드 다운로드 → "지금 재시작" 알림 → quitAndInstall

### 코드 사인 (선택)

서명 안 하면 사용자가 처음 설치할 때 Windows SmartScreen 경고가 뜬다 ("실행 안 함" 화면 → "추가 정보" → "실행" 클릭).
정식 배포 시 EV 인증서 ($300/년) 사면 SmartScreen 우회 가능.
electron-builder 가 `CSC_LINK` / `CSC_KEY_PASSWORD` 환경변수로 자동 처리.

---

## 🐛 트러블슈팅

### 먼저 해볼 것: Preflight Health Check
앱 실행 후 DevTools 콘솔에서:
```js
await window.api.getHealth()   // 또는 await window.api.getHealth(true) 로 강제 재검사
```
ffmpeg / Python / 사전 / 프리셋 / CapCut 의 OK/WARN/FAIL 상태와 각 항목별 `fixes` 배열
(복붙 가능한 해결 명령) 이 반환됩니다. 부팅 로그에도 같은 내용이 한 줄씩 찍힙니다.

### Python 서비스가 시작되지 않음
앱 로그에 `Python venv 가 없습니다 (...)` 또는 `import faster_whisper 실패` 가 보이면:
```bash
pnpm run setup:python
```
포트 충돌이 의심되면 (드문 경우):
```bash
netstat -ano | findstr :5555
```

### ffmpeg 를 찾지 못함
보통은 `pnpm install` 만 다시 하면 `ffmpeg-static` 이 자동 설치됩니다.
```bash
pnpm install
```
그래도 실패하면 (사내망 / 프록시 등 npm 다운로드 차단 환경) 시스템에 ffmpeg 를 설치하면
resolver 가 자동으로 시스템 PATH 를 fallback 으로 사용합니다.
```bash
choco install ffmpeg     # Windows + chocolatey
scoop install ffmpeg     # Windows + scoop
brew install ffmpeg      # macOS
```
환경변수 `CUTBACK_FFMPEG=절대경로` 로 임의 위치를 강제 지정할 수도 있습니다.

### Whisper 모델 다운로드 느림 (첫 실행 시 1.5GB 다운)
```bash
# venv 활성화 후 미리 받아두기
python/stt_service/venv/Scripts/python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3', device='cpu')"
```

### Filler 사전을 못 찾음 (legacy fallback 으로 동작)
앱 로그에 `lexicon load failed` 가 뜨면 저장소가 일부 손상된 것입니다. 다시 클론하거나
`presets/lexicons/korean-fillers.json` 을 복원하세요.
환경변수 `CUTBACK_FILLER_LEXICON=절대경로` 로 위치를 직접 지정할 수도 있습니다.

### TypeScript 컴파일 에러
```bash
pnpm clean && pnpm install
pnpm type-check
```

### 완전 초기화 (최후 수단)
```bash
pnpm clean
rmdir /s /q python\stt_service\venv     # Windows
# rm -rf python/stt_service/venv         # Unix
pnpm setup
```

### `pnpm dist` 가 PyInstaller 단계에서 실패
`scripts/build-python-exe.js` 출력 마지막 줄을 확인:
- `venv 가 없습니다` → `pnpm run setup:python` 먼저
- `PyInstaller 설치 실패` → 인터넷/디스크 공간 확인
- `torch 빌드 실패` → Python 3.13+ 호환성 문제일 수 있음. 3.11 또는 3.12 venv 권장.

### `pnpm release` 시 "401 Unauthorized" / "GH_TOKEN not set"
GitHub Personal Access Token 누락 또는 권한 부족.
```bash
setx GH_TOKEN "ghp_여기에토큰"
# 새 터미널 열고 다시 시도
```
토큰 권한은 `repo` (private) 또는 `public_repo` (public) 필수.

### 사용자가 새 버전을 못 받음
- GitHub Releases 가 **draft 가 아니라 published** 상태인지 확인
- `latest.yml` 파일이 release assets 에 같이 올라갔는지 확인 (electron-builder 가 자동 생성)
- 사용자 앱은 1시간마다 폴링하므로 즉시 적용 안 됨. 강제 확인은 메뉴 → "업데이트 확인"

---

## 🤝 기여하기

### 이슈 및 버그 리포트
- GitHub Issues: (추후 공개)
- 버그 리포트 시 포함사항:
  - OS 버전 (Windows 10/11)
  - CapCut 버전
  - 영상 파일 포맷 및 길이
  - 에러 로그 (`logs/error.log`)

### 커뮤니티 프리셋 기여
1. `presets/community/` 폴더에 프리셋 추가
2. README에 설명 추가
3. Pull Request 제출

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 🙏 크레딧

- **Whisper**: OpenAI의 오픈소스 STT 모델
- **faster-whisper**: Systran의 최적화된 Whisper 구현
- **ffmpeg**: 오디오/비디오 처리 도구
- **Electron**: 크로스 플랫폼 데스크톱 앱 프레임워크

---

## 📞 문의

- **개발자**: CapCut AI Assistant Team
- **이메일**: (추후 공개)
- **Discord**: (추후 공개)

---

**Made with ❤️ for Korean content creators**
