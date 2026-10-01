import argparse,json
from pathlib import Path
from faster_whisper import WhisperModel

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--out',required=True); ap.add_argument('--model',default='small'); a=ap.parse_args()
 if not Path(a.input).exists(): raise SystemExit(f'TRANSCRIBE_INPUT_MISSING: {a.input}')
 try: model=WhisperModel(a.model,device='cpu',compute_type='int8',local_files_only=True)
 except Exception as e: raise SystemExit(f'TRANSCRIBE_MODEL_ERROR: {e}')
 segs,info=model.transcribe(a.input,word_timestamps=True,vad_filter=True)
 rows=[]
 for s in segs:
  rows.append({'start':s.start,'end':s.end,'text':s.text.strip(),'words':[{'start':w.start,'end':w.end,'word':w.word.strip(),'probability':w.probability} for w in (s.words or []) if w.word.strip()]})
 if not rows: raise SystemExit('TRANSCRIBE_EMPTY: no speech segments')
 out={'method':f'faster-whisper {a.model} cpu int8','language':info.language,'segments':rows}
 Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps({'segments':len(rows),'language':info.language},ensure_ascii=False))
if __name__=='__main__': main()
