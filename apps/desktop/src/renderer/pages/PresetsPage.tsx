import React, { useState, useEffect, useCallback } from 'react';

interface PresetInfo {
  id: string;
  name: string;
  type: string;
  description?: string;
}

interface PresetDetail {
  name: string;
  type: string;
  version: string;
  description?: string;
  audio: {
    silence_threshold_db: number;
    min_silence_duration_ms: number;
    pre_cut_padding_ms: number;
    post_cut_padding_ms: number;
  };
  filler_words: {
    removal_strength: string;
    context_aware: boolean;
    preserve_natural_pauses: boolean;
  };
  captions: {
    segmentation_mode: string;
    max_chars_per_line: number;
    max_lines: number;
  };
  pacing: {
    target_tempo: number;
    allow_jump_cuts: boolean;
    naturalness_score_min: number;
  };
}

const DEFAULT_PRESET: PresetDetail = {
  name: '',
  type: 'custom',
  version: '1.0.0',
  description: '',
  audio: {
    silence_threshold_db: -38,
    min_silence_duration_ms: 600,
    pre_cut_padding_ms: 100,
    post_cut_padding_ms: 80,
  },
  filler_words: {
    removal_strength: 'balanced',
    context_aware: true,
    preserve_natural_pauses: true,
  },
  captions: {
    segmentation_mode: 'by_sentence',
    max_chars_per_line: 18,
    max_lines: 2,
  },
  pacing: {
    target_tempo: 150,
    allow_jump_cuts: false,
    naturalness_score_min: 0.7,
  },
};

export default function PresetsPage() {
  const [presets, setPresets] = useState<PresetInfo[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editing, setEditing] = useState<PresetDetail | null>(null);
  const [isNew, setIsNew] = useState(false);
  const [customName, setCustomName] = useState('');

  const loadPresets = useCallback(async () => {
    try {
      const result = (await window.api.listPresets()) as PresetInfo[];
      setPresets(result);
    } catch (err) {
      console.error('Failed to load presets:', err);
    }
  }, []);

  useEffect(() => {
    loadPresets();
  }, [loadPresets]);

  const handleSelect = async (id: string) => {
    setSelectedId(id);
    setIsNew(false);
    try {
      const preset = (await window.api.loadPreset(id)) as PresetDetail;
      setEditing(preset);
      setCustomName(id);
    } catch (err) {
      console.error('Failed to load preset:', err);
    }
  };

  const handleNew = () => {
    setSelectedId(null);
    setIsNew(true);
    setEditing({ ...DEFAULT_PRESET, name: '새 프리셋' });
    setCustomName('custom-new-' + Date.now());
  };

  const handleSave = async () => {
    if (!editing) return;
    const id = isNew ? customName : selectedId;
    if (!id) return;

    try {
      await window.api.savePreset(id, editing);
      await loadPresets();
      setSelectedId(id);
      setIsNew(false);
    } catch (err) {
      console.error('Failed to save preset:', err);
    }
  };

  const handleDelete = async () => {
    if (!selectedId) return;
    const preset = presets.find((p) => p.id === selectedId);
    if (preset?.type !== 'custom') return;

    try {
      await window.api.deletePreset(selectedId);
      setSelectedId(null);
      setEditing(null);
      await loadPresets();
    } catch (err) {
      console.error('Failed to delete preset:', err);
    }
  };

  const updateAudio = (key: string, value: number) => {
    if (!editing) return;
    setEditing({
      ...editing,
      audio: { ...editing.audio, [key]: value },
    });
  };

  const updateFiller = (key: string, value: unknown) => {
    if (!editing) return;
    setEditing({
      ...editing,
      filler_words: { ...editing.filler_words, [key]: value },
    });
  };

  const updateCaptions = (key: string, value: unknown) => {
    if (!editing) return;
    setEditing({
      ...editing,
      captions: { ...editing.captions, [key]: value },
    });
  };

  const updatePacing = (key: string, value: unknown) => {
    if (!editing) return;
    setEditing({
      ...editing,
      pacing: { ...editing.pacing, [key]: value },
    });
  };

  const isCustom = editing?.type === 'custom' || isNew;

  return (
    <>
      <div className="page-header">
        <h1>프리셋 관리</h1>
        <p>편집 프리셋을 조회, 생성, 수정할 수 있습니다</p>
      </div>

      <div className="page-body" style={{ display: 'flex', gap: 24 }}>
        {/* Left: Preset List */}
        <div style={{ width: 260, flexShrink: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontSize: 13, fontWeight: 600 }}>프리셋 목록</span>
            <button className="btn btn-primary btn-sm" onClick={handleNew}>
              + 새 프리셋
            </button>
          </div>

          <div className="preset-list">
            {presets.map((p) => (
              <div
                key={p.id}
                className={`preset-list-item ${selectedId === p.id ? 'selected' : ''}`}
                onClick={() => handleSelect(p.id)}
              >
                <div className="preset-list-name">{p.name}</div>
                <div className="preset-list-meta">
                  <span className={`preset-type-badge ${p.type}`}>{p.type}</span>
                </div>
              </div>
            ))}
            {presets.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: 13, padding: 16, textAlign: 'center' }}>
                프리셋이 없습니다
              </div>
            )}
          </div>
        </div>

        {/* Right: Preset Editor */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {editing ? (
            <div className="preset-editor">
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <div>
                  <input
                    className="preset-name-input"
                    value={editing.name}
                    onChange={(e) => setEditing({ ...editing, name: e.target.value })}
                    disabled={!isCustom}
                    placeholder="프리셋 이름"
                  />
                  {!isCustom && (
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 8 }}>
                      (기본 프리셋 - 읽기 전용)
                    </span>
                  )}
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  {isCustom && (
                    <>
                      <button className="btn btn-primary btn-sm" onClick={handleSave}>
                        저장
                      </button>
                      {!isNew && (
                        <button className="btn btn-danger btn-sm" onClick={handleDelete}>
                          삭제
                        </button>
                      )}
                    </>
                  )}
                </div>
              </div>

              {/* Audio Settings */}
              <section className="editor-section">
                <h3>오디오 분석</h3>
                <div className="editor-grid">
                  <label>
                    <span>무음 임계값 (dB)</span>
                    <input
                      type="range"
                      min={-60}
                      max={-20}
                      value={editing.audio.silence_threshold_db}
                      onChange={(e) => updateAudio('silence_threshold_db', Number(e.target.value))}
                      disabled={!isCustom}
                    />
                    <span className="range-value">{editing.audio.silence_threshold_db} dB</span>
                  </label>
                  <label>
                    <span>최소 무음 길이 (ms)</span>
                    <input
                      type="range"
                      min={200}
                      max={2000}
                      step={100}
                      value={editing.audio.min_silence_duration_ms}
                      onChange={(e) => updateAudio('min_silence_duration_ms', Number(e.target.value))}
                      disabled={!isCustom}
                    />
                    <span className="range-value">{editing.audio.min_silence_duration_ms} ms</span>
                  </label>
                  <label>
                    <span>앞쪽 패딩 (ms)</span>
                    <input
                      type="range"
                      min={0}
                      max={500}
                      step={10}
                      value={editing.audio.pre_cut_padding_ms}
                      onChange={(e) => updateAudio('pre_cut_padding_ms', Number(e.target.value))}
                      disabled={!isCustom}
                    />
                    <span className="range-value">{editing.audio.pre_cut_padding_ms} ms</span>
                  </label>
                  <label>
                    <span>뒤쪽 패딩 (ms)</span>
                    <input
                      type="range"
                      min={0}
                      max={500}
                      step={10}
                      value={editing.audio.post_cut_padding_ms}
                      onChange={(e) => updateAudio('post_cut_padding_ms', Number(e.target.value))}
                      disabled={!isCustom}
                    />
                    <span className="range-value">{editing.audio.post_cut_padding_ms} ms</span>
                  </label>
                </div>
              </section>

              {/* Filler Word Settings */}
              <section className="editor-section">
                <h3>말버릇 제거</h3>
                <div className="editor-grid">
                  <label>
                    <span>제거 강도</span>
                    <select
                      value={editing.filler_words.removal_strength}
                      onChange={(e) => updateFiller('removal_strength', e.target.value)}
                      disabled={!isCustom}
                    >
                      <option value="conservative">보수적</option>
                      <option value="balanced">균형</option>
                      <option value="aggressive">공격적</option>
                    </select>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={editing.filler_words.context_aware}
                      onChange={(e) => updateFiller('context_aware', e.target.checked)}
                      disabled={!isCustom}
                    />
                    <span>문맥 인식</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={editing.filler_words.preserve_natural_pauses}
                      onChange={(e) => updateFiller('preserve_natural_pauses', e.target.checked)}
                      disabled={!isCustom}
                    />
                    <span>자연스러운 호흡 보존</span>
                  </label>
                </div>
              </section>

              {/* Caption Settings */}
              <section className="editor-section">
                <h3>자막</h3>
                <div className="editor-grid">
                  <label>
                    <span>자막 끊기 모드</span>
                    <select
                      value={editing.captions.segmentation_mode}
                      onChange={(e) => updateCaptions('segmentation_mode', e.target.value)}
                      disabled={!isCustom}
                    >
                      <option value="by_sentence">문장 단위</option>
                      <option value="by_time">시간 단위</option>
                      <option value="by_breath">호흡 단위</option>
                    </select>
                  </label>
                  <label>
                    <span>줄당 최대 글자 수</span>
                    <input
                      type="range"
                      min={10}
                      max={30}
                      value={editing.captions.max_chars_per_line}
                      onChange={(e) => updateCaptions('max_chars_per_line', Number(e.target.value))}
                      disabled={!isCustom}
                    />
                    <span className="range-value">{editing.captions.max_chars_per_line}자</span>
                  </label>
                  <label>
                    <span>최대 줄 수</span>
                    <select
                      value={editing.captions.max_lines}
                      onChange={(e) => updateCaptions('max_lines', Number(e.target.value))}
                      disabled={!isCustom}
                    >
                      <option value={1}>1줄</option>
                      <option value={2}>2줄</option>
                      <option value={3}>3줄</option>
                    </select>
                  </label>
                </div>
              </section>

              {/* Pacing Settings */}
              <section className="editor-section">
                <h3>페이싱</h3>
                <div className="editor-grid">
                  <label>
                    <span>목표 속도 (WPM)</span>
                    <input
                      type="range"
                      min={80}
                      max={250}
                      step={5}
                      value={editing.pacing.target_tempo}
                      onChange={(e) => updatePacing('target_tempo', Number(e.target.value))}
                      disabled={!isCustom}
                    />
                    <span className="range-value">{editing.pacing.target_tempo} WPM</span>
                  </label>
                  <label>
                    <span>자연스러움 최소 점수</span>
                    <input
                      type="range"
                      min={0}
                      max={1}
                      step={0.05}
                      value={editing.pacing.naturalness_score_min}
                      onChange={(e) => updatePacing('naturalness_score_min', Number(e.target.value))}
                      disabled={!isCustom}
                    />
                    <span className="range-value">{editing.pacing.naturalness_score_min}</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={editing.pacing.allow_jump_cuts}
                      onChange={(e) => updatePacing('allow_jump_cuts', e.target.checked)}
                      disabled={!isCustom}
                    />
                    <span>점프컷 허용</span>
                  </label>
                </div>
              </section>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: 14 }}>
              프리셋을 선택하거나 새로 만드세요
            </div>
          )}
        </div>
      </div>
    </>
  );
}
