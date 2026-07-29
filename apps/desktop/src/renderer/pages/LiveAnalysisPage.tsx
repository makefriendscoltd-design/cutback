import React, { useEffect, useMemo, useRef, useState } from 'react';
import WaveformDisplay from '../components/timeline/WaveformDisplay';
import OverlayLayer, {
  OverlayLegend,
  CUT_COLORS,
} from '../components/timeline/OverlayLayer';
import DetailPanel from '../components/timeline/DetailPanel';
import ThresholdControls, {
  ThresholdValues,
  deriveBaseline,
} from '../components/timeline/ThresholdControls';
import { useJobStore } from '../store/jobStore';

type CutType = keyof typeof CUT_COLORS;

interface PartialCut {
  id: string;
  type: CutType;
  start: number;
  end: number;
  duration: number;
  confidence: number;
  reason: string;
  reasonText?: string;
  source: string;
  presetRule?: string;
  enabled: boolean;
  reviewRequired?: boolean;
  metadata?: Record<string, unknown>;
}

interface PipelinePartial {
  audioPath?: string;
  silenceCuts?: PartialCut[];
  fillerCuts?: PartialCut[];
  retakeCuts?: PartialCut[];
  captionSegments?: PartialCut[];
  transcript?: { duration: number; words: unknown[]; full_text: string };
}

interface LiveAnalysisPageProps {
  onAnalysisComplete?: () => void;
}

/**
 * Live Analysis Timeline.
 *
 * 분석이 진행되는 동안:
 *  1. 오디오 추출 → 파형 peaks 요청
 *  2. 무음/말버릇/재시도/자막 단계가 끝날 때마다 IPC partial 이벤트로 cut 데이터 수신
 *  3. WaveformDisplay 위에 OverlayLayer 로 색상 구간 표시
 *  4. 사용자가 구간 클릭 → 우측 DetailPanel 에서 시작/종료/사유/confidence/preset rule 확인
 *
 * 분석 중에 click 가능, 단계가 추가되면 자동으로 새 색상 구간이 나타남.
 */
export default function LiveAnalysisPage({
  onAnalysisComplete,
}: LiveAnalysisPageProps) {
  const { currentJobId, jobs, currentResults, progressDetail, toggleCutDecision } =
    useJobStore();
  const currentJob = jobs.find((j) => j.id === currentJobId);

  const [peaks, setPeaks] = useState<number[]>([]);
  const [audioDuration, setAudioDuration] = useState<number>(0);
  const [partials, setPartials] = useState<{
    silenceCuts: PartialCut[];
    fillerCuts: PartialCut[];
    retakeCuts: PartialCut[];
    captionSegments: PartialCut[];
  }>({
    silenceCuts: [],
    fillerCuts: [],
    retakeCuts: [],
    captionSegments: [],
  });
  const [selectedCutId, setSelectedCutId] = useState<string | undefined>();
  const peaksRequestedFor = useRef<string | null>(null);

  // ----- Threshold controls (preview recompute) -----
  const [audioPath, setAudioPath] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<unknown>(null);
  const [thresholds, setThresholds] = useState<ThresholdValues | null>(null);
  const [baseline, setBaseline] = useState<ThresholdValues | null>(null);
  const [isComputing, setIsComputing] = useState(false);
  const [lastRecomputeMs, setLastRecomputeMs] = useState<number | undefined>();
  const recomputeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // job 이 바뀌면 (새 작업 시작) state 초기화
  useEffect(() => {
    if (!currentJobId) return;
    setPeaks([]);
    setAudioDuration(0);
    setPartials({
      silenceCuts: [],
      fillerCuts: [],
      retakeCuts: [],
      captionSegments: [],
    });
    setSelectedCutId(undefined);
    peaksRequestedFor.current = null;
    setAudioPath(null);
    setTranscript(null);
    setThresholds(null);
    setBaseline(null);
    setIsComputing(false);
    setLastRecomputeMs(undefined);
  }, [currentJobId]);

  // 새 job 시작 시 baseline (preset 기본값) 로드
  useEffect(() => {
    if (!currentJob?.presetId) return;
    let cancelled = false;
    (async () => {
      const preset = (await window.api.loadPreset(currentJob.presetId)) as
        | Parameters<typeof deriveBaseline>[0]
        | null;
      if (cancelled) return;
      const base = deriveBaseline(preset);
      setBaseline(base);
      if (!thresholds) setThresholds(base);
    })();
    return () => {
      cancelled = true;
    };
  }, [currentJob?.presetId]);

  // partial 결과 스트림 구독
  useEffect(() => {
    const off = window.api.onJobPartial(async (data) => {
      if (data.jobId !== currentJobId) return;
      const partial = data.partial as PipelinePartial;

      // 오디오 추출 단계: peaks 요청 + audioPath 캐시 (recompute 에 사용)
      if (partial.audioPath && peaksRequestedFor.current !== partial.audioPath) {
        peaksRequestedFor.current = partial.audioPath;
        setAudioPath(partial.audioPath);
        const result = await window.api.audioPeaks(partial.audioPath, 1500);
        if (result.success && result.peaks) {
          setPeaks(result.peaks);
          if (result.duration) setAudioDuration(result.duration);
        }
      }

      // 단계별 cut 누적
      setPartials((prev) => ({
        silenceCuts: partial.silenceCuts ?? prev.silenceCuts,
        fillerCuts: partial.fillerCuts ?? prev.fillerCuts,
        retakeCuts: partial.retakeCuts ?? prev.retakeCuts,
        captionSegments: partial.captionSegments ?? prev.captionSegments,
      }));

      // transcript 가 들어오면 duration 보정 + recompute 용 캐시
      if (partial.transcript) {
        setTranscript(partial.transcript);
        if (partial.transcript.duration && audioDuration === 0) {
          setAudioDuration(partial.transcript.duration);
        }
      }
    });
    return off;
  }, [currentJobId, audioDuration]);

  // ----- Debounced recompute when thresholds change -----
  // 슬라이더 값을 바꿀 때마다 350ms debounce 후 IPC 호출.
  // 결과가 오면 partials.silenceCuts / fillerCuts 를 덮어쓴다.
  useEffect(() => {
    if (!thresholds || !baseline || !audioPath || !currentJobId || !currentJob?.presetId) {
      return;
    }
    // baseline 과 동일하면 굳이 recompute 안 함
    if (
      thresholds.silenceThresholdDb === baseline.silenceThresholdDb &&
      thresholds.minSilenceDurationMs === baseline.minSilenceDurationMs &&
      thresholds.fillerStrength === baseline.fillerStrength
    ) {
      return;
    }
    if (recomputeTimer.current) clearTimeout(recomputeTimer.current);
    recomputeTimer.current = setTimeout(async () => {
      setIsComputing(true);
      try {
        const res = await window.api.recomputeCuts({
          jobId: currentJobId,
          audioPath,
          transcript: transcript ?? undefined,
          presetId: currentJob.presetId,
          overrides: {
            audio: {
              silence_threshold_db: thresholds.silenceThresholdDb,
              min_silence_duration_ms: thresholds.minSilenceDurationMs,
            },
            filler_words: {
              removal_strength: thresholds.fillerStrength,
            },
          },
        });
        if (res.success) {
          setPartials((prev) => ({
            ...prev,
            silenceCuts: (res.silenceCuts as PartialCut[]) ?? prev.silenceCuts,
            fillerCuts: (res.fillerCuts as PartialCut[]) ?? prev.fillerCuts,
          }));
          setLastRecomputeMs(res.durationMs);
          // 선택된 cut 이 새 데이터에 없으면 선택 해제
          setSelectedCutId(undefined);
        }
      } finally {
        setIsComputing(false);
      }
    }, 350);
    return () => {
      if (recomputeTimer.current) clearTimeout(recomputeTimer.current);
    };
  }, [thresholds, baseline, audioPath, transcript, currentJobId, currentJob?.presetId]);

  // 분석 완료 후 (currentResults 가 채워짐) 표시 데이터 결정
  // 완료 결과가 있으면 그것을 우선 사용, 아니면 partial 누적 사용
  const allCuts: PartialCut[] = useMemo(() => {
    if (currentResults?.cutDecisions && currentResults.cutDecisions.length > 0) {
      const completed = currentResults.cutDecisions as unknown as PartialCut[];
      const captions = (currentResults as unknown as { captionSegments?: PartialCut[] })
        .captionSegments;
      // 완료 결과는 captions 가 분리되어 있을 수 있어 partials 의 captionSegments 도 합침
      return [...completed, ...(captions ?? partials.captionSegments)];
    }
    return [
      ...partials.silenceCuts,
      ...partials.fillerCuts,
      ...partials.retakeCuts,
      ...partials.captionSegments,
    ];
  }, [currentResults, partials]);

  const counts = useMemo(
    () => ({
      silence: allCuts.filter((c) => c.type === 'silence').length,
      filler_word: allCuts.filter((c) => c.type === 'filler_word').length,
      retake: allCuts.filter((c) => c.type === 'retake').length,
      caption_segment: allCuts.filter((c) => c.type === 'caption_segment').length,
    }),
    [allCuts]
  );

  const selectedCut = useMemo(
    () => allCuts.find((c) => c.id === selectedCutId) ?? null,
    [allCuts, selectedCutId]
  );

  const isProcessing = currentJob?.status === 'processing';
  const isFailed = currentJob?.status === 'failed';
  const progress = currentJob?.progress ?? 0;

  // job 완료 시 콜백
  useEffect(() => {
    if (currentJob?.status === 'completed' && onAnalysisComplete) {
      // 자동 전환 없이 버튼으로 유도 (아래 UI 참조)
    }
  }, [currentJob?.status, onAnalysisComplete]);

  if (!currentJobId) {
    return (
      <>
        <div className="page-header">
          <h1>라이브 분석 타임라인</h1>
          <p>분석 중인 작업이 없습니다. 먼저 새 작업을 시작하세요.</p>
        </div>
      </>
    );
  }

  const timelineHeight = 140;

  return (
    <>
      <div className="page-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1>라이브 분석 타임라인</h1>
          <p style={isFailed ? { color: 'var(--danger)' } : undefined}>
            {isProcessing
              ? `${progressDetail || '분석 진행 중...'} (${progress}%)`
              : currentJob?.status === 'completed'
              ? '분석 완료. 색상 구간을 클릭해 상세 정보를 확인하세요.'
              : isFailed
              ? `분석 실패: ${currentJob?.error || '알 수 없는 오류'}`
              : '대기 중'}
          </p>
        </div>
        {currentJob?.status === 'completed' && onAnalysisComplete && (
          <button
            className="btn btn-primary"
            onClick={onAnalysisComplete}
            style={{ fontWeight: 600, fontSize: 15, padding: '10px 24px', whiteSpace: 'nowrap' }}
          >
            검수 / 편집으로 이동 →
          </button>
        )}
      </div>

      <div className="page-body" style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>
        {/* 왼쪽: Waveform + Overlay */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              padding: 16,
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-md)',
              marginBottom: 16,
            }}
          >
            <div style={{ position: 'relative', marginBottom: 12 }}>
              <WaveformDisplay
                peaks={peaks}
                duration={audioDuration}
                analysisProgress={progress}
                height={timelineHeight}
              />
              <OverlayLayer
                cuts={allCuts.map((c) => ({
                  id: c.id,
                  type: c.type,
                  start: c.start,
                  end: c.end,
                  enabled: c.enabled,
                  reviewRequired: c.reviewRequired,
                }))}
                duration={audioDuration}
                height={timelineHeight}
                selectedCutId={selectedCutId}
                onCutClick={(id) => setSelectedCutId(id)}
              />
            </div>

            <OverlayLegend counts={counts} />

            {/* 진행 상태 바 */}
            {isProcessing && (
              <div style={{ marginTop: 16 }}>
                <div className="progress-bar-container">
                  <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
                </div>
                <div
                  style={{
                    marginTop: 6,
                    fontSize: 11,
                    color: 'var(--text-secondary)',
                  }}
                >
                  {progressDetail}
                </div>
              </div>
            )}
          </div>

          {/* 통계 */}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <Stat label="총 길이" value={audioDuration > 0 ? `${audioDuration.toFixed(1)}s` : '-'} />
            <Stat label="무음" value={String(counts.silence)} color={CUT_COLORS.silence} />
            <Stat label="말버릇" value={String(counts.filler_word)} color={CUT_COLORS.filler_word} />
            <Stat label="재시도" value={String(counts.retake)} color={CUT_COLORS.retake} />
            <Stat label="자막" value={String(counts.caption_segment)} color={CUT_COLORS.caption_segment} />
          </div>
        </div>

        {/* 오른쪽: Threshold + Detail Panel */}
        <div
          style={{
            width: 360,
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
          }}
        >
          {thresholds && baseline && (
            <ThresholdControls
              values={thresholds}
              onChange={setThresholds}
              baseline={baseline}
              onReset={() => setThresholds(baseline)}
              isComputing={isComputing}
              lastRecomputeMs={lastRecomputeMs}
            />
          )}

          <div
            style={{
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-md)',
              minHeight: 300,
            }}
          >
            <DetailPanel
              cut={selectedCut}
              onToggleEnabled={async (cutId, enabled) => {
                await window.api.toggleCut(cutId, enabled);
                // store 의 currentResults.cutDecisions 도 갱신 → ReviewPage 가 자동으로 반영
                toggleCutDecision(cutId, enabled);
                // 분석 진행 중이라 currentResults 가 아직 없으면 partials 도 갱신
                setPartials((prev) => ({
                  silenceCuts: prev.silenceCuts.map((c) =>
                    c.id === cutId ? { ...c, enabled } : c
                  ),
                  fillerCuts: prev.fillerCuts.map((c) =>
                    c.id === cutId ? { ...c, enabled } : c
                  ),
                  retakeCuts: prev.retakeCuts.map((c) =>
                    c.id === cutId ? { ...c, enabled } : c
                  ),
                  captionSegments: prev.captionSegments,
                }));
              }}
            />
          </div>
        </div>
      </div>
    </>
  );
}

function Stat({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div
      style={{
        flex: '1 1 100px',
        padding: '12px 16px',
        background: 'var(--bg-secondary)',
        borderRadius: 'var(--radius-md)',
        borderLeft: color ? `3px solid ${color}` : undefined,
      }}
    >
      <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)' }}>
        {value}
      </div>
    </div>
  );
}
