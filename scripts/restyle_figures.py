"""Regenerate the five main-text figures as publication-quality vector PDFs.

Reads the stored JSON results (no re-simulation), applies a uniform style
(single-column 3.4 in width, 8 pt fonts, Arial/Helvetica, stacked panels with
(a)/(b) labels), and writes results/<name>.pdf alongside the original PNGs.
"""

from __future__ import annotations

import json

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.5,
    "lines.linewidth": 1.0, "lines.markersize": 3.5,
    "axes.linewidth": 0.6, "grid.linewidth": 0.4, "grid.alpha": 0.3,
    "legend.framealpha": 0.9, "legend.handlelength": 1.6,
    "savefig.dpi": 300, "pdf.fonttype": 42,
})
W = 3.4  # single-column width (in)


def _load(p):
    with open(p) as f:
        return json.load(f)


def _panel_label(ax, s):
    # outside the axes (left-aligned title) so it can never collide with data
    ax.set_title(s, loc="left", fontsize=9, fontweight="bold", pad=3)


def fig_crossover():
    d = _load("results/corrected_crossover.json")
    ps = np.array(d["ps"])
    fig, axes = plt.subplots(2, 1, figsize=(W, 4.5), sharex=True)
    for ax, name, lab in [(axes[0], "localZ", "(a)"),
                          (axes[1], "collective", "(b)")]:
        s = d[name]
        tm, ts = np.array(s["tmean"]), np.array(s["tstd"])
        ax.plot(ps, s["scar"], "o-", color="C3", label="scar code")
        ax.plot(ps, tm, "s--", color="C0", label="thermal ensemble")
        ax.fill_between(ps, tm - ts, tm + ts, color="C0", alpha=0.25,
                        label=r"thermal $\pm1\sigma$")
        ax.set_ylabel(r"$C_R$")
        ax.grid(True)
        _panel_label(ax, lab)
    axes[0].legend(loc="lower left")   # curves run top-left -> bottom-right
    axes[1].set_xlabel("measurement rate $p$")
    fig.tight_layout(h_pad=0.6)
    fig.savefig("results/corrected_crossover.pdf")
    plt.close(fig)


def fig_scaling():
    d = _load("results/ensemble_scaling.json")
    l18 = _load("results/L18_check.json")
    rows = d["rows"]
    L = np.array([r["L"] for r in rows] + [l18["L"]])
    fig, ax = plt.subplots(figsize=(W, 2.6))
    ax.axhline(0, color="k", lw=0.6)
    for meas, c, mk, ls, lab in [("localZ", "0.35", "s", "--", "local $Z$"),
                                 ("collective", "C2", "o", "-", "collective")]:
        dv = np.array([r[meas]["dCR"] for r in rows]
                      + [l18["rows"][meas]["dCR"]])
        b = np.array([r[meas]["CR_therm_std"] for r in rows]
                     + [l18["rows"][meas]["CR_therm_std"]])
        ax.plot(L, dv, marker=mk, ls=ls, color=c, label=lab)
        ax.fill_between(L, dv - b, dv + b, color=c, alpha=0.18)
    ax.set_xlabel("system size $L$")
    ax.set_ylabel(r"$\Delta C_R$ at $p=0.10$")
    ax.set_xticks(L)
    ax.legend(loc="center left")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig("results/ensemble_scaling.pdf")
    plt.close(fig)


def fig_mechanism():
    d = _load("results/mechanism.json")
    pts = d["points"]
    SP = np.array([q[0] for q in pts])
    LK = np.array([q[1] for q in pts])
    CR = np.array([q[2] for q in pts])
    kinds = [q[3] for q in pts]
    SPs, lks, Cs = d["scar"]
    fig, axes = plt.subplots(2, 1, figsize=(W, 4.5))
    for ax, X, xlab, sx, lab in [
            (axes[0], SP, r"$Z$-basis participation $S_P$ (nats)", SPs, "(a)"),
            (axes[1], LK, r"logical leak $|\langle0_L|O|1_L\rangle|$", lks, "(b)")]:
        for kind, c, mk in [("eigen", "C0", "o"), ("product", "C1", "^")]:
            sel = [i for i, k in enumerate(kinds) if k == kind]
            ax.scatter(X[sel], CR[sel], c=c, marker=mk, s=14, alpha=0.85,
                       label=kind)
        ax.scatter([sx], [Cs], c="C3", marker="*", s=90, edgecolor="k",
                   linewidth=0.5, zorder=5, label="scar")
        ax.set_xlabel(xlab)
        ax.set_ylabel(r"collective $C_R$")
        ax.grid(True)
        _panel_label(ax, lab)
    # the S_P gap (no data between the product column and the eigen cluster)
    axes[0].legend(loc="lower center")
    fig.tight_layout(h_pad=0.8)
    fig.savefig("results/mechanism.pdf")
    plt.close(fig)


def fig_spin1():
    pxp = _load("results/dfs_rescue.json")["results"]
    s1 = _load("results/spin1_dfs_L6.json")
    k = 20  # thermal-ensemble size in the high-statistics spin-1 run
    fig, axes = plt.subplots(2, 1, figsize=(W, 4.5),
                             gridspec_kw={"height_ratios": [1.35, 1.0]})
    ax = axes[0]
    ax.axhline(0, color="k", lw=0.6)
    p_pxp = [r["p"] for r in pxp["J2"]]
    ax.plot(p_pxp, [r["dCR"] for r in pxp["J2"]], "o-", color="C0",
            label=r"PXP, $J^2$ (approx. scar)")
    for key, c, mk, ls, lab in [("operator", "C3", "s", "-",
                                 r"spin-1, $J^2$ (exact scar)"),
                                ("sites", "0.4", "^", "--",
                                 r"spin-1, local $S^z$")]:
        rows = s1[key]
        p = [r["p"] for r in rows]
        dv = np.array([r["dCR"] for r in rows])
        sem = np.array([r["CR_therm_sd"] for r in rows]) / np.sqrt(k)
        ax.errorbar(p, dv, yerr=sem, fmt=mk, ls=ls, color=c, capsize=2,
                    label=lab)
    ax.set_xlabel("measurement rate $p$")
    ax.set_ylabel(r"$\Delta C_R$")
    ax.set_ylim(-0.3, 1.05)           # headroom so the legend sits clear
    ax.legend(loc="upper left")
    ax.grid(True)
    _panel_label(ax, "(a)")
    ax = axes[1]
    vals = [32.5, max(s1["var_scar"], 1e-14)]
    bars = ax.bar(["PXP\n(approx.)", "spin-1\n(exact)"], vals,
                  color=["C0", "C3"], width=0.5)
    ax.set_yscale("log")
    ax.set_ylabel(r"scar $\mathrm{Var}\,J^2$")
    ax.set_ylim(1e-15, 5e3)          # headroom above the value labels
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 3,
                f"{v:.1f}" if v > 0.1 else r"$\sim10^{-13}$",
                ha="center", fontsize=7)
    ax.grid(True, axis="y")
    _panel_label(ax, "(b)")
    fig.tight_layout(h_pad=0.8)
    fig.savefig("results/spin1_rescue.pdf")
    plt.close(fig)


def fig_extensive():
    fig, ax = plt.subplots(figsize=(W, 2.8))
    for Lv, c in [(10, "C0"), (14, "C2"), (18, "C3")]:
        d = _load(f"results/extensive_L{Lv}.json")
        rows = d["rows"]
        p = np.array([r["p"] for r in rows])
        sc = np.array([r["scar_density"] for r in rows])
        th = np.array([r["thermal_density"] for r in rows])
        ts = np.array([r["thermal_density_sd"] for r in rows])
        ax.plot(p, sc, "o-", color=c, label=f"$L={Lv}$ ($k={d['k']}$)")
        ax.plot(p, th, "s--", color=c, alpha=0.6)
        ax.fill_between(p, th - ts, th + ts, color=c, alpha=0.15)
    ax.plot([], [], "ks--", alpha=0.6, label="thermal (same colour)")
    ax.set_xlabel("measurement rate $p$")
    ax.set_ylabel(r"density $S_R/k$")
    ax.legend(loc="lower left")        # curves run top-left -> bottom-right
    ax.grid(True)
    fig.tight_layout()
    fig.savefig("results/extensive.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig_crossover(); print("corrected_crossover.pdf")
    fig_scaling(); print("ensemble_scaling.pdf")
    fig_mechanism(); print("mechanism.pdf")
    fig_spin1(); print("spin1_rescue.pdf")
    fig_extensive(); print("extensive.pdf")
    print("done")
