// 사용: VID, TARGET_TITLE, TARGET_ID(롱폼 영상 ID) 를 앞에 정의해서 실행. 결과는 마지막에 RESULT 줄.
const p = await openTab(`https://studio.youtube.com/video/${VID}/edit`);
await sleep(5000);
const deep = `(pred) => { const walk = (root) => { for (const e of root.querySelectorAll('*')) { if (e.shadowRoot) { const r = walk(e.shadowRoot); if (r) return r; } if (pred(e)) return e; } }; return walk(document); }`;
const readVal = () => p.evaluate(`(() => { const lab=[...document.querySelectorAll('.label-text')].find(e=>e.textContent.trim()==='관련 동영상'); const trig=lab && lab.closest('ytcp-dropdown-trigger'); return trig ? trig.innerText.replace(/\\s+/g,' ').trim() : null; })()`);
let before = await readVal();
for (let i = 0; i < 20 && !before; i++) { await sleep(2000); before = await readVal(); }   // Studio 로딩·처리 대기(최대 40초)
let res = 'FAIL';
if (!before) { res = 'FAIL no related-video field'; }
else if (before.includes(TARGET_TITLE.slice(0, 12))) { res = 'OK already set'; }
else {
  await p.evaluate(`(() => { const lab=[...document.querySelectorAll('.label-text')].find(e=>e.textContent.trim()==='관련 동영상'); const t=lab.closest('ytcp-dropdown-trigger'); t.scrollIntoView({block:'center'}); t.click(); })()`);
  await sleep(2500);
  // 검색: 롱폼 영상 ID 로(제목 일부는 단어가 잘리면 결과 0). value 대입 말고 실제 입력처럼 insertText
  await p.evaluate(`(() => { const d=[...document.querySelectorAll('ytcp-dialog')].find(x=>x.innerText.includes('특정 동영상 선택')); const inp=d && d.querySelector('input'); if (inp) { inp.focus(); inp.select(); document.execCommand('insertText', false, ${JSON.stringify(TARGET_ID)}); inp.dispatchEvent(new Event('input',{bubbles:true})); } })()`);
  await sleep(2500);
  const picked = await p.evaluate(`(() => { const d=[...document.querySelectorAll('ytcp-dialog')].find(x=>x.innerText.includes('특정 동영상 선택')); if(!d) return 'no dialog';
    const cands=[...d.querySelectorAll('*')].filter(e=>e.children.length===0 && e.textContent.trim().startsWith(${JSON.stringify(TARGET_TITLE.slice(0, 15))}));
    if(!cands.length) return 'not found';
    const row=cands[0].closest('[role=option], ytcp-video-pick-dialog-item, .video-pick, li, ytcp-entity-card, div[tabindex]') || cands[0];
    row.scrollIntoView({block:'center'}); row.click(); return 'picked '+row.tagName; })()`);
  console.log('pick:', picked);
  await sleep(2500);
  const mid = await readVal();
  console.log('field now:', mid);
  const saved = await p.evaluate(`(() => { const b=document.querySelector('#save'); if(!b) return 'no save'; if(b.hasAttribute('disabled') || b.getAttribute('aria-disabled')==='true') return 'save disabled'; b.click(); return 'saved'; })()`);
  console.log('save:', saved);
  await sleep(5000);
  // 새로 열어서 저장값 확인
  await p.goto?.(`https://studio.youtube.com/video/${VID}/edit`) ?? p.evaluate(`location.reload()`);
  await sleep(6000);
  const after = await readVal();
  console.log('after reload:', after);
  res = after && after.includes(TARGET_TITLE.slice(0, 12)) ? 'OK' : 'FAIL not saved (' + after + ')';
}
console.log('RESULT: ' + res);
await closeTab?.(p);
