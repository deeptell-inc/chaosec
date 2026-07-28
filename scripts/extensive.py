"""Extensive (many-logical-qubit) code comparison.

The scar tower is (L+1)-dimensional, so the largest scar code holds
k = floor(log2(L+1)) logical qubits -- sub-extensive. We encode that maximal
k-qubit code (2^k tower states, maximally entangled with a k-qubit reference)
and compare its monitored reference entropy S_R in [0,k] against a same-
dimension thermal code (2^k mid-spectrum eigenstates, ensemble-averaged) under
local-Z monitoring. Reports the protected-information density S_R / k.
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import PXPModel, diagonalize, identify_scars
from scarcode.su2 import casimir
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def propagator_from_spectrum(spec, dt):
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=14)
    ap.add_argument("--ntraj", type=int, default=200)
    ap.add_argument("--kthermal", type=int, default=8)
    ap.add_argument("--ps", default=None,
                    help="comma-separated measurement rates "
                         "(default: the grid of the shipped results)")
    ap.add_argument("--measure", choices=["localZ", "collective", "operator"],
                    default="localZ")
    args = ap.parse_args()
    L, dt = args.L, 0.6

    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    U = propagator_from_spectrum(spec, dt)
    w, ov = spec.energies, spec.z2_overlap

    tower = np.where(spec.scar_mask)[0]
    k = int(np.floor(np.log2(len(tower))))
    mcode = 2 ** k
    # scar code: the 2^k highest-Z2-overlap tower states
    scar_idx = tower[np.argsort(ov[tower])[::-1][:mcode]]
    scar_code = [spec.vectors[:, i] for i in scar_idx]
    e_lo, e_hi = w[scar_idx].min(), w[scar_idx].max()

    # thermal code ensemble: 2^k generic (non-scar) eigenstates within the same
    # energy span, drawn several times
    pool = np.array([i for i in range(len(w))
                     if not spec.scar_mask[i] and ov[i] < 0.02
                     and e_lo - 0.5 <= w[i] <= e_hi + 0.5])
    rng = np.random.default_rng(0)
    thermal_codes = [[spec.vectors[:, i] for i in rng.choice(pool, mcode, replace=False)]
                     for _ in range(args.kthermal)]

    coll = (sum((-1) ** i * m.z_diagonal(i) for i in range(L))
            if args.measure == "collective" else None)
    op = casimir(m) if args.measure == "operator" else None
    mon = MonitoredPXP(m, dt=dt, U=U, collective_op=coll, operator=op)
    print(f"L={L}: tower dim={len(tower)}, k={k} logical qubits (code dim {mcode}); "
          f"{len(pool)} thermal states in window; measure={args.measure}")
    # Default grids match the shipped results/ JSONs: the local runs behind
    # Fig. 4 used p = 0, 0.02, 0.04, 0.08; the collective/operator runs behind
    # Table S8 used p = 0, 0.04, 0.08, 0.12.  Override with --ps.
    if args.ps:
        ps = [float(x) for x in args.ps.split(",")]
    elif args.measure == "localZ":
        ps = [0.0, 0.02, 0.04, 0.08]
    else:
        ps = [0.0, 0.04, 0.08, 0.12]
    rows = []
    for p in ps:
        cfg = TrajectoryConfig(p=p, n_steps=40, dt=dt, measure=args.measure,
                               record_every=4)
        rs = mon.coherent_information_code(scar_code, cfg, args.ntraj, seed=10)
        dt_ = np.array([mon.coherent_information_code(tc, cfg, args.ntraj, seed=10)["density"]
                        for tc in thermal_codes])
        rows.append(dict(p=p, k=k, scar_density=rs["density"],
                         thermal_density=float(dt_.mean()),
                         thermal_density_sd=float(dt_.std(ddof=1)),
                         d_density=float(rs["density"] - dt_.mean())))
        print(f"  p={p:.2f}: scar S_R/k={rs['density']:.3f}  "
              f"thermal S_R/k={dt_.mean():.3f}±{dt_.std(ddof=1):.3f}  "
              f"Delta={rs['density']-dt_.mean():+.3f}")

    os.makedirs("results", exist_ok=True)
    tag = f"L{L}" if args.measure == "localZ" else f"L{L}_{args.measure}"
    json.dump(dict(L=L, k=k, code_dim=mcode, n_tower=len(tower),
                   measure=args.measure, rows=rows),
              open(f"results/extensive_{tag}.json", "w"), indent=2)
    print(f"saved -> results/extensive_{tag}.json")


if __name__ == "__main__":
    main()
