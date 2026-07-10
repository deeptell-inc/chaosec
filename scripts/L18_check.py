"""L=18 robustness point for the finite-size scaling (referee response).

Extends the ensemble-averaged Delta C_R = C_R(scar) - <C_R(thermal)> to
L=18 (constrained dim F(20)=6765) at p=0.10 for local-Z and collective
(staggered-Z) monitoring, to show the refutation persists at the largest
accessible size.
"""

from __future__ import annotations

import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      thermal_ensemble)
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def propagator_from_spectrum(spec, dt):
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T


def cr(mon, v0, v1, p, ntraj, measure, nsteps=40, dt=0.6):
    cfg = TrajectoryConfig(p=p, n_steps=nsteps, dt=dt, measure=measure,
                           record_every=4)
    return mon.coherent_information(v0, v1, cfg, ntraj, seed=10)["C_R"]


def main():
    L, dt, p, ntraj, kmax = 18, 0.6, 0.10, 120, 6
    print(f"L={L} building spectrum (dim=F(20)=6765)...", flush=True)
    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    s0, s1, (ks0, ks1) = scar_code(spec)
    Ea, Eb = spec.energies[ks0], spec.energies[ks1]
    therm = thermal_ensemble(spec, (Ea, Eb), window=0.5, kmax=kmax, seed=1)
    U = propagator_from_spectrum(spec, dt)
    stag = sum((-1) ** i * m.z_diagonal(i) for i in range(L))
    print(f"  scar E=({Ea:+.2f},{Eb:+.2f}), {len(therm)} thermal pairs; running...",
          flush=True)

    rows = {}
    for name, coll, meas in [("localZ", None, "localZ"),
                             ("collective", stag, "collective")]:
        mon = MonitoredPXP(m, dt=dt, collective_op=coll, U=U)
        cs = cr(mon, s0, s1, p, ntraj, meas)
        ct = np.array([cr(mon, a, b, p, ntraj, meas) for a, b in therm])
        d = cs - ct.mean()
        rows[name] = dict(CR_scar=float(cs), CR_therm_mean=float(ct.mean()),
                          CR_therm_std=float(ct.std(ddof=1)), dCR=float(d))
        print(f"  [{name:10s}] scar={cs:.3f} therm={ct.mean():.3f}"
              f"±{ct.std(ddof=1):.3f}  dCR={d:+.3f}", flush=True)

    os.makedirs("results", exist_ok=True)
    json.dump(dict(L=L, p=p, ntraj=ntraj, rows=rows),
              open("results/L18_check.json", "w"), indent=2)
    print("saved -> results/L18_check.json", flush=True)


if __name__ == "__main__":
    main()
