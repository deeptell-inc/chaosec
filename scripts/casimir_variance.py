"""Generator for the Casimir-variance comparison quoted in the paper.

Computes Var J^2 for the chiral-symmetric PXP scar pair (E ~ +/-2.74) and for
the energy-matched thermal ensemble selected exactly as in dfs_rescue.py
(window 0.3 around +/-E_target, Z2 overlap < 0.02, non-tower, seed 1, 10
pairs). Ships the numbers that back the "irreducible scar Casimir variance"
mechanism statement, replacing an earlier manuscript-only value.
"""

from __future__ import annotations

import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import PXPModel, diagonalize, identify_scars
from scarcode.su2 import casimir


def var_of(v, J2):
    m1 = np.vdot(v, J2 @ v).real
    m2 = np.vdot(v, J2 @ (J2 @ v)).real
    return float(m2 - m1 ** 2)


def main():
    L, Etarget = 14, 2.74
    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    J2 = casimir(m)
    w, ov = spec.energies, spec.z2_overlap

    def scar_at(sign):
        idx = np.array([k for k in range(len(w))
                        if abs(w[k] - sign * Etarget) < 0.15 and spec.scar_mask[k]])
        return int(idx[np.argmax(ov[idx])])

    ks = [scar_at(+1), scar_at(-1)]
    scar_vars = [var_of(spec.vectors[:, k], J2) for k in ks]

    pos = [k for k in range(len(w)) if abs(w[k] - Etarget) < 0.3
           and ov[k] < 0.02 and not spec.scar_mask[k]]
    neg = [k for k in range(len(w)) if abs(w[k] + Etarget) < 0.3
           and ov[k] < 0.02 and not spec.scar_mask[k]]
    rng = np.random.default_rng(1)
    rng.shuffle(pos); rng.shuffle(neg)
    therm_states = list(pos[:10]) + list(neg[:10])
    therm_vars = [var_of(spec.vectors[:, k], J2) for k in therm_states]

    out = dict(L=L, Etarget=Etarget,
               scar_vars=scar_vars, scar_var_mean=float(np.mean(scar_vars)),
               thermal_vars=therm_vars,
               thermal_var_mean=float(np.mean(therm_vars)),
               thermal_var_min=float(np.min(therm_vars)),
               thermal_var_max=float(np.max(therm_vars)),
               n_thermal=len(therm_vars))
    os.makedirs("results", exist_ok=True)
    json.dump(out, open("results/casimir_variance.json", "w"), indent=2)
    print(f"scar Var J^2      : {out['scar_var_mean']:.2f} "
          f"(states: {[round(v,2) for v in scar_vars]})")
    print(f"thermal Var J^2   : mean {out['thermal_var_mean']:.2f}  "
          f"range [{out['thermal_var_min']:.2f}, {out['thermal_var_max']:.2f}]  "
          f"(n={out['n_thermal']})")
    print("saved -> results/casimir_variance.json")


if __name__ == "__main__":
    main()
