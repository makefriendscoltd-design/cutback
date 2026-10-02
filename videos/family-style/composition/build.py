"""Generate HyperFrames HTML from the measured style and an optional clean-source episode.

No network, TTS, publishing, or renderer invocation occurs in this builder.
"""
import argparse
import html
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(path):
    return json.loads(Path(path).read_text())


def esc(value):
    return html.escape(str(value), quote=True)


def box(values):
    x, y, w, h = values
    return f"left:{x}px;top:{y}px;width:{w}px;height:{h}px"


def media(path):
    resolved = (ROOT / path).resolve()
    if not resolved.is_file():
        raise ValueError(f"Missing media: {path}")
    if not resolved.is_relative_to(ROOT):
        raise ValueError("Copy episode assets into the composition before building")
    return esc(path)


def media_duration(path):
    media(path)
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                             'format=duration', '-of', 'json', str(ROOT / path)],
                            check=True, capture_output=True, text=True)
    return float(json.loads(result.stdout)['format']['duration'])


def build(episode_path=None):
    s = load(ROOT / "style.json")
    episode = load(episode_path) if episode_path else None
    c = s["canvas"]
    duration = episode["duration"] if episode else c["duration"]
    if duration <= 0:
        raise ValueError("Duration must be positive")
    title = episode.get("title", s["title"]["text"]) if episode else s["title"]["text"]
    subtitle = episode.get("subtitle", s["subtitle"]["text"]) if episode else s["subtitle"]["text"]
    nodes = []
    if episode:
        if not episode.get("thread_url") or not episode.get("thread_text"):
            raise ValueError("A new episode requires its source thread URL and exact post text")
        if episode.get("source_has_baked_captions") is not False:
            raise ValueError("A new episode requires an explicitly clean source")
        if not episode.get("script_reviewed"):
            raise ValueError("Review script against source before producing a new episode")
        previous_end = 0.0
        for i, scene in enumerate(episode["scenes"]):
            start, end = scene["start"], scene["end"]
            if abs(start - previous_end) > 1 / c["fps"] or end <= start:
                raise ValueError(f"Scene {i} has a gap, overlap, or invalid range")
            if not scene.get("supports_caption"):
                raise ValueError(f"Scene {i} needs a source-to-script semantic anchor")
            media_start, scene_rate = scene.get('media_start', 0), scene.get('rate', 1)
            if media_start < 0 or scene_rate <= 0:
                raise ValueError(f"Scene {i} has invalid source timing")
            if media_start + (end-start)*scene_rate > media_duration(scene['path']) + 1/c['fps']:
                raise ValueError(f"Scene {i} exceeds its source; choose a real source range")
            previous_end = end
            nodes.append(f'<video id="source-{i}" class="clip panel" src="{media(scene["path"])}" muted playsinline data-start="{start}" data-duration="{end-start}" data-media-start="{scene.get("media_start", 0)}" data-playback-rate="{scene.get("rate", 1)}" data-track-index="1" style="object-fit:contain"></video>')
        if abs(previous_end - duration) > 1 / c["fps"]:
            raise ValueError("Scene coverage must equal episode duration")
        voice = episode["voice"]
        rate = 1 if voice.get("already_speed_adjusted") else s["voice"]["render_speed"]
        voice_path = voice["path"]
        actual_duration = media_duration(voice_path) / rate
        if abs(actual_duration-duration) > max(.06, 2/c['fps']):
            raise ValueError(f"Episode duration {duration}s does not match retimed voice {actual_duration:.3f}s")
        captions = episode["captions"]
        timebase = episode["caption_timebase"]
        if timebase not in ("raw_voice_seconds", "output_seconds"):
            raise ValueError("Caption timebase must be explicit")
        prev = 0
        for i, cap in enumerate(captions):
            # Raw voice timing is divided exactly once, independent of whether the
            # waveform has already been sped up in a preprocessing step.
            divisor = s["voice"]["render_speed"] if timebase == "raw_voice_seconds" else 1
            start, end = cap["start"] / divisor, cap["end"] / divisor
            if start < prev - 1e-6 or end <= start or end > duration + 1 / c["fps"]:
                raise ValueError(f"Invalid caption timing at {i}")
            prev = end
            nodes.append(f'<div id="caption-{i}" class="clip caption" data-start="{start:.6f}" data-duration="{end-start:.6f}" data-track-index="3"><span>{esc(cap["text"])}</span></div>')
    else:
        nodes.append(f'<video id="reference-panel" class="clip panel" src="{media(s["panel"]["path"])}" muted playsinline data-start="0" data-duration="{duration}" data-track-index="1"></video>')
        voice_path, rate = s["voice"]["path"], 1
    t, sub, cap, avatar = s["title"], s["subtitle"], s["captions"], s["avatar"]
    avatar_path = episode.get('avatar_path', avatar['path']) if episode else avatar['path']
    # Explicit finite clip windows keep framework seeking deterministic when a
    # new narration is longer than the reusable presenter loop.
    loop_length = media_duration(avatar_path)
    if loop_length <= 0:
        raise ValueError('Avatar media has no duration')
    at, number = 0.0, 0
    while at < duration - 1e-6:
        length = min(loop_length, duration-at)
        nodes.append(f'<video id="avatar-{number}" class="clip avatar" src="{media(avatar_path)}" muted playsinline data-start="{at}" data-duration="{length}" data-media-start="0" data-track-index="6"></video>')
        at += length
        number += 1
    nodes.extend([
        f'<div id="title" class="clip title" data-start="0" data-duration="{duration}" data-track-index="4"><span>{esc(title)}</span></div>',
        f'<div id="subtitle" class="clip subtitle" data-start="0" data-duration="{duration}" data-track-index="5"><span>{esc(subtitle)}</span></div>',
        f'<audio id="narration" class="clip" src="{media(voice_path)}" data-start="0" data-duration="{duration}" data-playback-rate="{rate}" data-track-index="2"></audio>',
    ])
    out = f'''<!doctype html>
<html lang="ko" data-resolution="portrait-4k"><head>
<meta charset="utf-8"><meta name="viewport" content="width={c['width']}, height={c['height']}">
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:AggroBold;src:url('assets/fonts/{t['font']}');font-weight:700}}
@font-face{{font-family:AggroMedium;src:url('assets/fonts/{sub['font']}');font-weight:500}}
@font-face{{font-family:SCoreDream;src:url('assets/fonts/{cap['font']}');font-weight:500}}
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:{c['width']}px;height:{c['height']}px;overflow:hidden;background:{c['background']}}}
#root{{width:100%;height:100%;position:relative;background:{c['background']}}}
.clip{{position:absolute}}.panel{{{box(s['panel']['box'])};object-fit:fill;z-index:1}}
.title{{{box(t['box'])};background:#fff;display:flex;justify-content:center;align-items:center;z-index:4}}
.title span{{font-family:AggroBold;font-size:{t['font_size']}px;font-weight:700;line-height:1;white-space:nowrap;color:{t['color']};transform:translateY({t.get('glyph_offset_y',0)}px);display:block}}
.subtitle{{{box(sub['box'])};display:flex;justify-content:center;align-items:center;z-index:4}}
.subtitle span{{font-family:AggroMedium;font-size:{sub['font_size']}px;font-weight:500;line-height:1;white-space:nowrap;color:{sub['color']};display:block}}
.caption{{left:0;top:{cap['center'][1]-cap['font_size']}px;width:100%;height:{cap['font_size']*2}px;display:flex;align-items:center;justify-content:center;z-index:3}}
.caption span{{font-family:SCoreDream;font-size:{cap['font_size']}px;font-weight:{cap['weight']};line-height:1.3;white-space:nowrap;color:{cap['color']};max-width:{cap['max_width']}px;text-shadow:{','.join('0 0 '+str(b)+'px '+cap['shadow']['color'] for b in cap['shadow'].get('layers_px',[cap['shadow']['blur'],cap['shadow']['blur']/2]))};display:block}}
.avatar{{{box(avatar['box'])};border-radius:50%;object-fit:cover;z-index:5}}
</style></head><body>
<div id="root" data-composition-id="family" data-width="{c['width']}" data-height="{c['height']}" data-duration="{duration}" data-fps="{c['fps']}">
{''.join(nodes)}
</div><script>
const tl=gsap.timeline({{paused:true}});
window.__timelines['family']=tl;
</script></body></html>'''
    (ROOT / "index.html").write_text(out)
    print(f"Built {'clean episode' if episode else 'reference reconstruction (baked source captions)'}: {duration}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--episode", type=Path)
    args = parser.parse_args()
    ROOT = args.project.resolve()
    build(args.episode)
