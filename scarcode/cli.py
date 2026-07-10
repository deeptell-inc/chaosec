"""Command-line demo / self-check for the ``scarcode`` package.

Run ``scarcode-demo`` after installation. It exercises the core objects and
prints the key validated quantities, so a fresh install can be confirmed in a
few seconds.
"""

from __future__ import annotations

import numpy as np

from . import (PXPModel, diagonalize, identify_scars, scar_code,
               thermal_ensemble, MonitoredPXP, TrajectoryConfig,
               casimir, Spin1Scar, __version__)


def main() -> int:
    np.seterr(all="ignore")
    print(f"scarcode {__version__} — self-check\n")

    # 1. PXP constrained basis: dimension is Fibonacci F(L+2)
    def fib(n):
        a, b = 1, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return a
    L = 12
    m = PXPModel(L)
    ok_dim = (m.dim == fib(L + 2))
    print(f"[1] PXP L={L}: dim={m.dim}  (Fibonacci F(14)={fib(14)})  "
          f"{'OK' if ok_dim else 'FAIL'}")

    # 2. Z2 scar revival (t~4.70, F~0.74)
    spec = diagonalize(m)
    z2 = m.neel_state(0)
    c2 = (spec.vectors.T @ z2) ** 2
    ts = np.linspace(3.0, 6.0, 301)
    fid = np.abs((np.exp(-1j * np.outer(ts, spec.energies)) * c2).sum(1)) ** 2
    i = int(np.argmax(fid))
    print(f"[2] Z2 revival: t={ts[i]:.2f}  fidelity={fid[i]:.3f}  "
          f"{'OK' if fid[i] > 0.6 else 'FAIL'}")

    # 3. Monitored channel: p=0 => C_R=1 exactly
    identify_scars(spec, L=L)
    s0, s1, (k0, k1) = scar_code(spec)
    mon = MonitoredPXP(m, dt=0.6)
    cfg0 = TrajectoryConfig(p=0.0, n_steps=10, dt=0.6)
    cr0 = mon.coherent_information(s0, s1, cfg0, n_traj=3, seed=1)["C_R"]
    print(f"[3] monitored p=0: C_R={cr0:.4f}  "
          f"{'OK' if abs(cr0 - 1.0) < 1e-6 else 'FAIL'}")

    # 4. Thermal ensemble baseline beats scar under monitoring (headline)
    Ea, Eb = spec.energies[k0], spec.energies[k1]
    therm = thermal_ensemble(spec, (Ea, Eb), kmax=6, seed=1)
    cfg = TrajectoryConfig(p=0.06, n_steps=30, dt=0.6)
    cs = mon.coherent_information(s0, s1, cfg, 80, seed=2)["C_R"]
    ct = np.mean([mon.coherent_information(a, b, cfg, 80, seed=2)["C_R"]
                  for a, b in therm])
    print(f"[4] local monitoring p=0.06: C_R(scar)={cs:.3f}  "
          f"C_R(thermal)={ct:.3f}  -> thermal {'wins' if ct >= cs else 'loses'}")

    # 5. Spin-1 exact scars: J^2 variance = 0 on the tower
    sp = Spin1Scar(4, h=1.0, D=0.1)
    ens, tw = sp.tower()
    J2 = sp.casimir()
    j2 = [(tw[:, n] @ (J2 @ tw[:, n])).real for n in range(tw.shape[1])]
    print(f"[5] spin-1 L=4: tower size={tw.shape[1]}  J^2 mean={np.mean(j2):.3f} "
          f"std={np.std(j2):.1e}  {'OK' if np.std(j2) < 1e-6 else 'FAIL'}")

    print("\nself-check complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
