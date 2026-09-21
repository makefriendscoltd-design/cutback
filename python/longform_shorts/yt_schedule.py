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
EXPECT_CHANNEL = os.environ.get("LFS_YT_CHANNEL", "나민수")   # 다른 채널 토큰이면 중단
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


def channel(svc):
    if isinstance(svc, Offline):
        return {"snippet": {"title": "나민수 AI (미리보기: 공개분만)"}}
    ch = svc.channels().list(part="snippet,contentDetails", mine=True).execute()["items"][0]
    if EXPECT_CHANNEL not in ch["snippet"]["title"]:
        sys.exit(f"토큰 채널이 '{ch['snippet']['title']}' — '{EXPECT_CHANNEL}' 아님. 중단")
    return ch


def occupied(svc, ch, max_items=300) -> list[dt.datetime]:
    """채널 영상들의 공개(또는 예약 공개) 시각. 비공개 예약분까지 포함."""
    if isinstance(svc, Offline):
        return svc.times
    pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while len(ids) < max_items:
        r = svc.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    out = []
    for i in range(0, len(ids), 50):
        r = svc.videos().list(part="status,snippet", id=",".join(ids[i:i + 50])).execute()
        for v in r["items"]:
            t = v["status"].get("publishAt") or v["snippet"].get("publishedAt")
            if t:
                out.append(dt.datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(KST))
    return out


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
    busy = occupied(svc, ch)
    recur = recurring_times(busy)
    old = core.load_json(d / "schedule.json", {"items": []})
    done = {i["clip"]: i for i in old["items"] if i.get("video_id")}
    plan = core.load_json(d / "plan.json")
    clips = [c for c in plan["clips"] if c.get("selected") and (d / "out" / f"{c['id']}.mp4").exists()]
    # 후킹 점수 높은 것부터 먼저 공개
    clips.sort(key=lambda c: -int(c.get("hook") or 0))
    taken = [dt.datetime.fromisoformat(i["publish_at"]) for i in done.values()]
    items = list(done.values())
    now = dt.datetime.now(KST)
    day = now.date()
    pending = [c for c in clips if c["id"] not in done]
    while pending:
        count = sum(1 for t in taken if t.date() == day)
        for s in SLOTS:
            if not pending or count >= PER_DAY:
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
    out = {"channel": ch["snippet"]["title"], "recurring_avoided": [t.strftime("%H:%M") for t in recur],
           "buffer_min": BUFFER_MIN, "items": items}
    if save:
        core.save_json(d / "schedule.json", out)
    return out


META_PROMPT = """너는 유튜브 '나민수 AI' 채널 쇼츠 담당이야. 아래 쇼츠들은 나민수 본인 롱폼에서 잘라낸 거야.
쇼츠마다 유튜브 제목과 설명글을 써.

채널 기존 쇼츠 형식(따라 할 것):
- 제목: 20자 안팎, "~하는 법", "~한 실제 사례" 처럼 무슨 내용인지 한눈에. 해시태그·이모지·따옴표 없음
  예) "클로드 코드로 왓츠앱 상담 봇 만들기", "프롬프트는 짧게, 클로드 결과는 더 좋게", "내 컴퓨터에 AI를 직접 깔아 쓰는 법"
- 설명: 첫 문단 1~2문장 후킹 + "저장하고 끝까지 보세요!" / 빈 줄 / 핵심 2~3개를 "첫째, ~입니다." 식으로 한 문단씩
- 기존 쇼츠는 남의 영상 소개라 "이 남자 미쳤습니다"로 시작하지만, 이건 나민수 본인 이야기니 그 문장은 쓰지 마.
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
    raw = core.ask_llm(META_PROMPT.format(clips="\n\n".join(blocks)))
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
    busy = occupied(svc, ch)          # 올리기 직전에 다시 조회해서 그 사이 생긴 예약과도 안 겹치게
    recur = recurring_times(busy)
    n = 0
    for it in sched["items"]:
        if it.get("video_id") or n >= limit:
            continue
        when = dt.datetime.fromisoformat(it["publish_at"])
        if when < dt.datetime.now(KST) + dt.timedelta(minutes=30):
            it["error"] = "예약 시각이 지나거나 임박 — plan 다시 돌려야 함"
            continue
        others = [b for b in busy if abs((b - when).total_seconds()) > 1]
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
            if "quota" in str(e).lower():
                core.log("쿼터 소진 — 내일 다시 실행")
                break
            continue
        it.update(video_id=r["id"], uploaded_at=dt.datetime.now(KST).isoformat())
        it.pop("error", None)
        core.save_json(d / "schedule.json", sched)
        core.log(f"예약 완료 {it['clip']} → {it['publish_at']} https://youtu.be/{r['id']}")
        n += 1
    return sched


def set_related(video_id: str, target_title: str) -> str:
    """Aside 브라우저로 Studio '관련 동영상'을 롱폼으로 지정. API 에 이 항목이 없어서 UI 로 한다."""
    import subprocess
    js = (core.ROOT / "aside_related.js").read_text()
    code = f"const VID={json.dumps(video_id)}; const TARGET_TITLE={json.dumps(target_title)};\n{js}"
    try:
        out = subprocess.run(["aside", "repl", code], capture_output=True, text=True, timeout=240).stdout
    except subprocess.TimeoutExpired:
        return "FAIL timeout"
    line = [l for l in out.splitlines() if "RESULT:" in l]
    return line[-1].split("RESULT:", 1)[1].strip() if line else "FAIL no result"


def related_all(d: Path):
    sched = core.load_json(d / "schedule.json")
    title = core.load_json(d / "meta.json", {}).get("title", "")
    for it in sched["items"]:
        if it.get("video_id") and not str(it.get("related", "")).startswith("OK"):
            it["related"] = set_related(it["video_id"], title)
            core.log(f"관련 동영상 {it['clip']}: {it['related']}")
            core.save_json(d / "schedule.json", sched)
    return sched


def show(s):
    print("채널:", s["channel"], "| 피한 반복 시간대:", s["recurring_avoided"], f"| 간격 ±{s['buffer_min']}분")
    for i in s["items"]:
        st = (f"https://youtu.be/{i['video_id']} | 관련동영상 {i.get('related', '-')}") if i.get("video_id") else ("오류: " + i["error"] if i.get("error") else "업로드 대기")
        print(i["publish_at"][:16].replace("T", " "), i["clip"], "|", i["title"], "|", st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["auth", "meta", "plan", "upload", "related", "status"])
    ap.add_argument("job", nargs="?")
    ap.add_argument("--offline", action="store_true", help="로그인 없이 공개 쇼츠만 보고 배정 미리보기(저장 안 함)")
    ap.add_argument("--yes", action="store_true", help="실제 업로드 확인")
    ap.add_argument("--limit", type=int, default=PER_RUN)
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
    if a.cmd == "related":
        return show(related_all(d))
    if a.cmd == "status":
        return show(core.load_json(d / "schedule.json"))
    svc = yt()
    if a.cmd == "plan":
        show(make_plan(d, svc))
    elif a.cmd == "upload":
        if not a.yes:
            sys.exit("실제 업로드는 --yes 를 붙여야 실행됨")
        upload(d, svc, a.limit)
        show(related_all(d))   # 올린 것마다 관련 동영상 바로 지정


if __name__ == "__main__":
    main()
