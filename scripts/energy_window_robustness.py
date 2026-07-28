"""Energy-matching tolerance audit for the thermal-ensemble baseline.

Addresses the review finding that the manuscript claimed scar and thermal codes
sit at the "same two energies" while `thermal_ensemble` accepts states within
+/- `window` (0.5 in the headline scripts). Three checks at the headline point
(PXP L=14, p=0.10, local + collective monitoring, kmax=12, seed=1, ntraj=250 --
identical to corrected_crossover.py):

1. Disclose the actual offset distribution of the window=0.5 ensemble:
   per-state |E - E_target| and per-pair total-energy shift
   (Ea'+Eb') - (Ea+Eb).
2. Rerun with tighter windows (0.25, 0.10). If the scar deficit Delta C_R is an
   energy-mismatch artifact it must shrink/vanish as the window tightens.
3. Within the window=0.5 ensemble, correlate per-pair C_R against the pair's
   energy offset (Spearman). A flat relation means residual energy dependence
   does not drive the thermal band.

Output: results/energy_window_robustness.json + console summary.
"""

from __future__ import annotations

import json
import os

import numpy as np
from scipy.stats import spearmanr

np.seterr(all="ignore")

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      thermal_ensemble)
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def propagator_from_spectrum(spec, dt):
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T


def main():
    L, dt, ntraj, kmax, p = 14, 0.6, 250, 12, 0.10
    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    s0, s1, (ks0, ks1) = scar_code(spec)
    Ea, Eb = float(spec.energies[ks0]), float(spec.energies[ks1])
    U = propagator_from_spectrum(spec, dt)
    stag = sum((-1) ** i * m.z_diagonal(i) for i in range(L))

    modes = [("localZ", None, "localZ"), ("collective", stag, "collective")]
    out = {"L": L, "p": p, "ntraj": ntraj, "kmax": kmax, "seed": 1,
           "targets": [Ea, Eb], "windows": {}}

    # scar reference (window-independent)
    scar_cr = {}
    for name, coll, meas in modes:
        mon = MonitoredPXP(m, dt=dt, collective_op=coll, U=U)
        cfg = TrajectoryConfig(p=p, n_steps=40, dt=dt, measure=meas,
                               record_every=4)
        scar_cr[name] = mon.coherent_information(s0, s1, cfg, ntraj, 10)["C_R"]
    out["scar_C_R"] = scar_cr
    print(f"scar C_R @ p={p}: {scar_cr}")

    for window in (0.5, 0.25, 0.10):
        therm, idx = thermal_ensemble(spec, (Ea, Eb), window=window, kmax=kmax,
                                      seed=1, return_indices=True)
        off_a = [float(spec.energies[a] - Ea) for a, _ in idx]
        off_b = [float(spec.energies[b] - Eb) for _, b in idx]
        shift = [oa + ob for oa, ob in zip(off_a, off_b)]
        mean_abs = [0.5 * (abs(oa) + abs(ob)) for oa, ob in zip(off_a, off_b)]

        wrec = {"n_pairs": len(idx), "offset_a": off_a, "offset_b": off_b,
                "pair_total_shift": shift,
                "mean_abs_offset": float(np.mean(mean_abs)),
                "max_abs_offset": float(max(max(map(abs, off_a)),
                                            max(map(abs, off_b))))}
        for name, coll, meas in modes:
            mon = MonitoredPXP(m, dt=dt, collective_op=coll, U=U)
            cfg = TrajectoryConfig(p=p, n_steps=40, dt=dt, measure=meas,
                                   record_every=4)
            cr = [mon.coherent_information(a, b, cfg, ntraj, 10)["C_R"]
                  for a, b in therm]
            rho_off, pv_off = spearmanr(mean_abs, cr)
            rho_sh, pv_sh = spearmanr(shift, cr)
            wrec[name] = {
                "C_R": cr, "mean": float(np.mean(cr)),
                "std": float(np.std(cr, ddof=1)),
                "delta_scar_minus_thermal": float(scar_cr[name] - np.mean(cr)),
                "spearman_CR_vs_absoffset": [float(rho_off), float(pv_off)],
                "spearman_CR_vs_totalshift": [float(rho_sh), float(pv_sh)],
            }
            print(f"window={window:.2f} {name}: thermal {np.mean(cr):.3f}"
                  f"+/-{np.std(cr, ddof=1):.3f}  DeltaC_R="
                  f"{scar_cr[name] - np.mean(cr):+.3f}  "
                  f"rho(|off|)={rho_off:+.2f} (p={pv_off:.2f})")
        print(f"window={window:.2f}: mean|off|={wrec['mean_abs_offset']:.3f} "
              f"max|off|={wrec['max_abs_offset']:.3f} n={len(idx)}")
        out["windows"][str(window)] = wrec

    os.makedirs("results", exist_ok=True)
    json.dump(out, open("results/energy_window_robustness.json", "w"),
              indent=2)
    print("saved -> results/energy_window_robustness.json")


if __name__ == "__main__":
    main()
