"""Monitored PXP dynamics and reference-qubit coherent information.

A logical qubit is maximally entangled with a reference ``R``:

    |Psi(0)> = (|0>_R |0_L> + |1>_R |1_L>) / sqrt(2).

The system ``Q`` evolves under alternating PXP Hamiltonian steps and random
projective measurements; the reference is inert. Per quantum trajectory the
joint ``RQ`` state stays pure, so the reference entanglement entropy
``S_R = -Tr rho_R log2 rho_R`` in [0,1] measures how much logical information
survives. Its trajectory average

    C_R(p) = < S_R >_traj

is the single-qubit coherent-information order parameter of the monitored
channel (Gullans-Huse purification): ``C_R ~ 1`` recoverable, ``C_R ~ 0`` lost.

The joint state is stored as ``phi`` of shape ``(dim_Q, 2)`` with column ``r``
holding ``<r_R| Psi>`` (an unnormalised system vector).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm

from .pxp import PXPModel


def propagator(model: PXPModel, dt: float) -> np.ndarray:
    """Dense unitary ``exp(-i H dt)`` in the constrained basis."""
    H = model.hamiltonian().toarray()
    return expm(-1j * H * dt)


def _reference_entropy(phi: np.ndarray) -> float:
    """S_R (bits) from the joint state ``phi`` (shape (dim,2))."""
    rho_r = phi.conj().T @ phi                 # 2x2 Hermitian, trace 1
    lam = np.linalg.eigvalsh(rho_r).real
    lam = lam[lam > 1e-14]
    return float(-np.sum(lam * np.log2(lam)))


@dataclass
class TrajectoryConfig:
    p: float                    # measurement probability per step (per site for localZ)
    n_steps: int                # number of (evolve + measure) steps
    dt: float = 1.0             # Hamiltonian time per step
    measure: str = "localZ"     # "localZ", "collective", or "block"
    block_size: int = 1         # support size for "block" measurement (1..L)
    record_every: int = 1       # record S_R every this many steps


class MonitoredPXP:
    """Trajectory sampler for a monitored PXP logical qubit."""

    def __init__(self, model: PXPModel, dt: float = 1.0,
                 collective_op: np.ndarray | None = None,
                 U: np.ndarray | None = None,
                 operator: np.ndarray | None = None, op_tol: float = 1e-6,
                 site_diags: np.ndarray | None = None):
        self.model = model
        self.dt = dt
        self.U = U if U is not None else propagator(model, dt)
        # qubit-specific precomputes (skipped for non-qubit models like spin-1)
        if hasattr(model, "n_diagonal"):
            self.occ = np.array([model.n_diagonal(i) for i in range(model.L)])
            self.zdiag = np.array([model.z_diagonal(i) for i in range(model.L)])
        else:
            self.occ = self.zdiag = None
        # general per-site diagonal operators for "sites" measurement (e.g.
        # spin-1 S^z_i); defaults to the qubit z-diagonals when available.
        self.site_diags = (site_diags if site_diags is not None else self.zdiag)
        # optional collective measurement operator diagonal (dim,)
        self.collective_op = collective_op
        # optional general Hermitian measurement operator (measure="operator"):
        # precompute eigenbasis and integer eigenvalue labels for projection.
        self.op_V = None
        self.op_labels = None
        if operator is not None:
            wO, VO = np.linalg.eigh(operator)
            lab = np.zeros(len(wO), dtype=int)
            cur = 0
            for k in range(1, len(wO)):
                if wO[k] - wO[k - 1] > op_tol:
                    cur += 1
                lab[k] = cur
            self.op_V = VO
            self.op_labels = lab

    # ------------------------------------------------------------ measurement
    def _measure_localZ(self, phi: np.ndarray, p: float, rng) -> np.ndarray:
        L = self.model.L
        for i in range(L):
            if rng.random() >= p:
                continue
            occ_i = self.occ[i]
            weight = (np.abs(phi) ** 2).sum(axis=1)   # sum over code columns
            p1 = float(weight[occ_i == 1].sum())      # prob(site i excited)
            if rng.random() < p1:
                keep = occ_i == 1
                norm = p1
            else:
                keep = occ_i == 0
                norm = 1.0 - p1
            if norm < 1e-15:
                continue
            phi = phi * keep[:, None]
            phi /= np.sqrt(norm)
        return phi

    def _project_operator(self, phi: np.ndarray, vals: np.ndarray,
                          rng) -> np.ndarray:
        """Projective measurement of a diagonal operator ``vals``: Born-sample an
        eigenvalue and project the joint state onto that eigenspace."""
        weight = (np.abs(phi) ** 2).sum(axis=1)       # sum over code columns
        keyed = np.round(vals, 9)
        uniq = np.unique(keyed)
        probs = np.array([weight[keyed == v].sum() for v in uniq])
        probs = probs / probs.sum()
        v = rng.choice(uniq, p=probs)
        keep = keyed == v
        norm = float(weight[keep].sum())
        if norm < 1e-15:
            return phi
        phi = phi * keep[:, None]
        phi /= np.sqrt(norm)
        return phi

    def _measure_collective(self, phi: np.ndarray, p: float, rng) -> np.ndarray:
        """With probability ``p`` measure the fixed ``collective_op`` globally."""
        if rng.random() >= p:
            return phi
        return self._project_operator(phi, self.collective_op, rng)

    def _measure_block(self, phi: np.ndarray, p: float, ell: int,
                       rng) -> np.ndarray:
        """With probability ``p`` measure the block-sum ``sum_{i in W} Z_i`` for a
        random contiguous window ``W`` of size ``ell`` (OBC).

        ``ell=1`` reduces to a single-site Z measurement (local); ``ell=L`` is a
        global uniform-magnetisation measurement. Holding the per-step event
        count fixed, ``ell`` isolates measurement *support size* from rate.
        """
        if rng.random() >= p:
            return phi
        L = self.model.L
        j = int(rng.integers(0, L - ell + 1))
        vals = self.zdiag[j:j + ell].sum(axis=0)
        return self._project_operator(phi, vals, rng)

    def _measure_sites(self, phi: np.ndarray, p: float, rng) -> np.ndarray:
        """With probability ``p`` per site, measure that site's diagonal operator
        ``site_diags[j]`` (single-site projective measurement). Works for any
        local dimension (qubit Z, spin-1 S^z, ...)."""
        for j in range(self.model.L):
            if rng.random() >= p:
                continue
            phi = self._project_operator(phi, self.site_diags[j], rng)
        return phi

    def _measure_operator(self, phi: np.ndarray, p: float, rng) -> np.ndarray:
        """With probability ``p`` measure the general Hermitian ``operator`` by
        Born-sampling one of its (grouped) eigenvalues and projecting onto that
        eigenspace. Used to test DFS protection (e.g. the su(2) Casimir J^2)."""
        if rng.random() >= p:
            return phi
        psi = self.op_V.conj().T @ phi               # to operator eigenbasis
        proj = self._project_operator(psi, self.op_labels.astype(float), rng)
        return self.op_V @ proj                      # back to computational basis

    # ------------------------------------------------------------- trajectory
    def run_code(self, code_states, cfg: TrajectoryConfig, rng) -> np.ndarray:
        """One trajectory for an ``m``-dimensional code maximally entangled with
        an ``m``-level reference. ``code_states`` is a list of ``m`` orthonormal
        system vectors; the joint state is ``sum_c |c>_R|code_c>/sqrt(m)``.
        Returns the recorded reference entropy ``S_R`` (in bits, range [0, log2 m])."""
        m = len(code_states)
        phi = np.zeros((self.model.dim, m), dtype=complex)
        for c, v in enumerate(code_states):
            phi[:, c] = v / np.sqrt(m)
        rec = []
        if cfg.measure == "localZ":
            def measure(ph): return self._measure_localZ(ph, cfg.p, rng)
        elif cfg.measure == "collective":
            def measure(ph): return self._measure_collective(ph, cfg.p, rng)
        elif cfg.measure == "block":
            def measure(ph): return self._measure_block(ph, cfg.p,
                                                        cfg.block_size, rng)
        elif cfg.measure == "operator":
            def measure(ph): return self._measure_operator(ph, cfg.p, rng)
        elif cfg.measure == "sites":
            def measure(ph): return self._measure_sites(ph, cfg.p, rng)
        else:
            raise ValueError(f"unknown measure mode {cfg.measure!r}")
        for step in range(cfg.n_steps):
            phi = self.U @ phi
            phi = measure(phi)
            if (step + 1) % cfg.record_every == 0:
                rec.append(_reference_entropy(phi))
        return np.array(rec)

    def run(self, logical0: np.ndarray, logical1: np.ndarray,
            cfg: TrajectoryConfig, rng) -> np.ndarray:
        """Single-qubit code: thin wrapper over :meth:`run_code`."""
        return self.run_code([logical0, logical1], cfg, rng)

    def coherent_information_code(self, code_states, cfg: TrajectoryConfig,
                                  n_traj: int, seed: int = 0) -> dict:
        """Extensive (k-logical-qubit) version. Returns steady-state
        ``S_R`` (bits), its per-qubit density ``S_R/log2 m``, and SEMs."""
        rng = np.random.default_rng(seed)
        recs = np.array([self.run_code(code_states, cfg, rng)
                         for _ in range(n_traj)])
        tail = recs[:, recs.shape[1] - max(1, recs.shape[1] // 4):]
        k = np.log2(len(code_states))
        sr = float(tail.mean())
        sr_sem = float(tail.mean(axis=1).std(ddof=1) / np.sqrt(n_traj))
        return dict(S_R=sr, S_R_sem=sr_sem, k=k,
                    density=sr / k if k > 0 else 0.0)

    def coherent_information(self, logical0: np.ndarray, logical1: np.ndarray,
                             cfg: TrajectoryConfig, n_traj: int,
                             seed: int = 0) -> dict:
        """Trajectory-averaged S_R(t) and steady-state value C_R.

        Returns dict with ``times``, ``S_R_mean``, ``S_R_sem``, ``C_R``
        (mean over the last quarter of the record), ``C_R_sem``.
        """
        rng = np.random.default_rng(seed)
        recs = np.array([self.run(logical0, logical1, cfg, rng)
                         for _ in range(n_traj)])          # (n_traj, n_rec)
        mean = recs.mean(axis=0)
        sem = recs.std(axis=0, ddof=1) / np.sqrt(n_traj)
        times = (np.arange(1, len(mean) + 1) * cfg.record_every) * cfg.dt
        tail = recs[:, len(mean) - max(1, len(mean) // 4):]
        c_r = float(tail.mean())
        c_r_sem = float(tail.mean(axis=1).std(ddof=1) / np.sqrt(n_traj))
        return dict(times=times, S_R_mean=mean, S_R_sem=sem,
                    C_R=c_r, C_R_sem=c_r_sem)
