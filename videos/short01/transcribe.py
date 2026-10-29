from pathlib import Path
import json
from faster_whisper import WhisperModel
r=Path(__file__).resolve().parent
m=WhisperModel("small",device='cpu',compute_type='int8',cpu_threads=2)
s,info=m.transcribe(str(r/'src/source.mp4'),language='ko',word_timestamps=True,vad_filter=False)
rows=[dict(start=x.start,end=x.end,text=x.text,words=[dict(start=w.start,end=w.end,word=w.word,probability=w.probability) for w in x.words]) for x in s]
(r/'src/transcript.json').write_text(json.dumps({'raw':rows},ensure_ascii=False,indent=2))
for x in rows:print(round(x['start'],2),round(x['end'],2),x['text'])
