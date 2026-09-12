import pathlib,json,subprocess,mlx_whisper
r=pathlib.Path(__file__).resolve().parent
p=json.load(open(r/'edit-plan.json'));out=pathlib.Path('/Users/apple/Downloads/20260911_175145_컷편집_v2_타이트.mp4')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,duration,nb_frames,r_frame_rate:format=duration,size','-of','json',str(out)]))
(r/'output-probe.json').write_text(json.dumps(probe,indent=2))
with open(r/'decode.log','w') as log:subprocess.run(['ffmpeg','-y','-v','error','-i',str(out),'-f','null','-'],stderr=log,check=True)
x=mlx_whisper.transcribe(str(out),path_or_hf_repo='mlx-community/whisper-large-v3-turbo',language='ko',word_timestamps=True,condition_on_previous_text=False)
(r/'output-transcript.json').write_text(json.dumps(x,ensure_ascii=False))
(r/'output-transcript.txt').write_text('\n'.join(f"{s['start']:.2f}-{s['end']:.2f} {s['text']}" for s in x['segments']))
print(json.dumps(probe,ensure_ascii=False));print('decode errors',len((r/'decode.log').read_text()));print('expected duration',p['duration'])
for t in [1,120,p['duration']-1]:
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(out),'-frames:v','1','-vf','scale=640:-1',str(r/f'verify-{int(t)}.jpg')],check=True)
