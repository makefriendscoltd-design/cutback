# AI 학교 1일차 v19

편집 규칙 정본: ../../.agents/skills/ai-school-video-edit/references/styles.json

검정 그림자 자막, 1초 두 줄 POV 헤드카피, 1배속 꼬리물기 컷과 기존 오디오를 보존한 버전이다. `export_4k.sh`는 검증된 v19 마스터를 2160×3840으로 Lanczos 확대하고 오디오를 복사한다. 네이티브 4K 촬영 디테일 복원은 아니다.

`delivery-verification.json`에 49.6초·1488프레임·전체 디코딩 검증을 기록했다. 노션 AI 학교의 1일차 → 완성본에는 4K 파일만 남은 것을 새로고침 후 확인했다.

영상·음원·폰트·스티커 등 대용량 미디어는 Git에 포함하지 않는다. 로컬 `assets/`, `composition/assets/`, 렌더용 의존 파일이 필요하므로 새 체크아웃만으로 전체 편집을 재렌더할 수는 없다. MP4는 이 로컬 폴더와 노션에 보관한다. 소스와 EDL·자막·스타일 설정을 이 커밋으로 보존한다.
