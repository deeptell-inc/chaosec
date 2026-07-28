"""Referee finding B-1 follow-up: is the Casimir-DFS failure of PXP scars a
property of scarring, or of the hybridization of the two mid-spectrum rungs
the manuscript happened to encode in?

For chiral scar pairs (|+E>, |-E>) at increasing FSA purity
(E = 2.737 baseline, 4.058, 5.343, 6.572, 7.710 at L=14) this script runs
the same monitored comparison as scripts/dfs_rescue.py -- Casimir J^2 and
local-Z monitoring against an energy-matched thermal ensemble -- and records
each pair's Var J^2, logical J^2 leak, FSA weight, and ensemble size.

If the purer pairs still lose under J^2, the refutation is
identification-robust (stronger paper).  If they win, the claim
"no Casimir measurement can be a true DFS for approximate scars" must be
replaced by a hybridization-controlled statement.

Writes results/pure_rung_dfs.json.
"""

import json
import os

import numpy as np

from scarcode import PXPModel, diagonalize, identify_scars, thermal_ensemble
from scarcode.monitor import MonitoredPXP, TrajectoryConfig
from scarcode.su2 import casimir, h_plus


def propagator_from_spectrum(spec, dt):
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T

L = 14
DT = 0.6
NTRAJ = 200
KMAX = 10
SEED = 1
PS = (0.04, 0.08, 0.12)
TARGET_ES = (2.737, 4.058, 5.343, 6.572, 7.710)

OUT = os.path.join(os.path.dirname(__file__), "..", "results",
                   "pure_rung_dfs.json")


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


def main():
    model = PXPModel(L)
    spec = diagonalize(model)
    identify_scars(spec, L=L)
    J2 = casimir(model)
    U = propagator_from_spectrum(spec, DT)
    w_fsa, fsa = fsa_tower(model)

    res = dict(L=L, ntraj=NTRAJ, kmax=KMAX, window=0.5, ps=list(PS), pairs=[])
    for Etgt in TARGET_ES:
        ip = int(np.argmin(np.abs(spec.energies - Etgt)))
        im = int(np.argmin(np.abs(spec.energies + Etgt)))
        Ep, Em = spec.energies[ip], spec.energies[im]
        vp, vm = spec.vectors[:, ip], spec.vectors[:, im]
        f = fsa[:, int(np.argmin(np.abs(w_fsa - Etgt)))]
        weight = float(np.abs(f @ vp) ** 2)
        m1 = vp @ (J2 @ vp)
        var = float(vp @ (J2 @ (J2 @ vp)) - m1 ** 2)
        leak = float(abs(vp @ (J2 @ vm)))
        diff = float(abs(vp @ (J2 @ vp) - vm @ (J2 @ vm)))
        therm = thermal_ensemble(spec, (Em, Ep), window=0.5, kmax=KMAX,
                                 seed=SEED)
        row = dict(E=float(Ep), fsa_weight=weight, var_J2=var,
                   leak_J2=leak, diff_J2=diff, n_therm=len(therm),
                   modes={})
        print(f"E={Ep:+.3f} w={weight:.3f} VarJ2={var:.2f} leak={leak:.3f} "
              f"diff={diff:.3f} n_therm={len(therm)}")
        for mode, kw in (("operator", dict(operator=J2)), ("localZ", {})):
            mon = MonitoredPXP(model, dt=DT, U=U, **kw)
            entry = []
            for p in PS:
                cfg = TrajectoryConfig(p=p, n_steps=40, dt=DT, measure=mode,
                                       record_every=4)
                cs = mon.coherent_information(vp, vm, cfg, NTRAJ, SEED)["C_R"]
                tv = [mon.coherent_information(t0, t1, cfg, NTRAJ, SEED)["C_R"]
                      for t0, t1 in therm]
                entry.append(dict(p=p, scar=cs,
                                  therm_mean=float(np.mean(tv)),
                                  therm_std=float(np.std(tv, ddof=1)),
                                  dCR=cs - float(np.mean(tv))))
                print(f"  {mode} p={p:.2f}: scar={cs:.4f} "
                      f"therm={np.mean(tv):.4f}+-{np.std(tv, ddof=1):.4f}")
            row["modes"][mode] = entry
        res["pairs"].append(row)
        json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
