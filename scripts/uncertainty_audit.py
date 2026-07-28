"""Round-2 referee fixes: (a) local-channel depth scan at a low rate where
information survives the added depth, and (b) a hierarchical uncertainty
audit of the headline sign decisions.

(a) At p=0.10 the local channel purifies both codes by depth ~80, so the
    depth-robustness of the local ordering must be checked at a lower rate.
    Runs L=14 localZ at p=0.02 for depths 40/80/160.

(b) The +-1 sigma thermal band is pair-to-pair spread, not an inference on
    the mean difference.  For the headline points (L=14 p=0.10 local and
    collective; L=12 p=0.10 local) this stores the scar trajectory SEM and
    every thermal pair's C_R with its trajectory SEM, then forms a
    hierarchical bootstrap 95% CI of Delta C_R: resample pairs (level 1)
    and perturb each pair and the scar by its trajectory SEM (level 2).

Writes results/uncertainty_audit.json.
"""

import json
import os

import numpy as np

from scarcode import PXPModel, diagonalize, identify_scars, scar_code, thermal_ensemble
from scarcode.monitor import MonitoredPXP, TrajectoryConfig

DT = 0.6
KMAX = 12
SEED = 1
NTRAJ = 250
OUT = os.path.join(os.path.dirname(__file__), "..", "results",
                   "uncertainty_audit.json")


def _setup(L):
    model = PXPModel(L)
    spec = diagonalize(model)
    identify_scars(spec, L=L)
    U = (spec.vectors * np.exp(-1j * spec.energies * DT)) @ spec.vectors.conj().T
    M = sum((-1) ** i * model.z_diagonal(i) for i in range(L))
    s0, s1, (k0, k1) = scar_code(spec)
    therm = thermal_ensemble(spec, (spec.energies[k0], spec.energies[k1]),
                             window=0.5, kmax=KMAX, seed=SEED)
    return model, spec, U, M, s0, s1, therm


def _cr(mon, v0, v1, p, n_steps, ntraj, measure):
    cfg = TrajectoryConfig(p=p, n_steps=n_steps, dt=DT, measure=measure,
                           record_every=4)
    out = mon.coherent_information(v0, v1, cfg, ntraj, SEED)
    return out["C_R"], out["C_R_sem"]


def part_a():
    model, spec, U, M, s0, s1, therm = _setup(14)
    mon = MonitoredPXP(model, dt=DT, U=U)
    rows = []
    for n_steps in (40, 80, 160):
        ntraj = 250 if n_steps <= 80 else 150
        cs, cs_sem = _cr(mon, s0, s1, 0.02, n_steps, ntraj, "localZ")
        tv = [_cr(mon, a, b, 0.02, n_steps, ntraj, "localZ")[0]
              for a, b in therm]
        rows.append(dict(n_steps=n_steps, scar=cs, scar_sem=cs_sem,
                         therm_mean=float(np.mean(tv)),
                         therm_std=float(np.std(tv, ddof=1)),
                         dCR=cs - float(np.mean(tv))))
        print(f"[a] localZ p=0.02 depth={n_steps}: scar={cs:.4f} "
              f"therm={np.mean(tv):.4f}+-{np.std(tv, ddof=1):.4f}")
    return rows


def _boot_ci(scar, scar_sem, pair_crs, pair_sems, nboot=20000, seed=7):
    rng = np.random.default_rng(seed)
    pair_crs = np.asarray(pair_crs)
    pair_sems = np.asarray(pair_sems)
    n = len(pair_crs)
    idx = rng.integers(0, n, size=(nboot, n))
    boots = (pair_crs[idx] + pair_sems[idx] * rng.standard_normal((nboot, n))
             ).mean(axis=1)
    scar_b = scar + scar_sem * rng.standard_normal(nboot)
    d = scar_b - boots
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def part_b():
    out = []
    for L, measure in ((14, "localZ"), (14, "collective"), (12, "localZ")):
        model, spec, U, M, s0, s1, therm = _setup(L)
        mon = MonitoredPXP(model, dt=DT, U=U,
                           collective_op=(M if measure == "collective" else None))
        cs, cs_sem = _cr(mon, s0, s1, 0.10, 40, NTRAJ, measure)
        pair_crs, pair_sems = [], []
        for a, b in therm:
            c, s = _cr(mon, a, b, 0.10, 40, NTRAJ, measure)
            pair_crs.append(c)
            pair_sems.append(s)
        ci = _boot_ci(cs, cs_sem, pair_crs, pair_sems)
        d = cs - float(np.mean(pair_crs))
        out.append(dict(L=L, measure=measure, p=0.10, scar=cs,
                        scar_sem=cs_sem, pair_crs=pair_crs,
                        pair_sems=pair_sems, dCR=d, ci95=ci,
                        excludes_zero=bool(ci[1] < 0 or ci[0] > 0)))
        print(f"[b] L={L} {measure}: dCR={d:+.4f} 95%CI=[{ci[0]:+.4f},"
              f"{ci[1]:+.4f}] excludes0={out[-1]['excludes_zero']}")
    return out


def main():
    data = dict(depth_scan_p002=part_a(), headline_ci=part_b())
    json.dump(data, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
