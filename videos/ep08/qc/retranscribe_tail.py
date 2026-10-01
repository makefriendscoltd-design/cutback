from faster_whisper import WhisperModel

m = WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True, cpu_threads=2)
segments, _ = m.transcribe(
    "videos/ep08/src/source_16k.wav",
    language="ko",
    word_timestamps=True,
    vad_filter=False,
    clip_timestamps="70,85.041",
    beam_size=5,
    initial_prompt="클로덱스 루프 스킬과 설정 방법이 궁금하시면 댓글에 팀이라고 남겨주세요",
)
for segment in segments:
    print(f"{segment.start:.3f}-{segment.end:.3f} {segment.text}")
    for word in segment.words:
        print(f"  {word.start:.3f}-{word.end:.3f} {word.word} p={word.probability:.3f}")
