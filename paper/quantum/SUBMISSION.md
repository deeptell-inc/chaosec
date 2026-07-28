# Quantum (quantum-journal.org) submission — handoff checklist

Status: **ready to submit** (all artifacts built 2026-07-27, 0 LaTeX errors).
History: PRX Quantum desk rejection 2026-07-27 (selectivity, no technical
criticism); transferred content unchanged, reformatted to `quantumarticle`.

## What is in this directory

| file | purpose |
|---|---|
| `main.tex` / `main.pdf` | Manuscript, quantumarticle class, 11 pp. Supplement is merged as Appendices A–I (Quantum has no length limit and prefers self-contained papers). |
| `cover_letter.tex` / `.pdf` | Cover letter addressed to the Editors of Quantum (2 pp, 8 suggested referees). |
| `arxiv/` + `arxiv-v1.tar.gz` + `arxiv-v1.zip` | Self-contained arXiv source bundle (main.tex + main.bbl + 9 figures = 11 files, flat, no directory). Both archives hold the same 11 files and are each verified to compile standalone with pdflatex; upload either one. |
| `abstract.txt` | Plain-text abstract for the arXiv/Scholastica abstract field, **1850 characters** (arXiv's hard limit is 1920). Paste this file rather than re-flattening the LaTeX. |
| `../refs.bib` | Shared bibliography — now with a `doi` field on **all 34 entries** (Quantum requires DOI-hyperlinked references; `quantum.bst` renders them). |

## Step 1 — arXiv (REQUIRED first; Quantum only accepts arXiv submissions)

1. Upload `arxiv-v1.tar.gz` (or `arxiv-v1.zip`) at https://arxiv.org/submit
   - **Do not zip the `arxiv/` folder from the Finder.** That produces a
     nested `arxiv/` directory plus `__MACOSX/._*` AppleDouble entries, and it
     sweeps in `main.pdf` and the `.aux/.log/.out/.blg` files. arXiv rejects a
     source package that also contains the compiled PDF, and the stray `.aux`
     confuses AutoTeX. Use the prepared archives, which are flat and clean.
   - Primary category: `quant-ph`; suggested cross-lists: `cond-mat.stat-mech`, `cond-mat.str-el`
   - License: the arXiv default non-exclusive license is sufficient (Quantum
     publishes the journal version CC BY 4.0 on top of the arXiv posting).
   - `\pdfoutput=1` is already in the preamble as arXiv requires; the `.bbl`
     is included so arXiv does not need to run BibTeX.
2. In the metadata form, paste `abstract.txt` into the abstract field (1850
   characters — arXiv rejects anything over 1920).
3. Wait for the announcement and note the arXiv ID (e.g. `2607.XXXXX`).

## Step 2 — Quantum (Scholastica)

1. Submit at https://quantum-journal.scholasticahq.com (link from
   https://quantum-journal.org/instructions/) by entering the **arXiv ID** —
   Quantum pulls the paper from arXiv; no PDF upload of the manuscript needed.
2. Paste the abstract (use `abstract.txt`), attach `cover_letter.pdf`, and enter
   the suggested referees from the cover letter.
3. Declarations to reuse: no funding; both authors conceived the study, H.W.
   did everything else (already stated in the manuscript back matter);
   data/code at doi:10.5281/zenodo.21642056 + github.com/deeptell-inc/chaosec.
4. Note: Quantum charges a publication fee only on acceptance; fee waivers can
   be requested during submission, no justification required.

## If revising before submission

Edit `main.tex`, then from this directory:

```bash
/Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex
/Library/TeX/texbin/bibtex main
/Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex
/Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex
```

then refresh the arXiv bundle: copy `main.bbl` into `arxiv/`, regenerate
`arxiv/main.tex` (strip `\graphicspath`, point `\bibliography` at `refs`), and
re-tar. If the abstract changed, regenerate `abstract.txt` and re-check the
1920-character limit.

Two traps worth remembering:

- **Never run `bibtex` inside `arxiv/`.** There is no `refs.bib` there, so it
  overwrites the shipped `main.bbl` with a 3-line stub and every citation goes
  undefined. Only `pdflatex` runs in that directory.
- **Archive the bundle with an explicit file list**, not `--exclude='*.pdf'` —
  five of the nine figures are PDFs and a blanket exclude silently drops them.
  The bundle must contain exactly 11 files, flat. The zip form is
  `zip -j -X arxiv-v1.zip arxiv/main.tex arxiv/main.bbl arxiv/*.pdf arxiv/*.png`
  minus `main.pdf`; `-j` flattens and `-X` drops the macOS extra attributes.

Class quirk: `\pdfoutput=1` must sit AFTER `\documentclass` and before the first
`\usepackage` (the class deliberately resets it to 0 and checks).
