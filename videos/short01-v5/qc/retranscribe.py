import sys,json
from faster_whisper import WhisperModel
m=WhisperModel("small",device='cpu',compute_type='int8',cpu_threads=4)
s,_=m.transcribe(sys.argv[1],language='ko',word_timestamps=True,vad_filter=False)
rows=[dict(start=x.start,end=x.end,text=x.text,words=[dict(start=w.start,end=w.end,word=w.word) for w in x.words]) for x in s]
json.dump({'raw':rows},open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
for x in rows:print(round(x['start'],2),round(x['end'],2),x['text'])
