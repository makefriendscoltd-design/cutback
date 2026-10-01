# AI학교 8탄 · Claudex Loop

- 상태: 완료
- 최종 MP4: `renders/AI학교_8탄_ClaudexLoop_Owen_v1.mp4`
- 길이: 73.833초 / 1080×1920 / 30fps / 2,215프레임
- 원본: 85.041초, 촬영 발화 1.16–82.30초 사용
- 컷: 50ms RMS와 raw/VAD 단어 경계를 대조해 문장 사이 쉼 17곳을 약 0.12초로 단축. 발화 단어 삭제 없음
- CTA: 독립 재전사로 `클로덱스 루프 스킬과 설정 방법이 궁금하시면 댓글에 팀이라고 남겨주세요` 확인
- 화면: 16장면, full 7비트, full↔card 13전환, 0.3초 `power2.inOut`
- 자막: 38개, Pretendard 800/60px, 한 줄, 문장부호 없음. 38/38 실제 DOM 검사 통과
- 폰트: Pretendard·JetBrains Mono 파일 로드 확인, 404/요청 실패 0건
- HyperFrames: CLI 0.8.103 final check, findings 0
- MP4: 전체 디코딩 오류 0, 73.833초, -14.23 LUFS, true peak -2.53 dBTP
- 시각 검증: 첫 프레임, 장면 중간 접촉 시트, 전환 전·중·후 인코딩 프레임, 마지막 CTA 프레임 확인
- 음성 검증: 원본 파형·50ms RMS·raw/VAD ASR·CTA 독립 ASR·최종 MP4 독립 ASR 대조. 직접 청취는 미검증
- 한글 점검: 짧은 UI·후킹 문구에 quick-rules 적용. 고유명사·수치·실제 발화 보존, 번역투·문장부호 추가 없음
