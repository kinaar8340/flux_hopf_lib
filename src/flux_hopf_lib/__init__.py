"""
flux_hopf_lib
=============
Shared core library for the Hopf / flux / quaternion / conduit ecosystem.

Subpackages
-----------
quaternion   Unit quaternions, rotors, Rodrigues helpers (numpy; optional torch).
hopf         Hopf fibration maps, fibers, hopfion textures, linking.
flux         Flux lattice parameters, gauge dynamics, defect densities.
simulation   λt-normalization, survival probes, twist-PDE relaxation, κ helpers.
conduit      Base conduit protocol and mixins for specialized conduits.
utils        Grids, constants, small shared helpers.

This package is the single source of truth for foundational math and probes.
Specialized pipelines (VQC encoding, Gradio portals, full RubikConeConduit)
remain in consumer repos (toe, mystery, vqc_proto, hfb, kingdom, …).
"""

from __future__ import annotations

from flux_hopf_lib.constants import (
    DEFAULT_KAPPA,
    E,
    E_INV2,
    GOLDEN_ANGLE_DEG,
    GOLDEN_ANGLE_FRACTION,
    GOLDEN_ANGLE_RAD,
    PHI,
    PHI_INV2,
    PI,
    R_RESIDUAL,
    THETA_CRIT_BASE,
    W_G_LOCK,
)

__version__ = "0.2.1"

__all__ = [
    "__version__",
    "PHI",
    "E",
    "PI",
    "R_RESIDUAL",
    "E_INV2",
    "GOLDEN_ANGLE_DEG",
    "GOLDEN_ANGLE_RAD",
    "GOLDEN_ANGLE_FRACTION",
    "PHI_INV2",
    "DEFAULT_KAPPA",
    "THETA_CRIT_BASE",
    "W_G_LOCK",
]
