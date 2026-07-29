import React, { useMemo, useState } from 'react';
import { useJobStore, AssetInfo, SentenceInfo, TimelineClipInfo } from '../store/jobStore';

/**
 * Mode B 분석 결과 뷰어.
 *
 * 보여주는 것:
 *  1. 문장 단위 타임라인 — 각 문장에 어떤 B-roll 클립이 매칭됐는지, confidence, 조정 전략 (trim/speed/repeat/freeze)
 *  2. 가로 timeline 바 — 어떤 시점에 어떤 클립이 재생될지 한눈에
 *  3. 사용된 vs 미사용 B-roll 통계
 *  4. EDL 내보내기 + (앞으로) MP4 렌더링 버튼
 */
export default function ModeBResultPage() {
  const { currentResults, currentJobId, jobs } = useJobStore();
  const currentJob = jobs.find((j) => j.id === currentJobId);
  const [selectedSentenceId, setSelectedSentenceId] = useState<string | null>(null);

  if (currentJob?.status === 'processing') {
    return (
      <>
        <div className="page-header">
          <h1>Mode B 분석 진행 중</h1>
          <p>{currentJob.progress}% — 보이스오버 + B-roll 매칭 중...</p>
        </div>
      </>
    );
  }

  if (!currentResults?.roughCutTimeline || !currentResults.sentenceTimeline || !currentResults.assetIndex) {
    return (
      <>
        <div className="page-header">
          <h1>Mode B 결과</h1>
          <p>아직 분석된 결과가 없습니다. 새 작업에서 Mode B 로 분석을 시작하세요.</p>
        </div>
      </>
    );
  }

  const { roughCutTimeline, sentenceTimeline, assetIndex } = currentResults;
  const videoTrack = roughCutTimeline.tracks.find((t) => t.type === 'video');
  const clips = videoTrack?.clips ?? [];

  // 문장 ID → 매칭된 클립 매핑
  const clipBySentenceId = new Map<string, TimelineClipInfo>();
  for (const clip of clips) clipBySentenceId.set(clip.sentenceId, clip);

  // 에셋 ID → 에셋 정보 매핑
  const assetById = new Map<string, AssetInfo>();
  for (const a of assetIndex.assets) assetById.set(a.id, a);

  // 사용된 B-roll asset id 세트
  const usedAssetIds = new Set<string>();
  for (const c of clips) usedAssetIds.add(c.assetId);
  const unusedAssets = assetIndex.assets.filter((a) => !usedAssetIds.has(a.id));

  const totalDuration = roughCutTimeline.totalDuration;
  const avgConfPct = Math.round(roughCutTimeline.metadata.averageConfidence * 100);

  const handleExportEDL = async () => {
    if (!currentJobId) return;
    const result = await window.api.exportEDL(currentJobId);
    if (result.success) alert(`EDL 저장: ${result.path}`);
    else alert(`EDL 내보내기 실패: ${result.error}`);
  };

  return (
    <>
      <div className="page-header">
        <h1>Mode B 결과 — 보이스오버 + B-roll 자동 매칭</h1>
        <p>
          문장 {sentenceTimeline.sentences.length}개에 B-roll {clips.length}개 매칭 ·
          평균 신뢰도 {avgConfPct}% ·{' '}
          {roughCutTimeline.metadata.reviewRequiredCount > 0 ? (
            <span style={{ color: 'var(--warning)' }}>
              검수 필요 {roughCutTimeline.metadata.reviewRequiredCount}개
            </span>
          ) : (
            <span style={{ color: 'var(--success)' }}>모두 신뢰도 OK</span>
          )}
        </p>
      </div>

      <div className="page-body">
        {/* KPI cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{formatTime(totalDuration)}</div>
            <div className="stat-label">총 길이 (보이스오버 기준)</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{sentenceTimeline.sentences.length}</div>
            <div className="stat-label">문장</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {usedAssetIds.size} / {assetIndex.assets.length}
            </div>
            <div className="stat-label">사용된 / 보유 B-roll</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{avgConfPct}%</div>
            <div className="stat-label">평균 매칭 신뢰도</div>
          </div>
        </div>

        {/* Horizontal timeline visualization */}
        <div style={{ marginTop: 24 }}>
          <h2 style={{ fontSize: 16, marginBottom: 8 }}>타임라인</h2>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 12 }}>
            각 색상 블록 = 한 문장 + 그 문장에 매칭된 B-roll 클립. 클릭해서 상세 보기.
          </p>
          <div
            style={{
              position: 'relative',
              height: 56,
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-sm)',
              overflow: 'hidden',
            }}
          >
            {clips.map((clip) => {
              const sentence = sentenceTimeline.sentences.find((s) => s.id === clip.sentenceId);
              const asset = assetById.get(clip.assetId);
              if (!sentence) return null;
              const left = (clip.timelineStart / totalDuration) * 100;
              const width = ((clip.timelineEnd - clip.timelineStart) / totalDuration) * 100;
              const isSelected = clip.sentenceId === selectedSentenceId;
              const confColor = colorByConfidence(clip.confidence);
              return (
                <div
                  key={clip.id}
                  title={`${sentence.text} → ${asset?.fileName ?? '?'} (${Math.round(clip.confidence * 100)}%)`}
                  onClick={() => setSelectedSentenceId(clip.sentenceId)}
                  style={{
                    position: 'absolute',
                    left: `${left}%`,
                    width: `${Math.max(0.3, width)}%`,
                    top: 4,
                    bottom: 4,
                    background: confColor,
                    border: isSelected ? '2px solid #fff' : '1px solid rgba(0,0,0,0.2)',
                    borderRadius: 3,
                    cursor: 'pointer',
                    boxSizing: 'border-box',
                    overflow: 'hidden',
                    fontSize: 10,
                    color: '#fff',
                    paddingLeft: 4,
                    display: 'flex',
                    alignItems: 'center',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {asset?.fileName ?? '?'}
                </div>
              );
            })}
          </div>
          <div style={{ display: 'flex', gap: 16, marginTop: 8, fontSize: 11, color: 'var(--text-secondary)' }}>
            <LegendDot color="rgba(74, 222, 128, 0.8)" label="신뢰도 ≥ 80%" />
            <LegendDot color="rgba(250, 204, 21, 0.8)" label="60~80%" />
            <LegendDot color="rgba(248, 113, 113, 0.8)" label="< 60% (검수 필요)" />
          </div>
        </div>

        {/* Sentence-level detail list */}
        <div style={{ marginTop: 32, display: 'grid', gridTemplateColumns: '1fr 360px', gap: 16 }}>
          <div>
            <h2 style={{ fontSize: 16, marginBottom: 12 }}>문장별 매칭</h2>
            <div style={{ maxHeight: 480, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {sentenceTimeline.sentences.map((sentence, idx) => {
                const clip = clipBySentenceId.get(sentence.id);
                const asset = clip ? assetById.get(clip.assetId) : null;
                const isSelected = sentence.id === selectedSentenceId;
                const confPct = clip ? Math.round(clip.confidence * 100) : 0;
                const conf = clip?.confidence ?? 0;
                const dotColor = colorByConfidence(conf);
                return (
                  <div
                    key={sentence.id}
                    onClick={() => setSelectedSentenceId(sentence.id)}
                    style={{
                      display: 'flex',
                      gap: 12,
                      padding: '10px 12px',
                      background: isSelected ? 'var(--bg-active)' : 'var(--bg-secondary)',
                      borderRadius: 'var(--radius-sm)',
                      borderLeft: `3px solid ${dotColor}`,
                      cursor: 'pointer',
                    }}
                  >
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', minWidth: 30 }}>
                      #{idx + 1}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, color: 'var(--text-primary)', marginBottom: 4 }}>
                        {sentence.text}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-secondary)', display: 'flex', gap: 12 }}>
                        <span>{formatTime(sentence.start)} – {formatTime(sentence.end)}</span>
                        {clip ? (
                          <>
                            <span>→ {asset?.fileName ?? '?'}</span>
                            <span style={{ color: dotColor }}>{confPct}%</span>
                            {clip.adjustmentStrategy && (
                              <span style={{ color: 'var(--text-muted)' }}>{clip.adjustmentStrategy}</span>
                            )}
                            {clip.playbackSpeed !== 1.0 && (
                              <span style={{ color: 'var(--text-muted)' }}>×{clip.playbackSpeed.toFixed(2)}</span>
                            )}
                          </>
                        ) : (
                          <span style={{ color: 'var(--danger)' }}>매칭 안 됨</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right detail panel */}
          <div>
            <h2 style={{ fontSize: 16, marginBottom: 12 }}>상세</h2>
            <SentenceDetail
              sentence={selectedSentenceId ? sentenceTimeline.sentences.find((s) => s.id === selectedSentenceId) ?? null : null}
              clip={selectedSentenceId ? clipBySentenceId.get(selectedSentenceId) ?? null : null}
              assetById={assetById}
            />

            {/* Unused B-roll */}
            {unusedAssets.length > 0 && (
              <div style={{ marginTop: 16, padding: 12, background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 6 }}>
                  사용되지 않은 B-roll ({unusedAssets.length}개)
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>
                  키워드 매칭 점수가 임계값 미만이라 자동으로 배치되지 않았습니다.
                </div>
                <ul style={{ margin: 0, paddingLeft: 16, fontSize: 11, color: 'var(--text-secondary)' }}>
                  {unusedAssets.slice(0, 6).map((a) => (
                    <li key={a.id}>{a.fileName}</li>
                  ))}
                  {unusedAssets.length > 6 && <li>... 외 {unusedAssets.length - 6}개</li>}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Export buttons */}
        <div style={{ marginTop: 32, display: 'flex', gap: 12 }}>
          <button className="btn btn-secondary" onClick={handleExportEDL}>
            EDL 내보내기
          </button>
        </div>
      </div>
    </>
  );
}

function SentenceDetail({
  sentence,
  clip,
  assetById,
}: {
  sentence: SentenceInfo | null;
  clip: TimelineClipInfo | null;
  assetById: Map<string, AssetInfo>;
}) {
  if (!sentence) {
    return (
      <div
        style={{
          padding: 16,
          background: 'var(--bg-secondary)',
          borderRadius: 'var(--radius-sm)',
          fontSize: 12,
          color: 'var(--text-secondary)',
          lineHeight: 1.6,
        }}
      >
        문장을 선택하면 매칭된 B-roll 클립과 조정 전략, 대체 후보를 볼 수 있습니다.
      </div>
    );
  }

  const asset = clip ? assetById.get(clip.assetId) : null;
  const alts = clip?.alternatives ?? [];

  return (
    <div style={{ padding: 16, background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', fontSize: 12, lineHeight: 1.6 }}>
      <div style={{ fontWeight: 600, marginBottom: 8, color: 'var(--text-primary)', fontSize: 13 }}>
        {sentence.text}
      </div>
      <Row label="구간" value={`${formatTime(sentence.start)} – ${formatTime(sentence.end)}`} />
      <Row label="길이" value={`${sentence.duration.toFixed(2)}s`} />

      <Divider />

      {clip && asset ? (
        <>
          <Row label="매칭 클립" value={asset.fileName} />
          <Row label="신뢰도" value={`${Math.round(clip.confidence * 100)}%`} valueColor={colorByConfidence(clip.confidence)} />
          <Row label="원본 in/out" value={`${clip.sourceIn.toFixed(2)} – ${clip.sourceOut.toFixed(2)}s`} />
          <Row label="재생 속도" value={`×${clip.playbackSpeed.toFixed(2)}`} />
          {clip.adjustmentStrategy && <Row label="조정 전략" value={strategyLabel(clip.adjustmentStrategy)} />}
        </>
      ) : (
        <div style={{ color: 'var(--danger)' }}>이 문장은 매칭된 B-roll 이 없습니다.</div>
      )}

      {alts.length > 0 && (
        <>
          <Divider />
          <div style={{ color: 'var(--text-secondary)', marginBottom: 6 }}>대체 후보</div>
          <ul style={{ margin: 0, paddingLeft: 16, fontSize: 11 }}>
            {alts.slice(0, 5).map((a, i) => {
              const asset2 = assetById.get(a.assetId);
              return (
                <li key={i} style={{ color: 'var(--text-muted)' }}>
                  {asset2?.fileName ?? a.assetId} ({Math.round(a.score * 100)}%)
                </li>
              );
            })}
          </ul>
        </>
      )}
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 2, background: color }} />
      {label}
    </div>
  );
}

function Row({ label, value, valueColor }: { label: string; value: string; valueColor?: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
      <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
      <span style={{ color: valueColor ?? 'var(--text-primary)', fontFamily: valueColor ? 'inherit' : 'ui-monospace, monospace' }}>
        {value}
      </span>
    </div>
  );
}

function Divider() {
  return <div style={{ height: 1, background: 'var(--bg-active)', margin: '10px 0' }} />;
}

function colorByConfidence(c: number): string {
  if (c >= 0.8) return 'rgba(74, 222, 128, 0.85)';
  if (c >= 0.6) return 'rgba(250, 204, 21, 0.85)';
  return 'rgba(248, 113, 113, 0.85)';
}

function strategyLabel(s: string): string {
  return (
    {
      trim: '트리밍 (앞뒤 잘라 길이 맞춤)',
      speed: '속도 조정 (재생 속도로 길이 맞춤)',
      repeat: '반복 재생',
      freeze: 'Freeze frame (마지막 프레임 정지)',
    }[s] ?? s
  );
}

function formatTime(s: number): string {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  const ms = Math.floor((s % 1) * 100);
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}.${String(ms).padStart(2, '0')}`;
}
