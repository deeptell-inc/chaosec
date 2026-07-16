"""B: a single predictor that collapses C_R across codes, measurements, models.

The two-channel criterion is captured by ONE exact, Monte-Carlo-free scalar:
the reference entropy that survives a SINGLE projective measurement of the
operator O on the initial code,

    s1(O) = sum_g q_g S(rho_R^g),   rho_R^g[a,b] = <v_b|Pi_g|v_a> / (2 q_g),
    q_g = (<v_0|Pi_g|v_0> + <v_1|Pi_g|v_1>)/2,

where Pi_g are the spectral projectors of O (grouped eigenvalues). s1=1 means the
measurement cannot resolve the code (a decoherence-free subspace); s1=0 means it
fully reads it out. It automatically folds in BOTH channels: eigenvalue
distinguishability (variance) AND non-invariance (leak).

We compute s1(O) exactly and the monitored steady-state C_R(O) dynamically for a
family of codes and several global operators, in both the PXP and the spin-1
model, and test whether C_R collapses onto a single monotone function of s1.
"""

from __future__ import annotations

import json
import os

import numpy as np

np.seterr(all="ignore")

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code)
from scarcode.su2 import casimir as pxp_casimir
from scarcode.spin1 import Spin1Scar
from scarcode.monitor import MonitoredPXP, TrajectoryConfig


def _binent(vals):
    p = np.clip(vals.real, 0, 1)
    p = p[p > 1e-14]
    return float(-np.sum(p * np.log2(p)))


def s1_predictor(v0, v1, O, tol=1e-6):
    """Exact surviving reference entropy after one projective O-measurement."""
    w, V = np.linalg.eigh(O)
    a0 = V.conj().T @ v0
    a1 = V.conj().T @ v1
    # group eigenvalues
    groups, cur = [], [0]
    for k in range(1, len(w)):
        if w[k] - w[k - 1] > tol:
            groups.append(cur); cur = []
        cur.append(k)
    groups.append(cur)
    s = 0.0
    for g in groups:
        idx = np.array(g)
        m00 = float(np.sum(np.abs(a0[idx]) ** 2))
        m11 = float(np.sum(np.abs(a1[idx]) ** 2))
        m10 = complex(np.sum(np.conj(a1[idx]) * a0[idx]))
        q = 0.5 * (m00 + m11)
        if q < 1e-15:
            continue
        rho = np.array([[m00, np.conj(m10)], [m10, m11]]) / (2 * q)
        s += q * _binent(np.linalg.eigvalsh(rho))
    return s


def cr_dynamic(mon, v0, v1, p, measure, ntraj=150, dt=0.6):
    cfg = TrajectoryConfig(p=p, n_steps=40, dt=dt, measure=measure,
                           record_every=4)
    return mon.coherent_information(v0, v1, cfg, ntraj, seed=10)["C_R"]


def pxp_points(p=0.10):
    L = 14
    m = PXPModel(L)
    spec = diagonalize(m)
    identify_scars(spec, L=L)
    s0, s1c, (ks0, ks1) = scar_code(spec)
    Ea, Eb = spec.energies[ks0], spec.energies[ks1]
    w, ov = spec.energies, spec.z2_overlap
    U = (spec.vectors * np.exp(-1j * w * 0.6)) @ spec.vectors.conj().T

    def near(E, n=10, win=0.7):
        idx = np.array([k for k in range(len(w)) if abs(w[k] - E) < win])
        return idx[np.argsort(ov[idx])[::-1]][:n]
    A, B = near(Ea), near(Eb)
    codes = [(spec.vectors[:, a], spec.vectors[:, b], "eigen")
             for a, b in zip(A, B)]
    rng = np.random.default_rng(0)
    for _ in range(4):
        i, j = rng.choice(m.dim, 2, replace=False)
        e0 = np.zeros(m.dim, complex); e0[i] = 1
        e1 = np.zeros(m.dim, complex); e1[j] = 1
        codes.append((e0, e1, "product"))
    codes.append((s0, s1c, "scar"))

    stag = np.diag(sum((-1) ** i * m.z_diagonal(i) for i in range(L)))
    unif = np.diag(sum(m.z_diagonal(i) for i in range(L)))
    J2 = pxp_casimir(m)
    ops = {"staggered": (stag, "operator"), "uniform": (unif, "operator"),
           "casimir": (J2, "operator")}
    rows = []
    for oname, (O, mode) in ops.items():
        mon = MonitoredPXP(m, dt=0.6, U=U, operator=O)
        for v0, v1, kind in codes:
            rows.append(dict(model="PXP", op=oname, kind=kind,
                             s1=s1_predictor(v0, v1, O),
                             CR=cr_dynamic(mon, v0, v1, p, "operator")))
        print(f"  PXP/{oname}: done ({len(codes)} codes)", flush=True)
    return rows


def spin1_points(p=0.10):
    L = 6
    sp = Spin1Scar(L, h=1.0, D=0.1)
    H = sp.hamiltonian().toarray()
    w, V = np.linalg.eigh(H)
    ens, tw = sp.tower()
    J2 = sp.casimir()
    U = (V * np.exp(-1j * w * 0.6)) @ V.conj().T
    tower_ov = np.max(np.abs(V.conj().T @ tw) ** 2, axis=1)
    is_tower = tower_ov > 0.9
    order = np.argsort(np.abs(ens))
    codes = [(tw[:, order[0]], tw[:, order[1]], "scar")]
    Ea, Eb = ens[order[0]], ens[order[1]]
    pool = [k for k in range(len(w)) if not is_tower[k] and abs(w[k]) < 4]
    rng = np.random.default_rng(1)
    for _ in range(9):
        a, b = rng.choice(pool, 2, replace=False)
        codes.append((V[:, a], V[:, b], "eigen"))
    stag = np.diag(sum((-1) ** i * sp.sz_diagonals()[i] for i in range(L)))
    ops = {"casimir": J2, "staggered": stag}
    rows = []
    for oname, O in ops.items():
        mon = MonitoredPXP(sp, dt=0.6, U=U, operator=O)
        for v0, v1, kind in codes:
            rows.append(dict(model="spin1", op=oname, kind=kind,
                             s1=s1_predictor(v0, v1, O),
                             CR=cr_dynamic(mon, v0, v1, p, "operator")))
        print(f"  spin1/{oname}: done ({len(codes)} codes)", flush=True)
    return rows


def main():
    print("computing predictor collapse (p=0.10)...", flush=True)
    rows = pxp_points() + spin1_points()
    s1 = np.array([r["s1"] for r in rows])
    CR = np.array([r["CR"] for r in rows])
    sp = float(np.corrcoef(np.argsort(np.argsort(s1)),
                           np.argsort(np.argsort(CR)))[0, 1])
    pear = float(np.corrcoef(s1, CR)[0, 1])
    print(f"\nN={len(rows)} points  Spearman(s1,C_R)={sp:+.3f}  Pearson={pear:+.3f}")

    os.makedirs("results", exist_ok=True)
    json.dump(dict(p=0.10, spearman=sp, pearson=pear, rows=rows),
              open("results/predictor.json", "w"), indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    styles = {("PXP", "staggered"): ("C0", "o"), ("PXP", "uniform"): ("C1", "o"),
              ("PXP", "casimir"): ("C2", "o"), ("spin1", "casimir"): ("C3", "s"),
              ("spin1", "staggered"): ("C4", "s")}
    for (model, op), (c, mk) in styles.items():
        sel = [i for i, r in enumerate(rows) if r["model"] == model and r["op"] == op]
        if sel:
            ax.scatter(s1[sel], CR[sel], c=c, marker=mk, s=45, alpha=0.85,
                       label=f"{model}/{op}")
    xs = np.linspace(0, 1, 50)
    ax.plot(xs, xs, "k--", lw=0.8, alpha=0.5, label="$C_R=s_1$ (guide)")
    ax.set_xlabel(r"single-measurement predictor $s_1(O)$ (exact)")
    ax.set_ylabel(r"monitored $C_R$ at $p=0.10$ (dynamical)")
    ax.set_title(f"One predictor collapses protection across codes,\n"
                 f"measurements, and models  (Spearman={sp:+.2f}, N={len(rows)})")
    ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig("results/predictor.png", dpi=140)
    print("saved -> results/predictor.png")


if __name__ == "__main__":
    main()
