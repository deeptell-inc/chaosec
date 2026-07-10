"""PXP model on a constrained (Rydberg-blockade) Hilbert space.

Conventions
-----------
- Chain of ``L`` sites, open boundary conditions (OBC) unless ``pbc=True``.
- Site basis: ``0`` = ground, ``1`` = Rydberg/excited.
- Blockade constraint: no two adjacent excitations (no ``11`` on neighbouring
  sites; also across the seam when ``pbc=True``).
- Hamiltonian ``H = sum_i P_{i-1} X_i P_{i+1}`` where ``P = |0><0|`` projects a
  neighbour onto its ground state; boundary neighbours are treated as absent
  (i.e. ``P`` -> identity).

The constrained basis has dimension ``F(L+2)`` (Fibonacci) for OBC.
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp


class PXPModel:
    """Constrained basis and PXP Hamiltonian for a spin chain of length ``L``."""

    def __init__(self, L: int, pbc: bool = False):
        self.L = int(L)
        self.pbc = bool(pbc)
        self.states = self._build_basis()          # list[int] bitmasks
        self.index = {s: i for i, s in enumerate(self.states)}
        self.dim = len(self.states)
        self._H = None

    # ------------------------------------------------------------------ basis
    def _allowed(self, s: int) -> bool:
        L = self.L
        # no adjacent excitations within the chain
        if s & (s << 1):
            return False
        # seam constraint for PBC: bit 0 and bit L-1 not both set
        if self.pbc and (s >> (L - 1)) & 1 and s & 1:
            return False
        return True

    def _build_basis(self) -> list[int]:
        return [s for s in range(1 << self.L) if self._allowed(s)]

    # ------------------------------------------------------------- observables
    def bit(self, s: int, i: int) -> int:
        """Return occupation (0/1) of site ``i`` in basis state ``s``."""
        return (s >> i) & 1

    def z_diagonal(self, i: int) -> np.ndarray:
        """Diagonal of the Pauli-Z operator on site ``i`` (Z|0>=+|0>, Z|1>=-|1>).

        Returned as a length-``dim`` real vector over the constrained basis.
        """
        return np.array([1.0 - 2.0 * self.bit(s, i) for s in self.states])

    def n_diagonal(self, i: int) -> np.ndarray:
        """Diagonal of the number operator n_i = |1><1| on site ``i``."""
        return np.array([float(self.bit(s, i)) for s in self.states], dtype=float)

    # ------------------------------------------------------------ hamiltonian
    def _neighbours_ground(self, s: int, i: int) -> bool:
        """True if both neighbours of site ``i`` are in the ground state."""
        L = self.L
        left = i - 1
        right = i + 1
        if self.pbc:
            left %= L
            right %= L
        if left >= 0 and self.bit(s, left):
            return False
        if right < L and self.bit(s, right):
            return False
        return True

    def hamiltonian(self) -> sp.csr_matrix:
        """Sparse PXP Hamiltonian in the constrained basis (real symmetric)."""
        if self._H is not None:
            return self._H
        rows, cols, data = [], [], []
        for a, s in enumerate(self.states):
            for i in range(self.L):
                if not self._neighbours_ground(s, i):
                    continue
                t = s ^ (1 << i)          # flip site i
                b = self.index.get(t)
                if b is None:             # flipped state left the constrained space
                    continue
                rows.append(b)
                cols.append(a)
                data.append(1.0)
        H = sp.csr_matrix((data, (rows, cols)), shape=(self.dim, self.dim))
        self._H = H
        return H

    # ---------------------------------------------------------- special states
    def neel_state(self, shift: int = 0) -> np.ndarray:
        """Return the Z2 (Neel) product state |1010...> as a basis vector.

        ``shift=0`` puts excitations on even sites, ``shift=1`` on odd sites.
        """
        mask = 0
        for i in range(self.L):
            if (i % 2) == (shift % 2):
                mask |= (1 << i)
        idx = self.index.get(mask)
        if idx is None:
            raise ValueError("Neel state not in constrained basis (check L/pbc).")
        v = np.zeros(self.dim)
        v[idx] = 1.0
        return v
