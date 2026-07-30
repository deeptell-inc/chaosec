# Results Summary — Scars vs Thermal Codes under Monitoring

**Project:** Do quantum many-body scars protect quantum information better than
thermal states under measurement?
**Answer:** No — chaotic (thermal) states are the better codes under every
generic measurement. A refutation, with the mechanism pinned down.
**Authors:** Hikaru Wakaura, Taiki Tanimae (QIRI, Tokyo).
**Target venue:** PRX Quantum.

---

## 1. The question and the framework

- **Setup.** Encode a logical qubit in a 2-dim code `{|0_L>,|1_L>}` maximally
  entangled with a reference `R`, evolve the system under **monitored PXP
  dynamics** (alternating `e^{-iH·dt}` with random projective measurement), and
  track the **reference coherent information** `C_R = <S_R>_traj ∈ [0,1]`
  (`C_R→1` recoverable, `C_R→0` lost).
- **Comparison.** Scar code (PXP tower eigenstates) vs **energy-matched thermal
  code**, at the same two eigen-energies to remove the energy confound.
- **Established backdrop.** MIPT ⇄ QEC ⇄ channel capacity (Choi–Bao–Qi–Altman;
  Gullans–Huse; Fan et al.); ETH ⇒ approximate QEC (Brandão et al.; Bao–Cheng;
  arXiv:2510.26758). The novelty is the direct scar-vs-thermal coding comparison.

## 2. Headline result — the hypothesis is refuted

Under **every generic measurement tested**, the thermal code protects
information at least as well as, and usually much better than, the scar code:

| Measurement | ΔC_R = C_R(scar) − C_R(thermal), L=14, p=0.10 |
|---|---|
| local `Z` | ≈ −0.03 … −0.06 |
| collective (staggered `M`) | ≈ **−0.25 … −0.32** |
| block support `ℓ` (1→L) | negative throughout |

- **Finite-size:** ΔC_R < 0 for **all L = 10, 12, 14, 16, 18**; roughly size-
  independent (collective ~ −0.30 at L=18). Not a finite-size artifact.
- **Figures:** `ensemble_scaling.png`, `corrected_crossover.png`,
  `phase_diagram_L14.png`.

## 3. The critical methodological finding (self-correction)

An early version showed a **spurious scar advantage** under collective
measurement. Cause: the thermal baseline was a **single** eigenstate nearest the
scar-rung energy — systematically an atypical near-scar, low-`C_R` outlier
(0th percentile of the ensemble; `C_R=0.53` vs ensemble mean `0.87`).
**Ensemble-averaging over ~12–20 thermal pairs reverses the sign** and is
essential to the conclusion. **Lesson: never baseline against a single
eigenstate.**

## 4. Mechanism — a two-channel criterion

A projective measurement of operator `O` leaves the logical qubit untouched iff
the code is an `O`-eigenspace with one shared eigenvalue. A measurement
**resolves** (dephases) the code through either:

1. **(i) eigenvalue distinguishability** — differing `O`-expectation or nonzero
   `O`-variance ⇒ different outcome distributions `P_0, P_1`;
2. **(ii) non-invariance** — `<0_L|O|1_L> ≠ 0` coherently mixes the logical
   states.

- The PXP scar realizes **both**: under `M` (the emergent su(2) generator) the
  leak `|<0_L|M|1_L>| = 1.73` (channel ii); under the Casimir `J²` a large
  variance (channel i). Thermal codes realize neither.
- **A diagonal-only measure fails:** the Bhattacharyya overlap `BC(P_0,P_1)`
  does *not* predict `C_R` (Spearman +0.39; the scar has high `BC=0.96` yet low
  `C_R` — its fragility is off-diagonal). Both channels are required; no single
  scalar predicts protection. (`bhattacharyya.png`)
- **Figure:** `mechanism.png`.

## 5. The DFS "rescue" — fails for PXP, succeeds only for exact scars

- **PXP (approximate scars):** the chiral-symmetric pair `(|+E>,|−E>)` has equal
  `<J²>` and zero leak — a *nominal* DFS — yet **still loses** under `J²`
  monitoring (ΔC_R = −0.18,−0.13,−0.09). Reason: equal mean + zero leak are
  **not sufficient**; a true DFS needs the code states to be `O`-eigenstates
  (zero variance). PXP scars carry `Var J² ≈ 32.5`.
- **Second model — spin-1 Schecter–Iadecola (exact su(2) scars):** the tower
  `|S_n>=(Q⁺)ⁿ|Ω>` is an exact multiplet; `J²` is **exactly constant on the
  tower, variance ~1e-13**. There the Casimir *is* a true DFS and the scar is
  **perfectly protected** under `J²` (`C_R=1.000`, ΔC_R = +0.6…+0.8), for
  L=6,8 and parameters `(h,D)=(0.5,0.3),(1.0,0.1),(1.5,0.0)`.
- **But even exact scars gain nothing generically:** under local `S^z` the
  exact-scar and thermal codes are **comparable** (`|ΔC_R| ≲ 0.1`).
- **Interpretation:** the Casimir variance — not scarring itself — is the
  control parameter. Scar structure helps *only* under a fine-tuned, non-local
  Casimir probe matched to an exact algebra. **Figure:** `spin1_rescue.png`.

## 6. Extensive (many-logical-qubit) code

The scar tower is only `(L+1)`-dimensional ⇒ it hosts at most
`k = ⌊log₂(L+1)⌋` logical qubits (**sub-extensive**). Even that **maximal**
`k`-qubit scar code loses to a same-dimension thermal code:

| L (k) | Δ(S_R/k), local, p=0.02/0.04/0.08 |
|---|---|
| 10 (3) | −0.168, −0.121, −0.035 |
| 14 (3) | −0.172, −0.139, −0.063 |
| 18 (4) | −0.242, −0.192, −0.045 |

Under collective `M` the gap is even larger (−0.32…−0.43 at L=14); under the
fine-tuned `J²` the two are comparable (+0.02…+0.03) — the same exception.
**Figure:** `extensive.png`; details in Supplement Table.

## 7. Literature calibration

Reproducing the monitored-Néel entanglement transition and mapping the per-step
rate via `γ = p/dt` gives `γ_c ≈ 0.083` (`p_c ≈ 0.05`), same order as the
`γ_c ≈ 0.013` of Paviglianiti–Silva (PRL 2025); the ~6× factor matches the
projective-per-step vs continuous-weak protocol difference. **Figure:**
`gamma_mapping.png`.

## 8. One-line thesis

> Under any generic measurement, information protection is set by a code's
> spread in the measurement basis (scrambling), not its athermality; PXP scars
> lose everywhere, exact scars gain only under a fine-tuned Casimir DFS, and the
> Casimir *variance* is the single control parameter. This realizes the
> ETH ⇒ approximate-QEC correspondence operationally in monitored circuits.

## 9. Deliverables (all compile / pass)

- **Manuscript** `paper/main.tex` → `main.pdf` (5 pp, revtex4-2 `prxquantum`),
  7 figures, 34 refs, 0 undefined citations.
- **Supplement** `paper/supplement.tex` → `supplement.pdf` (~3 pp, 8 sections).
- **Cover letter** `paper/cover_letter.tex` → `cover_letter.pdf` (PRX Quantum,
  3-paragraph appeal + 8 recommended referees).
- **Python package** `scarcode` 0.1.0: `pip install -e .`, `scarcode-demo`,
  `pytest` (11/11), `python -m build` (sdist+wheel, `twine check` PASSED).
- **Git repo** initialized (branch `main`, clean tree).

## 10. Open / optional items

- Extensive comparison currently local+collective+J² at L=14 only (single-qubit
  and spin-1 fuller).
- PXP periodic boundary conditions not checked.
- Larger thermal ensembles everywhere would tighten error bars.
- Paper needs: acknowledgments/funding, real Zenodo DOI, referee emails.
- Verify PyPI name `scarcode` is free before upload.

---

# UPDATE 2026-07-27/28 — venue pivot, three adversarial panels, retitle

The sections above describe the 2026-07-10 state (PRX Quantum target, "scrambling
not athermality" framing). Everything below supersedes where it conflicts.

## 11. Venue: PRX Quantum → Quantum

PRX Quantum desk-rejected 2026-07-27 (selectivity only, no technical criticism).
New venue: **Quantum (quantum-journal.org)**, arXiv-first (Scholastica takes an
arXiv ID). Canonical manuscript is now **`paper/quantum/main.tex`**
(quantumarticle, 15 pp, supplement merged as Appendices A–I). The legacy PRX
pair `paper/main.tex` + `supplement.tex` is **frozen pre-panel** and no longer
maintained. Bundles: `paper/quantum/arxiv-v1.tar.gz` and `.zip` (12 files,
clean-room verified 15 pp / 0 errors). `paper/quantum/abstract.txt` = paste-ready
plain abstract, 1,899 chars (arXiv limit 1,920; do NOT paste from main.tex —
its comment lines push it over the limit).

## 12. What three rounds of adversarial review changed (ledger X1, R1–R23)

Panels: Codex CLI + Claude Opus, independent, all findings verified by
reproduction before fixing. claims-ledger.md is the authoritative record.

**Survived everything (now CI-backed):**
- The canonical (adjacent-rung) PXP scar code loses to the energy-matched
  thermal ensemble under **every generic measurement**: local, collective,
  block sums across the whole (p,ℓ) grid. Hierarchical bootstrap 95% CIs
  exclude zero at all headline points, incl. the marginal L=12 local point;
  a 5-seed audit finds every seed negative.
- NEW, stronger: at p=0.02 (where info survives) the local deficit **grows
  with size**: −0.16 → −0.38 for L=10→18 (Fig. 2 now two panels).
- Depth-robust where information survives added depth (p=0.02: −0.14/−0.15/−0.13
  at depths 40/80/160); C_R is disclosed as a fixed-depth estimator (last 2 of
  10 records, t∈[21.6,24]), not an asymptotic capacity.

**Corrected / retracted:**
- "Irreducible Casimir variance" (R1): Var J² is a **hybridization** diagnostic
  (47.6→0.89 along the FSA tower); canonical rungs are the *most* hybridized.
- "Deficit tracks the excess variance" (R11): fine-J² has an effectively
  nondegenerate spectrum → destroys ANY 2-dim chiral code; scar C_R was
  rung-independent to 13 digits; the apparent trend was thermal-side noise.
- "Multiplet-binned Casimir rescues purer rungs" (R22): bin-geometry artifact —
  shifting j(j+1) boundaries by ±1 flips all outcomes. Retracted.
- γ_c "volume-to-area crossing" (R5): not resolved at our sizes (density falls
  monotonically with L at every p). Now order-of-magnitude only.
- spin-1 "changes sign as p grows" (R4): L=8 rerun with 20 pairs stays positive
  (+0.20/+0.10/+0.08); exact scars' local low-rate advantage is **open at scale**.
- Phase diagram "deepens with ℓ": non-monotone (even-ℓ milder). Fixed.

**New results the panels forced into existence:**
- **Purity scan (the new headline mechanism)**: under local Z, ΔC_R rises
  monotonically with FSA weight, crossing to a scar **advantage** near w≈0.65
  (−0.069→+0.099 at p=0.04, z≈7 at the purest rung). Athermality is not the
  liability — hybridization is. New Fig. `purity_trend.pdf` + section.
- **Fine-J² on the adjacent-rung code**: scar WINS (+0.19/+0.15/+0.13, CIs
  exclude zero) — the su(2)-adapted probe fails to resolve the scar code
  (BC=0.958, small leak), exactly as the two-channel criterion predicts.

## 13. New title and thesis

> **Algebraic leak and thermal hybridization, not athermality, defeat quantum
> many-body scar codes under generic measurement**

Two structural liabilities: (i) the emergent su(2) order parameter's logical
leak (collective fragility, tower-wide); (ii) hybridization with the thermal
bulk (local/Casimir degradation, maximal exactly at the experimentally
accessed rungs). The spin-1 exact-scar model anchors the zero-variance limit.
Nature-style scoring (Codex 6.5/6.0/6.0/7.0/5.5, Opus 5/6/6/5/4): specialist
journal appropriate; Nature-tier blocked by lack of interventional causality.

## 14. Infrastructure completed since §9

- **Zenodo**: metadata of 21336840 corrected via new `zenodo-deposit
  --edit-record`; **v0.1.1 published** = the citable DOI
  **10.5281/zenodo.21642056** (v0.1.0 archive couldn't reproduce the
  manuscript — 5 cited scripts missing). Concept DOI 10.5281/zenodo.21336839.
- **PyPI**: `scarcode` name free; dist/ rebuilt from current source,
  twine-checked, fresh-venv verified. Upload still needs user creds.
- Numbered section/subsection headings throughout (was run-in \paragraph's).
- New audit scripts: `fsa_purity_audit.py`, `pure_rung_dfs.py`,
  `pure_rung_dfs2.py`, `referee_audit.py`, `uncertainty_audit.py`,
  `l16_partner_check.py`, `nature_panel_fixes.py`, `plot_purity_trend.py`,
  `energy_window_robustness.py`.

## 15. Remaining user actions

1. arXiv: upload `arxiv-v1.tar.gz` (or `.zip`); abstract from `abstract.txt`
   (in clipboard, 1,899 chars). quant-ph primary; cross-list
   cond-mat.stat-mech, cond-mat.str-el.
2. Scholastica: submit with the arXiv ID (see `paper/quantum/SUBMISSION.md`).
3. Optional: `twine upload dist/*`; decide whether to keep the new title.
