import React from 'react';
import { CUT_COLORS, CUT_LABELS } from './OverlayLayer';

interface CutDetail {
  id: string;
  type: keyof typeof CUT_COLORS;
  start: number;
  end: number;
  duration: number;
  confidence: number;
  reason: string;
  reasonText?: string;
  source: string;
  presetRule?: string;
  enabled: boolean;
  reviewRequired?: boolean;
  metadata?: Record<string, unknown>;
}

interface DetailPanelProps {
  cut: CutDetail | null;
  onToggleEnabled?: (cutId: string, enabled: boolean) => void;
}

const SOURCE_LABELS: Record<string, string> = {
  automatic: '자동 감지',
  manual_override: '수동 추가',
  preset_rule: '프리셋 규칙',
  calibration: '학습값 적용',
};

const REASON_LABELS: Record<string, string> = {
  silence_over_threshold: '무음 (threshold 초과)',
  filler_detected: '말버릇 감지',
  duplicate_phrase: '중복 발화 (재시도)',
  manual_override: '수동 지정',
  preset_rule: '프리셋 규칙',
  caption_segment: '자막 세그먼트',
};

function formatTime(s: number): string {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  const ms = Math.floor((s % 1) * 1000);
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}.${String(ms).padStart(3, '0')}`;
}

/** 우측 상세 패널: 선택된 cut 의 시작/종료/이유/confidence/preset rule 표시 */
export default function DetailPanel({ cut, onToggleEnabled }: DetailPanelProps) {
  if (!cut) {
    return (
      <div
        style={{
          padding: 20,
          color: 'var(--text-secondary)',
          fontSize: 13,
          lineHeight: 1.6,
        }}
      >
        타임라인의 색상 구간을 클릭하면 상세 정보가 여기 표시됩니다.
        <ul style={{ marginTop: 12, paddingLeft: 20 }}>
          <li>회색: 무음</li>
          <li>주황: 말버릇</li>
          <li>분홍: 재시도 후보</li>
          <li>파랑 띠: 자막 세그먼트</li>
        </ul>
      </div>
    );
  }

  const confidencePct = Math.round(cut.confidence * 100);
  const confidenceColor =
    cut.confidence >= 0.8
      ? '#4ade80'
      : cut.confidence >= 0.6
      ? '#facc15'
      : '#f87171';

  return (
    <div style={{ padding: 20, fontSize: 13, lineHeight: 1.6 }}>
      {/* 타입 배지 */}
      <div
        style={{
          display: 'inline-block',
          padding: '4px 10px',
          background: CUT_COLORS[cut.type],
          color: '#fff',
          borderRadius: 4,
          fontWeight: 600,
          fontSize: 11,
          marginBottom: 12,
        }}
      >
        {CUT_LABELS[cut.type]}
        {cut.reviewRequired && ' · 검수 필요'}
        {!cut.enabled && cut.type !== 'caption_segment' && ' · 비활성'}
      </div>

      {/* 한 줄 설명 */}
      {cut.reasonText && (
        <div style={{ marginBottom: 16, color: 'var(--text-primary)', fontSize: 14 }}>
          {cut.reasonText}
        </div>
      )}

      {/* 시간 정보 */}
      <Row label="시작" value={formatTime(cut.start)} mono />
      <Row label="종료" value={formatTime(cut.end)} mono />
      <Row label="길이" value={`${cut.duration.toFixed(2)}s`} mono />

      <Divider />

      {/* 분석 정보 */}
      <Row label="감지 사유" value={REASON_LABELS[cut.reason] ?? cut.reason} />
      <Row label="출처" value={SOURCE_LABELS[cut.source] ?? cut.source} />

      <div style={{ margin: '12px 0' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginBottom: 4 }}>
          Confidence
        </div>
        <div
          style={{
            position: 'relative',
            height: 8,
            background: 'var(--bg-active)',
            borderRadius: 4,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: `${confidencePct}%`,
              background: confidenceColor,
            }}
          />
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>
          {confidencePct}%
        </div>
      </div>

      {cut.presetRule && (
        <>
          <Divider />
          <div style={{ marginBottom: 8 }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginBottom: 4 }}>
              적용된 프리셋 규칙
            </div>
            <code
              style={{
                display: 'block',
                padding: '8px 10px',
                background: 'var(--bg-secondary)',
                borderRadius: 4,
                fontSize: 11,
                color: 'var(--text-primary)',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
              }}
            >
              {cut.presetRule}
            </code>
          </div>
        </>
      )}

      {cut.metadata && Object.keys(cut.metadata).length > 0 && (
        <>
          <Divider />
          <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginBottom: 4 }}>
            메타데이터
          </div>
          <pre
            style={{
              fontSize: 11,
              padding: 10,
              background: 'var(--bg-secondary)',
              borderRadius: 4,
              overflowX: 'auto',
              margin: 0,
            }}
          >
            {JSON.stringify(cut.metadata, null, 2)}
          </pre>
        </>
      )}

      {cut.type !== 'caption_segment' && onToggleEnabled && (
        <>
          <Divider />
          <button
            className={`btn ${cut.enabled ? 'btn-secondary' : 'btn-primary'}`}
            onClick={() => onToggleEnabled(cut.id, !cut.enabled)}
            style={{ width: '100%' }}
          >
            {cut.enabled ? '이 컷 비활성화 (되돌리기)' : '이 컷 활성화'}
          </button>
        </>
      )}
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
      <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{label}</span>
      <span
        style={{
          color: 'var(--text-primary)',
          fontFamily: mono ? 'ui-monospace, monospace' : 'inherit',
          fontSize: 12,
        }}
      >
        {value}
      </span>
    </div>
  );
}

function Divider() {
  return <div style={{ height: 1, background: 'var(--bg-active)', margin: '12px 0' }} />;
}
