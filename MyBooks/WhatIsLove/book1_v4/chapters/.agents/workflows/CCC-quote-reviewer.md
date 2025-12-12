# **CCC**: Review accuracy of quoted CCC paragraphs

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
4. Mark as verified or needs correction

---

## Priority System



| Value | Label | Use When |
|:-----:|-------|----------|
| `1` | HIGH | Misquote changes meaning, wrong paragraph, doctrinal impact, non-existent reference |
| `2` | REC | Minor wording differences, truncation that doesn't change meaning |
| `3` | OPT | Formatting issues, citation style preferences |

---

## Output

Return **only** the JSON object specified by the calling tool. Do not include any prose, markdown, or code fences outside the JSON.

**Status rule:**
- Set `overall_status` to `"PASS"` when `failed_checks` is empty.
- Set `overall_status` to `"FAIL"` when `failed_checks` is non-empty.

**Recommendations:**
- Use priority `1`/`2`/`3` per the priority system.
- Include `reference` and `source_link` for each CCC-related correction.

---

## Issue Types and Priority Classification

### Priority 1 (HIGH) — Use when:
- **Misquote** — Words changed, added, or removed in ways that alter meaning
- **Wrong paragraph** — Citation points to different content
- **Non-existent reference** — Paragraph number doesn't exist or is out of range (1-2865)
- **Contextual misuse** — CCC passage used out of context or selectively quoted to change meaning
- **Conflated** — Multiple paragraphs merged without indication

### Priority 2 (REC) — Use when:
- **Truncated** — Quote cut off but meaning preserved
- **Minor wording** — Small differences that don't change meaning
- **Edition mismatch** — Text from a different edition but meaning is identical

### Priority 3 (OPT) — Use when:
- **Formatting** — Citation style inconsistencies
- **Stylistic** — Preference for fuller quote when partial is acceptable

---

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
