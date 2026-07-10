"""Corrected headline figure: C_R(p) for the scar code vs the thermal ENSEMBLE.

Supersedes the earlier crossover_L14.png (which compared against a single biased
thermal pair). Shows the scar C_R(p) line sitting BELOW the thermal-ensemble band
for both local-Z and collective monitoring => thermal is the better code.
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


def main():
    L, dt, ntraj, kmax = 14, 0.6, 250, 12
    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    s0, s1, (ks0, ks1) = scar_code(spec)
    Ea, Eb = spec.energies[ks0], spec.energies[ks1]
    therm = thermal_ensemble(spec, (Ea, Eb), window=0.5, kmax=kmax, seed=1)
    U = propagator_from_spectrum(spec, dt)
    stag = sum((-1) ** i * m.z_diagonal(i) for i in range(L))
    ps = np.linspace(0.0, 0.16, 9)

    data = {}
    for name, coll, meas in [("localZ", None, "localZ"),
                             ("collective", stag, "collective")]:
        mon = MonitoredPXP(m, dt=dt, collective_op=coll, U=U)
        scar, tmean, tstd = [], [], []
        for p in ps:
            cfg = TrajectoryConfig(p=float(p), n_steps=40, dt=dt, measure=meas,
                                   record_every=4)
            scar.append(mon.coherent_information(s0, s1, cfg, ntraj, 10)["C_R"])
            ct = np.array([mon.coherent_information(a, b, cfg, ntraj, 10)["C_R"]
                           for a, b in therm])
            tmean.append(ct.mean()); tstd.append(ct.std(ddof=1))
        data[name] = dict(scar=scar, tmean=tmean, tstd=tstd)
        print(f"{name}: done")

    os.makedirs("results", exist_ok=True)
    json.dump(dict(L=L, ps=ps.tolist(), **data),
              open("results/corrected_crossover.json", "w"), indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, name in zip(axes, ["localZ", "collective"]):
        d = data[name]
        tm, ts = np.array(d["tmean"]), np.array(d["tstd"])
        ax.plot(ps, d["scar"], "o-", color="C3", label="scar code")
        ax.plot(ps, tm, "s--", color="C0", label="thermal ensemble (mean)")
        ax.fill_between(ps, tm - ts, tm + ts, color="C0", alpha=0.25,
                        label="thermal ±1σ")
        ax.set_title(f"{name} monitoring")
        ax.set_xlabel("measurement rate p"); ax.grid(alpha=0.3); ax.legend()
    axes[0].set_ylabel(r"coherent information $C_R$")
    fig.suptitle(f"Thermal code beats scar code (PXP L={L}) — corrected baseline")
    fig.tight_layout()
    fig.savefig("results/corrected_crossover.png", dpi=140)
    print("saved -> results/corrected_crossover.png")


if __name__ == "__main__":
    main()
