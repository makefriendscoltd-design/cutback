# 윈도우에서 바이어 강의 편집 이어가기

이 패키지는 현재 확정본의 편집 소스와 필요한 미디어를 함께 담았다. 직원 PC의 Codex에서 이 폴더를 열고 아래 문장을 붙여 넣는다.

> AGENTS.md와 START_HERE.md를 읽고 이 강의 편집을 이어받아 줘. 필요한 환경을 확인하고 setup.ps1을 실행해. 15초 미리보기를 출력하고 실제 자막·화면·소리를 확인해. 실패하면 원인을 해결하고, Windows에서 검증된 것과 미검증인 것을 구분해서 보고해.

압축은 로컬 폴더(예: C:\VideoWork\Buyer-Lecture-Windows-v2)에 푼다. ZIP 안에서 실행하지 않는다. Python 3.11 이상과 FFmpeg/ffprobe(libass·libx264 포함)가 필요하다. 미설치 도구는 직원 Codex가 PC 상태를 확인해서 설치한다. 계정과 로그인 정보는 옮기지 않는다.

PowerShell에서 이 폴더로 이동한 뒤 실행:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
.\.venv\Scripts\python.exe -X utf8 run.py preview
.\.venv\Scripts\python.exe -X utf8 run.py render
.\.venv\Scripts\python.exe -X utf8 run.py verify
```

미리보기: qa/preview-15s.mp4. 전체 출력: output/buyer-lecture-v2.mp4. 검수: DELIVERY-VERIFICATION.json과 qa/delivery-contact.jpg. 전체 출력은 12분14초·1920×1080·25fps다. verify는 전체 디코드와 영상·음성 길이,4구간 싱크를 검사한다. 마지막으로 실제 재생과 화면 확인이 필요하다. 설치 성공만으로 완료가 아니다.

기존 컷은 cut-base.mp4에 들어 있다. 자막 수정은 sentence-groups.json → run.py render 순서다. 컷을 다시 바꾸려면 source/original.mp4와 edit-plan.json을 기준으로 cut-base를 재생성하고 자막·그래픽 시간도 함께 대조해야 한다. 그래픽 렌더는 동봉되어 있어 기존 영상 재출력에 Node/HyperFrames 설치는 필요 없다. 새 그래픽 제작에는 별도 HyperFrames 환경이 필요하다.

맥에서 전달용 소스의 미리보기 실행을 검사한다. 실제 Windows 실행은 이 패키지를 받은 PC에서 해야 하며 아직 미검증이다. 참고 화면과 기존 검증 기록은 qa/에 들어 있다. 원본 작업 커밋: 999f60c.
