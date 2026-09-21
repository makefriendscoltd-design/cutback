# 롱폼 → 숏폼 클리핑 (lfs)

유튜브 롱폼 링크 하나 → 의미 단위 숏폼 여러 개 (1080x1920, 검정 배경 + 헤드카피 2줄 + 가운데 원본 + 자막).
레이아웃은 인스타 DdYjImEiUL1 실측값.

## 설치 (맥, Apple Silicon)
    uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
    # ffmpeg(brew), loopguard agent-run(구간·헤드카피 LLM) 필요. 폰트는 packages/shorts-composer/assets/fonts

## 사용
    .venv/bin/python lfs.py run "<유튜브 URL>"          # 다운로드→전사→구간·헤드카피→검수 페이지 자동 오픈
    .venv/bin/python lfs.py review <영상ID>              # 검수 페이지 다시 열기
    .venv/bin/python lfs.py render <영상ID> [c01 c03]    # 검수 없이 렌더

검수 페이지(127.0.0.1:8765): 후보별 사용 여부 체크, 헤드카피 2줄 수정(미리보기 즉시 반영),
하단 문구(1줄=우리 계정, 2줄=<원본 채널>), 자막 위치(영상 안/아래/끄기) → "선택한 것 렌더".
결과: `jobs/<영상ID>/out/cNN.mp4`

## 파이프라인
1. yt-dlp 1080p 다운로드 → 16k wav
2. mlx-whisper large-v3-turbo 단어 타임스탬프 전사 (영상 제목을 힌트로)
3. agent-run(LLM): 의미 단위 구간 + head1(맥락)/head2(후킹) + STT 오타 교정표(fixes)
4. 컷: 필러 단어 제거 + 단어 사이 틈/늘어진 단어 안의 묵음·웅얼거림을 음향으로 확인해 제거
5. ffmpeg 한 번에 trim·concat·레이아웃·ASS 자막·라우드니스(-14 LUFS)

## 알려진 한계
- whisper는 '음·어'를 받아 적지 않음 → 음향(에너지·음색 변화)으로 잡는다. 말이 빽빽한 영상은 줄어드는 폭이 작다(5~10%)
- 원본에 자막이 박혀 있으면 자막 위치를 '영상 아래' 또는 '넣지 않음'으로
- 세로(9:16) 원본은 미지원

## 유튜브 쇼츠 예약 업로드 (나민수 AI)
    .venv/bin/python yt_schedule.py auth                 # 최초 1회 구글 로그인(나민수 채널 선택) → secrets/ (깃 제외)
    .venv/bin/python yt_schedule.py meta <영상ID>         # 제목·설명 초안(검수 페이지에서 수정 가능)
    .venv/bin/python yt_schedule.py plan <영상ID>         # 시간 배정 → jobs/<ID>/schedule.json
    .venv/bin/python yt_schedule.py upload <영상ID> --yes # 비공개+예약 업로드 → Aside 로 관련 동영상 지정
    .venv/bin/python yt_schedule.py status <영상ID>

- 하루 5칸(07:30·13:30·15:30·17:30·22:30). 채널 전체 영상(예약분 포함)과 최근 2주 반복 시간대에서 ±90분 안이면 건너뜀
- 업로드 직전 채널을 다시 조회해 그 사이 생긴 예약과도 겹치면 올리지 않음. 채널명에 '나민수'가 없으면 중단
- 관련 동영상은 API 항목이 없어 `aside repl` + `aside_related.js` 로 Studio 에서 지정하고, 새로고침 후 값을 다시 읽어 확인
- 업로드 1건 = API 쿼터 1600. 쿼터 소진 시 멈추고 다음 실행에서 이어감
