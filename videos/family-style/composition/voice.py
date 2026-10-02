"""Prepare or generate a single-take ElevenLabs voice with character alignment.

Default: local request preparation. --generate performs the billable API call.
The returned audio is 1x; HyperFrames applies the style's 1.3x at render time.
"""
import argparse
import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent


def captions_from_alignment(lines, alignment):
    chars = alignment['characters']
    starts = alignment['character_start_times_seconds']
    ends = alignment['character_end_times_seconds']
    if not (len(chars) == len(starts) == len(ends)):
        raise ValueError('Malformed provider alignment')
    # Match original spelling, ignoring provider whitespace differences only.
    indices = [i for i, ch in enumerate(chars) if not ch.isspace()]
    compact = ''.join(chars[i] for i in indices)
    wanted = ''.join(ch for line in lines for ch in line if not ch.isspace())
    if compact != wanted:
        raise ValueError('Provider changed text: inspect alignment before captioning; no guessed timing')
    result, cursor = [], 0
    for line in lines:
        count = len(''.join(line.split()))
        first, last = indices[cursor], indices[cursor + count - 1]
        result.append({'start': starts[first], 'end': ends[last], 'text': line})
        cursor += count
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script', type=Path, help='One caption phrase per line')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--model', help='Omit to use provider default, not a claim about the reference model')
    ap.add_argument('--voice-id', default=os.environ.get('ELEVENLABS_VOICE_ID'), help='Private voice ID; otherwise use local style setting')
    ap.add_argument('--generate', action='store_true')
    a = ap.parse_args()
    s = json.loads((ROOT / 'style.json').read_text())
    voice_id = a.voice_id or s['voice'].get('voice_id')
    if not voice_id:
        ap.error('Set --voice-id or ELEVENLABS_VOICE_ID')
    lines = [line.strip() for line in a.script.read_text().splitlines() if line.strip()]
    if not lines:
        ap.error('Script is empty')
    body = {'text': ' '.join(lines), 'voice_settings': {'speed': 1.0}}
    if a.model:
        body['model_id'] = a.model
    if a.out.exists() and any(a.out.iterdir()):
        ap.error('Output directory is not empty; choose a new take directory')
    a.out.mkdir(parents=True, exist_ok=True)
    metadata = {'provider': 'elevenlabs', 'voice_id': voice_id,
                'generation_speed': 1.0, 'render_speed': s['voice']['render_speed'],
                'already_speed_adjusted': False, 'caption_timebase': 'raw_voice_seconds',
                'request': body, 'status': 'prepared_only'}
    manifest = a.out / 'voice-request.json'
    manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    if not a.generate:
        print('Prepared locally; no API request or credits used.')
        return
    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key:
        raise SystemExit('Missing ELEVENLABS_API_KEY; request remains prepared only.')
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128"
    req = Request(url, data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'}, method='POST')
    try:
        with urlopen(req, timeout=180) as response:
            data = json.load(response)
    except HTTPError as error:
        raise SystemExit(f'ElevenLabs HTTP {error.code}; no automatic retry') from None
    audio = base64.b64decode(data.pop('audio_base64'), validate=True)
    (a.out / 'voice-raw.mp3').write_bytes(audio)
    (a.out / 'alignment.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
    metadata['status'] = 'audio_generated_alignment_pending'
    manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    captions = captions_from_alignment(lines, data['alignment'])
    (a.out / 'captions-raw.json').write_text(json.dumps(captions, ensure_ascii=False, indent=2))
    metadata['status'] = 'generated_with_verified_text_alignment'
    manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    print('Voice and matching raw-time captions saved. Render at configured speed exactly once.')


if __name__ == '__main__':
    main()
