"""Second model (spin-1 Schecter-Iadecola exact scars): does the refutation
generalize, and does the EXACT-su(2) make the J^2 DFS rescue succeed?

Predictions from the model-independent criterion:
  - local S^z measurement: thermal > scar  (refutation generalizes)
  - J^2 (exact Casimir, zero scar variance): scar > thermal  (rescue SUCCEEDS,
    the clean contrast to PXP where scar J^2 variance ~32 made it fail)
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode.spin1 import Spin1Scar
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=6)
    ap.add_argument("--ntraj", type=int, default=150)
    ap.add_argument("--kthermal", type=int, default=6)
    ap.add_argument("--h", type=float, default=1.0)
    ap.add_argument("--D", type=float, default=0.1)
    args = ap.parse_args()
    L, dt = args.L, 0.6

    m = Spin1Scar(L, J=1.0, h=args.h, D=args.D)
    H = m.hamiltonian().toarray()
    w, V = np.linalg.eigh(H)
    ens_t, tw = m.tower()
    J2 = m.casimir()

    # identify tower eigenvectors by overlap with exact scar states
    tower_ov = np.max(np.abs(V.conj().T @ tw) ** 2, axis=1)   # (dim,)
    is_tower = tower_ov > 0.9

    # scar code: two mid-tower rungs (nearest E=0), from the exact tower
    order = np.argsort(np.abs(ens_t))
    n0, n1 = order[0], order[1]
    s0, s1 = tw[:, n0], tw[:, n1]
    Ea, Eb = ens_t[n0], ens_t[n1]

    # thermal ensemble: non-tower eigenstates energy-matched to Ea, Eb
    def thermal_pool(E, win=0.8):
        idx = [k for k in range(len(w)) if abs(w[k] - E) < win and not is_tower[k]]
        return sorted(idx, key=lambda k: abs(w[k] - E))
    pa, pb = thermal_pool(Ea), thermal_pool(Eb)
    rng = np.random.default_rng(1)
    rng.shuffle(pa); rng.shuffle(pb)
    therm = [(V[:, a], V[:, b]) for a, b in zip(pa[:args.kthermal],
                                                pb[:args.kthermal])]

    # J^2 statics (the mechanism contrast)
    def var(v): return float((v @ (J2 @ (J2 @ v))).real - (v @ (J2 @ v)).real ** 2)
    var_s = 0.5 * (var(s0) + var(s1))
    var_t = np.mean([0.5 * (var(a) + var(b)) for a, b in therm])
    leak_s = abs(np.vdot(s0, J2 @ s1))
    print(f"L={L} dim={m.dim}: scar E=({Ea:+.2f},{Eb:+.2f}), {len(therm)} thermal pairs")
    print(f"  J^2 variance: scar={var_s:.3e} (exact 0)  thermal={var_t:.2f}"
          f"  | scar leak<0|J2|1>={leak_s:.2e}")

    Uprop = (V * np.exp(-1j * w * dt)) @ V.conj().T
    site_diags = m.sz_diagonals()
    mon_site = MonitoredPXP(m, dt=dt, U=Uprop, site_diags=site_diags)
    mon_J2 = MonitoredPXP(m, dt=dt, U=Uprop, operator=J2)

    def cr(mon, v0, v1, p, measure):
        cfg = TrajectoryConfig(p=p, n_steps=40, dt=dt, measure=measure,
                               record_every=4)
        return mon.coherent_information(v0, v1, cfg, args.ntraj, seed=10)["C_R"]

    out = {"L": L, "var_scar": var_s, "var_thermal": float(var_t)}
    print("\n meas       p     CR_scar   CR_therm(mean±sd)   dCR")
    for label, mon, meas in [("local Sz", mon_site, "sites"),
                             ("J^2", mon_J2, "operator")]:
        rows = []
        for p in [0.04, 0.08, 0.12]:
            cs = cr(mon, s0, s1, p, meas)
            ct = np.array([cr(mon, a, b, p, meas) for a, b in therm])
            d = cs - ct.mean()
            rows.append(dict(p=p, CR_scar=float(cs), CR_therm=float(ct.mean()),
                             CR_therm_sd=float(ct.std(ddof=1)), dCR=float(d)))
            print(f" {label:8s} {p:.2f}   {cs:.3f}     "
                  f"{ct.mean():.3f}±{ct.std(ddof=1):.3f}       {d:+.3f}")
        out[meas] = rows
    verdict_local = "thermal wins (refutation generalizes)" if out["sites"][-1]["dCR"] < 0 else "scar wins"
    verdict_J2 = "SCAR WINS (DFS rescue SUCCEEDS)" if out["operator"][-1]["dCR"] > 0.05 else "rescue fails"
    print(f"\n VERDICT  local Sz -> {verdict_local}")
    print(f" VERDICT  J^2      -> {verdict_J2}")

    out["h"] = args.h; out["D"] = args.D
    os.makedirs("results", exist_ok=True)
    tag = f"L{L}" if (args.h == 1.0 and args.D == 0.1) else f"L{L}_h{args.h}_D{args.D}"
    json.dump(out, open(f"results/spin1_dfs_{tag}.json", "w"), indent=2)
    print(f"saved -> results/spin1_dfs_{tag}.json")


if __name__ == "__main__":
    main()
