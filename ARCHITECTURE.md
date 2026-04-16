# System Architecture

## 전체 구조

```
cutback/
├── apps/
│   └── desktop/                      # Electron 메인 애플리케이션
│       ├── src/
│       │   ├── main/                 # Electron main process (Node.js)
│       │   │   ├── index.ts          # 앱 엔트리포인트
│       │   │   ├── ipc-handlers.ts   # IPC 통신 핸들러
│       │   │   ├── window-manager.ts # 창 관리
│       │   │   └── task-queue.ts     # 작업 큐 관리
│       │   ├── renderer/             # Electron renderer (React)
│       │   │   ├── App.tsx           # 메인 React 컴포넌트
│       │   │   ├── components/       # UI 컴포넌트
│       │   │   ├── pages/            # 페이지
│       │   │   ├── hooks/            # Custom React hooks
│       │   │   └── store/            # Zustand 상태 관리
│       │   └── preload/
│       │       └── index.ts          # Preload script (IPC bridge)
│       ├── package.json
│       └── tsconfig.json
├── packages/
│   ├── core/                         # 핵심 비즈니스 로직
│   │   ├── src/
│   │   │   ├── job-manager.ts        # 작업 관리
│   │   │   ├── pipeline.ts           # 처리 파이프라인
│   │   │   └── types.ts              # 핵심 타입 정의
│   │   └── package.json
│   ├── audio-engine/                 # 오디오 분석 엔진
│   │   ├── src/
│   │   │   ├── silence-detector.ts   # 무음 감지
│   │   │   ├── vad-wrapper.ts        # VAD 통합
│   │   │   └── audio-utils.ts        # 오디오 유틸리티
│   │   └── package.json
│   ├── transcript-engine/            # Transcript 엔진
│   │   ├── src/
│   │   │   ├── stt-client.ts         # Whisper STT 클라이언트
│   │   │   ├── filler-detector.ts    # Filler word 감지
│   │   │   ├── retake-detector.ts    # Retake 감지
│   │   │   └── segmentation.ts       # 자막 세그먼트 생성
│   │   └── package.json
│   ├── capcut-controller/            # CapCut 제어
│   │   ├── src/
│   │   │   ├── automation.ts         # UI 자동화
│   │   │   ├── edl-generator.ts      # EDL/XML 생성
│   │   │   └── capcut-api.ts         # (향후) 공식 API 래퍼
│   │   └── package.json
│   ├── preset-manager/               # 프리셋 관리
│   │   ├── src/
│   │   │   ├── preset-loader.ts      # 프리셋 로드
│   │   │   ├── preset-validator.ts   # 프리셋 검증
│   │   │   └── naturalness-score.ts  # 자연스러움 점수 계산
│   │   └── package.json
│   └── shared/                       # 공통 유틸, 타입
│       ├── src/
│       │   ├── types/                # 공통 타입 정의
│       │   ├── utils/                # 유틸 함수
│       │   └── constants.ts          # 상수
│       └── package.json
├── python/                           # Python 보조 엔진
│   ├── stt_service/                  # Whisper STT 서비스
│   │   ├── main.py                   # ZeroMQ 서버
│   │   ├── whisper_wrapper.py        # Whisper 래퍼
│   │   └── requirements.txt
│   └── vad_service/                  # VAD 서비스
│       ├── main.py                   # ZeroMQ 서버
│       ├── vad_wrapper.py            # Silero VAD 래퍼
│       └── requirements.txt
├── presets/                          # 프리셋 JSON 파일
│   ├── types/
│   │   ├── ad-short-form.json
│   │   ├── info-talking-head.json
│   │   └── vlog-style.json
│   ├── brands/
│   │   └── (사용자별 브랜드 프리셋)
│   └── custom/
│       └── (사용자 커스텀 프리셋)
├── scripts/                          # 빌드, 배포 스크립트
│   ├── setup-python.sh
│   ├── build.js
│   └── package-app.js
├── docs/                             # 추가 문서
│   ├── API.md
│   ├── DEVELOPMENT.md
│   └── TROUBLESHOOTING.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── pnpm-workspace.yaml
├── package.json                      # 루트 package.json
├── tsconfig.json                     # 공통 TypeScript 설정
├── PRD.md
├── PRESET_DESIGN.md
├── ARCHITECTURE.md                   # (이 파일)
└── README.md
```

## 데이터 플로우

### 1. 영상 업로드 → 분석

```
[User Upload Video]
        ↓
[Electron Renderer: Upload UI]
        ↓ (IPC)
[Electron Main: File Watcher]
        ↓
[Core: Job Manager] → [Task Queue]
        ↓
[Pipeline: Audio Analysis]
        ├→ [audio-engine: silence-detector] → ffmpeg
        └→ [python/vad_service] → Silero VAD
        ↓
[Pipeline: Transcript Generation]
        └→ [python/stt_service] → Whisper (faster-whisper)
        ↓
[Pipeline: Filler Detection]
        └→ [transcript-engine: filler-detector]
        ↓
[Pipeline: Edit Decision Engine]
        └→ [core: decision-maker] + [preset-manager]
        ↓
[Results: Cut Decisions JSON]
```

### 2. 검수 UI → CapCut 적용

```
[Electron Renderer: Transcript Viewer]
        ↓ (User Review & Confirm)
[Electron Renderer: Export Action]
        ↓ (IPC)
[Electron Main: CapCut Controller]
        ├→ [Option 1] capcut-controller: automation → Windows Automation
        └→ [Option 2] capcut-controller: edl-generator → EDL File
        ↓
[CapCut Desktop]
```

## 주요 컴포넌트 설명

### Core (`packages/core`)
**책임**: 전체 작업 흐름 조율, 파이프라인 관리
**핵심 모듈**:
- `JobManager`: 작업 생성, 상태 추적, 큐 관리
- `Pipeline`: 단계별 처리 파이프라인 (audio → transcript → edit decision)
- `StateManager`: 작업 상태 DB (SQLite) 저장

**입력**: 영상 파일 경로, 프리셋 ID
**출력**: 완료된 작업 결과 (Cut Decisions, Transcript, Captions)

### Audio Engine (`packages/audio-engine`)
**책임**: 오디오 분석 (무음 감지, VAD)
**의존성**:
- ffmpeg (외부 바이너리)
- Python VAD service (ZeroMQ 통신)

**주요 알고리즘**:
```typescript
interface SilenceDetectionResult {
  timestamp: number;      // 시작 시점 (초)
  duration: number;       // 지속 시간 (초)
  confidence: number;     // 확신도 (0.0 ~ 1.0)
  db_level: number;       // 평균 dB
}

async function detectSilence(
  audioFilePath: string,
  threshold_db: number,
  min_duration_ms: number
): Promise<SilenceDetectionResult[]>
```

### Transcript Engine (`packages/transcript-engine`)
**책임**: STT, Filler word 감지, Retake 감지, 자막 세그먼트 생성
**의존성**:
- Python STT service (Whisper)
- Korean NLP 라이브러리 (향후: KoNLPy, 현재: 정규식)

**핵심 타입**:
```typescript
interface Word {
  text: string;
  start: number;
  end: number;
  confidence: number;
}

interface Transcript {
  words: Word[];
  full_text: string;
  language: string;
}

interface FillerWordMatch {
  word: Word;
  type: 'high_confidence' | 'medium_confidence' | 'context_dependent';
  removal_recommendation: boolean;
}
```

### CapCut Controller (`packages/capcut-controller`)
**책임**: CapCut Desktop 제어
**전략**:
1. **Primary**: Windows Automation (node-window-manager + robotjs)
   - CapCut 창 찾기, 포커스
   - 단축키 자동화 (Ctrl+Import, Timeline Split 등)
2. **Fallback**: EDL/XML 생성 + 사용자 수동 import

**리스크 완화**:
- CapCut UI 좌표를 설정 파일로 관리 (`capcut-ui-config.json`)
- 버전별 설정 프로필 지원
- 이미지 인식 fallback (OpenCV.js - Phase 2)

### Preset Manager (`packages/preset-manager`)
**책임**: 프리셋 로드, 검증, 자연스러움 점수 계산
**프리셋 스키마**:
```typescript
interface Preset {
  name: string;
  type: 'ad-short-form' | 'info-talking-head' | 'vlog-style' | 'brand' | 'custom';
  version: string;
  audio: AudioParams;
  filler_words: FillerWordParams;
  captions: CaptionParams;
  style: StyleParams;
  pacing: PacingParams;
  effects?: EffectParams;
}
```

**Naturalness Score**:
```typescript
function calculateNaturalnessScore(
  cutDecisions: CutDecision[],
  originalDuration: number,
  preset: Preset
): number {
  // 0.0 (기계적) ~ 1.0 (자연스러움)
  // 기준: 컷 빈도, 짧은 구간, 연속 컷, pause 보존
}
```

## 프로세스 간 통신 (IPC)

### Electron Main ↔ Renderer
**프로토콜**: Electron IPC
**채널**:
```typescript
// Renderer → Main
'job:create'         // 새 작업 생성
'job:cancel'         // 작업 취소
'preset:load'        // 프리셋 로드
'export:edl'         // EDL 내보내기
'export:capcut'      // CapCut 적용

// Main → Renderer
'job:progress'       // 작업 진행도 업데이트
'job:completed'      // 작업 완료
'job:error'          // 에러 발생
```

### Node.js ↔ Python
**프로토콜**: ZeroMQ (REQ-REP 패턴)
**포트**:
- STT Service: `tcp://127.0.0.1:5555`
- VAD Service: `tcp://127.0.0.1:5556`

**메시지 포맷** (JSON):
```json
{
  "action": "transcribe",
  "payload": {
    "audio_path": "/path/to/audio.wav",
    "language": "ko",
    "word_timestamps": true
  }
}
```

## 성능 최적화 전략

### 1. Worker Threads
- 오디오 분석은 별도 Worker에서 처리 → UI 블록 방지
- CPU 집약적 작업 (transcript segmentation) Worker 분산

### 2. Streaming Processing
- 대용량 영상: 청크 단위 스트리밍 분석
- ffmpeg stdout 스트림 파싱

### 3. 캐싱
- Transcript 결과 캐싱 (파일 해시 기반)
- 프리셋 메모리 캐싱

### 4. Python 서비스 최적화
- Whisper 모델 메모리에 상주 (첫 요청 시 로드)
- Batch 처리 지원 (여러 영상 동시 처리 시)

## 에러 처리 및 복구

### 작업 실패 시나리오
1. **Python 서비스 미응답**
   - 재연결 시도 (3회, exponential backoff)
   - Fallback: 사용자에게 수동 STT 입력 옵션

2. **CapCut 자동화 실패**
   - Fallback: EDL 파일 생성 + import 가이드 표시

3. **영상 파일 손상**
   - ffmpeg probe로 사전 검증
   - 에러 메시지: "영상 파일을 읽을 수 없습니다. 다른 포맷으로 변환해주세요."

4. **프리셋 검증 실패**
   - 기본 프리셋으로 fallback
   - 경고: "커스텀 프리셋에 오류가 있어 기본 프리셋을 사용합니다."

### 로그 시스템
```typescript
// packages/shared/src/logger.ts
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// 사용 예시
logger.info('Job created', { jobId: '123', preset: 'ad-short-form' });
logger.error('Python service timeout', { service: 'stt', error: err.message });
```

## 보안 및 개인정보

### 데이터 처리 원칙
- **로컬 우선**: 모든 처리는 사용자 PC에서 (클라우드 전송 없음)
- **임시 파일 관리**: 작업 완료 후 임시 오디오 파일 자동 삭제
- **프리셋 암호화**: 브랜드 프리셋에 민감 정보 포함 시 암호화 옵션

### 파일 시스템 권한
- 최소 권한 원칙: 사용자 지정 폴더만 접근
- CapCut 프로젝트 폴더 자동 감지 (레지스트리 또는 기본 경로)

## 확장성 고려사항

### 향후 추가 기능
1. **다른 편집 툴 지원**
   - Premiere Pro 플러그인 (CEP 또는 ExtendScript)
   - DaVinci Resolve 연동

2. **클라우드 동기화**
   - 프리셋 클라우드 백업
   - 팀 협업 기능

3. **AI 고도화**
   - GPT-4 기반 컨텍스트 분석 (어떤 구간이 중요한지 자동 판단)
   - 감정 분석 기반 편집 (긍정적 구간 강조)

---

**Last Updated**: 2026-04-15
**Version**: 1.0.0
