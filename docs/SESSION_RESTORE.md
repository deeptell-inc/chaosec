# Session Restoration — Thinking Process & State

Purpose: reconstruct *how* this project was reasoned through, the decisions and
dead ends, the gotchas, and exactly where to resume. Pairs with
`RESULTS_SUMMARY.md` (the *what*) and the auto-memory note
`scar-vs-thermal-channel-capacity-mipt` (the running trail).

Repo root: `/Users/deeptell01/Documents/alterego/personal/chaosec/`
(a self-contained **git repo**, branch `main`; the *workspace* root is not git).

---

## 0. Origin

Started as a scoping question (Japanese): *"quantifying chaos as an
error-correction capacity in MIPT — do random-measured scar states protect
information better than thermal states, as quantum channel capacity? Has this
been done?"* The whole project grew from answering that.

## 1. Reasoning arc (chronological)

1. **Literature review.** Confirmed the framework (MIPT⇄QEC⇄coherent info) is
   established; the *specific* scar-vs-thermal comparison under monitoring was a
   genuine gap. Closest prior: Paviglianiti–Silva (monitored PXP scars, PRL
   2025) — had the stage but measured fidelity/entanglement, never channel
   capacity. Decisive tension found: arXiv:2510.26758 (ETH ⇒ approximate QEC)
   suggests *thermal* states are the good codes — i.e., the hypothesis was
   likely **backwards**.
2. **Idea reframing.** Original hope "scar > thermal" was reframed to a
   "noise-model-dependent crossover" — where does each win?
3. **Implementation.** Built `scarcode`: PXP constrained basis, monitored
   trajectory engine (`phi ∈ ℂ^{dim×2}`, reference entropy), scar/thermal
   selection, KL diagnostics. Validated (Fibonacci dim; Z2 revival t≈4.70,
   F≈0.74; `p=0 ⇒ C_R=1`).
4. **First (WRONG) result.** With a *single* thermal pair, local ≈ tie,
   collective → apparent **scar advantage**. Built a whole story (crossover
   phase diagram, block-ℓ axis, mechanism) around it. Even a "confounder check"
   (varying the collective operator) seemed to confirm it.
5. **THE REVERSAL.** User prioritized *ensemble-averaging the thermal baseline*
   "because it affects robustness." It **overturned the headline**: the single
   thermal pair was a 0th-percentile outlier; the typical thermal code wins.
   Everything was re-derived; figures moved to `results/superseded/`.
6. **Mechanism.** First proposed "protection ∝ measurement-basis participation"
   (weak Spearman +0.41). A later Bhattacharyya test showed diagonal overlap
   *doesn't* predict `C_R` (scar is high-overlap yet fragile) → corrected to the
   **two-channel criterion** (variance / leak). This is the honest, defensible
   mechanism.
7. **DFS rescue.** Built the emergent-su(2) Casimir `J²` for PXP; the nominal
   DFS still fails (variance 32.5). Predicted: an *exact*-su(2) model would flip
   it.
8. **Second model.** Implemented spin-1 Schecter–Iadecola (exact scars). `J²`
   variance = 0 exactly ⇒ Casimir DFS **succeeds** (`C_R=1`), confirming
   variance is the control parameter. But honest nuance (found via L=8 +
   high-stat L=6): under *local* measurement exact scars are merely
   *comparable*, not beaten — so the strict refutation is a *generic-measurement*
   statement.
9. **Reviewer pass (as Nature referee).** Scored novelty 4 / data-qty 5 /
   data-qual 6 / story 5 / logic 6 → reject Nature, fits PRX Quantum. Fixes:
   title +"generic"; two-channel criterion; sub-extensive capacity; spin-1
   parameter robustness; honest framing.
10. **Extensive code.** Generalized the engine to k-qubit codes; the maximal
    `⌊log₂(L+1)⌋`-qubit scar code loses too (local & collective; comparable
    under J²). Answers the "single-qubit only" critique.
11. **Packaging.** Wrote pyproject/LICENSE/tests/CLI/README; verified install,
    demo, tests, build, twine; git-committed.

## 2. Key decisions & rationale

- **Reference coherent information `C_R = <S_R>_traj`** as the capacity proxy
  (single encoded qubit; Gullans–Huse purification style). Extended to k qubits
  via `S_R ∈ [0,k]`, density `S_R/k`.
- **Energy-matched codes** (same two eigen-energies) to kill the energy
  confound; **ensemble** thermal baseline (non-negotiable, see §1.5).
- **Two models** on purpose: PXP (approximate scars, the paradigm) + spin-1
  (exact scars, isolates the variance mechanism as a falsifiable prediction).
- **Honesty over narrative:** every time data contradicted a claim (the
  reversal; spin-1 local; Bhattacharyya), the *claim* was changed, not the data.

## 3. Gotchas / non-obvious facts (read before touching code)

- **PXP has an exponentially large `E=0` zero-mode manifold** (8/13/21 modes at
  L=10/12/14). Scar/thermal codes must be built from **positive-energy rungs**
  (`|E|>0.8`), else eigenstate selection is ill-defined.
- **The scar "tower" via top-Z2-overlap includes contaminants** near E≈±1.4,
  ±2.7; the true tower is the equally-spaced ladder E≈0,±1.33,±2.66,±4.0. Use
  `identify_scars` + positive rungs.
- **Ensemble baseline is load-bearing.** A single `thermal_code` pair is biased
  toward atypical low-`C_R` near-scar states → inverts the sign. Always
  `thermal_ensemble`.
- **DFS needs eigenstates, not just equal mean + zero leak.** Nonzero variance
  ⇒ measurement still resolves the code. This is *the* subtlety.
- **spin-1 `S^+` convention:** raising maps lower→higher index (lower-triangular
  in basis m=−1,0,+1). Getting this backwards makes `Q⁺|Ω>=0` (tower size 1).
- **su(2) normalization (spin-1):** `J⁺=Q⁺/2, J^z=Sz_tot/2` gives the proper
  Casimir `= J(J+1)`; the naive `Jz=[Q⁺,Q⁻]/2` does **not**.
- **Apple Accelerate BLAS** prints benign `RuntimeWarning: ... in matmul`;
  results are correct. Guarded in `casimir` via `np.errstate`; pytest filters
  them. Linux/OpenBLAS won't show them.
- **`scripts/spin1_dfs.py` prints a misleading one-line VERDICT** (checks only
  the last p); trust the full table.
- **Background jobs buffer stdout when piped through `tail`** — you won't see
  partial output; watch for the output JSON file instead.

## 4. Current state (as of last session)

- Paper: `paper/{main,supplement,cover_letter}.{tex,pdf}` all compile clean
  (revtex4-2 `prxquantum`). Main 5 pp, 7 figs, 34 refs, 0 undefined cites.
- Package: `scarcode` 0.1.0 installs, tests 11/11, builds, twine PASSED, git
  committed (2 commits, clean tree). `dist/` has sdist+wheel.
- Figures/data in `results/` (superseded ones archived in `results/superseded/`).

## 5. How to resume

```bash
cd /Users/deeptell01/Documents/alterego/personal/chaosec
pip install -e ".[dev]"     # or use the existing install
scarcode-demo               # 5-point self-check
pytest                      # 11 tests
# reproduce any figure:
python scripts/ensemble_scaling.py   # main refutation
python scripts/spin1_dfs.py          # second model
python scripts/extensive.py --measure collective
# recompile paper:
cd paper && export PATH="/Library/TeX/texbin:$PATH"
pdflatex main; bibtex main; pdflatex main; pdflatex main
```

## 6. TODO (prioritized)

1. **Submit prep:** insert acknowledgments/funding; real Zenodo DOI (paper +
   README bibtex); referee institutional emails in cover letter.
2. **Upload:** verify PyPI name `scarcode` is free (else rename in
   `pyproject.toml`); `gh repo create` + push; `twine upload dist/*`.
3. **Optional robustness (likely reviewer asks):** extensive comparison at more
   sizes / collective+J² at L≠14; PXP periodic BCs; larger thermal ensembles.
4. **If rejected from PRX Quantum:** reformat for Quantum / SciPost Physics →
   PRResearch (fallback PRB).

## 7. Map: modules ↔ scripts ↔ figures

- `pxp.py` (basis+H), `states.py` (selection, ensembles, entropies),
  `diagnostics.py` (KL), `monitor.py` (trajectories; single- & multi-qubit),
  `su2.py` (PXP Casimir), `spin1.py` (exact-scar model), `cli.py` (demo).
- `ensemble_scaling.py`→`ensemble_scaling.png`;
  `corrected_crossover.py`→`corrected_crossover.png`;
  `mechanism.py`→`mechanism.png`; `bhattacharyya.py`→`bhattacharyya.png`;
  `phase_diagram.py`→`phase_diagram_L14.png`;
  `gamma_mapping.py`→`gamma_mapping.png`;
  `dfs_rescue.py` + `spin1_dfs.py`→`spin1_rescue.png`;
  `extensive.py` + `plot_extensive.py`→`extensive.png`.
