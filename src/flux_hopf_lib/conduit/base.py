"""Base conduit config, mixins, and golden-angle helpers.

Full ``RubikConeConduit`` / ``TwistedHelicalConduit`` stay in toe (torch +
ring topology). Consumer conduits should inherit these mixins or implement
``ConduitProtocol`` and import shared κ / survival logic from this package.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from flux_hopf_lib.constants import (
    DEFAULT_GAUGE_STRENGTH,
    DEFAULT_KAPPA,
    DEFAULT_MAX_DEPTH,
    DEFAULT_TWIST_RATE,
    GOLDEN_ANGLE_DEG,
    GOLDEN_ANGLE_RAD,
    PHI,
    PHI_INV2,
    W_G_LOCK,
)


@dataclass
class ConduitConfig:
    """Shared geometric / gauge parameters for helical and Rubik-style conduits."""

    embed_dim: int = 384
    twist_rate: float = DEFAULT_TWIST_RATE
    max_depth: float = DEFAULT_MAX_DEPTH
    num_polarizations: int = 3
    kappa: float = DEFAULT_KAPPA
    gauge_strength: float = DEFAULT_GAUGE_STRENGTH
    golden_angle_steps: bool = False
    golden_angle_mode: str = "golden"  # or "phi_inv2"
    w_g_lock: float = W_G_LOCK
    extra: dict[str, Any] = field(default_factory=dict)

    def characteristic_rate(self) -> float:
        return float(self.kappa)


def apply_golden_angle_increment(
    s: float,
    step_index: int | None = None,
    *,
    max_depth: float = DEFAULT_MAX_DEPTH,
    mode: str = "golden",
) -> tuple[float, float]:
    """
    Advance arc-length s by golden-angle (or φ⁻²) irrational packing step.

    Returns (adjusted_s, golden_phase_rad) for helical twist on the unit circle.
    Used when golden_angle_steps=True on TwistedHelicalConduit / RubikConeConduit.
    """
    if mode == "phi_inv2":
        step_rad = PHI_INV2 * (2.0 * math.pi / 9.0)
    else:
        step_rad = GOLDEN_ANGLE_RAD

    step_arc = max_depth * (GOLDEN_ANGLE_DEG / 360.0) / 1000.0
    if step_arc <= 0:
        return s, 0.0

    if step_index is None:
        step_index = int(s / step_arc)
    golden_phase = (step_index * step_rad) % (2.0 * math.pi)
    adjusted_s = float(step_index * step_arc)
    return adjusted_s, golden_phase


class GoldenAngleMixin:
    """Mixin providing golden-angle / Fibonacci helpers (numpy-friendly)."""

    PHI: float = PHI
    max_depth: float = DEFAULT_MAX_DEPTH
    golden_angle_mode: str = "golden"

    def fib(self, n: int) -> int:
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def golden_scale(self, base: float, fib_index: int = 8) -> float:
        f_n = self.fib(fib_index)
        f_np1 = self.fib(fib_index + 1)
        fib_ratio = f_np1 / f_n if f_n != 0 else self.PHI
        return base * fib_ratio

    def golden_phase_at(self, s: float, step_index: int | None = None) -> tuple[float, float]:
        mode = getattr(self, "golden_angle_mode", "golden")
        max_depth = getattr(self, "max_depth", DEFAULT_MAX_DEPTH)
        return apply_golden_angle_increment(s, step_index, max_depth=max_depth, mode=mode)

    def vortex_digit_fib(self, pol_idx: int = 0, s: float = 0.0, fib_index: int = 13) -> int:
        scaled = self.golden_scale(abs(s) + pol_idx * 0.37, fib_index=fib_index)
        digit = int(scaled) % 9
        return 9 if digit == 0 else digit

    @staticmethod
    def vortex_advance(digit: int, steps: int = 1) -> int:
        for _ in range(steps):
            digit = (digit * 2) % 9
            if digit == 0:
                digit = 9
        return digit

    @staticmethod
    def vortex_is_369_control(digit: int) -> bool:
        return digit in (3, 6, 9)


class GaugePointerMixin:
    """Mixin for global pointer κ damping and W_g lock metadata."""

    kappa: float = DEFAULT_KAPPA
    gauge_strength: float = DEFAULT_GAUGE_STRENGTH
    w_g_lock: float = W_G_LOCK

    def characteristic_rate(self) -> float:
        """λ for gauge-restoring dynamics (≈ κ in mean-field reduction)."""
        return float(self.kappa)

    def gauge_alpha(self, avg_imbalance: float, kappa_weight: float = 0.1) -> float:
        return float(
            -self.gauge_strength * avg_imbalance - self.kappa * avg_imbalance * kappa_weight
        )

    def steps_to_lambda_t(self, lambda_t: float = 2.0, dt: float = 0.001) -> int:
        from flux_hopf_lib.simulation.survival import steps_for_lambda_t

        return steps_for_lambda_t(lambda_t, self.kappa, dt)


@runtime_checkable
class ConduitProtocol(Protocol):
    """Minimal interface specialized conduits should expose."""

    kappa: float
    gauge_strength: float

    def characteristic_rate(self) -> float: ...
