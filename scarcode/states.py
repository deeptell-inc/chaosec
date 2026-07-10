"""Eigenstate classification (scar vs thermal) and code-space construction.

A logical qubit is encoded in a two-dimensional subspace spanned by two
orthonormal eigenstates of the PXP Hamiltonian:

- **scar code**: two adjacent states of the ``Z2`` scar tower near mid-spectrum;
- **thermal code**: two adjacent generic (thermal) eigenstates near mid-spectrum.

The scar tower is identified as the eigenstates with anomalously large overlap
on the Neel state ``|Z2>`` (the standard forward-scattering fingerprint).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .pxp import PXPModel


@dataclass
class Spectrum:
    energies: np.ndarray      # (dim,)
    vectors: np.ndarray       # (dim, dim), column k is eigenvector k
    z2_overlap: np.ndarray    # (dim,) |<Z2|E_k>|^2 (even-shift Neel)
    scar_mask: np.ndarray     # (dim,) bool, True for scar-tower members


def diagonalize(model: PXPModel) -> Spectrum:
    H = model.hamiltonian().toarray()
    w, V = np.linalg.eigh(H)
    z2 = model.neel_state(0)
    ov = np.abs(V.T @ z2) ** 2
    return Spectrum(energies=w, vectors=V, z2_overlap=ov,
                    scar_mask=np.zeros(len(w), dtype=bool))


def identify_scars(spec: Spectrum, n_tower: int | None = None,
                   L: int | None = None) -> np.ndarray:
    """Flag the ``L+1`` scar-tower eigenstates by top Z2 overlap.

    The PXP ``Z2`` tower has ``L+1`` members. We select them as the eigenstates
    with the largest ``|<Z2|E>|^2``. Returns a boolean mask (also stored on
    ``spec.scar_mask``).
    """
    if n_tower is None:
        if L is None:
            raise ValueError("provide n_tower or L")
        n_tower = L + 1
    idx = np.argsort(spec.z2_overlap)[::-1][:n_tower]
    mask = np.zeros(len(spec.energies), dtype=bool)
    mask[idx] = True
    spec.scar_mask = mask
    return mask


def scar_rungs(spec: Spectrum, e_min: float = 0.8, min_gap: float = 0.8,
               n: int = 2) -> list[int]:
    """Greedily select ``n`` scar-tower rungs at positive energy.

    Picks the highest ``Z2``-overlap eigenstates with ``E > e_min`` subject to a
    minimum pairwise energy gap ``min_gap`` (so each pick is a distinct rung,
    not a near-degenerate contaminant). Positive energies are used to stay clear
    of the exponentially degenerate ``E=0`` zero-mode manifold.
    """
    w = spec.energies
    pos = np.where(w > e_min)[0]
    order = pos[np.argsort(spec.z2_overlap[pos])[::-1]]
    chosen: list[int] = []
    for k in order:
        if all(abs(w[k] - w[c]) > min_gap for c in chosen):
            chosen.append(int(k))
        if len(chosen) == n:
            break
    if len(chosen) < n:
        raise ValueError("could not find enough distinct scar rungs")
    return chosen


def scar_code(spec: Spectrum) -> tuple[np.ndarray, np.ndarray, tuple[int, int]]:
    """Return (|0_L>, |1_L>, (k0,k1)) from two distinct positive-energy rungs."""
    k0, k1 = scar_rungs(spec, n=2)
    return spec.vectors[:, k0].copy(), spec.vectors[:, k1].copy(), (k0, k1)


def thermal_code(spec: Spectrum, target_energies: tuple[float, float],
                 z2_cut: float = 0.02, e_floor: float = 0.3
                 ) -> tuple[np.ndarray, np.ndarray, tuple[int, int]]:
    """Return (|0_L>, |1_L>, (k0,k1)): thermal states energy-matched to targets.

    For each target energy we pick the nearest generic (non-scar, small ``Z2``
    overlap) eigenstate away from the ``E=0`` zero-mode sea (``|E|>e_floor``).
    Sharing the target energies with :func:`scar_code` removes the energy
    mismatch confound, isolating the scar-vs-thermal character.
    """
    w = spec.energies
    pool = np.array([k for k in range(len(w))
                     if spec.z2_overlap[k] < z2_cut and abs(w[k]) > e_floor])
    if pool.size < 2:
        raise ValueError("thermal pool too small; relax z2_cut/e_floor")
    picks: list[int] = []
    for E in target_energies:
        cand = pool[np.argsort(np.abs(w[pool] - E))]
        for k in cand:
            if k not in picks:
                picks.append(int(k))
                break
    k0, k1 = picks[0], picks[1]
    return spec.vectors[:, k0].copy(), spec.vectors[:, k1].copy(), (k0, k1)


def thermal_ensemble(spec: Spectrum, target_energies: tuple[float, float],
                     window: float = 0.4, kmax: int = 30, z2_cut: float = 0.02,
                     e_floor: float = 0.3, seed: int = 0
                     ) -> list[tuple[np.ndarray, np.ndarray]]:
    """Return up to ``kmax`` thermal code pairs energy-matched to the targets.

    For each target energy we collect all generic (non-scar, small ``Z2``
    overlap) eigenstates within ``+/- window``; a code pair draws one state from
    each window. Averaging ``C_R`` over the returned pairs gives a *typical
    thermal* baseline with an error band, replacing the single arbitrary pair.
    """
    w = spec.energies
    Ea, Eb = target_energies

    def pool(E):
        return np.array([k for k in range(len(w))
                         if not spec.scar_mask[k]
                         and spec.z2_overlap[k] < z2_cut
                         and abs(w[k]) > e_floor
                         and abs(w[k] - E) < window])

    pa, pb = pool(Ea), pool(Eb)
    if pa.size == 0 or pb.size == 0:
        raise ValueError("empty thermal window; widen `window`")
    rng = np.random.default_rng(seed)
    pairs = [(int(a), int(b)) for a in pa for b in pb if a != b]
    rng.shuffle(pairs)
    pairs = pairs[:kmax]
    return [(spec.vectors[:, a].copy(), spec.vectors[:, b].copy())
            for a, b in pairs]


def participation_entropy(state: np.ndarray, base: str = "e") -> float:
    """Shannon participation entropy of ``state`` in the (computational) basis.

    Since constrained-basis vectors live in the Z (product) basis, this is the
    spread of the state across measurement-basis configurations:
    ``S_P = -sum_i |c_i|^2 log |c_i|^2``. Larger ``S_P`` => more Z-basis spread
    => (empirically) more dephasing under collective Z measurement.
    """
    p = np.abs(state) ** 2
    p = p[p > 1e-14]
    log = np.log2 if base == "2" else np.log
    return float(-np.sum(p * log(p)))


# --------------------------------------------------------------- entanglement
def embed_full(model: PXPModel, state: np.ndarray) -> np.ndarray:
    """Embed a constrained-basis vector into the full ``2**L`` Hilbert space."""
    full = np.zeros(1 << model.L, dtype=complex)
    for amp, s in zip(state, model.states):
        full[s] = amp
    return full


def entanglement_entropy(model: PXPModel, state: np.ndarray, cut: int) -> float:
    """von Neumann entropy (bits) across a bipartition after site ``cut``.

    Sites ``[0, cut)`` form subsystem A, ``[cut, L)`` form B. The state is
    embedded into the full ``2**L`` space so the bipartition is a plain reshape.
    """
    full = embed_full(model, state)
    LA = cut
    LB = model.L - cut
    mat = full.reshape(1 << LA, 1 << LB)
    s = np.linalg.svd(mat, compute_uv=False)
    p = s ** 2
    p = p[p > 1e-14]
    return float(-np.sum(p * np.log2(p)))
