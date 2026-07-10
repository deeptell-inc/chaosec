"""Finite-size scaling with an ENSEMBLE-averaged thermal baseline.

Replaces the single arbitrary thermal pair by an ensemble of energy-matched
thermal code pairs. Reports C_R(scar) minus the ensemble-mean thermal C_R, with
a band = std over the thermal ensemble (typical-state fluctuations), for local-Z
and collective (staggered-Z) monitoring. Also carries the zero-entanglement
product control.
"""

from __future__ import annotations

import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      thermal_ensemble, participation_entropy,
                      entanglement_entropy)
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def propagator_from_spectrum(spec, dt):
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T


def cr(mon, v0, v1, p, ntraj, measure, seed=10, nsteps=40, dt=0.6):
    cfg = TrajectoryConfig(p=p, n_steps=nsteps, dt=dt, measure=measure,
                           record_every=4)
    return mon.coherent_information(v0, v1, cfg, ntraj, seed=seed)["C_R"]


def main():
    Ls = [10, 12, 14, 16]
    p = 0.10
    ntraj = 200
    dt = 0.6
    kmax = 12
    rows = []
    print(f"ensemble scaling  p={p} ntraj={ntraj} kmax(thermal)={kmax}")
    hdr = (f"{'L':>3} | {'meas':10s} {'CR_scar':>8} "
           f"{'CR_therm(mean±sd)':>18} {'dCR':>7} {'CR_prod':>8}")
    for L in Ls:
        m = PXPModel(L)
        spec = diagonalize(m)
        identify_scars(spec, L=L)
        s0, s1, (ks0, ks1) = scar_code(spec)
        Ea, Eb = spec.energies[ks0], spec.energies[ks1]
        therm = thermal_ensemble(spec, (Ea, Eb), window=0.5, kmax=kmax, seed=1)
        rng = np.random.default_rng(3)
        i, j = rng.choice(m.dim, size=2, replace=False)
        pr0 = np.zeros(m.dim, complex); pr0[i] = 1
        pr1 = np.zeros(m.dim, complex); pr1[j] = 1
        U = propagator_from_spectrum(spec, dt)

        # Z-basis participation (mechanism bookkeeping)
        SP_scar = 0.5 * (participation_entropy(s0) + participation_entropy(s1))
        SP_therm = np.mean([0.5 * (participation_entropy(a)
                                   + participation_entropy(b))
                            for a, b in therm])
        print(hdr)
        row = dict(L=L, Ea=float(Ea), Eb=float(Eb),
                   n_thermal=len(therm), SP_scar=SP_scar,
                   SP_thermal=float(SP_therm))
        for measure, coll in [("localZ", None),
                              ("collective", sum((-1) ** i * m.z_diagonal(i)
                                                 for i in range(L)))]:
            mon = MonitoredPXP(m, dt=dt, collective_op=coll, U=U)
            cs = cr(mon, s0, s1, p, ntraj, measure)
            ct = np.array([cr(mon, a, b, p, ntraj, measure) for a, b in therm])
            cp = cr(mon, pr0, pr1, p, ntraj, measure)
            d = cs - ct.mean()
            row[measure] = dict(CR_scar=cs, CR_therm_mean=float(ct.mean()),
                                CR_therm_std=float(ct.std(ddof=1)),
                                dCR=float(d), CR_prod=cp)
            print(f"{L:>3} | {measure:10s} {cs:8.3f} "
                  f"{ct.mean():8.3f}±{ct.std(ddof=1):.3f}     {d:+.3f} {cp:8.3f}")
        rows.append(row)
        print()

    os.makedirs("results", exist_ok=True)
    with open("results/ensemble_scaling.json", "w") as f:
        json.dump(dict(p=p, ntraj=ntraj, dt=dt, rows=rows), f, indent=2)

    # ---- figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    Larr = np.array([r["L"] for r in rows])
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    ax.axhline(0, color="k", lw=0.8)
    for meas, c, mk, ls in [("localZ", "gray", "s", "--"),
                            ("collective", "C2", "o", "-")]:
        d = np.array([r[meas]["dCR"] for r in rows])
        band = np.array([r[meas]["CR_therm_std"] for r in rows])
        ax.plot(Larr, d, marker=mk, ls=ls, color=c, label=f"{meas} (scar−therm)")
        ax.fill_between(Larr, d - band, d + band, color=c, alpha=0.2)
    ax.set_xlabel("system size L")
    ax.set_ylabel(rf"$\Delta C_R$ at $p={p}$ (band = thermal-ensemble std)")
    ax.set_title("Scar advantage vs ensemble-averaged thermal baseline")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("results/ensemble_scaling.png", dpi=140)
    print("saved -> results/ensemble_scaling.png")


if __name__ == "__main__":
    main()
