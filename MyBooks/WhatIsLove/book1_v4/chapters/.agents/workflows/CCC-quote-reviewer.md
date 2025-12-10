# **CCC: Review accuracy of quoted CCC paragraphs**

## Task
Verify **every** Catechism of the Catholic Church (CCC) quote in the text against the official Vatican source. Each citation must be checked word-for-word.

## Verification Process

### Step 1: Extract All CCC References
Scan the chapter and list every CCC reference that is:
- Directly quoted (in quotation marks)
- Paraphrased with a paragraph number citation
- Referenced by paragraph number (e.g., CCC 1234)

### Step 2: Verify Each Citation
For each CCC reference, use these **reliable sources** (in order of preference):
1. `http://www.scborromeo.org/ccc/para/[PARAGRAPH].htm` — St. Charles Borromeo (quick lookup)

**Quick Reference URL Format:**
- CCC 1 - `http://scborromeo.org/ccc/para/1.htm`
- CCC 2055 - `http://scborromeo.org/ccc/para/2055.htm`
- CCC 1823-1826 (range) - Check each paragraph individually

**Verification steps:**
1. Copy the exact quoted text from the chapter
2. Look up the paragraph at the source
3. Compare word-for-word
4. Mark as ✅ Verified or ❌ Needs Correction

### Step 3: Output Results

#### If ALL citations verify correctly:
```
## CCC Verification: ✅✅✅ PASSED
All [X] Catechism citations in this chapter have been verified against official sources.
```

#### ONLY WHEN ANY citations need correction, create this table:

```markdown
## CCC Verification: ❌ CORRECTIONS NEEDED

| # | Reference | Text in Chapter | Correct CCC Text | Issue | Source Link |
|---|-----------|-----------------|------------------|-------|-------------|
| 1 | CCC 1823 | "Charity is the theological virtue..." | "Charity is the theological virtue by which we love God above all things..." | Truncated quote | [St. Charles Borromeo](https://scborromeo.org/ccc/para/1823.htm) |
| 2 | CCC 2055 | "Jesus summarizes the law" | "When someone asks him, 'Which commandment in the Law is the greatest?'..." | Paraphrase presented as quote | [St. Charles Borromeo](https://scborromeo.org/ccc/para/2055.htm) |
```

**Issue types to flag:**
- **Misquote** — Words changed, added, or removed
- **Wrong paragraph** — Citation points to different content
- **Paraphrase as quote** — Summary presented in quotation marks
- **Non-existent reference** — Paragraph number doesn't exist or is out of range
- **Truncated** — Quote cut off mid-sentence changing meaning
- **Conflated** — Multiple paragraphs merged without indication
- **Edition mismatch** — Text from a different edition or translation

## Additional Checks
*   **Paragraph Range Validity:** CCC paragraphs range from 1-2865; flag any numbers outside this range
*   **Cross-References:** If the CCC itself references other paragraphs (cf. 1234), verify those are accurate if mentioned
*   **Contextual Fidelity:** Flag any CCC passages used out of context or selectively quoted to change meaning

## Common CCC Sections Reference
- **Part One** (The Profession of Faith): CCC 1-1065
- **Part Two** (The Celebration): CCC 1066-1690
- **Part Three** (Life in Christ): CCC 1691-2557
- **Part Four** (Christian Prayer): CCC 2558-2865

## Notes
- The CCC has been published in multiple languages; always verify against the official English translation
- Do not allow references to the Compendium of the CCC—these use different numbering and should be clearly distinguished
- Footnotes in the CCC are part of the official text and may be quoted
- Partial quotes are NOT acceptable.
- In-brief summaries (e.g., CCC 1831 summarizes 1822-1829) should be cited as the summary paragraph, not the range
