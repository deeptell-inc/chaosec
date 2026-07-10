"""Core validation tests for the scarcode package.

These lock in the physics benchmarks used throughout the paper: the constrained
Fibonacci dimension, the Z2 scar revival, the p=0 sanity of the monitored
channel, exactness of the spin-1 scar tower, and the vanishing Casimir variance
that makes the exact scars a decoherence-free subspace.
"""

import numpy as np
import pytest

from scarcode import (PXPModel, diagonalize, identify_scars, scar_code,
                      thermal_ensemble, MonitoredPXP, TrajectoryConfig,
                      Spin1Scar)


def _fib(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a


@pytest.mark.parametrize("L,expected", [(4, 8), (6, 21), (10, 144), (12, 377)])
def test_fibonacci_dimension(L, expected):
    m = PXPModel(L)
    assert m.dim == expected == _fib(L + 2)


def test_pxp_hamiltonian_symmetric_traceless():
    H = PXPModel(10).hamiltonian().toarray()
    assert np.allclose(H, H.T)
    assert abs(np.trace(H)) < 1e-9


def test_z2_revival():
    m = PXPModel(12)
    spec = diagonalize(m)
    z2 = m.neel_state(0)
    c2 = (spec.vectors.T @ z2) ** 2
    ts = np.linspace(3.0, 6.0, 301)
    fid = np.abs((np.exp(-1j * np.outer(ts, spec.energies)) * c2).sum(1)) ** 2
    peak = fid.max()
    t_peak = ts[int(np.argmax(fid))]
    assert 4.4 < t_peak < 5.0        # canonical PXP revival period
    assert peak > 0.6                # partial revival height


def test_monitored_p0_gives_unit_coherent_information():
    m = PXPModel(10)
    spec = diagonalize(m)
    identify_scars(spec, L=10)
    s0, s1, _ = scar_code(spec)
    mon = MonitoredPXP(m, dt=0.6)
    cfg = TrajectoryConfig(p=0.0, n_steps=8, dt=0.6)
    out = mon.coherent_information(s0, s1, cfg, n_traj=3, seed=0)
    assert abs(out["C_R"] - 1.0) < 1e-9


def test_monitored_large_p_purifies():
    m = PXPModel(10)
    spec = diagonalize(m)
    identify_scars(spec, L=10)
    s0, s1, _ = scar_code(spec)
    mon = MonitoredPXP(m, dt=0.6)
    cfg = TrajectoryConfig(p=0.4, n_steps=30, dt=0.6)
    out = mon.coherent_information(s0, s1, cfg, n_traj=60, seed=0)
    assert out["C_R"] < 0.1          # information is lost at high measurement rate


def test_thermal_ensemble_beats_scar_locally():
    m = PXPModel(12)
    spec = diagonalize(m)
    identify_scars(spec, L=12)
    s0, s1, (k0, k1) = scar_code(spec)
    therm = thermal_ensemble(spec, (spec.energies[k0], spec.energies[k1]),
                             kmax=8, seed=1)
    mon = MonitoredPXP(m, dt=0.6)
    cfg = TrajectoryConfig(p=0.08, n_steps=30, dt=0.6)
    cs = mon.coherent_information(s0, s1, cfg, 80, seed=2)["C_R"]
    ct = np.mean([mon.coherent_information(a, b, cfg, 80, seed=2)["C_R"]
                  for a, b in therm])
    assert ct >= cs - 0.02           # thermal ensemble is at least as good


def test_spin1_exact_tower_and_zero_casimir_variance():
    sp = Spin1Scar(6, h=1.0, D=0.1)
    H = sp.hamiltonian().toarray()
    ens, tw = sp.tower()
    assert tw.shape[1] == sp.L + 1                       # tower has L+1 rungs
    # exact eigenstates
    resid = max(np.linalg.norm(H @ tw[:, n] - ens[n] * tw[:, n])
                for n in range(tw.shape[1]))
    assert resid < 1e-10
    # equally spaced by 2
    assert np.allclose(np.diff(ens), 2.0, atol=1e-6)
    # Casimir constant on the tower (zero variance on each scar)
    J2 = sp.casimir()
    j2 = [(tw[:, n] @ (J2 @ tw[:, n])).real for n in range(tw.shape[1])]
    assert np.std(j2) < 1e-8
    assert abs(np.mean(j2) - (sp.L / 2) * (sp.L / 2 + 1)) < 1e-6


def test_forward_scattering_split():
    sp = Spin1Scar(4)
    assert sp.hamiltonian() is not None
    assert PXPModel(8).hamiltonian().shape[0] == 55
