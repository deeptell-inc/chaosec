"""DFS rescue test: can the scar code win under a fine-tuned J^2 measurement?

The emergent su(2) Casimir J^2 is constant on a true multiplet. PXP scars only
approximately close the algebra, BUT the chiral-symmetric pair (|+E>, |-E>) of
scar rungs is *exactly* J^2-degenerate (diff = 0, tiny leak), whereas generic
thermal +/-E pairs are not. So a J^2 measurement is an (approximate) DFS for the
symmetric scar code but dephases thermal codes.

We compare C_R(scar +/-E) against a thermal ensemble of +/-E pairs under
(a) J^2 (operator) measurement and (b) local-Z baseline. A positive collective
Delta C_R would be the fine-tuned rescue; note it needs the specific symmetric
encoding AND the highly non-local J^2 observable.
"""

from __future__ import annotations

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


def sym_pair(spec, Etarget, tol, want_scar, z2cut=0.02):
    """Highest- (scar) or low- (thermal) Z2-overlap +/-E eigenstate indices."""
    w, ov = spec.energies, spec.z2_overlap
    def side(sign):
        idx = [k for k in range(len(w))
               if abs(w[k] - sign * Etarget) < tol
               and (spec.scar_mask[k] if want_scar else (ov[k] < z2cut))]
        if not idx:
            return None
        idx = np.array(idx)
        return int(idx[np.argmax(ov[idx])] if want_scar
                   else idx[np.argmin(np.abs(w[idx] - sign * Etarget))])
    return side(+1), side(-1)


def main():
    L, dt, ntraj = 14, 0.6, 200
    Etarget = 2.74
    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    U = propagator_from_spectrum(spec, dt)
    J2 = casimir(m)

    kp, kn = sym_pair(spec, Etarget, 0.15, want_scar=True)
    s0, s1 = spec.vectors[:, kp], spec.vectors[:, kn]

    # thermal ensemble of generic +/-E pairs
    w, ov = spec.energies, spec.z2_overlap
    pos = [k for k in range(len(w)) if abs(w[k] - Etarget) < 0.3
           and ov[k] < 0.02 and not spec.scar_mask[k]]
    neg = [k for k in range(len(w)) if abs(w[k] + Etarget) < 0.3
           and ov[k] < 0.02 and not spec.scar_mask[k]]
    rng = np.random.default_rng(1)
    rng.shuffle(pos); rng.shuffle(neg)
    therm = [(spec.vectors[:, a], spec.vectors[:, b])
             for a, b in zip(pos[:10], neg[:10])]

    # DFS diagnostics
    def d(v): return float(np.vdot(v, J2 @ v).real)
    def lk(a, b): return abs(np.vdot(a, J2 @ b))
    print(f"L={L} J^2 DFS check:")
    print(f"  scar +/-E : J2 diff={abs(d(s0)-d(s1)):.3f} leak={lk(s0,s1):.3f}")
    tdiff = np.mean([abs(d(a)-d(b)) for a, b in therm])
    print(f"  thermal   : mean J2 diff={tdiff:.3f} (nonzero => dephased by J2)")

    mon_J2 = MonitoredPXP(m, dt=dt, U=U, operator=J2)
    mon_loc = MonitoredPXP(m, dt=dt, U=U)
    ps = [0.04, 0.08, 0.12]
    out = {}
    for meas, mon in [("J2", mon_J2), ("localZ", mon_loc)]:
        rows = []
        for p in ps:
            cfg = TrajectoryConfig(p=p, n_steps=40, dt=dt,
                                   measure="operator" if meas == "J2" else "localZ",
                                   record_every=4)
            cs = mon.coherent_information(s0, s1, cfg, ntraj, 10)["C_R"]
            ct = np.array([mon.coherent_information(a, b, cfg, ntraj, 10)["C_R"]
                           for a, b in therm])
            rows.append(dict(p=p, CR_scar=cs, CR_therm_mean=float(ct.mean()),
                             CR_therm_std=float(ct.std(ddof=1)),
                             dCR=float(cs - ct.mean())))
            print(f"  [{meas:6s}] p={p:.2f}: scar={cs:.3f} "
                  f"therm={ct.mean():.3f}±{ct.std(ddof=1):.3f}  dCR={cs-ct.mean():+.3f}")
        out[meas] = rows

    os.makedirs("results", exist_ok=True)
    json.dump(dict(L=L, Etarget=Etarget,
                   scar_J2_diff=abs(d(s0)-d(s1)), scar_J2_leak=lk(s0, s1),
                   thermal_J2_diff=float(tdiff), results=out),
              open("results/dfs_rescue.json", "w"), indent=2)
    print("\nsaved -> results/dfs_rescue.json")
    verdict = ("RESCUE WORKS" if out["J2"][-1]["dCR"] > 0.05
               else "rescue fails/marginal")
    print(f"VERDICT (J2, largest p): dCR={out['J2'][-1]['dCR']:+.3f} -> {verdict}")


if __name__ == "__main__":
    main()
