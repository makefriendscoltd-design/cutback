import React, { useEffect, useRef } from 'react';

interface WaveformDisplayProps {
  /** 0.0~1.0 normalized peaks (audio-engine 의 extractWaveformPeaks 출력) */
  peaks: number[];
  /** 총 길이 (초) — 진행 표시 가이드용 */
  duration: number;
  /** 현재 재생 위치 (초). undefined 면 표시 안 함. */
  currentTime?: number;
  /** 분석 진행률 0~100. peaks 가 아직 비어있을 때 progress bar 표시 */
  analysisProgress?: number;
  height?: number;
  color?: string;
  backgroundColor?: string;
}

/**
 * Canvas 기반 오디오 파형 디스플레이.
 * peaks 데이터가 들어오기 전에는 progress bar 만 보이고,
 * 들어오는 즉시 파형으로 전환된다.
 */
export default function WaveformDisplay({
  peaks,
  duration,
  currentTime,
  analysisProgress,
  height = 120,
  color = '#5b8def',
  backgroundColor = '#1a1d23',
}: WaveformDisplayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const dpr = window.devicePixelRatio || 1;
    const cssWidth = container.clientWidth;
    const cssHeight = height;

    canvas.width = cssWidth * dpr;
    canvas.height = cssHeight * dpr;
    canvas.style.width = `${cssWidth}px`;
    canvas.style.height = `${cssHeight}px`;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    // 배경
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, cssWidth, cssHeight);

    if (peaks.length === 0) {
      // peaks 아직 없음 → 분석 진행 상태만 표시
      if (typeof analysisProgress === 'number') {
        const barHeight = 4;
        const y = cssHeight / 2 - barHeight / 2;
        ctx.fillStyle = '#2a2d33';
        ctx.fillRect(0, y, cssWidth, barHeight);
        ctx.fillStyle = color;
        ctx.fillRect(0, y, (cssWidth * analysisProgress) / 100, barHeight);
      }
      return;
    }

    // 파형 그리기 — 각 bucket 을 위/아래 대칭 막대로
    const barWidth = cssWidth / peaks.length;
    const center = cssHeight / 2;
    ctx.fillStyle = color;

    for (let i = 0; i < peaks.length; i++) {
      const peak = peaks[i];
      const barHeight = peak * (cssHeight - 4);
      const x = i * barWidth;
      ctx.fillRect(x, center - barHeight / 2, Math.max(1, barWidth - 0.5), barHeight);
    }

    // 재생 위치 (있으면)
    if (typeof currentTime === 'number' && duration > 0) {
      const x = (currentTime / duration) * cssWidth;
      ctx.fillStyle = '#fff';
      ctx.fillRect(x - 1, 0, 2, cssHeight);
    }
  }, [peaks, duration, currentTime, analysisProgress, height, color, backgroundColor]);

  return (
    <div ref={containerRef} style={{ width: '100%', position: 'relative' }}>
      <canvas ref={canvasRef} style={{ display: 'block', width: '100%' }} />
    </div>
  );
}
