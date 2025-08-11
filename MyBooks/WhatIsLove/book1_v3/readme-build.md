I’ll outline a simple, reliable pipeline you can run locally (one command) and, if you want, the same pipeline in CI so a PDF artifact is produced automatically on each commit.

### What we’ll use
- Pandoc as the converter
- Tectonic as the TeX engine (auto-fetches LaTeX packages; simpler than full MacTeX)

### 1) Install the tools (macOS)
```bash
brew update
brew install pandoc tectonic
```

### 2) Create the file order
Make a `build-chapters-order.txt` in your `chapters` folder that lists files in the exact sequence you want. For example:
```text
0_cover.md
000_forward.md
00_Introduction.md
chapter_01.md
chapter_02.md
chapter_03.md
chapter_04.md
chapter_05.md
chapter_06.md
chapter_07.md
chapter_08.md
chapter_09.md
chapter_10.md
chapter_11.md
chapter_12.md
chapter_13.md
z_appendix_on_the_marriage_covenant.md
z_appendix_on_teaching_the_children.md
y_appendix_definitions.md
```

Note: You currently have `y_appendix_definitions.html`. Convert it once:
```bash
cd /Users/patiman/git/catholic/MyBooks/WhatIsLove/book1_v3/chapters
pandoc y_appendix_definitions.html -f html -t gfm -o y_appendix_definitions.md
```
Then reference the `.md` in `build-chapters-order.txt`.

### 3) Add book metadata and print layout
Create `build-metadata.yaml` in `chapters`:
```yaml
title: What Is Love?
author: Your Name
lang: en-US
documentclass: book
classoption:
  - oneside
geometry:
  - paperwidth=6in
  - paperheight=9in
  - margin=0.8in
  - bindingoffset=0.2in
mainfont: Libertinus Serif
monofont: Latin Modern Mono
colorlinks: true
top-level-division: chapter
header-includes:
  - |
    \usepackage{fancyhdr}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[LE,RO]{What Is Love?}
    \fancyfoot[CE,CO]{\thepage}
```

Tip:
- 6x9" is a common trim for paperbacks. Adjust margins/bindingoffset as you like.
- If your chapters already start with `# Chapter …`, Pandoc will create chapters and start them on new pages automatically with the `book` class.
- Page numbers: enabled by the `fancyhdr` footer (`\fancyfoot[CE,CO]{\thepage}`) in the metadata above; no extra flags needed.

### 4) One-command build script (Python)
Create `bin/build` at `/Users/patiman/git/catholic/MyBooks/WhatIsLove/book1_v3/bin/build` (no extension):
```python
#!/usr/bin/env python3
import os
import subprocess

ROOT_DIR = "/Users/patiman/git/catholic/MyBooks/WhatIsLove/book1_v3"
CHAPTERS_DIR = os.path.join(ROOT_DIR, "chapters")
ORDER_FILE = os.path.join(CHAPTERS_DIR, "build-chapters-order.txt")
METADATA_FILE = os.path.join(CHAPTERS_DIR, "build-metadata.yaml")
OUTPUT_PDF = os.path.join(ROOT_DIR, "WhatIsLove_book.pdf")

def read_ordered_files(order_path: str):
    files = []
    with open(order_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            files.append(os.path.join(CHAPTERS_DIR, line))
    return files

def main():
    files = read_ordered_files(ORDER_FILE)
    cmd = [
        "pandoc",
        "--from=gfm+smart",
        "--toc",
        "--pdf-engine=tectonic",
        f"--metadata-file={METADATA_FILE}",
        "--output", OUTPUT_PDF,
        *files,
    ]
    subprocess.run(cmd, check=True)
    print(f"Built: {OUTPUT_PDF}")

if __name__ == "__main__":
    main()
```

Make it executable and run it:
```bash
chmod +x /Users/patiman/git/catholic/MyBooks/WhatIsLove/book1_v3/bin/build
/Users/patiman/git/catholic/MyBooks/WhatIsLove/book1_v3/bin/build
```

That’s it—your combined PDF will be at:
`/Users/patiman/git/catholic/MyBooks/WhatIsLove/book1_v3/WhatIsLove_book.pdf`

### Notes and options
- Images: keep source images at 300 dpi for print; relative paths work fine.
- Page breaks: using `documentclass: book` and top-level `#` headings per chapter is usually enough. You can insert manual breaks with `\newpage` if needed.
- Fonts: change `mainfont` if you prefer (e.g., `TeX Gyre Pagella`, `EB Garamond` if installed).
- HTML callouts/quotes: if your chapters use your custom HTML templates for blockquotes and callouts [[memory:5585395]], those styles won’t carry into PDF automatically. If you want them styled in PDF, we can add a tiny Pandoc Lua filter to map those `<div class="blockquote">` and `<div class="callout">` blocks into nice LaTeX boxes. Say the word and I’ll drop in that filter.

### Files to create
- `chapters/build-chapters-order.txt`
- `chapters/build-metadata.yaml`
- `bin/build` (Python script)

Status update:
- Drafted a simple, reproducible Pandoc + Tectonic pipeline using a Python runner at `bin/build`, tailored to your `chapters` directory. Included a one-time conversion for your HTML appendix and notes about your custom HTML templates’ behavior in PDF.

- Built pipeline uses: `build-chapters-order.txt` → `pandoc` (with `build-metadata.yaml`) → `WhatIsLove_book.pdf` at the repository root.

- **Deliverables**
  - `chapters/build-chapters-order.txt`: explicit chapter order
  - `chapters/build-metadata.yaml`: title, layout, fonts, page size, headers/footers (page numbers enabled via fancyhdr)
  - `bin/build`: one-command Python build

- **Run**
  - `brew install pandoc tectonic`
  - `/Users/patiman/git/catholic/MyBooks/WhatIsLove/book1_v3/bin/build`

- **Caveats**
  - Convert `y_appendix_definitions.html` to markdown once.
  - If you want your custom HTML blockquote/callout styling in the PDF, I can add a small Pandoc Lua filter to map them cleanly.
