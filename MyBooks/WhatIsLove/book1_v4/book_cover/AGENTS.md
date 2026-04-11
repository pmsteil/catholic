# AGENTS.md

This folder contains book cover concept development assets for **What Is Love?**. It is a focused design workspace for cover ideation, prompt drafting, print-spec planning, and SVG-based concept generation.

## Purpose

Use this folder to:
- define and refine the theological and visual direction of the cover
- preserve creative briefs, print specs, and marketing copy
- prototype cover art concepts in Python/SVG
- compare alternate sacred cover directions before final production
- maintain a clear separation between **cover development** and the main manuscript

This is a **book-cover workspace**, not the main writing/editing folder for the manuscript.

## Current Direction

The folder now shows a stronger convergence toward a **front-cover crucifix / Eucharistic host / altar / covenant-arch concept** with supporting back-cover copy and print production specs.

The emerging preferred direction appears to be:
- **baroque / reverent / sacred-book aesthetic**
- **maroon dried-blood background** with subtle tone-on-tone ornamental pattern
- **gold linework and typography**
- **central crucifix**
- **semi-transparent Eucharistic host behind the crossbar**
- **grouped three-part rays** symbolizing Truth, Justice, and Mercy flowing together
- **stone altar + chalice beneath the crucifix**
- **three-strand arch/pillars** symbolizing covenant / Church / the binding of Truth, Justice, and Mercy

## What’s In This Folder

### Core design and concept documents
- `book-cover-design-prompt.md`
  - Earlier main design brief
  - Establishes tone, audience, typography, imagery options, palette, production notes, and back cover copy
  - Good high-level orientation document

- `book-cover-design-prompt-textual-architecture.md`
  - Concept manifesto for a **text-built sacred image**
  - Explores cathedral / cross / sacred heart / rose-window compositions made from theological words
  - Important if revisiting the “cover as theological diagram” direction

- `book-cover-word-palette.md`
  - Canonical theological vocabulary bank for text-generated art
  - Organized by virtues, pillars, sacraments, liturgy, commandments, Scripture, CCC language, and Latin
  - Primary source material for the SVG generators

- `cover-image-prompt.md`
  - Earlier layered prompt for a simpler 2D Catholic cover
  - Uses maroon background, host, crucifix, segmented rays, and title treatment
  - Useful as a transitional concept between a simple AI cover and the more developed final spec

### New specification / production files
- `_book_cover_design_spec.md`
  - **Most important current file for production direction**
  - Defines trim size, page count, spine width, bleed, final spread dimensions, typography, palette, front-cover imagery hierarchy, and updated back-cover content
  - Includes the updated final image brief and strongest statement of current design intent
  - Treat this as the **active source of truth** unless superseded

- `_book-cover-back-blurb.md`
  - Standalone back-cover blurb text
  - Use this as the working copy source for back-cover layout, editing, and revision
  - Mirrors the newer, more urgent/apologetic marketing framing

### Python SVG generators
These scripts generate concept art programmatically using `svgwrite`.

- `generate_cathedral_cover.py`
  - First cathedral/textual-architecture implementation
  - Maps theological word zones into a Gothic cathedral composition

- `generate_cathedral_cover_v2.py`
  - More advanced cathedral version
  - Text conforms more tightly to architectural geometry and curves

- `generate_cathedral_cover_v3.py`
  - Most art-forward cathedral iteration
  - Text becomes visual mass rather than readable architectural annotation

- `generate_cross_rays_cover.py`
  - Cross-centered concept with radiating theological beams
  - Closer in spirit to the newer “grouped rays from Christ outward” direction
  - Strong conceptual bridge between symbolic clarity and theological meaning

- `generate_crucifix_cover.py`
  - Crucifix-centered text-built concept
  - Most aligned with the current sacred focal-image direction
  - Best candidate to adapt if continuing toward the updated front-cover spec in code

## Folder Analysis

This folder currently contains **four layers of cover development**:

1. **General creative briefs**
   - broad visual/theological exploration
   - includes traditional and symbolic Catholic cover approaches

2. **Textual architecture exploration**
   - ambitious cathedral / sacred diagram concept
   - intellectually rich, visually distinctive, but more complex and less immediate

3. **Symbolic sacred focal-image experiments**
   - cross, rays, crucifix
   - stronger readability at thumbnail and print-market scale

4. **Production-oriented final direction**
   - explicit print specs
   - updated back blurb
   - clarified front-cover hierarchy
   - strongest evidence of the intended final cover system

## Recommended File Priority

When working in this folder, use this order:

1. `_book_cover_design_spec.md`
   - current source of truth for trim, bleed, spine, typography, palette, and front/back cover requirements
2. `_book-cover-back-blurb.md`
   - current working back-cover copy
3. `book-cover-design-prompt.md`
   - broader design rationale and earlier framing
4. `book-cover-word-palette.md`
   - theological source text for any text-built design system
5. `cover-image-prompt.md`
   - useful for simplified image-generation direction
6. Python generators
   - only after the concept lane is confirmed

## Working Guidance

### If the goal is final cover production
Favor the files with leading underscores:
- `_book_cover_design_spec.md`
- `_book-cover-back-blurb.md`

These appear to represent the most current practical direction.

### If the goal is concept exploration
Use:
- `book-cover-design-prompt-textual-architecture.md`
- `book-cover-word-palette.md`
- the `generate_*` Python scripts

### If generating a new image prompt
Base it primarily on:
- `_book_cover_design_spec.md`
- then borrow wording from `cover-image-prompt.md`
- and only use the word palette if intentionally pursuing text-constructed imagery

## Guidance for Future Edits

- Preserve the theological seriousness and Catholic visual identity
- Keep the cover reverent, weighty, and print-friendly
- Avoid modern self-help aesthetics
- Prefer classical serif typography and disciplined composition
- Treat the crucifix as the unmistakable focal point if following the current final spec
- Keep supporting symbols subordinate:
  - host
  - rays
  - altar and chalice
  - covenant arch / pillars
- Maintain consistency with the book’s core claim:
  - *God’s Perfect Love is the sacred, sacrificial gift of covenant, binding truth, justice, and mercy into life-giving communion.*

## Practical Notes

- Current printer target: **BookPrintOnDemand.com**
- Current print spec from the design spec:
  - trim: 6" × 9"
  - page count: 334
  - spine: ~0.93"
  - full spread with bleed: ~13.43" × 9.5"
- The Python scripts currently output concept assets to Patrick’s desktop designer output folder
- The scripts appear to be concept generators, not full wrap-cover production tools

## Suggested Next Step

If continuing development here, create one additional file:
- `README-cover-workflow.md`

It should record:
- which brief is current
- which back-cover copy is approved
- whether the active direction is:
  - AI-generated painted cover
  - SVG symbolic cover
  - full wrap cover layout
- how to generate previews
- where final export assets should be saved

## Active Recommendation

If choosing one script to evolve toward the new final spec, start with:
- `generate_crucifix_cover.py`

If choosing one file as the authoritative brief, start with:
- `_book_cover_design_spec.md`
