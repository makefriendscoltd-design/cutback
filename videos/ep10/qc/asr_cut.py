from pathlib import Path
import json
from faster_whisper import WhisperModel
r=Path(__file__).resolve().parents[1]
m=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=2)
s,_=m.transcribe(str(r/'assets/voice.m4a'),language='ko',word_timestamps=True,vad_filter=True)
rows=[dict(start=x.start,end=x.end,text=x.text) for x in s]
(r/'qc/cut-asr.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for x in rows:print(f"{x['start']:.2f}–{x['end']:.2f} {x['text']}")
