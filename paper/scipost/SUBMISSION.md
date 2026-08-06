# SciPost Physics submission — handoff checklist

Status: **ready** (2026-07-31). History: PRX Quantum desk reject 07-27, PRB
desk reject 07-31 — both selectivity templates, no technical criticism. User
chose SciPost Physics.

No new manuscript build is needed: SciPost submits **by arXiv ID**, and the
existing bundle `../quantum/arxiv-v1.tar.gz` (quantumarticle, 15 pp,
clean-room verified) is the manuscript. SciPost's own LaTeX class is only
required at production after acceptance — do not convert now.

## Steps (all user-side)

1. **arXiv first** (if not already posted): upload `../quantum/arxiv-v1.tar.gz`
   per `../quantum/SUBMISSION.md` (quant-ph primary; abstract from
   `../quantum/abstract.txt`, 1,899 chars). Wait for the announcement.
2. **SciPost account**: log in at https://scipost.org (ORCID login supported;
   the submitting author needs a Contributor account).
3. **Submit**: https://scipost.org/submissions/submit_manuscript — enter the
   arXiv identifier **with version** (e.g. `2508.XXXXXv1`), journal =
   SciPost Physics.
4. Paste the blocks from `submission_text.md` into the matching form fields
   (acceptance-criteria justification is REQUIRED; SciPost takes text fields,
   not a cover-letter PDF).
5. Referee suggestions: optional; list in `submission_text.md`.

Notes:
- Open peer review: reports and author replies are published. No APC ever.
- If rerouted to SciPost Physics Core: still refereed, still free —
  recommended to accept rather than restart elsewhere.
- On acceptance, production will ask for the SciPost template; convert then
  (the quantumarticle→revtex conversion notes in `../prb/SUBMISSION.md` show
  which commands are class-specific).
