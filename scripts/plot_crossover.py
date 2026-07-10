"""Plot C_R(p) scar vs thermal for local-Z and collective monitoring.

Reads results/scan_localZ_L{L}.json and results/scan_collective_L{L}.json and
produces results/crossover_L{L}.png showing that the scar advantage Delta C_R is
~0 for local noise but positive for collective noise.
"""

from __future__ import annotations

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load(path):
    with open(path) as f:
        d = json.load(f)
    rows = d["rows"]
    p = np.array([r["p"] for r in rows])
    return d["meta"], p, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=14)
    args = ap.parse_args()
    L = args.L

    _, p, loc = load(f"results/scan_localZ_L{L}.json")
    _, _, col = load(f"results/scan_collective_L{L}.json")

    def col_of(rows, key):
        return np.array([r[key] for r in rows])

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # panel 1: local Z
    ax = axes[0]
    ax.plot(p, col_of(loc, "CR_scar"), "o-", label="scar", color="C3")
    ax.plot(p, col_of(loc, "CR_thermal"), "s--", label="thermal", color="C0")
    ax.set_title("local-Z monitoring")
    ax.set_xlabel("measurement rate p"); ax.set_ylabel(r"$C_R=\langle S_R\rangle$")
    ax.legend(); ax.grid(alpha=0.3)

    # panel 2: collective
    ax = axes[1]
    ax.plot(p, col_of(col, "CR_scar"), "o-", label="scar", color="C3")
    ax.plot(p, col_of(col, "CR_thermal"), "s--", label="thermal", color="C0")
    ax.set_title("collective (staggered-Z) monitoring")
    ax.set_xlabel("measurement rate p"); ax.set_ylabel(r"$C_R=\langle S_R\rangle$")
    ax.legend(); ax.grid(alpha=0.3)

    # panel 3: advantage
    ax = axes[2]
    ax.axhline(0, color="k", lw=0.8)
    ax.plot(p, col_of(loc, "CR_scar") - col_of(loc, "CR_thermal"),
            "o-", label="local Z", color="gray")
    ax.plot(p, col_of(col, "CR_scar") - col_of(col, "CR_thermal"),
            "o-", label="collective", color="C2")
    ax.set_title(r"scar advantage $\Delta C_R$")
    ax.set_xlabel("measurement rate p"); ax.set_ylabel(r"$\Delta C_R$")
    ax.legend(); ax.grid(alpha=0.3)

    fig.suptitle(f"Scar vs thermal information protection (PXP, L={L})")
    fig.tight_layout()
    out = f"results/crossover_L{L}.png"
    fig.savefig(out, dpi=140)
    print("saved ->", out)


if __name__ == "__main__":
    main()
