from pathlib import Path
import json,mlx_whisper
r=Path(__file__).parent
x=mlx_whisper.transcribe('/Users/apple/Downloads/원본_온라인 오프라인 바이어 미팅 노하우.mp4',path_or_hf_repo='mlx-community/whisper-large-v3-turbo',language='ko',word_timestamps=True,condition_on_previous_text=False)
(r/'transcript.json').write_text(json.dumps(x,ensure_ascii=False,indent=2))
(r/'transcript.txt').write_text('\n'.join(f"{s['start']:.2f}-{s['end']:.2f} {s['text']}" for s in x['segments']))
print('transcribed',len(x['segments']))
