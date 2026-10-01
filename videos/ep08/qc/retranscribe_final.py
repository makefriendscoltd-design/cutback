from faster_whisper import WhisperModel
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
m=WhisperModel('small',device='cpu',compute_type='int8',local_files_only=True,cpu_threads=2)
segments,_=m.transcribe(str(root/'renders/AI학교_8탄_ClaudexLoop_Owen_v1.mp4'),language='ko',vad_filter=False,word_timestamps=True,beam_size=5,initial_prompt='클로덱스 루프 페이블 5.1 GPT-6 아스트라 대시보드 가격 배송비 환불 광고비 댓글에 팀')
rows=[{'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in s.words]} for s in segments]
(root/'qc/final-asr.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(''.join(r['text'] for r in rows))
