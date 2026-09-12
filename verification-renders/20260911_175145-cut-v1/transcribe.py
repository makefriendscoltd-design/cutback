import pathlib,json,mlx_whisper
r=pathlib.Path(__file__).parent
p=next(pathlib.Path('/Users/apple/Downloads').glob('20260911_175145*'))
x=mlx_whisper.transcribe(str(p),path_or_hf_repo='mlx-community/whisper-large-v3-turbo',language='ko',word_timestamps=True,condition_on_previous_text=False)
(r/'transcript.json').write_text(json.dumps(x,ensure_ascii=False,indent=2))
(r/'transcript.txt').write_text('\n'.join(f"{s['start']:.2f}-{s['end']:.2f} {s['text']}" for s in x['segments']))
print('transcribed',len(x['segments']))
