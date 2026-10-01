# 9탄 · 일마다 AI 직원 따로 뽑는 법 — 완료

완성본: `renders/AI학교_9탄_Agents_Owen_v1.mp4`

- 43.999초, 1080×1920, 30fps, 1,319프레임, 54.38MB.
- 실제 촬영 발화와 전자책 CTA를 사용했다. 첫 프레임부터 한국어 후킹·인물·첫 자막이 보인다.
- card 21.48초 / full 22.54초, 인물 full 7비트, card/full 전환 13곳이다. 모든 전환은 0.3초 `power2.inOut`이다.
- 30개 자막은 전부 한 줄, Pretendard 800/60px, 문장부호 없음, 안전영역 실측을 통과했다.
- HyperFrames 0.8.103 check의 lint/runtime/layout 오류 0·경고 0. 실제 MP4 전체 디코딩 오류 0.
- 장면 스냅샷 `qc/preview/contact-sheet-1..4.jpg`, 인코딩본 전환 전·중·후 `qc/encoded-transitions.jpg`를 확인했다.
- 최종 음량 -14.05 LUFS / -1.45 dBTP. 렌더러 출력의 오디오가 -21.34 LUFS로 감쇠돼, 검증한 최종 mix를 `qc/remux_final.py`로 영상 스트림에 무손실 remux했다. 이후 전체 MP4를 다시 검증했다.
- 최종 독립 ASR은 본문 제품명과 전자책 CTA 순서를 보존했다. 근거는 `qc/final-asr.json`, `qc/audio-final-review.md`다.
- 미검증: 사람의 연속 음성 청취. 외부 업로드·게시 없음.
