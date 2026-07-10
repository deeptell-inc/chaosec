"""Plot finite-size scaling of Delta C_R from results/scaling.json."""

from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    with open("results/scaling.json") as f:
        d = json.load(f)
    rows = d["rows"]
    L = np.array([r["L"] for r in rows])

    def col(k):
        return np.array([r[k] for r in rows])

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.axhline(0, color="k", lw=0.8)
    ax.errorbar(L, col("dCR_local"), yerr=col("dCR_local_sem"),
                marker="s", ls="--", color="gray", label="local-Z (scar-therm)")
    ax.errorbar(L, col("dCR_coll"), yerr=col("dCR_coll_sem"),
                marker="o", color="C2", label="collective (scar-therm)")
    ax.errorbar(L, col("dCR_prod_coll"), yerr=col("dCR_prod_coll_sem"),
                marker="^", ls=":", color="C1",
                label="collective (product-therm) [control]")
    ax.set_xlabel("system size L")
    ax.set_ylabel(r"$\Delta C_R$ at $p=%.2f$" % d["p"])
    ax.set_title("Finite-size scaling of the scar protection advantage")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("results/scaling_L.png", dpi=140)
    print("saved -> results/scaling_L.png")


if __name__ == "__main__":
    main()
