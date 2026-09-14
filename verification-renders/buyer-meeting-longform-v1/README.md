# 바이어 미팅 롱폼 편집 v1

입력은 사용자가 지정한 Aside 네이버웍스 드라이브의 `원본_온라인 오프라인 바이어 미팅 노하우.mp4`다. 원본은 Downloads에 보존했다. 나민수/AI 학교 채널 편집과 별도 사례이며 해당 브랜딩·홍보영상·업로드는 적용하지 않았다.

편집 정본은 `edit-plan.json`, 자막 교정은 `transcript-corrections.json`과 `captions.json`, 디자인 정본은 `caption-style.json`, 그래픽 정본은 `build_graphics.py`와 `graphic-events-source.json`이다. 원본 시각을 최종 시각에 매핑한 파생 입력이 `graphic-events.json`이다.

제작 순서: `transcribe.py` → 교정/무음 검토 → `build_cut.py` → `build_captions.py` → `build_graphics.py`와 HyperFrames 알파 렌더 → `assemble.py` → `verify_delivery.py`. 기존 파일을 다시 실행하면 파생 파일을 덮어쓸 수 있으므로 다음 버전은 새 폴더에서 만든다.

원본은 슬라이드 화면과 큰 강사 컷아웃, 중복된 작은 화상회의 타일을 포함한다. 큰 강사와 슬라이드·저작권 문구는 보존하고 중복 타일 영역을 제외했다. 글로 된 강의 자료를 계속 움직이거나 확대해 읽기 어렵게 만들지 않도록 전체 슬라이드 줌은 적용하지 않았다. 기존 슬라이드 사진을 살리고 핵심 6구간에 새 의미 그래픽과 절제된 효과음을 넣었다. 오프닝의 무관한 영문 템플릿 잔여 문구를 정리했다.

자막 요청: Pretendard SemiBold, 캡컷 글자 크기 5, 흰색, 검정 블록 불투명도 68%, 최대 2줄. 캡컷 UI와 로컬 초안에서 5의 정확한 픽셀 환산값은 확보하지 못했다. 실제 렌더는 30px로 구현했고 이 값은 추정이며 동일 캡컷 렌더와의 일치는 미검증이다. 실제 폰트 선택은 `qa/font-check.log`에 Pretendard-SemiBold로 확인했다. 실제 모든 청크는 한 줄이다.

전체 디코딩/프레임/AV 길이/대표 구간 싱크는 `DELIVERY-VERIFICATION.json` 참조. 음성 원문과 의미 교정의 불확실성은 `qa/correction-audio-audit.json`, 편집 후 시작·중간·끝의 독립 전사 검사는 `qa/cut-audio-audit.json`에 보존했다. 이 표본 검사만으로 모든 미세 음절을 전수 청취했다고 주장하지 않는다.

최종 파일: `/Users/apple/Downloads/바이어_온라인_오프라인_미팅_롱폼_편집_v1.mp4`

대용량 원본/렌더/오디오와 외부 도구는 로컬 의존성이다. Python(mlx-whisper/NumPy/Pillow), FFmpeg/FFprobe, HyperFrames가 필요하다. 자막과 브리프를 다른 입력에 복사할 때 인명·채널·강의 사실을 그대로 옮기지 않는다.
