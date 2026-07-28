"""O2-5: the L=16 point of Fig. 2 uses the other member of the 2.64/2.74
anticrossing doublet (overlap ranking flips there).  Does the choice of
doublet partner change the L=16 local/collective deficit?"""
import json, os
import numpy as np
from scarcode import PXPModel, diagonalize, identify_scars, scar_code, thermal_ensemble
from scarcode.monitor import MonitoredPXP, TrajectoryConfig

L, DT, NTRAJ, KMAX, SEED, P = 16, 0.6, 200, 12, 1, 0.10
m = PXPModel(L); spec = diagonalize(m); identify_scars(spec, L=L)
U = (spec.vectors * np.exp(-1j * spec.energies * DT)) @ spec.vectors.conj().T
M = sum((-1) ** i * m.z_diagonal(i) for i in range(L))
s0, s1, (k0, k1) = scar_code(spec)
E0, E1 = spec.energies[k0], spec.energies[k1]
# the other doublet member near |E1|
cand = [k for k in range(len(spec.energies))
        if abs(spec.energies[k] - E1) < 0.2 and k != k1]
k1b = max(cand, key=lambda k: spec.z2_overlap[k])
E1b = spec.energies[k1b]
print(f"canonical rungs: E=({E0:.4f},{E1:.4f}) ov=({spec.z2_overlap[k0]:.4f},{spec.z2_overlap[k1]:.4f})")
print(f"alternative partner: E={E1b:.4f} ov={spec.z2_overlap[k1b]:.4f}")
out = dict(L=L, p=P, canonical=[float(E0), float(E1)], alternative=float(E1b), rows={})
for tag, kb in (("canonical", k1), ("partner", k1b)):
    Eb = spec.energies[kb]
    therm = thermal_ensemble(spec, (E0, Eb), window=0.5, kmax=KMAX, seed=SEED)
    for meas, op in (("localZ", None), ("collective", M)):
        mon = MonitoredPXP(m, dt=DT, U=U, collective_op=op)
        cfg = TrajectoryConfig(p=P, n_steps=40, dt=DT, measure=meas, record_every=4)
        cs = mon.coherent_information(spec.vectors[:, k0], spec.vectors[:, kb], cfg, NTRAJ, SEED)["C_R"]
        tv = [mon.coherent_information(a, b, cfg, NTRAJ, SEED)["C_R"] for a, b in therm]
        d = cs - float(np.mean(tv))
        out["rows"][f"{tag}_{meas}"] = dict(scar=cs, therm_mean=float(np.mean(tv)),
                                            therm_std=float(np.std(tv, ddof=1)), dCR=d)
        print(f"{tag:9s} {meas:10s}: scar={cs:.4f} therm={np.mean(tv):.4f}+-{np.std(tv,ddof=1):.4f} dCR={d:+.4f}")
json.dump(out, open("results/l16_partner_check.json", "w"), indent=1)
print("saved")
