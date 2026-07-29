import React, { useState, useEffect } from 'react';
import { useJobStore } from './store/jobStore';
import UploadPage from './pages/UploadPage';
import ReviewPage from './pages/ReviewPage';
import JobsPage from './pages/JobsPage';
import PresetsPage from './pages/PresetsPage';
import LiveAnalysisPage from './pages/LiveAnalysisPage';
import ModeBResultPage from './pages/ModeBResultPage';

type Page = 'upload' | 'live' | 'review' | 'jobs' | 'presets';

export default function App() {
  const [page, setPage] = useState<Page>('upload');
  const { currentJobId, jobs, updateJobProgress, updateJobStatus, setCurrentResults } = useJobStore();

  // IPC 이벤트 리스너 등록
  useEffect(() => {
    const offProgress = window.api.onJobProgress((data) => {
      updateJobProgress(data.jobId, data.progress, data.detail);
    });

    const offCompleted = window.api.onJobCompleted(async (data) => {
      updateJobStatus(data.jobId, 'completed');
      // 파이프라인에서 직접 받은 결과 사용, 없으면 DB에서 로드
      if (data.results) {
        setCurrentResults(data.results as Parameters<typeof setCurrentResults>[0]);
      } else {
        const { results } = await window.api.getJob(data.jobId);
        if (results) {
          setCurrentResults(results as Parameters<typeof setCurrentResults>[0]);
        }
      }
      // 분석 완료 후에도 live 페이지에 머물러 사용자가 결과를 검토할 수 있게 하고,
      // 사이드바의 "검수 / 편집" 버튼으로 ReviewPage 로 넘어가도록 한다.
    });

    const offError = window.api.onJobError((data) => {
      updateJobStatus(data.jobId, 'failed', data.error);
    });

    return () => {
      offProgress();
      offCompleted();
      offError();
    };
  }, [updateJobProgress, updateJobStatus, setCurrentResults]);

  const currentJob = jobs.find((j) => j.id === currentJobId);
  // Mode 선택: Job 의 editMode 가 'mode-b' 면 검수 페이지를 Mode B 뷰어로 분기.
  // (results 에 roughCutTimeline 이 있으면 Mode B 결과)
  const isModeB =
    (currentJob as { editMode?: string } | undefined)?.editMode === 'mode-b';

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">Cutback</div>
          <div className="sidebar-subtitle">AI 편집 어시스턴트</div>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${page === 'upload' ? 'active' : ''}`}
            onClick={() => setPage('upload')}
          >
            + 새 작업
          </button>
          <button
            className={`nav-item ${page === 'live' ? 'active' : ''}`}
            onClick={() => setPage('live')}
            disabled={!currentJobId}
          >
            라이브 분석
          </button>
          <button
            className={`nav-item ${page === 'review' ? 'active' : ''}`}
            onClick={() => setPage('review')}
            disabled={!currentJobId}
          >
            검수 / 편집
          </button>
          <button
            className={`nav-item ${page === 'jobs' ? 'active' : ''}`}
            onClick={() => setPage('jobs')}
          >
            작업 목록 ({jobs.length})
          </button>
          <button
            className={`nav-item ${page === 'presets' ? 'active' : ''}`}
            onClick={() => setPage('presets')}
          >
            프리셋 관리
          </button>
        </nav>

        {/* 현재 작업 상태 */}
        {currentJob && currentJob.status === 'processing' && (
          <div style={{ padding: '16px', borderTop: '1px solid var(--border)' }}>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>
              처리 중...
            </div>
            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{ width: `${currentJob.progress}%` }}
              />
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
              {currentJob.progress}%
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {page === 'upload' && (
          <UploadPage
            onJobStarted={() => {
              // 분석 시작 즉시 라이브 타임라인으로 전환
              setPage('live');
            }}
          />
        )}
        {page === 'live' && <LiveAnalysisPage onAnalysisComplete={() => setPage('review')} />}
        {page === 'review' && (isModeB ? <ModeBResultPage /> : <ReviewPage />)}
        {page === 'jobs' && <JobsPage onSelectJob={() => setPage('review')} />}
        {page === 'presets' && <PresetsPage />}
      </main>
    </div>
  );
}
