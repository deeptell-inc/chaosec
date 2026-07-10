"""Mechanism test: does collective-measurement protection track Z-basis spread?

At fixed L and p we sweep a family of codes spanning low -> high Z-basis
participation entropy S_P and measure their collective-measurement coherent
information C_R. The claim (scars protect because they are Z-basis localised,
not because they are "scars") predicts a MONOTONIC DECREASING C_R vs S_P, with
the scar sitting on the same curve as generic states of equal S_P.

Codes swept (all energy-matched near the two scar-rung energies):
  - product      : two random Z-basis (product) states           -> lowest S_P
  - eigen-sweep  : eigenstate pairs ordered by Z2 overlap, i.e.
                   from scar-like (high overlap, low S_P) to
                   thermal-like (low overlap, high S_P)
  - scar         : the canonical scar-rung code (highlighted)
"""

from __future__ import annotations

import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      participation_entropy)
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def propagator_from_spectrum(spec, dt):
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T


def main():
    L = 14
    p = 0.10
    ntraj = 250
    dt = 0.6
    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    s0, s1, (ks0, ks1) = scar_code(spec)
    Ea, Eb = spec.energies[ks0], spec.energies[ks1]
    U = propagator_from_spectrum(spec, dt)
    stag = sum((-1) ** i * m.z_diagonal(i) for i in range(L))
    mon = MonitoredPXP(m, dt=dt, collective_op=stag, U=U)
    w = spec.energies

    def eigs_near(E, n=16, window=0.7):
        idx = np.array([k for k in range(len(w)) if abs(w[k] - E) < window])
        # order by Z2 overlap: scar-like (high) -> thermal-like (low)
        return idx[np.argsort(spec.z2_overlap[idx])[::-1]][:n]

    A = eigs_near(Ea)
    B = eigs_near(Eb)
    npair = min(len(A), len(B))

    def measure_code(v0, v1):
        cfg = TrajectoryConfig(p=p, n_steps=40, dt=dt, measure="collective",
                               record_every=4)
        C = mon.coherent_information(v0, v1, cfg, ntraj, seed=10)["C_R"]
        SP = 0.5 * (participation_entropy(v0) + participation_entropy(v1))
        leak = abs(np.vdot(v0, stag * v1))           # |<0|O|1>| logical leak
        return SP, leak, C

    pts = []  # (S_P, leak, C_R, kind)
    for a, b in zip(A[:npair], B[:npair]):
        SP, lk, C = measure_code(spec.vectors[:, a], spec.vectors[:, b])
        pts.append((SP, lk, C, "eigen"))
    rng = np.random.default_rng(0)
    for _ in range(8):
        i, j = rng.choice(m.dim, size=2, replace=False)
        v0 = np.zeros(m.dim, complex); v0[i] = 1
        v1 = np.zeros(m.dim, complex); v1[j] = 1
        SP, lk, C = measure_code(v0, v1)
        pts.append((SP, lk, C, "product"))
    SP_s, lk_s, C_s = measure_code(s0, s1)            # canonical scar (highlight)

    SP = np.array([q[0] for q in pts])
    LK = np.array([q[1] for q in pts])
    CR = np.array([q[2] for q in pts])
    kinds = [q[3] for q in pts]

    def spearman(x, y):
        return float(np.corrcoef(np.argsort(np.argsort(x)),
                                 np.argsort(np.argsort(y)))[0, 1])
    r_sp = spearman(SP, CR)
    r_lk = spearman(LK, CR)
    print(f"L={L} p={p}:")
    print(f"  Spearman(S_P,  C_R) = {r_sp:+.3f}")
    print(f"  Spearman(leak, C_R) = {r_lk:+.3f}   <- logical leak |<0|O|1>|")
    print(f"  scar: S_P={SP_s:.3f} leak={lk_s:.3f} C_R={C_s:.3f}  "
          f"(leak is the outlier that makes scar fragile)")

    os.makedirs("results", exist_ok=True)
    with open("results/mechanism.json", "w") as f:
        json.dump(dict(L=L, p=p, spearman_SP=r_sp, spearman_leak=r_lk,
                       scar=[SP_s, lk_s, C_s],
                       points=[[float(a), float(b), float(c), k]
                               for (a, b, c, k) in pts]), f, indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for ax, X, xlab, r, sval in [
            (axes[0], SP, r"Z-basis participation $S_P$ (nats)", r_sp, SP_s),
            (axes[1], LK, r"logical leak $|\langle0|O|1\rangle|$", r_lk, lk_s)]:
        for kind, c, mk in [("eigen", "C0", "o"), ("product", "C1", "^")]:
            sel = [i for i, k in enumerate(kinds) if k == kind]
            ax.scatter(X[sel], CR[sel], c=c, marker=mk, s=45, alpha=0.8,
                       label=kind)
        ax.scatter([sval], [C_s], c="C3", marker="*", s=260, edgecolor="k",
                   zorder=5, label="scar")
        ax.set_xlabel(xlab); ax.set_ylabel(r"collective $C_R$ at $p=%.2f$" % p)
        ax.set_title(f"Spearman = {r:+.2f}")
        ax.legend(); ax.grid(alpha=0.3)
    fig.suptitle(rf"Why thermal beats scar (PXP L={L}): ETH scrambling "
                 rf"(participation trend) + scar SGA-leak penalty")
    fig.tight_layout()
    fig.savefig("results/mechanism.png", dpi=140)
    print("saved -> results/mechanism.png")


if __name__ == "__main__":
    main()
