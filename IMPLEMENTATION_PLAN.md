# Step-by-Step 구현 계획

## 현재 상태 (2026-04-15)

### ✅ 완료된 작업
1. **프로젝트 구조 생성**
   - Monorepo 구조 (pnpm workspace)
   - apps/desktop, packages/*, python/* 폴더 생성
   - 모든 package.json 설정 완료

2. **문서 작성**
   - PRD.md (제품 요구사항)
   - PRESET_DESIGN.md (프리셋 설계)
   - ARCHITECTURE.md (시스템 아키텍처)
   - README.md (종합 가이드)

3. **공통 패키지 (shared)**
   - 타입 정의 (Job, Transcript, CutDecision, Preset 등)
   - 상수 (한국어 filler word 사전, IPC 채널 등)
   - 로거 (Winston 기반)

4. **오디오 엔진 (audio-engine)**
   - SilenceDetector 구현 (ffmpeg silencedetect 사용)
   - AudioParams → SilenceDetectorOptions 변환
   - Padding 적용 로직

5. **Transcript 엔진 (transcript-engine)**
   - FillerDetector 구현
   - 한국어 filler word 감지 (high/medium/context-dependent)
   - 문맥 인식 제거 로직

6. **프리셋 시스템 (preset-manager)**
   - PresetLoader 구현
   - 3가지 기본 프리셋 JSON (광고형, 정보형, 브이로그형)
   - 베이스 프리셋 상속 및 오버라이드

7. **Python STT 서비스**
   - ZeroMQ 서버 구현
   - Whisper (faster-whisper) 래퍼
   - Word-level timestamp 지원

---

## 다음 단계 (우선순위순)

### Step 1: Core 패키지 완성 (3~5일)

**목표**: 작업 관리 및 처리 파이프라인 구현

#### 1.1 JobManager 구현
```typescript
// packages/core/src/job-manager.ts
export class JobManager {
  async createJob(params: CreateJobParams): Promise<Job>
  async processJob(jobId: string): Promise<void>
  async cancelJob(jobId: string): Promise<void>
  async getJob(jobId: string): Promise<Job>
  async listJobs(): Promise<Job[]>
}
```

**구현 사항**:
- SQLite DB 스키마 설계 (jobs, cut_decisions 테이블)
- Job 상태 관리 (PENDING → PROCESSING → COMPLETED/FAILED)
- 진행도 업데이트 (IPC로 Renderer에 전송)

#### 1.2 Pipeline 구현
```typescript
// packages/core/src/pipeline.ts
export class ProcessingPipeline {
  async execute(job: Job): Promise<JobResults>
}
```

**파이프라인 단계**:
1. 오디오 추출 (ffmpeg)
2. 무음 감지 (audio-engine)
3. STT (Python 서비스 호출)
4. Filler 감지 (transcript-engine)
5. Cut decision 생성
6. 자막 세그먼트 생성
7. 자연스러움 점수 계산
8. 결과 저장

#### 1.3 ZeroMQ Client 구현
```typescript
// packages/core/src/python-client.ts
export class PythonClient {
  async transcribe(audioPath: string, language: string): Promise<Transcript>
  async checkHealth(): Promise<boolean>
}
```

**구현 사항**:
- zeromq.js를 사용한 REQ-REP 통신
- 재시도 로직 (3회, exponential backoff)
- Timeout 처리

---

### Step 2: Electron Main Process 구현 (2~3일)

**목표**: IPC 핸들러 및 앱 초기화

#### 2.1 Main Process 기본 구조
```typescript
// apps/desktop/src/main/index.ts
import { app, BrowserWindow } from 'electron';

app.on('ready', async () => {
  await initDatabase();
  await startPythonService();
  createWindow();
  registerIPCHandlers();
});
```

**구현 사항**:
- Electron 앱 초기화
- SQLite DB 초기화
- Python 서비스 자동 시작 (child_process)
- 창 관리 (개발 모드 vs 프로덕션)

#### 2.2 IPC Handlers
```typescript
// apps/desktop/src/main/ipc-handlers.ts
ipcMain.handle('job:create', async (event, params) => {
  return await jobManager.createJob(params);
});

ipcMain.handle('preset:list', async () => {
  return await presetLoader.listAll();
});
```

**구현 사항**:
- 모든 IPC 채널 구현 (job, preset, export, settings)
- 에러 처리 및 로깅
- 진행도 이벤트 전송 (Main → Renderer)

---

### Step 3: React UI 구현 (5~7일)

**목표**: 사용자 인터페이스 완성

#### 3.1 기본 레이아웃
```
┌─────────────────────────────────────────┐
│  Header: Cutback AI Assistant           │
├─────────────┬───────────────────────────┤
│  Sidebar    │  Main Content             │
│  - Upload   │                           │
│  - Jobs     │  Upload Area              │
│  - Presets  │  or                       │
│  - Settings │  Transcript Viewer        │
│             │  or                       │
│             │  Review Panel             │
└─────────────┴───────────────────────────┘
```

#### 3.2 주요 컴포넌트

**Upload Page**
```tsx
// apps/desktop/src/renderer/pages/UploadPage.tsx
<UploadPage>
  <FileDropZone onFileSelect={handleFileSelect} />
  <PresetSelector presets={presets} selected={selectedPreset} />
  <Button onClick={handleStartJob}>분석 시작</Button>
</UploadPage>
```

**Transcript Viewer**
```tsx
// apps/desktop/src/renderer/components/TranscriptViewer.tsx
<TranscriptViewer transcript={transcript} cutDecisions={cutDecisions}>
  {words.map(word => (
    <Word
      key={word.id}
      text={word.text}
      isFiltered={isCutDecision(word)}
      onClick={handleWordClick} // 타임라인 이동
    />
  ))}
</TranscriptViewer>
```

**Review Panel**
```tsx
// apps/desktop/src/renderer/components/ReviewPanel.tsx
<ReviewPanel>
  <Statistics stats={jobResults.statistics} />
  <CutDecisionsList
    decisions={cutDecisions}
    onToggle={handleToggleCut} // 컷 활성화/비활성화
  />
  <ExportButtons
    onExportEDL={handleExportEDL}
    onExportSRT={handleExportSRT}
  />
</ReviewPanel>
```

#### 3.3 상태 관리 (Zustand)
```typescript
// apps/desktop/src/renderer/store/jobStore.ts
interface JobStore {
  jobs: Job[];
  currentJob: Job | null;
  createJob: (params) => Promise<void>;
  updateJobProgress: (jobId, progress) => void;
}

export const useJobStore = create<JobStore>((set, get) => ({
  jobs: [],
  createJob: async (params) => {
    const job = await window.api.createJob(params);
    set({ jobs: [...get().jobs, job], currentJob: job });
  },
  // ...
}));
```

---

### Step 4: EDL/SRT Export 구현 (2~3일)

**목표**: CapCut import 가능한 파일 생성

#### 4.1 EDL Generator
```typescript
// packages/capcut-controller/src/edl-generator.ts
export function generateEDL(cutDecisions: CutDecision[], videoPath: string): string {
  // CMX3600 EDL 포맷
  // TITLE: Cutback Export
  // 001 AX V C 00:00:00:00 00:00:05:12 00:00:00:00 00:00:05:12
  // ...
}
```

#### 4.2 SRT Generator
```typescript
// packages/capcut-controller/src/srt-generator.ts
export function generateSRT(captions: Caption[]): string {
  // 1
  // 00:00:00,000 --> 00:00:03,000
  // 안녕하세요
  // ...
}
```

**구현 사항**:
- Cut decisions를 EDL entry로 변환
- Timecode 계산 (프레임레이트 고려)
- Caption을 SRT 포맷으로 변환
- 파일 저장

---

### Step 5: 통합 테스트 및 디버깅 (3~5일)

**목표**: End-to-End 워크플로우 검증

#### 5.1 테스트 시나리오

**시나리오 1: 광고형 숏폼**
1. 60초 제품 광고 영상 업로드
2. `ad-short-form` 프리셋 선택
3. 분석 실행
4. 결과 확인:
   - 무음 제거 개수
   - Filler word 제거 개수
   - 자연스러움 점수
5. Transcript 뷰어에서 특정 filler 되돌리기
6. EDL/SRT 내보내기
7. CapCut에서 import 테스트

**시나리오 2: 정보형 토킹헤드**
1. 5분 설명 영상 업로드
2. `info-talking-head` 프리셋 선택
3. 분석 실행
4. 자연스러움 점수가 0.75 이상인지 확인
5. 내보내기

#### 5.2 디버깅 체크리스트
- [ ] Python 서비스 자동 시작/종료
- [ ] ffmpeg 없을 때 에러 메시지
- [ ] 대용량 영상(10분+) 처리 성능
- [ ] 영상 파일 손상 시 에러 처리
- [ ] IPC 통신 안정성
- [ ] 로그 파일 생성 확인
- [ ] 메모리 누수 없는지 확인

---

### Step 6: 빌드 및 배포 준비 (2~3일)

**목표**: Windows 실행 파일 생성

#### 6.1 Electron Builder 설정
```json
// apps/desktop/package.json
{
  "build": {
    "appId": "com.cutback.assistant",
    "productName": "Cutback",
    "win": {
      "target": ["nsis"],
      "icon": "build/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "include": "build/installer.nsh"
    },
    "extraResources": [
      {
        "from": "python/stt_service",
        "to": "python/stt_service"
      },
      {
        "from": "presets",
        "to": "presets"
      }
    ]
  }
}
```

#### 6.2 Python 번들링
```bash
# PyInstaller로 Python 서비스를 단일 실행 파일로 변환
cd python/stt_service
pyinstaller --onefile main.py

# 또는 앱 내에서 Python 인터프리터 포함
# (portable Python 사용)
```

#### 6.3 설치 스크립트
```bash
# scripts/build.js
- TypeScript 빌드
- Electron 패키징
- Python 서비스 번들링
- 최종 NSIS 인스톨러 생성
```

---

## Phase 2 기능 (MVP 이후)

### Retake Detection (2주)
- 텍스트 유사도 분석 (Levenshtein distance)
- 음성 품질 점수 계산
- 최선 버전 자동 선택

### CapCut UI Automation (3주)
- Windows Automation API 사용
- CapCut 창 찾기 및 포커스
- 단축키 자동화 (Import, Split, Delete)
- UI 좌표 설정 파일로 관리
- 이미지 인식 fallback (OpenCV.js)

### Zoom Keyframe Automation (2주)
- 강조 단어 자동 감지 (대문자, 반복, 감정 단어)
- Keyframe 포인트 계산
- EDL에 transform 효과 추가

### 자연스러움 점수 시스템 (1주)
- 컷 빈도 페널티
- 짧은 구간 페널티
- 연속 컷 페널티
- Pause 보존 보너스
- 실시간 점수 표시

---

## 우선순위 요약

### 🔴 High Priority (MVP 필수)
1. **Core Pipeline** (Step 1) - 전체 흐름의 핵심
2. **React UI** (Step 3) - 사용자 경험
3. **EDL Export** (Step 4) - CapCut 연동

### 🟡 Medium Priority (MVP 중요)
4. **Electron Main** (Step 2) - 앱 기반
5. **통합 테스트** (Step 5) - 품질 보증

### 🟢 Low Priority (MVP 이후)
6. **빌드/배포** (Step 6) - 공개 배포 시
7. **Phase 2 기능** - 확장 기능

---

## 개발 시 주의사항

### 1. Python 서비스 관리
- **문제**: Python 프로세스 좀비화, 포트 충돌
- **해결**:
  - 앱 종료 시 Python 프로세스 강제 종료
  - 포트 사용 중이면 kill 후 재시작
  - Health check endpoint로 상태 확인

### 2. ffmpeg 의존성
- **문제**: 사용자 PC에 ffmpeg 없을 수 있음
- **해결**:
  - ffmpeg 번들링 (ffmpeg-static 패키지)
  - 또는 설치 가이드 제공

### 3. Whisper 모델 다운로드
- **문제**: 첫 실행 시 모델 다운로드 느림 (large-v3: 3GB)
- **해결**:
  - 설치 시 모델 사전 다운로드
  - 또는 첫 실행 시 프로그레스 바 표시
  - 작은 모델(medium)로 fallback 옵션

### 4. 메모리 관리
- **문제**: 대용량 영상 처리 시 메모리 부족
- **해결**:
  - 오디오만 추출하여 처리
  - Worker thread로 분리
  - 청크 단위 스트리밍 처리

### 5. 타임라인 동기화
- **문제**: Cut decision 적용 후 타임라인 sync 깨짐
- **해결**:
  - 모든 timestamp를 원본 기준으로 저장
  - EDL 생성 시 누적 offset 계산

---

## 예상 일정

### MVP (Phase 1) 완성: **4주**
- Week 1: Core + Electron Main (Step 1-2)
- Week 2: React UI (Step 3)
- Week 3: EDL Export + 통합 테스트 (Step 4-5)
- Week 4: 디버깅 + 문서 정리

### Phase 2: **+8주**
- Week 5-6: Retake Detection
- Week 7-9: CapCut UI Automation
- Week 10-11: Zoom Keyframe + 자연스러움 점수
- Week 12: 통합 및 최적화

### 공개 배포: **+2주**
- Week 13-14: 빌드/배포 파이프라인, 문서 완성

---

## 다음 작업 시작하기

### 바로 시작 가능한 작업
```bash
# 1. Core 패키지 JobManager 구현
cd packages/core/src
# job-manager.ts, pipeline.ts, python-client.ts 생성

# 2. Electron Main Process 구현
cd apps/desktop/src/main
# index.ts, ipc-handlers.ts, window-manager.ts 생성

# 3. React UI 기본 구조
cd apps/desktop/src/renderer
# App.tsx, pages/UploadPage.tsx, components/ 생성
```

---

**Last Updated**: 2026-04-15
**Status**: MVP 개발 진행 중 (40% 완료)
