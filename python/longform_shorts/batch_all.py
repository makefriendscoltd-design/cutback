"""여러 롱폼을 순서대로 끝까지: 다운로드 → 전사 → 구간·헤드카피 → 렌더 → 제목·설명 → 시간 배정 → 예약 업로드 → 관련 동영상.

  .venv/bin/python batch_all.py VIDEO_ID [VIDEO_ID ...]
  .venv/bin/python batch_all.py            # 인자 없으면 jobs/_todo.json 전체 (매일 자동 실행용)

단계마다 결과 파일이 있으면 건너뛰므로 끊겨도 같은 명령으로 이어진다.
쿼터가 막히면 업로드만 멈추고 나머지 영상의 제작은 계속한다(다음 실행에서 업로드 재개).
진행 로그: jobs/_batch.log
"""
from __future__ import annotations

import datetime as dt
import subprocess
import sys
import traceback

import lfs
import lfs_core as core
import yt_schedule as ys

LOG = core.JOBS / "_batch.log"
TRACK = "/Users/apple/orca/projects/aimax-crm-observability/bin/aimax-crm-track"


def log(msg):
    line = f"{dt.datetime.now():%m-%d %H:%M} {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def one(vid: str, svc) -> str:
    d = core.download(f"https://youtu.be/{vid}")
    cfg = core.load_json(d / "config.json", {})
    cfg.setdefault("caption_pos", "below")   # 나민수 롱폼은 화면 녹화 + 원본 자막 없음
    cfg.setdefault("theme", "aimax")
    core.save_json(d / "config.json", cfg)
    core.transcribe(d)
    plan = core.plan(d, 12)
    log(f"{vid} 구간 {len(plan['clips'])}개")
    todo = [c["id"] for c in plan["clips"] if c.get("selected") and not (d / "out" / f"{c['id']}.json").exists()]
    if todo:
        lfs.render_many(d, todo)
    bad = [k for k, v in lfs.STATUS.items() if v["state"] == "error"]
    if bad:
        log(f"{vid} 렌더 실패 {bad}")
    if not all(c.get("yt_title") for c in core.load_json(d / "plan.json")["clips"]):
        ys.write_meta(d)
    try:
        got = ys.resolve_holds(d, svc)
        if got:
            log(f"{vid} 보류 항목 연결 {got}")
    except Exception as e:  # noqa: BLE001
        log(f"{vid} 보류 연결 보류: {str(e)[:60]}")
    sched = core.load_json(d / "schedule.json", {"items": []})
    if not all(i.get("video_id") for i in sched["items"]) or not sched["items"]:
        ys.make_plan(d, svc)
    before = sum(1 for i in core.load_json(d / "schedule.json")["items"] if i.get("video_id"))
    sched = ys.upload(d, svc, limit=100)
    errs_now = " ".join(str(i.get("error", "")) for i in sched["items"] if not i.get("video_id"))
    if "uploadLimitExceeded" in errs_now or "Video Uploads per day" in errs_now:
        # 채널 하루 업로드 개수 한도 — Studio(Aside)도 같은 한도라 대체 불가. 다음 날 자동 실행에서 이어감
        log(f"{vid} 채널 하루 업로드 한도 도달 → 내일 이어서")
    elif "quota" in errs_now.lower():
        log(f"{vid} API 쿼터 막힘 → Aside 로 Studio 직접 업로드")
        sched = ys.aside_upload_pending(d, svc=svc)
    try:
        moved = ys.audit_fix(d, svc)   # 최종 안전망: 채널 전체와 다시 대조, 겹치면 이쪽을 옮김
        if moved:
            log(f"{vid} ⚠ 겹침 자동 이동 {moved}")
    except Exception as e:  # noqa: BLE001
        log(f"{vid} 겹침 대조 보류: {str(e)[:80]}")
    sched = ys.related_all(d)
    try:
        bad = ys.verify(d, svc)   # API 가 되면 예약 시각을 다시 대조(Aside 로 올린 것 포함)
        if bad:
            log(f"{vid} ⚠ 예약 상태 불일치 {bad}")
    except Exception as e:  # noqa: BLE001 — 쿼터로 조회도 막히면 다음 실행에서 확인
        log(f"{vid} 검증 보류: {str(e)[:80]}")
    sched = core.load_json(d / "schedule.json")
    items = sched["items"]
    up = sum(1 for i in items if i.get("video_id"))
    rel = sum(1 for i in items if str(i.get("related", "")).startswith("OK"))
    errs = [i.get("error", "")[:80] for i in items if i.get("error")]
    new = up - before
    if new > 0:
        subprocess.run([TRACK, "emit", "--source-system", "cutback-longform-shorts", "--channel", "youtube_shorts",
                        "--stage", "planned", "--status", "success", "--origin-agent", "claude-code", "--project", "cutback",
                        "--campaign", f"naminsoo-{vid}-shorts", "--count", str(new),
                        "--evidence-path", str(d / "schedule.json"), "--dedupe-key", f"naminsoo-{vid}-shorts-scheduled-{up}"],
                       capture_output=True)
    span = f"{items[0]['publish_at'][:16]} ~ {items[-1]['publish_at'][:16]}" if items else "-"
    log(f"{vid} 업로드 {up}/{len(items)} 관련동영상 {rel}/{len(items)} | {span}" + (f" | 오류 {errs[:2]}" if errs else ""))
    return "quota" if any("quota" in e.lower() for e in errs) else "ok"


def main():
    import fcntl
    lock = open(core.JOBS / "_batch.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)   # 이미 돌고 있으면 겹쳐 돌지 않음
    except OSError:
        log("이미 실행 중 — 이번 회차 건너뜀")
        return
    svc = ys.yt()
    try:
        ys.channel(svc)
    except Exception as e:  # noqa: BLE001
        log(f"채널 확인 실패(쿼터?): {str(e)[:80]}")
    ids = sys.argv[1:] or [x[1] for x in dict.fromkeys(map(tuple, core.load_json(core.JOBS / "_todo.json", [])))]
    for vid in dict.fromkeys(ids):
        lfs.STATUS.clear()
        try:
            one(vid, svc)
        except Exception as e:  # noqa: BLE001 — 영상 하나 실패해도 다음 영상 진행
            log(f"{vid} 실패: {e!r}")
            traceback.print_exc()
    log("전체 끝")


if __name__ == "__main__":
    main()
