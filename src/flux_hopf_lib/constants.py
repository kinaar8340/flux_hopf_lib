"""Shared mathematical and model constants across the ecosystem.

Extracted from toe ``relaxation_survival``, mystery probes, and conduit
golden-angle / gauge conventions so every consumer imports one definition.
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Transcendental / geometric constants
# ---------------------------------------------------------------------------
PHI: float = (1.0 + math.sqrt(5.0)) / 2.0
E: float = math.e
PI: float = math.pi

# Mystery residual: φ² + e² − π²  (Pythagorean-style interpretive residual)
R_RESIDUAL: float = PHI**2 + E**2 - PI**2

# Universal survival fraction at λt = 2 for memoryless exponential decay
E_INV2: float = math.exp(-2.0)

# Golden-angle packing (phyllotaxis / Hopf S¹)
GOLDEN_ANGLE_DEG: float = 360.0 * (1.0 - 1.0 / PHI)  # ≈ 137.5078°
GOLDEN_ANGLE_RAD: float = math.radians(GOLDEN_ANGLE_DEG)
GOLDEN_ANGLE_FRACTION: float = GOLDEN_ANGLE_DEG / 1000.0  # ≈ 0.1375
PHI_INV2: float = 1.0 / PHI**2  # ≈ 0.381966

# ---------------------------------------------------------------------------
# Gauged lattice / conduit defaults (toe RubikConeConduit conventions)
# ---------------------------------------------------------------------------
DEFAULT_KAPPA: float = 0.85
DEFAULT_GAUGE_STRENGTH: float = 0.88
DEFAULT_TWIST_RATE: float = 12.5
DEFAULT_MAX_DEPTH: float = 56.0

# Burst threshold base: θ_crit = π(1 + κ)  (also fixed 5.8 rad in some demos)
THETA_CRIT_BASE: float = PI  # multiply by (1 + κ) via theta_crit(kappa)

# Topological clock lock (rad) used by RubikConeConduit epoch sync
W_G_LOCK: float = 111.408

# λt survival horizon target
DEFAULT_LAMBDA_T: float = 2.0


def theta_crit(kappa: float = DEFAULT_KAPPA) -> float:
    """Burst sink threshold θ_crit = π(1 + κ)."""
    return PI * (1.0 + kappa)
