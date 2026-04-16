# 프로젝트 현재 상태

**생성일**: 2026-04-15
**버전**: 0.1.0 (MVP 개발 중)
**완성도**: 40%

---

## ✅ 완료된 작업

### 1. 프로젝트 인프라 (100%)
- [x] Monorepo 구조 생성 (pnpm workspace)
- [x] 모든 패키지 package.json 설정
- [x] TypeScript 설정 (tsconfig.json)
- [x] 폴더 구조 완성

### 2. 문서 (100%)
- [x] PRD.md - 제품 요구사항 정의
- [x] PRESET_DESIGN.md - 프리셋 상세 설계
- [x] ARCHITECTURE.md - 시스템 아키텍처
- [x] IMPLEMENTATION_PLAN.md - 단계별 구현 계획
- [x] README.md - 종합 가이드
- [x] STATUS.md - 현재 상태 (이 파일)

### 3. Shared 패키지 (100%)
- [x] 전체 타입 시스템 정의 (Job, Transcript, CutDecision, Preset 등)
- [x] 상수 정의 (한국어 filler word 사전, IPC 채널 등)
- [x] Logger 구현 (Winston 기반)

### 4. Audio Engine 패키지 (80%)
- [x] SilenceDetector 구현 (ffmpeg silencedetect)
- [x] Padding 적용 로직
- [ ] VAD 서비스 통합 (Phase 2)

### 5. Transcript Engine 패키지 (70%)
- [x] FillerDetector 구현
- [x] 한국어 filler word 감지 (3단계 신뢰도)
- [x] 문맥 인식 제거 로직
- [ ] Retake Detection (Phase 2)
- [ ] Caption Segmentation (진행 필요)

### 6. Preset Manager 패키지 (100%)
- [x] PresetLoader 구현
- [x] 캐싱 시스템
- [x] 베이스 프리셋 상속 및 병합
- [x] 3가지 기본 프리셋 JSON (광고형, 정보형, 브이로그형)

### 7. Python STT 서비스 (90%)
- [x] ZeroMQ 서버 구현
- [x] Whisper 래퍼 (faster-whisper)
- [x] Word-level timestamp 지원
- [ ] 실제 테스트 필요

---

## 🚧 진행 중인 작업

### 다음 우선순위 작업
1. **Core 패키지 완성** (진행 필요)
   - [ ] JobManager 구현
   - [ ] Pipeline 구현
   - [ ] PythonClient (ZeroMQ 클라이언트) 구현

2. **Electron Main Process** (진행 필요)
   - [ ] 앱 초기화
   - [ ] IPC Handlers
   - [ ] Python 서비스 자동 시작

3. **React UI** (진행 필요)
   - [ ] 기본 레이아웃
   - [ ] Upload Page
   - [ ] Transcript Viewer
   - [ ] Review Panel

---

## 📋 미완성 작업

### MVP 필수 작업
- [ ] EDL/SRT 생성기 (capcut-controller)
- [ ] Caption Segmentation (transcript-engine)
- [ ] Naturalness Score 계산 (preset-manager)
- [ ] 통합 테스트
- [ ] 빌드 스크립트

### Phase 2 작업
- [ ] Retake Detection
- [ ] CapCut UI Automation
- [ ] Zoom Keyframe Automation
- [ ] 배치 처리

---

## 🎯 다음 단계 (추천 순서)

### Step 1: Core Pipeline 구현 (3~5일)
**파일 생성 필요**:
```
packages/core/src/
├── job-manager.ts       # 작업 생성, 조회, 상태 관리
├── pipeline.ts          # 처리 파이프라인
├── python-client.ts     # ZeroMQ 클라이언트
├── database.ts          # SQLite DB 초기화
└── index.ts             # Export
```

**핵심 작업**:
- SQLite 스키마 설계
- Job 상태 머신 구현
- 파이프라인 단계별 실행
- 에러 처리 및 재시도

### Step 2: Electron Main (2~3일)
**파일 생성 필요**:
```
apps/desktop/src/main/
├── index.ts             # 앱 진입점
├── ipc-handlers.ts      # IPC 핸들러
├── window-manager.ts    # 창 관리
└── python-service.ts    # Python 프로세스 관리
```

### Step 3: React UI (5~7일)
**파일 생성 필요**:
```
apps/desktop/src/renderer/
├── App.tsx                        # 메인 앱
├── pages/
│   ├── UploadPage.tsx
│   ├── JobsPage.tsx
│   └── SettingsPage.tsx
├── components/
│   ├── TranscriptViewer.tsx
│   ├── ReviewPanel.tsx
│   ├── PresetSelector.tsx
│   └── FileDropZone.tsx
└── store/
    ├── jobStore.ts
    └── presetStore.ts
```

---

## 🔧 즉시 실행 가능한 명령어

### 의존성 설치
```bash
cd d:\coding\cutback
pnpm install
```

### Python 환경 설정
```bash
cd python/stt_service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 개발 서버 시작 (준비 완료 후)
```bash
# 터미널 1: Python STT 서비스
cd python/stt_service
venv\Scripts\activate
python main.py

# 터미널 2: Electron 앱
cd d:\coding\cutback
pnpm dev
```

---

## 📂 현재 파일 트리

```
cutback/
├── apps/
│   └── desktop/
│       ├── package.json ✅
│       └── src/
│           ├── main/ (구현 필요 🚧)
│           ├── renderer/ (구현 필요 🚧)
│           └── preload/ (구현 필요 🚧)
├── packages/
│   ├── core/
│   │   ├── package.json ✅
│   │   └── src/ (구현 필요 🚧)
│   ├── audio-engine/
│   │   ├── package.json ✅
│   │   └── src/
│   │       ├── silence-detector.ts ✅
│   │       └── index.ts ✅
│   ├── transcript-engine/
│   │   ├── package.json ✅
│   │   └── src/
│   │       ├── filler-detector.ts ✅
│   │       └── (stt-client.ts, segmentation.ts 필요 🚧)
│   ├── capcut-controller/
│   │   ├── package.json ✅
│   │   └── src/ (구현 필요 🚧)
│   ├── preset-manager/
│   │   ├── package.json ✅
│   │   └── src/
│   │       ├── preset-loader.ts ✅
│   │       └── (naturalness-score.ts 필요 🚧)
│   └── shared/
│       ├── package.json ✅
│       └── src/
│           ├── types/index.ts ✅
│           ├── constants.ts ✅
│           ├── utils/logger.ts ✅
│           └── index.ts ✅
├── python/
│   ├── stt_service/
│   │   ├── main.py ✅
│   │   ├── whisper_wrapper.py ✅
│   │   └── requirements.txt ✅
│   └── vad_service/ (Phase 2 🔮)
├── presets/
│   ├── types/
│   │   ├── ad-short-form.json ✅
│   │   ├── info-talking-head.json ✅
│   │   └── vlog-style.json ✅
│   ├── brands/ (사용자 추가용)
│   └── custom/ (사용자 추가용)
├── docs/ (추가 문서용)
├── scripts/ (빌드 스크립트 필요 🚧)
├── pnpm-workspace.yaml ✅
├── package.json ✅
├── tsconfig.json ✅
├── PRD.md ✅
├── PRESET_DESIGN.md ✅
├── ARCHITECTURE.md ✅
├── IMPLEMENTATION_PLAN.md ✅
├── README.md ✅
└── STATUS.md ✅ (이 파일)
```

---

## 💡 개발 팁

### TypeScript 컴파일 확인
```bash
# 전체 타입 체크
pnpm type-check

# 특정 패키지만
pnpm --filter @cutback/shared build
```

### 로그 확인
```bash
# 앱 실행 후
cd logs
cat combined.log
cat error.log
```

### Python 서비스 테스트
```python
# test_stt.py
import zmq
import json

ctx = zmq.Context()
sock = ctx.socket(zmq.REQ)
sock.connect('tcp://127.0.0.1:5555')

# Health check
sock.send_string(json.dumps({'action': 'health'}))
print(sock.recv_string())
```

---

## 🐛 알려진 이슈

### 1. UUID import 문제 (해결 예정)
- transcript-engine에서 uuid 사용
- package.json에 `uuid` 추가 필요

### 2. ffmpeg PATH (사용자 환경 의존)
- README에 설치 가이드 포함됨
- 번들링 옵션 고려 중

### 3. Whisper 모델 다운로드
- 첫 실행 시 시간 소요
- 설치 스크립트에서 사전 다운로드 예정

---

## 📞 다음 작업 시작 방법

### 방법 1: Core 패키지부터 구현
```bash
cd packages/core/src
# job-manager.ts, pipeline.ts, python-client.ts 생성
# IMPLEMENTATION_PLAN.md Step 1 참조
```

### 방법 2: Electron UI 스켈레톤 먼저 구현
```bash
cd apps/desktop/src
# main/index.ts, renderer/App.tsx 생성
# IMPLEMENTATION_PLAN.md Step 2-3 참조
```

### 추천: **Core 패키지 먼저** 구현
이유:
- UI 없이도 파이프라인 테스트 가능
- 백엔드 로직 안정화 후 UI 연결이 효율적
- 테스트 코드 작성하기 쉬움

---

## 🎉 축하합니다!

프로젝트 구조가 완성되었습니다. 이제 실제 구현만 하면 됩니다.

**현재 진행도: 40%**
**MVP 예상 완성: 4주 후**

다음 작업을 시작하려면:
1. `IMPLEMENTATION_PLAN.md` Step 1 참조
2. `packages/core/src/job-manager.ts` 생성부터 시작
3. 궁금한 점은 `ARCHITECTURE.md` 참조

---

**Happy Coding! 🚀**
