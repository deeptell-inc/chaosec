"""Data supplements demanded by the Nature-style panel (2026-07-28).

--part a  Binning controls for the coarse-grained-Casimir rescue (P3):
          does the pure-rung rescue survive when the outcome bins are
          (i) five equal-width bins over the spectral range, or the
          j(j+1) bins shifted by (ii) +1.0 and (iii) -1.0?
--part b  Low-rate size scan (P4): the p=0.10 headline sits in the nearly
          purified regime for the local channel.  Reruns the L-scan at
          p=0.02, where most of the information survives, L=10..16
          (+ L=18 with the reduced ensemble of L18_check).
--part c  Multi-seed audit of the marginal L=12 local point and the L=14
          headline points (P6): pools 5 trajectory seeds and reports the
          seed-level spread alongside the hierarchical CI.

Writes results/nature_panel_fixes.json (merging parts).
"""

import argparse
import json
import os

import numpy as np

from scarcode import PXPModel, diagonalize, identify_scars, scar_code, thermal_ensemble
from scarcode.monitor import MonitoredPXP, TrajectoryConfig
from scarcode.su2 import casimir, h_plus

DT = 0.6
OUT = os.path.join(os.path.dirname(__file__), "..", "results",
                   "nature_panel_fixes.json")


def propagator(spec, dt):
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T


def fsa_tower(model):
    z2 = model.neel_state()
    Hp = h_plus(model)
    basis, v = [z2], z2
    for _ in range(model.L):
        v = Hp @ v
        for b in basis:
            v = v - (b @ v) * b
        n = np.linalg.norm(v)
        if n < 1e-10:
            break
        basis.append(v / n)
        v = basis[-1]
    B = np.array(basis).T
    h = B.T @ (model.hamiltonian() @ B)
    w, u = np.linalg.eigh(h)
    return w, B @ u


def clean_pool(spec, fsa_nearest, target, window):
    return sorted(
        [k for k in range(len(spec.energies))
         if abs(spec.energies[k] - target) < window
         and not spec.scar_mask[k] and k not in fsa_nearest
         and spec.z2_overlap[k] < 0.02 and abs(spec.energies[k]) > 0.3],
        key=lambda k: abs(spec.energies[k] - target))


def cr(mon, v0, v1, p, ntraj, measure, seed, n_steps=40):
    cfg = TrajectoryConfig(p=p, n_steps=n_steps, dt=DT, measure=measure,
                           record_every=4)
    return mon.coherent_information(v0, v1, cfg, ntraj, seed)["C_R"]


def part_a():
    L, ntraj, kpairs, seed = 14, 200, 10, 1
    model = PXPModel(L)
    spec = diagonalize(model)
    identify_scars(spec, L=L)
    J2 = casimir(model)
    U = propagator(spec, DT)
    _, fsa = fsa_tower(model)
    fsa_nearest = {int(np.argmax(np.abs(spec.vectors.T @ fsa[:, r]) ** 2))
                   for r in range(fsa.shape[1])}
    wO = np.sort(np.linalg.eigvalsh(J2))
    lo, hi = wO[0], wO[-1]
    js = np.arange(0, 8)
    jt = (js * (js + 1)).astype(float)

    def labels_from_edges(edges):
        return np.searchsorted(edges, wO)

    schemes = {
        "equal5": labels_from_edges(np.linspace(lo, hi, 6)[1:-1]),
        "jj_plus1": np.array([int(np.argmin(np.abs(jt + 1.0 - x)))
                              for x in wO]),
        "jj_minus1": np.array([int(np.argmin(np.abs(jt - 1.0 - x)))
                               for x in wO]),
    }
    res = {}
    for tag, lab in schemes.items():
        mon = MonitoredPXP(model, dt=DT, U=U, operator=J2)
        mon.op_labels = lab
        res[tag] = []
        for Etgt in (2.737, 5.343, 6.572):
            ip = int(np.argmin(np.abs(spec.energies - Etgt)))
            im = int(np.argmin(np.abs(spec.energies + Etgt)))
            rng = np.random.default_rng(seed)
            pa = clean_pool(spec, fsa_nearest, -Etgt, 0.5)
            pb = clean_pool(spec, fsa_nearest, +Etgt, 0.5)
            rng.shuffle(pa)
            rng.shuffle(pb)
            pairs = list(zip(pa[:kpairs], pb[:kpairs]))
            row = dict(E=Etgt, entries=[])
            for p in (0.04, 0.08, 0.12):
                cs = cr(mon, spec.vectors[:, ip], spec.vectors[:, im], p,
                        ntraj, "operator", seed)
                tv = [cr(mon, spec.vectors[:, a], spec.vectors[:, b], p,
                         ntraj, "operator", seed) for a, b in pairs]
                row["entries"].append(dict(p=p, dCR=cs - float(np.mean(tv)),
                                           scar=cs,
                                           therm_mean=float(np.mean(tv))))
                print(f"[a] {tag} E={Etgt} p={p:.2f}: "
                      f"dCR={row['entries'][-1]['dCR']:+.4f}")
            res[tag].append(row)
    return res


def part_b():
    res = []
    for L, kmax, ntraj in ((10, 12, 200), (12, 12, 200), (14, 12, 200),
                           (16, 12, 200), (18, 6, 120)):
        model = PXPModel(L)
        spec = diagonalize(model)
        identify_scars(spec, L=L)
        U = propagator(spec, DT)
        M = sum((-1) ** i * model.z_diagonal(i) for i in range(L))
        s0, s1, (k0, k1) = scar_code(spec)
        therm = thermal_ensemble(spec, (spec.energies[k0], spec.energies[k1]),
                                 window=0.5, kmax=kmax, seed=1)
        row = dict(L=L, p=0.02, kmax=kmax, ntraj=ntraj)
        for meas, op in (("localZ", None), ("collective", M)):
            mon = MonitoredPXP(model, dt=DT, U=U, collective_op=op)
            cs = cr(mon, s0, s1, 0.02, ntraj, meas, 10)
            tv = [cr(mon, a, b, 0.02, ntraj, meas, 10) for a, b in therm]
            row[meas] = dict(scar=cs, therm_mean=float(np.mean(tv)),
                             therm_std=float(np.std(tv, ddof=1)),
                             dCR=cs - float(np.mean(tv)))
            print(f"[b] L={L} {meas}: scar={cs:.4f} "
                  f"therm={np.mean(tv):.4f}+-{np.std(tv, ddof=1):.4f}")
        res.append(row)
        _dump({"lowrate_scaling": res})
    return res


def part_c():
    seeds = (1, 2, 3, 5, 10)
    res = []
    for L, meas in ((12, "localZ"), (14, "localZ"), (14, "collective")):
        model = PXPModel(L)
        spec = diagonalize(model)
        identify_scars(spec, L=L)
        U = propagator(spec, DT)
        M = sum((-1) ** i * model.z_diagonal(i) for i in range(L))
        s0, s1, (k0, k1) = scar_code(spec)
        therm = thermal_ensemble(spec, (spec.energies[k0], spec.energies[k1]),
                                 window=0.5, kmax=12, seed=1)
        mon = MonitoredPXP(model, dt=DT, U=U,
                           collective_op=(M if meas == "collective" else None))
        per_seed = []
        for sd in seeds:
            cs = cr(mon, s0, s1, 0.10, 250, meas, sd)
            tv = [cr(mon, a, b, 0.10, 250, meas, sd) for a, b in therm]
            per_seed.append(dict(seed=sd, dCR=cs - float(np.mean(tv)),
                                 scar=cs, therm_mean=float(np.mean(tv))))
            print(f"[c] L={L} {meas} seed={sd}: "
                  f"dCR={per_seed[-1]['dCR']:+.4f}")
        d = [r["dCR"] for r in per_seed]
        res.append(dict(L=L, measure=meas, p=0.10, per_seed=per_seed,
                        pooled_dCR=float(np.mean(d)),
                        seed_sd=float(np.std(d, ddof=1)),
                        all_negative=bool(max(d) < 0)))
        _dump({"multiseed": res})
    return res


def _dump(update):
    data = {}
    if os.path.exists(OUT):
        data = json.load(open(OUT))
    data.update(update)
    json.dump(data, open(OUT, "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=["a", "b", "c"])
    args = ap.parse_args()
    if args.part == "a":
        _dump({"binning_controls": part_a()})
    elif args.part == "b":
        _dump({"lowrate_scaling": part_b()})
    else:
        _dump({"multiseed": part_c()})
    print("wrote", OUT)


if __name__ == "__main__":
    main()
