# EP11 v4 검증 보고

- 산출물: `renders/AI학교_11탄_Owen_v4.mp4` (1080×1920, 30fps, 45.200초)
- 원본 보존 계약: cuts, C_SRC, voice, presenter 동일; 자체 `mix.m4a`; 이벤트 해시·7개 cue 시간/범위 모두 통과
- 오디오: 최종 -14.08 LUFS, -2.03 dBTP; voice-bed 17.19 LU; 렌더 디코딩 대 mix 상관 0.999492, 지연 0ms; mix 45.200초
- HyperFrames: 최종 저장 검사 `ok=true`; runtime/layout/contrast 오류·경고 0
- 자막: 33/33 표시·한 줄·문장부호 제거·가로/세로 안전영역·클립 중점 통과
- 화면: 성과행 선택→AI 인사이트, 고객군 토글→초안 생성, 권한 토글의 7개 실제 액션을 인코딩 프레임에서 확인
- full 장면은 빌드 assertion으로 빈 presenter 화면만 허용하며 UI는 card 장면에만 배치
- 카메라: full 15.84초(35.04%), 분리된 full beat 4개 통과
- 검토 자료: `qc/final-contact-sheet.jpg`, `qc/action-filmstrip.jpg`, `qc/render-verification.json`, `qc/action-verification.json`, `qc/caption-audit.json`, `qc/final-check.json`, `qc/audio/mix-report.json`, `qc/render.log`

- Parent independent review: final scene midpoints/end, action states and all8 encoded camera transition triplets reviewed; no face-covering panels. Transition evidence: qc/transition-sheet.jpg and qc/parent-transition-review-*.jpg.
- Direct full soundtrack listening: not performed.
