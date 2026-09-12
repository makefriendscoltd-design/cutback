import mlx_whisper,pathlib,json
r=pathlib.Path(__file__).parent
p=next(pathlib.Path('/Users/apple/Downloads').glob('20260911_175145*'))
x=mlx_whisper.transcribe(str(p),path_or_hf_repo='mlx-community/whisper-small-mlx',language='ko',word_timestamps=True,condition_on_previous_text=False)
(r/'audit-small.json').write_text(json.dumps(x,ensure_ascii=False))
(r/'audit-small.txt').write_text('\n'.join(f"{s['start']:.2f}-{s['end']:.2f} {s['text']}" for s in x['segments']))
