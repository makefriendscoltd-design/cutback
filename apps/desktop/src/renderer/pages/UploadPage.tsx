import React, { useState, useCallback, useEffect } from 'react';
import { useJobStore } from '../store/jobStore';
import ShortsComposeSection from '../components/ShortsComposeSection';

interface UploadPageProps {
  onJobStarted: (jobId: string) => void;
}

type EditMode = 'mode-a' | 'mode-b' | 'mode-c';

/**
 * Mode B(보이스오버+B-roll)/Mode C(릴스 조립) 진입점 노출 여부.
 *
 * 현재 제품 범위는 롱폼 편집 하나로 좁혀둔 상태다. 두 모드의 구현은
 * 그대로 남아 있으므로 true 로 바꾸면 바로 다시 쓸 수 있다.
 */
const SHOW_EXPERIMENTAL_MODES = false;

const MODE_A_PRESETS = [
  {
    id: 'ad-short-form',
    name: '광고형 숏폼',
    desc: '빠른 템포, 후킹 강조, 간결한 자막. 15~60초 광고에 최적화.',
    ratio: '9:16' as const,
    tags: ['9:16', 'aggressive', '170 WPM', '점프컷'],
    mode: 'mode-a' as EditMode,
  },
  {
    id: 'info-talking-head',
    name: '정보형 토킹헤드',
    desc: '이해도 우선, 자연스러운 호흡 유지. 3~10분 설명 영상.',
    ratio: '16:9' as const,
    tags: ['16:9', 'balanced', '140 WPM', '자연스러움'],
    mode: 'mode-a' as EditMode,
  },
  {
    id: 'vlog-style',
    name: '브이로그형',
    desc: '친근하고 자연스러운 편집. 호흡 충분히 보존.',
    ratio: '16:9' as const,
    tags: ['16:9', 'conservative', '130 WPM', '감성적'],
    mode: 'mode-a' as EditMode,
  },
];

const MODE_B_PRESETS = [
  {
    id: 'ad-product-broll',
    name: '제품 광고 (B-roll)',
    desc: '보이스오버 + 제품 B-roll 자동 조합. 빠른 컷 전환.',
    ratio: '9:16' as const,
    tags: ['9:16', 'B-roll', '키워드매칭', '빠른컷'],
    mode: 'mode-b' as EditMode,
  },
  {
    id: 'info-broll',
    name: '정보 전달형 (B-roll)',
    desc: '설명 콘텐츠 + B-roll 조합. 안정적 템포, 자연스러운 전환.',
    ratio: '16:9' as const,
    tags: ['16:9', 'B-roll', 'crossfade', '안정적'],
    mode: 'mode-b' as EditMode,
  },
  {
    id: 'ugc-review',
    name: 'UGC 리뷰 (B-roll)',
    desc: '사용자 리뷰 + 제품/경험 B-roll. 유연한 편집.',
    ratio: '9:16' as const,
    tags: ['9:16', 'B-roll', 'UGC', '유연함'],
    mode: 'mode-b' as EditMode,
  },
];

interface CalibrationInfo {
  presetId: string;
  sampleCount: number;
  restoredFillers: Record<string, number>;
  manualCutCount: number;
}

export default function UploadPage({ onJobStarted }: UploadPageProps) {
  const [editMode, setEditMode] = useState<EditMode>('mode-a');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [brollFiles, setBrollFiles] = useState<string[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('ad-short-form');
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [calibration, setCalibration] = useState<CalibrationInfo | null>(null);

  const { addJob, progressDetail, currentJobId, jobs } = useJobStore();
  const currentJob = jobs.find((j) => j.id === currentJobId);
  const isProcessing = currentJob?.status === 'processing';

  const handleFileSelect = useCallback(async () => {
    // Mode A: 영상만, Mode B: 보이스오버용 오디오/영상 모두 허용
    const filePath =
      editMode === 'mode-b'
        ? await window.api.openVoiceoverDialog()
        : await window.api.openVideoDialog();
    if (filePath) {
      setSelectedFile(filePath);
    }
  }, [editMode]);

  // 선택된 preset 의 calibration 데이터 로드 (학습된 사용자 선호도 표시)
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const result = await window.api.getCalibration(selectedPreset);
        if (cancelled) return;
        if (result.success && result.calibration) {
          const cal = result.calibration as CalibrationInfo;
          setCalibration({
            presetId: cal.presetId,
            sampleCount: cal.sampleCount,
            restoredFillers: cal.restoredFillers ?? {},
            manualCutCount: cal.manualCutCount ?? 0,
          });
        } else {
          setCalibration(null);
        }
      } catch {
        setCalibration(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedPreset]);

  const handleBrollSelect = useCallback(async () => {
    const filePaths = await window.api.openMultipleVideosDialog?.();
    if (filePaths && filePaths.length > 0) {
      setBrollFiles((prev) => [...prev, ...filePaths]);
    }
  }, []);

  const handleModeChange = useCallback((newMode: EditMode) => {
    setEditMode(newMode);
    setSelectedFile(null);
    setBrollFiles([]);
    // Mode C 는 프리셋/Job 파이프라인을 안 쓰므로 프리셋은 그대로 둠
    if (newMode !== 'mode-c') {
      setSelectedPreset(newMode === 'mode-a' ? 'ad-short-form' : 'ad-product-broll');
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
    if (editMode === 'mode-c') return; // Mode C 는 ShortsComposeSection 이 자체 처리
    if (editMode === 'mode-b' && brollFiles.length === 0) {
      alert('Mode B 작업은 B-roll 클립이 1개 이상 필요합니다.\n"+ B-roll 추가" 버튼으로 영상 클립을 먼저 올려주세요.');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await window.api.createJob({
        videoPath: selectedFile,
        presetId: selectedPreset,
        editMode,
        assetPaths: editMode === 'mode-b' ? brollFiles : undefined,
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
          editMode,
          assetPaths: editMode === 'mode-b' ? brollFiles : undefined,
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
  }, [selectedFile, selectedPreset, editMode, brollFiles, addJob, onJobStarted]);

  const PRESETS = editMode === 'mode-a' ? MODE_A_PRESETS : MODE_B_PRESETS;

  return (
    <>
      <div className="page-header">
        <h1>새 작업</h1>
        <p>영상 파일을 업로드하고 프리셋을 선택하세요</p>
      </div>

      <div className="page-body">
        {/* Mode Selector
            현재 제품 범위는 롱폼 편집(Mode A) 하나다.
            Mode B/C 코드는 남아 있지만 진입점을 노출하지 않는다.
            다시 켜려면 SHOW_EXPERIMENTAL_MODES 를 true 로. */}
        {SHOW_EXPERIMENTAL_MODES && (
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 16, marginBottom: 12 }}>편집 모드</h2>
          <div style={{ display: 'flex', gap: 12 }}>
            <button
              className={`btn ${editMode === 'mode-a' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => handleModeChange('mode-a')}
              disabled={isProcessing}
            >
              Mode A: 단일 영상 편집
            </button>
            <button
              className={`btn ${editMode === 'mode-b' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => handleModeChange('mode-b')}
              disabled={isProcessing}
            >
              Mode B: 보이스오버 + B-roll
            </button>
            <button
              className={`btn ${editMode === 'mode-c' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => handleModeChange('mode-c')}
              disabled={isProcessing}
            >
              Mode C: 릴스 자동 조립
            </button>
          </div>

          {/* Mode B 사용 안내 */}
          {editMode === 'mode-b' && (
            <div
              style={{
                marginTop: 12,
                padding: '12px 14px',
                background: 'rgba(91, 141, 239, 0.08)',
                borderLeft: '3px solid var(--accent-primary)',
                borderRadius: 'var(--radius-sm)',
                fontSize: 12,
                lineHeight: 1.6,
              }}
            >
              <div style={{ fontWeight: 600, marginBottom: 6, color: 'var(--text-primary)' }}>
                Mode B 사용 흐름
              </div>
              <ol style={{ margin: 0, paddingLeft: 18, color: 'var(--text-secondary)' }}>
                <li>
                  <strong>① 보이스오버 (필수)</strong>: 내레이션 음성 파일 (mp3/wav/mp4/mov).
                  STT 로 문장 단위 타임라인 생성.
                </li>
                <li>
                  <strong>② B-roll 클립 (필수, 여러 개)</strong>: 본인이 직접 촬영하거나
                  미리 받아둔 보조 영상들 (제품 샷, 데모, 풍경 등). 문장에 자동 매칭됨.
                </li>
                <li>
                  <strong>③ 키워드 매칭</strong>: "이 제품은 방수가 됩니다" 문장 → 파일명/태그가{' '}
                  <code style={{ background: 'var(--bg-active)', padding: '0 4px', borderRadius: 2 }}>
                    waterproof
                  </code>
                  ,{' '}
                  <code style={{ background: 'var(--bg-active)', padding: '0 4px', borderRadius: 2 }}>
                    water
                  </code>{' '}
                  같은 클립을 자동 매칭. 길이 안 맞으면 트리밍/속도/반복 자동 결정.
                </li>
              </ol>
              <div style={{ marginTop: 8, color: 'var(--text-muted)', fontSize: 11 }}>
                ⚠️ <strong>지원 안 함</strong>: 외부 라이브러리 (Giphy/Pexels 등)에서 자동으로 짤·밈 가져오기는 별도 기능입니다.
                Mode B 는 본인이 보유한 클립만 다룹니다.
              </div>
            </div>
          )}
        </div>
        )}

        {/* Mode C: 릴스 자동 조립 (Job 파이프라인 미사용) */}
        {editMode === 'mode-c' ? (
          <ShortsComposeSection />
        ) : (
        <>
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
              : editMode === 'mode-a'
              ? '영상 파일을 여기에 드래그하거나 클릭하세요'
              : '보이스오버 오디오/영상 파일을 선택하세요'}
          </div>
          <div className="drop-zone-hint">
            {editMode === 'mode-a' ? 'MP4, MOV, AVI, MKV, WebM 지원' : 'MP3, WAV, MP4, MOV 지원'}
          </div>
        </div>

        {/* Mode B: B-roll Files */}
        {editMode === 'mode-b' && (
          <div style={{ marginTop: 24 }}>
            <h2 style={{ fontSize: 16, marginBottom: 12 }}>B-roll 클립 ({brollFiles.length}개)</h2>
            <button
              className="btn btn-secondary"
              onClick={handleBrollSelect}
              disabled={isProcessing}
              style={{ marginBottom: 12 }}
            >
              + B-roll 추가
            </button>
            {brollFiles.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {brollFiles.map((file, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '8px 12px',
                      background: 'var(--bg-secondary)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: 12,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <span>{file.split('\\').pop() || file.split('/').pop()}</span>
                    <button
                      onClick={() => setBrollFiles((prev) => prev.filter((_, i) => i !== idx))}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        padding: '4px 8px',
                      }}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Preset Selection */}
        <div style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: 16, marginBottom: 4 }}>편집 프리셋 선택</h2>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 12 }}>
            영상 타입에 맞는 프리셋을 선택하면 최적의 편집 설정이 적용됩니다
          </p>

          {/* Calibration learned-preferences hint */}
          {calibration && calibration.sampleCount > 0 && (
            <div
              style={{
                marginBottom: 12,
                padding: '10px 12px',
                background: 'rgba(91, 141, 239, 0.1)',
                borderLeft: '3px solid var(--accent-primary)',
                borderRadius: 'var(--radius-sm)',
                fontSize: 12,
                color: 'var(--text-secondary)',
              }}
            >
              <span style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>
                학습됨
              </span>{' '}
              · 이 프리셋은 {calibration.sampleCount}개 작업에서 당신의 편집 패턴을 학습했어요.
              {Object.keys(calibration.restoredFillers).length > 0 && (
                <>
                  {' '}자주 보존하는 단어:{' '}
                  {Object.entries(calibration.restoredFillers)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 4)
                    .map(([word, count]) => `"${word}"(${count})`)
                    .join(', ')}
                </>
              )}
              {calibration.manualCutCount > 0 && (
                <> · 직접 추가한 컷 {calibration.manualCutCount}개</>
              )}
            </div>
          )}

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
        <div style={{ marginTop: 32 }}>
          {/* Mode B 요구사항 미충족 안내 */}
          {editMode === 'mode-b' && selectedFile && brollFiles.length === 0 && (
            <div
              style={{
                marginBottom: 12,
                padding: '10px 12px',
                background: 'rgba(245, 158, 11, 0.1)',
                borderLeft: '3px solid var(--warning)',
                borderRadius: 'var(--radius-sm)',
                fontSize: 12,
              }}
            >
              <strong style={{ color: 'var(--warning)' }}>B-roll 클립이 비어 있습니다.</strong>{' '}
              Mode B 는 보이스오버 + 1개 이상의 B-roll 클립이 필요합니다.
            </div>
          )}
          <div style={{ display: 'flex', gap: 12 }}>
            <button
              className="btn btn-primary"
              disabled={
                !selectedFile ||
                (editMode === 'mode-b' && brollFiles.length === 0) ||
                isSubmitting ||
                isProcessing
              }
              onClick={handleStartJob}
            >
              {isSubmitting ? '작업 생성 중...' : isProcessing ? '처리 중...' : '분석 시작'}
            </button>
            {selectedFile && !isProcessing && (
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setSelectedFile(null);
                  setBrollFiles([]);
                }}
              >
                파일 초기화
              </button>
            )}
          </div>
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
        </>
        )}
      </div>
    </>
  );
}
