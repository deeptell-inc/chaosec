# scarcode

**Do quantum many-body scars protect quantum information better than thermal
states under measurement? No.**

`scarcode` computes the reference-qubit **coherent information** of a logical
qubit encoded in the PXP **scar** subspace versus an energy-matched **thermal**
subspace under monitored (measurement-induced) dynamics, and finds that chaotic
thermal codes protect information *better* than scar codes under every generic
measurement — a quantitative refutation of scar-enhanced information protection.
It ships the exactly-solvable spin-1 second model that isolates the mechanism
(the emergent-su(2) Casimir variance).

This is the reproduction package for the manuscript *"Chaotic states outperform
quantum many-body scars as codes under generic measurement"* (Wakaura &
Tanimae).

## Installation

```bash
pip install scarcode            # from PyPI
# or, from a clone:
pip install -e ".[dev]"         # editable, with test + plotting extras
```

Requires Python ≥ 3.9, NumPy, and SciPy (`matplotlib` only for the plotting
scripts).

## Quick start

Confirm the install with the built-in self-check:

```bash
scarcode-demo
```
```
[1] PXP L=12: dim=377  (Fibonacci F(14)=377)  OK
[2] Z2 revival: t=4.71  fidelity=0.743  OK
[3] monitored p=0: C_R=1.0000  OK
[4] local monitoring p=0.06: C_R(scar)=0.351  C_R(thermal)=0.485  -> thermal wins
[5] spin-1 L=4: tower size=5  J^2 mean=6.000 std=1.1e-15  OK
```

Programmatic use:

```python
import numpy as np
from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      thermal_ensemble, MonitoredPXP, TrajectoryConfig)

m = PXPModel(14)                       # constrained (Rydberg-blockade) chain
spec = diagonalize(m)
identify_scars(spec, L=14)
s0, s1, (k0, k1) = scar_code(spec)     # a scar code (two tower rungs)
therm = thermal_ensemble(spec, (spec.energies[k0], spec.energies[k1]), kmax=12)

mon = MonitoredPXP(m, dt=0.6)
cfg = TrajectoryConfig(p=0.10, n_steps=40, dt=0.6, measure="localZ")
c_scar = mon.coherent_information(s0, s1, cfg, n_traj=200)["C_R"]
c_therm = np.mean([mon.coherent_information(a, b, cfg, 200)["C_R"] for a, b in therm])
print(c_scar, c_therm)                 # thermal >= scar
```

Measurement models: `measure="localZ"` (per-site), `"collective"` (a global
diagonal operator via `collective_op=`), `"block"` (support size `block_size`),
`"operator"` (any Hermitian `operator=`, e.g. the su(2) Casimir), `"sites"`
(per-site for arbitrary local dimension, e.g. spin-1 `S^z`).

## Package layout

```
scarcode/
  pxp.py          # constrained Fibonacci basis + PXP Hamiltonian
  states.py       # scar/thermal eigenstate selection, ensembles, entropies
  diagnostics.py  # static Knill-Laflamme violation
  monitor.py      # monitored trajectories; single- and multi-qubit coherent info
  su2.py          # emergent-su(2) generator H+ and Casimir J^2 (PXP)
  spin1.py        # spin-1 Schecter-Iadecola model with EXACT su(2) scars
  cli.py          # `scarcode-demo` self-check
scripts/          # paper-reproduction drivers (see below)
tests/            # pytest suite (physics benchmarks)
paper/            # manuscript, supplement, cover letter (LaTeX)
```

## Reproducing the paper

Each figure has a driver in `scripts/` (outputs to `results/`):

| script | result |
|---|---|
| `ensemble_scaling.py` | main refutation: ΔC_R < 0 at all L, both channels |
| `corrected_crossover.py` | C_R(p): scar below the thermal-ensemble band |
| `mechanism.py` | leak / participation channels controlling C_R |
| `phase_diagram.py` | ΔC_R(p, ℓ) vs measurement support size |
| `gamma_mapping.py` | calibration to the γ_c of arXiv:2503.22618 |
| `dfs_rescue.py` | Casimir DFS rescue fails for approximate PXP scars |
| `spin1_dfs.py` | exact spin-1 scars: Casimir rescue succeeds |
| `extensive.py` | maximal k-qubit scar code vs thermal (`--measure`) |

```bash
python scripts/ensemble_scaling.py     # etc. (no PYTHONPATH needed once installed)
```

## Testing

```bash
pytest
```

The suite locks in the Fibonacci dimension, the Z2 revival, the `p=0 ⇒ C_R=1`
sanity, the high-`p` purification, the thermal-beats-scar comparison, and the
exactness / zero Casimir variance of the spin-1 scar tower.

> **Note (Apple Silicon):** the Accelerate BLAS may print benign
> `RuntimeWarning: ... in matmul` during dense matrix products; results are
> unaffected (all tests pass). Other platforms (OpenBLAS/MKL) do not show these.

## Key result

Under every **generic** measurement (local, collective, block-support), and for
codes from one logical qubit up to the maximal `⌊log₂(L+1)⌋`-qubit scar code,
the thermal code protects information at least as well as — and usually much
better than — the scar code, at sizes up to `L=18`. The scar's emergent-su(2)
generator supplies a logical leak that dephases it, and its Casimir carries an
irreducible variance; only in an exactly-solvable spin-1 model (zero Casimir
variance) does a fine-tuned Casimir measurement protect the scar, isolating that
variance as the control parameter.

## Citation

```bibtex
@article{WakauraTanimae2026scarcode,
  title  = {Chaotic states outperform quantum many-body scars as codes under
            generic measurement: a refutation of scar-enhanced information protection},
  author = {Wakaura, Hikaru and Tanimae, Taiki},
  year   = {2026}
}
```

## License

MIT — see [LICENSE](LICENSE).
