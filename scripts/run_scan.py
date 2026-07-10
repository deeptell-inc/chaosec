"""Scan measurement rate p: scar-code vs thermal-code coherent information.

Produces the first slice of the (measurement rate x noise structure) phase
diagram. For each p we compute the reference-qubit coherent information
C_R = <S_R>_traj (steady state) and the integrated transient protection
A = int S_R(t) dt, for a logical qubit encoded in the PXP scar subspace vs an
energy-matched thermal subspace, under a chosen measurement model.

Usage:
    python scripts/run_scan.py --L 14 --measure localZ --ntraj 300
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np

np.seterr(all="ignore")  # suppress spurious Accelerate-BLAS matmul FP warnings

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      thermal_code, entanglement_entropy)
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def staggered_z(model: PXPModel) -> np.ndarray:
    """Diagonal of the staggered magnetisation sum_i (-1)^i Z_i."""
    return sum((-1) ** i * model.z_diagonal(i) for i in range(model.L))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=14)
    ap.add_argument("--dt", type=float, default=0.6)
    ap.add_argument("--nsteps", type=int, default=40)
    ap.add_argument("--ntraj", type=int, default=300)
    ap.add_argument("--pmax", type=float, default=0.18)
    ap.add_argument("--npts", type=int, default=10)
    ap.add_argument("--measure", choices=["localZ", "collective"],
                    default="localZ")
    ap.add_argument("--seed", type=int, default=10)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    m = PXPModel(args.L)
    spec = diagonalize(m)
    identify_scars(spec, L=args.L)
    s0, s1, (ks0, ks1) = scar_code(spec)
    Ea, Eb = float(spec.energies[ks0]), float(spec.energies[ks1])
    t0, t1, (kt0, kt1) = thermal_code(spec, (Ea, Eb))

    coll = staggered_z(m) if args.measure == "collective" else None
    mon = MonitoredPXP(m, dt=args.dt, collective_op=coll)

    cut = args.L // 2
    meta = dict(
        L=args.L, dt=args.dt, nsteps=args.nsteps, ntraj=args.ntraj,
        measure=args.measure,
        scar_energies=[Ea, Eb], thermal_energies=[float(spec.energies[kt0]),
                                                  float(spec.energies[kt1])],
        scar_S_half=[entanglement_entropy(m, s0, cut),
                     entanglement_entropy(m, s1, cut)],
        thermal_S_half=[entanglement_entropy(m, t0, cut),
                        entanglement_entropy(m, t1, cut)],
    )

    ps = np.linspace(0.0, args.pmax, args.npts)
    rows = []
    print(f"L={args.L} measure={args.measure} "
          f"scar E=({Ea:+.2f},{Eb:+.2f}) thermal matched")
    print(" p       C_R(scar)  C_R(therm)  dC_R      A(scar)  A(therm)  dA")
    for p in ps:
        cfg = TrajectoryConfig(p=float(p), n_steps=args.nsteps, dt=args.dt,
                               measure=args.measure, record_every=2)
        rs = mon.coherent_information(s0, s1, cfg, args.ntraj, seed=args.seed)
        rt = mon.coherent_information(t0, t1, cfg, args.ntraj, seed=args.seed)
        As = float(np.trapezoid(rs["S_R_mean"], rs["times"]))
        At = float(np.trapezoid(rt["S_R_mean"], rt["times"]))
        rows.append(dict(p=float(p), CR_scar=rs["C_R"], CR_scar_sem=rs["C_R_sem"],
                         CR_thermal=rt["C_R"], CR_thermal_sem=rt["C_R_sem"],
                         area_scar=As, area_thermal=At))
        print(f"{p:.3f}   {rs['C_R']:.3f}      {rt['C_R']:.3f}      "
              f"{rs['C_R']-rt['C_R']:+.3f}    {As:5.2f}    {At:5.2f}    {As-At:+.2f}")

    out = args.out or os.path.join("results", f"scan_{args.measure}_L{args.L}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(meta=meta, rows=rows), f, indent=2)
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
