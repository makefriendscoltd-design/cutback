import React, { useEffect, useMemo, useState } from 'react';
import { useJobStore, CutDecisionInfo } from '../store/jobStore';
import BeforeAfterPreview from '../components/BeforeAfterPreview';

/** 시간 포맷 (초 → MM:SS) */
function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}

/** 자연스러움 점수 라벨 */
function getScoreLabel(score: number): { label: string; color: string } {
  if (score >= 0.9) return { label: '매우 자연스러움', color: 'var(--success)' };
  if (score >= 0.75) return { label: '자연스러움', color: 'var(--info)' };
  if (score >= 0.6) return { label: '보통', color: 'var(--warning)' };
  return { label: '과편집 주의', color: 'var(--danger)' };
}

type CutFilter = 'all' | 'silence' | 'filler_word' | 'retake';

export default function ReviewPage() {
  const {
    currentResults,
    currentJobId,
    toggleCutDecision,
    addManualCut,
    undoCutChange,
    redoCutChange,
    cutHistory,
    jobs,
  } = useJobStore();
  const currentJob = jobs.find((j) => j.id === currentJobId);
  const [cutFilter, setCutFilter] = useState<CutFilter>('all');
  /** Descript 스타일 word 선택 (단일 또는 shift-range) */
  const [selectedWordIndices, setSelectedWordIndices] = useState<Set<number>>(new Set());
  const [anchorIndex, setAnchorIndex] = useState<number | null>(null);

  const canUndo = cutHistory.past.length > 0;
  const canRedo = cutHistory.future.length > 0;

  // 작업이 아직 진행 중인 경우
  if (currentJob?.status === 'processing') {
    return (
      <>
        <div className="page-header">
          <h1>분석 진행 중</h1>
          <p>영상을 분석하고 있습니다. 잠시 기다려주세요.</p>
        </div>
        <div className="page-body">
          <div style={{ maxWidth: 400, margin: '60px auto', textAlign: 'center' }}>
            <div className="progress-bar-container" style={{ height: 12 }}>
              <div
                className="progress-bar-fill"
                style={{ width: `${currentJob.progress}%` }}
              />
            </div>
            <div style={{ marginTop: 12, fontSize: 18, fontWeight: 600 }}>
              {currentJob.progress}%
            </div>
          </div>
        </div>
      </>
    );
  }

  if (!currentResults) {
    return (
      <>
        <div className="page-header">
          <h1>검수 / 편집</h1>
          <p>아직 분석된 결과가 없습니다. 새 작업을 먼저 시작하세요.</p>
        </div>
      </>
    );
  }

  // Mode B 결과는 ModeBResultPage 가 처리. 여기 도달했는데 Mode A 결과가 없으면 안내.
  if (!currentResults.transcript || !currentResults.cutDecisions || !currentResults.statistics) {
    return (
      <>
        <div className="page-header">
          <h1>검수 / 편집</h1>
          <p>이 작업은 Mode A 결과가 없습니다. (Mode B 작업이면 자동으로 Mode B 뷰어로 갑니다.)</p>
        </div>
      </>
    );
  }

  const { transcript, cutDecisions, statistics } = currentResults;
  const scoreInfo = getScoreLabel(statistics.naturalness_score);

  // 필터링된 컷 리스트
  const filteredCuts = cutFilter === 'all'
    ? cutDecisions
    : cutDecisions.filter((c) => c.type === cutFilter);

  // 단어별 컷 상태 매핑
  const wordCutMap = useMemo(() => {
    const map = new Map<number, CutDecisionInfo>();
    for (const cut of cutDecisions) {
      for (let i = 0; i < transcript.words.length; i++) {
        const word = transcript.words[i];
        if (word.start >= cut.start && word.end <= cut.end) {
          map.set(i, cut);
        }
      }
    }
    return map;
  }, [cutDecisions, transcript.words]);

  const handleToggleCut = async (cutId: string) => {
    const cut = cutDecisions.find((c) => c.id === cutId);
    if (!cut) return;
    const newEnabled = !cut.enabled;
    // store 갱신 → LiveAnalysisPage 도 자동으로 반영 (같은 객체 참조)
    toggleCutDecision(cutId, newEnabled);
    await window.api.toggleCut(cutId, newEnabled);

    // Calibration: 사용자가 자동 감지된 filler 를 복원했다면 (enabled=true → false) 그 단어를 학습
    if (cut.type === 'filler_word' && cut.enabled && !newEnabled && currentJob?.presetId) {
      const fillerText = cut.metadata?.filler_text;
      if (typeof fillerText === 'string') {
        // background — 실패해도 UX 영향 없음
        void window.api.recordCalibration(currentJob.presetId, {
          restoredFillerWords: [fillerText],
        });
      }
    }
  };

  /**
   * 선택된 단어들에 대해 manual cut 수행 (또는 이미 cut 인 경우 토글).
   * Descript 스타일: 사용자가 단어를 선택하고 Delete 키를 누르면 그 구간이 비활성화되어 시각적으로 회색이 됨.
   */
  const handleDeleteSelectedWords = () => {
    if (selectedWordIndices.size === 0) return;
    const indices = Array.from(selectedWordIndices).sort((a, b) => a - b);
    const firstWord = transcript.words[indices[0]];
    const lastWord = transcript.words[indices[indices.length - 1]];
    if (!firstWord || !lastWord) return;

    // 선택 영역 안의 모든 단어가 같은 cut 에 속하면 그 cut 을 토글
    const cutsAtSelection = indices
      .map((i) => wordCutMap.get(i))
      .filter((c): c is CutDecisionInfo => Boolean(c));
    const allSameCut =
      cutsAtSelection.length === indices.length &&
      cutsAtSelection.every((c) => c.id === cutsAtSelection[0].id);

    if (allSameCut && cutsAtSelection.length > 0) {
      // 토글
      void handleToggleCut(cutsAtSelection[0].id);
    } else {
      // 새 manual cut
      const text = indices.map((i) => transcript.words[i].text).join(' ');
      const durationMs = (lastWord.end - firstWord.start) * 1000;
      addManualCut({
        start: firstWord.start,
        end: lastWord.end,
        text,
      });
      // Calibration: 사용자가 직접 추가한 cut 의 길이 기록
      if (currentJob?.presetId) {
        void window.api.recordCalibration(currentJob.presetId, {
          manualCutDurationsMs: [durationMs],
        });
      }
    }
    setSelectedWordIndices(new Set());
    setAnchorIndex(null);
  };

  // 키보드 단축키: Delete / Backspace 로 선택 단어 cut, Cmd/Ctrl+Z 로 undo
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // input 필드에 포커스 있으면 무시
      const target = e.target as HTMLElement | null;
      if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
        return;
      }
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedWordIndices.size > 0) {
        e.preventDefault();
        handleDeleteSelectedWords();
      } else if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        if (canUndo) undoCutChange();
      } else if (
        ((e.metaKey || e.ctrlKey) && e.key === 'z' && e.shiftKey) ||
        ((e.metaKey || e.ctrlKey) && e.key === 'y')
      ) {
        e.preventDefault();
        if (canRedo) redoCutChange();
      } else if (e.key === 'Escape') {
        setSelectedWordIndices(new Set());
        setAnchorIndex(null);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  });

  const handleWordClick = (index: number, e: React.MouseEvent) => {
    if (e.shiftKey && anchorIndex !== null) {
      // range select
      const [from, to] =
        anchorIndex < index ? [anchorIndex, index] : [index, anchorIndex];
      const next = new Set<number>();
      for (let i = from; i <= to; i++) next.add(i);
      setSelectedWordIndices(next);
    } else if (e.metaKey || e.ctrlKey) {
      // multi-select (toggle)
      const next = new Set(selectedWordIndices);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      setSelectedWordIndices(next);
      setAnchorIndex(index);
    } else {
      // single click: cut 위에 있으면 토글, 아니면 단어만 선택
      const cut = wordCutMap.get(index);
      if (cut) {
        void handleToggleCut(cut.id);
        setSelectedWordIndices(new Set());
        setAnchorIndex(null);
      } else {
        setSelectedWordIndices(new Set([index]));
        setAnchorIndex(index);
      }
    }
  };

  const handleExportEDL = async () => {
    if (!currentJobId) return;
    const result = await window.api.exportEDL(currentJobId);
    if (result.success) {
      alert(`EDL 저장 완료: ${result.path}`);
    }
  };

  const handleExportSRT = async () => {
    if (!currentJobId) return;
    const result = await window.api.exportSRT(currentJobId);
    if (result.success) {
      alert(`SRT 저장 완료: ${result.path}`);
    }
  };

  const handleExportCapCut = async () => {
    if (!currentJobId) return;
    const result = await window.api.exportCapCut(currentJobId);
    if (result.success) {
      alert(result.message || 'CapCut 프로젝트가 생성되었습니다. CapCut을 열면 프로젝트 목록에 나타납니다.');
    } else {
      alert(`CapCut 내보내기 실패: ${result.error}`);
    }
  };

  const [isRendering, setIsRendering] = useState(false);

  const handleRenderVideo = async () => {
    if (!currentJobId || isRendering) return;
    setIsRendering(true);
    try {
      const result = await window.api.renderVideo(currentJobId);
      if (result.success) {
        alert(`영상 렌더링 완료!\n${result.path}`);
      } else if (result.error !== 'Cancelled') {
        alert(`렌더링 실패: ${result.error}`);
      }
    } finally {
      setIsRendering(false);
    }
  };

  const savedTime = statistics.original_duration - statistics.edited_duration;
  const savedPercent = statistics.original_duration > 0
    ? ((savedTime / statistics.original_duration) * 100).toFixed(1)
    : '0';

  return (
    <>
      <div className="page-header">
        <h1>검수 / 편집</h1>
        <p>
          분석 결과를 확인하고 최종 편집을 조정하세요
          {savedTime > 0 && (
            <span style={{ marginLeft: 12, color: 'var(--success)', fontWeight: 500 }}>
              {formatTime(savedTime)} 절약 ({savedPercent}%)
            </span>
          )}
        </p>
      </div>

      <div className="page-body">
        {/* Statistics */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{formatTime(statistics.original_duration)}</div>
            <div className="stat-label">원본 길이</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{formatTime(statistics.edited_duration)}</div>
            <div className="stat-label">편집 후 길이</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{statistics.silence_removed}</div>
            <div className="stat-label">무음 제거</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{statistics.fillers_removed}</div>
            <div className="stat-label">말버릇 제거</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{statistics.retakes_removed}</div>
            <div className="stat-label">리테이크 제거</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: scoreInfo.color }}>
              {(statistics.naturalness_score * 100).toFixed(0)}%
            </div>
            <div className="stat-label">{scoreInfo.label}</div>
          </div>
        </div>

        {/* Before / After Preview */}
        {currentJob?.videoPath && (
          <div style={{ marginTop: 24 }}>
            <BeforeAfterPreview
              videoPath={currentJob.videoPath}
              cuts={cutDecisions.map((c) => ({
                start: c.start,
                end: c.end,
                enabled: c.enabled,
                type: c.type,
              }))}
              originalDuration={statistics.original_duration}
              editedDuration={statistics.edited_duration}
              kpi={{
                silenceRemoved: statistics.silence_removed,
                fillersRemoved: statistics.fillers_removed,
                retakesRemoved: statistics.retakes_removed,
              }}
            />
          </div>
        )}

        {/* Transcript Viewer */}
        <div style={{ marginTop: 24 }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 12,
            }}
          >
            <h2 style={{ fontSize: 16, margin: 0 }}>Transcript</h2>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              {selectedWordIndices.size > 0 && (
                <span style={{ fontSize: 12, color: 'var(--text-secondary)', marginRight: 8 }}>
                  {selectedWordIndices.size}개 단어 선택됨
                </span>
              )}
              <button
                className="btn btn-secondary btn-sm"
                onClick={handleDeleteSelectedWords}
                disabled={selectedWordIndices.size === 0}
                title="선택한 단어를 컷으로 추가 (Delete)"
              >
                선택 컷 (Delete)
              </button>
              <button
                className="btn btn-secondary btn-sm"
                onClick={undoCutChange}
                disabled={!canUndo}
                title="실행 취소 (Ctrl+Z)"
              >
                ↶ Undo {canUndo ? `(${cutHistory.past.length})` : ''}
              </button>
              <button
                className="btn btn-secondary btn-sm"
                onClick={redoCutChange}
                disabled={!canRedo}
                title="다시 실행 (Ctrl+Shift+Z)"
              >
                ↷ Redo
              </button>
            </div>
          </div>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>
            클릭으로 선택, Shift+클릭으로 범위, Delete 로 컷 추가. 취소선이 그어진 단어는 제거 예정.
            <span style={{ marginLeft: 12, padding: '2px 6px', background: 'rgba(239,68,68,0.15)', borderRadius: 2, fontSize: 11 }}>무음</span>
            <span style={{ marginLeft: 4, padding: '2px 6px', background: 'rgba(245,158,11,0.15)', borderRadius: 2, fontSize: 11 }}>말버릇</span>
            <span style={{ marginLeft: 4, padding: '2px 6px', background: 'rgba(59,130,246,0.15)', borderRadius: 2, fontSize: 11 }}>리테이크</span>
          </p>

          <div className="transcript-container">
            {transcript.words.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 20 }}>
                STT 결과가 없습니다 (Python 서비스 미연결 시 빈 결과)
              </div>
            ) : (
              transcript.words.map((word, index) => {
                const cut = wordCutMap.get(index);
                const isSelected = selectedWordIndices.has(index);
                let className = 'transcript-word';

                if (cut) {
                  if (!cut.enabled) {
                    className += ' cut-disabled';
                  } else if (cut.type === 'silence') {
                    className += ' cut-silence';
                  } else if (cut.type === 'filler_word') {
                    className += ' cut-filler';
                  } else if (cut.type === 'retake') {
                    className += ' cut-retake';
                  }
                }

                return (
                  <span
                    key={index}
                    className={className}
                    style={
                      isSelected
                        ? {
                            background: 'rgba(91, 141, 239, 0.35)',
                            outline: '1px solid var(--accent-primary)',
                            borderRadius: 2,
                          }
                        : undefined
                    }
                    title={
                      cut
                        ? `${cut.reasonText ?? cut.type} | ${formatTime(cut.start)}~${formatTime(cut.end)} | ${cut.enabled ? '제거됨 (클릭으로 복원)' : '복원됨 (클릭으로 제거)'}`
                        : `${formatTime(word.start)} (클릭 후 Delete 로 컷 추가)`
                    }
                    onClick={(e) => handleWordClick(index, e)}
                  >
                    {word.text}{' '}
                  </span>
                );
              })
            )}
          </div>
        </div>

        {/* Cut Decisions List */}
        <div style={{ marginTop: 24 }}>
          <h2 style={{ fontSize: 16, marginBottom: 12 }}>편집 포인트 ({cutDecisions.length}개)</h2>

          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            {([
              ['all', `전체 (${cutDecisions.length})`],
              ['silence', `무음 (${cutDecisions.filter((c) => c.type === 'silence').length})`],
              ['filler_word', `말버릇 (${cutDecisions.filter((c) => c.type === 'filler_word').length})`],
              ['retake', `리테이크 (${cutDecisions.filter((c) => c.type === 'retake').length})`],
            ] as [CutFilter, string][]).map(([filter, label]) => (
              <button
                key={filter}
                className={`btn btn-sm ${cutFilter === filter ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setCutFilter(filter)}
              >
                {label}
              </button>
            ))}
          </div>

          <div style={{ maxHeight: 300, overflowY: 'auto' }}>
            {filteredCuts.slice(0, 100).map((cut) => (
              <div
                key={cut.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: '8px 12px',
                  background: cut.enabled ? 'var(--bg-secondary)' : 'var(--bg-primary)',
                  borderRadius: 'var(--radius-sm)',
                  marginBottom: 4,
                  opacity: cut.enabled ? 1 : 0.5,
                  cursor: 'pointer',
                }}
                onClick={() => handleToggleCut(cut.id)}
              >
                <span
                  style={{
                    fontSize: 11,
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-sm)',
                    background:
                      cut.type === 'silence'
                        ? 'rgba(239,68,68,0.15)'
                        : cut.type === 'filler_word'
                          ? 'rgba(245,158,11,0.15)'
                          : 'rgba(59,130,246,0.15)',
                    color:
                      cut.type === 'silence'
                        ? 'var(--danger)'
                        : cut.type === 'filler_word'
                          ? 'var(--warning)'
                          : 'var(--info)',
                    minWidth: 60,
                    textAlign: 'center',
                  }}
                >
                  {cut.type === 'silence' ? '무음' : cut.type === 'filler_word' ? '말버릇' : '리테이크'}
                </span>
                <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                  {formatTime(cut.start)} ~ {formatTime(cut.end)}
                </span>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  {cut.duration.toFixed(1)}s
                </span>
                {cut.metadata?.filler_text != null && (
                  <span style={{ fontSize: 12, color: 'var(--warning)' }}>
                    "{String(cut.metadata.filler_text)}"
                  </span>
                )}
                <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-muted)' }}>
                  {cut.enabled ? '제거' : '복원됨'}
                </span>
              </div>
            ))}
            {filteredCuts.length > 100 && (
              <div style={{ padding: 12, textAlign: 'center', color: 'var(--text-muted)', fontSize: 12 }}>
                + {filteredCuts.length - 100}개 더...
              </div>
            )}
            {filteredCuts.length === 0 && (
              <div style={{ padding: 20, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                해당 타입의 편집 포인트가 없습니다
              </div>
            )}
          </div>
        </div>

        {/* Export */}
        <div style={{ marginTop: 32, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary"
            onClick={handleRenderVideo}
            disabled={isRendering}
            style={{ fontWeight: 600 }}
          >
            {isRendering ? '렌더링 중...' : '영상 렌더링 (MP4)'}
          </button>
          <button className="btn btn-secondary" onClick={handleExportEDL}>
            EDL 내보내기
          </button>
          <button className="btn btn-secondary" onClick={handleExportSRT}>
            SRT 자막 내보내기
          </button>
          <button className="btn btn-secondary" onClick={handleExportCapCut}>
            CapCut으로 보내기
          </button>
        </div>
      </div>
    </>
  );
}
