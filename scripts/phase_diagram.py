"""2D phase diagram of the scar advantage Delta C_R(p, ell).

Axes:
  p    -- measurement rate (per step)
  ell  -- measurement support size (block-sum Z over ell contiguous sites).
          ell=1 is local single-site Z; ell=L is global uniform magnetisation.
          The per-step event count is fixed, so ell isolates *locality*.

For each (p, ell) we compute Delta C_R = C_R(scar) - C_R(thermal). The
Delta C_R = 0 contour is the crossover line separating "no scar advantage"
(local, small ell) from "scar-protected" (collective, large ell).

Saves results/phase_diagram_L{L}.json and results/phase_diagram_L{L}.png.
"""

from __future__ import annotations

import argparse
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=14)
    ap.add_argument("--ntraj", type=int, default=200)
    ap.add_argument("--nsteps", type=int, default=40)
    ap.add_argument("--dt", type=float, default=0.6)
    ap.add_argument("--npx", type=int, default=7)
    ap.add_argument("--pmax", type=float, default=0.14)
    ap.add_argument("--kthermal", type=int, default=6)
    args = ap.parse_args()
    L = args.L

    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    s0, s1, (ks0, ks1) = scar_code(spec)
    Ea, Eb = spec.energies[ks0], spec.energies[ks1]
    therm = thermal_ensemble(spec, (Ea, Eb), window=0.5, kmax=args.kthermal,
                             seed=1)
    U = propagator_from_spectrum(spec, args.dt)
    mon = MonitoredPXP(m, dt=args.dt, U=U)

    ps = np.linspace(0.02, args.pmax, args.npx)
    ells = sorted(set([1, 2, 3, max(4, L // 3), max(6, L // 2),
                       int(0.8 * L), L]))
    D = np.full((len(ells), len(ps)), np.nan)
    Dsem = np.full_like(D, np.nan)

    print(f"phase diagram L={L} ntraj={args.ntraj}  ells={ells}")
    for a, ell in enumerate(ells):
        for b, p in enumerate(ps):
            cfg = TrajectoryConfig(p=float(p), n_steps=args.nsteps, dt=args.dt,
                                   measure="block", block_size=ell,
                                   record_every=4)
            rs = mon.coherent_information(s0, s1, cfg, args.ntraj, seed=10)
            ct = np.array([mon.coherent_information(a, b, cfg, args.ntraj,
                                                    seed=10)["C_R"]
                           for a, b in therm])
            D[a, b] = rs["C_R"] - ct.mean()          # scar - ensemble thermal
            Dsem[a, b] = np.hypot(rs["C_R_sem"], ct.std(ddof=1) / len(ct) ** 0.5)
        print(f"  ell={ell:2d}: dCR = "
              + " ".join(f"{D[a,b]:+.3f}" for b in range(len(ps))))

    payload = dict(L=L, ntraj=args.ntraj, dt=args.dt, ps=ps.tolist(),
                   ells=list(ells), dCR=D.tolist(), dCR_sem=Dsem.tolist())
    os.makedirs("results", exist_ok=True)
    with open(f"results/phase_diagram_L{L}.json", "w") as f:
        json.dump(payload, f, indent=2)

    # ---- plot
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 5))
    vmax = np.nanmax(np.abs(D))
    im = ax.pcolormesh(ps, ells, D, shading="nearest",
                       cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    try:
        cs = ax.contour(ps, ells, D, levels=[0.0], colors="k", linewidths=1.5)
        ax.clabel(cs, fmt=r"$\Delta C_R=0$")
    except Exception:
        pass
    ax.set_xlabel("measurement rate p")
    ax.set_ylabel(r"measurement support size $\ell$")
    ax.set_title(rf"$\Delta C_R(p,\ell)$ vs ensemble thermal  (PXP, L={L}) "
                 rf"— negative = scar worse")
    fig.colorbar(im, ax=ax, label=r"$\Delta C_R = C_R^{scar}-C_R^{therm}$")
    fig.tight_layout()
    fig.savefig(f"results/phase_diagram_L{L}.png", dpi=140)
    print(f"saved -> results/phase_diagram_L{L}.png")


if __name__ == "__main__":
    main()
