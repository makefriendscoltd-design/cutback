import React, { useEffect } from 'react';
import { useJobStore } from '../store/jobStore';

interface JobsPageProps {
  onSelectJob: () => void;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleString('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  pending: { label: '대기', color: 'var(--text-muted)' },
  processing: { label: '처리 중', color: 'var(--warning)' },
  completed: { label: '완료', color: 'var(--success)' },
  failed: { label: '실패', color: 'var(--danger)' },
  cancelled: { label: '취소됨', color: 'var(--text-muted)' },
};

export default function JobsPage({ onSelectJob }: JobsPageProps) {
  const { jobs, setJobs, setCurrentJob, setCurrentResults } = useJobStore();

  // 페이지 진입 시 작업 목록 새로고침
  useEffect(() => {
    window.api.listJobs().then((jobList) => {
      setJobs(
        (jobList as Array<{
          id: string;
          videoPath: string;
          presetId: string;
          status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
          progress: number;
          createdAt: string;
          error?: string;
        }>).map((j) => ({
          id: j.id,
          videoPath: j.videoPath,
          presetId: j.presetId,
          status: j.status,
          progress: j.progress,
          createdAt: j.createdAt,
          error: j.error,
        }))
      );
    });
  }, [setJobs]);

  const handleSelectJob = async (jobId: string) => {
    setCurrentJob(jobId);

    const { results } = await window.api.getJob(jobId);
    if (results) {
      setCurrentResults(results as Parameters<typeof setCurrentResults>[0]);
    }

    onSelectJob();
  };

  return (
    <>
      <div className="page-header">
        <h1>작업 목록</h1>
        <p>이전 작업 결과를 확인하고 이어서 편집하세요</p>
      </div>

      <div className="page-body">
        {jobs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>
            <div style={{ fontSize: 48, marginBottom: 16, opacity: 0.3 }}>
              -
            </div>
            <div>아직 작업이 없습니다</div>
            <div style={{ fontSize: 12, marginTop: 4 }}>
              "새 작업"에서 영상을 업로드하세요
            </div>
          </div>
        ) : (
          <div className="job-list">
            {jobs.map((job) => {
              const statusInfo = STATUS_LABELS[job.status] || STATUS_LABELS.pending;
              const fileName = job.videoPath.split('\\').pop() || job.videoPath.split('/').pop() || '(알 수 없음)';

              return (
                <div
                  key={job.id}
                  className="job-item"
                  onClick={() => handleSelectJob(job.id)}
                >
                  <div className={`job-status ${job.status}`} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 500, fontSize: 13 }}>{fileName}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                      {job.presetId} | {formatDate(job.createdAt)}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 12, color: statusInfo.color, fontWeight: 500 }}>
                      {statusInfo.label}
                    </div>
                    {job.status === 'processing' && (
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        {job.progress}%
                      </div>
                    )}
                    {job.error && (
                      <div style={{ fontSize: 11, color: 'var(--danger)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {job.error}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}
