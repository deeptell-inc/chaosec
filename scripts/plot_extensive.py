"""Plot the extensive (k-qubit) code comparison across sizes."""
from __future__ import annotations
import glob, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    # only the plain local-monitoring files: extensive_L<size>.json
    # (skip the _collective/_operator variants, which belong to Table S8)
    files = [f for f in glob.glob("results/extensive_L*.json")
             if f.split("_L")[1].split(".")[0].isdigit()]
    files = sorted(files, key=lambda f: int(f.split("_L")[1].split(".")[0]))
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    colors = ["C0", "C2", "C3", "C4"]
    for f, c in zip(files, colors):
        d = json.load(open(f))
        rows = d["rows"]
        p = np.array([r["p"] for r in rows])
        sc = np.array([r["scar_density"] for r in rows])
        th = np.array([r["thermal_density"] for r in rows])
        ths = np.array([r["thermal_density_sd"] for r in rows])
        lbl = f"L={d['L']} (k={d['k']})"
        ax.plot(p, sc, "o-", color=c, label=f"scar {lbl}")
        ax.plot(p, th, "s--", color=c, alpha=0.6)
        ax.fill_between(p, th - ths, th + ths, color=c, alpha=0.15)
    ax.plot([], [], "ks--", alpha=0.6, label="thermal (same colour)")
    ax.set_xlabel("measurement rate p")
    ax.set_ylabel(r"protected-information density $S_R/k$")
    ax.set_title("Maximal (extensive) scar code loses to a same-dimension\n"
                 "thermal code at every size (local monitoring)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("results/extensive.png", dpi=140)
    print("saved -> results/extensive.png")


if __name__ == "__main__":
    main()
