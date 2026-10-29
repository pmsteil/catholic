(function(){
  "use strict";
  var KEY = (typeof REVIEW_KEY !== "undefined") ? REVIEW_KEY : "review-doc";
  var TITLE  = (typeof REVIEW_TITLE  !== "undefined") ? REVIEW_TITLE  : document.title;
  var SOURCE = (typeof REVIEW_SOURCE !== "undefined") ? REVIEW_SOURCE : "";
  var LABEL  = (typeof REVIEW_LABEL  !== "undefined") ? REVIEW_LABEL  : "";
  var STEM   = (typeof REVIEW_STEM   !== "undefined") ? REVIEW_STEM   : "review";
  var GENERATOR = (typeof REVIEW_GENERATOR !== "undefined") ? REVIEW_GENERATOR : "";
  // Build time, as a UTC instant. Rendered in the reader's own timezone below —
  // the file may well have been built on a machine in a different one.
  var GENERATED_ISO = (typeof REVIEW_GENERATED !== "undefined") ? REVIEW_GENERATED : "";
  var GENERATED = "";
  (function(){
    if (!GENERATED_ISO) return;
    var d = new Date(GENERATED_ISO);
    if (isNaN(d.getTime())) return;          // keep the server-rendered fallback
    try {
      GENERATED = d.toLocaleString(undefined, { day: 'numeric', month: 'long',
        year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch(e) { return; }
    var el = document.querySelector('.colophon time[datetime]');
    if (el) el.textContent = GENERATED;
  })();
  // This document's own filename, read from the URL rather than baked in at
  // build time — the reader may well have renamed or moved the file, and a
  // stale name in the export is worse than none.
  var FILE = (function(){
    try {
      var last = decodeURIComponent((location.pathname || '').split('/').pop() || '');
      if (last) return last;
    } catch(e) {}
    return (typeof REVIEW_FILE !== "undefined") ? REVIEW_FILE : '';
  })();
  // ── note storage ────────────────────────────────────────────────────────
  // Notes are a review pass in progress and must survive things the reviewer
  // did not choose: a rebuilt document, a bumped storage key, a different
  // browser, a cleared cache. Three layers do that.
  //
  //   1. Every note is stored with the *text it was attached to*, so it can be
  //      re-attached by quotation when ids shift under a rebuild.
  //   2. Notes for the same source document are recoverable across storage
  //      keys, so a new build of a chapter can pick up the pass already in
  //      progress under the previous key.
  //   3. The exported Markdown carries a machine-readable copy of all of it, so
  //      the file the reviewer already saves is also a complete restore point —
  //      the one layer that survives losing the browser entirely.
  //
  // DOC is what ties versions of the same document together: the source path,
  // which stays put while keys, filenames and ids move.
  var DOC = (typeof REVIEW_DOC !== "undefined" && REVIEW_DOC) ? REVIEW_DOC
          : (SOURCE || STEM || TITLE);
  var STORE_V = 1;

  var notes  = {};   // id -> note text
  var quotes = {};   // id -> the target's text when the note was written
  var refs   = {};   // id -> the target's reference, for notes that lose their target
  // Notes whose target no longer exists in this document. Kept, surfaced in the
  // export, and never silently dropped — a note the reviewer wrote is theirs.
  var unplaced = [];

  function nowISO(){ try { return new Date().toISOString(); } catch(e) { return ''; } }

  // Accepts the current payload and the original flat `{id: "text"}` map, so a
  // document saved by an earlier build still opens with its notes.
  function readStore(raw){
    if (!raw) return null;
    var o; try { o = JSON.parse(raw); } catch(e) { return null; }
    if (!o || typeof o !== 'object') return null;
    if (o.notes && typeof o.notes === 'object') {
      return { doc: o.doc || '', title: o.title || '', saved: o.saved || '',
               notes: o.notes, unplaced: o.unplaced || [] };
    }
    var flat = {}, any = false;
    for (var k in o) if (typeof o[k] === 'string') { flat[k] = { t: o[k] }; any = true; }
    return any ? { doc:'', title:'', saved:'', notes: flat, unplaced: [] } : null;
  }

  function plainOf(el){ return ((el && el.dataset.plain) || '').trim(); }

  // Where does a stored note belong in *this* document? The id it was written
  // against is only trustworthy if the text there still matches; otherwise the
  // quotation is what identifies the passage. A quotation matching more than one
  // target ("✓" appears in eighty cells) identifies nothing, so it is left
  // unplaced rather than guessed at.
  function locate(id, entry){
    var el = document.getElementById(id);
    var live = !!(el && el.matches && el.matches(SEL));
    var q = (entry.q || '').trim();
    if (!q) return live ? id : null;      // a note from before quotes were kept
    if (live && plainOf(el) === q) return id;
    var all = targets(), hit = null;
    for (var i = 0; i < all.length; i++) {
      if (plainOf(all[i]) === q) { if (hit) return null; hit = all[i].id; }
    }
    // Deliberately no fall back to the id. Block ids are positional, so once a
    // paragraph is deleted the old id still resolves — to a *different*
    // paragraph. Attaching there would silently move a note onto text it was
    // never about, which is far worse than admitting it has no home.
    return hit;
  }

  // Merge a stored payload into the live note set. Returns what happened so the
  // caller can tell the reviewer rather than changing the document silently.
  function adopt(store, opts){
    opts = opts || {};
    var placed = 0, moved = 0, lost = 0;
    for (var id in store.notes) {
      var e = store.notes[id];
      var text = (typeof e === 'string') ? e : (e && e.t) || '';
      if (!text) continue;
      var entry = (typeof e === 'string') ? {} : (e || {});
      if (opts.keepExisting && notes[id]) continue;
      var target = locate(id, entry);
      if (target) {
        if (target !== id) moved++;
        notes[target]  = text;
        quotes[target] = entry.q || plainOf(document.getElementById(target));
        refs[target]   = entry.ref || '';
        placed++;
      } else {
        unplaced.push({ t: text, ref: entry.ref || id, q: entry.q || '' });
        lost++;
      }
    }
    (store.unplaced || []).forEach(function(u){
      // An unplaced note may find its home again in a later build.
      var target = u.q ? locate('', { q: u.q }) : null;
      if (target && !notes[target]) {
        notes[target] = u.t; quotes[target] = u.q; refs[target] = u.ref || ''; placed++; moved++;
      } else { unplaced.push(u); lost++; }
    });
    return { placed: placed, moved: moved, lost: lost };
  }

  // Other saved passes for this same source document, newest first. This is what
  // makes a rebuilt document — or one whose storage key was bumped — able to pick
  // up a review already in progress.
  function otherPasses(){
    var out = [];
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var k = localStorage.key(i);
        if (!k || k === KEY || k.indexOf(':focus') !== -1) continue;
        var s = readStore(localStorage.getItem(k));
        if (!s || !s.notes) continue;
        var n = Object.keys(s.notes).length;
        if (!n) continue;
        // Only offer a pass we can actually confirm belongs to this document.
        // A pass with neither .doc nor .title recorded (very old, saved before
        // this identity check existed) is NOT "unproven, so allow it" — that
        // let an untagged legacy note from one chapter get offered as a
        // recovery for every other chapter opened afterward in the same
        // browser. Treat "nothing to check against" as "not a match".
        if (DOC) {
          if (s.doc) { if (s.doc !== DOC) continue; }
          else if (s.title) { if (s.title !== TITLE) continue; }
          else continue;   // no identity recorded at all — cannot confirm, skip
        }
        out.push({ key: k, store: s, n: n, saved: s.saved || '' });
      }
    } catch(e) { return []; }
    out.sort(function(a, b){ return a.saved < b.saved ? 1 : a.saved > b.saved ? -1 : 0; });
    return out;
  }

  // ── target model ────────────────────────────────────────────────────────
  // Four kinds of target — block, sentence, table row, table cell — but only one
  // code path. Every target owns a <div class="note-slot" data-for="ID"> emitted
  // by the builder, so finding a target's note never depends on its shape.
  var SEL = '.blk[id],.sent[id],.rblk[id],.cblk[id],.hblk[id]';
  function targets(){ return Array.prototype.slice.call(document.querySelectorAll(SEL)); }
  function slotOf(el){ return document.querySelector('.note-slot[data-for="' + el.id + '"]'); }
  function kindOf(el){
    return el.classList.contains('sent') ? 'sentence'
         : el.classList.contains('cblk') ? 'cell'
         : el.classList.contains('rblk') ? 'row'
         : el.classList.contains('hblk') ? 'heading' : 'block';
  }

  // innerText is not universal — jsdom and some embedded engines omit it, and
  // reading it blind throws inside a click handler, which looks like a dead button.
  function textOf(el){
    if (!el) return '';
    var t = (typeof el.innerText === 'string') ? el.innerText : el.textContent;
    return (t || '').replace(/[ \t]+/g, ' ').replace(/ *\n */g, '\n').trim();
  }
  function sourceText(el){
    var k = kindOf(el);
    if (k === 'row') {
      return Array.prototype.slice.call(el.querySelectorAll('td:not(.col-act)'))
        .map(function(td){ return textOf(td.querySelector('.cell__text')); }).join(' | ');
    }
    if (k === 'cell') return textOf(el.querySelector('.cell__text'));
    if (k === 'sentence') return textOf(el);
    // The heading's own ✎ button lives inside it, so read the text span, not the
    // element — otherwise the prefill picks up the pencil.
    if (k === 'heading') return textOf(el.querySelector('.hblk__text'));
    return textOf(el.querySelector('.blk__body'));
  }

  var flash = document.getElementById('flash');
  function say(msg, kind){
    flash.innerHTML = '<div class="alert alert--' + (kind || 'success') + '"><div>' + msg + '</div></div>';
    clearTimeout(say._t); say._t = setTimeout(function(){ flash.innerHTML = ''; }, 3200);
  }
  function payload(){
    var p = { v: STORE_V, doc: DOC, title: TITLE, saved: nowISO(), notes: {} };
    for (var id in notes) {
      var el = document.getElementById(id);
      p.notes[id] = { t: notes[id],
                      ref: (el && el.dataset.ref) || refs[id] || '',
                      q: quotes[id] || plainOf(el) };
    }
    if (unplaced.length) p.unplaced = unplaced;
    return p;
  }
  function save(){
    try { localStorage.setItem(KEY, JSON.stringify(payload())); }
    catch(e){ say('Could not save to this browser — download your review notes before closing.','danger'); }
    render();
  }
  // Questions count too: if Claude left three questions and the reader hasn't
  // written a note of their own, the export bar should not read "No notes yet"
  // and sit disabled — there is something to export either way.
  function count(){ return Object.keys(notes).length + unplaced.length + qblocks().length; }

  // ── render ──────────────────────────────────────────────────────────────
  function render(){
    var noteN = Object.keys(notes).length + unplaced.length, qN = qblocks().length, n = noteN + qN;
    var label = !noteN && !qN ? 'No notes yet'
      : !qN ? (noteN + (noteN === 1 ? ' note' : ' notes'))
      : !noteN ? (qN + (qN === 1 ? ' question' : ' questions'))
      : (noteN + (noteN === 1 ? ' note' : ' notes')) + ' · ' + qN + (qN === 1 ? ' question' : ' questions');
    document.getElementById('count').textContent = label;
    // Hidden, not just disabled: a reviewer with zero notes and zero questions
    // has nothing these buttons act on, and a visible-but-dead control reads
    // as broken rather than as "nothing here yet".
    ['reviewBtn','copyBtn','clearBtn'].forEach(function(id){ document.getElementById(id).hidden = n === 0; });
    updateNoteNav();

    targets().forEach(function(el){
      if (el.dataset.editing === '1') return;
      var slot = slotOf(el); if (!slot) return;
      if (notes[el.id]) {
        el.classList.add('has-note');
        slot.innerHTML =
          '<div class="note"><span class="note__ref">' + el.dataset.ref + '</span>'
          + '<span class="note__text"></span>'
          + '<span class="note__acts">'
          + '<button class="btn btn--sm btn--icon" data-act="edit" title="Edit this note"'
          + ' aria-label="Edit the note on ' + el.dataset.ref + '">✎</button>'
          + '<button class="btn btn--sm btn--icon" data-act="del" title="Remove this note"'
          + ' aria-label="Remove the note on ' + el.dataset.ref + '">×</button>'
          + '</span></div>';
        slot.querySelector('.note__text').textContent = notes[el.id];
      } else {
        el.classList.remove('has-note');
        slot.innerHTML = '';
      }
    });
    // A row's note lives in a following <tr>, which must be hidden when empty or
    // the table gains a blank stripe under every row.
    Array.prototype.forEach.call(document.querySelectorAll('tr.note-row'), function(tr){
      tr.hidden = !tr.querySelector('.note-slot').innerHTML;
    });
  }

  // ── editor ──────────────────────────────────────────────────────────────
  function openEditor(el){
    var slot = slotOf(el); if (!slot) return;
    autoCommit(el);
    el.dataset.editing = '1';
    var tr = el.closest ? null : null;
    var row = slot.closest('tr.note-row'); if (row) row.hidden = false;
    slot.innerHTML =
      '<div class="note note--editing"><span class="note__ref">' + el.dataset.ref + '</span>'
      + '<span class="note__field"><label class="visually-hidden" for="ta-' + el.id + '">'
      + 'Suggested edit for ' + el.dataset.ref + '</label>'
      + '<textarea id="ta-' + el.id + '" rows="3"></textarea></span>'
      + '<span class="note__acts is-open">'
      + '<button class="btn btn--primary btn--sm" data-act="save">Save</button>'
      + '<button class="btn btn--sm" data-act="cancel">Cancel</button></span></div>';
    var ta = slot.querySelector('textarea');
    var original = sourceText(el);
    ta.value = notes[el.id] !== undefined ? notes[el.id] : original;
    ta.dataset.original = original;
    ta.rows = Math.max(2, Math.min(14, Math.ceil(ta.value.length / 78) + 1));
    ta.focus();
    // Caret at the end, nothing selected: a full selection means the first
    // keystroke destroys the text the reviewer came to edit.
    ta.setSelectionRange(ta.value.length, ta.value.length);
    ta.addEventListener('keydown', function(ev){
      if (ev.key === 'Escape') { ev.stopPropagation(); closeEditor(el); }
      // preventDefault matters here: without it, the browser's own default
      // handling for Enter (inserting a newline) can still run after this
      // handler returns, since nothing has told it the key was spoken for.
      // That default insert racing the textarea getting torn out of the DOM
      // by commit()/render() is exactly the kind of gap that shows up as
      // "save works on some blocks but not others" — stop it outright rather
      // than rely on timing.
      if ((ev.metaKey || ev.ctrlKey) && ev.key === 'Enter') { ev.preventDefault(); commit(el); }
    });
  }
  function afterEdit(el){
    el.dataset.editing = '0';
    var btn = el.classList.contains('sent') || el.classList.contains('cblk')
      ? el : el.querySelector('.blk__add');
    if (btn && btn.focus) btn.focus();
    // Deliberately does NOT set the keyboard cursor. Opening an editor with the
    // mouse should not leave a selection behind, or Esc afterwards clears an
    // invisible cursor instead of doing what the reader expects.
  }
  function commit(el){
    var slot = slotOf(el), ta = slot && slot.querySelector('textarea');
    if (!ta) { el.dataset.editing = '0'; render(); return; }
    var v = (ta.value || '').trim();
    if (v === (ta.dataset.original || '').trim()) {
      afterEdit(el); render();
      say('No change — nothing saved for ' + el.dataset.ref + '.', 'warn');
      return;
    }
    if (v) {
      notes[el.id] = v;
      // Captured now, while the target is in front of us: this is what lets the
      // note find its way back if the document is rebuilt and ids shift.
      quotes[el.id] = plainOf(el);
      refs[el.id] = el.dataset.ref || '';
    } else {
      delete notes[el.id]; delete quotes[el.id]; delete refs[el.id];
    }
    afterEdit(el); save();
    say(v ? 'Saved ' + el.dataset.ref : 'Cleared ' + el.dataset.ref);
  }
  function closeEditor(el){ afterEdit(el); render(); }

  // Leaving an open editor saves it. Someone who types a suggestion and then
  // clicks the next paragraph has finished that thought — discarding it because
  // they did not press Save is losing their work on a technicality.
  function autoCommit(except){
    var open = document.querySelector('[data-editing="1"]');
    if (!open || open === except) return false;
    var slot = slotOf(open), ta = slot && slot.querySelector('textarea');
    if (!ta) { open.dataset.editing = '0'; render(); return false; }
    var v = (ta.value || '').trim();
    var changed = v !== (ta.dataset.original || '').trim();
    if (changed) {
      if (v) { notes[open.id] = v; } else { delete notes[open.id]; }
      open.dataset.editing = '0'; save();
      say('Saved ' + open.dataset.ref + ' automatically.');
    } else {
      open.dataset.editing = '0'; render();   // silent: nothing was written
    }
    return changed;
  }

  // ── notes whose passage changed ─────────────────────────────────────────
  // A note in `unplaced` has no live element to hang its "has-note" styling
  // on — that's what unplaced means — so render() can never show it in the
  // body, only the export could. But an unplaced note is very often exactly
  // the reviewer's own suggestion that just got applied, and the reviewer
  // wants to see that it's still accounted for until they've checked the new
  // prose and dismissed it themselves. So it gets a panel of its own, with a
  // Clear per note — visible in the document, not just inside the export
  // dialog, and it stays until the reviewer says otherwise.
  function renderUnplaced(){
    var panel = document.getElementById('unplacedPanel'), list = document.getElementById('unplacedList');
    if (!panel || !list) return;
    if (!unplaced.length) { panel.hidden = true; list.innerHTML = ''; return; }
    panel.hidden = false;
    document.getElementById('unplacedCount').textContent =
      '(' + unplaced.length + (unplaced.length === 1 ? ' note' : ' notes') + ')';
    list.innerHTML = unplaced.map(function(u, i){
      var esc = function(s){ return (s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;'); };
      return '<li data-i="' + i + '"><p class="unplaced__ref">' + esc(u.ref || 'note') + '</p>'
        + '<blockquote class="unplaced__was">' + esc(u.q || '(text not recorded)') + '</blockquote>'
        + '<p class="unplaced__note">' + esc(u.t) + '</p>'
        + '<button class="btn btn--sm" data-act="clear-unplaced" data-i="' + i + '">Clear</button></li>';
    }).join('');
  }
  document.addEventListener('click', function(ev){
    var btn = ev.target.closest && ev.target.closest('[data-act="clear-unplaced"]');
    if (!btn) return;
    var i = parseInt(btn.dataset.i, 10);
    if (isNaN(i)) return;
    unplaced.splice(i, 1);
    save(); renderUnplaced();
    say('Cleared.');
  });

  // ── reviewer questions (Claude → reader) ────────────────────────────────
  // A question box is a different kind of thing from a note: the reviewer
  // isn't marking up the chapter, they're answering something asked of them.
  // So it gets its own storage, separate from `notes`, keyed by the stable
  // "key" the question was built with rather than a target id — a question's
  // identity doesn't need the notes model's quote-based re-attachment, because
  // it isn't attached to shifting prose in the first place.
  var ANSWERS_KEY = KEY + ':answers';
  var answers = {};
  function readAnswers(raw){
    if (!raw) return {};
    try { var o = JSON.parse(raw); return (o && typeof o === 'object') ? o : {}; }
    catch(e) { return {}; }
  }
  function saveAnswers(){
    try { localStorage.setItem(ANSWERS_KEY, JSON.stringify(answers)); }
    catch(e){ say('Could not save your answer to this browser.', 'danger'); }
  }
  function qblocks(){ return Array.prototype.slice.call(document.querySelectorAll('.qblk[data-qkey]')); }
  function markAnswered(box, has){
    box.classList.toggle('qblk--answered', !!has);
    var label = box.querySelector('.qblk__label');
    if (label) label.textContent = has ? 'Question from your reviewer — answered' : 'Question from your reviewer';
  }
  // Questions get their nav entry inline, at their real position among the
  // section links — the builder already put it there and gave it the box's
  // own highlight class. All the runtime has to do is keep that entry's
  // answered state in sync, by matching its href back to the question's key.
  function markQuestionNav(key, has){
    var a = document.querySelector('.toc-question a[href="#q-' + key + '"]');
    if (a) a.classList.toggle('is-answered', !!has);
  }
  function loadAnswerBoxes(){
    answers = readAnswers(localStorage.getItem(ANSWERS_KEY));
    qblocks().forEach(function(box){
      var ta = box.querySelector('.qblk__answer'), key = box.dataset.qkey;
      if (!ta) return;
      ta.value = answers[key] || '';
      markAnswered(box, ta.value.trim());
      markQuestionNav(key, ta.value.trim());
    });
  }
  // No Save button, by design: a question box is meant to feel like filling in
  // a form field, not authoring an edit, and it should never be possible to
  // type an answer and lose it by navigating away.
  document.addEventListener('input', function(ev){
    var ta = ev.target.closest && ev.target.closest('.qblk__answer');
    if (!ta) return;
    var box = ta.closest('.qblk');
    answers[box.dataset.qkey] = ta.value;
    saveAnswers();
    markAnswered(box, ta.value.trim());
    markQuestionNav(box.dataset.qkey, ta.value.trim());
  });

  // ── pointer ─────────────────────────────────────────────────────────────
  document.addEventListener('click', function(ev){
    // Anything outside the open editor counts as leaving it. Buttons inside the
    // editor (Save, Cancel) are excluded so Cancel can still mean cancel.
    var inEditor = ev.target.closest && ev.target.closest('.note--editing');
    if (!inEditor) autoCommit(null);

    var btn = ev.target.closest('button');
    if (btn) {
      var act = btn.dataset.act;
      if (act) {
        var slot = btn.closest('.note-slot');
        var el = slot ? document.getElementById(slot.dataset.for) : null;
        if (el) {
          if (act === 'edit')   { openEditor(el); return; }
          if (act === 'save')   { commit(el); return; }
          if (act === 'cancel') { closeEditor(el); return; }
          if (act === 'del')    { delete notes[el.id]; save(); say('Removed ' + el.dataset.ref); return; }
        }
      }
      if (btn.classList.contains('blk__add')) { openEditor(btn.closest('.blk')); return; }
      if (btn.classList.contains('cell__add')) { openEditor(btn.closest('.cblk')); return; }
      if (btn.classList.contains('row__add')) { openEditor(btn.closest('.rblk')); return; }
      if (btn.classList.contains('hblk__add')) { openEditor(btn.closest('.hblk')); return; }
      return;
    }
    // Clicking the text edits it, whatever the text is — a heading, an epigraph,
    // a list, a table cell, a sentence. `closest` resolves to the finest target
    // under the pointer, so a sentence wins over its paragraph and a cell wins
    // over its table, and the coarser grain stays available from the ✎.
    if (!ev.target.closest) return;
    // A saved note is itself editable: clicking it reopens that note, rather
    // than opening a second editor for the block it hangs off. The note's own
    // text is what you want back in the box, and openEditor prefills with the
    // saved note when there is one.
    var inSlot = ev.target.closest('.note-slot');
    if (inSlot) {
      if (ev.target.closest('.note--editing')) return;   // already open; let the caret be
      var owner = document.getElementById(inSlot.dataset.for);
      if (!owner) return;
      var s = window.getSelection();
      if (s && !s.isCollapsed) return;
      openEditor(owner);
      return;
    }
    var t = ev.target.closest(SEL);
    if (!t) return;
    // Inside a table only the cells are click targets: a click on the table's own
    // padding should not open an editor for all eight rows at once. The explicit
    // "Comment on whole table" button is how that is asked for.
    if (t.classList.contains('blk--table')) return;
    // Only when nothing is selected — otherwise selecting text to read it would
    // fire the editor instead.
    var sel = window.getSelection();
    if (sel && !sel.isCollapsed) return;
    openEditor(t);   // mouse use leaves no keyboard cursor behind
  });

  // ── keyboard navigation ─────────────────────────────────────────────────
  // Up/Down walk the coarse targets — the units a reader thinks in. Left/Right
  // step into the fine ones: sentences inside a paragraph, cells inside a row.
  var current = null;
  function coarse(){
    return targets().filter(function(el){
      var k = kindOf(el); return k === 'block' || k === 'row';
    });
  }
  function fineOf(el){
    var k = kindOf(el);
    if (k === 'block') return Array.prototype.slice.call(el.querySelectorAll('.sent'));
    if (k === 'row')   return Array.prototype.slice.call(el.querySelectorAll('td.cblk'));
    return [];
  }
  function setCurrent(el, scroll, force){
    if (current) current.classList.remove('is-cur');
    current = el || null;
    if (!current) return;
    current.classList.add('is-cur');
    if (scroll !== false) {
      var r = current.getBoundingClientRect();
      if (force || r.top < 90 || r.bottom > window.innerHeight - 80) {
        current.scrollIntoView({ block: 'center' });
      }
    }
  }
  function step(dir){
    var list = coarse();
    if (!list.length) return;
    var base = current;
    if (base && (kindOf(base) === 'sentence' || kindOf(base) === 'cell')) {
      base = base.closest('.blk') || base.closest('.rblk');
    }
    var i = base ? list.indexOf(base) : -1;
    if (i === -1) {
      // start from whatever is on screen rather than the top of the document
      i = 0;
      for (var j = 0; j < list.length; j++) {
        if (list[j].getBoundingClientRect().top > 80) { i = j; break; }
      }
      setCurrent(list[i]);
      return;
    }
    setCurrent(list[Math.max(0, Math.min(list.length - 1, i + dir))]);
  }
  function stepFine(dir){
    if (!current) return;
    var k = kindOf(current);
    if (k === 'block' || k === 'row') {
      var f = fineOf(current);
      if (f.length) setCurrent(dir > 0 ? f[0] : f[f.length - 1]);
      return;
    }
    var parent = current.closest('.blk') || current.closest('.rblk');
    var sibs = fineOf(parent), i = sibs.indexOf(current) + dir;
    if (i < 0) { setCurrent(parent); return; }
    if (i >= sibs.length) { setCurrent(parent); return; }
    setCurrent(sibs[i]);
  }

  // ── prev/next note ──────────────────────────────────────────────────────
  // Jump directly between whatever needs the reviewer's attention — a note at
  // whatever granularity it was written at (sentence, cell, row, block,
  // heading), OR a question waiting for an answer — rather than walking
  // every paragraph in between the way Up/Down does. This is for revisiting
  // a pass, not exploring the chapter, so notes and questions share one
  // ordering: wherever each one actually sits in the document.
  function navTargets(){
    var noted = targets().filter(function(el){ return !!notes[el.id]; });
    var qs = qblocks();
    if (!qs.length) return noted;
    return noted.concat(qs).sort(function(a, b){
      var rel = a.compareDocumentPosition(b);
      return (rel & Node.DOCUMENT_POSITION_FOLLOWING) ? -1 : 1;
    });
  }
  function gotoNote(dir){
    var list = navTargets();
    if (!list.length) return;
    var i = current ? list.indexOf(current) : -1;
    var next = (i === -1) ? (dir > 0 ? list[0] : list[list.length - 1])
                           : list[(i + dir + list.length) % list.length];
    setCurrent(next);
  }
  var prevNoteBtn = document.getElementById('prevNoteBtn'), nextNoteBtn = document.getElementById('nextNoteBtn');
  if (prevNoteBtn) prevNoteBtn.addEventListener('click', function(){ gotoNote(-1); });
  if (nextNoteBtn) nextNoteBtn.addEventListener('click', function(){ gotoNote(1); });
  function updateNoteNav(){
    var has = navTargets().length > 0;
    if (prevNoteBtn) prevNoteBtn.hidden = !has;
    if (nextNoteBtn) nextNoteBtn.hidden = !has;
  }

  document.addEventListener('keydown', function(ev){
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if (typing || ev.metaKey || ev.ctrlKey || ev.altKey) {
      if (ev.key === 'Escape' && !typing) {} else return;
    }
    switch (ev.key) {
      case 'ArrowDown': ev.preventDefault(); autoCommit(null); step(1); return;
      case 'ArrowUp':   ev.preventDefault(); autoCommit(null); step(-1); return;
      // Left/Right are the physical-key equivalent of the header's prev/next
      // note buttons — requested explicitly, and it supersedes the older
      // "step into the sentence/cell inside the current block" behavior
      // those keys used to carry (stepFine() below is now unused; left in
      // place rather than deleted, in case that finer-grained stepping is
      // wanted back some other way later).
      case 'ArrowRight': ev.preventDefault(); gotoNote(1); return;
      case 'ArrowLeft':  ev.preventDefault(); gotoNote(-1); return;
      case 'e': case 'E':
        if (current) { ev.preventDefault(); openEditor(current); }
        return;
      case 'f': case 'F':
        ev.preventDefault(); setFocus(!document.body.classList.contains('is-focus')); return;
      case 'Escape':
        if (current) { setCurrent(null); return; }
        if (document.body.classList.contains('is-focus')) setFocus(false);
        return;
    }
  });

  // ── export ──────────────────────────────────────────────────────────────
  var KINDLABEL = { sentence: ' (sentence)', row: ' (table row)', heading: ' (heading)',
                    cell: ' (table cell)', block: ' (paragraph or block)' };
  function stamp(){
    var d = new Date(), z = function(n){ return (n < 10 ? '0' : '') + n; };
    return d.getFullYear() + '-' + z(d.getMonth() + 1) + '-' + z(d.getDate())
         + ' ' + z(d.getHours()) + ':' + z(d.getMinutes());
  }
  function buildMarkdown(){
    // Written to be handed to a person *or* a language model and acted on with
    // no other context. Crucially it does not claim every note is an edit —
    // a reviewer marks up prose with questions and objections as much as with
    // replacements, and a file that says "proposed edits" invites a model to
    // rewrite the text in answer to a question.
    var n = count();
    var out = ['# Review of ' + (LABEL ? LABEL + ' — ' : '') + TITLE, ''];
    if (SOURCE)    out.push('Source document: `' + SOURCE + '`  (the file these notes are about)');
    if (FILE)      out.push('Review file: `' + FILE + '`  (where the notes were made)');
    if (GENERATOR) out.push('Generated by: ' + GENERATOR + '  (what built this review file — use the same tool to rebuild it)');
    // Two different dates on purpose: if the review file was built long before
    // the notes were exported, the source may have moved on underneath it.
    if (GENERATED || GENERATED_ISO)
      out.push('Review file generated: ' + (GENERATED || GENERATED_ISO) + '  ');
    out.push('Exported: ' + stamp() + '  ');
    out.push(n + ' note' + (n === 1 ? '' : 's') + ' from a review pass.');
    out.push('');
    out.push('## How to read this file');
    out.push('');
    out.push('Each section below is one note the author attached to one specific place in'
             + (SOURCE ? ' the source document `' + SOURCE + '`' : ' the source document')
             + '. The review file is a generated HTML copy used to collect the notes; it is'
             + ' not the file to change.');
    out.push('');
    out.push('- The **heading** gives a reference, what kind of thing the note is attached to,');
    out.push('  and the section it sits in — e.g. `¶042·s3 (sentence) — Section 1 › Marxism`.');
    out.push('- The **quoted line** (`>`) is that text as it currently stands in the source.');
    out.push('- The **note** beneath it is the author writing about that text. It may be any of:');
    out.push('    - replacement prose to substitute for the quotation,');
    out.push('    - an instruction describing a change to make,');
    out.push('    - a question, an objection, a doubt, or an observation that wants a');
    out.push('      considered answer rather than an edit.');
    out.push('');
    out.push('  **Read each note on its own terms and respond to what it actually says.**');
    out.push('  Do not assume a note is a replacement. If it reads as finished prose meant to');
    out.push('  stand in for the quotation, treat it as one; if it asks a question or raises a');
    out.push('  concern, answer it and say what you would change and why — do not quietly');
    out.push('  rewrite the passage in place of replying.');
    out.push('');
    out.push('- Where a note does call for a change, **its scope is exactly the quoted text**.');
    out.push('  A `(sentence)` note concerns that one sentence inside its paragraph; a');
    out.push('  `(table cell)` note concerns that one cell. Do not rewrite the surrounding');
    out.push('  text to match unless the note asks for it.');
    out.push('- References like `¶042` are generated by the review tool and **do not appear in');
    out.push('  the source file**. Locate each note by its quoted text and section heading.');
    out.push('- Make no changes beyond what these notes call for.');
    out.push('');
    out.push('---');
    out.push('');
    targets().forEach(function(el){
      if (!notes[el.id]) return;
      var k = kindOf(el), plain = el.dataset.plain || '';
      var where = el.dataset.path || '';
      if (k === 'cell' && el.dataset.col) where = (where ? where + ' › ' : '') + el.dataset.col;
      out.push('## ' + el.dataset.ref + KINDLABEL[k] + (where ? ' — ' + where : ''));
      out.push('');
      out.push('Current text:');
      out.push('');
      var words = plain.split(/\s+/);
      out.push('> ' + (k === 'block' && words.length > 14
        ? words.slice(0, 14).join(' ') + ' …' : plain));
      out.push('');
      out.push('Note from the author:');
      out.push('');
      out.push(notes[el.id]);
      out.push('');
    });
    // Notes whose passage is no longer in the document — it was rewritten or cut
    // between builds. They are listed rather than dropped: the reviewer wrote
    // them, and only the reviewer can decide they no longer apply.
    if (unplaced.length) {
      out.push('## Notes whose passage was not found');
      out.push('');
      out.push('These were written against text that is no longer in the source — it has been');
      out.push('rewritten or removed since. They are kept here so nothing is lost; each one');
      out.push('needs a human decision about whether it still applies.');
      out.push('');
      unplaced.forEach(function(u){
        out.push('- **' + (u.ref || 'note') + '** — was attached to: '
                 + (u.q ? '"' + u.q.slice(0, 120) + '"' : '(text not recorded)'));
        out.push('  ' + u.t.replace(/\n/g, '\n  '));
        out.push('');
      });
    }
    // Answers to the reviewer questions Claude left in the document, if any.
    // These are the point of the whole feature: they need to reach the export
    // alongside the ordinary notes, since that export is what gets acted on.
    var qb = qblocks();
    if (qb.length) {
      out.push('## Answers to questions asked in this document');
      out.push('');
      qb.forEach(function(box){
        var q = (box.querySelector('.qblk__text').textContent || '').trim();
        var a = (answers[box.dataset.qkey] || '').trim();
        out.push('**Question' + (box.dataset.qanchor ? ' (' + box.dataset.qanchor + ')' : '') + ':** ' + q);
        out.push('');
        out.push('**Answer:** ' + (a || '_(not answered yet)_'));
        out.push('');
      });
      out.push('---');
      out.push('');
    }
    // A restore point. The reviewer already saves this file; making it also a
    // complete snapshot means the review survives losing the browser, the
    // machine, or the document it was made in. Last, and fenced, so it stays out
    // of the way of whoever is reading the notes.
    out.push('---');
    out.push('');
    out.push('<!-- review-notes-data -->');
    out.push('Ignore the block below — it is not part of the review. It is a machine-readable');
    out.push('copy of the notes above, kept as a backup record.');
    out.push('');
    out.push('```review-notes-data');
    out.push(JSON.stringify(payload()));
    out.push('```');
    if (qb.length) {
      out.push('');
      out.push('```review-answers-data');
      out.push(JSON.stringify(answers));
      out.push('```');
    }
    return out.join('\n');
  }

  var dlg = document.getElementById('exportDlg');
  document.getElementById('copyBtn').addEventListener('click', function(){
    document.getElementById('exportBox').value = buildMarkdown(); dlg.showModal();
  });
  document.getElementById('reviewBtn').addEventListener('click', function(){
    document.getElementById('exportBox').value = count() ? buildMarkdown() : 'No review notes yet.';
    dlg.showModal();
  });
  document.getElementById('dlgClose').addEventListener('click', function(){ dlg.close(); });
  document.getElementById('dlgCopy').addEventListener('click', function(){
    var box = document.getElementById('exportBox');
    box.select(); box.setSelectionRange(0, box.value.length);
    var ok = false;
    try { ok = document.execCommand('copy'); } catch(e) { ok = false; }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(box.value).then(function(){
        dlg.close(); say('Copied ' + count() + ' review notes to the clipboard.');
      }, function(){
        say(ok ? 'Copied.' : 'Copy blocked — the text is selected, press Ctrl/Cmd+C.',
            ok ? 'success' : 'warn');
      });
    } else {
      dlg.close();
      say(ok ? 'Copied ' + count() + ' review notes.' : 'Press Ctrl/Cmd+C to copy the selected text.',
          ok ? 'success' : 'warn');
    }
  });
  var cdlg = document.getElementById('clearDlg');
  document.getElementById('clearBtn').addEventListener('click', function(){
    // Deliberately counts only notes, not question answers: "Clear all" is
    // for the reviewer's own markup, and wiping their answers to Claude's
    // questions as a side effect of that button would be a surprise, not a
    // convenience.
    var n = Object.keys(notes).length + unplaced.length;
    cdlg.querySelector('p').textContent =
      'This removes all ' + n + ' note' + (n === 1 ? '' : 's')
      + ' from this browser. Answers to any questions above are left alone. This cannot be undone.';
    cdlg.showModal();
  });
  document.getElementById('clearCancel').addEventListener('click', function(){ cdlg.close(); });
  document.getElementById('clearYes').addEventListener('click', function(){
    notes = {}; quotes = {}; refs = {}; unplaced = [];
    save(); renderUnplaced(); cdlg.close(); say('All review notes cleared.');
  });

  // ── restoring notes ─────────────────────────────────────────────────────
  // The manual "load a notes file" path (file picker + drag/drop) was removed —
  // this reviewer doesn't need it. What's left, restoreFrom, is still load-
  // bearing: it's how offerRecovery() below brings over an earlier pass found
  // in localStorage under a different key.
  function restoreFrom(parsed, whence){
    // Answers restore independently of notes: a file with only answered
    // questions and no notes is still worth restoring, and one with notes but
    // no answers block (an older export, or a build with no questions) should
    // not clobber answers already sitting in this browser.
    var restoredAnswers = 0;
    if (parsed.answers) {
      for (var k in parsed.answers) {
        if (parsed.answers[k] && !answers[k]) { answers[k] = parsed.answers[k]; restoredAnswers++; }
      }
      if (restoredAnswers) { saveAnswers(); loadAnswerBoxes(); }
    }
    var store = parsed.store;
    if (!store || !Object.keys(store.notes || {}).length) {
      if (restoredAnswers) say('Restored ' + restoredAnswers + ' answer' + (restoredAnswers === 1 ? '' : 's')
        + (whence ? ' from ' + whence : '') + '.');
      else say('No review notes found in that file.', 'warn');
      return;
    }
    var r = adopt(store, { keepExisting: true });
    save();
    renderUnplaced();
    var msg = 'Restored ' + r.placed + ' note' + (r.placed === 1 ? '' : 's')
            + (restoredAnswers ? ' and ' + restoredAnswers + ' answer' + (restoredAnswers === 1 ? '' : 's') : '')
            + (whence ? ' from ' + whence : '');
    if (r.moved) msg += ' · ' + r.moved + ' re-attached to moved text';
    if (r.lost)  msg += ' · ' + r.lost + ' could not be placed (kept in the export)';
    say(msg, r.lost ? 'warn' : 'success');
  }

  // An earlier pass on this same document, saved under a different key — which is
  // what a rebuilt document looks like from here. Offered, never merged silently:
  // the reviewer should know where the notes on their screen came from.
  function offerRecovery(){
    if (count()) return;
    var passes = otherPasses();
    if (!passes.length) return;
    var best = passes[0];
    var bar = document.getElementById('recover');
    if (!bar) return;
    document.getElementById('recoverMsg').textContent =
      best.n + ' review note' + (best.n === 1 ? '' : 's') + ' from an earlier version of '
      + 'this document' + (best.saved ? ', saved ' + best.saved.slice(0, 10) : '') + '.';
    bar.hidden = false;
    document.getElementById('recoverYes').addEventListener('click', function(){
      restoreFrom({ store: best.store, answers: null }, 'the earlier version');
      bar.hidden = true;
    });
    document.getElementById('recoverNo').addEventListener('click', function(){ bar.hidden = true; });
  }

  // ── scrollspy ───────────────────────────────────────────────────────────
  // The highlighted entry is the heading that is *currently pinned* — the same
  // one the reader can see stuck at the top. Deriving it from the sticky offset
  // rather than guessing with a viewport band means the sidebar and the sticky
  // bar can never disagree.
  var nav = document.querySelector('.rev-toc');
  var links = nav ? Array.prototype.slice.call(nav.querySelectorAll('a')) : [];
  var heads = links.map(function(a){ return document.getElementById(a.getAttribute('href').slice(1)); });

  // Clicking a left-hand nav entry (a section heading or an inline question)
  // should center its target the same way arrow-key/button navigation does,
  // rather than relying on the browser's default top-aligned anchor jump.
  if (nav) {
    nav.addEventListener('click', function(ev){
      var a = ev.target.closest('a');
      if (!a || !nav.contains(a)) return;
      var href = a.getAttribute('href') || '';
      if (href.charAt(0) !== '#') return;
      var target = document.getElementById(href.slice(1));
      if (!target) return;
      ev.preventDefault();
      setCurrent(target, true, true);
      history.replaceState(null, '', href);
    });
  }

  function stickyTopOf(h){
    var t = parseFloat(getComputedStyle(h).top);
    return isNaN(t) ? 0 : t;
  }
  function spy(){
    if (!links.length) return;
    var curH2 = -1, curH3 = -1;
    for (var i = 0; i < heads.length; i++) {
      var h = heads[i]; if (!h) continue;
      if (h.getBoundingClientRect().top <= stickyTopOf(h) + 2) {
        if (h.tagName === 'H2') { curH2 = i; curH3 = -1; }
        else { curH3 = i; }
      }
    }
    var active = curH3 !== -1 ? [curH2, curH3] : [curH2];
    links.forEach(function(a, i){
      if (active.indexOf(i) !== -1) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    });
    // Keep the active entry visible without scrolling the page itself.
    var lead = links[curH3 !== -1 ? curH3 : curH2];
    if (lead && nav.scrollHeight > nav.clientHeight + 4) {
      var lr = lead.getBoundingClientRect(), nr = nav.getBoundingClientRect();
      if (lr.top < nr.top + 8) nav.scrollTop -= (nr.top + 8 - lr.top);
      else if (lr.bottom > nr.bottom - 8) nav.scrollTop += (lr.bottom - nr.bottom + 8);
    }
  }
  // ── sticky table headers ────────────────────────────────────────────────
  // A pinned thead has to clear whatever heading is already pinned above it.
  // That offset cannot be a constant: the h3 over one table wraps to two lines
  // and the one over the next does not, and focus mode drops the appbar out of
  // the stack entirely. So it is measured per table, from the headings that
  // actually govern that table, and re-measured whenever the stack can change.
  // Layout only — never called from the scroll handler.
  function layoutTableHeads(){
    var wide = window.matchMedia('(min-width:701px)').matches;
    var tables = document.querySelectorAll('.blk--table table');
    for (var i = 0; i < tables.length; i++) {
      var table = tables[i];
      if (!wide) { table.style.removeProperty('--thead-top'); continue; }
      // The nearest enclosing subsection wins; a table with no h3 above it
      // sits directly under the section's h2.
      var sec = table.closest('.sec--3') || table.closest('.sec--2');
      var head = sec && sec.querySelector(':scope > h3, :scope > h2');
      if (!head) { table.style.removeProperty('--thead-top'); continue; }
      var top = stickyTopOf(head) + head.getBoundingClientRect().height;
      table.style.setProperty('--thead-top', Math.round(top) + 'px');
    }
  }

  var ticking = false;
  function onScroll(){
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function(){ ticking = false; spy(); });
  }
  window.addEventListener('resize', layoutTableHeads);
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);

  // ── focus mode ──────────────────────────────────────────────────────────
  var FKEY = KEY + ':focus';
  var fBtn = document.getElementById('focusBtn'), fExit = document.getElementById('focusExit');
  function setFocus(on){
    document.body.classList.toggle('is-focus', on);
    fBtn.setAttribute('aria-pressed', String(on));
    fBtn.textContent = on ? 'Exit focus' : 'Focus';
    fExit.hidden = !on;
    try { localStorage.setItem(FKEY, on ? '1' : '0'); } catch(e) {}
  }
  fBtn.addEventListener('click', function(){
    setFocus(!document.body.classList.contains('is-focus'));
    spy();               // the sticky offset changes with the appbar, so recompute
    layoutTableHeads();  // …and so does every pinned thead below it
  });
  fExit.addEventListener('click', function(){ setFocus(false); fBtn.focus(); });
  try { if (localStorage.getItem(FKEY) === '1') setFocus(true); } catch(e) {}

  // Question boxes borrow the brand's OPPOSITE mode from whatever the page is
  // in right now — that's the whole trick that makes them stand out without
  // an invented colour. build_review.py can only bake in "opposite of the
  // mode this document was BUILT in", though: it has no way to know the
  // reader will flip Dark/Light at runtime. So each box's mode class has to
  // be recomputed live, every time the toggle fires, to stay the opposite of
  // whatever the reader is looking at right now rather than freezing at
  // whatever it was on page load.
  function syncQuestionMode(){
    var r = document.documentElement;
    var ramp = r.classList.contains('love--blue') ? 'love--blue'
             : r.classList.contains('love--red')  ? 'love--red' : null;
    if (!ramp) return;   // no-brand fallback build: nothing to invert
    var opposite = r.classList.contains('love--light') ? 'love--dark' : 'love--light';
    Array.prototype.forEach.call(document.querySelectorAll('.qblk, .toc-question'), function(el){
      el.classList.add('love', ramp);
      el.classList.remove('love--light', 'love--dark');
      el.classList.add(opposite);
    });
  }

  var root = document.documentElement, mb = document.getElementById('modeBtn');
  mb.addEventListener('click', function(){
    var dark = root.classList.toggle('love--dark');
    root.classList.toggle('love--light', !dark);
    mb.textContent = dark ? 'Light' : 'Dark';
    mb.setAttribute('aria-pressed', String(dark));
    syncQuestionMode();
  });

  // Each start-up step runs in its own try/catch. Without this, one bad step —
  // a malformed stored payload from an earlier build, a browser quirk in a
  // feature added later — throws once and silently cancels every step after
  // it in this synchronous block, because an uncaught exception here has
  // nowhere else to go. That is exactly the failure mode that once made both
  // "notes render in the body" and "the questions nav populates" vanish
  // together despite neither one being broken on its own: whichever ran first
  // threw, and the rest of this list never got the chance to run at all.
  // console.error still surfaces the real cause for anyone who opens devtools.
  function safeStep(name, fn){
    try { fn(); } catch(e) { try { console.error('review.js: ' + name + ' failed', e); } catch(e2) {} }
  }

  // Load this document's own saved pass, re-attaching by quotation where the
  // text has moved since it was written.
  safeStep('restore saved notes', function(){
    var mine = readStore(localStorage.getItem(KEY));
    if (mine) {
      var r = adopt(mine, {});
      if (r.moved || r.lost) {
        var m = [];
        if (r.moved) m.push(r.moved + ' re-attached to moved text');
        if (r.lost)  m.push(r.lost + ' could not be placed — kept in the export');
        setTimeout(function(){ say('Notes reloaded · ' + m.join(' · '), r.lost ? 'warn' : ''); }, 400);
      }
    }
  });
  safeStep('offer recovery', offerRecovery);
  safeStep('load answer boxes', loadAnswerBoxes);
  safeStep('render', render);
  safeStep('render unplaced notes', renderUnplaced);
  safeStep('sync question mode', syncQuestionMode);
  safeStep('scrollspy', spy);
  safeStep('layout table heads', layoutTableHeads);
  // Webfonts land after first paint and change heading heights, so measure
  // again once they have.
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(layoutTableHeads).catch(function(){});
  }
  window.addEventListener('beforeunload', function(e){
    if (autoCommit(null)) { /* saved on the way out */ }
  });
})();
