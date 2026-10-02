# 패밀리 숏폼 — Threads 링크로 제작

Threads 본문과 가로형 영상을 받아 대본, 장면 편집, 내레이션, 자막을 만들고 HyperFrames로 렌더하는 Codex 스킬입니다.

설치 후 Codex에 이렇게 요청합니다.

> $family-shorts https://www.threads.com/@choi.openai/post/Dd-ruXhkx6C

사용자는 링크만 입력합니다. Codex가 원문과 장면을 읽고 대본을 구성하며, Python 도구가 음성 생성과 자막 싱크, 렌더를 처리합니다. **허브 웹페이지 안에서 직접 렌더하는 서비스는 아닙니다.**

## 설치

이 저장소를 받은 뒤 `videos/family-style` 폴더 전체를 `~/.agents/skills/family-shorts`에 복사하거나 심볼릭 링크로 연결합니다. 기존 설치가 있으면 덮어쓰기 전에 변경 내용을 비교하세요. Python 3.10+, Node/npm, ffmpeg/ffprobe가 필요하며 HyperFrames는 0.8.109로 고정되어 있습니다.

처음 한 번 승인된 여자 캐릭터 영상과 ElevenLabs 보이스 ID를 등록하고, `ELEVENLABS_API_KEY` 환경 변수를 설정합니다. 구체적인 명령과 실행 흐름은 [SKILL.md](SKILL.md)에 있습니다. 개인 자료와 API 키는 저장소에 포함하지 않습니다.

## 출력과 확인 범위

- 세로 4K60 및 1080×1920 MP4
- 본문, 대본, 장면표, 편집 가능한 HyperFrames HTML
- 1배속 ElevenLabs 음성을 렌더 시 1.3배속으로 재생하고 같은 시간 기준으로 맞춘 자막
- 렌더 검사, 프레임 캡처, 영상 규격 검사 결과

111 레퍼런스의 두 줄 제목, 폰트 크기, 패널 위치, 파란 자막 그림자와 원형 캐릭터 배치를 반영했습니다. 글과 화면에 맞춘 장면 선택은 Codex가 수행합니다. 비공개 글·다운로드 차단·원본 자막·여러 영상은 추가 판단이 필요하며 모든 링크의 성공을 보장하지 않습니다. 음성 API 사용료는 ElevenLabs 계정에 청구됩니다.

폰트 원본과 이용 조건: [샌드박스 어그로](https://www.sandbox.co.kr/company-ci), [S-Core Dream](https://s-core.co.kr/company/font/). 배포본의 라이선스는 `licenses/`에 보존했습니다. GSAP 파일은 원본 헤더의 라이선스를 따릅니다.

## 실제 실행 검증

제공된 Claude Mods 게시물로 공개 원본 수집부터 32.2초 4K60·1080p 렌더까지 확인했습니다. 기존에 생성·검수한 음성을 캐시로 재사용했으며 재렌더 음성은 이전 검증본과 디코딩 결과가 같습니다. HyperFrames 구문·런타임·배치 오류는 0건입니다. 밝은 영상 위 자막 대비 경고 3건은 파란 그림자를 포함한 실제 프레임으로 확인했습니다. 새 링크의 장면 판단과 Windows 실행은 별도 검증 대상입니다.
