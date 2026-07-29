import React, { useEffect, useMemo, useRef, useState } from 'react';

interface CutSegment {
  start: number;
  end: number;
  enabled: boolean;
  type: string;
}

interface Props {
  videoPath: string;
  cuts: CutSegment[];
  /** 원본 길이 (초) */
  originalDuration: number;
  /** 편집 후 길이 (초). 미지정 시 cuts 로 자동 계산 */
  editedDuration?: number;
  /** KPI: 무음/말버릇/재시도 제거 수 */
  kpi?: {
    silenceRemoved: number;
    fillersRemoved: number;
    retakesRemoved: number;
  };
}

type Layout = 'side-by-side' | 'top-bottom';

/**
 * 원본 vs 편집 결과 비교 프리뷰.
 *
 * 좌(또는 위) = 원본 영상 그대로 재생
 * 우(또는 아래) = enabled cuts 를 skip 하면서 재생
 *
 * scrubber 는 원본 시간축을 기준으로 한다. 사용자가 시간을 옮기면
 *   - left video: currentTime = scrub
 *   - right video: 같은 원본 위치를 보여주되, 그 시점이 cut 안이면
 *                   다음 cut 종료 시점으로 자동 점프
 */
export default function BeforeAfterPreview({
  videoPath,
  cuts,
  originalDuration,
  editedDuration,
  kpi,
}: Props) {
  const leftRef = useRef<HTMLVideoElement>(null);
  const rightRef = useRef<HTMLVideoElement>(null);
  const [layout, setLayout] = useState<Layout>('side-by-side');
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [muted, setMuted] = useState({ left: false, right: true });
  /**
   * video element 가 source 를 로드하지 못했을 때 (코덱 미지원, 파일 누락 등) 표시할 에러.
   * MediaError.code 1=ABORTED, 2=NETWORK, 3=DECODE, 4=SRC_NOT_SUPPORTED
   */
  const [videoError, setVideoError] = useState<{ code: number; message: string } | null>(null);

  /** ffmpeg 가 만든 H.264 preview 의 절대 경로 (HEVC 우회 + 신뢰성 보장) */
  const [previewPath, setPreviewPath] = useState<string | null>(null);
  const [previewProgress, setPreviewProgress] = useState<{ current: number; total: number } | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [isGeneratingPreview, setIsGeneratingPreview] = useState(false);
  const previewInFlight = useRef(false);

  // 컴포넌트 마운트 즉시 preview 생성 시도. 캐시 hit 이면 즉시 끝남.
  // onError 대기하다 안 잡히는 케이스가 있어 처음부터 H.264 preview 로 가는 게 가장 신뢰 가능.
  useEffect(() => {
    if (!videoPath) return;
    if (previewInFlight.current || previewPath) return;
    previewInFlight.current = true;
    setIsGeneratingPreview(true);
    const offProgress = window.api.onVideoPreviewProgress((data) => {
      setPreviewProgress({ current: data.current, total: data.total });
    });
    window.api
      .generateVideoPreview(videoPath)
      .then((res) => {
        if (res.success && res.previewPath) {
          setPreviewPath(res.previewPath);
          setVideoError(null);
          setPreviewProgress(null);
        } else {
          setPreviewError(res.error ?? 'Unknown error');
        }
      })
      .catch((e) => setPreviewError((e as Error).message))
      .finally(() => {
        previewInFlight.current = false;
        setIsGeneratingPreview(false);
        offProgress();
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videoPath]);

  // 활성화된 cut 만 (enabled=true)
  const activeCuts = useMemo(
    () => cuts.filter((c) => c.enabled).sort((a, b) => a.start - b.start),
    [cuts]
  );

  // 절약 시간 계산
  const savedTime = useMemo(
    () => activeCuts.reduce((sum, c) => sum + (c.end - c.start), 0),
    [activeCuts]
  );

  const finalEditedDuration = editedDuration ?? originalDuration - savedTime;

  // src URL — 항상 preview 우선 사용. mount 시 useEffect 가 generateVideoPreview 호출,
  // 캐시 hit 이면 즉시 / 최초만 ffmpeg 트랜스코딩 (몇십초). preview 가 없으면 src 비워둠.
  const videoSrc = useMemo(() => {
    if (!previewPath) return '';
    const normalized = previewPath.replace(/\\/g, '/');
    return `cutback-media:///${encodeURIComponent(normalized)}`;
  }, [previewPath]);

  // 우측 video: 원본 시간축으로 재생되다가 enabled cut 안에 들어오면 cut.end 로 점프
  const handleRightTimeUpdate = () => {
    const v = rightRef.current;
    if (!v) return;
    const t = v.currentTime;
    for (const cut of activeCuts) {
      if (t >= cut.start && t < cut.end) {
        // cut 끝으로 점프
        v.currentTime = cut.end + 0.001;
        return;
      }
    }
  };

  // 양쪽 video 동기화 + scrubber 갱신
  const handleLeftTimeUpdate = () => {
    const left = leftRef.current;
    if (!left) return;
    setCurrentTime(left.currentTime);
    // right 가 left 와 너무 떨어지면 sync
    const right = rightRef.current;
    if (right && Math.abs(right.currentTime - left.currentTime) > 0.5) {
      right.currentTime = left.currentTime;
    }
  };

  const handlePlayPause = () => {
    const left = leftRef.current;
    const right = rightRef.current;
    if (!left || !right) return;
    if (isPlaying) {
      left.pause();
      right.pause();
      setIsPlaying(false);
    } else {
      // play() 가 reject 되면 promise unhandled 가 콘솔에 뜨는 걸 방지
      left.play().catch(() => {});
      right.play().catch(() => {});
      setIsPlaying(true);
    }
  };

  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement>) => {
    const v = e.currentTarget;
    const err = v.error;
    if (!err) return;
    const codeMessages: Record<number, string> = {
      1: 'Aborted',
      2: 'Network error',
      3: '디코더 실패 — 영상 코덱(HEVC/H.265 등)을 Chromium 이 재생 못 함',
      4: '소스 미지원 — 영상 코덱(HEVC/H.265 등)을 Chromium 이 재생 못 함',
    };
    setVideoError({
      code: err.code,
      message: codeMessages[err.code] ?? err.message ?? 'Unknown',
    });

    // code 3/4 = 코덱 문제 → ffmpeg 로 H.264 preview 생성을 자동 trigger.
    // 단, 이미 previewPath 를 쓰는 중인데 그것도 실패했다면 무한루프 방지.
    if ((err.code === 3 || err.code === 4) && !previewPath && !previewInFlight.current) {
      previewInFlight.current = true;
      setIsGeneratingPreview(true);
      setPreviewError(null);
      const offProgress = window.api.onVideoPreviewProgress((data) => {
        setPreviewProgress({ current: data.current, total: data.total });
      });
      window.api
        .generateVideoPreview(videoPath)
        .then((res) => {
          if (res.success && res.previewPath) {
            setPreviewPath(res.previewPath);
            setVideoError(null);
            setPreviewProgress(null);
          } else {
            setPreviewError(res.error ?? 'Unknown error');
          }
        })
        .catch((e) => setPreviewError((e as Error).message))
        .finally(() => {
          previewInFlight.current = false;
          setIsGeneratingPreview(false);
          offProgress();
        });
    }
  };

  const handleScrub = (t: number) => {
    setCurrentTime(t);
    if (leftRef.current) leftRef.current.currentTime = t;
    if (rightRef.current) rightRef.current.currentTime = t;
  };

  // mute 변경 시 실제 video 에 반영
  useEffect(() => {
    if (leftRef.current) leftRef.current.muted = muted.left;
    if (rightRef.current) rightRef.current.muted = muted.right;
  }, [muted]);

  // src 가 바뀌면 video.load() 명시 호출.
  // React 의 video element 는 src prop 변경에 항상 fetch 를 새로 시작하지 않을 때가 있어
  // 안전하게 강제로 load 트리거.
  useEffect(() => {
    if (!videoSrc) return;
    if (leftRef.current) leftRef.current.load();
    if (rightRef.current) rightRef.current.load();
  }, [videoSrc]);

  const isHorizontal = layout === 'side-by-side';

  return (
    <div style={{ background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', padding: 16 }}>
      {/* Toolbar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 12,
          flexWrap: 'wrap',
          gap: 8,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <h2 style={{ margin: 0, fontSize: 16 }}>Before / After 비교</h2>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            왼쪽: 원본 · 오른쪽: 편집 결과
          </span>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          <button
            className={`btn btn-sm ${layout === 'side-by-side' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setLayout('side-by-side')}
          >
            좌우
          </button>
          <button
            className={`btn btn-sm ${layout === 'top-bottom' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setLayout('top-bottom')}
          >
            상하
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 8,
          marginBottom: 12,
        }}
      >
        <KpiCard
          label="총 절약 시간"
          value={`${savedTime.toFixed(1)}s`}
          sub={`${((savedTime / originalDuration) * 100).toFixed(1)}%`}
          accent
        />
        <KpiCard label="원본 길이" value={`${originalDuration.toFixed(1)}s`} />
        <KpiCard label="편집 후 길이" value={`${finalEditedDuration.toFixed(1)}s`} />
        <KpiCard
          label="제거된 구간"
          value={String(activeCuts.length)}
          sub={
            kpi
              ? `무음 ${kpi.silenceRemoved} · 말버릇 ${kpi.fillersRemoved} · 재시도 ${kpi.retakesRemoved}`
              : undefined
          }
        />
      </div>

      {/* Preview generation in progress */}
      {isGeneratingPreview ? (
        <div
          style={{
            padding: 12,
            marginBottom: 12,
            background: 'rgba(91, 141, 239, 0.1)',
            borderLeft: '3px solid var(--accent-primary)',
            borderRadius: 'var(--radius-sm)',
            fontSize: 12,
          }}
        >
          <div style={{ fontWeight: 600, marginBottom: 4 }}>
            영상이 HEVC 등 미지원 코덱이라 미리보기 트랜스코딩 중...
          </div>
          {previewProgress && previewProgress.total > 0 && (
            <>
              <div className="progress-bar-container" style={{ marginTop: 6 }}>
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${Math.min(100, (previewProgress.current / previewProgress.total) * 100)}%`,
                  }}
                />
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                {previewProgress.current.toFixed(0)}s / {previewProgress.total.toFixed(0)}s
              </div>
            </>
          )}
          <div style={{ color: 'var(--text-muted)', marginTop: 6, fontSize: 11 }}>
            한 번 만들어두면 캐시되어 다음부터 바로 떠요.
          </div>
        </div>
      ) : null}

      {/* Codec error after failed preview attempt */}
      {videoError && previewError && (
        <div
          style={{
            padding: 12,
            marginBottom: 12,
            background: 'rgba(239, 68, 68, 0.1)',
            borderLeft: '3px solid var(--danger)',
            borderRadius: 'var(--radius-sm)',
            fontSize: 12,
          }}
        >
          <div style={{ fontWeight: 600, marginBottom: 4 }}>
            영상 미리보기를 표시할 수 없습니다 (code {videoError.code})
          </div>
          <div style={{ color: 'var(--text-secondary)', marginBottom: 8 }}>
            {videoError.message}
          </div>
          <div style={{ color: 'var(--text-muted)', lineHeight: 1.5 }}>
            트랜스코딩도 실패: {previewError}
            <br />
            <strong style={{ color: 'var(--text-primary)' }}>
              아래 [영상 렌더링] 버튼으로 H.264 MP4 출력을 받으세요.
            </strong>
          </div>
        </div>
      )}

      {/* Videos — preview 가 준비되기 전에는 placeholder, 준비되면 video element 를 fresh 하게 mount.
          key={videoSrc} 로 src 변경 시 강제 remount → 기존 element 의 stale src 문제 회피. */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: isHorizontal ? '1fr 1fr' : '1fr',
          gridTemplateRows: isHorizontal ? '1fr' : '1fr 1fr',
          gap: 8,
          marginBottom: 12,
        }}
      >
        {videoSrc ? (
          <>
            <VideoPanel
              key={`left-${videoSrc}`}
              videoRef={leftRef}
              src={videoSrc}
              label="원본"
              accent="var(--text-secondary)"
              muted={muted.left}
              onTimeUpdate={handleLeftTimeUpdate}
              onError={handleVideoError}
              onMuteToggle={() => setMuted((m) => ({ ...m, left: !m.left }))}
            />
            <VideoPanel
              key={`right-${videoSrc}`}
              videoRef={rightRef}
              src={videoSrc}
              label="편집 결과"
              accent="var(--success)"
              muted={muted.right}
              onTimeUpdate={handleRightTimeUpdate}
              onError={handleVideoError}
              onMuteToggle={() => setMuted((m) => ({ ...m, right: !m.right }))}
            />
          </>
        ) : (
          <>
            <VideoPlaceholder label="원본" />
            <VideoPlaceholder label="편집 결과" />
          </>
        )}
      </div>

      {/* Scrubber */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button className="btn btn-primary btn-sm" onClick={handlePlayPause}>
          {isPlaying ? '일시정지' : '재생'}
        </button>
        <input
          type="range"
          min={0}
          max={originalDuration}
          step={0.1}
          value={currentTime}
          onChange={(e) => handleScrub(Number(e.target.value))}
          style={{ flex: 1, cursor: 'pointer' }}
        />
        <span
          style={{
            fontFamily: 'ui-monospace, monospace',
            fontSize: 12,
            color: 'var(--text-secondary)',
            minWidth: 100,
            textAlign: 'right',
          }}
        >
          {formatTime(currentTime)} / {formatTime(originalDuration)}
        </span>
      </div>
    </div>
  );
}

function VideoPanel({
  videoRef,
  src,
  label,
  accent,
  muted,
  onTimeUpdate,
  onError,
  onMuteToggle,
}: {
  videoRef: React.RefObject<HTMLVideoElement>;
  src: string;
  label: string;
  accent: string;
  muted: boolean;
  onTimeUpdate: () => void;
  onError?: (e: React.SyntheticEvent<HTMLVideoElement>) => void;
  onMuteToggle: () => void;
}) {
  return (
    <div style={{ position: 'relative', background: '#000', borderRadius: 4, overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute',
          top: 8,
          left: 8,
          padding: '2px 8px',
          background: 'rgba(0,0,0,0.6)',
          color: accent,
          fontSize: 11,
          fontWeight: 600,
          borderRadius: 2,
          zIndex: 1,
        }}
      >
        {label}
      </div>
      <button
        onClick={onMuteToggle}
        style={{
          position: 'absolute',
          top: 8,
          right: 8,
          padding: '4px 8px',
          background: 'rgba(0,0,0,0.6)',
          color: '#fff',
          fontSize: 11,
          border: 'none',
          borderRadius: 2,
          cursor: 'pointer',
          zIndex: 1,
        }}
      >
        {muted ? '🔇' : '🔊'}
      </button>
      <video
        ref={videoRef}
        onTimeUpdate={onTimeUpdate}
        onError={onError}
        onLoadStart={() => console.log('[BeforeAfter] loadstart', label, src)}
        onLoadedMetadata={(e) =>
          console.log('[BeforeAfter] loadedmetadata', label, {
            duration: e.currentTarget.duration,
            videoWidth: e.currentTarget.videoWidth,
          })
        }
        onCanPlay={() => console.log('[BeforeAfter] canplay', label)}
        muted={muted}
        playsInline
        preload="auto"
        controls
        style={{ width: '100%', height: '100%', display: 'block', minHeight: 220, background: '#000' }}
      >
        {/* <source> 로 src 를 주는 게 일부 Chromium 빌드에서 protocol scheme 문제를 회피한다.
            type 도 명시해서 디코더 hint 줌. */}
        <source src={src} type="video/mp4" />
      </video>
    </div>
  );
}

function VideoPlaceholder({ label }: { label: string }) {
  return (
    <div
      style={{
        position: 'relative',
        background: '#000',
        borderRadius: 4,
        minHeight: 220,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--text-muted)',
        fontSize: 12,
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 8,
          left: 8,
          padding: '2px 8px',
          background: 'rgba(0,0,0,0.6)',
          color: 'var(--text-secondary)',
          fontSize: 11,
          fontWeight: 600,
          borderRadius: 2,
        }}
      >
        {label}
      </div>
      <div>미리보기 준비 중...</div>
    </div>
  );
}

function KpiCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: boolean;
}) {
  return (
    <div
      style={{
        padding: 12,
        background: 'var(--bg-active)',
        borderRadius: 'var(--radius-sm)',
        borderLeft: accent ? '3px solid var(--success)' : undefined,
      }}
    >
      <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)' }}>{value}</div>
      {sub && <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

function formatTime(s: number): string {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  const ms = Math.floor((s % 1) * 100);
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}.${String(ms).padStart(2, '0')}`;
}
