// Aside 로 YouTube Studio 에 쇼츠 1개를 '예약 공개'로 올린다. API 쿼터가 막혔을 때의 대체 경로.
// 앞에 정의해서 실행: CID, FILE_URL(로컬 http), TITLE, DESC, RELATED_TITLE, DATE_TEXT("2026. 9. 27."), TIME_TEXT("오후 5:30")
// 마지막 줄: RESULT: OK <videoId> / RESULT: FAIL <이유>
const step = (s) => console.log('STEP ' + s);
let result = 'FAIL unknown';
const p = await openTab(`https://studio.youtube.com/channel/${CID}/videos/upload?d=ud`);
try {
  // 1) 파일: 로컬 서버에서 받아 세션 폴더에 저장 → 파일 선택 칸에 넣기
  const r = await fetch(FILE_URL);
  await fs.writeFile('up.mp4', Buffer.from(await r.arrayBuffer()));
  await sleep(5000);
  await p.locator('ytcp-uploads-file-picker input[type=file]').setInputFiles('up.mp4');
  step('file set');
  await p.waitForSelector('#title-textarea #textbox', { timeout: 60000 });
  await sleep(3000);
  let vid = '';
  for (let i = 0; i < 90 && !vid; i++) {   // 최대 3분
    const link = await p.evaluate(`(() => { const a=document.querySelector('ytcp-video-info a, .video-url-fadeable a'); return a ? a.href : ''; })()`);
    vid = (link.match(/(?:shorts\/|youtu\.be\/|v=)([\w-]{11})/) || [])[1] || '';
    if (!vid) await sleep(2000);
  }
  step('VIDEO_ID ' + vid);
  if (!vid) throw new Error('no video id — 예약 누르기 전 중단(ID 모르는 예약 영상이 생기지 않게)');

  // 2) 제목·설명 (contenteditable) — 기존 내용 지우고 입력
  const setText = (sel, text) => p.evaluate(`(() => { const el = document.querySelector(${JSON.stringify(sel)}); el.focus();
    document.execCommand('selectAll', false, null); document.execCommand('insertText', false, ${JSON.stringify(text)});
    el.dispatchEvent(new Event('input', {bubbles:true})); return el.innerText.trim().slice(0, 40); })()`);
  step('title ' + await setText('#title-textarea #textbox', TITLE));
  step('desc ' + await setText('#description-textarea #textbox', DESC));

  // 3) 아동용 아님
  step('kids ' + await p.evaluate(`(() => { const b=document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]'); if(!b) return 'no radio'; b.click(); return b.getAttribute('aria-checked'); })()`));

  // 4) 관련 동영상은 업로드 후 aside_related.js 로 따로 지정(업로드 창 안에서는 선택 창이 불안정)

  // 5) 다음 → 다음 → 다음 (동영상 요소, 검토 → 공개 상태)
  for (let i = 0; i < 3; i++) {
    await p.evaluate(`document.querySelector('#next-button').click()`);
    await sleep(2500);
  }
  step('at visibility');

  // 6) 예약: 펼치고 날짜·시간 입력
  await p.evaluate(`(() => { const b=document.querySelector('#second-container-expand-button'); if (b) b.click(); })()`);
  await sleep(1500);
  await p.evaluate(`document.querySelector('#datepicker-trigger').click()`);
  await sleep(1500);
  step('date ' + await p.evaluate(`(() => { const i=document.querySelector('ytcp-date-picker tp-yt-paper-input input, ytcp-date-picker input'); if(!i) return 'no date input';
    i.focus(); i.select(); document.execCommand('insertText', false, ${JSON.stringify(DATE_TEXT)}); i.dispatchEvent(new Event('input',{bubbles:true})); return i.value; })()`));
  await p.keyboard.press('Enter');
  await sleep(1500);
  step('time ' + await p.evaluate(`(() => { const i=document.querySelector('#time-of-day-container input'); if(!i) return 'no time input';
    i.focus(); i.select(); document.execCommand('insertText', false, ${JSON.stringify(TIME_TEXT)}); i.dispatchEvent(new Event('input',{bubbles:true})); return i.value; })()`));
  await p.keyboard.press('Enter');
  await sleep(1500);
  const shown = await p.evaluate(`(() => { const d=document.querySelector('#datepicker-trigger'); const t=document.querySelector('#time-of-day-container input'); return (d?d.innerText.trim():'') + ' | ' + (t?t.value:''); })()`);
  step('schedule shown ' + shown);
  if (!shown.includes(DATE_TEXT) || !shown.includes(TIME_TEXT)) {
    throw new Error('schedule mismatch: ' + shown);
  }


  // 8) 업로드 끝날 때까지 기다린 뒤 예약 버튼
  for (let i = 0; i < 120; i++) {
    const prog = await p.evaluate(`(() => (document.querySelector('ytcp-video-upload-progress')||{}).innerText || '')()`);
    if (!/업로드 중|Uploading/.test(prog)) break;
    await sleep(2000);
  }
  await p.evaluate(`document.querySelector('#done-button').click()`);
  await sleep(6000);
  step('done clicked');
  result = vid ? 'OK ' + vid : 'FAIL no video id';
} catch (e) {
  result = 'FAIL ' + String(e.message || e).slice(0, 200);
  // 실패해도 초안 ID 는 남긴다(파이썬 쪽에서 API 로 마저 완성)
}
await fs.unlink('up.mp4').catch(() => {});
console.log('RESULT: ' + result);
await closeTab(p);
