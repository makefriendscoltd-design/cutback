import React, { useState, useEffect } from 'react';

export interface ThresholdValues {
  /** silence threshold in dB. -50 (관대, 작은 소리도 무음 취급) ~ -20 (엄격) */
  silenceThresholdDb: number;
  /** 최소 무음 길이 (ms) */
  minSilenceDurationMs: number;
  /** filler word 제거 강도 */
  fillerStrength: 'conservative' | 'balanced' | 'aggressive';
}

interface Props {
  values: ThresholdValues;
  onChange: (next: ThresholdValues) => void;
  /** 마지막 recompute 가 걸린 시간 (ms) — UX 피드백 */
  lastRecomputeMs?: number;
  /** preview 가 진행 중인지 (debounce 후 IPC 응답 대기) */
  isComputing?: boolean;
  /** "원본 적용" 버튼 — 슬라이더 값을 0 으로 reset */
  onReset?: () => void;
  /** preset baseline (reset 의 기준값) */
  baseline?: ThresholdValues;
}

const STRENGTH_OPTIONS: ThresholdValues['fillerStrength'][] = [
  'conservative',
  'balanced',
  'aggressive',
];

const STRENGTH_LABELS = {
  conservative: '보수적',
  balanced: '균형',
  aggressive: '공격적',
};

/**
 * Live Analysis Timeline 옆에 붙는 슬라이더/토글 패널.
 * 값을 바꿀 때마다 onChange 호출 → LiveAnalysisPage 가 debounce 걸어 recompute IPC 호출.
 *
 * 실제 ffmpeg 편집은 export 단계에서만 실행되므로 슬라이더는 비파괴적이다.
 * "원본 적용" 버튼은 단순히 baseline 값으로 되돌린다.
 */
export default function ThresholdControls({
  values,
  onChange,
  lastRecomputeMs,
  isComputing,
  onReset,
  baseline,
}: Props) {
  return (
    <div
      style={{
        padding: 16,
        background: 'var(--bg-secondary)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <h3 style={{ margin: 0, fontSize: 14 }}>임계값 조정</h3>
        <span
          style={{
            fontSize: 11,
            color: isComputing ? 'var(--accent-primary)' : 'var(--text-muted)',
          }}
        >
          {isComputing
            ? '미리보기 계산 중...'
            : lastRecomputeMs
            ? `${lastRecomputeMs}ms`
            : ''}
        </span>
      </div>

      {/* Silence threshold dB */}
      <SliderRow
        label="무음 감도 (dB)"
        hint={`${values.silenceThresholdDb} dB · 낮을수록 작은 소리도 무음으로 취급`}
        min={-50}
        max={-20}
        step={1}
        value={values.silenceThresholdDb}
        onChange={(v) => onChange({ ...values, silenceThresholdDb: v })}
      />

      {/* Min silence duration ms */}
      <SliderRow
        label="최소 무음 길이 (ms)"
        hint={`${values.minSilenceDurationMs}ms 이상 지속되는 무음만 제거`}
        min={100}
        max={2000}
        step={50}
        value={values.minSilenceDurationMs}
        onChange={(v) => onChange({ ...values, minSilenceDurationMs: v })}
      />

      {/* Filler strength toggle */}
      <div>
        <div
          style={{
            fontSize: 12,
            color: 'var(--text-secondary)',
            marginBottom: 6,
            display: 'flex',
            justifyContent: 'space-between',
          }}
        >
          <span>말버릇 제거 강도</span>
          <span style={{ color: 'var(--text-muted)' }}>{STRENGTH_LABELS[values.fillerStrength]}</span>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {STRENGTH_OPTIONS.map((opt) => {
            const active = values.fillerStrength === opt;
            return (
              <button
                key={opt}
                onClick={() => onChange({ ...values, fillerStrength: opt })}
                style={{
                  flex: 1,
                  padding: '6px 0',
                  fontSize: 12,
                  background: active ? 'var(--accent-primary)' : 'var(--bg-active)',
                  color: active ? '#fff' : 'var(--text-secondary)',
                  border: 'none',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  fontWeight: active ? 600 : 400,
                  transition: 'background 120ms',
                }}
              >
                {STRENGTH_LABELS[opt]}
              </button>
            );
          })}
        </div>
      </div>

      {baseline && onReset && (
        <button
          onClick={onReset}
          className="btn btn-secondary"
          style={{ fontSize: 12, padding: '6px 12px' }}
          disabled={
            values.silenceThresholdDb === baseline.silenceThresholdDb &&
            values.minSilenceDurationMs === baseline.minSilenceDurationMs &&
            values.fillerStrength === baseline.fillerStrength
          }
        >
          프리셋 기본값으로 되돌리기
        </button>
      )}
    </div>
  );
}

function SliderRow({
  label,
  hint,
  min,
  max,
  step,
  value,
  onChange,
}: {
  label: string;
  hint: string;
  min: number;
  max: number;
  step: number;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <div>
      <div
        style={{
          fontSize: 12,
          color: 'var(--text-secondary)',
          marginBottom: 6,
        }}
      >
        {label}
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ width: '100%', cursor: 'pointer' }}
      />
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{hint}</div>
    </div>
  );
}

/** preset 의 audio/filler_words 에서 슬라이더 baseline 값 추출 */
export function deriveBaseline(preset: {
  audio?: { silence_threshold_db?: number; min_silence_duration_ms?: number };
  filler_words?: { removal_strength?: 'conservative' | 'balanced' | 'aggressive' };
} | null | undefined): ThresholdValues {
  return {
    silenceThresholdDb: preset?.audio?.silence_threshold_db ?? -35,
    minSilenceDurationMs: preset?.audio?.min_silence_duration_ms ?? 400,
    fillerStrength: preset?.filler_words?.removal_strength ?? 'balanced',
  };
}
