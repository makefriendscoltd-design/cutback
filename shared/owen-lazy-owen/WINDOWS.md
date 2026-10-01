# Windows: WSL2 required

Native PowerShell Python / Git Bash is unsupported. The approved renderer uses POSIX `fcntl.flock`, and the caption audit discovers a Linux/macOS headless Chrome binary. Replacing the lock alone is insufficient. This entry preserves the original lock, renderer 0.8.103, composition, timing and included assets.

## Install once

In Windows PowerShell, inspect `wsl --list --verbose`. If absent, install WSL using `wsl --install -d Ubuntu-24.04` and complete its setup/reboot. The distribution must show VERSION 2. WSL installation is a user-managed OS change, never performed by these scripts. See [Microsoft WSL commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands).

Inside Ubuntu 24.04 WSL2, use Linux Git, Python 3.10+, Node.js 22+ with npm/npx, FFmpeg/ffprobe with libx264, and headless Chromium libraries. Do not reuse a Windows or Mac virtual environment/node_modules. A typical Ubuntu dependency installation is:

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip ffmpeg ca-certificates \
  libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
  libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
  libgbm1 libasound2t64 libpango-1.0-0 libcairo2
```

Install a Linux Node.js 22+ release using your normal Node installer; Ubuntu's default Node package may be older. `node -p process.platform` must print `linux`. Keep the clone on WSL's Linux filesystem (for example `~/cutback-owen`), not a shared Windows drive.

```bash
git clone --branch share/owen-lazy-owen-20261001 --single-branch https://github.com/makefriendscoltd-design/cutback.git ~/cutback-owen
cd ~/cutback-owen/shared/owen-lazy-owen
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
bash run-wsl.sh preflight
bash run-wsl.sh prepare
bash run-wsl.sh smoke
```

`prepare` downloads the pinned renderer's headless Chrome before the caption auditor looks for it. Network access to npm, the Chrome download host and GSAP 3.14.2 CDN is required. A fresh transcription may download a faster-whisper model. No credentials are needed.

## Production example

From the same directory inside WSL2:

```bash
bash run-wsl.sh build
# Supply the original episode 7 recording at videos/ep07-v3/src/source.mp4.
bash run-wsl.sh render
```

The original private recording is excluded. Arbitrary footage cannot reuse episode 7 timestamps: follow README.md for new-episode authoring. `check` expects built composition and cut/mixed media; `smoke` supplies synthetic media in a temporary copy and is the complete no-private-input test. It preserves all 49.05 seconds of reference timing, generates only grid/tone source media and prints its temporary output/QC location. It does not overwrite production media.

Run all renders in one WSL distro, with the same user and TMPDIR, so the existing temporary-file lock coordinates them. Separate distros/Windows/macOS processes do not share this lock. Do not delete a live lock file. Run one smoke/production pipeline at a time: this lock serializes rendering, not concurrent edits to the same episode.

## What is verified

See VALIDATION.md. macOS can exercise the original full build/render/QC path and check that this WSL entry rejects a non-WSL host. It cannot prove Windows/WSL runtime or the Ubuntu dependency installation. On the target PC, success means `bash run-wsl.sh smoke` exits zero and the printed QC report shows 1080x1920/30fps, expected duration, zero decode errors, passing captions and audio bounds. Check its final-contact-sheet.jpg as well. Missing libraries, network errors or browser launch failures remain failures to resolve on that PC; preflight alone is not a render pass.
