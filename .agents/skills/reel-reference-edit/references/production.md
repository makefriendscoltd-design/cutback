# 실행 경로와 검증

이 문서는 에이전트가 새 전사에 맞는 애셋을 직접 설계·구현한 뒤 사용하는 제작 도구의 연결이다. 입력 하나를 받았다는 이유로 전사 검수와 창작이 자동 완료되지는 않는다. 같은 영상의 촬영 원본과 꼬리물기 마스터는 구별한다.

## 의존성

Python 3, ffmpeg/ffprobe, Node/npm, HyperFrames가 필요하다. 기존 HyperFrames 프로젝트를 이어갈 때는 `hyperframes` 스킬의 버전 확인 절차를 따른다. 아래 CLI는 0.8.36에서 실제 확인한 인터페이스다.

승인된 글꼴 3개와 공식 라이선스는 `assets/fonts/`에 포함되어 있다. GSAP은 번들하지 않으며 고정 버전 URL과 SHA-256으로 확보한다. 절대 경로로 된 과거 렌더 폴더의 글꼴 링크에 의존하지 않는다.

```bash
SKILL='/Users/apple/orca/projects/cutback/.agents/skills/reel-reference-edit'
python3 "$SKILL/scripts/resolve_dependencies.py" --output '/path/new-job-dependencies'
```

오프라인에서는 `--gsap '/path/gsap.min.js'`를 추가한다. 이 경우에도 같은 해시 검사를 한다. 결과 JSON의 `gsap`, `font_dir`을 다음 단계에서 사용한다.

## 새 작업 준비

입력 자체가 확인된 꼬리물기 편집본이면 `--input`과 `--audio-master`에 같은 파일을 준다. 별도 마스터라면 picture와 같은 시간축·길이인지 먼저 확인한다. 이 준비기는 불일치를 임의 컷으로 해결하지 않는다.

```bash
python3 "$SKILL/scripts/prepare.py" \
  --input '/path/edited-video.mp4' \
  --audio-master '/path/locked-master.mp4' \
  --captions '/path/verified-transcript.srt' \
  --style memo --output '/path/new-job'
```

결과는 `intake.json`, 대표 프레임, `BRIEF.md`, `edit-manifest.json`이다. 자막·음성 마스터 인자를 생략해 조사용 준비만 할 수 있지만, builder는 빠진 항목이 있으면 렌더 소스를 만들지 않는다. 준비기는 전사·음성 편집·새 애셋 창작을 수행하지 않는다.

manifest의 `assets`와 `upper_beats`는 처음에는 비어 있다. 실제 자막을 읽고 새로 작성한다. `composition.duration`은 입력에서 결정되며 오래된 작업의 길이·슬롯 수를 복사하지 않는다.

## 새 모션 애셋의 선렌더

각 애셋을 별도의 HyperFrames 프로젝트로 직접 구현한다. 내용이 없는 보일러플레이트를 완성 애셋으로 취급하지 않는다. 주제별 사물·그래픽·모션은 이번 전사에서 새로 설계한다.

1. 정본 `production_layout.supporting_asset`의 설계 크기에 출력 배율을 곱해 애셋 캔버스를 정한다. 기본 4K에서는 해당 상자가 2032×1178 출력 픽셀이다.
2. 프로젝트 `index.html`의 루트에 `data-composition-id`, `data-width`, `data-height`, `data-duration`, `data-fps`를 선언한다. SVG/HTML과 seek 가능한 `window.__timelines[id]`를 만든다. 구현 계약은 `hyperframes-core`와 `hyperframes-animation`을 따른다.
3. 다음 실제 CLI로 렌더한다. 프로젝트 경로를 첫 위치 인자로 넘긴다.

```bash
npx --yes hyperframes@0.8.36 check '/path/new-job/asset-studio/new-motion'
npx --yes hyperframes@0.8.36 render '/path/new-job/asset-studio/new-motion' \
  --output '/path/new-job/asset-studio/new-motion.mp4' --fps 30 --quality high
```

렌더 MP4와 새 HTML/SVG 소스를 모두 남긴다. 불투명 애셋은 MP4로 구성한다. 투명 합성이 필요하면 지원되는 알파 포맷으로 별도 실제 재생 검증을 거친다. 최종 builder에 HTML을 video인 것처럼 넘기지 않는다.

## manifest 연결

미디어 경로는 절대 경로로 기록한다. 현재 builder는 파일을 작업 composition의 assets 아래에 연결한다. 이동·납품할 때는 링크 대상까지 함께 패키징해야 한다.

| 항목 | 필요한 값 |
|---|---|
| `job_id` | 이번 작업 고유 ID |
| `assets[].id`, `path`, `kind` | 새 애셋의 ID, 렌더 파일, `video` 또는 `image` |
| `created_for_job` | 해당 `job_id`와 일치 |
| `authored_source` | 새로 작성한 HTML/SVG 등 편집 소스 경로 |
| `spoken_evidence` | `{ "caption_index": 0 }`처럼 실제 captions 번호 또는 start/end |
| `explanatory_purpose` | 발화의 무엇을 어떤 화면으로 이해시키는지 |
| `upper_beats[]` | start/end, kind, asset ID, 필요한 media_start |
| 카피 비트 | `kind: fragments`와 `lines`(행마다 문자열 배열), 또는 `kind: step`과 number/title |
| `captions[]` | 실제 start/end/text, source_start/source_end 또는 identity mapping |

마지막 조립 단계에서는 모션 원본을 선렌더한 `video`로 연결한다. validator가 원본 HTML을 허용하는 것과 builder가 그것을 자동 렌더하는 것은 다르다. 같은 비디오를 두 슬롯에서 재사용하면 검사에 실패한다. 다른 이름으로 재인코딩한 영상이나 메타데이터만 새로 붙인 기존 애셋은 사람이 소스·화면 검수에서 제외한다.

## 본편 조립과 4K 출력

```bash
python3 "$SKILL/scripts/build_composition.py" \
  --manifest '/path/new-job/edit-manifest.json' \
  --output '/path/new-job/composition' \
  --gsap '/path/new-job-dependencies/gsap.min.js'
python3 "$SKILL/scripts/validate_plan.py" \
  --plan '/path/new-job/composition/edit-plan.json' \
  --composition '/path/new-job/composition'
npx --yes hyperframes@0.8.36 check '/path/new-job/composition'
npx --yes hyperframes@0.8.36 render '/path/new-job/composition' \
  --output '/path/new-job/picture-4k.mp4' --fps 30 --quality high
```

기본값은 2160×3840 DOM 캔버스이며 설계 좌표를 균일하게 2배 적용한다. 명시적으로 작은 출력이 필요할 때만 builder에 `--resolution 1080`을 준다. 구운 자막과 `captions.srt`는 같은 최종 captions 배열에서 생성된다. 프로필 해시가 바뀌었다면 변경 의도를 검토하고 manifest를 다시 준비한다.

## 음성 보존과 전달 검증

렌더러가 만든 음성을 최종 원본으로 간주하지 않는다. 확인된 마스터 음성을 다시 연결한다. 아래는 MP4에 스트림 복사 가능한 마스터의 예다.

```bash
ffmpeg -v error -n -i '/path/new-job/picture-4k.mp4' \
  -i '/path/locked-master.mp4' -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a copy -movflags +faststart '/path/new-job/final-4k.mp4'
python3 "$SKILL/scripts/verify_delivery.py" \
  --plan '/path/new-job/composition/edit-plan.json' \
  --composition '/path/new-job/composition' \
  --final '/path/new-job/final-4k.mp4' --output '/path/new-job/qa'
```

마스터 코덱이 MP4 스트림 복사와 맞지 않으면 확인된 AAC donor가 있는지 먼저 찾는다. 없으면 PCM 보존이 가능한 무손실 출력 경로와 사용처 호환성을 검증한다. 임의 AAC 재인코딩 후 PCM 해시가 같은 것처럼 보고하지 않는다. `-shortest`로 오디오 끝을 숨기지 않는다.

검증기는 실제 마스터 길이, 해상도·fps, 전체 디코드, 패킷·PCM 해시와 대표 프레임을 확인한다. 기존 QA 폴더는 덮어쓰지 않는다. `--visual-reviewed`, `--direct-listened`, `--source-audited`는 해당 검수를 실제 수행한 뒤에만 사용한다. 직접 청취와 새 애셋의 의미·품질·출처 검토를 해시 성공으로 대체하지 않는다.

## 검증된 범위

새 2초 입력과 새 SVG/GSAP 애셋을 사용해 애셋 선렌더→준비→4K 조립 경로를 검증했다. 이는 런타임과 가변 길이·출력 배율의 검증이며 창작 품질의 예시가 아니다. 매 실제 영상의 전사 정확도, 얼굴 구도, 애셋 의미, 실제 속도와 시각 품질은 새로 검수한다.
