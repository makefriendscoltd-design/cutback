"""롱폼 링크 → 숏폼 후보 → 검수 → 렌더.

  .venv/bin/python lfs.py run <유튜브 URL>        # 다운로드·전사·구간추출 후 검수 페이지 오픈
  .venv/bin/python lfs.py review <job_id>          # 검수 페이지만 다시 열기
  .venv/bin/python lfs.py recopy <job_id>          # 구간은 그대로 두고 헤드카피만 다시 뽑기
  .venv/bin/python lfs.py render <job_id> [c01 ..] # 검수 없이 바로 렌더 (기본: selected=true 전부)
  .venv/bin/python lfs.py prepare <URL> --status s.json  # 팀 허브용: 검수 페이지 없이 후보까지만, 진행 상태를 파일로
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import lfs_core as core

STATUS: dict[str, dict] = {}   # clip id → {state, msg}
LOCK = threading.Lock()


def render_many(d: Path, ids: list[str] | None = None, status_file: Path | None = None):
    plan = core.load_json(d / "plan.json")
    clips = [c for c in plan["clips"] if (c["id"] in ids if ids else c.get("selected"))]

    def put(cid, state, msg):
        STATUS[cid] = {"state": state, "msg": msg}
        if status_file:
            core.save_json(status_file, {"stage": "render", "job": d.name, "clips": STATUS})
    for c in clips:
        put(c["id"], "queued", "대기")
    for c in clips:
        put(c["id"], "running", "렌더 중")
        try:
            out = core.render_clip(d, c, lambda m, cid=c["id"]: put(cid, "running", m))
            put(c["id"], "done", out.name)
            core.log("완료:", out)
        except Exception as e:  # noqa: BLE001 — 한 클립 실패가 전체를 멈추지 않게
            put(c["id"], "error", str(e)[-300:])
            core.log("실패:", c["id"], e)


def prepare(url: str, max_n: int, status_file: Path) -> Path:
    """다운로드 → 전사 → 구간·헤드카피. 단계마다 status_file 갱신, 실패도 기록"""
    st = {"stage": "download", "msg": "영상 받는 중"}
    core.save_json(status_file, st)
    try:
        d = core.download(url)
        st.update(job=d.name, stage="transcribe", msg="음성 받아쓰는 중")
        core.save_json(status_file, st)
        core.transcribe(d)
        st.update(stage="plan", msg="숏폼 구간·헤드카피 뽑는 중")
        core.save_json(status_file, st)
        core.plan(d, max_n)
        st.update(stage="ready", msg="후보 완성")
        core.save_json(status_file, st)
        return d
    except Exception as e:  # noqa: BLE001
        st.update(stage="error", msg=str(e)[-400:])
        core.save_json(status_file, st)
        raise


def serve(d: Path, port: int = 8765, open_browser: bool = True):
    html = (core.ROOT / "review.html").read_bytes()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _json(self, obj, code=200):
            b = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def _file(self, p: Path):
            if not p.exists():
                return self._json({"error": "not found"}, 404)
            size = p.stat().st_size
            rng = self.headers.get("Range")
            start, end = 0, size - 1
            if rng and rng.startswith("bytes="):
                a, _, b = rng[6:].partition("-")
                start = int(a) if a else 0
                end = min(int(b), size - 1) if b else size - 1
                self.send_response(206)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            else:
                self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(p.name)[0] or "application/octet-stream")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(end - start + 1))
            self.end_headers()
            with p.open("rb") as f:
                f.seek(start)
                left = end - start + 1
                try:
                    while left > 0:
                        chunk = f.read(min(1 << 20, left))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        left -= len(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    pass

        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html)
            elif path == "/api/plan":
                tr = core.load_json(d / "transcript.json")
                plan = core.load_json(d / "plan.json")
                for c in plan["clips"]:
                    c["text"] = " ".join(s["text"] for s in tr["segments"][c["start"]:c["end"] + 1])
                    c["rendered"] = (d / "out" / f"{c['id']}.mp4").exists()
                self._json({"plan": plan, "meta": core.load_json(d / "meta.json", {}),
                            "config": core.config_of(d), "themes": core.THEMES})
            elif path == "/api/status":
                self._json(STATUS)
            elif path == "/media/source.mp4":
                self._file(d / "source.mp4")
            elif path.startswith("/fonts/"):
                self._file(core.FONTS_DIR / Path(path).name)
            elif path.startswith("/out/"):
                self._file(d / "out" / Path(path).name)
            else:
                self._json({"error": "not found"}, 404)

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if self.path == "/api/save":
                with LOCK:
                    plan = core.load_json(d / "plan.json")
                    edits = {c["id"]: c for c in body.get("clips", [])}
                    for c in plan["clips"]:
                        if c["id"] in edits:
                            for k in ("selected", "head1", "head2", "alts", "yt_title", "yt_desc", "color1", "color2", "cap_color"):
                                if k in edits[c["id"]]:
                                    c[k] = edits[c["id"]][k]
                    core.save_json(d / "plan.json", plan)
                    if "config" in body:
                        cfg = core.load_json(d / "config.json", {})
                        cfg.update({k: body["config"][k] for k in ("footer1", "footer2", "caption_pos", "theme", "color1", "color2", "cap_color") if k in body["config"]})
                        core.save_json(d / "config.json", cfg)
                self._json({"ok": True})
            elif self.path == "/api/render":
                if any(s["state"] in ("queued", "running") for s in STATUS.values()):
                    return self._json({"error": "이미 렌더 중"}, 409)
                threading.Thread(target=render_many, args=(d, body.get("ids")), daemon=True).start()
                self._json({"ok": True})
            else:
                self._json({"error": "not found"}, 404)

    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    url = f"http://127.0.0.1:{port}/"
    core.log("검수 페이지:", url, "(Ctrl+C 로 종료)")
    if open_browser:
        webbrowser.open(url)
    srv.serve_forever()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("url")
    r.add_argument("--section", help='테스트용 부분 다운로드, 예: "*0:00-10:00"')
    r.add_argument("--max", type=int, default=10, help="최대 숏폼 개수")
    r.add_argument("--port", type=int, default=8765)
    r.add_argument("--no-review", action="store_true", help="검수 없이 전부 렌더")
    v = sub.add_parser("review")
    v.add_argument("job")
    v.add_argument("--port", type=int, default=8765)
    rc = sub.add_parser("recopy", help="구간은 그대로, 헤드카피만 다시 뽑기")
    rc.add_argument("job")
    rn = sub.add_parser("render")
    rn.add_argument("job")
    rn.add_argument("ids", nargs="*")
    rn.add_argument("--status")
    pr = sub.add_parser("prepare")
    pr.add_argument("url")
    pr.add_argument("--max", type=int, default=10)
    pr.add_argument("--status", required=True)
    a = ap.parse_args()

    if a.cmd == "run":
        d = core.download(a.url, a.section)
        core.transcribe(d)
        core.plan(d, a.max)
        if a.no_review:
            render_many(d)
        else:
            serve(d, a.port)
    elif a.cmd == "review":
        serve(core.JOBS / a.job, a.port)
    elif a.cmd == "prepare":
        prepare(a.url, a.max, Path(a.status))
    elif a.cmd == "recopy":
        for c in core.recopy(core.JOBS / a.job)["clips"]:
            print(c["id"], c["hook"], "|", c["head1"], "/", c["head2"], "| alts:", c.get("alts"))
    elif a.cmd == "render":
        render_many(core.JOBS / a.job, a.ids or None, Path(a.status) if a.status else None)


if __name__ == "__main__":
    main()
