# PRD: CapCut AI 편집 어시스턴트

## 문제 정의

### 현재 상황
- 숏폼/광고형 영상 편집은 노동 집약적 (무음 제거, 말버릇 편집, 자막 작업에 시간 소모)
- 기존 자동화 툴(Cutback, Descript 등)은 영어 중심이며 한국어 최적화 부족
- CapCut은 인기 있지만 자동화 기능 제한적
- 다중 채널/브랜드 운영 시 일관된 스타일 유지 어려움

### 타겟 페인 포인트
1. **무음 구간 수동 제거**: 10분 영상에 30분 소요
2. **한국어 말버릇 편집**: "어", "음", "약간", "사실" 등 수동 탐색
3. **자막 작업 반복**: 폰트/색상/위치 매번 수동 설정
4. **Retake 정리**: 같은 멘트 여러 번 찍은 것 중 최선 선택 어려움
5. **브랜드별 스타일 관리**: 채널마다 다른 자막 스타일 일일이 적용

## 타겟 사용자

### Primary Persona: 숏폼 크리에이터 "민지"
- 27세, 뷰티/라이프스타일 채널 운영
- 주 3회 유튜브 쇼츠, 인스타 릴스 업로드
- 편집 경험: 중급 (CapCut Desktop 6개월 사용)
- 페인: 촬영은 빠른데 편집에 하루 2~3시간 소요
- 니즈: "자막이랑 호흡 정리만 자동으로 되면 업로드 2배 늘릴 수 있는데..."

### Secondary Persona: 광고 에이전시 "재훈"
- 32세, 프리랜서 영상 PD
- 월 10~15개 브랜드 광고 영상 제작
- 페인: 브랜드별 자막 가이드 맞추느라 템플릿 관리 복잡
- 니즈: "브랜드 프리셋 하나로 자막 스타일 자동 적용되면 시간 30% 절약"

## 핵심 사용 시나리오

### Scenario 1: 빠른 Rough Cut (5분 → 30초)
```
사용자: 촬영한 10분 원본 영상 업로드
시스템:
  1. 무음 구간 자동 제거
  2. 말버릇(어, 음, 약간 등) 자동 제거
  3. Retake 구간 탐지 및 표시
  4. 자막 자동 생성
  5. "광고형 숏폼" 프리셋 적용
결과: 2분 30초 rough cut 완성 → 사용자는 미세 조정만
```

### Scenario 2: 브랜드 자막 프리셋 적용
```
사용자: "이 영상은 A 브랜드 스타일로"
시스템:
  1. A 브랜드 프리셋 로드 (폰트: Pretendard Bold, 색상: #FF6B6B, 위치: 하단 20%, 외곽선 2px)
  2. 자막 자동 생성 및 스타일 일괄 적용
  3. CapCut 프로젝트에 반영
결과: 수작업 30분 → 자동화 2분
```

### Scenario 3: Transcript 기반 미세 편집
```
사용자: Transcript 뷰어에서 제거할 말버릇 클릭 선택
시스템:
  1. 선택된 구간을 타임라인에서 비활성화 표시
  2. 사용자가 "되돌리기" 가능하게 회색 처리
  3. 최종 확정 시 CapCut에서 실제 컷 적용
결과: 텍스트 기반 편집으로 정확도 100%
```

## 핵심 기능

### F1: Auto Import to CapCut
- **목적**: 영상 파일을 자동으로 CapCut 프로젝트에 추가
- **입력**: 영상 파일 경로 또는 폴더
- **처리**:
  1. CapCut Desktop 실행 확인
  2. 신규 프로젝트 생성 또는 기존 프로젝트 열기
  3. 영상 파일 import (드래그 앤 드롭 자동화 또는 단축키)
- **출력**: CapCut 프로젝트 ID, 타임라인 참조
- **예외**: CapCut 미설치, 버전 불일치 → 안내 메시지
- **옵션**: 자동 프로젝트명, 타겟 트랙 선택
- **난이도**: ⭐⭐⭐⚠️ (UI 자동화 리스크)
- **MVP**: ✅ 포함 (Fallback: 수동 import 가이드)

### F2: Remove Silence
- **목적**: 무음 구간 자동 탐지 및 제거
- **입력**: 영상 파일, 프리셋(silence threshold, min duration)
- **처리**:
  1. ffmpeg로 오디오 추출
  2. silero-vad로 음성 구간 탐지
  3. threshold 이하 구간 중 min duration 이상인 구간 리스트업
  4. padding 적용 (pre/post cut)
  5. 컷 포인트 리스트 생성
- **출력**: Cut decisions JSON (timestamp, duration, confidence)
- **예외**: 영상 전체가 무음 → 경고
- **옵션**:
  - silence_threshold_db: -40 ~ -20
  - min_silence_duration_ms: 300 ~ 1000
  - pre_cut_padding_ms: 100 ~ 300
  - post_cut_padding_ms: 100 ~ 300
- **난이도**: ⭐⭐
- **MVP**: ✅ 포함

### F3: Korean Filler Word Removal
- **목적**: 한국어 말버릇 자동 탐지 및 제거
- **입력**: Transcript (word-level timestamp), 한국어 filler 사전
- **처리**:
  1. Whisper STT로 transcript 생성 (word-level timestamp)
  2. Filler word dictionary 매칭
  3. 컨텍스트 분석 (문장 시작/중간/끝에서 제거 강도 조절)
  4. 컷 포인트 리스트 생성
- **출력**: Filler word cut decisions
- **예외**: Transcript 실패 → 수동 입력 옵션
- **옵션**:
  - filler_removal_strength: conservative / balanced / aggressive
  - custom_filler_words: 사용자 추가 단어
- **난이도**: ⭐⭐⭐
- **MVP**: ✅ 포함

**한국어 Filler Word Dictionary (초기)**:
```json
{
  "강도별": {
    "high_confidence": ["어", "음", "어어", "음음", "에에"],
    "medium_confidence": ["약간", "뭔가", "좀", "되게", "진짜", "완전", "엄청"],
    "context_dependent": ["사실", "그니까", "근데", "이제", "그래서", "그럼", "일단"]
  },
  "패턴": {
    "repeated": "같은 단어 2회 이상 반복",
    "hesitation": "0.5초 이상 pause 전후 발화"
  }
}
```

### F4: Retake Detection
- **목적**: 같은 멘트를 여러 번 촬영한 구간 탐지
- **입력**: Transcript
- **처리**:
  1. 텍스트 유사도 분석 (sliding window)
  2. 80% 이상 유사한 구간 그룹화
  3. 각 그룹에서 최선 버전 추천 (유창성, 길이, 음성 품질 기준)
- **출력**: Retake groups, 추천 선택
- **예외**: 유사 구간 없음 → skip
- **옵션**: similarity_threshold: 0.7 ~ 0.95
- **난이도**: ⭐⭐⭐⭐
- **MVP**: ⚠️ 2차 확장 (텍스트 유사도만 MVP 포함)

### F5: Auto Captions with Style Presets
- **목적**: 자막 자동 생성 및 브랜드 스타일 적용
- **입력**: Transcript, 프리셋 (폰트, 색상, 위치, 애니메이션)
- **처리**:
  1. Transcript를 호흡 단위로 segmentation
  2. SRT 파일 생성
  3. 프리셋 스타일 매핑
  4. CapCut에 자막 import (또는 수동 가이드)
- **출력**: SRT 파일, 스타일 메타데이터
- **예외**: 프리셋 없음 → 기본 스타일
- **옵션**:
  - segmentation_mode: by_sentence / by_time / by_breath
  - max_chars_per_line: 10 ~ 30
  - line_break_optimization: true/false (한국어 자연스러운 끊기)
- **난이도**: ⭐⭐⭐
- **MVP**: ✅ 포함 (SRT 생성까지, CapCut import는 수동)

### F6: Zoom In/Out Keyframe Automation
- **목적**: 강조 단어에 자동 줌 효과
- **입력**: Transcript, 강조 단어 리스트 또는 자동 탐지
- **처리**:
  1. 강조 단어 탐지 (대문자, 반복, 감정 단어 등)
  2. 줌 키프레임 포인트 계산
  3. EDL/XML 생성 (CapCut import용)
- **출력**: Keyframe instructions
- **예외**: 강조 단어 없음 → skip
- **옵션**: zoom_intensity: 1.1x ~ 1.3x
- **난이도**: ⭐⭐⭐⭐⚠️
- **MVP**: ⚠️ 2차 확장 (EDL 생성까지만)

### F7: Transcript/Timeline Review UI
- **목적**: 편집 결과를 텍스트와 타임라인에서 검토
- **입력**: Transcript, Cut decisions
- **처리**:
  1. Transcript 뷰어에 컷 구간 시각화
  2. 클릭 시 비디오 플레이어 해당 시점 이동
  3. 제거된 구간 회색 표시, 되돌리기 버튼
- **출력**: 최종 편집 리스트
- **난이도**: ⭐⭐⭐
- **MVP**: ✅ 포함

### F8: Export-Ready Review Flow
- **목적**: 최종 검수 후 CapCut에 적용 또는 EDL 내보내기
- **입력**: 최종 편집 리스트
- **처리**:
  1. Cut decisions를 EDL/XML 포맷 변환
  2. (Option 1) CapCut UI 자동화로 컷 적용
  3. (Option 2) EDL 파일 생성 + 수동 import 가이드
- **출력**: 완성된 CapCut 프로젝트 또는 EDL 파일
- **난이도**: ⭐⭐⭐⭐⚠️
- **MVP**: ✅ EDL 생성까지 포함, UI 자동화는 실험적

## MVP 범위

### Phase 1 (MVP - 4주)
✅ 파일 업로드 및 작업 큐
✅ Remove Silence (ffmpeg + silero-vad)
✅ Whisper STT (word-level timestamp)
✅ Korean Filler Word Removal (패턴 매칭)
✅ Auto Captions (SRT 생성)
✅ Preset System (JSON 기반, 3개 기본 프리셋)
✅ Transcript Review UI (React)
✅ EDL/XML Export
⚠️ CapCut UI Automation (실험적, Fallback: 수동 가이드)

### Phase 2 (확장 - 8주)
- Retake Detection (고급 알고리즘)
- Zoom Keyframe Automation
- 자연스러움 점수 시스템
- CapCut 안정적 자동화 (이미지 인식 + 좌표)
- 브랜드 프리셋 관리 UI
- 배치 처리 (여러 영상 동시 처리)

### Phase 3 (고도화 - 12주 이후)
- 클라우드 동기화 (다중 PC 사용)
- 협업 기능 (팀원과 프리셋 공유)
- AI 기반 후킹 구간 강조
- Premiere Pro 연동
- 웹 버전 (브라우저 기반 경량판)

## 기술 리스크

| 리스크 | 확률 | 영향도 | 완화 전략 |
|--------|------|--------|-----------|
| CapCut UI 자동화 실패 | 높음 | 중간 | EDL/XML export + 수동 import 가이드 제공 |
| CapCut 버전 업데이트로 UI 변경 | 중간 | 높음 | 설정 파일로 UI 좌표 관리, 이미지 인식 fallback |
| Whisper STT 한국어 정확도 부족 | 낮음 | 높음 | faster-whisper large-v3 모델 사용, 사용자 수동 수정 UI |
| Python-Node 통신 불안정 | 낮음 | 중간 | zeromq 재연결 로직, HTTP fallback |
| 대용량 영상 처리 성능 | 중간 | 중간 | Worker thread 활용, 작업 큐 분산 |

## 성공 기준

### 정량적 지표
- MVP 출시 4주 내 달성
- 10분 영상 처리 시간: 5분 이내
- Silence 탐지 정확도: 90% 이상
- Filler word 탐지 재현율: 80% 이상
- 사용자 만족도(검수 시간 절감): 60% 이상

### 정성적 지표
- 사용자 피드백: "Cutback보다 한국어 편집이 편하다"
- 실무 도입: 최소 3개 브랜드/채널에서 활용
- 커뮤니티: 한국어 편집 자동화 툴로 인지도 확보

## 차별화 전략 요약

| Feature | Cutback | Descript | **우리 제품** |
|---------|---------|----------|---------------|
| 한국어 Filler | ❌ | ⚠️ (제한적) | ✅ **전용 사전** |
| 자막 호흡 최적화 | ❌ | ❌ | ✅ **한국어 특화** |
| 브랜드 프리셋 | ⚠️ | ⚠️ | ✅ **다중 저장** |
| 숏폼 템포 프리셋 | ❌ | ❌ | ✅ **3가지 타입** |
| CapCut 연동 | ❌ | ❌ | ✅ **네이티브** |
| 로컬 실행 | ✅ | ❌ (클라우드) | ✅ |
| 가격 | $9.99/mo | $12/mo | **무료 (오픈소스)** |

---

**Last Updated**: 2026-04-15
**Version**: 0.1.0
**Author**: CapCut AI Assistant Team
