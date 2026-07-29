# Mode B: Voiceover Crosscut - Product Requirements Document

## 1. 문제 정의

### 현재 상황
Cutback은 현재 **단일 영상의 토킹헤드 편집**에 특화되어 있음:
- 화자가 직접 말하는 롱폼/미드폼 가로 영상
- STT → 무음/필러 제거 → 자막 생성
- 단일 소스, 선형 파이프라인

### 새로운 니즈
**광고형 숏폼 제작 워크플로우**가 완전히 다름:
- 보이스오버 스크립트가 미리 작성됨
- 여러 개의 짧은 B-roll 클립이 준비됨 (제품 클로즈업, 사용 장면, 라이프스타일 컷)
- 스크립트 문장별로 적합한 영상을 매칭해서 붙여야 함
- 길이 조정 (trim/speed/repeat)이 필요
- 자막 + 헤드카피 오버레이

**기존 Mode A로는 불가능**:
- 다중 소스 입력 없음
- 보이스오버와 영상 분리 편집 없음
- 문장-클립 매칭 로직 없음
- rough cut 자동 생성 없음

## 2. 왜 이 기능이 필요한가

### 타겟 사용자
1. **마케터/광고 제작자**
   - 제품 광고 숏폼을 빠르게 제작해야 함
   - 스크립트는 있고, B-roll 소스도 있지만 편집이 병목
   - 1차 rough cut만 자동으로 만들어줘도 시간 절약

2. **유튜버/콘텐츠 크리에이터**
   - 정보형 숏폼 (예: "3가지 팁") 제작
   - 녹화한 여러 클립을 빠르게 조합하고 싶음

3. **에이전시**
   - 클라이언트별로 비슷한 패턴의 광고를 대량 생성
   - 템플릿화된 rough cut generator가 필요

### 비즈니스 가치
- **생산성 향상**: 수동 편집 3-5시간 → 자동 rough cut 10분 + 검수 30분
- **재사용성**: 한번 만든 스크립트 + B-roll 세트를 여러 버전으로 재조합 가능
- **전문 편집툴로의 진화**: 토킹헤드 → 광고 숏폼 → 향후 장편 다큐까지

## 3. 기존 모드와의 차이

| 항목 | Mode A: Speaker Edit | Mode B: Voiceover Crosscut |
|------|---------------------|---------------------------|
| **입력** | 단일 영상 | 스크립트 + 다중 영상 클립 |
| **음성** | 화자 음성 (영상 내) | 보이스오버 (별도) |
| **처리** | 시간축 컷 (무음/필러 제거) | 공간축 조합 (클립 매칭) |
| **출력** | 컷된 영상 + 자막 | rough cut 타임라인 |
| **자동화 수준** | 자동 컷 추천 | 자동 매칭 + 수동 검수 |
| **타겟** | 롱폼/미드폼 가로 | 숏폼 광고/정보형 |

## 4. 핵심 사용자 시나리오

### Scenario 1: 제품 광고 제작
```
사용자: 마케터
입력:
  - 보이스오버 스크립트: "새로운 스마트워치가 출시되었습니다.
    심박수 모니터링부터 수면 추적까지.
    이제 건강 관리가 더 쉬워집니다."
  - B-roll 클립 5개:
    1. watch_closeup.mp4 (제품 클로즈업)
    2. heart_rate.mp4 (심박수 화면)
    3. sleep_tracking.mp4 (수면 그래프)
    4. lifestyle_jogging.mp4 (조깅하는 사람)
    5. unboxing.mp4 (언박싱)

프로세스:
  1. 스크립트 문장 분절: 3개 문장
  2. 각 문장마다 적합한 클립 매칭:
     - 문장 1 → watch_closeup (제품 소개니까)
     - 문장 2 → heart_rate (심박수 언급) + sleep_tracking (수면 언급)
     - 문장 3 → lifestyle_jogging (건강 관리 = 라이프스타일)
  3. 길이 조정:
     - 문장 2 (5초)인데 heart_rate (2초) → 2.5배 속도 느리게 또는 repeat
  4. 1차 rough cut 생성
  5. 사용자 검수: 문장 3을 unboxing으로 교체
  6. CapCut JSON 출력

결과: 15초 광고 rough cut 완성
```

### Scenario 2: 정보형 숏폼
```
사용자: 유튜버
입력:
  - 보이스오버: "집에서 할 수 있는 3가지 운동.
    첫째, 플랭크. 둘째, 스쿼트. 셋째, 버피."
  - B-roll 클립 4개:
    1. plank_demo.mp4
    2. squat_demo.mp4
    3. burpee_demo.mp4
    4. intro_home.mp4 (집 인테리어)

프로세스:
  1. 문장 분절: 4개 (인트로 + 3가지)
  2. 매칭:
     - "집에서..." → intro_home
     - "플랭크" → plank_demo
     - "스쿼트" → squat_demo
     - "버피" → burpee_demo
  3. 자동 trim: 각 동작 2-3초씩만
  4. 자막 오버레이: "1. 플랭크", "2. 스쿼트", "3. 버피"

결과: 20초 정보형 숏폼 rough cut
```

## 5. MVP 범위

### Phase 1: Core Functionality (MVP)
**목표**: 자동 rough cut 생성 + 수동 검수

**포함 기능**:
- [x] 스크립트 텍스트 입력 (보이스오버 오디오는 Phase 2)
- [x] 여러 영상 클립 업로드 (drag & drop)
- [x] 문장 자동 분절 (간단한 정규식 기반)
- [x] 클립 메타데이터 추출 (duration, 파일명 기반 태그 추정)
- [x] 문장-클립 매칭 (키워드 + 길이 적합도)
- [x] 1차 rough cut 타임라인 생성
- [x] 길이 조정 전략 (trim, speed, repeat)
- [x] 검수 UI (후보 클립 교체)
- [x] JSON 타임라인 출력

**제외 (Phase 2+)**:
- ~~보이스오버 오디오 STT~~ (Phase 2)
- ~~비전 모델 기반 shot detection~~ (Phase 2)
- ~~CLIP embedding 기반 semantic matching~~ (Phase 3)
- ~~자동 전환 효과~~ (Phase 2)
- ~~CapCut 직접 적용 자동화~~ (Phase 2)

### Phase 2: Quality & Automation
- 보이스오버 오디오 입력 + STT
- ffmpeg scene detection 통합
- 기본 전환 효과 (crossfade, cut)
- CapCut JSON 직접 import 자동화

### Phase 3: Intelligence
- CLIP 모델로 시각적 semantic matching
- Shot detection 고도화 (PySceneDetect)
- 브랜드 안전 필터
- 멀티캠 지원

## 6. 기능 명세

### 6.1 Voiceover/Script Ingest
**입력**:
- 스크립트 텍스트 (plain text)
- 또는 보이스오버 오디오 파일 (.mp3, .wav)

**출력**:
```typescript
interface SentenceTimeline {
  sentences: Sentence[];
  totalDuration: number; // 보이스오버 총 길이 (오디오인 경우)
}

interface Sentence {
  id: string;
  text: string;
  startTime: number; // 보이스오버에서의 시작 시간 (초)
  endTime: number;   // 보이스오버에서의 종료 시간 (초)
  duration: number;  // 이 문장의 길이 (초)
  keywords: string[]; // 추출된 키워드
}
```

**처리**:
1. 텍스트인 경우:
   - 정규식으로 문장 분절 (`.`, `!`, `?` 기준)
   - duration은 예상치 계산 (한국어 평균 읽기 속도: 초당 3-4음절)
   - 키워드 추출 (형태소 분석 또는 빈도 기반)

2. 오디오인 경우:
   - STT로 텍스트 + 타임스탬프 추출
   - 문장 경계에서 자동 분절
   - 각 문장의 실제 startTime, endTime 사용

### 6.2 Sentence Segmentation
**알고리즘** (Phase 1 - 간단한 규칙 기반):
```typescript
function segmentSentences(text: string): Sentence[] {
  // 1. 문장부호 기준 split
  const raw = text.split(/([.!?])\s+/).filter(s => s.trim());

  // 2. 너무 짧은 문장 병합 (3단어 미만)
  const merged = mergeShor

tSentences(raw);

  // 3. duration 예측
  const avgReadingSpeed = 3.5; // 초당 음절
  return merged.map((s, i) => ({
    id: `sent_${i}`,
    text: s,
    startTime: calculateStart(merged.slice(0, i)),
    endTime: calculateEnd(merged.slice(0, i+1)),
    duration: countSyllables(s) / avgReadingSpeed,
    keywords: extractKeywords(s)
  }));
}
```

### 6.3 Multi-Clip Asset Indexing
**입력**: 여러 영상 파일 경로 배열

**출력**:
```typescript
interface AssetIndex {
  assets: Asset[];
}

interface Asset {
  id: string;
  filePath: string;
  fileName: string;
  duration: number;
  shots: Shot[]; // 장면 분절 (Phase 1에서는 전체를 1개 shot으로)
  metadata: AssetMetadata;
}

interface Shot {
  id: string;
  assetId: string;
  inPoint: number;  // 이 shot의 시작점 (asset 내 시간)
  outPoint: number; // 이 shot의 종료점
  duration: number;
  tags: string[];   // 추정된 태그
  features: ShotFeatures;
}

interface ShotFeatures {
  motionIntensity: 'low' | 'medium' | 'high'; // 움직임 강도
  hasface: boolean;        // 인물 presence (추정)
  isCloseup: boolean;      // 클로즈업 여부 (추정)
  dominantColor: string;   // 주 색상 (hex)
  estimatedScene: string;  // 추정 장면 ("product", "lifestyle", "text", etc.)
}

interface AssetMetadata {
  fps: number;
  resolution: { width: number; height: number };
  codec: string;
}
```

**처리** (Phase 1 MVP):
```typescript
async function indexAssets(filePaths: string[]): Promise<AssetIndex> {
  const assets: Asset[] = [];

  for (const path of filePaths) {
    // 1. ffprobe로 메타데이터 추출
    const metadata = await ffprobeMetadata(path);

    // 2. 파일명 기반 태그 추정
    const tags = extractTagsFromFilename(path);
    // 예: "product_closeup_watch.mp4" → ["product", "closeup", "watch"]

    // 3. Shot 생성 (Phase 1: 전체를 1개 shot으로)
    const shot: Shot = {
      id: `shot_${uuid()}`,
      assetId: path,
      inPoint: 0,
      outPoint: metadata.duration,
      duration: metadata.duration,
      tags,
      features: {
        motionIntensity: 'medium', // 기본값
        hasface: tags.includes('person') || tags.includes('face'),
        isCloseup: tags.includes('closeup'),
        dominantColor: '#000000',
        estimatedScene: guessSceneType(tags)
      }
    };

    assets.push({
      id: path,
      filePath: path,
      fileName: getFileName(path),
      duration: metadata.duration,
      shots: [shot],
      metadata
    });
  }

  return { assets };
}
```

### 6.4 Sentence-to-Clip Recommendation
**입력**:
- `SentenceTimeline`
- `AssetIndex`

**출력**:
```typescript
interface MatchResult {
  sentenceId: string;
  candidates: ClipCandidate[];
}

interface ClipCandidate {
  shotId: string;
  assetId: string;
  score: number;           // 0.0 ~ 1.0
  reasons: string[];       // 점수 근거
  suggestedInPoint: number;
  suggestedOutPoint: number;
  adjustmentStrategy: AdjustmentStrategy;
}

interface AdjustmentStrategy {
  method: 'trim' | 'speed' | 'repeat' | 'freeze';
  params: {
    speed?: number;        // 배속 (0.5 = 느리게, 2.0 = 빠르게)
    repeatCount?: number;  // 반복 횟수
    trimIn?: number;       // trim 시작점
    trimOut?: number;      // trim 종료점
  };
}
```

### 6.5 Clip Scoring
**점수 계산 규칙**:

```typescript
function scoreClip(sentence: Sentence, shot: Shot): number {
  let score = 0.0;

  // 1. 키워드 매칭 (40점)
  const keywordMatch = calculateKeywordMatch(sentence.keywords, shot.tags);
  score += keywordMatch * 0.4;

  // 2. 길이 적합도 (30점)
  const lengthFit = calculateLengthFit(sentence.duration, shot.duration);
  score += lengthFit * 0.3;

  // 3. 장면 타입 적합도 (20점)
  const sceneMatch = calculateSceneMatch(sentence, shot);
  score += sceneMatch * 0.2;

  // 4. 다양성 보너스 (10점) - 이전에 사용 안 한 클립 우대
  const diversityBonus = calculateDiversityBonus(shot, previousSelections);
  score += diversityBonus * 0.1;

  return Math.min(1.0, score);
}

function calculateKeywordMatch(keywords: string[], tags: string[]): number {
  const matches = keywords.filter(k => tags.some(t =>
    t.includes(k) || k.includes(t)
  )).length;
  return matches / Math.max(keywords.length, 1);
}

function calculateLengthFit(targetDuration: number, clipDuration: number): number {
  const ratio = clipDuration / targetDuration;

  // 이상적: 0.8 ~ 1.5배
  if (ratio >= 0.8 && ratio <= 1.5) return 1.0;

  // 허용: 0.5 ~ 3.0배
  if (ratio >= 0.5 && ratio <= 3.0) return 0.7;

  // 그 외: 페널티
  return 0.3;
}
```

### 6.6 Automatic Rough Cut Generation
**입력**: `MatchResult[]` (각 문장의 매칭 결과)

**출력**:
```typescript
interface RoughCutTimeline {
  tracks: Track[];
  totalDuration: number;
}

interface Track {
  type: 'video' | 'audio' | 'caption';
  clips: TimelineClip[];
}

interface TimelineClip {
  id: string;
  trackType: 'video' | 'audio' | 'caption';
  sentenceId: string;
  assetId: string;
  shotId: string;

  // 타임라인상 위치
  timelineStart: number;
  timelineEnd: number;

  // 소스 클립 정보
  sourceIn: number;
  sourceOut: number;

  // 조정
  playbackSpeed: number;
  repeatCount: number;

  // 메타
  confidence: number;
  alternatives: ClipCandidate[]; // top-3 후보
  notes: string;
}
```

**알고리즘**:
```typescript
function generateRoughCut(
  sentences: Sentence[],
  matchResults: MatchResult[]
): RoughCutTimeline {
  const videoTrack: TimelineClip[] = [];
  let currentTime = 0;

  for (const sentence of sentences) {
    const match = matchResults.find(m => m.sentenceId === sentence.id);
    const bestCandidate = match.candidates[0]; // 가장 높은 점수

    // 길이 조정
    const adjustment = bestCandidate.adjustmentStrategy;
    let clipDuration = sentence.duration;

    if (adjustment.method === 'speed') {
      clipDuration = (bestCandidate.suggestedOutPoint - bestCandidate.suggestedInPoint)
                    / adjustment.params.speed;
    } else if (adjustment.method === 'trim') {
      clipDuration = adjustment.params.trimOut - adjustment.params.trimIn;
    }

    videoTrack.push({
      id: `clip_${sentence.id}`,
      trackType: 'video',
      sentenceId: sentence.id,
      assetId: bestCandidate.assetId,
      shotId: bestCandidate.shotId,
      timelineStart: currentTime,
      timelineEnd: currentTime + clipDuration,
      sourceIn: bestCandidate.suggestedInPoint,
      sourceOut: bestCandidate.suggestedOutPoint,
      playbackSpeed: adjustment.params.speed || 1.0,
      repeatCount: adjustment.params.repeatCount || 1,
      confidence: bestCandidate.score,
      alternatives: match.candidates.slice(1, 4),
      notes: bestCandidate.reasons.join('; ')
    });

    currentTime += clipDuration;
  }

  return {
    tracks: [
      { type: 'video', clips: videoTrack },
      { type: 'audio', clips: [] }, // 보이스오버는 별도
      { type: 'caption', clips: [] } // 자막은 별도 생성
    ],
    totalDuration: currentTime
  };
}
```

### 6.7 Speed Adjustment Strategy
**결정 규칙**:
```typescript
function decideAdjustment(
  targetDuration: number,
  clipDuration: number
): AdjustmentStrategy {
  const ratio = clipDuration / targetDuration;

  // Case 1: 거의 맞음 (±20%)
  if (ratio >= 0.8 && ratio <= 1.2) {
    return { method: 'trim', params: {
      trimIn: 0,
      trimOut: targetDuration
    }};
  }

  // Case 2: 클립이 짧음 (50% ~ 80%)
  if (ratio >= 0.5 && ratio < 0.8) {
    // 속도 느리게 (0.6배 ~ 0.8배)
    const speed = ratio;
    return { method: 'speed', params: { speed }};
  }

  // Case 3: 클립이 매우 짧음 (<50%)
  if (ratio < 0.5) {
    // 반복 또는 freeze
    if (clipDuration < 1.0) {
      return { method: 'freeze', params: {} };
    }
    const repeatCount = Math.ceil(targetDuration / clipDuration);
    return { method: 'repeat', params: { repeatCount }};
  }

  // Case 4: 클립이 김 (120% ~ 300%)
  if (ratio > 1.2 && ratio <= 3.0) {
    // 속도 빠르게 또는 trim
    if (ratio < 2.0) {
      return { method: 'speed', params: { speed: ratio }};
    } else {
      return { method: 'trim', params: {
        trimIn: 0,
        trimOut: targetDuration
      }};
    }
  }

  // Case 5: 클립이 매우 김 (>300%)
  return { method: 'trim', params: {
    trimIn: 0,
    trimOut: targetDuration
  }};
}
```

### 6.8 Review and Replace Flow
**UI 요구사항**:
- 문장별로 선택된 클립 미리보기
- confidence 점수 표시
- top-3 후보 썸네일 표시
- 클릭으로 후보 교체
- 조정 방식 (trim/speed/repeat) 표시 및 수정 가능

**데이터 업데이트**:
```typescript
function replaceClip(
  timeline: RoughCutTimeline,
  sentenceId: string,
  newCandidateIndex: number
): RoughCutTimeline {
  const clip = timeline.tracks[0].clips.find(c => c.sentenceId === sentenceId);
  const newCandidate = clip.alternatives[newCandidateIndex];

  // 클립 정보 업데이트
  clip.assetId = newCandidate.assetId;
  clip.shotId = newCandidate.shotId;
  clip.sourceIn = newCandidate.suggestedInPoint;
  clip.sourceOut = newCandidate.suggestedOutPoint;
  clip.playbackSpeed = newCandidate.adjustmentStrategy.params.speed || 1.0;
  clip.confidence = newCandidate.score;
  clip.notes = newCandidate.reasons.join('; ');

  return timeline;
}
```

### 6.9 Headline / Caption Overlay Compatibility
**자막 생성 규칙**:
- 각 문장을 자막으로 변환
- 타임라인 동기화 (문장 duration = 자막 duration)

**헤드카피** (광고용):
- 프리셋에서 정의
- 예: 첫 문장에는 "NEW!" 오버레이
- 마지막 문장에는 "지금 구매하세요" CTA

```typescript
interface CaptionClip extends TimelineClip {
  text: string;
  style: {
    fontSize: number;
    fontWeight: number;
    color: string;
    position: 'top' | 'center' | 'bottom';
    effect?: 'fade-in' | 'slide-up' | 'typewriter';
  };
}
```

## 7. 향후 확장 포인트

### Phase 2
- 보이스오버 오디오 입력 + STT
- Scene detection (ffmpeg 또는 PySceneDetect)
- 기본 전환 효과
- CapCut 직접 적용 자동화

### Phase 3
- CLIP embedding 기반 semantic matching
- 얼굴 인식 (face detection)
- 제품 인식 (object detection)
- 브랜드 안전 필터 (NSFW detection)

### Phase 4
- Multicam 지원
- A-roll / B-roll lane 분리
- 오디오 waveform 기반 스무딩
- GPT-4 기반 스토리텔링 분석

## 8. 성공 지표

### MVP 성공 기준
- [ ] 3문장 스크립트 + 5개 클립 입력 시 rough cut 생성 가능
- [ ] 80% 이상의 문장에서 적합한 클립 매칭 (사용자 테스트)
- [ ] 검수 시간 5분 이내로 rough cut 완성 가능
- [ ] CapCut 호환 JSON 출력 정상 동작

### Long-term 지표
- 사용자당 월 평균 rough cut 생성 횟수
- 후보 클립 교체 비율 (낮을수록 자동 매칭 정확도 높음)
- rough cut → 최종 영상 전환율
- 편집 시간 절감 비율

---

**Document Version**: 1.0.0
**Last Updated**: 2026-04-16
**Owner**: Cutback Team
