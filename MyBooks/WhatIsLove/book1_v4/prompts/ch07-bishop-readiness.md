Bishop-readiness revision of Chapter 7 ("Justice: God Is Justice") of *What Is Love? God's Perfect Love*. Use the `wil-review-chapter` skill. Same process as Ch. 6, finished 2026-09-24 (memory.html §18, entries 46–58).

HOW I WORK WITH YOU
- Don't hand me a triage to rule on. Go straight to a redline of your best improvements; I approve with "y" or correct you.
- Before every write: dry-run the edits on a scratch copy, confirm every anchor matches exactly once, render a word-level redline (colored text, no white background), send it as an HTML file, and wait for "y".
- No word counts, anywhere.
- After each write: confirm the chapter is identical to the dry-run output, check <sup> numbers against the Notes list, and add a "Completed" card to memory.html §18 right after <h3>Completed</h3>, divs balanced. Next entry number: 59.
- Group related fixes into one redline. On anything doctrinal, give me the reasoning in two or three lines, and correct me plainly when I'm wrong.

FILES AND TOOLS
- Source of truth: chapters/chapter_07.md in book1_v4. The review HTML is disposable.
- Before the first write, back up the chapter and memory.html to archive/ch07-pre-<date>/.
- Redline tools: prompts/redline-tools/ (dry.py, redline.py, tpl.html with %%TITLE%% / %%NOTE%% / %%BODY%%, and an example edits.py). Copy them to a work folder in the VM home (the device's /tmp isn't writable). Each round: write editsN.py as E=[(group, line, old, new)], then
    sed 's/from edits import E/from editsN import E/' dry.py > dryN.py   (same for redline.py)
    python3 dryN.py before.md after.md
    python3 redlineN.py <workdir> before.md chapters/reports/ch07-redlineN-<date>.html tplN.html
  Write step: cmp before.md with the chapter, run dryN.py on the chapter in place, cmp with after.md.
- Review doc, if we build one: key wil-ch07-suggestions-v1, Love Brand.

FORMATTING THAT MUST SURVIVE (baseline 2026-09-24)
- 5 <div class="blockquote"> with 5 \hfill\small attributions; 3 callouts; divs 8/8.
- Footnotes are raw <sup>N</sup> with a hand-built ### Notes list between \footnotesize and \normalsize. Never [^N]. Now sup 1–2 against notes 1–2 (1 = Declaration of Independence / pursuit of happiness; 2 = St. John Paul II, TOB 19:4).
- No Greek or Hebrew script; transliterate.

STANDING RULES
- Verify every factual claim, quotation, and CCC / encyclical / Summa number against two independent sources (vatican.va first). Leave out any detail the sources disagree on.
- Scripture is RSV Catholic Edition, quoted whole: a whole verse or none; otherwise cite with "cf." No "· RSV" tag. Never verify against a downloaded "open" RSV (copyright; todo 28).
- Show the good a reader reached for; never charge a motive. No polemic against Protestants. "Threads" is the book's word.
- A capital He means God only. *Author* is reserved for God. Always "St. John Paul II" (line 139 now says "Pope Saint John Paul II"). Name a saint at the head of a paragraph. "The marital act," never "sex act".
- The canonical definition of love is fixed word for word.
- Ch. 7 follows the four-part pattern for Chs. 6–9; Ch. 6 is the reference implementation.
- Don't reopen rejected items: memory.html "Theological / Structural Rejections", entry 32, the partiality paragraph once proposed for Ch. 7, and the Ch. 5/6 rejections (John 8 as truth-without-mercy, "warring, not the leaving", the abuser line).

KNOWN ITEMS FOR CH. 7
1. Pending verifications: every CCC number in the Decision 5 sub-callouts was stated from memory; Aquinas ST II-II q.81 (religion) and q.99 (sacrilege); section numbers for any Dominus Iesus, Dives in Misericordia, Caritas in Veritate or Evangelium Vitae citation.
2. Settled design to keep: Justice is the deliberate two-sin exception (idolatry toward God, exploitation of the vulnerable toward neighbor). Reconciliation stays a one-paragraph preview; its full treatment is Ch. 8. The Declaration quote stays universal (no country named), and its footnote does not claim Jefferson meant beatitudo. Ch. 6 hands idolatry's full unpacking (Decalogue, CCC 2113, modern idols) to Ch. 7; make sure Ch. 7 carries it without repeating Ch. 6.
3. Todo 40, gratitude. In Ch. 7 it appears only as a listed duty ("Justice Toward God: Worship, obedience, gratitude…") and among Aquinas's parts of justice. My argument: existence is received, so worship is owed, and even the capacity to be grateful was given; a rock cannot be grateful. Help me decide whether it belongs here. Ch. 6 now says "We are alive, and the rock is not"; build on it, don't restate it.
4. The Matt 23:23 opening blockquote: move it to Further Study only if the chapter runs long.
5. Note only (entry 19): four of the five "Justice Toward God Severed" distortions and all three "Justice Toward Neighbor Severed" items have no row in the Ch. 13–14 matrices.
6. Ch. 6 now covers the Church as teacher and living witness, Scripture and Tradition as one deposit (CCC 80, 82, 97), faith as submission of mind and will (CCC 143–144), and "every refusal … extends the wound". Don't duplicate it; cross-reference if needed.
7. Before calling the chapter done: the read-aloud pass, and a check that the Bridge names Ch. 8 and previews mercy.

Start by reading AGENTS.md, memory.html (§6 "Chapter 7 (Justice) Decisions", §16, §18) and the chapter, then send me your first redline.
