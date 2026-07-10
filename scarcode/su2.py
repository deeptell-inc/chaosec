"""Emergent su(2) spectrum-generating algebra of the PXP scar tower.

Forward-scattering split of the PXP Hamiltonian H = H+ + H-, where H+ moves the
Neel state |Z2> toward the anti-Neel by removing excitations on even sites and
adding them on odd sites (H- is the Hermitian conjugate). From these,

    Jx = (H+ + H-)/2 = H/2,   Jy = (H+ - H-)/(2i),   Jz = [H+, H-]/2,
    J^2 = (H+ H- + H- H+)/2 + Jz^2.

If the algebra closed exactly, the (L+1)-state scar tower would be a single
su(2) multiplet and J^2 would be *constant* on it (a Casimir). For PXP the
algebra closes only approximately, so J^2 is approximately constant on the tower
-- i.e. the scar code is an approximate decoherence-free subspace (DFS) of a
J^2 measurement, while generic thermal states are spread over J and get
dephased. This module lets us test that DFS-rescue scenario.
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from .pxp import PXPModel


def h_plus(model: PXPModel) -> sp.csr_matrix:
    """Raising part H+ of the PXP forward-scattering split (constrained basis)."""
    rows, cols, data = [], [], []
    for a, s in enumerate(model.states):
        for i in range(model.L):
            if not model._neighbours_ground(s, i):
                continue
            bit = (s >> i) & 1
            if i % 2 == 0:
                # even site: sigma^-  (remove excitation)  requires bit==1
                if bit != 1:
                    continue
            else:
                # odd site: sigma^+  (add excitation)  requires bit==0
                if bit != 0:
                    continue
            t = s ^ (1 << i)
            b = model.index.get(t)
            if b is None:
                continue
            rows.append(b); cols.append(a); data.append(1.0)
    return sp.csr_matrix((data, (rows, cols)), shape=(model.dim, model.dim))


def casimir(model: PXPModel) -> np.ndarray:
    """Dense J^2 = (H+H- + H-H+)/2 + Jz^2 with Jz = [H+, H-]/2."""
    Hp = h_plus(model).toarray()
    Hm = Hp.conj().T
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        Jz = 0.5 * (Hp @ Hm - Hm @ Hp)
        J2 = 0.5 * (Hp @ Hm + Hm @ Hp) + Jz @ Jz
    return 0.5 * (J2 + J2.conj().T)          # symmetrise numerical noise


def check_split(model: PXPModel) -> float:
    """Return ||(H+ + H-) - H_PXP|| to validate the forward-scattering split."""
    Hp = h_plus(model).toarray()
    H = model.hamiltonian().toarray()
    return float(np.linalg.norm((Hp + Hp.conj().T) - H))
