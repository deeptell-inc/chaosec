"""Confounder check: is the collective-measurement scar advantage real (SGA
structure) or a generic artifact?

Decisive control: vary the collective operator being measured.
- staggered  = sum_i (-1)^i Z_i   (aligned with the emergent su(2) SGA / Neel
                                    order parameter -- should protect scars)
- uniform    = sum_i Z_i          (total magnetisation -- NOT the SGA generator)
- random     = sum_i s_i Z_i,     s_i in {+-1} fixed random (generic collective)

For each operator we report:
  (i)  static: logical off-diagonal <0|O|1>, distinguishability, and the
       *tower closure* = fraction of O|rung> that stays inside the (L+1)-dim
       scar tower (large closure => O keeps the code in a controlled subspace);
  (ii) dynamic: steady-state Delta C_R = C_R(scar) - C_R(thermal).

Prediction if the advantage is genuinely SGA-specific: Delta C_R > 0 for
staggered but ~0 for uniform/random.
"""

from __future__ import annotations

import numpy as np

np.seterr(all="ignore")

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      thermal_code)
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def collective_ops(model: PXPModel, seed: int = 0) -> dict:
    L = model.L
    Z = [model.z_diagonal(i) for i in range(L)]
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1.0, 1.0], size=L)
    return {
        "staggered": sum((-1) ** i * Z[i] for i in range(L)),
        "uniform": sum(Z),
        "random": sum(signs[i] * Z[i] for i in range(L)),
    }


def tower_projector(spec, model, n_tower=None):
    """Columns = orthonormal basis of the (L+1)-dim scar tower (top overlap)."""
    n = (model.L + 1) if n_tower is None else n_tower
    idx = np.argsort(spec.z2_overlap)[::-1][:n]
    return spec.vectors[:, idx]                      # (dim, n)


def closure(op_diag, state, Ptower):
    """Fraction of O|state> that lies in the tower subspace."""
    v = op_diag * state
    nv = np.linalg.norm(v)
    if nv < 1e-14:
        return float("nan")
    proj = Ptower @ (Ptower.conj().T @ v)
    return float((np.linalg.norm(proj) / nv) ** 2)


def main():
    L = 14
    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    s0, s1, (ks0, ks1) = scar_code(spec)
    Ea, Eb = spec.energies[ks0], spec.energies[ks1]
    t0, t1, _ = thermal_code(spec, (Ea, Eb))
    Ptower = tower_projector(spec, m)
    ops = collective_ops(m)

    p_probe = 0.10
    ntraj = 400
    print(f"L={L}  p={p_probe}  ntraj={ntraj}\n")
    print(f"{'operator':10s} | static: |<0|O|1>|  closure(scar) closure(therm)"
          f" | dynamic: dC_R")
    print("-" * 78)
    for name, O in ops.items():
        offs = abs(np.vdot(s0, O * s1))
        cl_s = 0.5 * (closure(O, s0, Ptower) + closure(O, s1, Ptower))
        cl_t = 0.5 * (closure(O, t0, Ptower) + closure(O, t1, Ptower))
        mon = MonitoredPXP(m, dt=0.6, collective_op=O)
        cfg = TrajectoryConfig(p=p_probe, n_steps=40, dt=0.6,
                               measure="collective", record_every=2)
        rs = mon.coherent_information(s0, s1, cfg, ntraj, seed=10)
        rt = mon.coherent_information(t0, t1, cfg, ntraj, seed=10)
        d = rs["C_R"] - rt["C_R"]
        dsem = np.hypot(rs["C_R_sem"], rt["C_R_sem"])
        print(f"{name:10s} | {offs:9.3f}      {cl_s:6.3f}        {cl_t:6.3f}"
              f"      | {d:+.3f} +/- {dsem:.3f}")


if __name__ == "__main__":
    main()
