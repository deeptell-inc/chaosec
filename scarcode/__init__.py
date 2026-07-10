"""scarcode: information protection of scar vs thermal codes under monitoring.

Compares how well a logical qubit encoded in the PXP scar subspace vs a generic
thermal subspace protects quantum information, quantified statically via
Knill-Laflamme violation and dynamically via the reference-qubit coherent
information of a monitored circuit.
"""

from .pxp import PXPModel
from .states import (Spectrum, diagonalize, identify_scars, scar_code,
                     scar_rungs, thermal_code, thermal_ensemble,
                     entanglement_entropy, participation_entropy)
from .diagnostics import KLReport, kl_local_z
from .monitor import MonitoredPXP, TrajectoryConfig, propagator
from .su2 import h_plus, casimir, check_split
from .spin1 import Spin1Scar

__version__ = "0.1.0"

__all__ = [
    # core PXP model + spectrum
    "PXPModel", "Spectrum", "diagonalize", "identify_scars",
    "scar_code", "scar_rungs", "thermal_code", "thermal_ensemble",
    "entanglement_entropy", "participation_entropy",
    # static diagnostics
    "KLReport", "kl_local_z",
    # monitored dynamics
    "MonitoredPXP", "TrajectoryConfig", "propagator",
    # emergent su(2) Casimir
    "h_plus", "casimir", "check_split",
    # second model
    "Spin1Scar",
    "__version__",
]
