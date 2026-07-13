"""Topological / gauge-adjacent invariants for Hopf lattice work.

Companions to ``linking_number_pair``: W_g conventions, holonomy proxies,
and simple fiber diagnostics.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from flux_hopf_lib.constants import PI, W_G_LOCK

Array = NDArray[np.floating]


def wg_from_base(wg_base: float = 350.0) -> float:
    """Topological clock W_g = wg_base / π (default 350/π ≈ 111.408)."""
    return float(wg_base / PI)


def wg_relative_residual(measured_winding: float, wg_base: float = 350.0) -> float:
    """|W − W_g| / W_g for a measured geometric winding."""
    target = wg_from_base(wg_base)
    return float(abs(measured_winding - target) / (abs(target) + 1e-12))


def holonomy_phase_proxy(
    phases: Array,
    *,
    unwrap: bool = True,
) -> dict[str, float]:
    """
    Lightweight holonomy diagnostic on a closed phase sample.

    Returns net winding (rad), residual to 2πℤ, and RMS fluctuation.
    """
    phases = np.asarray(phases, dtype=float).reshape(-1)
    if phases.size < 2:
        return {"net_phase": 0.0, "residual_2pi": 0.0, "rms": 0.0, "winding_approx": 0.0}
    p = np.unwrap(phases) if unwrap else phases
    net = float(p[-1] - p[0])
    residual = float(net - 2.0 * PI * round(net / (2.0 * PI)))
    rms = float(np.sqrt(np.mean((p - p.mean()) ** 2)))
    return {
        "net_phase": net,
        "residual_2pi": residual,
        "rms": rms,
        "winding_approx": net / (2.0 * PI),
    }


def base_point_chordal_distance(
    base_a: tuple[float, float, float] | Array,
    base_b: tuple[float, float, float] | Array,
) -> float:
    """Chordal distance between two unit vectors on S²."""
    a = np.asarray(base_a, dtype=float).reshape(3)
    b = np.asarray(base_b, dtype=float).reshape(3)
    a = a / (np.linalg.norm(a) + 1e-12)
    b = b / (np.linalg.norm(b) + 1e-12)
    return float(np.linalg.norm(a - b))


def fiber_pair_diagnostics(
    fiber_a: dict[str, Any],
    fiber_b: dict[str, Any],
) -> dict[str, float]:
    """Linking number + base-point separation for two sampled fibers."""
    from flux_hopf_lib.hopf.fibration import fiber_linking_number

    ba = (fiber_a["base_y1"], fiber_a["base_y2"], fiber_a["base_y3"])
    bb = (fiber_b["base_y1"], fiber_b["base_y2"], fiber_b["base_y3"])
    return {
        "linking_number": fiber_linking_number(fiber_a, fiber_b),
        "base_chordal_distance": base_point_chordal_distance(ba, bb),
        "wg_lock": W_G_LOCK,
        "wg_350_over_pi": wg_from_base(350.0),
    }
