"""Schecter-Iadecola spin-1 XY magnet with EXACT su(2) quantum many-body scars.

H = J sum_i (Sx_i Sx_{i+1} + Sy_i Sy_{i+1}) + h sum_i Sz_i + D sum_i (Sz_i)^2

(PRL 123, 147201 (2019)). The tower |S_n> = (Q^+)^n |Omega> with
    Q^+ = sum_j (-1)^j (S_j^+)^2 ,   |Omega> = |m=-1>^{otimes L}
are EXACT eigenstates forming an exact su(2) multiplet of pseudospin J = L/2
(each site's {m=-1, m=+1} is a pseudospin-1/2; m=0 is outside the tower). Hence
the Casimir J^2 built from Q^+ is *exactly* constant on the tower with zero
variance on each scar -- the sharp contrast to PXP, whose approximate scars carry
large Casimir variance. This is the second model used to (i) test whether the
refutation (thermal > scar) generalizes and (ii) test whether an EXACT-su(2)
scar makes the J^2 decoherence-free-subspace rescue succeed.

Local basis index 0,1,2 <-> m = -1, 0, +1.
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp

SQ2 = np.sqrt(2.0)
# spin-1 matrices in basis (m=-1, 0, +1) = index (0, 1, 2)
SZ = np.diag([-1.0, 0.0, 1.0])
# raising S^+|m> ~ |m+1> maps lower index -> higher index (lower-triangular)
SP = np.array([[0, 0, 0], [SQ2, 0, 0], [0, SQ2, 0]], dtype=float)
SM = SP.T.copy()
SX = 0.5 * (SP + SM)
SY = -0.5j * (SP - SM)
SP2 = SP @ SP                                                        # (S^+)^2


class Spin1Scar:
    def __init__(self, L: int, J: float = 1.0, h: float = 1.0, D: float = 0.0):
        self.L = int(L)
        self.J, self.h, self.D = J, h, D
        self.dim = 3 ** self.L
        self._H = None

    # ------------------------------------------------------------- operators
    def _op_at(self, local: np.ndarray, j: int) -> sp.csr_matrix:
        mats = [sp.identity(3, format="csr")] * self.L
        mats[j] = sp.csr_matrix(local)
        out = mats[0]
        for k in range(1, self.L):
            out = sp.kron(out, mats[k], format="csr")
        return out

    def hamiltonian(self) -> sp.csr_matrix:
        if self._H is not None:
            return self._H
        L = self.L
        H = sp.csr_matrix((self.dim, self.dim), dtype=complex)
        Sx = [self._op_at(SX, j) for j in range(L)]
        Sy = [self._op_at(SY, j) for j in range(L)]
        Sz = [self._op_at(SZ, j) for j in range(L)]
        for j in range(L - 1):
            H = H + self.J * (Sx[j] @ Sx[j + 1] + Sy[j] @ Sy[j + 1])
        for j in range(L):
            H = H + self.h * Sz[j] + self.D * (Sz[j] @ Sz[j])
        H = 0.5 * (H + H.getH())
        self._H = H.real if np.allclose(H.imag.toarray(), 0) else H
        return self._H

    def q_plus(self) -> sp.csr_matrix:
        """Exact su(2) raising operator Q^+ = sum_j (-1)^j (S_j^+)^2."""
        Q = sp.csr_matrix((self.dim, self.dim), dtype=float)
        for j in range(self.L):
            Q = Q + ((-1) ** j) * self._op_at(SP2, j)
        return Q

    def omega(self) -> np.ndarray:
        v = np.zeros(self.dim)
        v[0] = 1.0                     # all sites in local index 0 = m=-1
        return v

    def tower(self) -> tuple[np.ndarray, np.ndarray]:
        """Return (energies, states) of the exact scar tower |S_n>, n=0..L."""
        Q = self.q_plus().toarray()
        H = self.hamiltonian().toarray()
        states, ens = [], []
        v = self.omega().astype(float)
        for n in range(self.L + 1):
            w = v.copy()
            nrm = np.linalg.norm(w)
            if nrm < 1e-12:
                break
            w = w / nrm
            states.append(w)
            ens.append(float(w @ (H @ w)))
            v = Q @ v                  # next rung (unnormalised)
        return np.array(ens), np.array(states).T   # states as columns

    def casimir(self) -> np.ndarray:
        r"""Properly-normalised su(2) Casimir J^2 (dense).

        Generators J^+ = Q^+/2, J^- = Q^-/2, J^z = Sz_tot/2 satisfy
        [J^z,J^\pm]=\pm J^\pm and [J^+,J^-]=2J^z, so J^2 = J_z^2 +
        (J^+J^- + J^-J^+)/2 is the Casimir and equals J(J+1)=(L/2)(L/2+1)
        on the exact scar tower (zero variance on every scar).
        """
        Jp = 0.5 * self.q_plus().toarray().astype(complex)
        Jm = Jp.conj().T
        Sztot = sum(self._op_at(SZ, j).toarray() for j in range(self.L))
        Jz = 0.5 * Sztot.astype(complex)
        # np.errstate guards benign FP-exception flags raised by some BLAS
        # backends (e.g. Apple Accelerate) during these dense matmuls.
        with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
            J2 = Jz @ Jz + 0.5 * (Jp @ Jm + Jm @ Jp)
        return 0.5 * (J2 + J2.conj().T)

    def sz_diagonals(self) -> np.ndarray:
        """Per-site S^z diagonals (L, dim) for local measurement."""
        return np.array([self._op_at(SZ, j).diagonal().real for j in range(self.L)])
