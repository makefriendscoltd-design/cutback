#!/usr/bin/env node
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const project = path.resolve(import.meta.dirname, '..');
const outPath = path.join(import.meta.dirname, 'caption-audit.json');

function findFiles(root, basename, maxDepth = 7, depth = 0, found = []) {
  if (depth > maxDepth || !fs.existsSync(root)) return found;
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const full = path.join(root, entry.name);
    if (entry.isDirectory()) findFiles(full, basename, maxDepth, depth + 1, found);
    else if (entry.name === basename) found.push(full);
  }
  return found;
}

const npxRoot = path.join(os.homedir(), '.npm', '_npx');
const puppeteerEntries = findFiles(npxRoot, 'puppeteer-core.js', 8)
  .filter((p) => p.endsWith('/puppeteer-core/lib/puppeteer/puppeteer-core.js'))
  .sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
if (!puppeteerEntries.length) throw new Error('Installed puppeteer-core runtime not found');
const { default: puppeteer } = await import(pathToFileURL(puppeteerEntries[0]).href);

const chromeRoot = path.join(os.homedir(), '.cache', 'hyperframes', 'chrome');
const chromeEntries = findFiles(chromeRoot, 'chrome-headless-shell', 8)
  .filter((p) => fs.statSync(p).isFile())
  .sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
if (!chromeEntries.length) throw new Error('HyperFrames headless Chrome not found');

const mime = new Map([
  ['.html', 'text/html; charset=utf-8'], ['.js', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'], ['.woff2', 'font/woff2'], ['.ttf', 'font/ttf'],
  ['.png', 'image/png'], ['.jpg', 'image/jpeg'], ['.jpeg', 'image/jpeg'],
  ['.mp4', 'video/mp4'], ['.m4a', 'audio/mp4'],
]);
const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname);
  const requested = path.resolve(project, `.${urlPath === '/' ? '/index.html' : urlPath}`);
  if (!requested.startsWith(`${project}${path.sep}`) || !fs.existsSync(requested) || fs.statSync(requested).isDirectory()) {
    res.writeHead(404).end('not found'); return;
  }
  res.writeHead(200, { 'content-type': mime.get(path.extname(requested)) || 'application/octet-stream' });
  fs.createReadStream(requested).pipe(res);
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const port = server.address().port;

const browser = await puppeteer.launch({
  executablePath: chromeEntries[0], headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--hide-scrollbars', '--mute-audio', '--window-size=1080,1920'],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
  await page.evaluateOnNewDocument(() => { window.__timelines = {}; });
  await page.setRequestInterception(true);
  page.on('request', (request) => request.resourceType() === 'media' ? request.abort() : request.continue());
  await page.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: 'networkidle0', timeout: 30000 });
  await page.evaluate(async () => { if (document.fonts) await document.fonts.ready; });

  const rows = await page.evaluate(() => {
    const punctuation = /[.,?!"'…“”‘’]/u;
    const captions = [...document.querySelectorAll('.caption')];
    return captions.map((caption, index) => {
      const start = Number(caption.dataset.start);
      const duration = Number(caption.dataset.duration);
      const midpoint = start + duration / 2;
      const timeline = window.__timelines?.main;
      if (timeline && typeof timeline.time === 'function') timeline.time(midpoint, false);
      const span = caption.querySelector('span');
      const style = getComputedStyle(span);
      const rect = span.getBoundingClientRect();
      const range = document.createRange();
      range.selectNodeContents(span);
      const lineTops = [...range.getClientRects()].filter((r) => r.width > 0 && r.height > 0)
        .map((r) => Math.round(r.top * 10) / 10)
        .filter((v, i, a) => a.indexOf(v) === i);
      const text = span.textContent.trim();
      const visible = style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
      const safeRight = rect.top >= 1000 ? 900 : 1016;
      const checks = {
        visible,
        actualText: text.length > 0,
        oneLine: lineTops.length === 1,
        punctuationFree: !punctuation.test(text),
        horizontalSafe: rect.left >= 64 - 0.5 && rect.right <= safeRight + 0.5,
        verticalSafe: rect.top >= 300 - 0.5 && rect.bottom <= 1440 + 0.5,
        midpointInsideClip: midpoint >= start && midpoint <= start + duration,
      };
      return {
        index, id: caption.id, text, mode: caption.classList.contains('card') ? 'card' : 'full',
        start, duration, midpoint: Number(midpoint.toFixed(4)), fontSize: style.fontSize,
        rect: { x: +rect.x.toFixed(2), y: +rect.y.toFixed(2), width: +rect.width.toFixed(2), height: +rect.height.toFixed(2), right: +rect.right.toFixed(2), bottom: +rect.bottom.toFixed(2) },
        lineCount: lineTops.length, checks,
        failures: Object.entries(checks).filter(([, ok]) => !ok).map(([name]) => name),
      };
    });
  });

  const runtime = await page.evaluate(() => ({
    gsapVersion: window.gsap?.version || null,
    mainTimelinePresent: Boolean(window.__timelines?.main && typeof window.__timelines.main.time === 'function'),
    fontsStatus: document.fonts?.status || null,
  }));

  const checkNames = Object.keys(rows[0]?.checks || {});
  const counts = Object.fromEntries(checkNames.map((name) => [name, rows.filter((r) => r.checks[name]).length]));
  const failures = rows.filter((r) => r.failures.length);
  const xs = rows.flatMap((r) => [r.rect.x, r.rect.right]);
  const ys = rows.flatMap((r) => [r.rect.y, r.rect.bottom]);
  const report = {
    generatedAt: new Date().toISOString(),
    method: 'Localhost static server + installed HyperFrames Chrome headless shell + installed puppeteer-core; 1080x1920 viewport; document fonts awaited; main GSAP timeline sought to each caption midpoint; computed DOM text, Range line boxes, opacity, and bounding rectangles measured.',
    source: 'index.html', viewport: { width: 1080, height: 1920, deviceScaleFactor: 1 }, runtime,
    rules: { expectedCaptions: 38, x: [64, 1016], highCaptionRightLimit: 900, highCaptionThresholdY: 1000, y: [300, 1440] },
    totals: {
      captions: rows.length, card: rows.filter((r) => r.mode === 'card').length,
      full: rows.filter((r) => r.mode === 'full').length,
      autoShrunkBelow60px: rows.filter((r) => parseFloat(r.fontSize) < 60).length,
      passedAll: rows.length - failures.length, failed: failures.length, ...counts,
      measuredBounds: { minX: Math.min(...xs), maxX: Math.max(...xs), minY: Math.min(...ys), maxY: Math.max(...ys) },
    },
    failureIds: failures.map((r) => r.id), captions: rows,
  };
  fs.writeFileSync(outPath, `${JSON.stringify(report, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify(report.totals)}\n`);
  if (rows.length !== 38 || failures.length) process.exitCode = 1;
} finally {
  await browser.close();
  await new Promise((resolve) => server.close(resolve));
}
