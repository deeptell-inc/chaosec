"""Referee-audit computations for the adversarial-panel revision (2026-07-28).

Three independent checks, each answering one Round-1 referee finding:

(a) depth-scan     -- C_R is estimated at a fixed circuit depth (40 steps,
                      last-quarter time average).  Does the scar deficit
                      persist when the depth is doubled and quadrupled, or
                      is the fixed-depth comparison an artifact of the
                      estimator?  (Referee A, finding 1)
(b) best-pair scan -- the single-qubit scar code uses the two canonical
                      positive rungs.  Does ANY pair of positive-energy
                      tower rungs beat the thermal ensemble mean, i.e. is
                      the deficit an artifact of the pair choice?
                      (Referee A, finding 3)
(c) extensive-sel  -- the maximal 2^k code selects tower states by Z2
                      overlap, which at L=14 admits one E~0 tower state.
                      Rerun with the |E|>0.8 filter of Appendix A: does
                      excluding the zero-mode change the verdict?
                      (Referee A, finding 3)

Usage: python scripts/referee_audit.py [--part a|b|c|all]
Writes results/referee_audit.json (merging parts as they complete).
"""

import argparse
import itertools
import json
import os

import numpy as np

from scarcode import PXPModel, diagonalize, identify_scars, scar_code, thermal_ensemble
from scarcode.monitor import MonitoredPXP, TrajectoryConfig

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "referee_audit.json")

L = 14
DT = 0.6
P = 0.10
SEED = 1
KMAX = 12


def _setup(L):
    model = PXPModel(L)
    spec = diagonalize(model)
    identify_scars(spec, L=L)
    U = (spec.vectors * np.exp(-1j * spec.energies * DT)) @ spec.vectors.conj().T
    M = sum((-1) ** i * model.z_diagonal(i) for i in range(L))
    return model, spec, U, M


def _run_code(mon, v0, v1, p, n_steps, ntraj, measure, seed):
    cfg = TrajectoryConfig(p=p, n_steps=n_steps, dt=DT, measure=measure,
                           record_every=4)
    out = mon.coherent_information(v0, v1, cfg, ntraj, seed)
    return out["C_R"], out["C_R_sem"]


def part_a():
    """Depth scan: scar vs thermal ensemble at n_steps = 40, 80, 160."""
    model, spec, U, M = _setup(L)
    s0, s1, (ks0, ks1) = scar_code(spec)
    Ea, Eb = spec.energies[ks0], spec.energies[ks1]
    therm = thermal_ensemble(spec, (Ea, Eb), window=0.5, kmax=KMAX, seed=SEED)
    res = {}
    for measure, op in (("localZ", None), ("collective", M)):
        mon = MonitoredPXP(model, dt=DT, U=U, collective_op=op)
        res[measure] = []
        for n_steps in (40, 80, 160):
            ntraj = 250 if n_steps <= 80 else 150
            cs, cs_sem = _run_code(mon, s0, s1, P, n_steps, ntraj, measure, SEED)
            tvals = [
                _run_code(mon, t0, t1, P, n_steps, ntraj, measure, SEED)[0]
                for t0, t1 in therm
            ]
            res[measure].append(dict(
                n_steps=n_steps, t_final=n_steps * DT,
                scar=cs, scar_sem=cs_sem,
                therm_mean=float(np.mean(tvals)),
                therm_std=float(np.std(tvals, ddof=1)),
                n_pairs=len(tvals),
                dCR=cs - float(np.mean(tvals)),
            ))
            print(f"[a] {measure} n={n_steps}: scar={cs:.4f} "
                  f"therm={np.mean(tvals):.4f}+-{np.std(tvals, ddof=1):.4f}")
    return res


def part_b():
    """Every pair of positive-energy tower rungs vs the thermal ensemble."""
    res = {}
    for Lb in (10, 14):
        model, spec, U, M = _setup(Lb)
        tower = np.where(spec.scar_mask)[0]
        pos = [i for i in tower if spec.energies[i] > 0.8]
        _, _, (ks0, ks1) = scar_code(spec)
        Ea, Eb = spec.energies[ks0], spec.energies[ks1]
        therm = thermal_ensemble(spec, (Ea, Eb), window=0.5, kmax=KMAX,
                                 seed=SEED)
        res[f"L{Lb}"] = {"pos_rung_energies":
                         [float(spec.energies[i]) for i in pos]}
        for measure, op in (("localZ", None), ("collective", M)):
            mon = MonitoredPXP(model, dt=DT, U=U, collective_op=op)
            ntraj = 150
            pairs = []
            for i, j in itertools.combinations(pos, 2):
                c, _ = _run_code(mon, spec.vectors[:, i], spec.vectors[:, j],
                                 P, 40, ntraj, measure, SEED)
                pairs.append(dict(E=(float(spec.energies[i]),
                                     float(spec.energies[j])), C_R=c))
            tvals = [
                _run_code(mon, t0, t1, P, 40, ntraj, measure, SEED)[0]
                for t0, t1 in therm
            ]
            best = max(p["C_R"] for p in pairs)
            res[f"L{Lb}"][measure] = dict(
                pairs=pairs, best_pair=best,
                therm_mean=float(np.mean(tvals)),
                therm_std=float(np.std(tvals, ddof=1)),
                best_minus_therm=best - float(np.mean(tvals)),
            )
            print(f"[b] L={Lb} {measure}: best pair {best:.4f} vs "
                  f"therm {np.mean(tvals):.4f}")
    return res


def part_c():
    """Maximal code with the zero-mode-free (|E|>0.8) tower selection."""
    model, spec, U, _ = _setup(L)
    tower = np.where(spec.scar_mask)[0]
    k = int(np.floor(np.log2(len(tower))))
    m = 2 ** k
    ov = spec.z2_overlap
    default = tower[np.argsort(ov[tower])[::-1][:m]]
    nonzero = np.array([i for i in tower if abs(spec.energies[i]) > 0.8])
    filtered = nonzero[np.argsort(ov[nonzero])[::-1][:m]]
    mon = MonitoredPXP(model, dt=DT, U=U)
    res = {"k": k,
           "default_energies": sorted(float(spec.energies[i]) for i in default),
           "filtered_energies": sorted(float(spec.energies[i]) for i in filtered)}
    for tag, idx in (("default", default), ("filtered", filtered)):
        code = [spec.vectors[:, i] for i in idx]
        vals = []
        for p in (0.02, 0.04, 0.08):
            cfg = TrajectoryConfig(p=p, n_steps=40, dt=DT, measure="localZ",
                                   record_every=4)
            out = mon.coherent_information_code(code, cfg, 150, SEED)
            vals.append(dict(p=p, density=out["density"]))
        res[tag] = vals
        print(f"[c] {tag}: " + "  ".join(
            f"p={v['p']:.2f} S_R/k={v['density']:.4f}" for v in vals))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="all", choices=["a", "b", "c", "all"])
    args = ap.parse_args()
    data = {}
    if os.path.exists(OUT):
        data = json.load(open(OUT))
    if args.part in ("a", "all"):
        data["depth_scan"] = part_a()
    if args.part in ("b", "all"):
        data["best_pair"] = part_b()
    if args.part in ("c", "all"):
        data["extensive_selection"] = part_c()
    json.dump(data, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
