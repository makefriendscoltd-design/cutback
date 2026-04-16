import React, { useState, useEffect } from 'react';
import { useJobStore } from './store/jobStore';
import UploadPage from './pages/UploadPage';
import ReviewPage from './pages/ReviewPage';
import JobsPage from './pages/JobsPage';
import PresetsPage from './pages/PresetsPage';

type Page = 'upload' | 'review' | 'jobs' | 'presets';

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
      setPage('review');
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
        {page === 'upload' && <UploadPage onJobStarted={() => { /* stay on upload, progress shows inline */ }} />}
        {page === 'review' && <ReviewPage />}
        {page === 'jobs' && <JobsPage onSelectJob={() => setPage('review')} />}
        {page === 'presets' && <PresetsPage />}
      </main>
    </div>
  );
}
