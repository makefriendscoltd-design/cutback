/**
 * 자막용 무료 폰트 다운로드 (SIL OFL 1.1 — 상업 사용/임베딩 무료)
 *
 * 사용: pnpm --filter @cutback/shorts-composer fonts
 * 대상: packages/shorts-composer/assets/fonts/
 *
 * 이미 있으면 스킵. 개별 다운로드 실패는 경고만 하고 계속 진행
 * (폰트가 없으면 런타임에 시스템 폰트로 폴백됨).
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const FONTS = [
  {
    file: 'Pretendard-ExtraBold.otf',
    url: 'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/public/static/Pretendard-ExtraBold.otf',
  },
  {
    file: 'Pretendard-Bold.otf',
    url: 'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/public/static/Pretendard-Bold.otf',
  },
  {
    file: 'SUIT-Bold.otf',
    url: 'https://cdn.jsdelivr.net/gh/sun-typeface/SUIT@2.0/fonts/static/otf/SUIT-Bold.otf',
  },
];

const outDir = path.join(__dirname, '..', 'assets', 'fonts');

function download(url, dest, redirects = 0) {
  return new Promise((resolve, reject) => {
    if (redirects > 5) return reject(new Error('Too many redirects'));
    https
      .get(url, (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          res.resume();
          return resolve(download(res.headers.location, dest, redirects + 1));
        }
        if (res.statusCode !== 200) {
          res.resume();
          return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
        }
        const tmp = dest + '.tmp';
        const out = fs.createWriteStream(tmp);
        res.pipe(out);
        out.on('finish', () => {
          out.close(() => {
            fs.renameSync(tmp, dest);
            resolve();
          });
        });
        out.on('error', reject);
      })
      .on('error', reject);
  });
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  for (const font of FONTS) {
    const dest = path.join(outDir, font.file);
    if (fs.existsSync(dest) && fs.statSync(dest).size > 10000) {
      console.log(`[skip] ${font.file} (already exists)`);
      continue;
    }
    try {
      process.stdout.write(`[download] ${font.file} ... `);
      await download(font.url, dest);
      const kb = Math.round(fs.statSync(dest).size / 1024);
      console.log(`OK (${kb} KB)`);
    } catch (err) {
      console.warn(`FAILED: ${err.message} — 시스템 폰트로 폴백됩니다`);
    }
  }
  console.log(`fonts dir: ${outDir}`);
})();
