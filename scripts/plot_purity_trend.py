"""Publication figure: protection versus FSA purity (Nature-panel P1).

Plots the scar-minus-thermal coherent information at each energy-matchable
rung of the PXP tower against the rung's FSA-mode weight, for (a) local-Z
monitoring and (b) the multiplet-binned Casimir, from the cleaned-pool scan
results/pure_rung_dfs2.json.  This is the purity-resolved result the panel
asked to promote from a parenthetical to a figure.
"""

import json
import os

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
W = 3.4

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "..", "results", "pure_rung_dfs2.json")
OUT = os.path.join(HERE, "..", "results", "purity_trend.pdf")


def main():
    d = json.load(open(SRC))
    rows = [r for r in d["pairs"] if r.get("modes")]
    w = [r["fsa_weight"] for r in rows]
    fig, ax = plt.subplots(figsize=(W, 2.7))
    colors = {0.04: "C0", 0.08: "C1", 0.12: "C3"}
    ax.axhline(0, color="k", lw=0.6)
    for i, p in enumerate((0.04, 0.08, 0.12)):
        y = [r["modes"]["localZ"][i]["dCR"] for r in rows]
        ax.plot(w, y, "o-", color=colors[p], label=f"$p={p:.2f}$")
    ax.annotate("canonical rung", (w[0], -0.069),
                xytext=(w[0] + 0.015, -0.095), fontsize=6.5, ha="left",
                arrowprops=dict(arrowstyle="-", lw=0.5))
    ax.set_ylabel(r"$\Delta C_R$ (scar $-$ thermal), local $Z$")
    ax.grid(True)
    ax.legend(loc="upper left")
    ax.set_xlabel(r"FSA weight $w$ of the scar rung")
    fig.tight_layout(pad=0.4)
    fig.savefig(OUT)
    print("saved ->", OUT)


if __name__ == "__main__":
    main()
