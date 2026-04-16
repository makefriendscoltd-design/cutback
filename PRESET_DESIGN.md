# Preset System Design

## 프리셋 시스템 아키텍처

```
preset/
├── types/
│   ├── ad-short-form.json      # 광고형 숏폼
│   ├── info-talking-head.json  # 정보형 토킹헤드
│   └── vlog-style.json         # 브이로그형
├── brands/
│   ├── brand-a.json            # A 브랜드 자막 스타일
│   └── brand-b.json            # B 브랜드 자막 스타일
└── custom/
    └── user-custom-1.json      # 사용자 커스텀 프리셋
```

## 프리셋 파라미터 정의

### 1. Audio Processing Parameters

| 파라미터 | 설명 | 단위 | 범위 |
|----------|------|------|------|
| `silence_threshold_db` | 무음으로 간주할 데시벨 임계값 | dB | -50 ~ -20 |
| `min_silence_duration_ms` | 최소 무음 지속 시간 (이보다 짧으면 무시) | ms | 200 ~ 1500 |
| `pre_cut_padding_ms` | 컷 전 여백 (자연스러운 호흡 유지) | ms | 50 ~ 400 |
| `post_cut_padding_ms` | 컷 후 여백 | ms | 50 ~ 400 |

### 2. Filler Word Parameters

| 파라미터 | 설명 | 값 |
|----------|------|-----|
| `filler_removal_strength` | 말버릇 제거 강도 | conservative / balanced / aggressive |
| `context_aware` | 문맥 인식 제거 (문장 시작/끝 보호) | true / false |
| `preserve_natural_pauses` | 자연스러운 pause 보존 | true / false |

### 3. Caption Parameters

| 파라미터 | 설명 | 예시 |
|----------|------|------|
| `segmentation_mode` | 자막 끊기 방식 | by_sentence / by_time / by_breath |
| `max_chars_per_line` | 한 줄 최대 글자 수 | 10 ~ 30 |
| `max_lines` | 최대 줄 수 | 1 ~ 3 |
| `line_break_optimization` | 한국어 자연스러운 끊기 | true / false |
| `emphasis_words` | 강조 단어 리스트 | ["지금", "특가", "단독"] |

### 4. Style Parameters

| 파라미터 | 설명 | 예시 |
|----------|------|------|
| `font_family` | 폰트 | Pretendard, Noto Sans KR |
| `font_size` | 폰트 크기 | 36 ~ 72 |
| `font_weight` | 폰트 굵기 | 400 ~ 900 |
| `text_color` | 텍스트 색상 | #FFFFFF |
| `outline_color` | 외곽선 색상 | #000000 |
| `outline_width` | 외곽선 두께 | 0 ~ 5 |
| `shadow_enabled` | 그림자 활성화 | true / false |
| `position_vertical` | 세로 위치 | top / center / bottom |
| `position_offset_percent` | 위치 오프셋 | 10 ~ 30 |

### 5. Pacing Parameters

| 파라미터 | 설명 | 값 |
|----------|------|-----|
| `target_tempo` | 목표 템포 (words per minute) | 120 ~ 200 |
| `allow_jump_cuts` | 점프 컷 허용 | true / false |
| `naturalness_score_min` | 최소 자연스러움 점수 (이하면 경고) | 0.5 ~ 0.9 |

## 프리셋 상세 설계

### Preset 1: 광고형 숏폼 (Ad Short-Form)

**타겟**: 15~60초 제품 광고, 프로모션 영상
**특징**: 빠른 템포, 강한 임팩트, 명확한 메시지 전달

```json
{
  "name": "광고형 숏폼",
  "type": "ad-short-form",
  "version": "1.0.0",
  "description": "15~60초 제품 광고 최적화. 빠른 템포, 후킹 강조, 간결한 자막.",

  "audio": {
    "silence_threshold_db": -35,
    "min_silence_duration_ms": 400,
    "pre_cut_padding_ms": 100,
    "post_cut_padding_ms": 150,
    "reasoning": "광고는 템포가 빨라야 하므로 0.4초 이상 무음만 제거. padding은 최소화하되 너무 딱딱하지 않게 100~150ms 유지."
  },

  "filler_words": {
    "removal_strength": "aggressive",
    "context_aware": true,
    "preserve_natural_pauses": false,
    "custom_fillers": ["음", "어", "약간", "뭔가", "좀"],
    "reasoning": "광고는 간결함이 생명. 말버릇 최대한 제거하되, 문맥상 '약간 달콤한' 같은 의미 있는 경우는 보존."
  },

  "captions": {
    "segmentation_mode": "by_breath",
    "max_chars_per_line": 15,
    "max_lines": 2,
    "line_break_optimization": true,
    "emphasis_words": ["지금", "특가", "단독", "최초", "한정", "무료"],
    "reasoning": "숏폼은 짧고 강렬한 자막. 한 줄 15자 이내로 가독성 확보. 강조 단어는 자동 스타일링."
  },

  "style": {
    "font_family": "Pretendard",
    "font_size": 48,
    "font_weight": 800,
    "text_color": "#FFFFFF",
    "outline_color": "#000000",
    "outline_width": 3,
    "shadow_enabled": true,
    "shadow_color": "#000000",
    "shadow_opacity": 0.5,
    "position_vertical": "bottom",
    "position_offset_percent": 20,
    "reasoning": "대비가 강한 흰색 + 검정 외곽선. 하단 20% 위치로 얼굴 가리지 않음. 굵은 폰트로 임팩트."
  },

  "pacing": {
    "target_tempo": 170,
    "allow_jump_cuts": true,
    "naturalness_score_min": 0.6,
    "hook_first_3sec": true,
    "reasoning": "170 WPM은 빠른 광고 템포. 점프 컷 적극 활용. 첫 3초 후킹 구간은 자동 강조."
  },

  "effects": {
    "auto_zoom_on_emphasis": true,
    "zoom_intensity": 1.15,
    "transition_speed": "fast"
  }
}
```

**왜 이렇게 설정했나?**
- **silence_threshold -35dB**: 광고는 배경음악이 깔리는 경우가 많아 너무 낮은 threshold는 오탐 유발
- **min_silence 400ms**: 0.4초 이상만 무음으로 간주 → 빠른 템포 유지
- **aggressive filler removal**: 광고에서 "음", "어"는 치명적, 과감하게 제거
- **15자 max**: 모바일 세로 화면에서 한 눈에 읽을 수 있는 최대 길이
- **170 WPM**: 일반 대화 150 WPM보다 빠름. 광고 표준 템포

---

### Preset 2: 정보형 토킹헤드 (Info Talking-Head)

**타겟**: 3~10분 설명 영상, 강의형 콘텐츠
**특징**: 이해 중심, 적절한 호흡, 정보 전달 명확성

```json
{
  "name": "정보형 토킹헤드",
  "type": "info-talking-head",
  "version": "1.0.0",
  "description": "3~10분 설명/강의형 영상. 이해도 우선, 자연스러운 호흡 유지.",

  "audio": {
    "silence_threshold_db": -38,
    "min_silence_duration_ms": 800,
    "pre_cut_padding_ms": 200,
    "post_cut_padding_ms": 250,
    "reasoning": "정보형은 호흡이 중요. 0.8초 이상만 무음 제거하여 생각 정리 시간 보존. padding 넉넉히."
  },

  "filler_words": {
    "removal_strength": "balanced",
    "context_aware": true,
    "preserve_natural_pauses": true,
    "custom_fillers": ["음", "어", "어어"],
    "reasoning": "과한 편집은 기계적. '약간', '사실' 같은 연결어는 보존해 자연스러움 유지."
  },

  "captions": {
    "segmentation_mode": "by_sentence",
    "max_chars_per_line": 20,
    "max_lines": 2,
    "line_break_optimization": true,
    "emphasis_words": ["중요", "핵심", "정리하면", "결론"],
    "reasoning": "문장 단위 끊기로 의미 전달 명확히. 20자까지 허용하여 문장 완성도 확보."
  },

  "style": {
    "font_family": "Noto Sans KR",
    "font_size": 40,
    "font_weight": 600,
    "text_color": "#FFFFFF",
    "outline_color": "#000000",
    "outline_width": 2,
    "shadow_enabled": false,
    "position_vertical": "bottom",
    "position_offset_percent": 15,
    "reasoning": "가독성 중심. Noto Sans는 정보 전달에 최적화. 외곽선 2px로 깔끔함 유지."
  },

  "pacing": {
    "target_tempo": 140,
    "allow_jump_cuts": true,
    "naturalness_score_min": 0.75,
    "hook_first_3sec": false,
    "reasoning": "140 WPM은 이해하기 편한 속도. 자연스러움 점수 0.75 이상 유지로 과편집 방지."
  },

  "effects": {
    "auto_zoom_on_emphasis": false,
    "transition_speed": "medium"
  }
}
```

**왜 이렇게 설정했나?**
- **800ms min_silence**: 설명 중 생각 정리 시간 필요 → 짧은 pause는 보존
- **balanced filler**: "사실 이건 말이죠"에서 '사실'은 의미 있음, 맥락 고려
- **문장 단위 segmentation**: "이 기능은 / 매우 중요합니다" (O), "이 기능은 매우 / 중요합니다" (X)
- **140 WPM**: TED 강연 평균 속도, 이해도 최적화
- **naturalness 0.75**: 과편집 방지, 자연스러운 흐름 중시

---

### Preset 3: 브이로그형 (Vlog Style)

**타겟**: 1~5분 일상 브이로그, 개인 채널
**특징**: 친근함, 자연스러움, 감성적 연결

```json
{
  "name": "브이로그형",
  "type": "vlog-style",
  "version": "1.0.0",
  "description": "1~5분 일상 브이로그. 친근하고 자연스러운 편집.",

  "audio": {
    "silence_threshold_db": -40,
    "min_silence_duration_ms": 1000,
    "pre_cut_padding_ms": 300,
    "post_cut_padding_ms": 300,
    "reasoning": "브이로그는 너무 빡빡하면 피곤함. 1초 이상만 무음 제거하고 호흡 충분히 보존."
  },

  "filler_words": {
    "removal_strength": "conservative",
    "context_aware": true,
    "preserve_natural_pauses": true,
    "custom_fillers": ["음", "어"],
    "reasoning": "브이로그는 자연스러움이 매력. '약간', '진짜', '완전' 같은 표현은 친근함의 일부."
  },

  "captions": {
    "segmentation_mode": "by_time",
    "max_chars_per_line": 18,
    "max_lines": 2,
    "line_break_optimization": true,
    "emphasis_words": [],
    "reasoning": "시간 기반 끊기(3~4초 단위)로 시청 리듬 유지. 강조 단어 없이 자연스럽게."
  },

  "style": {
    "font_family": "Pretendard",
    "font_size": 42,
    "font_weight": 500,
    "text_color": "#FFFFFF",
    "outline_color": "#FFB6C1",
    "outline_width": 2,
    "shadow_enabled": true,
    "shadow_color": "#FFC0CB",
    "shadow_opacity": 0.3,
    "position_vertical": "bottom",
    "position_offset_percent": 18,
    "reasoning": "부드러운 핑크 외곽선/그림자로 감성 연출. 폰트 굵기 500으로 편안함."
  },

  "pacing": {
    "target_tempo": 130,
    "allow_jump_cuts": false,
    "naturalness_score_min": 0.85,
    "hook_first_3sec": false,
    "reasoning": "130 WPM은 느긋한 대화 속도. 점프 컷 최소화로 자연스러운 흐름. 자연스러움 0.85 이상."
  },

  "effects": {
    "auto_zoom_on_emphasis": false,
    "transition_speed": "slow"
  }
}
```

**왜 이렇게 설정했나?**
- **1000ms min_silence**: 브이로그는 여유가 매력, 긴 pause도 보존
- **conservative filler**: "오늘 진짜 완전 힘들었어"에서 '진짜', '완전'은 감정 표현의 일부
- **시간 기반 segmentation**: 문장보다 시청 리듬 우선
- **핑크 외곽선**: 감성적, 친근한 분위기 (브랜드 색상 변경 가능)
- **점프 컷 X**: 자연스러운 흐름이 브이로그 정체성

---

## 브랜드 프리셋 예시

### Brand A: 뷰티 브랜드

```json
{
  "name": "Brand A - 뷰티",
  "type": "brand",
  "base_preset": "ad-short-form",
  "overrides": {
    "style": {
      "font_family": "Pretendard",
      "font_weight": 700,
      "text_color": "#FFB6C1",
      "outline_color": "#FFFFFF",
      "outline_width": 3,
      "position_offset_percent": 25
    },
    "captions": {
      "emphasis_words": ["NEW", "신제품", "한정", "특가"]
    }
  },
  "reasoning": "뷰티 브랜드 컬러 #FFB6C1(핑크) 반영. 신제품 강조."
}
```

### Brand B: 테크 리뷰

```json
{
  "name": "Brand B - 테크",
  "type": "brand",
  "base_preset": "info-talking-head",
  "overrides": {
    "style": {
      "font_family": "Roboto Mono",
      "font_weight": 600,
      "text_color": "#00FF00",
      "outline_color": "#000000",
      "outline_width": 2,
      "position_vertical": "top",
      "position_offset_percent": 10
    }
  },
  "reasoning": "테크 느낌의 모노스페이스 폰트 + 그린 컬러. 상단 자막으로 차별화."
}
```

## 자연스러움 점수 (Naturalness Score) 계산

```python
def calculate_naturalness_score(cut_decisions, original_duration):
    """
    0.0 (완전 기계적) ~ 1.0 (완전 자연스러움)
    """
    score = 1.0

    # 1. 과도한 컷 빈도 페널티
    cut_frequency = len(cut_decisions) / (original_duration / 60)  # cuts per minute
    if cut_frequency > 20:  # 분당 20개 이상 컷은 과편집
        score -= (cut_frequency - 20) * 0.01

    # 2. 너무 짧은 구간 페널티
    for decision in cut_decisions:
        if decision['duration'] < 0.3:  # 0.3초 이하는 너무 짧음
            score -= 0.02

    # 3. 연속 컷 페널티 (호흡 없이 연속 컷)
    for i in range(len(cut_decisions) - 1):
        gap = cut_decisions[i+1]['start'] - cut_decisions[i]['end']
        if gap < 0.5:  # 0.5초 이내 연속 컷
            score -= 0.03

    # 4. 자연스러운 pause 보존 보너스
    preserved_pauses = count_preserved_pauses(cut_decisions)
    score += preserved_pauses * 0.02

    return max(0.0, min(1.0, score))
```

## 프리셋 확장 전략

### 사용자 커스텀 프리셋 생성 플로우
```
1. 기존 프리셋 선택 (base)
2. UI에서 파라미터 조정
3. 샘플 영상으로 테스트
4. "프리셋으로 저장" 버튼
5. custom/ 폴더에 JSON 저장
```

### 커뮤니티 프리셋 공유 (Phase 3)
- GitHub repo에 community-presets/ 폴더
- 사용자가 Pull Request로 프리셋 기여
- 인기 프리셋은 공식 프리셋으로 승격

---

**Last Updated**: 2026-04-15
**Version**: 1.0.0
