// Layout checks the DOM cannot answer: icon size, row geometry, colour inheritance.
const { chromium } = require('playwright');
let pass = 0, fail = 0;
const ok = (c, m) => { c ? pass++ : (fail++, console.log('  FAIL ' + m)); };

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const w of [1440, 1024, 760]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 } });
    pg.on('pageerror', e => { fail++; console.log('  JS ERROR ' + e.message); });
    await pg.goto('file:///tmp/wt/out/ch15-review.html');
    await pg.waitForTimeout(250);
    // The export controls are disabled until a note exists, so make one —
    // measuring a disabled button's geometry would not prove anything.
    await pg.evaluate(() => {
      const b = document.querySelector('.blk[id]');
      b.querySelector('.blk__add').click();
      const s = document.querySelector('.note-slot[data-for="' + b.id + '"]');
      s.querySelector('textarea').value = 'geometry fixture';
      s.querySelector('[data-act="save"]').click();
    });
    await pg.waitForTimeout(120);

    const r = await pg.evaluate(() => {
      const g = id => document.getElementById(id).getBoundingClientRect();
      const svg = id => document.getElementById(id).querySelector('svg').getBoundingClientRect();
      const col = id => getComputedStyle(document.getElementById(id).querySelector('svg')).color;
      const bar = document.querySelector('.rev-bar').getBoundingClientRect();
      return {
        ids: ['reviewBtn','dlBtn','copyBtn'].map(id => ({
          id, b: g(id), s: svg(id), color: col(id),
          txt: document.getElementById(id).textContent.trim()
        })),
        bar, appbarH: document.querySelector('.appbar').getBoundingClientRect().height,
        vh: innerHeight
      };
    });

    for (const x of r.ids) {
      ok(x.s.width > 10 && x.s.width < 18, `${w}px ${x.id} icon ${x.s.width.toFixed(1)}px wide`);
      ok(Math.abs(x.s.width - x.s.height) < 0.6, `${w}px ${x.id} icon square`);
      // icon vertically centred against the button box
      const dc = Math.abs((x.s.top + x.s.height / 2) - (x.b.top + x.b.height / 2));
      ok(dc < 1.5, `${w}px ${x.id} icon centred (off by ${dc.toFixed(2)}px)`);
      // icon sits left of the text, inside the button
      ok(x.s.left >= x.b.left - 0.5 && x.s.right <= x.b.right, `${w}px ${x.id} icon inside the button`);
      ok(x.b.height <= 34, `${w}px ${x.id} still a small button (${x.b.height.toFixed(1)}px)`);
    }
    // colour inheritance: primary button's icon differs from the outlined ones
    ok(r.ids[0].color !== r.ids[2].color, `${w}px primary icon inherits its own token`);
    // the bar is one line and does not eat the viewport
    ok(r.bar.height < 70, `${w}px footer bar single row (${r.bar.height.toFixed(1)}px)`);
    ok(r.bar.bottom <= r.vh + 0.5, `${w}px footer bar pinned to the bottom`);
    // buttons in source order left to right, none overlapping
    const [a1, a2, a3] = r.ids.map(x => x.b);
    ok(a1.right <= a2.left + 0.5 && a2.right <= a3.left + 0.5, `${w}px buttons in order, no overlap`);

    // dark mode: the icon must follow
    await pg.click('#modeBtn'); await pg.waitForTimeout(120);
    const dk = await pg.evaluate(() => ['reviewBtn','dlBtn','copyBtn']
      .map(id => getComputedStyle(document.getElementById(id).querySelector('svg')).color));
    ok(dk.every((c, i) => c !== r.ids[i].color), `${w}px icons change colour in dark mode`);

    // the real dialog, not a shim
    await pg.click('#modeBtn');
    await pg.click('#reviewBtn'); await pg.waitForTimeout(150);
    ok(await pg.evaluate(() => document.getElementById('exportDlg').open), `${w}px View review notes opens the dialog`);
    await pg.evaluate(() => document.getElementById('exportDlg').close());
    await pg.close();
  }
  await b.close();
  console.log(`btnshot.js: ${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})();
