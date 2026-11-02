"""렌더된 숏폼을 나민수 채널에 '예약 공개'로 올린다. 하루 5개, 다른 쇼츠와 시간 안 겹치게.

  .venv/bin/python yt_schedule.py plan <job_id>             # 슬롯 배정만 (업로드 안 함) → jobs/<id>/schedule.json
  .venv/bin/python yt_schedule.py upload <job_id> --yes     # 배정된 것 중 아직 안 올린 것을 최대 5개 업로드(비공개+publishAt)
  .venv/bin/python yt_schedule.py status <job_id>

- 업로드는 비공개 + publishAt 이라 공개는 유튜브가 그 시각에 한다(우리 쪽 상시 실행 불필요).
- 업로드 1건 = API 쿼터 1600. 프로젝트 하루 한도(기본 1만)를 다른 도구와 같이 쓰므로 1회 최대 5개.
- 겹침 판정: 채널의 모든 영상(공개 시각 + 예약 공개 시각) + 최근 2주 반복 시간대(예: 매일 11:00/20:00) 기준 ±BUFFER 분.
- 토큰은 youtubereply 의 나민수 토큰을 읽기만 한다(갱신된 토큰을 원본 파일에 쓰지 않음).
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import sys
from pathlib import Path

import lfs_core as core

KST = dt.timezone(dt.timedelta(hours=9))
# 토큰은 이 폴더 secrets/ 에 따로 둔다(깃 제외). 클라이언트는 회사 구글 프로젝트 것을 경로로만 참조
TOKEN = Path(os.environ.get("LFS_YT_TOKEN", str(core.ROOT / "secrets" / "token.naminsoo.json")))
CLIENT = Path(os.environ.get("LFS_YT_CLIENT", "/Users/apple/coding/youtubereply/client_secret.json"))
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]   # 업로드 + 비공개 예약 영상 조회
# 다른 채널 토큰이면 중단. 채널명은 바뀌므로(나민수 AI → 나교장의 AI사장학교) 채널 ID 로 확인한다
DEFAULT_CHANNEL_ID = (core.ROOT / "secrets" / "channel_id").read_text().strip()   # 나민수(나교장의 AI사장학교)
EXPECT_CHANNEL_ID = os.environ.get("LFS_YT_CHANNEL_ID") or DEFAULT_CHANNEL_ID
CHANNEL_NAME = os.environ.get("LFS_YT_CHANNEL_NAME") or "나민수 AI"   # 제목·설명 프롬프트에 들어가는 채널 이름
SLOTS = ["07:30", "13:30", "15:30", "17:30", "22:30"]       # 기존 09:00·11:00·20:00 과 90분 이상 떨어진 후보
BUFFER_MIN = 90
PER_DAY = 5
PER_RUN = 5


def yt():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    if not TOKEN.exists():
        sys.exit("로그인 필요: .venv/bin/python yt_schedule.py auth  (브라우저에서 나민수 채널 선택)")
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds.valid:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def auth():
    from google_auth_oauthlib.flow import InstalledAppFlow
    creds = InstalledAppFlow.from_client_secrets_file(str(CLIENT), SCOPES).run_local_server(port=0, prompt="consent")
    TOKEN.parent.mkdir(exist_ok=True)
    TOKEN.write_text(creds.to_json())
    os.chmod(TOKEN, 0o600)
    if os.environ.get("LFS_YT_CHANNEL_ID") == "new":   # 새 채널 연결: 검사 대신 어떤 채널인지 기록
        from googleapiclient.discovery import build
        ch = build("youtube", "v3", credentials=creds, cache_discovery=False).channels().list(part="snippet", mine=True).execute()["items"][0]
        TOKEN.with_suffix(".channel.json").write_text(json.dumps({"id": ch["id"], "title": ch["snippet"]["title"]}, ensure_ascii=False))
        print("채널:", ch["snippet"]["title"], ch["id"])
        return
    print("채널:", channel(yt())["snippet"]["title"])


class Offline:
    """로그인 전 미리보기용: 공개된 쇼츠 시각만 yt-dlp 로 모은다(비공개 예약분은 못 봄)."""
    def __init__(self, handle="@naminsoo_aimax", n=60):
        import subprocess
        ytdlp = str(core.ROOT / ".venv" / "bin" / "yt-dlp")
        ids = subprocess.run([ytdlp, "--flat-playlist", "--playlist-end", str(n), "--print", "%(id)s",
                              f"https://www.youtube.com/{handle}/shorts"], capture_output=True, text=True).stdout.split()
        ts = subprocess.run([ytdlp, "--skip-download", "--no-warnings", "--print", "%(timestamp)s", *[f"https://youtu.be/{i}" for i in ids]],
                            capture_output=True, text=True).stdout.split()
        self.times = [dt.datetime.fromtimestamp(int(t), KST) for t in ts if t.isdigit()]


# 쿼터 막혔을 때 쓰는 마지막 조회 결과. 채널마다 따로
CACHE = core.JOBS / ("_channel_cache.json" if EXPECT_CHANNEL_ID == DEFAULT_CHANNEL_ID else f"_channel_cache.{EXPECT_CHANNEL_ID}.json")


def schedules():
    """이 채널의 schedule.json 들. channel_id 가 없는 예전 기록은 나민수 채널 것"""
    return [f for f in core.JOBS.glob("*/schedule.json")
            if core.load_json(f, {}).get("channel_id", DEFAULT_CHANNEL_ID) == EXPECT_CHANNEL_ID]


def _quota(e) -> bool:
    return "quota" in str(e).lower()


def channel(svc):
    if isinstance(svc, Offline):
        return {"snippet": {"title": "나민수 AI (미리보기: 공개분만)"}}
    try:
        ch = svc.channels().list(part="snippet,contentDetails", mine=True).execute()["items"][0]
    except Exception as e:  # noqa: BLE001
        if not _quota(e) or not CACHE.exists():
            raise
        ch = core.load_json(CACHE)["channel"]
        core.log("쿼터 막힘 — 채널 정보는 마지막 조회본 사용")
    if ch.get("id") != EXPECT_CHANNEL_ID:
        sys.exit(f"토큰 채널이 '{ch['snippet']['title']}'({ch.get('id')}) — {EXPECT_CHANNEL_ID} 아님. 중단")
    return ch


def our_video_ids() -> set[str]:
    return {i["video_id"] for f in schedules()
            for i in core.load_json(f, {"items": []})["items"] if i.get("video_id")}


def other_jobs_planned(d: Path) -> list[dt.datetime]:
    """다른 작업에서 배정만 되고 아직 안 올라간 시각도 자리 차지로 본다."""
    return [dt.datetime.fromisoformat(i["publish_at"]) for f in schedules() if f.parent != d
            for i in core.load_json(f, {"items": []})["items"] if not i.get("video_id")]


def occupied(svc, ch, max_items=2000, with_ids=False):
    """채널 영상들의 공개(또는 예약 공개) 시각. 비공개 예약분까지 포함.

    업로드 목록(playlistItems)은 50개씩 넘겨 읽는 사이 새 업로드가 끼면 순서가 밀려 일부를 건너뛴다.
    그래서 목록에서 본 ID + 예전에 본 ID(캐시) + 우리 기록 ID 를 합쳐 videos.list 로 'ID 직접 조회'한다.
    """
    if isinstance(svc, Offline):
        return [(t, "") for t in svc.times] if with_ids else svc.times
    pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while len(ids) < max_items:
        r = svc.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    if CACHE.exists():
        ids += [v for _, v in core.load_json(CACHE).get("pairs", [])]
    ids += list(our_video_ids())
    ids = list(dict.fromkeys(i for i in ids if i))
    out = []
    for i in range(0, len(ids), 50):
        r = svc.videos().list(part="status,snippet", id=",".join(ids[i:i + 50])).execute()
        for v in r["items"]:   # 삭제된 영상은 응답에 없으므로 자연히 빠진다
            t = v["status"].get("publishAt") or v["snippet"].get("publishedAt")
            if t:
                out.append((dt.datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(KST), v["id"]))
    return out if with_ids else [t for t, _ in out]


def busy_and_recurring(svc, ch, d: Path):
    try:
        pairs = occupied(svc, ch, with_ids=True)
        core.save_json(CACHE, {"channel": ch, "at": dt.datetime.now(KST).isoformat(),
                               "pairs": [[t.isoformat(), v] for t, v in pairs]})
    except Exception as e:  # noqa: BLE001
        if not _quota(e) or not CACHE.exists():
            raise
        c = core.load_json(CACHE)
        pairs = [(dt.datetime.fromisoformat(t), v) for t, v in c["pairs"]]
        # 캐시 이후 우리가 올린 것(Aside 포함)도 자리 차지로 추가
        known = {v for _, v in pairs}
        pairs += [(dt.datetime.fromisoformat(i["publish_at"]), i["video_id"]) for f in schedules()
                  for i in core.load_json(f, {"items": []})["items"] if i.get("video_id") and i["video_id"] not in known]
        core.log(f"쿼터 막힘 — 채널 예약 목록은 {c['at'][:16]} 조회본 + 우리 업로드분으로 판단")
    ours = our_video_ids()
    # Studio(Aside)로 올린 영상은 업로드 목록에 늦게 잡힌다 → 우리 기록(schedule.json)도 항상 합친다
    known = {v for _, v in pairs}
    pairs = pairs + [(dt.datetime.fromisoformat(i["publish_at"]), i["video_id"]) for f in schedules()
                     for i in core.load_json(f, {"items": []})["items"] if i.get("video_id") and i["video_id"] not in known]
    # 반복 시간대는 '남의' 쇼츠로만 판단 — 우리 07:30·13:30 칸이 반복으로 잡혀 스스로 막히는 걸 방지
    recur = recurring_times([t for t, vid in pairs if vid not in ours])
    return [t for t, _ in pairs] + other_jobs_planned(d), recur


def recurring_times(times: list[dt.datetime], days=14, min_days=3) -> list[dt.time]:
    """최근 2주 동안 3일 이상 같은 시각에 올라간 시간대 = 앞으로도 쓸 시간대로 보고 피한다."""
    since = dt.datetime.now(KST) - dt.timedelta(days=days)
    per_day = collections.defaultdict(set)
    for t in times:
        if since <= t <= dt.datetime.now(KST):
            per_day[(t.hour, t.minute)].add(t.date())
    return [dt.time(h, m) for (h, m), ds in per_day.items() if len(ds) >= min_days]


def clashes(when: dt.datetime, busy: list[dt.datetime], recur: list[dt.time]) -> bool:
    buf = dt.timedelta(minutes=BUFFER_MIN)
    if any(abs(when - b) < buf for b in busy):
        return True
    for rt in recur:
        r = dt.datetime.combine(when.date(), rt, KST)
        if abs(when - r) < buf:
            return True
    return False


def make_plan(d: Path, svc, save=True) -> dict:
    ch = channel(svc)
    busy, recur = busy_and_recurring(svc, ch, d)
    if core.config_of(d).get("ignore_recurring"):   # 실제 예약된 영상만 피한다(과거 반복 시간대는 무시)
        recur = []
    old = core.load_json(d / "schedule.json", {"items": []})
    done = {i["clip"]: i for i in old["items"] if i.get("video_id") or i.get("hold")}
    plan = core.load_json(d / "plan.json")
    clips = [c for c in plan["clips"] if c.get("selected") and (d / "out" / f"{c['id']}.mp4").exists()]
    # 후킹 점수 높은 것부터 먼저 공개
    clips.sort(key=lambda c: (c.get("rank", 999), -int(c.get("hook") or 0)))   # rank 를 주면 그 순서가 우선
    taken = [dt.datetime.fromisoformat(i["publish_at"]) for i in done.values()]
    items = list(done.values())
    now = dt.datetime.now(KST)
    day = now.date()
    pending = [c for c in clips if c["id"] not in done]
    per_day = int(core.config_of(d).get("per_day") or PER_DAY)   # 영상별로 하루 개수를 줄일 수 있다(config.json per_day)
    while pending:
        if day > now.date() + dt.timedelta(days=180):
            raise RuntimeError("180일 안에 빈 칸이 없음 — SLOTS/BUFFER 확인")
        count = sum(1 for t in taken if t.date() == day)
        for s in SLOTS:
            if not pending or count >= per_day:
                break
            when = dt.datetime.combine(day, dt.time.fromisoformat(s), KST)
            if when < now + dt.timedelta(hours=2) or clashes(when, busy + taken, recur):
                continue
            c = pending.pop(0)
            taken.append(when)
            count += 1
            items.append({"clip": c["id"], "publish_at": when.isoformat(), "title": title_of(c)})
        day += dt.timedelta(days=1)
    items.sort(key=lambda i: i["publish_at"])
    out = {"channel": ch["snippet"]["title"], "channel_id": ch.get("id", EXPECT_CHANNEL_ID), "recurring_avoided": [t.strftime("%H:%M") for t in recur],
           "buffer_min": BUFFER_MIN, "items": items}
    if save:
        core.save_json(d / "schedule.json", out)
    return out


META_PROMPT = """너는 유튜브 '{channel}' 채널 쇼츠 담당이야. 아래 쇼츠들은 {owner} 롱폼에서 잘라낸 거야.
쇼츠마다 유튜브 제목과 설명글을 써.

채널 기존 쇼츠 형식(따라 할 것):
- 제목: 20자 안팎, "~하는 법", "~한 실제 사례" 처럼 무슨 내용인지 한눈에. 해시태그·이모지·따옴표 없음
  예) "클로드 코드로 왓츠앱 상담 봇 만들기", "프롬프트는 짧게, 클로드 결과는 더 좋게", "내 컴퓨터에 AI를 직접 깔아 쓰는 법"
- 설명: 첫 문단 1~2문장 후킹 + "저장하고 끝까지 보세요!" / 빈 줄 / 핵심 2~3개를 "첫째, ~입니다." 식으로 한 문단씩
- "이 남자 미쳤습니다" 같은 남의 영상 소개 문장은 쓰지 마.
- 영상에서 실제로 한 말만. 숫자·사례 지어내지 마.
- 설명 맨 끝 줄에 넣지 마: 링크, 해시태그 (코드가 붙임)

JSON만 출력. {{"clips":[{{"id":"c01","title":"...","description":"..."}}]}}

{clips}
"""


def write_meta(d: Path) -> dict:
    """LLM 으로 제목·설명 초안을 만들어 plan.json 의 yt_title / yt_desc 에 저장(검수 페이지에서 수정 가능)."""
    tr = core.load_json(d / "transcript.json")
    plan = core.load_json(d / "plan.json")
    fixes = plan.get("fixes", [])
    blocks = []
    for c in plan["clips"]:
        text = " ".join(s["text"] for s in tr["segments"][c["start"]:c["end"] + 1])
        for f in fixes:
            text = text.replace(f["from"], f["to"])
        blocks.append(f"## {c['id']} (헤드카피: {c['head1']} / {c['head2']})\n{text}")
    owner = "나민수 본인" if EXPECT_CHANNEL_ID == DEFAULT_CHANNEL_ID else "원본"
    raw = core.ask_llm(META_PROMPT.format(channel=CHANNEL_NAME, owner=owner, clips="\n\n".join(blocks)))
    new = {x["id"]: x for x in raw["clips"]}
    for c in plan["clips"]:
        if c["id"] in new:
            c["yt_title"] = new[c["id"]]["title"][:100]
            c["yt_desc"] = new[c["id"]]["description"]
    core.save_json(d / "plan.json", plan)
    return plan


def title_of(c) -> str:
    return (c.get("yt_title") or f"{c['head1']} {c['head2']}").strip()[:100]


def description_of(d: Path, clip_id: str = "") -> str:
    meta = core.load_json(d / "meta.json", {})
    c = next((x for x in core.load_json(d / "plan.json")["clips"] if x["id"] == clip_id), {})
    body = c.get("yt_desc") or f"{c.get('head1', '')} {c.get('head2', '')}"
    return f"{body}\n\n풀영상: {meta.get('url', '')}"


def upload(d: Path, svc, limit=PER_RUN):
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    sched = core.load_json(d / "schedule.json")
    ch = channel(svc)
    busy, recur = busy_and_recurring(svc, ch, d)   # 올리기 직전에 다시 조회해서 그 사이 생긴 예약과도 안 겹치게
    if core.config_of(d).get("ignore_recurring"):
        recur = []
    n = 0
    for it in sched["items"]:
        if it.get("video_id") or it.get("hold") or n >= limit:
            continue
        if it.get("draft_id"):
            finish_draft(d, it, svc)
            core.save_json(d / "schedule.json", sched)
            continue
        when = dt.datetime.fromisoformat(it["publish_at"])
        if when < dt.datetime.now(KST) + dt.timedelta(minutes=30):
            it["error"] = "예약 시각이 지나거나 임박 — plan 다시 돌려야 함"
            continue
        # 아직 안 올린 항목이라 채널 목록에 자기 자신은 없다 → 아무것도 빼지 않고 그대로 검사
        # (예전엔 '같은 시각'을 자기 자신으로 보고 빼서 정확히 겹치는 다른 영상을 놓쳤음)
        mine_planned = [dt.datetime.fromisoformat(i["publish_at"]) for i in sched["items"] if i is not it and not i.get("video_id")]
        others = [b for b in busy if b not in mine_planned]
        if clashes(when, others, recur):
            it["error"] = "그 사이 다른 영상과 시간이 겹침 — plan 다시 돌려야 함"
            continue
        body = {"snippet": {"title": it["title"], "description": description_of(d, it["clip"]), "categoryId": "27",
                            "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
                "status": {"privacyStatus": "private", "publishAt": when.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                           "selfDeclaredMadeForKids": False}}
        media = MediaFileUpload(str(d / "out" / f"{it['clip']}.mp4"), mimetype="video/mp4", resumable=True)
        try:
            r = svc.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        except HttpError as e:
            it["error"] = str(e)[:300]
            core.save_json(d / "schedule.json", sched)
            if "quota" in str(e).lower() or "uploadLimitExceeded" in str(e):
                core.log("쿼터/채널 업로드 한도 — 내일 다시 실행")
                break
            continue
        it.update(video_id=r["id"], uploaded_at=dt.datetime.now(KST).isoformat())
        it.pop("error", None)
        core.save_json(d / "schedule.json", sched)
        core.log(f"예약 완료 {it['clip']} → {it['publish_at']} https://youtu.be/{r['id']}")
        n += 1
    return sched


def set_related(video_id: str, target_title: str, target_id: str) -> str:
    """Aside 브라우저로 Studio '관련 동영상'을 롱폼으로 지정. API 에 이 항목이 없어서 UI 로 한다."""
    import subprocess
    js = (core.ROOT / "aside_related.js").read_text()
    code = (f"const VID={json.dumps(video_id)}; const TARGET_TITLE={json.dumps(target_title, ensure_ascii=False)}; "
            f"const TARGET_ID={json.dumps(target_id)};\n{js}")
    try:
        out = subprocess.run(["aside", "repl", code], capture_output=True, text=True, timeout=240).stdout
    except subprocess.TimeoutExpired:
        return "FAIL timeout"
    line = [l for l in out.splitlines() if "RESULT:" in l]
    return line[-1].split("RESULT:", 1)[1].strip() if line else "FAIL no result"


def related_all(d: Path):
    sched = core.load_json(d / "schedule.json")
    meta = core.load_json(d / "meta.json", {})
    for it in sched["items"]:
        if it.get("video_id") and not str(it.get("related", "")).startswith("OK"):
            it["related"] = set_related(it["video_id"], meta.get("title", ""), meta.get("id", d.name))
            core.log(f"관련 동영상 {it['clip']}: {it['related']}")
            core.save_json(d / "schedule.json", sched)
    return sched


def _ko_date(t: dt.datetime) -> str:
    return f"{t.year}. {t.month}. {t.day}."


def _ko_time(t: dt.datetime) -> str:
    h = t.hour % 12 or 12
    return f"{'오전' if t.hour < 12 else '오후'} {h}:{t.minute:02d}"


def aside_upload(d: Path, it: dict) -> str:
    """API 쿼터가 막혔을 때: Aside 브라우저로 Studio 에 직접 예약 업로드. 영상 파일은 임시 로컬 서버로 넘긴다."""
    import functools
    import http.server
    import subprocess
    import threading
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(d / "out"))
    handler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        when = dt.datetime.fromisoformat(it["publish_at"]).astimezone(KST)
        consts = {"CID": (core.ROOT / "secrets" / "channel_id").read_text().strip(),
                  "FILE_URL": f"http://127.0.0.1:{srv.server_address[1]}/{it['clip']}.mp4",
                  "TITLE": it["title"], "DESC": description_of(d, it["clip"]),
                  "RELATED_TITLE": core.load_json(d / "meta.json", {}).get("title", ""),
                  "DATE_TEXT": _ko_date(when), "TIME_TEXT": _ko_time(when)}
        code = "".join(f"const {k}={json.dumps(v, ensure_ascii=False)};\n" for k, v in consts.items())
        code += (core.ROOT / "aside_upload.js").read_text()
        try:
            out = subprocess.run(["aside", "repl", code], capture_output=True, text=True, timeout=900).stdout
        except subprocess.TimeoutExpired:
            return "FAIL timeout"
        (d / "out" / f"{it['clip']}.aside.log").write_text(out)
        line = [l for l in out.splitlines() if "RESULT:" in l]
        draft = [l.split("VIDEO_ID", 1)[1].strip() for l in out.splitlines() if "STEP VIDEO_ID" in l]
        if draft and draft[-1]:
            it["draft_id"] = draft[-1]
        return line[-1].split("RESULT:", 1)[1].strip() if line else "FAIL no result"
    finally:
        srv.shutdown()


def resolve_holds(d: Path, svc) -> list[str]:
    """보류(ID 모름) 항목을 채널 영상 제목으로 찾아 연결."""
    sched = core.load_json(d / "schedule.json")
    held = [i for i in sched["items"] if i.get("hold") and not i.get("video_id")]
    if not held:
        return []
    pairs = occupied(svc, channel(svc), with_ids=True)
    ids = [v for _, v in pairs]
    titles = {}
    for k in range(0, len(ids), 50):
        for v in svc.videos().list(part="snippet,status", id=",".join(ids[k:k + 50])).execute()["items"]:
            titles.setdefault(v["snippet"]["title"], []).append(v)
    done = []
    known = our_video_ids()
    for it in held:
        cands = [v for v in titles.get(it["title"], []) if v["id"] not in known]
        since = dt.datetime.fromisoformat(it["hold"]) if isinstance(it["hold"], str) else dt.datetime.now(KST)
        if not cands and dt.datetime.now(KST) - since > dt.timedelta(hours=6):
            it.pop("hold", None)   # 6시간 지나도 채널에 없음 = 업로드가 거절됐던 것 → 다시 올릴 수 있게 해제
            done.append(f"{it['clip']} 보류 해제(채널에 없음)")
            continue
        if len(cands) == 1:
            it.update(video_id=cands[0]["id"], via="aside(보류 후 연결)")
            it.pop("hold", None); it.pop("error", None)
            done.append(f"{it['clip']}={cands[0]['id']}")
    core.save_json(d / "schedule.json", sched)
    return done


def finish_draft(d: Path, it: dict, svc) -> bool:
    """Aside 가 파일만 올리고 멈춘 초안을 API 로 예약까지 마무리(쿼터 있을 때)."""
    when = dt.datetime.fromisoformat(it["publish_at"])
    try:
        svc.videos().update(part="snippet,status", body={"id": it["draft_id"],
            "snippet": {"title": it["title"], "description": description_of(d, it["clip"]), "categoryId": "27",
                        "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
                       "publishAt": when.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")}}).execute()
    except Exception as e:  # noqa: BLE001
        core.log(f"초안 {it['draft_id']} 마무리 보류: {str(e)[:80]}")
        return False
    it.update(video_id=it.pop("draft_id"), via="aside-file+api-schedule", uploaded_at=dt.datetime.now(KST).isoformat())
    it.pop("error", None)
    return True


def aside_upload_pending(d: Path, limit=100, svc=None) -> dict:
    sched = core.load_json(d / "schedule.json")
    n = 0
    for it in sched["items"]:
        if it.get("video_id") or it.get("hold") or n >= limit:
            continue
        if it.get("draft_id"):   # 전에 멈춘 초안이 있으면 새로 올리지 말고 그걸 마무리
            if svc and finish_draft(d, it, svc):
                n += 1
            core.save_json(d / "schedule.json", sched)
            continue
        if dt.datetime.fromisoformat(it["publish_at"]) < dt.datetime.now(KST) + dt.timedelta(minutes=30):
            continue
        res = aside_upload(d, it)
        core.log(f"Aside 업로드 {it['clip']}: {res}")
        if res.startswith("OK"):
            it.update(video_id=res.split()[1], via="aside",
                      uploaded_at=dt.datetime.now(KST).isoformat())
            it.pop("error", None)
            n += 1
        else:
            it["error"] = "aside: " + res
            if "done clicked" in (d / "out" / f"{it['clip']}.aside.log").read_text(errors="ignore") and not it.get("draft_id"):
                it["hold"] = dt.datetime.now(KST).isoformat()   # 예약은 눌렸는데 ID 를 모름 → 재업로드 금지, resolve_holds 로 나중에 연결
            if it.get("draft_id") and svc:
                finish_draft(d, it, svc)
        core.save_json(d / "schedule.json", sched)
        if not res.startswith("OK"):
            break   # 화면 구조가 바뀐 경우 연달아 실패하지 않게 멈춤
    return sched


def verify(d: Path, svc) -> list[str]:
    """API 로 예약 상태를 다시 읽어 schedule.json 과 대조. 어긋난 clip id 목록."""
    sched = core.load_json(d / "schedule.json")
    ids = [i["video_id"] for i in sched["items"] if i.get("video_id")]
    got = {}
    for k in range(0, len(ids), 50):
        for v in svc.videos().list(part="status", id=",".join(ids[k:k + 50])).execute()["items"]:
            got[v["id"]] = v["status"]
    bad = []
    for i in sched["items"]:
        if not i.get("video_id"):
            continue
        st = got.get(i["video_id"])
        want = dt.datetime.fromisoformat(i["publish_at"])
        pa = st and st.get("publishAt")
        ok = st and ((st["privacyStatus"] == "private" and pa and
                      dt.datetime.fromisoformat(pa.replace("Z", "+00:00")) == want) or
                     (st["privacyStatus"] == "public" and want <= dt.datetime.now(KST)))
        i["verified"] = bool(ok)
        if not ok:
            bad.append(i["clip"])
    core.save_json(d / "schedule.json", sched)
    return bad


def audit_fix(d: Path, svc) -> list[str]:
    """업로드 후 최종 안전망: 채널 실제 예약 시각 기준으로 이 작업 쇼츠가 다른 영상과 ±BUFFER 안이면
    이 작업 쪽을 가장 빠른 빈 칸으로 옮긴다. 옮긴 목록 반환."""
    ch = channel(svc)
    sched = core.load_json(d / "schedule.json")
    moved = []
    for it in sched["items"]:
        vid = it.get("video_id")
        if not vid:
            continue
        pairs = occupied(svc, ch, with_ids=True)
        known = {v for _, v in pairs}
        pairs += [(dt.datetime.fromisoformat(i["publish_at"]), i["video_id"]) for f in schedules()
                  for i in core.load_json(f, {"items": []})["items"] if i.get("video_id") and i["video_id"] not in known]
        real = {v: t for t, v in pairs}
        t = real.get(vid)
        if t is None or t <= dt.datetime.now(KST) + dt.timedelta(minutes=20):
            continue
        others = [o for o, v in pairs if v != vid]
        recur = recurring_times([o for o, v in pairs if v not in our_video_ids()])
        if not clashes(t, others, recur):
            continue
        day, new = dt.datetime.now(KST).date(), None
        while not new:
            for sl in SLOTS:
                w = dt.datetime.combine(day, dt.time.fromisoformat(sl), KST)
                if w > dt.datetime.now(KST) + dt.timedelta(hours=2) and not clashes(w, others + other_jobs_planned(d), recur):
                    new = w
                    break
            day += dt.timedelta(days=1)
        svc.videos().update(part="status", body={"id": vid, "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
                            "publishAt": new.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")}}).execute()
        it["publish_at"] = new.isoformat()
        core.save_json(d / "schedule.json", sched)
        moved.append(f"{it['clip']} {t:%m-%d %H:%M}→{new:%m-%d %H:%M}")
        core.log(f"⚠ 겹침 발견 → 이동 {moved[-1]}")
    return moved


def show(s):
    print("채널:", s["channel"], "| 피한 반복 시간대:", s["recurring_avoided"], f"| 간격 ±{s['buffer_min']}분")
    for i in s["items"]:
        st = (f"https://youtu.be/{i['video_id']} | 관련동영상 {i.get('related', '-')}") if i.get("video_id") else ("오류: " + i["error"] if i.get("error") else "업로드 대기")
        print(i["publish_at"][:16].replace("T", " "), i["clip"], "|", i["title"], "|", st)


TRACK = "/Users/apple/orca/projects/aimax-crm-observability/bin/aimax-crm-track"


def hub_upload(d: Path, status_file: Path, slug: str):
    """팀 허브 '예약 업로드' 버튼: 제목·설명 → 빈 시간 배정(하루 3개, 센 것부터) → 비공개 예약 업로드 → 관련 동영상(롱폼).
    단계마다 status_file 갱신. 이미 올라간 클립은 schedule.json 의 video_id 로 건너뛴다(다시 눌러도 중복 업로드 없음)."""
    import subprocess
    st = {"stage": "upload", "job": d.name, "channel": slug, "msg": "채널 확인 중"}

    def put(**kw):
        st.update(kw)
        core.save_json(status_file, st)
    put()
    try:
        cfg = core.load_json(d / "config.json", {})
        cfg.setdefault("per_day", 3)
        cfg.setdefault("ignore_recurring", True)
        core.save_json(d / "config.json", cfg)
        svc = yt()
        channel(svc)
        old = core.load_json(d / "schedule.json")
        if old and old.get("channel_id", DEFAULT_CHANNEL_ID) != EXPECT_CHANNEL_ID and any(i.get("video_id") for i in old["items"]):
            raise RuntimeError(f"이 작업은 이미 '{old.get('channel')}' 채널에 올렸어요. 다른 채널에는 새 작업으로 올려 주세요.")
        plan = core.load_json(d / "plan.json")
        if any(c.get("selected") and not c.get("yt_title") for c in plan["clips"]):
            put(msg="유튜브 제목·설명 쓰는 중")
            write_meta(d)
        put(msg="빈 시간 찾는 중")
        make_plan(d, svc)
        put(msg="예약 업로드 중")
        sched = upload(d, svc, limit=100)
        errs = [f"{i['clip']}: {i['error']}" for i in sched["items"] if i.get("error") and not i.get("video_id")]
        new = [i for i in sched["items"] if i.get("video_id") and not str(i.get("related", "")).startswith("OK")]
        put(msg="관련 동영상(롱폼) 지정 중", items=sched["items"])
        sched = related_all(d)
        if new:
            subprocess.run([TRACK, "emit", "--source-system", "youtube-data-api", "--channel", "youtube_shorts", "--stage", "planned",
                            "--status", "success", "--count", str(len(new)), "--campaign", f"hub-shorts-{slug}-{d.name}"],
                           capture_output=True, timeout=60, check=False)
        put(stage="uploaded", msg=("일부 실패: " + " / ".join(errs))[:600] if errs else "예약 완료", items=sched["items"])
    except BaseException as e:  # noqa: BLE001 — sys.exit 포함
        put(stage="upload_error", msg=str(e)[-600:])
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["auth", "hub-upload", "meta", "plan", "upload", "aside-upload", "verify", "audit", "related", "status"])
    ap.add_argument("job", nargs="?")
    ap.add_argument("--offline", action="store_true", help="로그인 없이 공개 쇼츠만 보고 배정 미리보기(저장 안 함)")
    ap.add_argument("--yes", action="store_true", help="실제 업로드 확인")
    ap.add_argument("--limit", type=int, default=PER_RUN)
    ap.add_argument("--status", help="hub-upload 진행 상태 파일")
    ap.add_argument("--slug", default="naminsoo")
    a = ap.parse_args()
    if a.cmd == "auth":
        return auth()
    d = core.JOBS / a.job
    if a.cmd == "meta":
        for c in write_meta(d)["clips"]:
            print(f"--- {c['id']} | {c['yt_title']}\n{c['yt_desc']}\n")
        return
    if a.cmd == "plan" and a.offline:
        return show(make_plan(d, Offline(), save=False))
    if a.cmd == "aside-upload":
        if not a.yes:
            sys.exit("실제 업로드는 --yes 를 붙여야 실행됨")
        return show(aside_upload_pending(d, a.limit, yt()))
    if a.cmd == "hub-upload":
        if not a.yes or not a.status:
            sys.exit("hub-upload 는 --yes --status 필요")
        return hub_upload(d, Path(a.status), a.slug)
    if a.cmd == "related":
        return show(related_all(d))
    if a.cmd == "status":
        return show(core.load_json(d / "schedule.json"))
    svc = yt()
    if a.cmd == "plan":
        show(make_plan(d, svc))
    elif a.cmd == "audit":
        print("이동:", audit_fix(d, svc) or "없음")
    elif a.cmd == "verify":
        print("어긋남:", verify(d, svc) or "없음")
    elif a.cmd == "upload":
        if not a.yes:
            sys.exit("실제 업로드는 --yes 를 붙여야 실행됨")
        upload(d, svc, a.limit)
        show(related_all(d))   # 올린 것마다 관련 동영상 바로 지정


if __name__ == "__main__":
    main()
