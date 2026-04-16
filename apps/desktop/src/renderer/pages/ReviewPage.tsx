import React, { useMemo, useState } from 'react';
import { useJobStore, CutDecisionInfo } from '../store/jobStore';

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
  const { currentResults, currentJobId, toggleCutDecision, jobs } = useJobStore();
  const currentJob = jobs.find((j) => j.id === currentJobId);
  const [cutFilter, setCutFilter] = useState<CutFilter>('all');

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
    toggleCutDecision(cutId);
    await window.api.toggleCut(cutId, newEnabled);
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

        {/* Transcript Viewer */}
        <div style={{ marginTop: 24 }}>
          <h2 style={{ fontSize: 16, marginBottom: 12 }}>Transcript</h2>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>
            취소선 = 제거 예정. 클릭하면 되돌릴 수 있습니다.
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
                    title={
                      cut
                        ? `${cut.type} | ${formatTime(cut.start)}~${formatTime(cut.end)} | ${cut.enabled ? '제거됨 (클릭으로 복원)' : '복원됨 (클릭으로 제거)'}`
                        : `${formatTime(word.start)}`
                    }
                    onClick={() => {
                      if (cut) handleToggleCut(cut.id);
                    }}
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
