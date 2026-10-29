// Footer button row: labels, icons, placement, and that the export still works.
const fs = require('fs');
const { JSDOM } = require('jsdom');
let pass = 0, fail = 0;
const ok = (c, m) => { c ? pass++ : (fail++, console.log('  FAIL ' + m)); };

const html = fs.readFileSync('/tmp/wt/out/ch15-review.html', 'utf8');
const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'file:///tmp/wt/out/ch15-review.html', pretendToBeVisual: true });
const d = dom.window.document;
// jsdom implements <dialog> but not showModal/close. Shim them so the handlers
// can run; real modal behaviour is checked in the browser pass, not here.
for (const dlg of d.querySelectorAll('dialog')) {
  dlg.showModal = function(){ this.setAttribute('open',''); };
  dlg.close = function(){ this.removeAttribute('open'); };
}
dom.window.addEventListener('error', e => { fail++; console.log('  JS ERROR ' + e.message); });

const bar = d.querySelector('.rev-bar__inner');
const appbar = d.querySelector('.appbar');

// 1. placement
ok(bar.querySelector('#reviewBtn'), 'reviewBtn moved into the footer bar');
ok(!appbar.querySelector('#reviewBtn'), 'reviewBtn no longer in the appbar');
ok(appbar.querySelector('#focusBtn') && appbar.querySelector('#modeBtn'), 'Focus and Dark stay in the appbar');

// 2. labels
const label = id => d.getElementById(id).textContent.trim();
ok(label('reviewBtn') === 'View review notes', 'reviewBtn label: ' + label('reviewBtn'));
ok(label('dlBtn') === 'Download review notes', 'dlBtn label: ' + label('dlBtn'));
ok(label('copyBtn') === 'Copy review notes', 'copyBtn label: ' + label('copyBtn'));
ok(!/Download \.md|Copy all suggestions|Review all/.test(html), 'no old labels anywhere in the output');

// 3. icons
for (const id of ['reviewBtn', 'dlBtn', 'copyBtn']) {
  const b = d.getElementById(id);
  const svg = b.querySelector('svg');
  ok(svg, id + ' has an inline svg');
  ok(svg && svg.getAttribute('stroke') === 'currentColor', id + ' icon strokes currentColor (inherits the token)');
  ok(svg && svg.getAttribute('aria-hidden') === 'true', id + ' icon is hidden from AT');
  ok(svg && !/fill="(?!none)/.test(svg.outerHTML), id + ' icon is not filled with a hard-coded colour');
  // the icon must never be the only label
  ok(b.textContent.trim().length > 3, id + ' still carries its text label');
  ok(!/#[0-9a-f]{3,6}/i.test(svg.outerHTML), id + ' icon has no hard-coded hex');
}

// 4. the button still does its job
const p = d.querySelector('.blk[id]');
p.querySelector('.blk__add').click();
const slot = d.querySelector('.note-slot[data-for="' + p.id + '"]');
const ta = slot.querySelector('textarea');
ta.value = 'A note for the export.';
slot.querySelector('[data-act="save"]').click();
d.getElementById('reviewBtn').click();
const box = d.getElementById('exportBox').value;
ok(box.includes('A note for the export.'), 'View review notes shows the note');
ok(box.includes('# Review of'), 'export header intact');
ok(d.getElementById('exportDlg').hasAttribute('open'), 'dialog opened');

// 5. wording consistency in the chrome
ok(d.getElementById('count').textContent.includes('note'), 'count reads in notes: ' + d.getElementById('count').textContent);
ok(d.querySelector('#exportDlg .panel__title').textContent === 'Review notes', 'dialog title renamed');
ok(d.getElementById('clearYes').textContent.trim() === 'Clear all notes', 'clear confirm renamed');

// 6. empty state — the whole export group goes disabled together, with the
// count beside it as the explanation. A live "View" next to three dead
// siblings reads as a bug.
d.getElementById('clearYes').click();
ok(['reviewBtn','copyBtn','dlBtn','clearBtn'].every(id => d.getElementById(id).disabled),
   'all four export controls disabled at zero notes');
ok(d.getElementById('count').textContent.trim() === 'No notes yet',
   'the count explains why they are disabled');
// and they come back
p.querySelector('.blk__add').click();
const slot2 = d.querySelector('.note-slot[data-for="' + p.id + '"]');
slot2.querySelector('textarea').value = 'second note';
slot2.querySelector('[data-act="save"]').click();
ok(['reviewBtn','copyBtn','dlBtn','clearBtn'].every(id => !d.getElementById(id).disabled),
   'all four re-enable once a note exists');

console.log(`btn.js: ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
