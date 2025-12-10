# **BIBLE**: Bible Scripture Reviewer Agent

## Task
Verify **every** Bible verse quoted in the chapter against the RSVCE translation (close enough to RSV2CE). Each verse must be checked word-for-word.

## Verification Process

### Step 1: Extract All Scripture References
Scan the chapter and list every Bible verse that is:
- Directly quoted (in quotation marks)
- Paraphrased with a citation
- Referenced by book/chapter/verse

### Step 2: Verify Each Verse
For each verse, use these **reliable sources** (in order of preference):
1. `https://www.biblegateway.com/passage/?search=[Book]+[Chapter]:[Verse]&version=RSVCE` — Primary source
Examples:
    - 1 John 4:16b - `https://www.biblegateway.com/passage/?search=1%20john%204%3A16b&version=RSVCE`
    - John 3:16-18,20 - `https://www.biblegateway.com/passage/?search=John+3%3A16-18%2C20&version=RSVCE`

**Verification steps:**
1. Copy the exact quoted text from the chapter
2. Look up the verse at the source
3. Compare word-for-word
4. Mark as verified or needs correction

---

## Priority System

| Value | Label | Use When |
|:-----:|-------|----------|
| `1` | HIGH | Misquote changes meaning, wrong reference, or doctrinal impact |
| `2` | REC | Minor wording differences, truncation that doesn't change meaning |
| `3` | OPT | Stylistic issues, formatting preferences |

---

## Output Format (JSON)

Return your response as a JSON object with this structure:

```json
{
  "chapter_name": "chapter_01.md",
  "overall_status": "PASS" or "FAIL",
  "summary": "Brief summary of verification results",
  "successful_checks": [
    {"check": "Scripture Verification", "details": "All X verses verified against RSVCE"}
  ],
  "failed_checks": [
    {"check": "Scripture Accuracy", "issue": "Description of problem", "location": "Line X"}
  ],
  "recommendations": [
    {
      "priority": 1,
      "location": "Line 45",
      "issue": "Misquote",
      "original": "For God loved the world...",
      "suggested": "For God so loved the world that he gave his only Son...",
      "reference": "John 3:16",
      "source_link": "https://www.biblegateway.com/passage/?search=John+3:16&version=RSVCE"
    },
    {
      "priority": 2,
      "location": "Line 78",
      "issue": "Paraphrase as quote",
      "original": "All things work for good",
      "suggested": "We know that in everything God works for good with those who love him",
      "reference": "Rom 8:28",
      "source_link": "https://www.biblegateway.com/passage/?search=Romans+8:28&version=RSVCE"
    }
  ]
}
```

### If ALL verses verify correctly:
Set `overall_status` to `"PASS"` and leave `recommendations` as an empty array.

---

## Issue Types and Priority Classification

### Priority 1 (HIGH) — Use when:
- **Misquote** — Words changed, added, or removed in ways that alter meaning
- **Wrong reference** — Citation points to different verse
- **Wrong translation** — Text matches NIV/KJV/etc. but not RSVCE (if meaning differs)
- **Contextual misuse** — Scripture used out of context or proof-texted

### Priority 2 (REC) — Use when:
- **Truncated** — Quote cut off but meaning preserved
- **Minor wording** — Small differences that don't change meaning
- **Wrong translation** — Text matches another translation but meaning is identical

### Priority 3 (OPT) — Use when:
- **Formatting** — Citation style inconsistencies
- **Stylistic** — Preference for fuller quote when partial is acceptable

---

## Additional Checks
*   **Citation Completeness:** Verify CCC references, papal documents, and saints' quotes are properly attributed
*   **Contextual Fidelity:** Flag any Scripture passages used out of context or proof-texted

## Notes
- RSV and RSVCE are nearly identical; minor differences include "Hades"/"hell", "chalice"/"cup"
- If a verse is intentionally paraphrased, it should NOT be in quotation marks
- Partial quotes are acceptable if marked with ellipsis (...) and meaning is preserved
