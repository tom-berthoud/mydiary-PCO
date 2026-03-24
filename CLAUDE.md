# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lecture notes compilation system for the "Programmation Concurrente" course at HEIG-VD. Weekly markdown notes are parsed, reorganized by theme, and compiled into a single styled PDF.

## Build Commands

```bash
make pdf          # Build the PDF (runs python3 build.py)
make clean        # Remove generated PDF
make new WEEK=XX  # Create a new weekly note template (semaine-XX.md)
```

**Dependencies:** Python 3, pyyaml, pandoc, texlive-xetex, texlive-latex-extra, texlive-lang-french, inkscape (for SVG→PDF)

## Build Pipeline

`build.py` does the following:
1. Scans for `semaine-*.md` files (sorted alphabetically)
2. Extracts sections matching `## [theme_id] Title` using regex
3. Validates theme IDs against `themes.yaml` (warns on unknown tags)
4. Converts SVG images to PDF via inkscape
5. Reorganizes all sections by theme (order from `themes.yaml`), not chronologically
6. Generates a temp markdown with `metadata.yaml` as YAML frontmatter
7. Calls pandoc with XeLaTeX to produce `notes_progconcur.pdf`

## Key Conventions

### Weekly Note Format

```markdown
# Semaine XX — YYYY-MM-DD

## [theme_id] Section Title
Content...

## [another_theme_id] Another Section
Content...
```

- Theme IDs must match an `id` in `themes.yaml` or the section is skipped with a warning
- Lab files use suffix: `semaine-XXlabo.md`
- Assets go in `assets/` with relative paths: `![alt](assets/file.png){width=70%}`

### Diagrams in PDF

Use raw LaTeX TikZ blocks for diagrams that render properly in PDF (not ASCII art):

````markdown
```{=latex}
\begin{center}
\begin{tikzpicture}[...]
  ...
\end{tikzpicture}
\end{center}
```
````

Available TikZ libraries (loaded in `metadata.yaml`): `arrows.meta`, `calc`, `positioning`, `decorations.pathreplacing`

When using TikZ inside a tikzpicture that has global `->` style, override with `-` on non-arrow draws (e.g., brace decorations).

### Configuration Files

- **themes.yaml** — defines theme IDs, titles, and ordering in the final PDF (16 themes)
- **metadata.yaml** — pandoc/LaTeX config: fonts, colors, margins, header/footer, code block styling, TikZ libraries

## CI/CD

GitHub Actions (`.github/workflows/build-pdf.yml`) auto-builds and deploys to GitHub Pages on push to `main`.

## Language

All content, comments, and UI text are in **French**.
