import { CutDecision, Caption, createLogger } from '@cutback/shared';
import fs from 'fs/promises';
import fsSync from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { generateSRT } from './srt-generator';

const logger = createLogger('capcut-project');

/**
 * CapCut Desktop draft_content.json 생성기
 *
 * 실제 CapCut Desktop 프로젝트 파일 구조를 정확히 복제하여
 * CapCut에서 직접 인식할 수 있는 프로젝트를 생성.
 */

interface CapCutProjectOptions {
  videoPath: string;
  videoDuration: number; // microseconds
  width?: number;
  height?: number;
  fps?: number;
}

// CapCut uses microseconds (1s = 1,000,000)
const MICRO = 1_000_000;

function secToMicro(sec: number): number {
  return Math.round(sec * MICRO);
}

function genId(): string {
  return uuidv4().toUpperCase();
}

// ─── Helper: Video Material ─────────────────────────────────────────

function createVideoMaterial(
  id: string,
  videoPath: string,
  duration: number,
  width: number,
  height: number
): Record<string, unknown> {
  return {
    aigc_history_id: '',
    aigc_item_id: '',
    aigc_type: 'none',
    audio_fade: null,
    beauty_body_auto_preset: null,
    beauty_body_preset_id: '',
    beauty_face_auto_preset: { name: '', preset_id: '', rate_map: '', scene: '' },
    beauty_face_auto_preset_infos: [],
    beauty_face_preset_infos: [],
    cartoon_path: '',
    category_id: '',
    category_name: '',
    check_flag: 62978047,
    content_feature_info: null,
    corner_pin: null,
    crop: {
      lower_left_x: 0.0, lower_left_y: 1.0,
      lower_right_x: 1.0, lower_right_y: 1.0,
      upper_left_x: 0.0, upper_left_y: 0.0,
      upper_right_x: 1.0, upper_right_y: 0.0,
    },
    crop_ratio: 'free',
    crop_scale: 1.0,
    duration,
    extra_type_option: 0,
    formula_id: '',
    freeze: null,
    has_audio: true,
    has_sound_separated: false,
    height,
    id,
    intensifies_audio_path: '',
    intensifies_path: '',
    is_ai_generate_content: false,
    is_copyright: false,
    is_text_edit_overdub: false,
    is_unified_beauty_mode: false,
    live_photo_cover_path: '',
    live_photo_timestamp: -1,
    local_id: '',
    local_material_from: '',
    local_material_id: '',
    material_id: '',
    material_name: path.basename(videoPath),
    material_url: '',
    matting: {
      custom_matting_id: '',
      enable_matting_stroke: false,
      expansion: 0,
      feather: 0,
      flag: 0,
      has_use_quick_brush: false,
      has_use_quick_eraser: false,
      interactiveTime: [],
      path: '',
      reverse: false,
      strokes: [],
    },
    media_path: '',
    multi_camera_info: null,
    object_locked: null,
    origin_material_id: '',
    path: videoPath,
    picture_from: 'none',
    picture_set_category_id: '',
    picture_set_category_name: '',
    request_id: '',
    reverse_intensifies_path: '',
    reverse_path: '',
    smart_match_info: null,
    smart_motion: null,
    source: 0,
    source_platform: 0,
    stable: { matrix_path: '', stable_level: 0, time_range: { duration: 0, start: 0 } },
    team_id: '',
    type: 'video',
    video_algorithm: {
      ai_background_configs: [],
      ai_expression_driven: null,
      ai_in_painting_config: [],
      ai_motion_driven: null,
      aigc_generate: null,
      aigc_generate_list: [],
      algorithms: [],
      complement_frame_config: null,
      deflicker: null,
      gameplay_configs: [],
      image_interpretation: null,
      motion_blur_config: null,
      mouth_shape_driver: null,
      noise_reduction: null,
      path: '',
      quality_enhance: null,
      skip_algorithm_index: [],
      smart_complement_frame: null,
      story_video_modify_video_config: { is_overwrite_last_video: false, task_id: '', tracker_task_id: '' },
      super_resolution: null,
      time_range: { duration, start: 0 },
    },
    video_mask_shadow: {
      alpha: 0.0, angle: 0.0, blur: 0.0, color: '', distance: 0.0, path: '', resource_id: '',
    },
    video_mask_stroke: {
      alpha: 0.0, color: '', distance: 0.0, horizontal_shift: 0.0,
      path: '', resource_id: '', size: 0.0, texture: 0.0, type: '', vertical_shift: 0.0,
    },
    width,
  };
}

// ─── Helper: Video Segment ──────────────────────────────────────────

function createVideoSegment(
  segmentId: string,
  materialId: string,
  sourceStart: number,
  sourceDuration: number,
  targetStart: number,
  targetDuration: number,
  extraMaterialRefs: string[]
): Record<string, unknown> {
  return {
    caption_info: null,
    cartoon: false,
    clip: {
      alpha: 1.0,
      flip: { horizontal: false, vertical: false },
      rotation: 0.0,
      scale: { x: 1.0, y: 1.0 },
      transform: { x: 0.0, y: 0.0 },
    },
    color_correct_alg_result: '',
    common_keyframes: [],
    desc: '',
    digital_human_template_group_id: '',
    enable_adjust: true,
    enable_adjust_mask: false,
    enable_color_correct_adjust: false,
    enable_color_curves: true,
    enable_color_match_adjust: false,
    enable_color_wheels: true,
    enable_hsl: false,
    enable_hsl_curves: true,
    enable_lut: true,
    enable_mask_shadow: false,
    enable_mask_stroke: false,
    enable_smart_color_adjust: false,
    enable_video_mask: true,
    extra_material_refs: extraMaterialRefs,
    group_id: '',
    hdr_settings: { intensity: 1.0, mode: 1, nits: 1000 },
    id: segmentId,
    intensifies_audio: false,
    is_loop: false,
    is_placeholder: false,
    is_tone_modify: false,
    keyframe_refs: [],
    last_nonzero_volume: 1.0,
    lyric_keyframes: null,
    material_id: materialId,
    raw_segment_id: '',
    render_index: 0,
    render_timerange: { duration: 0, start: 0 },
    responsive_layout: {
      enable: false,
      horizontal_pos_layout: 0,
      size_layout: 0,
      target_follow: '',
      vertical_pos_layout: 0,
    },
    reverse: false,
    source: 'segmentsourcenormal',
    source_timerange: { duration: sourceDuration, start: sourceStart },
    speed: 1.0,
    state: 0,
    target_timerange: { duration: targetDuration, start: targetStart },
    template_id: '',
    template_scene: 'default',
    track_attribute: 0,
    track_render_index: 0,
    uniform_scale: { on: true, value: 1.0 },
    visible: true,
    volume: 1.0,
  };
}

// ─── Helper: Text Material ──────────────────────────────────────────

function createTextMaterial(
  id: string,
  text: string,
  fontSize: number = 15.0,
  fontName: string = 'Pretendard'
): Record<string, unknown> {
  // 텍스트 길이에 비례하여 배경 너비 계산 (글자당 약 0.025)
  // CapCut의 background_width는 0~1 범위 (캔버스 비율)
  const charCount = Math.max(text.length, 4);
  const bgWidth = Math.min(0.95, 0.06 + charCount * 0.025);
  const bgHeight = 0.06; // 한 줄 자막 기준

  const contentJson = JSON.stringify({
    text,
    styles: [{
      fill: { content: { render_type: 'solid', solid: { color: [1, 1, 1] } } },
      font: { path: '', id: '' },
      size: fontSize,
      range: [0, text.length],
    }],
  });

  return {
    add_type: 0,
    alignment: 1,
    background_alpha: 1.0,
    background_color: '#000000',
    background_fill: '',
    background_height: bgHeight,
    background_horizontal_offset: 0.0,
    background_round_radius: 0.0,
    background_style: 1, // 1 = solid background 활성화
    background_vertical_offset: 0.0,
    background_width: bgWidth,
    base_content: '',
    bold_width: 0.0,
    border_alpha: 1.0,
    border_color: '',
    border_mode: 0,
    border_width: 0.08,
    caption_template_info: {
      category_id: '', category_name: '', effect_id: '', is_new: false,
      path: '', request_id: '', resource_id: '', resource_name: '',
      source_platform: 0, third_resource_id: '',
    },
    check_flag: 7,
    combo_info: { text_templates: [] },
    content: contentJson,
    current_words: { end_time: [], start_time: [], text: [] },
    cutoff_postfix: '',
    enable_path_typesetting: false,
    fixed_height: -1.0,
    fixed_width: -1.0,
    font_category_id: '',
    font_category_name: '',
    font_id: '',
    font_name: fontName,
    font_path: '',
    font_resource_id: '',
    font_size: fontSize,
    font_source_platform: 0,
    font_team_id: '',
    font_third_resource_id: '',
    font_title: fontName,
    font_url: '',
    fonts: [],
    force_apply_line_max_width: false,
    global_alpha: 1.0,
    group_id: '',
    has_shadow: false,
    id,
    initial_scale: 1.0,
    inner_padding: -1.0,
    is_batch_replace: false,
    is_lyric_effect: false,
    is_rich_text: false,
    is_words_linear: false,
    italic_degree: 0,
    ktv_color: '',
    language: '',
    layer_weight: 1,
    letter_spacing: 0.0,
    line_feed: 1,
    line_max_width: 0.82,
    line_spacing: 0.02,
    lyric_group_id: '',
    lyrics_template: {
      category_id: '', category_name: '', effect_id: '',
      panel: '', path: '', request_id: '', resource_id: '', resource_name: '',
    },
    multi_language_current: 'none',
    name: '',
    offset_on_path: 0.0,
    oneline_cutoff: false,
    operation_type: 0,
    original_size: [],
    preset_category: '',
    preset_category_id: '',
    preset_has_set_alignment: false,
    preset_id: '',
    preset_index: 0,
    preset_name: '',
    punc_model: '',
    recognize_model: '',
    recognize_task_id: '',
    recognize_text: '',
    recognize_type: 0,
    relevance_segment: [],
    shadow_alpha: 0.9,
    shadow_angle: -45.0,
    shadow_color: '',
    shadow_distance: 5.0,
    shadow_point: { x: 0.6363961030678928, y: -0.6363961030678928 },
    shadow_smoothing: 0.45,
    shape_clip_x: false,
    shape_clip_y: false,
    source_from: '',
    ssml_content: '',
    style_name: '',
    sub_template_id: -1,
    sub_type: 0,
    subtitle_keywords: null,
    subtitle_keywords_config: null,
    subtitle_template_original_fontsize: 0.0,
    text_alpha: 1.0,
    text_color: '#FFFFFF',
    text_curve: null,
    text_exceeds_path_process_type: 0,
    text_loop_on_path: false,
    text_preset_resource_id: '',
    text_size: 30,
    text_to_audio_ids: [],
    text_typesetting_path_index: 0,
    text_typesetting_paths: null,
    text_typesetting_paths_file: '',
    translate_original_text: '',
    tts_auto_update: false,
    type: 'text',
    typesetting: 0,
    underline: false,
    underline_offset: 0.22,
    underline_width: 0.05,
    use_effect_default_color: true,
    words: { end_time: [], start_time: [], text: [] },
  };
}

// ─── Helper: Text Segment ───────────────────────────────────────────

function createTextSegment(
  segmentId: string,
  materialId: string,
  targetStart: number,
  targetDuration: number,
  animationRef: string,
  trackRenderIndex: number = 1
): Record<string, unknown> {
  return {
    caption_info: null,
    cartoon: false,
    clip: {
      alpha: 1.0,
      flip: { horizontal: false, vertical: false },
      rotation: 0.0,
      scale: { x: 1.0, y: 1.0 },
      // y: -0.75 = 화면 하단 부근 (CapCut 좌표계: 위=+1, 아래=-1, 중앙=0)
      transform: { x: 0.0, y: -0.75 },
    },
    color_correct_alg_result: '',
    common_keyframes: [],
    desc: '',
    digital_human_template_group_id: '',
    enable_adjust: false,
    enable_adjust_mask: false,
    enable_color_correct_adjust: false,
    enable_color_curves: true,
    enable_color_match_adjust: false,
    enable_color_wheels: true,
    enable_hsl: false,
    enable_hsl_curves: true,
    enable_lut: false,
    enable_mask_shadow: false,
    enable_mask_stroke: false,
    enable_smart_color_adjust: false,
    enable_video_mask: true,
    extra_material_refs: [animationRef],
    group_id: '',
    hdr_settings: null,
    id: segmentId,
    intensifies_audio: false,
    is_loop: false,
    is_placeholder: false,
    is_tone_modify: false,
    keyframe_refs: [],
    last_nonzero_volume: 1.0,
    lyric_keyframes: null,
    material_id: materialId,
    raw_segment_id: '',
    render_index: 14000,
    render_timerange: { duration: 0, start: 0 },
    responsive_layout: {
      enable: false,
      horizontal_pos_layout: 0,
      size_layout: 0,
      target_follow: '',
      vertical_pos_layout: 0,
    },
    reverse: false,
    source: 'segmentsourcenormal',
    source_timerange: null,
    speed: 1.0,
    state: 0,
    target_timerange: { duration: targetDuration, start: targetStart },
    template_id: '',
    template_scene: 'default',
    track_attribute: 0,
    track_render_index: trackRenderIndex,
    uniform_scale: { on: true, value: 1.0 },
    visible: true,
    volume: 1.0,
  };
}

// ─── Audio Fade (boundary smoothing) ────────────────────────────────

/**
 * 컷 경계마다 짧은 audio fade 를 넣어 클릭/톤 단절 완화.
 *
 * - 영상 처음/끝 경계 → fade 없음 (원본 그대로 시작/끝)
 * - filler 경계 → 6ms (타이트하게, 호흡 안 끊기)
 * - silence 경계 → 12ms (자연스러운 톤 전환)
 * - retake 경계 → 25ms (불연속을 더 적극적으로 마스킹)
 *
 * 모든 값은 CapCut 의 audio_fade material 로 기록되어
 * 사용자가 CapCut 에서 다시 조정 가능.
 */
const FADE_BY_CUT_TYPE_MS: Record<string, number> = {
  filler_word: 6,
  silence: 12,
  retake: 25,
};

function fadeMsForCutType(cutType: string | null): number {
  if (!cutType) return 0;
  return FADE_BY_CUT_TYPE_MS[cutType] ?? 10;
}

function createAudioFadeMaterial(
  id: string,
  fadeInUs: number,
  fadeOutUs: number
): Record<string, unknown> {
  return {
    fade_in_duration: fadeInUs,
    fade_out_duration: fadeOutUs,
    fade_type: 0,
    id,
    type: 'audio_fade',
  };
}

// ─── Helper: Extra Materials per Segment ────────────────────────────

interface SegmentExtraMaterials {
  speedId: string;
  placeholderId: string;
  animationId: string;
  soundChannelId: string;
  materialColorId: string;
  vocalSepId: string;
  audioFadeId: string;
}

function createSegmentExtraMaterials(): SegmentExtraMaterials {
  return {
    speedId: genId(),
    placeholderId: genId(),
    animationId: genId(),
    soundChannelId: genId(),
    materialColorId: genId(),
    vocalSepId: genId(),
    audioFadeId: genId(),
  };
}

function pushExtraMaterialsToArrays(
  extras: SegmentExtraMaterials,
  arrays: {
    speeds: Record<string, unknown>[];
    placeholderInfos: Record<string, unknown>[];
    materialAnimations: Record<string, unknown>[];
    soundChannelMappings: Record<string, unknown>[];
    materialColors: Record<string, unknown>[];
    vocalSeparations: Record<string, unknown>[];
    audioFades: Record<string, unknown>[];
  },
  fadeInMs: number,
  fadeOutMs: number
): void {
  arrays.speeds.push({
    curve_speed: null,
    id: extras.speedId,
    mode: 0,
    speed: 1.0,
    type: 'speed',
  });
  arrays.placeholderInfos.push({
    error_path: '',
    error_text: '',
    id: extras.placeholderId,
    meta_type: 'none',
    res_path: '',
    res_text: '',
    type: 'placeholder_info',
  });
  arrays.materialAnimations.push({
    animations: [],
    id: extras.animationId,
    multi_language_current: 'none',
    type: 'sticker_animation',
  });
  arrays.soundChannelMappings.push({
    audio_channel_mapping: 0,
    id: extras.soundChannelId,
    is_config_open: false,
    type: '',
  });
  arrays.materialColors.push({
    gradient_angle: 90.0,
    gradient_colors: [],
    gradient_percents: [],
    height: 0.0,
    id: extras.materialColorId,
    is_color_clip: false,
    is_gradient: false,
    solid_color: '',
    width: 0.0,
  });
  arrays.vocalSeparations.push({
    choice: 0,
    enter_from: '',
    final_algorithm: '',
    id: extras.vocalSepId,
    production_path: '',
    removed_sounds: [],
    time_range: null,
    type: 'vocal_separation',
  });
  arrays.audioFades.push(
    createAudioFadeMaterial(
      extras.audioFadeId,
      Math.round(fadeInMs * 1000), // ms → microseconds
      Math.round(fadeOutMs * 1000)
    )
  );
}

// ─── Main: Generate CapCut Project ──────────────────────────────────

/**
 * CapCut draft_content.json 생성
 * 실제 CapCut Desktop v7.8+ 포맷에 맞춤
 */
export function generateCapCutProject(
  cutDecisions: CutDecision[],
  captions: Caption[],
  options: CapCutProjectOptions
): Record<string, unknown> {
  const {
    videoPath,
    videoDuration,
    width = 1920,
    height = 1080,
    fps = 30,
  } = options;

  const enabledCuts = cutDecisions
    .filter((c) => c.enabled)
    .sort((a, b) => a.start - b.start);

  // 유지할 구간 계산 (컷 사이의 구간)
  // 각 segment 의 좌/우 경계에 어떤 cut 타입이 있는지 함께 기록 → audio fade 결정에 사용.
  // - cutTypeBefore: 이 segment 직전에 잘려나간 cut 의 type (없으면 null = 영상 처음)
  // - cutTypeAfter:  이 segment 직후에 잘려나간 cut 의 type (없으면 null = 영상 끝)
  type KeepSegment = {
    start: number;
    end: number;
    cutTypeBefore: CutDecision['type'] | null;
    cutTypeAfter: CutDecision['type'] | null;
  };
  const keepSegments: KeepSegment[] = [];
  let cursor = 0;
  let prevCutType: CutDecision['type'] | null = null;
  const totalDurationSec = videoDuration / MICRO;

  for (const cut of enabledCuts) {
    if (cut.start > cursor) {
      keepSegments.push({
        start: cursor,
        end: cut.start,
        cutTypeBefore: prevCutType,
        cutTypeAfter: cut.type,
      });
    } else if (keepSegments.length > 0) {
      // 직전 segment 의 cutTypeAfter 가 빈 cut (cursor==cut.start) 이었다면 보정
      keepSegments[keepSegments.length - 1].cutTypeAfter = cut.type;
    }
    cursor = Math.max(cursor, cut.end);
    prevCutType = cut.type;
  }
  if (cursor < totalDurationSec) {
    keepSegments.push({
      start: cursor,
      end: totalDurationSec,
      cutTypeBefore: prevCutType,
      cutTypeAfter: null,
    });
  }

  // IDs
  const draftId = genId();
  const videoMaterialId = genId();
  const canvasMaterialId = genId();

  // Extra material arrays (video segments 마다 하나씩)
  const materialArrays = {
    speeds: [] as Record<string, unknown>[],
    placeholderInfos: [] as Record<string, unknown>[],
    materialAnimations: [] as Record<string, unknown>[],
    soundChannelMappings: [] as Record<string, unknown>[],
    materialColors: [] as Record<string, unknown>[],
    vocalSeparations: [] as Record<string, unknown>[],
    audioFades: [] as Record<string, unknown>[],
  };

  // Video segments 생성
  const videoSegments: Record<string, unknown>[] = [];
  let targetCursor = 0;

  for (const seg of keepSegments) {
    const extras = createSegmentExtraMaterials();
    // 좌/우 경계의 cut 타입에 따라 audio fade 길이 결정
    const fadeInMs = fadeMsForCutType(seg.cutTypeBefore);
    const fadeOutMs = fadeMsForCutType(seg.cutTypeAfter);
    pushExtraMaterialsToArrays(extras, materialArrays, fadeInMs, fadeOutMs);

    const duration = secToMicro(seg.end - seg.start);
    const extraRefs = [
      extras.speedId,
      extras.placeholderId,
      canvasMaterialId,
      extras.animationId,
      extras.soundChannelId,
      extras.materialColorId,
      extras.vocalSepId,
      extras.audioFadeId,
    ];

    videoSegments.push(
      createVideoSegment(
        genId(), videoMaterialId,
        secToMicro(seg.start), duration,
        targetCursor, duration,
        extraRefs
      )
    );
    targetCursor += duration;
  }

  // Text materials & segments (자막)
  const textMaterials: Record<string, unknown>[] = [];
  const textSegmentList: Record<string, unknown>[] = [];
  const textAnimations: Record<string, unknown>[] = [];

  for (const cap of captions) {
    const textMatId = genId();
    const textAnimId = genId();
    const duration = secToMicro(cap.end - cap.start);

    textAnimations.push({
      animations: [],
      id: textAnimId,
      multi_language_current: 'none',
      type: 'sticker_animation',
    });

    // 사용자 요구: 폰트 Pretendard, 크기 15, 검정 배경 고정
    textMaterials.push(createTextMaterial(textMatId, cap.text, 15.0, 'Pretendard'));
    textSegmentList.push(
      createTextSegment(genId(), textMatId, secToMicro(cap.start), duration, textAnimId)
    );
  }

  // Platform info
  const platformInfo = {
    app_id: 359289,
    app_source: 'cc',
    app_version: '7.8.0',
    device_id: genId().replace(/-/g, '').toLowerCase(),
    hard_disk_id: genId().replace(/-/g, '').toLowerCase(),
    mac_address: genId().replace(/-/g, '').toLowerCase().slice(0, 32),
    os: 'windows',
    os_version: '10.0.19045',
  };

  // Tracks
  const tracks: Record<string, unknown>[] = [
    {
      attribute: 0,
      flag: 0,
      id: genId(),
      is_default_name: true,
      name: '',
      segments: videoSegments,
      type: 'video',
    },
  ];

  if (textSegmentList.length > 0) {
    tracks.push({
      attribute: 0,
      flag: 0,
      id: genId(),
      is_default_name: true,
      name: '',
      segments: textSegmentList,
      type: 'text',
    });
  }

  // All material animations (video + text)
  const allAnimations = [...materialArrays.materialAnimations, ...textAnimations];

  // ─── Full Draft Object ────────────────────────────────────────────
  const draft: Record<string, unknown> = {
    canvas_config: {
      background: null,
      height,
      ratio: 'original',
      width,
    },
    color_space: -1,
    config: {
      adjust_max_index: 1,
      attachment_info: [],
      combination_max_index: 1,
      export_range: null,
      extract_audio_last_index: 1,
      lyrics_recognition_id: '',
      lyrics_sync: true,
      lyrics_taskinfo: [],
      maintrack_adsorb: true,
      material_save_mode: 0,
      multi_language_current: 'none',
      multi_language_list: [],
      multi_language_main: 'none',
      multi_language_mode: 'none',
      original_sound_last_index: 1,
      record_audio_last_index: 1,
      sticker_max_index: 1,
      subtitle_keywords_config: null,
      subtitle_recognition_id: '',
      subtitle_sync: true,
      subtitle_taskinfo: [],
      system_font_list: [],
      use_float_render: false,
      video_mute: false,
      zoom_info_params: null,
    },
    cover: null,
    create_time: 0,
    draft_type: 'video',
    duration: targetCursor,
    extra_info: null,
    fps: fps * 1.0,
    free_render_index_mode_on: false,
    function_assistant_info: {
      audio_noise_segid_list: [],
      auto_adjust: false,
      auto_adjust_fixed: false,
      auto_adjust_fixed_value: 50.0,
      auto_adjust_segid_list: [],
      auto_caption: false,
      auto_caption_segid_list: [],
      auto_caption_template_id: '',
      caption_opt: false,
      caption_opt_segid_list: [],
      color_correction: false,
      color_correction_fixed: false,
      color_correction_fixed_value: 50.0,
      color_correction_segid_list: [],
      deflicker_segid_list: [],
      enhance_quality: false,
      enhance_quality_fixed: false,
      enhance_quality_segid_list: [],
      enhance_voice_segid_list: [],
      enhande_voice: false,
      enhande_voice_fixed: false,
      eye_correction: false,
      eye_correction_segid_list: [],
      fixed_rec_applied: false,
      fps: { den: 1, num: 0 },
      normalize_loudness: false,
      normalize_loudness_audio_denoise_segid_list: [],
      normalize_loudness_fixed: false,
      normalize_loudness_segid_list: [],
      retouch: false,
      retouch_fixed: false,
      retouch_segid_list: [],
      smart_rec_applied: false,
      smart_segid_list: [],
      smooth_slow_motion: false,
      smooth_slow_motion_fixed: false,
      video_noise_segid_list: [],
    },
    group_container: null,
    id: draftId,
    is_drop_frame_timecode: false,
    keyframe_graph_list: [],
    keyframes: {
      adjusts: [],
      audios: [],
      effects: [],
      filters: [],
      handwrites: [],
      stickers: [],
      texts: [],
      videos: [],
    },
    last_modified_platform: platformInfo,
    lyrics_effects: [],
    materials: {
      ai_translates: [],
      audio_balances: [],
      audio_effects: [],
      audio_fades: materialArrays.audioFades,
      audio_pannings: [],
      audio_pitch_shifts: [],
      audio_track_indexes: [],
      audios: [],
      beats: [],
      canvases: [{
        album_image: '',
        blur: 0.0,
        color: '',
        id: canvasMaterialId,
        image: '',
        image_id: '',
        image_name: '',
        source_platform: 0,
        team_id: '',
        type: 'canvas_color',
      }],
      chromas: [],
      color_curves: [],
      common_mask: [],
      digital_human_model_dressing: [],
      digital_humans: [],
      drafts: [],
      effects: [],
      flowers: [],
      green_screens: [],
      handwrites: [],
      hsl: [],
      hsl_curves: [],
      images: [],
      log_color_wheels: [],
      loudnesses: [],
      manual_beautys: [],
      manual_deformations: [],
      material_animations: allAnimations,
      material_colors: materialArrays.materialColors,
      multi_language_refs: [],
      placeholder_infos: materialArrays.placeholderInfos,
      placeholders: [],
      plugin_effects: [],
      primary_color_wheels: [],
      realtime_denoises: [],
      shapes: [],
      smart_crops: [],
      smart_relights: [],
      sound_channel_mappings: materialArrays.soundChannelMappings,
      speeds: materialArrays.speeds,
      stickers: [],
      tail_leaders: [],
      text_templates: [],
      texts: textMaterials,
      time_marks: [],
      transitions: [],
      video_effects: [],
      video_radius: [],
      video_shadows: [],
      video_strokes: [],
      video_trackings: [],
      videos: [createVideoMaterial(videoMaterialId, videoPath, videoDuration, width, height)],
      vocal_beautifys: [],
      vocal_separations: materialArrays.vocalSeparations,
    },
    mutable_config: null,
    name: '',
    new_version: '153.0.0',
    path: '',
    platform: platformInfo,
    relationships: [],
    render_index_track_mode_on: true,
    retouch_cover: null,
    smart_ads_info: { draft_url: '', page_from: '', routine: '' },
    source: 'default',
    static_cover_image_path: '',
    time_marks: null,
    tracks,
    uneven_animation_template_info: {
      composition: '',
      content: '',
      order: '',
      sub_template_info_list: [],
    },
    update_time: 0,
    version: 360000,
  };

  logger.info('CapCut project generated', {
    videoSegments: videoSegments.length,
    textSegments: textSegmentList.length,
    duration: targetCursor,
  });

  return draft;
}

// ─── Save (수동 경로) ───────────────────────────────────────────────

export async function saveCapCutProject(
  cutDecisions: CutDecision[],
  captions: Caption[],
  outputPath: string,
  options: CapCutProjectOptions
): Promise<void> {
  const project = generateCapCutProject(cutDecisions, captions, options);
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, JSON.stringify(project, null, 2), 'utf-8');
  logger.info('CapCut project saved', { path: outputPath });
}

// ─── CapCut Drafts 폴더 탐지 ────────────────────────────────────────

/**
 * 탐색 대상 CapCut 드래프트 폴더 후보 목록.
 *
 * 버전에 따라 위치가 다르다:
 *   - 구버전:  %LOCALAPPDATA%\CapCut Drafts
 *   - 최신:    %LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft
 *   - 중국판:  JianyingPro
 *
 * Local 과 Roaming 을 모두 본다. 예전엔 Roaming 쪽 User Data 경로만 있어서,
 * 최신 CapCut 만 깔린 PC 에서 "설치되어 있지 않다" 는 오탐이 났다.
 */
/**
 * CapCut 설정파일(globalSetting)에 기록된 실제 드래프트 폴더 경로.
 *
 * 사용자가 CapCut 설정에서 저장 위치를 바꾸면(예: D:\내드래프트) 우리가 추측하는
 * 기본 경로엔 없지만 여기 `currentCustomDraftPath=...` 로 남는다.
 * 다른 PC 에서 "폴더 못 찾음" 이 나던 주 원인이라, 추측 경로보다 이걸 먼저 본다.
 */
function configuredDraftDirs(): string[] {
  const localAppData =
    process.env.LOCALAPPDATA ||
    (process.env.USERPROFILE
      ? path.join(process.env.USERPROFILE, 'AppData', 'Local')
      : '');
  if (!localAppData) return [];

  const dirs: string[] = [];
  for (const product of ['CapCut', 'JianyingPro']) {
    const settingPath = path.join(
      localAppData,
      product,
      'User Data',
      'Config',
      'globalSetting'
    );
    try {
      const content = fsSync.readFileSync(settingPath, 'utf8');
      const m = /currentCustomDraftPath=(.+)/.exec(content);
      if (m) {
        // 설정값은 백슬래시가 \\ 로 이스케이프돼 있다 → 실제 경로로 복원
        const p = m[1].trim().replace(/\\\\/g, '\\');
        if (p) dirs.push(p);
      }
    } catch {
      // 설정 파일이 없거나 못 읽으면 무시 (추측 경로로 폴백)
    }
  }
  return dirs;
}

export function capCutDraftDirCandidates(): string[] {
  const localAppData =
    process.env.LOCALAPPDATA ||
    (process.env.USERPROFILE
      ? path.join(process.env.USERPROFILE, 'AppData', 'Local')
      : '');
  const appData =
    process.env.APPDATA ||
    (process.env.USERPROFILE
      ? path.join(process.env.USERPROFILE, 'AppData', 'Roaming')
      : '');

  const roots = [localAppData, appData].filter(Boolean);
  const products = ['CapCut', 'JianyingPro'];

  // 설정파일에 적힌 실제 경로를 최우선 후보로
  const candidates: string[] = [...configuredDraftDirs()];
  for (const root of roots) {
    for (const product of products) {
      // 최신 구조
      candidates.push(
        path.join(root, product, 'User Data', 'Projects', 'com.lveditor.draft')
      );
      // 구 구조
      candidates.push(path.join(root, `${product} Drafts`));
    }
  }
  // 중복 제거 (설정 경로가 추측 경로와 겹칠 수 있음)
  return [...new Set(candidates)];
}

export function findCapCutDraftsDir(): string | null {
  for (const p of capCutDraftDirCandidates()) {
    try {
      if (fsSync.statSync(p).isDirectory()) {
        logger.info('CapCut drafts dir found', { path: p });
        return p;
      }
    } catch {
      continue;
    }
  }
  logger.warn('CapCut drafts dir not found', {
    checked: capCutDraftDirCandidates(),
  });
  return null;
}

// ─── CapCut 프로젝트 폴더에 직접 설치 ──────────────────────────────

export async function installToCapCut(
  cutDecisions: CutDecision[],
  captions: Caption[],
  options: CapCutProjectOptions
): Promise<{ projectDir: string; draftsDir: string }> {
  const draftsDir = findCapCutDraftsDir();
  if (!draftsDir) {
    // 어디를 봤는지 알려줘야 사용자가 실제 경로를 찾아 알려줄 수 있다.
    // ("설치되어 있는데 안 된다" 는 신고가 이 정보 없이는 진단 불가)
    throw new Error(
      'CapCut Desktop 프로젝트 폴더를 찾을 수 없습니다.\n' +
        'CapCut 을 한 번이라도 실행해 프로젝트를 만든 적이 있는지 확인해주세요.\n\n' +
        '확인한 경로:\n' +
        capCutDraftDirCandidates()
          .map((p) => `  - ${p}`)
          .join('\n')
    );
  }

  // 자막은 캡컷 프로젝트에 박지 않고 SRT 파일로만 별도 저장한다.
  // (사용자가 캡컷에서 SRT를 import하여 텍스트/스타일을 자유롭게 수정 가능)
  const project = generateCapCutProject(cutDecisions, [], options);
  const draftId = project.id as string;
  const projectName = `Cutback Export - ${path.basename(options.videoPath)}`;
  const projectDir = path.join(draftsDir, draftId);

  await fs.mkdir(projectDir, { recursive: true });

  // draft_content.json
  await fs.writeFile(
    path.join(projectDir, 'draft_content.json'),
    JSON.stringify(project, null, 2),
    'utf-8'
  );

  // draft_meta_info.json — 실제 CapCut 메타 포맷에 맞춤
  const nowMicro = Date.now() * 1000; // microseconds
  const nowSec = Math.floor(Date.now() / 1000);
  const projectDirForward = projectDir.replace(/\\/g, '/');
  const draftsBackslash = draftsDir.replace(/\//g, '\\');

  const metaInfo = {
    cloud_draft_cover: false,
    cloud_draft_sync: false,
    cloud_package_completed_time: '',
    draft_cloud_capcut_purchase_info: '',
    draft_cloud_last_action_download: false,
    draft_cloud_package_type: '',
    draft_cloud_purchase_info: '',
    draft_cloud_template_id: '',
    draft_cloud_tutorial_info: '',
    draft_cloud_videocut_purchase_info: '',
    draft_cover: '',
    draft_deeplink_url: '',
    draft_enterprise_info: {
      draft_enterprise_extra: '',
      draft_enterprise_id: '',
      draft_enterprise_name: '',
      enterprise_material: [],
    },
    draft_fold_path: projectDirForward,
    draft_id: draftId,
    draft_is_ae_produce: false,
    draft_is_ai_packaging_used: false,
    draft_is_ai_shorts: false,
    draft_is_ai_translate: false,
    draft_is_article_video_draft: false,
    draft_is_cloud_temp_draft: false,
    draft_is_from_deeplink: 'false',
    draft_is_invisible: false,
    draft_is_web_article_video: false,
    draft_materials: [
      {
        type: 0,
        value: [{
          ai_group_type: '',
          create_time: nowSec,
          duration: options.videoDuration,
          extra_info: path.basename(options.videoPath),
          file_Path: options.videoPath.replace(/\\/g, '/'),
          height: options.height ?? 1080,
          id: genId().toLowerCase(),
          import_time: nowSec,
          import_time_ms: nowMicro,
          item_source: 1,
          md5: '',
          metetype: 'video',
          roughcut_time_range: { duration: options.videoDuration, start: 0 },
          sub_time_range: { duration: -1, start: -1 },
          type: 0,
          width: options.width ?? 1920,
        }],
      },
      { type: 1, value: [] },
      { type: 2, value: [] },
      { type: 3, value: [] },
      { type: 6, value: [] },
      { type: 7, value: [] },
      { type: 8, value: [] },
    ],
    draft_materials_copied_info: [],
    draft_name: projectName,
    draft_need_rename_folder: false,
    draft_new_version: '',
    draft_removable_storage_device: '',
    draft_root_path: draftsBackslash,
    draft_segment_extra_info: [],
    draft_timeline_materials_size_: 0,
    draft_type: '',
    draft_web_article_video_enter_from: '',
    tm_draft_cloud_completed: '',
    tm_draft_cloud_entry_id: -1,
    tm_draft_cloud_modified: 0,
    tm_draft_cloud_parent_entry_id: -1,
    tm_draft_cloud_space_id: -1,
    tm_draft_cloud_user_id: -1,
    tm_draft_create: nowMicro,
    tm_draft_modified: nowMicro,
    tm_draft_removed: 0,
    tm_duration: project.duration as number,
  };

  await fs.writeFile(
    path.join(projectDir, 'draft_meta_info.json'),
    JSON.stringify(metaInfo, null, 2),
    'utf-8'
  );

  // SRT 자막 파일도 함께 저장 - 사용자가 캡컷에서 직접 import 후 스타일 수정 가능
  if (captions.length > 0) {
    try {
      const srtContent = generateSRT(captions);
      const bom = '\uFEFF';
      await fs.writeFile(
        path.join(projectDir, 'cutback-captions.srt'),
        bom + srtContent,
        'utf-8'
      );
      logger.info('SRT saved alongside CapCut project', { count: captions.length });
    } catch (err) {
      logger.warn('Failed to save SRT', { error: (err as Error).message });
    }
  }

  logger.info('CapCut project installed', { projectDir, projectName });
  return { projectDir, draftsDir };
}
