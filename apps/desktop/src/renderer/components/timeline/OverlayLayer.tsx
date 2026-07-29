import React from 'react';

/**
 * timeline overlay 색상 팔레트.
 * 사용자가 한눈에 cut 종류를 구분할 수 있어야 하므로 값을 자주 바꾸지 말 것.
 */
export const CUT_COLORS = {
  silence: 'rgba(120, 120, 120, 0.55)',
  filler_word: 'rgba(255, 159, 64, 0.55)',
  retake: 'rgba(255, 99, 132, 0.55)',
  caption_segment: 'rgba(91, 141, 239, 0.30)',
} as const;

export const CUT_COLORS_HOVER = {
  silence: 'rgba(160, 160, 160, 0.75)',
  filler_word: 'rgba(255, 159, 64, 0.85)',
  retake: 'rgba(255, 99, 132, 0.85)',
  caption_segment: 'rgba(91, 141, 239, 0.55)',
} as const;

export const CUT_LABELS = {
  silence: '무음',
  filler_word: '말버릇',
  retake: '재시도',
  caption_segment: '자막',
} as const;

interface CutSegment {
  id: string;
  type: keyof typeof CUT_COLORS;
  start: number;
  end: number;
  enabled: boolean;
  reviewRequired?: boolean;
}

interface OverlayLayerProps {
  cuts: CutSegment[];
  duration: number;
  height: number;
  selectedCutId?: string;
  onCutClick?: (cutId: string) => void;
}

/**
 * 파형 위에 cut 종류별로 색상 박스를 그린다.
 * 클릭하면 onCutClick 호출 → 우측 DetailPanel 에 정보 표시.
 *
 * 자막 (caption_segment) 은 enabled=false 로 들어와도 표시는 한다 (segmentation 가이드).
 */
export default function OverlayLayer({
  cuts,
  duration,
  height,
  selectedCutId,
  onCutClick,
}: OverlayLayerProps) {
  if (duration <= 0) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height,
        pointerEvents: 'none',
      }}
    >
      {cuts.map((cut) => {
        const left = (cut.start / duration) * 100;
        const width = ((cut.end - cut.start) / duration) * 100;
        const isCaption = cut.type === 'caption_segment';
        const isSelected = cut.id === selectedCutId;
        const baseColor = CUT_COLORS[cut.type];
        const hoverColor = CUT_COLORS_HOVER[cut.type];
        // 자막 세그먼트는 위쪽 띠로, 컷 종류는 전체 높이로
        const top = isCaption ? height - 16 : 0;
        const segHeight = isCaption ? 16 : height;
        const dimmed = !cut.enabled && !isCaption;

        return (
          <div
            key={cut.id}
            onClick={() => onCutClick?.(cut.id)}
            title={`${CUT_LABELS[cut.type]} ${cut.start.toFixed(2)}s - ${cut.end.toFixed(2)}s`}
            style={{
              position: 'absolute',
              left: `${left}%`,
              width: `${Math.max(0.15, width)}%`,
              top,
              height: segHeight,
              background: isSelected ? hoverColor : baseColor,
              opacity: dimmed ? 0.35 : 1,
              border: isSelected ? '2px solid #fff' : 'none',
              boxSizing: 'border-box',
              borderRadius: 2,
              cursor: 'pointer',
              pointerEvents: 'auto',
              transition: 'background 120ms ease',
            }}
            onMouseEnter={(e) => {
              if (!isSelected) {
                (e.currentTarget as HTMLDivElement).style.background = hoverColor;
              }
            }}
            onMouseLeave={(e) => {
              if (!isSelected) {
                (e.currentTarget as HTMLDivElement).style.background = baseColor;
              }
            }}
          />
        );
      })}
    </div>
  );
}

interface LegendProps {
  counts?: Partial<Record<keyof typeof CUT_COLORS, number>>;
}

/** Cut 종류별 범례 + 카운트 */
export function OverlayLegend({ counts }: LegendProps) {
  const types: (keyof typeof CUT_COLORS)[] = [
    'silence',
    'filler_word',
    'retake',
    'caption_segment',
  ];

  return (
    <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', fontSize: 12 }}>
      {types.map((t) => (
        <div key={t} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span
            style={{
              display: 'inline-block',
              width: 12,
              height: 12,
              background: CUT_COLORS[t],
              borderRadius: 2,
            }}
          />
          <span style={{ color: 'var(--text-secondary)' }}>
            {CUT_LABELS[t]}
            {counts && typeof counts[t] === 'number' ? ` (${counts[t]})` : ''}
          </span>
        </div>
      ))}
    </div>
  );
}
