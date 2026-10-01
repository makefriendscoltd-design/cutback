from pathlib import Path
from faster_whisper import WhisperModel
import json,subprocess
root=Path(__file__).resolve().parent
subprocess.run(['ffmpeg','-v','error','-y','-i',str(root/'src/source.mp4'),'-vn','-ac','1','-ar','16000',str(root/'src/source_16k.wav')],check=True)
m=WhisperModel('small',device='cpu',compute_type='int8',local_files_only=True,cpu_threads=2)
res={}
for key,vad in [('vad',True),('raw',False)]:
 segs,info=m.transcribe(str(root/'src/source_16k.wav'),language='ko',word_timestamps=True,vad_filter=vad,initial_prompt='오늘도 AI 직원을 뽑았습니다. 클로드 코드 플러그인 수파베이스 Supabase 버셀 Vercel 오 마이 클로드 코드 Chrome DevTools MCP 열아홉 명 배포')
 res[key]=[{'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in s.words]} for s in segs]
(root/'src/transcript.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
for s in res['raw']:print(f"{s['start']:.2f}-{s['end']:.2f} {s['text']}")
