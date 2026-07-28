"""Connect our measurement-rate axis p to the gamma_c ~ 0.013 of arXiv:2503.22618.

That paper reports a volume-law -> area-law entanglement transition of the
monitored Neel (scar) state at a critical *continuous-time* per-site rate
gamma_c ~ 0.013 (H coupling = 1). Our protocol applies dt of PXP evolution then
measures each site with probability p per step, so the equivalent continuous
rate is gamma = p / dt.

We reproduce their observable: evolve the single monitored Neel state under
local-Z measurement, record the steady-state half-chain entanglement S(p) for
several L, estimate the crossing p_c, and convert to gamma_c = p_c / dt.
"""

from __future__ import annotations

import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import PXPModel, diagonalize, entanglement_entropy


def propagator_from_spectrum(spec, dt):
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T


def measure_state(psi, occ, p, rng):
    L = occ.shape[0]
    for i in range(L):
        if rng.random() >= p:
            continue
        oi = occ[i]
        wt = np.abs(psi) ** 2
        p1 = float(wt[oi == 1].sum())
        if rng.random() < p1:
            keep = oi == 1; norm = p1
        else:
            keep = oi == 0; norm = 1.0 - p1
        if norm < 1e-15:
            continue
        psi = psi * keep
        psi /= np.sqrt(norm)
    return psi


def steady_entanglement(model, U, occ, psi0, p, n_steps, ntraj, cut, seed):
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(ntraj):
        psi = psi0.astype(complex).copy()
        for _ in range(n_steps):
            psi = U @ psi
            psi = measure_state(psi, occ, p, rng)
            psi /= np.linalg.norm(psi)
        vals.append(entanglement_entropy(model, psi, cut))
    return float(np.mean(vals)), float(np.std(vals) / np.sqrt(ntraj))


def main():
    dt = 0.6
    ntraj = 120
    n_steps = 40
    Ls = [10, 12, 14]
    ps = np.array([0.0, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.14])
    curves = {}
    print(f"monitored Neel-state half-chain entanglement (dt={dt})")
    for L in Ls:
        m = PXPModel(L)
        spec = diagonalize(m)
        U = propagator_from_spectrum(spec, dt)
        occ = np.array([m.n_diagonal(i) for i in range(L)])
        psi0 = m.neel_state(0)
        cut = L // 2
        S = []
        for p in ps:
            s, _ = steady_entanglement(m, U, occ, psi0, float(p), n_steps,
                                       ntraj, cut, seed=5)
            S.append(s)
        curves[L] = S
        print(f"  L={L}: S(p) = " + " ".join(f"{x:.2f}" for x in S))

    # estimate p_c: normalise each curve by its p=0 (volume) value and find where
    # the L-curves of S/(L) cross / collapse -- use the p where the spread across
    # L is minimal beyond the volume region (a simple crossing proxy).
    Sarr = {L: np.array(curves[L]) for L in Ls}
    norm = {L: Sarr[L] / (L / 2) for L in Ls}          # S per half-site
    spread = np.array([np.std([norm[L][b] for L in Ls]) for b in range(len(ps))])
    # crossing ~ argmin spread over the transition window (exclude p=0)
    b_cross = 1 + int(np.argmin(spread[1:]))
    p_c = float(ps[b_cross])
    gamma_c = p_c / dt

    print(f"\nestimated crossing p_c ~ {p_c:.3f}  ->  gamma_c = p_c/dt ~ {gamma_c:.3f}")
    print(f"arXiv:2503.22618 reports gamma_c ~ 0.013 "
          f"(continuous-time projective sigma^z)")
    print(f"ratio gamma_c(ours)/0.013 ~ {gamma_c/0.013:.1f}  "
          f"(protocol/estimator differ: stroboscopic per-step vs "
          f"continuous-time; crossing vs FSS)")

    os.makedirs("results", exist_ok=True)
    with open("results/gamma_mapping.json", "w") as f:
        json.dump(dict(dt=dt, ps=ps.tolist(), curves=curves,
                       p_c=p_c, gamma_c=gamma_c, gamma_c_ref=0.013), f, indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.5))
    for L in Ls:
        ax.plot(ps, curves[L], marker="o", label=f"L={L}")
    ax.axvline(p_c, color="k", ls=":", label=f"$p_c$≈{p_c:.3f} ($\\gamma_c$≈{gamma_c:.3f})")
    ax.set_xlabel("measurement rate p (per site per step)")
    ax.set_ylabel("steady-state half-chain entanglement S")
    ax.set_title("Monitored Neel-scar entanglement transition (γ = p/dt)")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("results/gamma_mapping.png", dpi=140)
    print("saved -> results/gamma_mapping.png")


if __name__ == "__main__":
    main()
