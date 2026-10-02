# EP06 v4 코드 감사 및 구현 기준

## 문서 상태

- 목적: Claude가 제작한 기존 시리즈(`owen-new`, `ep03`, `ep04`, `ep05`)의 시각·시간 설계와 `ep06-v3`를 코드 수준에서 비교하고, v4의 구현 및 검수 기준을 고정한다.
- Final status: IMPLEMENTED AND RENDER-VERIFIED. Historical proposals below are reconciled by Implementation decisions and Final acceptance. Full direct audio listening remains unverified.
- 보존 계약: `cuts.json`, 원본 발화에 연결된 `C_SRC`, 첫 훅의 의미와 발화 순서는 유지한다.
- 범위: 시각 장면, 문서 캡처, 오브젝트 상태 변화, 타이포그래피, 장면 내 타이밍, 전환, 카메라와 이벤트 기반 믹스의 연결.

## 확인된 차이

### 1. v3는 공통 패널을 만들었지만 장면별 문법을 잃었다

v3는 `.panel`, `.chrome`, `.gridbg`, `.badge`, `.doc`를 한 벌로 정의하고 거의 모든 설명을 같은 navy 패널에 넣는다(`videos/ep06-v3/build.py:16-35`). `presenter()`도 매번 같은 위치, 같은 62px Pretendard 제목, 같은 0.25초 `y/opacity` 입장을 반복한다(`videos/ep06-v3/build.py:37-38`). 이 함수가 `s04b`, `s06`, `s08`, `s11b`, `s14b`, `s15`에 반복되면서 서로 다른 의미가 같은 장면처럼 보인다(`videos/ep06-v3/build.py:53,55,57,61,65-66`).

기존 시리즈는 의미에 따라 문법을 바꾼다. ep03의 사원증은 낙하, 직책 도장, 진동, 유영을 순차 실행한다(`videos/ep03/build.py:64-82`). 같은 파일의 Premiere 금지 장면은 제목과 아이콘 입장, X 두 획 그리기, 진동, 탈색, 지속 확대를 조합한다(`videos/ep03/build.py:87-101`). ep04의 다섯 사원증은 개별 카드가 펼쳐진 뒤 월급 도장이 들어온다(`videos/ep04/build.py:90-110`). 장면 하나가 하나의 입장 효과로 끝나지 않고, 발화의 논리 단계를 오브젝트 사건으로 번역한다.

### 2. v3는 보유한 증거 캡처를 대부분 사용하지 않는다

v3 코드에서 실제 캡처를 호출하는 장면은 `google-blog.png`와 `readme-caution.png`뿐이다(`videos/ep06-v3/build.py:51,64`). 프로젝트에는 `overview.png`, `skill-pipeline.png`, `patch-reattack.png`, `repo.png`, `repo-desktop.png`, `disclaimers.png`, `getting-started.png`, `skills-install.png`도 있으나 v3 `build.py`에서 호출되지 않는다. `s04-form`, `s05-order`, `s07-map`, `s09-test`, `s10-patch`, `s11-retest`, `s13-isolate`는 대부분 합성 UI와 큰 설명 글자로 대체됐다(`videos/ep06-v3/build.py:52-64`).

기존 시리즈의 캡처는 장식이 아니라 증거 흐름이다. ep03 `shot_card()`는 원본 이미지 좌표를 받아 viewport 중심 pan/zoom을 만들고, 실제 좌표 위에 SVG 박스를 그린다. 긴 이동은 `none`, 짧은 재프레임은 `power2.inOut`으로 구분한다(`videos/ep03/build.py:123-146`). ep04 helper는 원본 픽셀을 표시 배율로 변환하고 지속 스크롤과 박스 draw를 생성한다(`videos/ep04/build.py:58-79`). ep05의 논문 장면은 전체 문맥에서 저자 위치로 2.6배 이동한 뒤 박스와 한글 nameplate를 보여준다(`videos/ep05/build.py:130-144`). confidence 장면은 문서 스크롤 뒤 해석 카드, 게이지, 수치 count-up을 겹친다(`videos/ep05/build.py:198-214`).

v4에서 캡처는 **공식 문서 또는 저장소를 설명하는 증거 이미지**로 취급한다. 실제 앱을 실시간 조작한 화면이라고 암시하지 않는다. 합성 주문서, 신청서, 재현 요청 등은 반드시 `화면 예시`, `흐름 설명용 예시`, `취약점 설명용 예시`처럼 예시임을 화면에 표시한다.

### 3. v3의 오브젝트는 등장하지만 상태가 충분히 변하지 않는다

v3 `s07-map`은 네 노드를 보여주지만 pulse는 x 이동 한 번과 y 이동 한 번만 수행해 전체 경로를 실제로 순회하지 않는다(`videos/ep06-v3/build.py:56`). `s09-test`는 명령, 요청자, FAIL, 설명을 순차 표시하지만 모두 독립 텍스트이며 증거 화면이나 재현 상태와 결합하지 않는다(`videos/ep06-v3/build.py:58`). `s10-patch`는 세 줄을 reveal하고 PATCH 배지를 띄우는 데 그친다(`videos/ep06-v3/build.py:59`). `s05-order`와 `s11-retest`는 같은 helper를 써서 반복 구조는 좋지만, 빨간 취약 상태가 cyan 차단 상태로 바뀌는 과정이 장면 사이에 생략된다(`videos/ep06-v3/build.py:39-46,54,60`).

기존 시리즈는 같은 오브젝트의 상태 변화로 의미를 만든다. ep04는 문서 카드가 떨어져 프로젝트 트리 안으로 축소·흡수된 뒤 파일 행, 프롬프트, 처리 결과가 이어진다(`videos/ep04/build.py:173-195`). ep05는 1,000개의 셀을 실제 DOM 오브젝트로 만들고 출현→분류색 변화→축소→비용 결과로 바꾼다(`videos/ep05/build.py:240-266`). 긴급도 장면은 점수 등장 후 5점 행이 맨 위로 재정렬되고 강조된다(`videos/ep05/build.py:288-302`).

### 4. v3는 폰트를 로드하지만 역할 분리가 약하다

기존 시리즈는 Nanum/Instrument Serif를 큰 개념과 제품명, Silkscreen을 기술 제품 표식, JetBrains Mono를 URL·코드·수치, Pretendard를 한국어 설명에 쓴다. ep03 제품 타이틀은 명조 kicker, 앱 아이콘, Instrument Serif 제품명, Mono 저장소명을 분리한다(`videos/ep03/build.py:104-120`). ep05 Jev 타이틀도 같은 계층을 유지한다(`videos/ep05/build.py:112-128`).

v3는 폰트 파일을 상속받지만 장면의 대부분이 Pretendard 굵은 글씨이고, Mono는 chrome/address/diff 일부에만 제한된다(`videos/ep06-v3/build.py:18-25,43,58-59`). v4는 제품명 `MANTIS`와 기술 표식, 문서 주소, 한국어 해석의 서체 역할을 분명히 나눈다.

### 5. 오디오 타이밍은 v3에서 새 컷과 분리됐다

타이밍 감사 결과, v3의 `assets/mix.m4a`는 기존 `ep06` 믹스와 byte-identical이다. 반면 v3에는 8.43초, 29.16초, 36.42초의 새 컷/구조가 들어갔다. 따라서 시각 이벤트가 새 장면 경계로 이동했는데도 효과음과 음악 사건은 이전 타임라인에 남아 있는 일반 믹스 불일치가 존재한다. v4는 v3 믹스를 복사해 쓰지 않고, v4 장면 이벤트에서 자체 믹스를 생성해야 한다.

## v4에서 재사용할 구현 메커니즘

### 원본 좌표 기반 `shot_card`

`shot_card`는 다음 계약으로 만든다.

- 캡처 원본의 너비·높이와 viewport 크기를 명시한다.
- 강조 박스와 카메라 키는 원본 이미지 좌표로 기록한다.
- 함수 내부에서 표시 배율과 transform을 계산한다. CSS 표시 좌표를 호출부에서 수작업으로 중복 계산하지 않는다.
- 전체 문맥 hold → 핵심 위치 이동 → outline draw → 한글 해석 plate 순서를 기본으로 한다.
- 긴 읽기 이동은 선형 또는 `sine.inOut`, 짧은 목적 이동은 `power2.inOut`, 박스 draw는 0.35~0.5초를 기준으로 한다.
- 캡처 출처 라벨을 유지하고, 합성 오버레이는 `예시`로 표시한다.

참조 구현은 `videos/ep03/build.py:123-151`, `videos/ep04/build.py:58-79`다.

### source-time named cue

ep05의 `J()`와 `add()`처럼 source time을 장면 local time으로 바꾸는 named cue를 사용한다(`videos/ep05/build.py:47-55`). 호출부에는 `.35`, `1.2` 같은 무맥락 local 숫자 대신 `map_start`, `finding`, `repro`, `patch`, `retest`, `blocked`, `warning`처럼 발화 의미가 드러나는 source cue를 전달한다. 같은 cue를 시각 애니메이션과 SFX 이벤트가 공유해야 한다. 컷이 바뀌면 하나의 변환 함수가 두 계층을 함께 이동시킨다.

### 의미가 있는 상태 변환

각 핵심 오브젝트는 단순 입장보다 상태 변화가 우선이다.

- 신청 버튼 → 주소의 주문 번호 → 노출된 영수증 → 취약 도장
- 코드 지도 노드 → 경로 순회 → 취약 노드 경고
- 실제 재현 캡처 → FAIL → 수정 diff
- 취약 영수증 → lock/wipe → 접근 차단 영수증
- 실제 서비스와 테스트 환경의 연결선 → 빨간 X로 절단
- README 경고문 → 원문 outline → 한국어 해석 → 전문가 확인

한 장면이 2초 이상이면 원칙적으로 발화와 연결된 사건을 세 개 이상 둔다. 단, 읽을 시간을 해치는 장식 움직임은 넣지 않는다.

### 타이포그래피 역할

- Pretendard: 자막, 한국어 설명, UI 본문
- JetBrains Mono: URL, 명령, 요청, 코드 diff, 숫자 ID
- Silkscreen: `MANTIS`, 기술 제품 표식, 짧은 영문 워드마크
- Instrument Serif 또는 Nanum Myeongjo: 챕터 kicker, 큰 개념명

제품명과 설명을 같은 굵기·같은 위치로 반복하지 않는다. 한 장면에서 위계는 제품/개념, 증거, 해석, 출처 순으로 읽혀야 한다.

### 카메라 hold와 punch

카메라 상세값은 별도 카메라 감사와 최종 렌더 판단을 따른다. 코드 수준 수용 기준은 다음과 같다.

- 새 장면마다 자동 punch를 만들지 않는다.
- 문서 전체 문맥은 최소한의 hold를 확보한 뒤 핵심 위치로 이동한다.
- punch는 `FAIL`, 취약 도장, 차단 성공처럼 의미가 바뀌는 순간에만 쓴다.
- 동일 panel↔presenter 반복 때문에 발생하는 기계적 왕복을 없앤다.
- 화면 내부 `shot_card` 이동과 호스트 카메라 이동이 같은 순간 서로 경쟁하지 않게 한다.

### v4 자체 이벤트 기반 믹스

v4는 named cue에서 `events.json`을 만들고 그 이벤트로 SFX와 음악 오토메이션을 생성한다. 최소 이벤트는 문서 focus/draw, 취약 도장, route 도착, FAIL, PATCH, retest block, warning X, CTA typing이다. 컷 매핑 이후의 output time을 단일 정본으로 쓰며, 과거 믹스 파일의 타임스탬프를 재사용하지 않는다.

## 장면별 구현 방향

- 첫 훅: 발화와 문구는 보존한다. 선 하나만 늘리는 v3 방식 대신 Silkscreen 제품 표식, 명조/Serif 개념명, Mono 출처를 층별로 입장시킨다.
- 보안팀 소개: 반복 `presenter()`를 제거하고 지도·탐색·재현·패치·재검사 역할을 카드 또는 노드로 보여준다. `skill-pipeline.png`를 증거 배경으로 사용할 수 있다.
- Google 소개: `google-blog.png` 전체 문맥에서 Mantis 명칭과 소개 문장으로 이동해 outline과 출처를 보여준다.
- 신청서/주문서: 합성 예시 라벨을 유지하고 버튼, URL 번호, 영수증을 같은 cyan shape로 연결한다.
- 코드 지도: `overview.png` 또는 `skill-pipeline.png`를 바탕으로 실제 경로를 순회하고 마지막 취약 노드에서 경고 상태로 변환한다.
- 검토/재현/패치: 중복 presenter 장면을 없애고 `patch-reattack.png`의 발견 위치→재현→diff를 한 증거 흐름으로 만든다.
- 재검사: 취약 상태와 동일한 레이아웃을 유지하면서 화면 안에서 lock/wipe 후 차단 상태로 바꾼다.
- 두 가지 주의: 서비스와 sandbox 연결을 끊는 물리적 변환, `readme-caution.png` 및 `disclaimers.png`의 실제 문장 outline을 사용한다.
- CTA: presenter 텍스트 대신 실제 댓글 입력 UI에서 `보안`을 `steps()`로 입력하고 커서 blink와 게시 버튼 pulse를 둔다.

## Final acceptance

- [x] Original 35 captions, source cut segments, approved opening and voice source preserved.
- [x] Distinct badge, document, light shop UI, code map, terminal, diff and comment structures replace repeated presenter summaries.
- [x] Three relevant official source captures use image-coordinate focus/outline; illustrative UI is labeled.
- [x] Visual semantic events and SFX share source-to-output-to-local conversion; 38 cues, mix manifest hash matches.
- [x] New stem-based mix replaces the old v3 audio; voice/bed separation 17.16 LU.
- [x] Actual output examined: all 20 scenes, 9 semantic actions (27 frames), 8 layout transitions (24 frames).
- [x] Final rendered audio vs expected mix: measured lag 0 ms, correlation 0.998967.
- [x] Caption 35/35 and camera contract pass; HF lint/runtime/layout/contrast errors 0, warnings 0.
- [x] 1080x1920/30fps, 42.433333s, 1273 frames, decode errors 0; final -14.10 LUFS/-1.53 dBTP.
- [ ] Direct human listening to the entire final soundtrack: not performed; frame/event/PCM checks are not a listening claim.

## Implementation decisions (v4, verified after encode)

The per-scene prescriptions above were audit proposals, not a claim that every suggestion shipped.
- Preserved the approved opening exactly. New typography roles appear in the security badge, source URLs, code and labels.
- Rejected an arbitrary five-screenshot minimum. Three directly relevant sources fit this 42-second narration: Google introduction, GitHub role files, README expert-review warning.
- Shop/code/test interfaces are labeled illustrative examples, never actual Mantis execution evidence.
- Multi-stage motion belongs to demonstration scenes; clean presenter holds remain clean. No arbitrary motion-count requirement.
- Captions remain below the face during camera resize and move to the card-safe position after resize, preserving the approved camera contract.
- build.py add() converts source time to output/local time once, substitutes the same cue into JS and events.json; mix.py reads only that generated event authority.
- EP02 stem normalization, ducking and static master gain replace the stale v3 mix. Event SHA256, original caption/cut identity and independent runtime checks are retained in qc/.
- Redundant presenter summaries are removed; explicit camera punches follow emphasis.

Evidence: qc/semantic-contract.json, qc/caption-audit.json, qc/camera-contract.json, qc/audio/mix-report.json. Final rendered proof is tracked in REPORT.md.

## Final implementation entrypoints

- build.py: add() maps named source events and substitutes local GSAP times; shot() ports ep03 image-coordinate framing and outline drawing.
- build.py: shop_body()/SHOP_CSS maintain the same synthetic order between exposure and denied states.
- build.py: s09-map/s12-test/s13-patch show request traversal, failure and owner check; s18-expert highlights the actual warning; s20-comment uses stepped typing.
- mix.py: event-based SFX, calibrated voice/bed stems, ducking and static master gain adapted from ep02/ep05.
- qc/verify_actions.py: actual encoded frame regions and independently decoded audio cross-correlation, using existing .venv-qwen-tts Python for NumPy.
- qc/action-verification.json, qc/render-verification.json, qc/final-check.json: final measured evidence.
- qc/v3-v4-comparison.jpg, qc/action-filmstrip.jpg, qc/transition-sheet.jpg: actual MP4 frame evidence.
