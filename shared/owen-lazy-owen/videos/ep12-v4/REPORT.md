# EP12 v4 검증 보고

- 산출물: `renders/AI학교_12탄_Owen_v4.mp4` (1080×1920, 30fps, 43.500초)
- 원본 보존 계약: cuts, C_SRC, voice, presenter 동일; 자체 `mix.m4a`; 이벤트 해시·4개 cue 시간/범위·선언 폰트 모두 통과
- 오디오: 최종 -14.06 LUFS, -1.94 dBTP; voice-bed 16.77 LU; 렌더 디코딩 대 mix 상관 0.999387, 지연 0ms; mix 43.500초
- HyperFrames: 최종 저장 검사 `ok=true`; runtime/layout/contrast 오류·경고 0
- 자막: 32/32 표시·한 줄·문장부호 제거·가로/세로 안전영역·클립 중점 통과
- 화면: 문의 도착→판정 질문→JSON 확률 게이지→애매한 문의 사람 검토 분기의 실제 액션을 인코딩 프레임에서 확인
- full 장면은 빌드 assertion으로 빈 presenter 화면만 허용하며 UI는 card 장면에만 배치
- 카메라: full 13.20초(30.34%), 분리된 full beat 5개 통과
- 검토 자료: `qc/final-contact-sheet.jpg`, `qc/action-filmstrip.jpg`, `qc/render-verification.json`, `qc/action-verification.json`, `qc/caption-audit.json`, `qc/final-check.json`, `qc/audio/mix-report.json`, `qc/render.log`

- Parent independent review: final scene midpoints/end, action states and all10 encoded camera transition triplets reviewed; no face-covering panels. Transition evidence: qc/transition-sheet.jpg and qc/parent-transition-review-*.jpg.
- Direct full soundtrack listening: not performed.
