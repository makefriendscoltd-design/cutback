"""롱폼 → 숏폼 클리핑 코어.

단계: download → transcribe → plan(LLM) → [사용자 검수] → render
작업 폴더(jobs/<id>/)에 단계별 산출물을 남겨서 어느 단계부터든 다시 돌릴 수 있다.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOBS = Path(os.environ["LFS_JOBS"]) if os.environ.get("LFS_JOBS") else ROOT / "jobs"   # 팀 허브는 자기 폴더를 넘겨 채널 배치와 섞이지 않게
FONTS_DIR = ROOT.parents[1] / "packages" / "shorts-composer" / "assets" / "fonts"
AGENT_RUN = Path("/Users/apple/orca/projects/loopguard/bin/agent-run")
WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"

# 캔버스 레이아웃 (레퍼런스 DdYjImEiUL1 실측, 1080x1920)
W, H = 1080, 1920
VIDEO_CENTER_Y = 960          # 16:9 원본 → 1080x608, y=656~1264
HEAD1_BOTTOM = 380            # 헤드카피 1줄
HEAD2_BOTTOM = 530            # 헤드카피 2줄
FOOTER1_TOP = 1385
FOOTER2_TOP = 1440

DEFAULT_CONFIG = {
    "footer1": "",            # 예: 채널 핸들
    "footer2": "",            # 예: <원본 영상 제목>
    "theme": "aimax",         # aimax(기존 쇼츠) / naminsoo(썸네일) / yellow
    "caption_pos": "inside",  # inside = 영상 하단 안쪽, below = 영상 바로 아래, off = 안 넣음(원본에 자막 있을 때)
    "caption_src": "stt",     # stt = 음성 인식 / burned = 원본에 박힌 자막을 OCR 로 읽어 옮김(영어 인터뷰를 한글 번역 자막으로)
    "burned_band": None,      # burned 일 때 원본 자막 띠 [x, y, w, h] (원본 픽셀)
    "color1": None,           # 헤드카피 윗줄 색(RRGGBB). 비우면 테마 색. 클립에 color1 이 있으면 그게 우선
    "color2": None,           # 헤드카피 아랫줄 색
    "cap_color": None,        # 자막 색(기본 흰색)
    "min_clip_sec": 30,
    "max_clip_sec": 75,
    "max_gap_sec": 0.25,      # 말 사이 이 이상 비면 잘라냄
    "pad_sec": 0.06,
}

# 전사된 단어가 이것뿐이면 '음·어' 구간으로 보고 제거
FILLERS = {"음", "어", "으", "흠", "엄", "음음", "어어", "으음", "어음", "음어", "에", "에이", "아아", "어엄", "그으", "저어"}


def log(*a):
    print("[lfs]", *a, file=sys.stderr, flush=True)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def job_dir(job_id: str) -> Path:
    d = JOBS / job_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_json(p: Path, default=None):
    return json.loads(p.read_text()) if p.exists() else default


def save_json(p: Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1))


def config_of(d: Path) -> dict:
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(load_json(d / "config.json", {}))
    return cfg


# ---------------------------------------------------------------- 1. download
def download(url: str, section: str | None = None) -> Path:
    ytdlp = ROOT / ".venv" / "bin" / "yt-dlp"
    info = json.loads(subprocess.run([str(ytdlp), "-J", "--no-playlist", url],
                                     check=True, capture_output=True, text=True).stdout)
    d = job_dir(info["id"])
    src = d / "source.mp4"
    save_json(d / "meta.json", {"url": url, "id": info["id"], "title": info.get("title"),
                                 "channel": info.get("channel") or info.get("uploader"),
                                 "duration": info.get("duration")})
    if not src.exists():
        # HLS(m3u8) 포맷은 조각 500 에러가 잦아 https 직링 포맷을 먼저 고른다
        # 같은 해상도면 비트레이트 높은 H.264 + AAC 우선. https 저비트레이트(AV1 285k 등)를 고르면 화면 글씨가 뭉개지고,
        # Opus/AV1 은 Safari 미리보기에서 재생·소리가 안 된다. HLS 조각 에러는 --fragment-retries 로 버틴다
        fmt = "bv*[height<=1080]+ba[ext=m4a]/bv*[height<=1080]+ba/b"
        cmd = [str(ytdlp), "--no-playlist", "--no-progress", "--fragment-retries", "30", "-f", fmt, "-S", "res:1080,vcodec:avc1,tbr",
               "--merge-output-format", "mp4", "-o", str(src), url]
        if section:  # 테스트용: "*0:00-10:00"
            cmd[1:1] = ["--download-sections", section, "--force-keyframes-at-cuts"]
        log("다운로드:", info.get("title"))
        run(cmd)
    cfg_p = d / "config.json"
    if not cfg_p.exists():
        # 레퍼런스처럼 1줄 = 우리 계정, 2줄 = <원본 채널>
        save_json(cfg_p, {"footer1": "", "footer2": f"<{info.get('channel') or info.get('uploader') or ''}>"})
    return d


# ---------------------------------------------------------------- 2. transcribe
def transcribe(d: Path) -> dict:
    out = d / "transcript.json"
    if out.exists():
        return load_json(out)
    wav = d / "audio.wav"
    if not wav.exists():
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(d / "source.mp4"), "-ac", "1", "-ar", "16000", str(wav)])
    import mlx_whisper
    title = load_json(d / "meta.json", {}).get("title", "")
    log("전사 중 (whisper large-v3-turbo)…")
    # 프롬프트에 '음… 어…'를 넣어야 whisper가 필러를 지우지 않고 받아 적는다
    r = mlx_whisper.transcribe(str(wav), path_or_hf_repo=WHISPER_MODEL, language="ko",
                               word_timestamps=True, condition_on_previous_text=False,
                               initial_prompt=f"{title}\n음… 어… 그러니까 이제, 네. 어, 그게 뭐냐면요.")
    segs = []
    for s in r["segments"]:
        words = [{"w": w["word"].strip(), "s": round(w["start"], 3), "e": round(w["end"], 3)}
                 for w in s.get("words", []) if w["word"].strip()]
        if words:
            segs.append({"i": len(segs), "s": words[0]["s"], "e": words[-1]["e"],
                         "text": s["text"].strip(), "words": words})
    data = {"segments": segs}
    save_json(out, data)
    return data


# ---------------------------------------------------------------- 3. plan (LLM)
HEAD_RULES = """- 구간마다 헤드카피 2줄(영상 위 큰 제목). 스크롤 넘기던 사람 엄지를 1초 안에 멈추게 하는 게 목적:
  - head1: 누가·어떤 상황 — 짧고 구체적으로 (공백 포함 14자 이내)
  - head2: 펀치라인 (공백 포함 12자 이내). 아래 무기 중 최소 하나:
    · 구체 숫자·결과 ("8시간 일, 1분 컷", "1500만원 굳었다")
    · 통념 뒤집기·금지 ("코딩 배우지 마세요", "요금제 비싼 거 필요 없음")
    · 반전·대비 ("개발자는 화내고 AI는 안 냄")
    · 궁금증 공백 — 답은 영상 안에 ("이거 하나로 끝남", "진짜 이유는 따로")
  - 설명·요약·교훈조 금지: "~하는 방법", "~의 중요성", "아주 작은 것부터", "~할 수도 있다" 같은 밋밋한 말 X
  - 두루뭉술한 "~수도" "~것" 어미 대신 단정·반말·명령형으로 끊어. 느낌표·물음표는 필요할 때만
  - 좋은 예) "기안84 다정한 모습에 / 정신 못 차리는 카즈하", "내 노트 한 장으로 / AI 영상 설계하기", "이 PPT / AI가 만들었다"
  - 내용에 없는 사실·숫자를 지어내지 마. 실제 발언 속 가장 센 한 줄을 찾아 더 세게.
- alts: 같은 구간에 대한 다른 각도의 헤드카피 2개 [[head1, head2], [head1, head2]]
"""

PLAN_PROMPT = """너는 유튜브 롱폼을 인스타 릴스/쇼츠로 잘라내는 숏폼 편집자야.
아래는 롱폼 전사본이야. 각 줄은 [문장번호] (시작시각) 내용.

할 일: 숏폼으로 따로 떼어도 그 자체로 이해되고, 첫 문장부터 궁금하게 만드는 '의미 단위' 구간을 골라.
- 구간 길이 {min_s}~{max_s}초 (음·어·묵음을 빼면 실제로는 20~30% 짧아짐)
- 구간은 겹치지 않게. 좋은 구간은 최대한 많이(최대 {max_n}개), 억지로 채우지는 마
- 시작 문장은 맥락 없이 들어도 이해되고 흥미로운 문장이어야 함. 끝은 말이 완결되는 지점
{head_rules}
- hook: 1~10 숏폼 성과 예상 점수
- fixes: 전사본의 음성인식 오타 교정 목록(고유명사·맥락상 명백한 것만). 예) "신용훈련자"→"신용불량자"

JSON만 출력해. 설명·코드펜스 금지.
{{"clips":[{{"start":문장번호,"end":문장번호,"title":"구간 요약 한 줄","head1":"...","head2":"...","alts":[["...","..."],["...","..."]],"hook":8,"why":"고른 이유 한 줄"}}],"fixes":[{{"from":"틀린 말","to":"고친 말"}}]}}

영상 제목: {title}

전사본:
{lines}
"""


def fmt_t(t: float) -> str:
    return f"{int(t // 60)}:{int(t % 60):02d}"


def ask_llm(prompt: str) -> dict:
    res = subprocess.run([str(AGENT_RUN), "--timeout", "900", "--tools", ""], input=prompt,
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"agent-run 실패: {res.stderr[-500:]}")
    return json.loads(re.search(r"\{.*\}", res.stdout, re.S).group(0))


RECOPY_PROMPT = """너는 숏폼 헤드카피 카피라이터야. 아래 구간들은 이미 골라둔 숏폼이야.
구간마다 헤드카피를 새로 써. 지금 카피는 너무 밋밋하다는 피드백을 받았어.
{head_rules}
- hook: 1~10 숏폼 성과 예상 점수 (새 카피 기준)

JSON만 출력해. 설명·코드펜스 금지.
{{"clips":[{{"id":"c01","head1":"...","head2":"...","alts":[["...","..."],["...","..."]],"hook":8}}]}}

영상 제목: {title}

{clips}
"""


def recopy(d: Path) -> dict:
    """구간은 그대로 두고 헤드카피만 다시 뽑는다."""
    tr = load_json(d / "transcript.json")
    plan_ = load_json(d / "plan.json")
    fixes = plan_.get("fixes", [])
    blocks = []
    for c in plan_["clips"]:
        text = " ".join(s["text"] for s in tr["segments"][c["start"]:c["end"] + 1])
        for f in fixes:
            text = text.replace(f["from"], f["to"])
        blocks.append(f"## {c['id']} (지금 카피: {c['head1']} / {c['head2']})\n{text}")
    log(f"헤드카피 다시 뽑는 중 ({len(blocks)}개)…")
    raw = ask_llm(RECOPY_PROMPT.format(head_rules=HEAD_RULES, title=load_json(d / "meta.json", {}).get("title", ""),
                                       clips="\n\n".join(blocks)))
    new = {c["id"]: c for c in raw["clips"]}
    for c in plan_["clips"]:
        n = new.get(c["id"])
        if n:
            c.update(head1=n["head1"], head2=n["head2"], alts=n.get("alts", []), hook=n.get("hook", c["hook"]))
    save_json(d / "plan.json", plan_)
    return plan_


def plan(d: Path, max_n: int = 10) -> dict:
    out = d / "plan.json"
    if out.exists():
        return load_json(out)
    tr = load_json(d / "transcript.json")
    meta = load_json(d / "meta.json", {})
    cfg = config_of(d)
    segs = tr["segments"]
    lines = "\n".join(f"[{s['i']}] ({fmt_t(s['s'])}) {s['text']}" for s in segs)
    prompt = PLAN_PROMPT.format(min_s=cfg["min_clip_sec"], max_s=cfg["max_clip_sec"], max_n=max_n,
                                title=meta.get("title", ""), lines=lines, head_rules=HEAD_RULES)
    log(f"구간·헤드카피 추출 중 (문장 {len(segs)}개)…")
    raw = ask_llm(prompt)
    clips = []
    for c in raw["clips"]:
        a, b = int(c["start"]), int(c["end"])
        if not (0 <= a <= b < len(segs)):
            continue
        clips.append({"id": f"c{len(clips) + 1:02d}", "start": a, "end": b,
                      "t0": segs[a]["s"], "t1": segs[b]["e"],
                      "title": c.get("title", ""), "head1": c.get("head1", ""), "head2": c.get("head2", ""),
                      "alts": c.get("alts", []), "hook": c.get("hook", 0), "why": c.get("why", ""), "selected": True})
    clips.sort(key=lambda c: c["t0"])
    for n, c in enumerate(clips, 1):
        c["id"] = f"c{n:02d}"
    fixes = [f for f in raw.get("fixes", []) if f.get("from") and f.get("to") and f["from"] != f["to"]]
    data = {"clips": clips, "fixes": fixes}
    save_json(out, data)
    return data


# ---------------------------------------------------------------- 4. cuts
def keep_ranges(tr: dict, clip: dict, cfg: dict):
    """클립 안에서 살릴 구간 리스트와, 살릴 단어(원본 시각)를 돌려준다."""
    words = [w for s in tr["segments"][clip["start"]:clip["end"] + 1] for w in s["words"]]
    kept = []
    for w in words:
        core = re.sub(r"[\s.,!?…~\-]", "", w["w"])
        if not core or core in FILLERS:
            continue
        if core in ("아", "그", "저") and w["e"] - w["s"] > 0.45:   # 길게 끄는 '아~ 그~'
            continue
        kept.append(w)
    pad, gap = cfg["pad_sec"], cfg["max_gap_sec"]
    dead = dead_air(d_of(tr), clip["t0"] - 0.5, clip["t1"] + 0.5)

    def quiet(a, b):
        """[a,b]의 절반 이상이 실제로 조용한가 — whisper 단어 위치가 틀린 경우 말소리를 지키기 위함"""
        cov = sum(max(0.0, min(b, de) - max(a, ds)) for ds, de in dead)
        return cov >= (b - a) * 0.5
    ranges = []
    for w in kept:
        s, e = max(0.0, w["s"] - pad), w["e"] + pad
        n_syl = max(1, len(re.sub(r"[^가-힣a-zA-Z0-9]", "", w["w"])))
        if w["e"] - w["s"] < n_syl * 0.07:   # 타임스탬프가 비정상 짧음 → 실제 발음은 더 앞에서 시작
            s = max(0.0, s - n_syl * 0.1)
        if ranges and (s - ranges[-1][1] <= gap or not quiet(ranges[-1][1], s)):
            ranges[-1][1] = max(ranges[-1][1], e)
        else:
            ranges.append([s, e])
    # whisper는 '음·어'를 받아 적지 않고 앞뒤 단어에 흡수시킨다. 그래서 단어 안쪽까지
    # 음향으로 한 번 더 훑어서 말 멈춤·웅얼거림 구간을 도려낸다.
    # whisper 단어 경계는 붙어 있어서 멈춤도 단어 안에 들어가 있다.
    # 정상 길이 단어는 가운데 절반만 보호하고, 늘어진 단어(필러 흡수)는 보호하지 않는다
    def syl(w):
        return max(1, len(re.sub(r"[^가-힣a-zA-Z0-9]", "", w["w"])))
    protected = [(w["s"] + (w["e"] - w["s"]) * 0.3, w["e"] - (w["e"] - w["s"]) * 0.3) for w in kept if w["e"] - w["s"] <= syl(w) * 0.2 + 0.25]
    for a, b in dead:
        if any(ps < b and a < pe for ps, pe in protected):
            continue
        nxt = []
        for s, e in ranges:
            if b <= s or a >= e:
                nxt.append([s, e])
                continue
            if a - s > 0.08:
                nxt.append([s, a])
            if e - b > 0.08:
                nxt.append([b, e])
        ranges = nxt
    return ranges, kept


_AUDIO: dict = {}


def d_of(tr: dict) -> Path:
    return Path(tr["_dir"])


def dead_air(d: Path, t0: float, t1: float, sr=16000, hop=160, n=512):
    """[t0,t1] 안에서 잘라낼 구간: 말소리 대비 조용한 곳 + 낮게 늘어지는 '음·어'.

    기준을 클립마다 다시 잡는다(배경음 있는 촬영본은 고정 dB로는 묵음이 안 잡힘).
    """
    import numpy as np
    import wave
    if d not in _AUDIO:
        with wave.open(str(d / "audio.wav")) as w:
            _AUDIO[d] = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    x = _AUDIO[d][int(max(0, t0) * sr):int(t1 * sr)]
    m = (len(x) - n) // hop
    if m < 10:
        return []
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop][:m] * np.hanning(n)
    sp = np.abs(np.fft.rfft(fr)) ** 2
    db = 10 * np.log10(sp.sum(1) + 1e-10)
    edges = np.geomspace(3, 256, 25).astype(int)
    bands = np.log10(np.stack([sp[:, edges[i]:edges[i + 1]].sum(1) for i in range(24)], 1) + 1e-10)
    flux = np.r_[np.full(3, 9.0), np.abs(bands[3:] - bands[:-3]).mean(1)]
    # 짧게 튀는 값 평활
    k = np.ones(5) / 5
    db, flux = np.convolve(db, k, "same"), np.convolve(flux, k, "same")
    loud = np.percentile(db, 90)
    silent = db < loud - 12
    hum = (db < loud - 7) & (flux < 0.33)       # 조용하고 음색 변화 없는 소리 = 웅얼거림
    out = []
    for mask, min_run in ((silent, 0.16), (hum | silent, 0.3)):
        i = 0
        while i < m:
            if not mask[i]:
                i += 1
                continue
            j = i
            while j < m and mask[j]:
                j += 1
            if (j - i) * hop / sr >= min_run:
                # 말 앞뒤 자음이 안 잘리게 양끝 50ms 남김
                out.append((t0 + i * hop / sr + 0.05, t0 + j * hop / sr - 0.05))
            i = j
    return sorted(out)


def remap(t: float, ranges) -> float | None:
    acc = 0.0
    for s, e in ranges:
        if t < s:
            return acc
        if t <= e:
            return acc + (t - s)
        acc += e - s
    return acc


# ---------------------------------------------------------------- 5. subtitles (ASS)
def ass_color(hex_rgb: str) -> str:
    r, g, b = hex_rgb[0:2], hex_rgb[2:4], hex_rgb[4:6]
    return f"&H00{b}{g}{r}".upper()


def ass_time(t: float) -> str:
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def ass_escape(s: str) -> str:
    return s.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def caption_chunks(kept, ranges, fixes=(), max_chars=16):
    """살린 단어를 편집 후 타임라인으로 옮겨 자막 덩어리로 묶는다."""
    out, cur = [], []

    def flush():
        if cur:
            text = " ".join(w["w"] for w in cur)
            for f in fixes:
                text = text.replace(f["from"], f["to"])
            out.append({"text": text, "s": cur[0]["ns"], "e": cur[-1]["ne"]})
            cur.clear()

    for w in kept:
        ns, ne = remap(w["s"], ranges), remap(w["e"], ranges)
        if ne - ns <= 0.01:
            continue
        nw = {"w": w["w"], "ns": ns, "ne": ne}
        text_len = len("".join(x["w"] for x in cur)) + len(w["w"])
        if cur and (text_len > max_chars or ns - cur[-1]["ne"] > 0.6):
            flush()
        cur.append(nw)
        if re.search(r"[.?!]$", w["w"]):
            flush()
    flush()
    # 다음 자막 시작까지 이어서 띄워 깜빡임 방지
    for a, b in zip(out, out[1:]):
        if b["s"] - a["e"] < 0.5 or a["e"] > b["s"]:
            a["e"] = b["s"]
    return out


# 헤드카피 테마. naminsoo = 나민수 AI 썸네일(굵은 흰/검 + 파랑 #0048F5 에 흰 테두리)
THEMES = {
    # aimax = 나민수 기존 쇼츠 실측(1wd3JBtFAW4 등): 2줄 같은 크기·시안·이탤릭, 글자높이 70px, 줄간격 20px(피치 90), y 352~512
    "aimax": {"font1": "Pretendard Black", "size1": 94, "color1": "18C0E0", "outline1": 0, "oc1": "000000",
              "font2": "Pretendard Black", "size2": 94, "color2": "18C0E0", "outline2": 0, "oc2": "000000",
              "italic": 1, "y1": 434, "y2": 524},
    # naminsoo = 나민수 롱폼 썸네일(흰 + 파랑 #0048F5 에 흰 테두리). 행간은 aimax 와 같은 20px
    "naminsoo": {"font1": "Pretendard Black", "size1": 76, "color1": "FFFFFF", "outline1": 0, "oc1": "000000",
                 "font2": "Pretendard Black", "size2": 100, "color2": "0048F5", "outline2": 7, "oc2": "FFFFFF",
                 "italic": 0, "y1": 412, "y2": 520},
    "yellow": {"font1": "Pretendard Bold", "size1": 64, "color1": "FFFFFF", "outline1": 0, "oc1": "000000",
               "font2": "Pretendard ExtraBold", "size2": 90, "color2": "FFC400", "outline2": 4, "oc2": "3A1E00",
               "italic": 0, "y1": HEAD1_BOTTOM, "y2": HEAD2_BOTTOM},
}

def text_width(text: str, size: float) -> float:
    """대략적인 가로폭(px). 한글=1em, 영문·숫자=0.6em, 공백=0.3em"""
    w = 0.0
    for ch in text:
        w += 1.0 if ord(ch) >= 0x1100 else (0.3 if ch == " " else 0.6)
    return w * size


def fit_size(text: str, size: int, outline: int, max_w: int = W - 80) -> int:
    width = text_width(text, size) + outline * 2 * len(text) * 0.5
    return size if width <= max_w else int(size * max_w / width)


def build_ass(clip, chunks, cfg, video_h, total):
    top = VIDEO_CENTER_Y - video_h // 2
    bottom = top + video_h
    pos = cfg["caption_pos"]
    cap_y = bottom - 36 if pos == "inside" else bottom + 100
    foot_shift = 110 if pos == "below" else 0   # 영상 아래 자막이면 하단 문구를 밀어냄
    font = "Pretendard"
    th = dict(THEMES.get(cfg.get("theme"), THEMES["aimax"]))
    for k in ("color1", "color2"):
        v = clip.get(k) or cfg.get(k)
        if v:
            th[k] = v.lstrip("#")
    cap_c = ass_color((clip.get("cap_color") or cfg.get("cap_color") or "FFFFFF").lstrip("#"))
    s1 = fit_size(clip["head1"], th["size1"], th["outline1"])
    s2 = fit_size(clip["head2"], th["size2"], th["outline2"])
    head = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Head1,{th['font1']},{s1},{ass_color(th['color1'])},&H00FFFFFF,{ass_color(th['oc1'])},&H00000000,0,0,0,0,100,100,0,0,1,{th['outline1']},0,2,40,40,0,1",
        f"Style: Head2,{th['font2']},{s2},{ass_color(th['color2'])},&H00FFFFFF,{ass_color(th['oc2'])},&H00000000,0,0,0,0,100,100,0,0,1,{th['outline2']},0,2,40,40,0,1",
        f"Style: Cap,{font} Bold,{CAP_SIZE},{cap_c},&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,1,2,60,60,0,1",
        f"Style: Foot1,{font} Bold,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,8,40,40,0,1",
        f"Style: Foot2,{font} Bold,32,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,8,40,40,0,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    end = ass_time(total + 1)
    ev = []

    def add(style, s, e, x, y, text):
        if text.strip():
            slant = "\\fax-0.24" if th["italic"] and style.startswith("Head") else ""
            ev.append(f"Dialogue: 0,{s},{e},{style},,0,0,0,,{{\\pos({x},{y}){slant}}}{ass_escape(text)}")

    add("Head1", ass_time(0), end, W // 2, th["y1"], clip["head1"])
    add("Head2", ass_time(0), end, W // 2, th["y2"], clip["head2"])
    add("Foot1", ass_time(0), end, W // 2, FOOTER1_TOP + foot_shift, cfg["footer1"])
    add("Foot2", ass_time(0), end, W // 2, FOOTER2_TOP + foot_shift, cfg["footer2"])
    for c in (chunks if pos != "off" else []):
        if pos == "below":   # 영상 바로 아래, 항상 한 줄. 길면 글자 수 비율로 시간을 나눠 차례로 띄운다
            parts = wrap_cap(c["text"])
            n = sum(len(x) for x in parts)
            t = c["s"]
            for x in parts:
                e = t + (c["e"] - c["s"]) * len(x) / n
                ev.append(f"Dialogue: 0,{ass_time(t)},{ass_time(e)},Cap,,0,0,0,,"
                          f"{{\\an8\\pos({W // 2},{bottom + 44})\\fs{fit_size(x, CAP_SIZE, 0, W - 120)}}}{ass_escape(x)}")
                t = e
        else:
            add("Cap", ass_time(c["s"]), ass_time(c["e"]), W // 2, cap_y, c["text"])
    return "\n".join(head + ev) + "\n"


CAP_SIZE = 54
OCR_BIN = ROOT / ".cache" / "ocr"


def wrap_cap(text: str, max_w: int = W - 120) -> list[str]:
    """한 줄에 안 들어가면 가운데에 가까운 띄어쓰기에서 나눈다(차례로 띄울 조각들). 조각도 길면 다시 나눈다."""
    if text_width(text, CAP_SIZE) <= max_w or " " not in text:
        return [text]
    mid = len(text) / 2
    cut = min((i for i, ch in enumerate(text) if ch == " "), key=lambda i: abs(i - mid))
    return wrap_cap(text[:cut], max_w) + wrap_cap(text[cut + 1:], max_w)


def clean_cap(text: str) -> str:
    """자막 규칙: 문장부호 제거(숫자 사이 쉼표는 남김)."""
    text = re.sub(r"(?<!\d),|,(?!\d)", " ", text)
    text = re.sub(r"[.?!…\"'“”‘’·~]", " ", text)
    text = re.sub(r"\bAl\b", "AI", text)   # OCR 이 AI 를 Al(소문자 L)로 읽음
    # OCR 잡티(_ - | 같은 기호만 있는 토큰) 제거
    return " ".join(t for t in text.split() if re.search(r"[가-힣A-Za-z0-9]", t.replace("_", "")))


def ocr(paths: list[Path]) -> list[str]:
    src = ROOT / "tools" / "ocr.swift"
    if not OCR_BIN.exists() or OCR_BIN.stat().st_mtime < src.stat().st_mtime:
        OCR_BIN.parent.mkdir(exist_ok=True)
        run(["swiftc", "-O", str(ROOT / "tools" / "ocr.swift"), "-o", str(OCR_BIN)])
    out = []
    for i in range(0, len(paths), 200):
        res = subprocess.run([str(OCR_BIN), *map(str, paths[i:i + 200])], capture_output=True, text=True, check=True)
        for ln in res.stdout.splitlines():
            # 화면 속 다른 글자(트윗 숫자 등)가 같이 읽히면 버리고 한글이 든 줄(=번역 자막)만 남긴다
            lines = ln.split("\t", 1)[1].split("\x1f") if "\t" in ln else []
            out.append(" ".join(x for x in lines if re.search(r"[가-힣]", x)))
    return out


def burned_chunks(d: Path, clip: dict, ranges, cfg, fps=4) -> list[dict]:
    """원본 영상에 박힌 자막을 OCR 로 읽어 편집 후 타임라인 자막으로 옮긴다."""
    import difflib
    import tempfile
    x, y, w, h = cfg["burned_band"]
    t0, t1 = ranges[0][0], ranges[-1][1]
    with tempfile.TemporaryDirectory() as tmp:
        run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", str(d / "source.mp4"),
             "-vf", f"fps={fps},crop={w}:{h}:{x}:{y}", str(Path(tmp) / "%05d.png")])
        frames = sorted(Path(tmp).glob("*.png"))
        texts = ocr(frames)
    groups = []   # [시작, 끝, [읽은 글자들]]
    for i, t in enumerate(texts):
        t = t.strip()
        s = t0 + i / fps
        if not re.search(r"[가-힣]", t):
            continue
        g = groups[-1] if groups else None
        if g and s - g[1] <= 1.01 / fps and difflib.SequenceMatcher(None, g[2][-1], t).ratio() > 0.7:
            g[1] = s + 1 / fps
            g[2].append(t)
        else:
            groups.append([s, s + 1 / fps, [t]])
    out = []
    for s, e, ts in groups:
        ns, ne = remap(s, ranges), remap(e, ranges)
        text = clean_cap(max(set(ts), key=ts.count))
        if ne - ns >= 0.3 and text:
            out.append({"text": text, "s": ns, "e": ne})
    return out


# ---------------------------------------------------------------- 6. render
def probe_size(p: Path):
    err = subprocess.run(["ffmpeg", "-i", str(p)], capture_output=True, text=True).stderr
    m = re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", err)
    return int(m.group(1)), int(m.group(2))


def render_clip(d: Path, clip: dict, progress=lambda msg: None) -> Path:
    tr = load_json(d / "transcript.json")
    tr["_dir"] = str(d)
    cfg = config_of(d)
    ranges, kept = keep_ranges(tr, clip, cfg)
    if not ranges:
        raise RuntimeError("살릴 구간이 없음")
    sw, sh = probe_size(d / "source.mp4")
    vh = round(W * sh / sw / 2) * 2
    if vh > H:
        raise RuntimeError("세로 원본은 아직 미지원")
    total = sum(e - s for s, e in ranges)
    outdir = d / "out"
    outdir.mkdir(exist_ok=True)
    if cfg.get("caption_src") == "burned" and cfg["caption_pos"] != "off":
        progress("원본 자막 읽는 중")
        chunks = burned_chunks(d, clip, ranges, cfg)
    else:
        chunks = caption_chunks(kept, ranges, load_json(d / "plan.json", {}).get("fixes", []))
    ass_p = outdir / f"{clip['id']}.ass"
    ass_p.write_text(build_ass(clip, chunks, cfg, vh, total))

    # 클립 구간만 빠르게 시킹해서 읽고, 그 안에서 trim → concat
    t0 = max(0.0, ranges[0][0] - 1.0)
    t1 = ranges[-1][1] + 0.5
    parts, labels = [], []
    for i, (s, e) in enumerate(ranges):
        rs, re_ = s - t0, e - t0
        fd = min(0.012, (e - s) / 4)
        parts.append(f"[0:v]trim=start={rs:.3f}:end={re_:.3f},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim=start={rs:.3f}:end={re_:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d={fd:.3f},areverse,afade=t=in:d={fd:.3f},areverse[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    fonts = str(FONTS_DIR).replace(":", r"\:")
    ass_arg = str(ass_p).replace(":", r"\:")
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(ranges)}:v=1:a=1[vc][ac];" \
        f"[vc]scale={W}:{vh}:flags=lanczos,setsar=1,pad={W}:{H}:0:{VIDEO_CENTER_Y - vh // 2}:black," \
        f"ass='{ass_arg}':fontsdir='{fonts}',fps=30,format=yuv420p[vo];[ac]loudnorm=I=-14:TP=-1.5:LRA=11[ao]"
    fc_p = outdir / f"{clip['id']}.filter"
    fc_p.write_text(fc)
    out = outdir / f"{clip['id']}.mp4"
    progress(f"렌더 중 ({len(ranges)}컷, {total:.1f}s)")
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", str(d / "source.mp4"),
         "-filter_complex_script", str(fc_p), "-map", "[vo]", "-map", "[ao]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", str(out)])
    save_json(outdir / f"{clip['id']}.json", {"clip": clip, "ranges": ranges, "duration": total,
                                               "src_duration": clip["t1"] - clip["t0"], "captions": chunks})
    return out
