# Physical Review B submission — handoff checklist

Status: **ready to submit** (built 2026-07-30, 0 LaTeX errors, 0 undefined refs).
History: PRX Quantum desk rejection 2026-07-27 (selectivity, no technical
criticism); manuscript since strengthened by three adversarial-panel rounds
(ledger X1, R1–R23) and retitled. User chose PRB over Quantum 2026-07-30.

## What is in this directory

| file | purpose |
|---|---|
| `main.tex` / `main.pdf` | Manuscript, REVTeX 4.2 `[aps,prb,twocolumn]`, 12 pp, appendices A–I included. Converted from the canonical `../quantum/main.tex` (content identical; class-level changes only). |
| `cover_letter.tex` / `.pdf` | Cover letter addressed to the Editors of PRB (2 pp, 8 suggested referees, PRX Quantum history disclosed). |
| `submit/` + `prb-submit.tar.gz` | Self-contained source bundle (main.tex + main.bbl + refs.bib + 10 figures, 13 files). Verified to compile standalone: 12 pp, 0 errors. |

## Conversion notes (quantumarticle → revtex4-2)

- Class: `[aps,prb,twocolumn]{revtex4-2}`; `\pdfoutput=1` kept.
- Abstract moved BEFORE `\maketitle` (REVTeX requirement).
- `\orcid{}` removed (unsupported; enter ORCID in the submission form).
- `\acknowledgments{...}` command → `\begin{acknowledgments}` environment.
- Dropped explicit `natbib`/`nameref` loads (REVTeX brings natbib; nameref was
  a quantumarticle-hook workaround). Added `hyperref` (for `\href`/`\url`).
- `\bibliographystyle{apsrev4-2}`.

## Submission steps

1. Go to https://authors.aps.org/Submissions/ → New Submission → PRB.
   - Either upload `prb-submit.tar.gz` directly, **or** — if the arXiv posting
     from the Quantum flow is already live — submit by arXiv ID (APS pulls the
     source; make sure the arXiv version is the PRB/REVTeX one or expect to
     upload source anyway).
2. Abstract field: paste `../quantum/abstract.txt` (verified identical to this
   manuscript's abstract, 1,899 chars plain).
3. Attach `cover_letter.pdf`; enter the 8 suggested referees from it.
4. Declarations: no funding; author contributions and data availability are in
   the manuscript back matter; data/code at doi:10.5281/zenodo.21642056 +
   github.com/deeptell-inc/chaosec.
5. ORCID 0000-0001-8381-8323 (H.W.) goes in the form, not the .tex.

## If revising before submission

Edit `main.tex`, then from this directory:

```bash
/Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex
/Library/TeX/texbin/bibtex main
/Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex
/Library/TeX/texbin/pdflatex -interaction=nonstopmode main.tex
```

then refresh the bundle: re-copy `main.tex` into `submit/` (strip
`\graphicspath`, point `\bibliography` at `refs`), copy `main.bbl`, re-tar with
the explicit 13-file list. Same traps as the arXiv bundle: never run bibtex in
`submit/` before `refs.bib` is there, and never tar with `--exclude='*.pdf'`
(five figures are PDFs).
