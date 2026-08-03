import React, { useState, useCallback, useEffect } from 'react';

/**
 * Mode C: 릴스 자동 조립 섹션 (UploadPage 안에서 렌더)
 *
 * 짧은 클립 여러 개 → 9:16 자동 조립 + 음절 단위 자막 + FHD/4K mp4 추출.
 * 워크플로우:
 *   1. 클립/보이스오버/스크립트 입력
 *   2. "자막 준비" → 보이스오버 있으면 STT 자동 받아쓰기, 없으면 스크립트 템포 배치
 *   3. 검수 표에서 오타/타이밍 수정
 *   4. 자막 방식(구움/SRT/둘다) 선택 후 "릴스 생성"
 */

interface FontInfo {
  id: string;
  family: string;
  license: string;
  available: boolean;
}

interface SubtitleEvent {
  text: string;
  start: number;
  end: number;
}

interface ComposeResult {
  outputPath: string;
  durationSec: number;
  segmentCount: number;
  subtitleEventCount: number;
  width: number;
  height: number;
  srtPath?: string;
}

type SubtitleMode = 'burn' | 'srt' | 'both';

export default function ShortsComposeSection() {
  const [clips, setClips] = useState<string[]>([]);
  const [voiceover, setVoiceover] = useState<string | null>(null);
  const [script, setScript] = useState('');
  const [resolution, setResolution] = useState<'fhd' | '4k'>('fhd');
  const [fontId, setFontId] = useState('pretendard-extrabold');
  const [fonts, setFonts] = useState<FontInfo[]>([]);
  const [tempo, setTempo] = useState(6);
  const [chunkMode, setChunkMode] = useState<'syllable' | 'sentence'>('syllable');
  const [chunkSyllables, setChunkSyllables] = useState(3);
  const [clipMin, setClipMin] = useState(1.0);
  const [clipMax, setClipMax] = useState(2.5);
  const [position, setPosition] = useState<'center' | 'bottom'>('center');
  const [subtitleMode, setSubtitleMode] = useState<SubtitleMode>('burn');

  // 자막 검수
  const [events, setEvents] = useState<SubtitleEvent[] | null>(null);
  const [isPreparing, setIsPreparing] = useState(false);
  const [subtitleSource, setSubtitleSource] = useState<'stt' | 'script' | 'none' | null>(null);
  const [sttNote, setSttNote] = useState<string | null>(null);

  const [isComposing, setIsComposing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMsg, setProgressMsg] = useState('');
  const [result, setResult] = useState<ComposeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    window.api.listShortsFonts?.().then(setFonts).catch(() => {});
  }, []);

  useEffect(() => {
    const off = window.api.onShortsProgress?.((p) => {
      setProgress(Math.round(p.progress * 100));
      setProgressMsg(p.message);
    });
    return () => off?.();
  }, []);

  const handleAddClips = useCallback(async () => {
    const paths = await window.api.openMultipleVideosDialog?.();
    if (paths && paths.length > 0) setClips((prev) => [...prev, ...paths]);
  }, []);

  const handleSelectVoiceover = useCallback(async () => {
    const p = await window.api.openVoiceoverDialog();
    if (p) {
      setVoiceover(p);
      setEvents(null); // 입력 바뀌면 검수 초기화
    }
  }, []);

  const moveClip = useCallback((idx: number, dir: -1 | 1) => {
    setClips((prev) => {
      const next = [...prev];
      const target = idx + dir;
      if (target < 0 || target >= next.length) return prev;
      [next[idx], next[target]] = [next[target], next[idx]];
      return next;
    });
  }, []);

  // 자막 준비: STT 또는 스크립트 → 검수용 events
  const handlePrepareSubtitles = useCallback(async () => {
    if (!voiceover && !script.trim()) return;
    setIsPreparing(true);
    setError(null);
    setSttNote(null);
    try {
      const res = await window.api.previewShortsSubtitles({
        script: script.trim() || undefined,
        voiceoverPath: voiceover ?? undefined,
        syllablesPerSecond: tempo,
        chunkMode,
        chunkSyllables,
      });
      if (res.success) {
        setEvents(res.events ?? []);
        setSubtitleSource(res.source ?? 'none');
        if (res.sttError) setSttNote(res.sttError);
      } else {
        setError(res.error ?? '자막 준비 실패');
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsPreparing(false);
    }
  }, [voiceover, script, tempo, chunkMode, chunkSyllables]);

  const updateEvent = useCallback((idx: number, patch: Partial<SubtitleEvent>) => {
    setEvents((prev) => {
      if (!prev) return prev;
      const next = [...prev];
      next[idx] = { ...next[idx], ...patch };
      return next;
    });
  }, []);

  const deleteEvent = useCallback((idx: number) => {
    setEvents((prev) => (prev ? prev.filter((_, i) => i !== idx) : prev));
  }, []);

  const handleCompose = useCallback(async () => {
    if (clips.length === 0) return;
    setIsComposing(true);
    setResult(null);
    setError(null);
    setProgress(0);
    setProgressMsg('시작 중...');
    try {
      const res = await window.api.composeShorts({
        clips,
        // 검수된 events 가 있으면 그걸, 없으면 raw script 를 넘김
        events: events ?? undefined,
        script: events ? undefined : script.trim() || undefined,
        voiceoverPath: voiceover ?? undefined,
        resolution,
        subtitleMode,
        clipDuration: { min: clipMin, max: clipMax },
        subtitle: {
          fontId,
          syllablesPerSecond: tempo,
          chunkMode,
          chunkSyllables,
          position,
        },
      });
      if (res.success) {
        setResult(res as ComposeResult);
      } else if (res.error !== 'Cancelled') {
        setError(res.error ?? '알 수 없는 오류');
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsComposing(false);
    }
  }, [clips, events, script, voiceover, resolution, subtitleMode, clipMin, clipMax, fontId, tempo, chunkMode, chunkSyllables, position]);

  const fileName = (p: string) => p.split('\\').pop() || p.split('/').pop() || p;

  const labelStyle: React.CSSProperties = {
    fontSize: 12,
    color: 'var(--text-secondary)',
    display: 'block',
    marginBottom: 4,
  };
  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '6px 8px',
    background: 'var(--bg-secondary)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    color: 'var(--text-primary)',
    fontSize: 13,
  };

  const hasSubtitleInput = !!voiceover || !!script.trim();

  return (
    <div>
      {/* 사용 안내 */}
      <div
        style={{
          marginTop: 12,
          padding: '12px 14px',
          background: 'rgba(91, 141, 239, 0.08)',
          borderLeft: '3px solid var(--accent-primary)',
          borderRadius: 'var(--radius-sm)',
          fontSize: 12,
          lineHeight: 1.6,
          marginBottom: 20,
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 6 }}>Mode C: 릴스 자동 조립</div>
        <span style={{ color: 'var(--text-secondary)' }}>
          1~2.5초짜리 짧은 클립들을 속도감 있게 이어붙여 릴스(9:16) mp4 로 추출합니다.
          보이스오버를 넣으면 STT 로 자막이 자동 생성되고, 굽기 전에 오타·타이밍을 검수·수정할 수 있습니다.
          자막을 SRT 로 따로 뽑으면 캡컷에서 이어서 편집할 수도 있습니다.
        </span>
      </div>

      {/* 클립 목록 */}
      <h2 style={{ fontSize: 16, marginBottom: 12 }}>클립 ({clips.length}개)</h2>
      <button
        className="btn btn-secondary"
        onClick={handleAddClips}
        disabled={isComposing}
        style={{ marginBottom: 12 }}
      >
        + 클립 추가 (여러 개 선택 가능)
      </button>
      {clips.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 8 }}>
          {clips.map((file, idx) => (
            <div
              key={`${file}-${idx}`}
              style={{
                padding: '8px 12px',
                background: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-sm)',
                fontSize: 12,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <span style={{ color: 'var(--text-muted)', width: 20 }}>{idx + 1}</span>
              <span style={{ flex: 1 }}>{fileName(file)}</span>
              <button onClick={() => moveClip(idx, -1)} disabled={idx === 0 || isComposing} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>↑</button>
              <button onClick={() => moveClip(idx, 1)} disabled={idx === clips.length - 1 || isComposing} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>↓</button>
              <button
                onClick={() => setClips((prev) => prev.filter((_, i) => i !== idx))}
                disabled={isComposing}
                style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {/* 보이스오버 (선택) */}
      <div style={{ marginTop: 20 }}>
        <h2 style={{ fontSize: 16, marginBottom: 8 }}>
          보이스오버 <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>(선택 — 있으면 자막이 STT 로 자동 생성되고 길이도 음성에 맞춰짐)</span>
        </h2>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button className="btn btn-secondary" onClick={handleSelectVoiceover} disabled={isComposing}>
            {voiceover ? fileName(voiceover) : '오디오 파일 선택'}
          </button>
          {voiceover && (
            <button
              onClick={() => { setVoiceover(null); setEvents(null); }}
              disabled={isComposing}
              style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
            >
              ✕ 제거
            </button>
          )}
        </div>
      </div>

      {/* 자막 스크립트 */}
      <div style={{ marginTop: 20 }}>
        <h2 style={{ fontSize: 16, marginBottom: 8 }}>
          자막 스크립트{' '}
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            {voiceover ? '(보이스오버 STT 실패 시 폴백용 — 비워둬도 됨)' : '(음절 단위로 빠르게 표시됨)'}
          </span>
        </h2>
        <textarea
          value={script}
          onChange={(e) => { setScript(e.target.value); setEvents(null); }}
          placeholder={'예) 집에서 할 수 있는 세가지 운동. 첫째 플랭크. 둘째 스쿼트. 셋째 버피.'}
          disabled={isComposing}
          rows={4}
          style={{ ...inputStyle, resize: 'vertical', fontFamily: 'inherit' }}
        />
      </div>

      {/* 자막 준비 버튼 */}
      {hasSubtitleInput && (
        <div style={{ marginTop: 12 }}>
          <button
            className="btn btn-secondary"
            onClick={handlePrepareSubtitles}
            disabled={isPreparing || isComposing}
          >
            {isPreparing
              ? (voiceover ? '음성 받아쓰는 중... (STT)' : '자막 준비 중...')
              : events
              ? '자막 다시 준비'
              : voiceover
              ? '자막 준비 (STT 자동 받아쓰기)'
              : '자막 준비 (검수용 미리보기)'}
          </button>
          {sttNote && (
            <div style={{ marginTop: 8, fontSize: 12, color: 'var(--warning)' }}>⚠️ {sttNote}</div>
          )}
        </div>
      )}

      {/* 자막 검수 표 */}
      {events && (
        <div style={{ marginTop: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <h2 style={{ fontSize: 15, margin: 0 }}>
              자막 검수 ({events.length}개){' '}
              {subtitleSource === 'stt' && <span style={{ fontSize: 11, color: 'var(--accent-primary)' }}>· STT 자동생성</span>}
              {subtitleSource === 'script' && <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>· 스크립트 기반</span>}
            </h2>
          </div>
          {events.length === 0 ? (
            <div style={{ fontSize: 12, color: 'var(--text-muted)', padding: 12, background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
              자막이 없습니다. 스크립트를 입력하거나 보이스오버를 넣어주세요.
            </div>
          ) : (
            <div style={{ maxHeight: 320, overflowY: 'auto', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                <thead>
                  <tr style={{ position: 'sticky', top: 0, background: 'var(--bg-active)' }}>
                    <th style={{ padding: '6px 8px', textAlign: 'left', width: 28 }}>#</th>
                    <th style={{ padding: '6px 8px', textAlign: 'left' }}>자막 텍스트</th>
                    <th style={{ padding: '6px 8px', textAlign: 'right', width: 74 }}>시작(초)</th>
                    <th style={{ padding: '6px 8px', textAlign: 'right', width: 74 }}>끝(초)</th>
                    <th style={{ padding: '6px 8px', width: 28 }}></th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((ev, idx) => (
                    <tr key={idx} style={{ borderTop: '1px solid var(--border)' }}>
                      <td style={{ padding: '4px 8px', color: 'var(--text-muted)' }}>{idx + 1}</td>
                      <td style={{ padding: '4px 8px' }}>
                        <input
                          value={ev.text}
                          onChange={(e) => updateEvent(idx, { text: e.target.value })}
                          disabled={isComposing}
                          style={{ ...inputStyle, padding: '4px 6px' }}
                        />
                      </td>
                      <td style={{ padding: '4px 8px' }}>
                        <input
                          type="number"
                          step={0.05}
                          value={ev.start.toFixed(2)}
                          onChange={(e) => updateEvent(idx, { start: Number(e.target.value) })}
                          disabled={isComposing}
                          style={{ ...inputStyle, padding: '4px 6px', textAlign: 'right' }}
                        />
                      </td>
                      <td style={{ padding: '4px 8px' }}>
                        <input
                          type="number"
                          step={0.05}
                          value={ev.end.toFixed(2)}
                          onChange={(e) => updateEvent(idx, { end: Number(e.target.value) })}
                          disabled={isComposing}
                          style={{ ...inputStyle, padding: '4px 6px', textAlign: 'right' }}
                        />
                      </td>
                      <td style={{ padding: '4px 8px', textAlign: 'center' }}>
                        <button
                          onClick={() => deleteEvent(idx)}
                          disabled={isComposing}
                          style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
                        >
                          ✕
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
            텍스트/타이밍을 직접 수정할 수 있습니다. 수정한 내용이 최종 영상에 반영됩니다.
          </div>
        </div>
      )}

      {/* 옵션 */}
      <div style={{ marginTop: 20, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
        <div>
          <label style={labelStyle}>해상도</label>
          <select value={resolution} onChange={(e) => setResolution(e.target.value as 'fhd' | '4k')} disabled={isComposing} style={inputStyle}>
            <option value="fhd">FHD (1080×1920) — 빠름</option>
            <option value="4k">4K (2160×3840) — 느림</option>
          </select>
        </div>
        <div>
          <label style={labelStyle}>자막 방식</label>
          <select value={subtitleMode} onChange={(e) => setSubtitleMode(e.target.value as SubtitleMode)} disabled={isComposing} style={inputStyle}>
            <option value="burn">구운 자막 (예쁨, 수정 불가)</option>
            <option value="srt">SRT 별도 (캡컷에서 수정)</option>
            <option value="both">둘 다 (구움 + SRT 백업)</option>
          </select>
        </div>
        <div>
          <label style={labelStyle}>자막 폰트 (전부 상업용 무료)</label>
          <select value={fontId} onChange={(e) => setFontId(e.target.value)} disabled={isComposing || subtitleMode === 'srt'} style={inputStyle}>
            {(fonts.length > 0
              ? fonts
              : [{ id: 'pretendard-extrabold', family: 'Pretendard ExtraBold', license: '', available: true }]
            ).map((f) => (
              <option key={f.id} value={f.id}>
                {f.family}{f.available ? '' : ' (미설치→시스템 폰트)'}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label style={labelStyle}>자막 위치</label>
          <select value={position} onChange={(e) => setPosition(e.target.value as 'center' | 'bottom')} disabled={isComposing || subtitleMode === 'srt'} style={inputStyle}>
            <option value="center">정중앙 (릴스 스타일)</option>
            <option value="bottom">하단</option>
          </select>
        </div>
        <div>
          <label style={labelStyle}>자막 단위</label>
          <select
            value={chunkMode}
            onChange={(e) => { setChunkMode(e.target.value as 'syllable' | 'sentence'); setEvents(null); }}
            disabled={isComposing}
            style={inputStyle}
          >
            <option value="syllable">음절 덩어리 (빠른 템포, 팡팡)</option>
            <option value="sentence">문장 단위 (한 문장 = 한 화면)</option>
          </select>
          {chunkMode === 'sentence' && (
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, lineHeight: 1.4 }}>
              문장 끝(다./요./죠. 등)에서만 끊습니다. 긴 문장은 쪼개지 않고 화면 안에서 줄바꿈돼요.
            </div>
          )}
        </div>
        <div>
          <label style={{ ...labelStyle, opacity: chunkMode === 'sentence' ? 0.4 : 1 }}>
            자막 끊기 ({chunkSyllables}음절/자막){' '}
            <span style={{ color: 'var(--text-muted)' }}>
              {chunkMode === 'sentence'
                ? '· 문장 단위에선 무시됨'
                : chunkSyllables <= 1 ? '한 음절씩 · 가장 빠름' : chunkSyllables >= 5 ? '길게' : '기본'}
            </span>
          </label>
          <input
            type="range"
            min={1}
            max={6}
            step={1}
            value={chunkSyllables}
            onChange={(e) => { setChunkSyllables(Number(e.target.value)); setEvents(null); }}
            disabled={isComposing || chunkMode === 'sentence'}
            style={{ width: '100%', opacity: chunkMode === 'sentence' ? 0.4 : 1 }}
          />
        </div>
        <div>
          <label style={labelStyle}>
            자막 속도 (초당 {tempo}음절){' '}
            {voiceover && <span style={{ color: 'var(--text-muted)' }}>· 음성 있으면 무시됨</span>}
          </label>
          <input
            type="range"
            min={3}
            max={12}
            step={0.5}
            value={tempo}
            onChange={(e) => { setTempo(Number(e.target.value)); setEvents(null); }}
            disabled={isComposing || !!voiceover}
            style={{ width: '100%', opacity: voiceover ? 0.4 : 1 }}
          />
        </div>
        <div>
          <label style={labelStyle}>클립당 최소 (초)</label>
          <input type="number" min={0.3} max={10} step={0.1} value={clipMin} onChange={(e) => setClipMin(Number(e.target.value))} disabled={isComposing} style={inputStyle} />
        </div>
        <div>
          <label style={labelStyle}>클립당 최대 (초)</label>
          <input type="number" min={0.5} max={15} step={0.1} value={clipMax} onChange={(e) => setClipMax(Number(e.target.value))} disabled={isComposing} style={inputStyle} />
        </div>
      </div>

      {/* 생성 버튼 */}
      <div style={{ marginTop: 24 }}>
        <button
          className="btn btn-primary"
          disabled={clips.length === 0 || isComposing || clipMin > clipMax}
          onClick={handleCompose}
        >
          {isComposing ? '생성 중...' : '릴스 생성 (mp4 추출)'}
        </button>
        {hasSubtitleInput && !events && (
          <span style={{ marginLeft: 12, fontSize: 12, color: 'var(--text-muted)' }}>
            먼저 "자막 준비"로 검수하면 오타를 고칠 수 있어요 (건너뛰면 자동 자막으로 바로 생성)
          </span>
        )}
        {clipMin > clipMax && (
          <span style={{ marginLeft: 12, fontSize: 12, color: 'var(--warning)' }}>
            최소 길이가 최대 길이보다 큽니다
          </span>
        )}
      </div>

      {/* 진행률 */}
      {isComposing && (
        <div style={{ marginTop: 16, padding: 20, background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: 13, fontWeight: 500 }}>{progressMsg}</span>
            <span style={{ fontSize: 13, color: 'var(--accent-primary)', fontWeight: 600 }}>{progress}%</span>
          </div>
          <div className="progress-bar-container">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
          {resolution === '4k' && (
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
              4K 인코딩은 CPU 를 많이 사용해 시간이 걸립니다 (10초 영상 기준 1~2분)
            </div>
          )}
        </div>
      )}

      {/* 결과 */}
      {result && (
        <div
          style={{
            marginTop: 16,
            padding: 16,
            background: 'rgba(34, 197, 94, 0.08)',
            borderLeft: '3px solid var(--success, #22c55e)',
            borderRadius: 'var(--radius-sm)',
            fontSize: 13,
          }}
        >
          <div style={{ fontWeight: 600, marginBottom: 4 }}>✅ 릴스 생성 완료</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
            {result.outputPath}
            <br />
            {result.width}×{result.height} · {result.durationSec.toFixed(1)}초 · 세그먼트{' '}
            {result.segmentCount}개 · 자막 {result.subtitleEventCount}개
            {result.srtPath && (
              <>
                <br />
                <span style={{ color: 'var(--accent-primary)' }}>📝 SRT 자막:</span> {result.srtPath}
              </>
            )}
          </div>
        </div>
      )}

      {/* 에러 */}
      {error && (
        <div
          style={{
            marginTop: 16,
            padding: 16,
            background: 'rgba(239, 68, 68, 0.08)',
            borderLeft: '3px solid var(--error, #ef4444)',
            borderRadius: 'var(--radius-sm)',
            fontSize: 13,
          }}
        >
          <strong>생성 실패:</strong> <span style={{ color: 'var(--text-secondary)' }}>{error}</span>
        </div>
      )}
    </div>
  );
}
