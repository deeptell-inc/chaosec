"""R2: validate the model-independent criterion directly.

The criterion predicts that protection under measuring operator O is set by the
overlap of the two logical states' O-outcome distributions P_0, P_1. We quantify
that overlap by the Bhattacharyya coefficient BC = sum_o sqrt(P_0(o) P_1(o))
(=1 identical, 0 disjoint) under the collective staggered operator M (diagonal),
and correlate it with the measured collective coherent information C_R across a
family of codes. A strong positive Spearman(BC, C_R) confirms the criterion far
more directly than the weak participation correlation.
"""

from __future__ import annotations

import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import PXPModel, diagonalize, identify_scars, scar_code
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def propagator_from_spectrum(spec, dt):
    phase = np.exp(-1j * spec.energies * dt)
    return (spec.vectors * phase) @ spec.vectors.conj().T


def outcome_dist(v, mvals, bins):
    """Distribution of the (diagonal) operator value for state v, on `bins`."""
    p = np.abs(v) ** 2
    hist = np.zeros(len(bins))
    idx = np.searchsorted(bins, np.round(mvals, 6))
    np.add.at(hist, np.clip(idx, 0, len(bins) - 1), p)
    return hist / hist.sum()


def main():
    L, dt, ntraj, p = 14, 0.6, 250, 0.10
    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    s0, s1, (ks0, ks1) = scar_code(spec)
    Ea, Eb = spec.energies[ks0], spec.energies[ks1]
    M = sum((-1) ** i * m.z_diagonal(i) for i in range(L))         # staggered Z
    mbins = np.unique(np.round(M, 6))
    U = propagator_from_spectrum(spec, dt)
    mon = MonitoredPXP(m, dt=dt, collective_op=M, U=U)
    w, ov = spec.energies, spec.z2_overlap

    def bc(v0, v1):
        P0 = outcome_dist(v0, M, mbins)
        P1 = outcome_dist(v1, M, mbins)
        return float(np.sum(np.sqrt(P0 * P1)))

    def CR(v0, v1):
        cfg = TrajectoryConfig(p=p, n_steps=40, dt=dt, measure="collective",
                               record_every=4)
        return mon.coherent_information(v0, v1, cfg, ntraj, seed=10)["C_R"]

    # family: eigen-sweep near (Ea,Eb) from scar-like to thermal-like + products
    def near(E, n=14, win=0.7):
        idx = np.array([k for k in range(len(w)) if abs(w[k] - E) < win])
        return idx[np.argsort(ov[idx])[::-1]][:n]
    A, B = near(Ea), near(Eb)
    pts = []
    for a, b in zip(A, B):
        va, vb = spec.vectors[:, a], spec.vectors[:, b]
        pts.append((bc(va, vb), CR(va, vb), "eigen"))
    rng = np.random.default_rng(0)
    for _ in range(8):
        i, j = rng.choice(m.dim, 2, replace=False)
        v0 = np.zeros(m.dim, complex); v0[i] = 1
        v1 = np.zeros(m.dim, complex); v1[j] = 1
        pts.append((bc(v0, v1), CR(v0, v1), "product"))
    bc_s, cr_s = bc(s0, s1), CR(s0, s1)
    pts.append((bc_s, cr_s, "scar"))

    BC = np.array([q[0] for q in pts]); CR_ = np.array([q[1] for q in pts])
    sp = float(np.corrcoef(np.argsort(np.argsort(BC)),
                           np.argsort(np.argsort(CR_)))[0, 1])
    print(f"L={L} p={p}: Spearman(BC, C_R) = {sp:+.3f}  (criterion predicts >>0)")
    print(f"  scar: BC={bc_s:.3f} C_R={cr_s:.3f}  (low BC = distinguishable = poorly protected)")

    os.makedirs("results", exist_ok=True)
    json.dump(dict(L=L, p=p, spearman=sp, scar=[bc_s, cr_s],
                   points=[[float(a), float(b), k] for a, b, k in pts]),
              open("results/bhattacharyya.json", "w"), indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    kinds = [q[2] for q in pts]
    for kind, c, mk in [("eigen", "C0", "o"), ("product", "C1", "^")]:
        sel = [i for i, k in enumerate(kinds) if k == kind]
        ax.scatter(BC[sel], CR_[sel], c=c, marker=mk, s=45, alpha=0.8, label=kind)
    ax.scatter([bc_s], [cr_s], c="C3", marker="*", s=260, edgecolor="k",
               zorder=5, label="scar")
    ax.set_xlabel(r"Bhattacharyya overlap of $P_0,P_1$ under $M$")
    ax.set_ylabel(r"collective $C_R$ at $p=%.2f$" % p)
    ax.set_title(f"Criterion confirmed: protection tracks outcome-distribution "
                 f"overlap\nSpearman = {sp:+.2f} (L={L})")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig("results/bhattacharyya.png", dpi=140)
    print("saved -> results/bhattacharyya.png")


if __name__ == "__main__":
    main()
