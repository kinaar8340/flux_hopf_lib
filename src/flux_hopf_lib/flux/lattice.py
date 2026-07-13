"""Base flux-lattice / gauge dynamics (numpy).

Encodes the shared κ / gauge-strength conventions used by toe conduits and
mystery survival probes, without pulling in torch or full RubikCone state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from flux_hopf_lib.constants import (
    DEFAULT_GAUGE_STRENGTH,
    DEFAULT_KAPPA,
    DEFAULT_MAX_DEPTH,
    DEFAULT_TWIST_RATE,
    PI,
    theta_crit,
)
from flux_hopf_lib.quaternion.core import q_conj, q_mult, q_normalize, small_rotor

Array = NDArray[np.floating]


@dataclass
class FluxLatticeConfig:
    """Shared parameters for gauged Hopf / flux flywheel lattices."""

    kappa: float = DEFAULT_KAPPA
    gauge_strength: float = DEFAULT_GAUGE_STRENGTH
    twist_rate: float = DEFAULT_TWIST_RATE
    max_depth: float = DEFAULT_MAX_DEPTH
    omega_L: float = 0.025
    omega_R: float = 0.0225
    delta_omega: float = 0.002
    diffusion: float = 0.05  # D in twist PDE
    theta_crit: float | None = None

    def __post_init__(self) -> None:
        if self.theta_crit is None:
            self.theta_crit = theta_crit(self.kappa)

    def characteristic_rate(self) -> float:
        """Mean-field λ ≈ κ from gauge restoring torque −κ θ̄."""
        return float(self.kappa)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kappa": self.kappa,
            "gauge_strength": self.gauge_strength,
            "twist_rate": self.twist_rate,
            "max_depth": self.max_depth,
            "omega_L": self.omega_L,
            "omega_R": self.omega_R,
            "delta_omega": self.delta_omega,
            "diffusion": self.diffusion,
            "theta_crit": self.theta_crit,
        }


@dataclass
class GaugeStepResult:
    quaternion: NDArray[np.float64]
    twist: float
    gauge_alpha: float
    burst: bool = False


def gauge_restoring_alpha(
    avg_imbalance: float,
    *,
    gauge_strength: float = DEFAULT_GAUGE_STRENGTH,
    kappa: float = DEFAULT_KAPPA,
    kappa_weight: float = 0.1,
) -> float:
    """Global pointer / gauge torque α = −g·I − κ_weight·κ·I."""
    return float(-gauge_strength * avg_imbalance - kappa * avg_imbalance * kappa_weight)


def two_gyro_gauge_step(
    current_q: Array,
    twist_history: Array | list[float],
    config: FluxLatticeConfig | None = None,
    *,
    kappa: float | None = None,
    gauge_strength: float | None = None,
    omega_L: float | None = None,
    omega_R: float | None = None,
) -> GaugeStepResult:
    """One discrete two-gyro gauged Hopf step (numpy).

    Matches the identity-survival loop in toe ``evolve_gauged_twist_survival``.
    """
    cfg = config or FluxLatticeConfig()
    k = cfg.kappa if kappa is None else kappa
    g = cfg.gauge_strength if gauge_strength is None else gauge_strength
    oL = cfg.omega_L if omega_L is None else omega_L
    oR = cfg.omega_R if omega_R is None else omega_R
    t_crit = cfg.theta_crit if cfg.theta_crit is not None else theta_crit(k)

    q = q_normalize(np.asarray(current_q, dtype=float))
    delta_L = small_rotor(oL, np.array([0.0, 0.0, 1.0]))
    delta_R = small_rotor(oR, np.array([0.0, 0.0, 1.0]))
    q = q_normalize(q_mult(q_mult(delta_L, q), q_conj(delta_R)))

    hist = np.asarray(twist_history, dtype=float)
    avg_imbalance = float(np.mean(hist) % (2 * PI)) if hist.size else 0.0
    alpha = gauge_restoring_alpha(avg_imbalance, gauge_strength=g, kappa=k)
    gauge_rot = np.array([np.cos(alpha), 0.0, 0.0, np.sin(alpha)])
    q = q_normalize(q_mult(q, gauge_rot))

    twist = float(2.0 * np.arccos(np.clip(q[0], -1.0, 1.0)))
    return GaugeStepResult(
        quaternion=q,
        twist=twist,
        gauge_alpha=alpha,
        burst=twist > t_crit,
    )


@dataclass
class FluxFlywheel:
    """Minimal flywheel state: quaternion + twist history under gauge dynamics."""

    config: FluxLatticeConfig = field(default_factory=FluxLatticeConfig)
    quaternion: NDArray[np.float64] = field(
        default_factory=lambda: np.array([1.0, 0.0, 0.0, 0.0])
    )
    twist_history: list[float] = field(default_factory=lambda: [0.0])
    burst_count: int = 0

    def step(self) -> GaugeStepResult:
        result = two_gyro_gauge_step(self.quaternion, self.twist_history, self.config)
        self.quaternion = result.quaternion
        self.twist_history.append(result.twist)
        if result.burst:
            self.burst_count += 1
        return result

    def run(self, n_steps: int) -> list[GaugeStepResult]:
        return [self.step() for _ in range(n_steps)]
