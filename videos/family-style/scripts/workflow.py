"""Deterministic half of the link-to-short skill. Python >=3.10, ffmpeg, Node.

The Codex skill supplies plan.json after reading the post and source frames.
No shell interpolation, browser UI, agent subprocess or publishing is used.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'composition'))
from voice import captions_from_alignment


def read(p):
    return json.loads(Path(p).read_text())


def save(p, data):
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)


def voice_environment(cfg):
    env = os.environ.copy()
    if env.get('ELEVENLABS_API_KEY'):
        return env
    source = cfg.get('api_key_source')
    if not source:
        raise ValueError('Set ELEVENLABS_API_KEY or a private api_key_source setting')
    # Read only a simple YAML token from an explicitly configured local source.
    # No shell sourcing, YAML object construction, config copying or secret logs.
    section_indent = None
    for raw in Path(source['path']).expanduser().read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        indent, value = len(raw) - len(raw.lstrip()), raw.strip()
        if section_indent is None:
            if value == source['section'] + ':':
                section_indent = indent
            continue
        if indent <= section_indent:
            break
        match = re.fullmatch(re.escape(source['key']) + r'''\s*:\s*['"]?([A-Za-z0-9_-]{20,})['"]?\s*(?:#.*)?''', value)
        if match:
            env['ELEVENLABS_API_KEY'] = match[1]
            return env
    raise ValueError('Configured credential source has no supported simple token; use environment variable')


def probe(p):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams',
                          '-show_format', '-of', 'json', p], capture_output=True, text=True).stdout)


def canonical(url):
    u = urlsplit(url)
    if u.scheme != 'https' or u.hostname not in ('threads.com', 'www.threads.com', 'threads.net', 'www.threads.net'):
        raise ValueError('Use an HTTPS Threads post URL')
    if not re.fullmatch(r'/@[^/]+/post/[A-Za-z0-9_-]+/?', u.path):
        raise ValueError('Use a single Threads post, not an account or feed')
    return 'https://www.threads.com' + u.path.rstrip('/')


def fetch(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(request, timeout=90) as response:
        return response.read()


class Meta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.description = ''
        self.sources = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('property') == 'og:description':
            self.description = a.get('content', '')
        if tag == 'source' and a.get('src'):
            self.sources.append(a['src'])


def prepare(a):
    url = canonical(a.url)
    p = a.project.resolve()
    p.mkdir(parents=True, exist_ok=True)
    manifest = p / 'source.json'
    if manifest.exists():
        old = read(manifest)
        if old['url'] != url:
            raise ValueError('Project already belongs to a different post')
        media = p / 'assets/media/source.mp4'
        if hashlib.sha256(media.read_bytes()).hexdigest() != old['sha256']:
            raise ValueError('Cached source changed; inspect before resuming')
        print('Using verified existing source; no download repeated.')
        return
    parser = Meta()
    parser.feed(fetch(url).decode('utf-8'))
    embed = Meta()
    embed.feed(fetch(url + '/embed').decode('utf-8'))
    # Never save transient CDN URLs or cookie-bearing pages in shared files.
    if not parser.description.strip() or not embed.sources:
        raise ValueError('Public post text/video unavailable; no invented fallback')
    if len(set(embed.sources)) != 1:
        raise ValueError('Multiple source videos: agent must resolve intended source explicitly')
    cdn = urlsplit(embed.sources[0])
    if cdn.scheme != 'https' or not any((cdn.hostname or '').endswith('.' + h) for h in ('cdninstagram.com', 'fbcdn.net')):
        raise ValueError('Unexpected media host')
    media = p / 'assets/media/source.mp4'
    media.parent.mkdir(parents=True, exist_ok=True)
    tmp = media.with_suffix('.part')
    tmp.write_bytes(fetch(embed.sources[0]))
    meta = probe(tmp)
    video = next(s for s in meta['streams'] if s['codec_type'] == 'video')
    if video['width'] <= video['height']:
        raise ValueError('This style expects horizontal source footage')
    tmp.replace(media)
    (p / 'post.txt').write_text(parser.description.strip() + '\n')
    save(manifest, {'url': url, 'sha256': hashlib.sha256(media.read_bytes()).hexdigest(),
                    'duration': float(meta['format']['duration']),
                    'width': video['width'], 'height': video['height']})
    frames = p / 'source-frames'
    frames.mkdir(exist_ok=True)
    run(['ffmpeg', '-v', 'error', '-y', '-i', media, '-vf', 'fps=1/2,scale=640:-2', frames / '%04d.jpg'])
    print(f'Prepared {p}: exact post text and numbered frames (frame 1 ~= 0s, every 2s).')


def configure(a):
    for f in (a.avatar,):
        if not f.is_file():
            raise ValueError(f'Missing asset: {f}')
        probe(f)
    a.config.parent.mkdir(parents=True, exist_ok=True)
    if a.config.exists():
        raise ValueError('Config exists; inspect and edit deliberately instead of overwriting')
    save(a.config, {'avatar': str(a.avatar.resolve()), 'voice_id': a.voice_id})
    a.config.chmod(0o600)
    print('Private asset/voice settings saved; API key remains environment-only.')


def produce(a):
    p = a.project.resolve()
    cfg = read(a.config)
    plan = read(p / 'plan.json')
    source = read(p / 'source.json')
    lines = plan['lines']
    if not lines or not all(isinstance(x, str) and x.strip() and x == x.strip() and '\n' not in x for x in lines):
        raise ValueError('Plan needs caption phrases')
    if not plan.get('review', {}).get('source_checked') or not plan['review'].get('korean_checked'):
        raise ValueError('Agent must record source and Korean-copy checks before TTS')
    if plan.get('source_has_baked_captions') is not False:
        raise ValueError('Inspect source and record baked caption status first')
    # Validate semantic mapping BEFORE spending TTS credits.
    covered = 0
    for scene in plan['scenes']:
        start, end = scene['from_line'], scene['to_line']
        if start != covered or end <= start or end > len(lines) or not scene.get('supports_caption'):
            raise ValueError('Scenes must cover all caption lines exactly once with evidence')
        if not 0 <= scene['media_start'] < scene['media_end'] <= source['duration'] + .001:
            raise ValueError('Source window outside actual footage')
        covered = end
    if covered != len(lines):
        raise ValueError('Scene coverage incomplete')
    for label, max_chars in [('title', 10), ('subtitle', 12)]:
        if not plan.get(label) or len(plan[label].replace(' ', '')) > max_chars:
            raise ValueError(f'{label} too long for reference layout; use a shorter headline')
    style = read(BASE / 'composition/style.json')
    style['voice']['voice_id'] = cfg['voice_id']
    save(p / 'style.json', style)
    assets = p / 'assets'
    shutil.copytree(BASE / 'composition/assets/fonts', assets / 'fonts', dirs_exist_ok=True)
    shutil.copy2(BASE / 'composition/assets/gsap.min.js', assets / 'gsap.min.js')
    shutil.copy2(BASE / 'composition/hyperframes.json', p / 'hyperframes.json')
    avatar = assets / 'media/avatar.mp4'
    shutil.copy2(cfg['avatar'], avatar)
    script = p / 'script.txt'
    script.write_text('\n'.join(lines) + '\n')
    identity = {'text': ' '.join(lines), 'voice_id': cfg['voice_id'], 'model': plan.get('voice_model'), 'speed': 1.0}
    signature = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    voice = assets / 'media' / ('voice-' + signature[:16])
    if not voice.exists():
        env = voice_environment(cfg)
        args = [sys.executable, BASE / 'composition/voice.py', script, '--out', voice,
                '--voice-id', cfg['voice_id'], '--generate']
        if plan.get('voice_model'):
            args += ['--model', plan['voice_model']]
        run(args, env=env)
    # Partial/uncertain provider calls are never automatically repeated.
    metadata = read(voice / 'voice-request.json')
    request = metadata['request']
    if metadata['voice_id'] != identity['voice_id'] or request['text'] != identity['text'] or request.get('model_id') != identity['model']:
        raise ValueError('Voice cache does not match requested script/voice/model')
    if metadata['status'] != 'generated_with_verified_text_alignment':
        raise ValueError('Incomplete take: inspect existing audio/alignment; do not bill a retry blindly')
    raw = captions_from_alignment(lines, read(voice / 'alignment.json')['alignment'])
    speed, fps = style['voice']['render_speed'], style['canvas']['fps']
    duration = math.ceil(float(probe(voice / 'voice-raw.mp3')['format']['duration']) / speed * fps) / fps
    scenes = []
    for item in plan['scenes']:
        start = raw[item['from_line']]['start'] / speed if item['from_line'] else 0
        end = raw[item['to_line']]['start'] / speed if item['to_line'] < len(raw) else duration
        # Short source windows slow down deterministically, never run beyond the clip.
        rate = min(1., (item['media_end'] - item['media_start']) / (end - start))
        if rate < .5:
            raise ValueError('Source window too short for narration; choose a longer meaningful window')
        scenes.append({'start': start, 'end': end, 'path': 'assets/media/source.mp4',
                       'media_start': item['media_start'], 'rate': rate,
                       'supports_caption': item['supports_caption']})
    episode = {'title': plan['title'], 'subtitle': plan['subtitle'], 'thread_url': source['url'],
               'thread_text': (p / 'post.txt').read_text(), 'script_reviewed': True,
               'source_has_baked_captions': False, 'duration': duration,
               'avatar_path': 'assets/media/avatar.mp4', 'scenes': scenes,
               'voice': {'path': str((voice / 'voice-raw.mp3').relative_to(p)), 'already_speed_adjusted': False},
               'caption_timebase': 'raw_voice_seconds',
               'captions': [{**c, 'text': c['text'].rstrip('.,?!')} for c in raw]}
    save(p / 'episode.json', episode)
    run([sys.executable, BASE / 'composition/build.py', '--project', p, '--episode', p / 'episode.json'])
    if a.build_only:
        print('Composition built; rendering not requested.')
        return
    verification = p / 'verification'
    verification.mkdir(exist_ok=True)
    cli = ['npx', '--yes', 'hyperframes@0.8.109']
    with (verification / 'check.json').open('w') as f:
        run(cli + ['check', str(p), '--at', ','.join(str(round(duration*x, 3)) for x in (.1,.3,.5,.7,.9)), '--snapshots', '--json'], stdout=f)
    run(cli + ['render', str(p), '--fps', str(fps), '--workers', '1', '--quality', 'delivery',
               '--frames-cache-dir', 'off', '--output', str(p / 'final-4k.mp4')])
    run(['ffmpeg', '-v', 'error', '-y', '-i', p / 'final-4k.mp4', '-vf', 'scale=1080:1920',
         '-c:v', 'libx264', '-crf', '19', '-preset', 'fast', '-c:a', 'copy', '-movflags', '+faststart', p / 'final-1080.mp4'])
    meta = probe(p / 'final-4k.mp4')
    v = next(x for x in meta['streams'] if x['codec_type'] == 'video')
    if (v['width'], v['height'], v['r_frame_rate']) != (2160,3840,'60/1') or abs(float(meta['format']['duration'])-duration) > .06:
        raise ValueError('Rendered dimensions/fps/duration do not match composition')
    if not any(x['codec_type'] == 'audio' for x in meta['streams']):
        raise ValueError('Rendered narration missing')
    run(['ffmpeg', '-v', 'error', '-i', p / 'final-4k.mp4', '-f', 'null', '-'])
    save(verification / 'probe.json', meta)
    print(f'Rendered {p / "final-4k.mp4"} and final-1080.mp4; agent must inspect snapshots and audio before handoff.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('url')
    prep.add_argument('--project', required=True, type=Path)
    prep.set_defaults(fn=prepare)
    config_default = Path(os.environ.get('FAMILY_SHORTS_CONFIG', str(Path.home() / '.config/family-shorts/config.json')))
    cfg = sub.add_parser('configure')
    cfg.add_argument('--avatar', required=True, type=Path)
    cfg.add_argument('--voice-id', required=True)
    cfg.add_argument('--config', type=Path, default=config_default)
    cfg.set_defaults(fn=configure)
    prod = sub.add_parser('produce')
    prod.add_argument('--project', required=True, type=Path)
    prod.add_argument('--config', type=Path, default=config_default)
    prod.add_argument('--build-only', action='store_true')
    prod.set_defaults(fn=produce)
    a = ap.parse_args()
    try:
        a.fn(a)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as e:
        raise SystemExit(f'Workflow stopped: {e}') from None


if __name__ == '__main__':
    main()
