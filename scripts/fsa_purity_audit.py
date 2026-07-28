"""Verify referee finding B-1: does the Casimir variance of the scar rungs
track FSA-mode hybridization rather than scarring itself?

Builds the forward-scattering-approximation (FSA) tower from |Z2> with the
repo's own H = H+ + H- split (scarcode.su2), diagonalizes H in that
(L+1)-dimensional Krylov space, and for every FSA rung reports:

  - the rung energy,
  - the nearest exact eigenstate and its FSA-mode weight |<FSA|E>|^2,
  - Var J^2 of that exact eigenstate,
  - Var J^2 of the FSA vector itself,
  - the number of thermal partners within +-0.5 (energy-matchability).

Writes results/fsa_purity.json.
"""

import json
import os

import numpy as np

from scarcode import PXPModel, diagonalize, identify_scars
from scarcode.su2 import casimir, h_plus

L = 14
OUT = os.path.join(os.path.dirname(__file__), "..", "results",
                   "fsa_purity.json")


def main():
    model = PXPModel(L)
    spec = diagonalize(model)
    identify_scars(spec, L=L)
    Hp = h_plus(model)
    J2 = casimir(model)

    # FSA Krylov space: repeatedly apply H+ to |Z2>, Gram-Schmidt.
    z2 = model.neel_state()
    basis = [z2]
    v = z2
    for _ in range(L):
        v = Hp @ v
        for b in basis:
            v = v - (b @ v) * b
        n = np.linalg.norm(v)
        if n < 1e-10:
            break
        v = v / n
        basis.append(v)
    B = np.array(basis).T                      # (dim, n_fsa)
    H = model.hamiltonian()
    h_fsa = B.T @ (H @ B)
    w_fsa, u_fsa = np.linalg.eigh(h_fsa)
    fsa_states = B @ u_fsa                     # columns: FSA tower states

    def var_j2(vec):
        m1 = vec @ (J2 @ vec)
        m2 = vec @ (J2 @ (J2 @ vec))
        return float(m2 - m1 ** 2)

    rows = []
    for r in range(fsa_states.shape[1]):
        f = fsa_states[:, r]
        ov = np.abs(spec.vectors.T @ f) ** 2
        j = int(np.argmax(ov))
        n_partners = int(np.sum(
            (np.abs(spec.energies - w_fsa[r]) < 0.5) & (~spec.scar_mask)
            & (np.abs(spec.energies) > 0.3)))
        rows.append(dict(
            fsa_E=float(w_fsa[r]),
            eig_E=float(spec.energies[j]),
            fsa_weight=float(ov[j]),
            var_eig=var_j2(spec.vectors[:, j]),
            var_fsa=var_j2(f),
            in_tower=bool(spec.scar_mask[j]),
            n_thermal_partners=n_partners,
        ))
        print(f"rung E_FSA={w_fsa[r]:+7.3f}  eig E={spec.energies[j]:+7.3f} "
              f"w={ov[r] if False else ov[j]:.3f}  VarJ2(eig)={rows[-1]['var_eig']:8.2f} "
            f"VarJ2(FSA)={rows[-1]['var_fsa']:6.2f}  partners={n_partners}")

    json.dump(dict(L=L, rungs=rows), open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
