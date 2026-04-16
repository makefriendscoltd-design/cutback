import React, { useState, useCallback } from 'react';
import { useJobStore } from '../store/jobStore';

interface UploadPageProps {
  onJobStarted: (jobId: string) => void;
}

const PRESETS = [
  {
    id: 'ad-short-form',
    name: '광고형 숏폼',
    desc: '빠른 템포, 후킹 강조, 간결한 자막. 15~60초 광고에 최적화.',
    ratio: '9:16' as const,
    tags: ['9:16', 'aggressive', '170 WPM', '점프컷'],
  },
  {
    id: 'info-talking-head',
    name: '정보형 토킹헤드',
    desc: '이해도 우선, 자연스러운 호흡 유지. 3~10분 설명 영상.',
    ratio: '16:9' as const,
    tags: ['16:9', 'balanced', '140 WPM', '자연스러움'],
  },
  {
    id: 'vlog-style',
    name: '브이로그형',
    desc: '친근하고 자연스러운 편집. 호흡 충분히 보존.',
    ratio: '16:9' as const,
    tags: ['16:9', 'conservative', '130 WPM', '감성적'],
  },
];

export default function UploadPage({ onJobStarted }: UploadPageProps) {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [selectedPreset, setSelectedPreset] = useState<string>('ad-short-form');
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { addJob, progressDetail, currentJobId, jobs } = useJobStore();
  const currentJob = jobs.find((j) => j.id === currentJobId);
  const isProcessing = currentJob?.status === 'processing';

  const handleFileSelect = useCallback(async () => {
    const filePath = await window.api.openVideoDialog();
    if (filePath) {
      setSelectedFile(filePath);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file.path);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleStartJob = useCallback(async () => {
    if (!selectedFile || !selectedPreset) return;

    setIsSubmitting(true);
    try {
      const result = await window.api.createJob({
        videoPath: selectedFile,
        presetId: selectedPreset,
      });

      if (result.success && result.job) {
        const job = result.job as {
          id: string;
          videoPath: string;
          presetId: string;
          status: 'pending';
          progress: number;
          createdAt: string;
        };
        addJob({
          id: job.id,
          videoPath: job.videoPath,
          presetId: job.presetId,
          status: 'processing',
          progress: 0,
          createdAt: new Date().toISOString(),
        });
        onJobStarted(job.id);
      }
    } catch (err) {
      console.error('Failed to create job:', err);
    } finally {
      setIsSubmitting(false);
    }
  }, [selectedFile, selectedPreset, addJob, onJobStarted]);

  return (
    <>
      <div className="page-header">
        <h1>새 작업</h1>
        <p>영상 파일을 업로드하고 프리셋을 선택하세요</p>
      </div>

      <div className="page-body">
        {/* File Drop Zone */}
        <div
          className={`drop-zone ${isDragging ? 'dragging' : ''}`}
          onClick={handleFileSelect}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <div className="drop-zone-icon">
            {selectedFile ? '✓' : '↑'}
          </div>
          <div className="drop-zone-text">
            {selectedFile
              ? selectedFile.split('\\').pop() || selectedFile.split('/').pop()
              : '영상 파일을 여기에 드래그하거나 클릭하세요'}
          </div>
          <div className="drop-zone-hint">
            MP4, MOV, AVI, MKV, WebM 지원
          </div>
        </div>

        {/* Preset Selection */}
        <div style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: 16, marginBottom: 4 }}>편집 프리셋 선택</h2>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 12 }}>
            영상 타입에 맞는 프리셋을 선택하면 최적의 편집 설정이 적용됩니다
          </p>

          <div className="preset-grid">
            {PRESETS.map((preset) => (
              <div
                key={preset.id}
                className={`preset-card ${selectedPreset === preset.id ? 'selected' : ''}`}
                onClick={() => setSelectedPreset(preset.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div className="preset-card-name" style={{ flex: 1 }}>{preset.name}</div>
                  <span
                    style={{
                      fontSize: 10,
                      padding: '2px 8px',
                      background: preset.ratio === '9:16' ? 'var(--accent-primary)' : 'var(--bg-active)',
                      color: preset.ratio === '9:16' ? '#fff' : 'var(--text-secondary)',
                      borderRadius: 'var(--radius-sm)',
                      fontWeight: 600,
                    }}
                  >
                    {preset.ratio}
                  </span>
                </div>
                <div className="preset-card-desc">{preset.desc}</div>
                <div style={{ display: 'flex', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
                  {preset.tags.filter(t => t !== preset.ratio).map((tag) => (
                    <span
                      key={tag}
                      style={{
                        fontSize: 10,
                        padding: '2px 8px',
                        background: 'var(--bg-active)',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Start Button */}
        <div style={{ marginTop: 32, display: 'flex', gap: 12 }}>
          <button
            className="btn btn-primary"
            disabled={!selectedFile || isSubmitting || isProcessing}
            onClick={handleStartJob}
          >
            {isSubmitting ? '작업 생성 중...' : isProcessing ? '처리 중...' : '분석 시작'}
          </button>
          {selectedFile && !isProcessing && (
            <button
              className="btn btn-secondary"
              onClick={() => setSelectedFile(null)}
            >
              파일 초기화
            </button>
          )}
        </div>

        {/* Live Progress */}
        {(isSubmitting || isProcessing) && (
          <div style={{ marginTop: 16, padding: 20, background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ fontSize: 13, fontWeight: 500 }}>
                {progressDetail || '작업을 준비하고 있습니다...'}
              </span>
              <span style={{ fontSize: 13, color: 'var(--accent-primary)', fontWeight: 600 }}>
                {currentJob?.progress ?? 0}%
              </span>
            </div>
            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{ width: `${currentJob?.progress ?? 5}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </>
  );
}
