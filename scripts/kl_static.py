"""Generator for the static Knill-Laflamme violation ratios quoted in the
Supplement (scar vs energy-matched thermal code under the local-Z error set).

Reproduces the original energy-matched single-pair diagnostic: for each L the
scar code is the two positive-energy tower rungs and the thermal code is the
nearest energy-matched generic pair (states.thermal_code).
"""

from __future__ import annotations

import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      thermal_code, kl_local_z)


def main():
    rows = []
    for L in [10, 12, 14]:
        m = PXPModel(L)
        spec = diagonalize(m)
        identify_scars(spec, L=L)
        s0, s1, (k0, k1) = scar_code(spec)
        t0, t1, _ = thermal_code(spec, (spec.energies[k0], spec.energies[k1]))
        r_s = kl_local_z(m, s0, s1).eps_rms
        r_t = kl_local_z(m, t0, t1).eps_rms
        rows.append(dict(L=L, eps_scar=float(r_s), eps_thermal=float(r_t),
                         ratio=float(r_s / r_t)))
        print(f"L={L}: eps_rms scar={r_s:.3e} thermal={r_t:.3e} "
              f"ratio={r_s/r_t:.2f}")
    os.makedirs("results", exist_ok=True)
    json.dump(dict(error_set="local-Z", rows=rows),
              open("results/kl_static.json", "w"), indent=2)
    print("saved -> results/kl_static.json")


if __name__ == "__main__":
    main()
