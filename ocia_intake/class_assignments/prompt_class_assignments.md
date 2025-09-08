# OCIA Table Assignment — Master Prompt (Reusable, 2025+)

**Goal:** Assign participants to **5 tables** so that:

1. seat those with the **highest Attending Probability** first,
2. **balance Sex** (Male/Female **only**),
3. **balance Baptized vs Not Baptized**,
4. then balance **Age Range**,
5. then **Present Religious Affiliation**.

> This prompt is reusable in future years. For **2025**, apply the defaults under **Quick Settings for This Year**.

---

## Quick Settings for This Year (no need to ask)

* **Tables:** `T = 5` (last year was 4; may change in future)
* **Attendance mapping:** `Yes = 1.00`, `Likely = 0.70`, `Not Likely = 0.30`
* **Sex values:** **Every row must be `Male` or `Female`**. If **any** other value or blank is detected, **halt with an error** (do **not** continue).
* **Table size band:** Strictly keep table sizes within **±1 person** (very important)
* **Attendance tier spread (NEW):** **Distribute attendance tiers evenly across tables**: place all `1.00` first (evenly), then `0.70`, then `0.30`. Within each tier, do not allow clustering—use per‑table tier targets and assign round‑robin with fairness scoring as a tiebreaker.
* **Special constraints:** none this year (e.g., no required separations/keep‑together rules)

---

## Input CSV columns (exact or close synonyms accepted)

`Attending Probability, First Name, Last Name, Sex, Age, Email Address, Phone, Have you been baptized?, Present religious affiliation, Current Marital Status, In what denomination were you baptized?`

> **Hard requirement:** The CSV **must** include all columns above (or clear synonyms). If a required column is missing or nonsensical, **halt and warn** (see **0) Preflight**).

---

## 0) Preflight schema & sanity checks (**HARD‑STOP on failure**)

Before any parsing or assignment, run these checks. If **any** fail, output a **Blocking Error Report** (see format below) and **stop**.

1. **Required columns present:** All listed columns (or obvious synonyms) exist.
2. **Sex domain:** Every `Sex` value ∈ {`Male`, `Female`} (no blanks, no other values).
3. **Attending Probability domain:** Each value is one of {`Yes`, `Likely`, `Not Likely`} or a numeric/percent convertible to `[0,1]`.
4. **Baptized question mappable:** `Have you been baptized?` is clearly mappable to `Yes/No/Unknown`.
5. **Age sanity:** If provided, ages are numeric integers in a plausible range `18–120`. (Out‑of‑range or non‑numeric → flag; not a hard stop unless >10% of rows.)
6. **Names present:** `First Name` and `Last Name` present (non‑blank). If >5% missing → hard stop.
7. **Contact key:** At least one contact field present per row (`Email Address` or `Phone`). If >10% missing both → hard stop.
8. **Duplicate detection:** Flag potential duplicates by identical email or phone. Not a hard stop, but must be reported.

**Blocking Error Report (format):**

* Title: `BLOCKING ERRORS — Fix CSV and re‑run`
* Bullet list of each failed check, with **counts**.
* Show up to **5 sample rows** (CSV snippets) per failed category.
* End with: `No assignment performed.`

---

## 1) Parse & normalize

* **Attending Probability (categorical):** Map `Yes→1.00`, `Likely→0.70`, `Not Likely→0.30`. If numeric/percent appears (future years), convert to `[0,1]`. Missing → **median** (fallback `0.50`).
* **Sex:** **Must be `Male` or `Female`. Any other value → HARD‑STOP** (see Preflight). No unknown/other categories are used **ever**.
* **Baptized:** From `Have you been baptized?` map to `Yes`, `No`, else `Unknown`.
* **Age Range buckets:** `18–19`, `20–25`, `26–29`, `30–39`, `40–49`, `50+`. (Out‑of‑range or blank ages: **exclude from targets**, seat evenly; also list under Data quality notes.)
* **Present religious affiliation:** keep literal; blank → `Unknown`.
* **Marital status:** carry through; **do not optimize** on it this year.

---

## 2) Compute global balance targets

Let total participants be `N`, tables `T=5`. Target table sizes must differ by **≤1**.

Compute dataset‑derived ratios for:

* **Sex:** target male/female ratio per table.
* **Baptism:** target Yes/No ratio per table (ignore `Unknown` for targets; distribute `Unknown` evenly).
* **Age:** ratio per age bucket (exclude unknown ages from target; distribute unknowns evenly).
* **Affiliation:** if >6 unique, keep **top 5** by frequency + `Other`.

> These are **soft targets** used by the scoring function below.

---

## 3) Seating order by attendance priority (tiered & balanced)

**MANDATORY tiering rule:**

1. Partition participants into **attendance tiers** using the mapped scores: `1.00`, then `0.70`, then `0.30` (for numeric inputs, snap to the nearest of these three using an epsilon of 0.02).
2. For each tier **in that order**, compute per‑table **tier capacities** by evenly distributing the tier count across `T` tables (first `remainder` tables get `+1`).
3. **Assign within the tier** using a **balanced round‑robin with fairness scoring**:

   * Among tables with remaining tier capacity, choose the one with the **lowest penalty** (see §4), tie‑break by **fewest people**, then **lowest table number**.
   * Do **not** exceed a table’s tier capacity before all tables meet theirs.
4. After all `1.00` are placed, repeat for `0.70`, then `0.30`.

This guarantees even spread of the highest‑probability attendees before filling the next tier.

---

## 4) Greedy assignment with fairness scoring

When evaluating candidate tables **within a tier**, score as below and pick the **lowest total penalty** (ties → fewer people → lowest table #):

**Penalty components (lower is better):**

* **Sex balance (w=4):** absolute deviation from sex target after seating this person.
* **Baptized balance (w=4):** absolute deviation from baptized Yes/No targets after seating this person.
* **Age balance (w=2):** sum of deviations across all age buckets.
* **Affiliation balance (w=1):** deviation for the person’s affiliation bucket.
* **Table size pressure (w=3):** penalty if adding here would push this table toward exceeding its size band sooner than others.
* **Deterministic tie‑break (w=0.001):** stable pseudo‑random via hash(email) × table index; ensures consistent re‑runs.

> **Note:** Attendance tier balance is enforced **outside** the scoring by per‑table tier capacities (see §3).

---

## 5) Local improvement passes (optional but recommended)

Run up to **2 passes** of pairwise swaps **within the same attendance tier** across tables. Make a swap **only if** it reduces the combined **Sex + Baptized** penalties for the two tables and keeps sizes within the ±1 band **and** preserves the tier counts per table. Stop early if no improving swap exists.

---

## 6) Outputs (in this exact order)

### A) Pre‑Assignment Dataset Summary (print first)

Report a **dataset intake snapshot** *before* any assignment:

* **Total participants (N)** found in the CSV
* **Attending Probability** counts: `Yes / Likely / Not Likely` (+ percentages) and the mapping used (`1.00 / 0.70 / 0.30`)
* **Sex** counts and percentages: `Male / Female` **only**
* **Baptized** counts and percentages: `Yes / No / Unknown`
* **Age buckets** counts and percentages: `18–19`, `20–25`, `26–29`, `30–39`, `40–49`, `50+` (note separately how many ages were missing/out‑of‑range)
* **Present religious affiliation**: total distinct categories; list **top 5** by count (+ percentages); group the remainder as `Other` with total count
* **Data quality notes**: duplicates (by email/phone), missing critical fields, out‑of‑range ages. If **any Preflight hard‑stop** was detected, **do not proceed**; emit the **Blocking Error Report** (see 0) and **stop**.

### B) Assignment CSV (input columns preserved, plus `Table`)

```
First Name,Last Name,Sex,Age,Attending Probability,Baptized?,Present religious affiliation,Current Marital Status,In what denomination were you baptized?,Email Address,Phone,Table
```

### C) Table Summary Report (human‑readable)

For **each table (1–5):**

* Total count; **M/F** counts (+%)
* Baptized Yes/No/Unknown (+%)
* **Attendance tier counts:** `1.00 / 0.70 / 0.30`
* Age bucket counts (+%)
* Top affiliations present with counts

**Global diagnostics:**

* Table sizes list (e.g., `10/10/10/9/9`)
* **Max deviation** across tables for **Sex** and for **Baptized** (percentage points)
* **Attendance tier spread:** list per‑table tier counts and flag any deviation from the even targets.
* Notes where perfect balance is mathematically impossible (e.g., skewed Sex or Baptism distribution)

### D) Reconciliation & Validation (print last)

Provide a **Validation Checklist** with explicit PASS/FAIL indicators:

* **Count reconciliation:** `N (dataset)` == `sum of all table counts` → PASS/FAIL
* **Size band:** every table size within **±1** of target sizes → PASS/FAIL (also show the size list)
* **Sex totals:** sum across tables equals dataset totals for `Male` and `Female` → PASS/FAIL
* **Baptized totals:** sum across tables equals dataset totals for `Yes/No/Unknown` → PASS/FAIL
* **Attendance tiers:** per‑table tier counts match the computed tier capacities for `1.00`, `0.70`, `0.30` → PASS/FAIL
* **Age totals:** sum across tables equals dataset totals for all age buckets → PASS/FAIL
* **Affiliation totals:** when using Top‑5+Other bucketing, table totals aggregate to dataset totals for those buckets → PASS/FAIL
* **Unassigned participants:** 0 expected → PASS/FAIL

If **any** check fails: attempt a deterministic, minimal‑change rebalance (re‑run improvement passes **within the affected tier(s)** while preserving the size band). If still failing, clearly mark **MANUAL REVIEW NEEDED** and list the offending tables, categories, and deltas.

Provide a **Validation Checklist** with explicit PASS/FAIL indicators:

* **Count reconciliation:** `N (dataset)` == `sum of all table counts` → PASS/FAIL
* **Size band:** every table size within **±1** of target sizes → PASS/FAIL (also show the size list)
* **Sex totals:** sum across tables equals dataset totals for `Male` and `Female` → PASS/FAIL
* **Baptized totals:** sum across tables equals dataset totals for `Yes/No/Unknown` → PASS/FAIL
* **Age totals:** sum across tables equals dataset totals for all age buckets (plus the number of unknown/out‑of‑range ages if any) → PASS/FAIL
* **Affiliation totals:** when using Top‑5+Other bucketing, table totals aggregate to dataset totals for those buckets → PASS/FAIL
* **Unassigned participants:** 0 expected → PASS/FAIL

If **any** check fails: attempt a deterministic, minimal‑change rebalance (re‑run improvement passes focused on the failing dimension while preserving the size band). If still failing, clearly mark **MANUAL REVIEW NEEDED** and list the offending tables, categories, and deltas.

---

## 7) Edge cases & guardrails

* **Sex:** Never invent or report any category other than `Male` and `Female`. Any other value is a **hard stop**.
* **Unknown values (non‑Sex):** For Baptism `Unknown`, missing/out‑of‑range Age, and rare affiliations: distribute evenly when possible; avoid clustering unless unavoidable.
* **Unavoidable imbalance:** When perfect balance isn’t possible, **minimize maximum deviation** and document in diagnostics.
* **Data quality:** Flag rows missing name/contact, but **still seat them** unless a Preflight hard‑stop threshold is met.

---

## 8) Default weights (tune as priorities change)

* `w_sex = 4`
* `w_baptized = 4`
* `w_age = 2`
* `w_affiliation = 1`
* `w_size = 3`
* `w_jitter = 0.001`

> If priorities change in future years, adjust the weights and/or the attendance mapping above.

---

## One‑Shot Instruction You Can Paste Above a CSV

> **Instruction:** Use the **OCIA Table Assignment — Master Prompt (Reusable, 2025+)** with the **Quick Settings for This Year**. **First, run the Preflight schema & sanity checks (Section 0). If any hard‑stop issue is detected, output the specified *Blocking Error Report* and STOP.** Otherwise, output the **Pre‑Assignment Dataset Summary** (Section 6A), then parse and normalize the CSV. **Assign participants in attendance‑tier order**: place all `1.00` evenly across the 5 tables, then all `0.70` evenly, then all `0.30`, using per‑table tier capacities and the fairness scoring (**§4**) as the tiebreaker within each tier. Keep table sizes within **±1**. After producing the **Assignment CSV** (Section 6B) and the **Table Summary Report** (Section 6C), finish with the **Reconciliation & Validation** checklist (Section 6D), including the **Attendance tiers** check. Do not stall on additional questions; apply the provided settings and proceed.
