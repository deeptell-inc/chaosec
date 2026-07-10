"""Static Knill-Laflamme (KL) diagnostics for a two-dimensional logical code.

For a code spanned by ``{|0_L>, |1_L>}`` and an error set ``{E_a}``, exact
correctability requires the KL conditions ``<i|E_a^dag E_b|j> = C_ab delta_ij``.
We probe the physically relevant *local dephasing / measurement* error set
``E_i = Z_i`` (single-site Pauli-Z), whose Kraus projectors ``(I +/- Z_i)/2``
generate a local Z-basis measurement. Two quantities control detectability of a
single-site error:

- ``u_i = <0|Z_i|1>``          (logical off-diagonal leak; must vanish),
- ``d_i = <0|Z_i|0> - <1|Z_i|1>`` (logical distinguishability; must vanish).

The scalar violation aggregates these over sites. A *good* code (small eps) is
one whose logical information is invisible to any single local measurement --
exactly the ETH => approximate-QEC statement of arXiv:2510.26758.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .pxp import PXPModel


@dataclass
class KLReport:
    eps_rms: float             # RMS over sites of the per-site KL violation
    eps_max: float             # worst single-site violation
    offdiag_rms: float         # RMS of |<0|Z_i|1>|
    diagdiff_rms: float        # RMS of |<0|Z_i|0> - <1|Z_i|1>|
    per_site_offdiag: np.ndarray
    per_site_diagdiff: np.ndarray


def kl_local_z(model: PXPModel, logical0: np.ndarray, logical1: np.ndarray
               ) -> KLReport:
    """Knill-Laflamme violation of a 2-dim code under the local-Z error set."""
    v0 = logical0
    v1 = logical1
    L = model.L
    offdiag = np.empty(L)
    diagdiff = np.empty(L)
    for i in range(L):
        z = model.z_diagonal(i)                      # diagonal of Z_i
        u = np.vdot(v0, z * v1)                       # <0|Z_i|1>
        e00 = np.vdot(v0, z * v0).real               # <0|Z_i|0>
        e11 = np.vdot(v1, z * v1).real               # <1|Z_i|1>
        offdiag[i] = abs(u)
        diagdiff[i] = abs(e00 - e11)
    per_site = 2.0 * offdiag ** 2 + diagdiff ** 2
    return KLReport(
        eps_rms=float(np.sqrt(per_site.mean())),
        eps_max=float(np.sqrt(per_site.max())),
        offdiag_rms=float(np.sqrt((offdiag ** 2).mean())),
        diagdiff_rms=float(np.sqrt((diagdiff ** 2).mean())),
        per_site_offdiag=offdiag,
        per_site_diagdiff=diagdiff,
    )
