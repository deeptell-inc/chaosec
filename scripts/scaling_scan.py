"""Finite-size scaling of the scar advantage Delta C_R.

For L in a range, at a fixed measurement rate p, compute
    Delta C_R = C_R(scar code) - C_R(thermal code)
under (a) local-Z and (b) collective (staggered-Z) monitoring.

Also includes an *attribution control*: a non-scar low-entanglement code made of
two random constrained-basis product states (S_ent = 0). If this product code
beats thermal as much as the scar code does, the advantage is a generic
low-entanglement effect rather than scar-specific.

Uses the eigendecomposition (already needed to pick states) to build the
propagator U = V diag(e^{-i w dt}) V^dag -- faster and more accurate than expm.
"""

from __future__ import annotations

import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      thermal_code, entanglement_entropy)
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def propagator_from_spectrum(spec, dt: float) -> np.ndarray:
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T


def product_code(model: PXPModel, rng) -> tuple[np.ndarray, np.ndarray]:
    """Two random constrained-basis product states (zero entanglement)."""
    i, j = rng.choice(model.dim, size=2, replace=False)
    v0 = np.zeros(model.dim, dtype=complex); v0[i] = 1.0
    v1 = np.zeros(model.dim, dtype=complex); v1[j] = 1.0
    return v0, v1


def delta_cr(mon, a0, a1, b0, b1, p, ntraj, seed, measure, nsteps=40, dt=0.6):
    cfg = TrajectoryConfig(p=p, n_steps=nsteps, dt=dt, measure=measure,
                           record_every=2)
    ra = mon.coherent_information(a0, a1, cfg, ntraj, seed=seed)
    rb = mon.coherent_information(b0, b1, cfg, ntraj, seed=seed)
    d = ra["C_R"] - rb["C_R"]
    sem = np.hypot(ra["C_R_sem"], rb["C_R_sem"])
    return d, sem, ra["C_R"], rb["C_R"]


def main():
    Ls = [10, 12, 14, 16]
    p = 0.10
    ntraj = 300
    dt = 0.6
    out_rows = []
    print(f"finite-size scaling  p={p} ntraj={ntraj} dt={dt}")
    print(f"{'L':>3} {'S_scar':>7} {'S_therm':>7} | "
          f"{'dCR_local':>10} {'dCR_coll':>10} {'dCR_prod_coll':>13}")
    print("-" * 62)
    for L in Ls:
        m = PXPModel(L)
        spec = diagonalize(m)
        identify_scars(spec, L=L)
        s0, s1, (ks0, ks1) = scar_code(spec)
        Ea, Eb = spec.energies[ks0], spec.energies[ks1]
        t0, t1, _ = thermal_code(spec, (Ea, Eb))
        U = propagator_from_spectrum(spec, dt)
        cut = L // 2
        S_scar = 0.5 * (entanglement_entropy(m, s0, cut)
                        + entanglement_entropy(m, s1, cut))
        S_therm = 0.5 * (entanglement_entropy(m, t0, cut)
                         + entanglement_entropy(m, t1, cut))

        stag = sum((-1) ** i * m.z_diagonal(i) for i in range(L))
        mon_local = MonitoredPXP(m, dt=dt, U=U)
        mon_coll = MonitoredPXP(m, dt=dt, collective_op=stag, U=U)

        d_loc, s_loc, _, _ = delta_cr(mon_local, s0, s1, t0, t1, p, ntraj,
                                      10, "localZ")
        d_col, s_col, _, _ = delta_cr(mon_coll, s0, s1, t0, t1, p, ntraj,
                                      10, "collective")
        # attribution control: product (non-scar, S=0) vs thermal, collective
        rng = np.random.default_rng(3)
        pr0, pr1 = product_code(m, rng)
        d_prod, s_prod, _, _ = delta_cr(mon_coll, pr0, pr1, t0, t1, p, ntraj,
                                        10, "collective")

        out_rows.append(dict(L=L, S_scar=S_scar, S_therm=S_therm,
                             dCR_local=d_loc, dCR_local_sem=s_loc,
                             dCR_coll=d_col, dCR_coll_sem=s_col,
                             dCR_prod_coll=d_prod, dCR_prod_coll_sem=s_prod))
        print(f"{L:>3} {S_scar:7.2f} {S_therm:7.2f} | "
              f"{d_loc:+.3f}±{s_loc:.3f} {d_col:+.3f}±{s_col:.3f} "
              f"{d_prod:+.3f}±{s_prod:.3f}")

    out = "results/scaling.json"
    os.makedirs("results", exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(p=p, ntraj=ntraj, dt=dt, rows=out_rows), f, indent=2)
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
