"""Hopf map S³ → S² and linking diagnostics.

Source lineage: hfb ``hfb.hopf.fibration`` (authoritative map + Gauss linking).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.floating]


def hopf_coordinates(
    eta: Array,
    xi1: Array,
    xi2: Array,
) -> tuple[Array, Array, Array, Array]:
    """S³ parametrization (η, ξ₁, ξ₂) → (x₁, x₂, x₃, x₄) with Σ xᵢ² = 1."""
    c1 = np.cos(xi1)
    s1 = np.sin(xi1)
    c2 = np.cos(xi2)
    s2 = np.sin(xi2)
    ce = np.cos(eta)
    se = np.sin(eta)
    x1 = ce * c1
    x2 = ce * s1
    x3 = se * c2
    x4 = se * s2
    return x1, x2, x3, x4


def hopf_map(
    x1: Array,
    x2: Array,
    x3: Array,
    x4: Array,
) -> tuple[Array, Array, Array]:
    """Standard Hopf fibration projection S³ → S²."""
    y1 = x1**2 - x2**2
    y2 = 2.0 * x1 * x2
    y3 = 2.0 * (x3 * x4 + x1 * x2)
    norm = np.sqrt(y1**2 + y2**2 + y3**2) + 1e-12
    return y1 / norm, y2 / norm, y3 / norm


def hopf_map_from_angles(
    eta: Array,
    xi1: Array,
    xi2: Array,
) -> tuple[Array, Array, Array]:
    """Compose ``hopf_coordinates`` + ``hopf_map``."""
    return hopf_map(*hopf_coordinates(eta, xi1, xi2))


def s3_from_quaternion(q: Array) -> tuple[Array, Array, Array, Array]:
    """Interpret quaternion components (w, x, y, z) as S³ coordinates."""
    q = np.asarray(q, dtype=float)
    n = np.linalg.norm(q, axis=-1, keepdims=True) + 1e-12
    q = q / n
    return q[..., 0], q[..., 1], q[..., 2], q[..., 3]


def linking_number_pair(
    curve_a: Array,
    curve_b: Array,
) -> float:
    """Gauss linking integral for two closed 3D curves (discrete sum)."""
    curve_a = np.asarray(curve_a, dtype=float)
    curve_b = np.asarray(curve_b, dtype=float)
    n_a = curve_a.shape[0]
    n_b = curve_b.shape[0]
    total = 0.0
    for i in range(n_a):
        r1 = curve_a[i]
        r2 = curve_a[(i + 1) % n_a]
        dr1 = r2 - r1
        for j in range(n_b):
            s1 = curve_b[j]
            s2 = curve_b[(j + 1) % n_b]
            dr2 = s2 - s1
            r12 = s1 - r1
            denom = np.linalg.norm(r12) ** 3 + 1e-12
            total += float(np.dot(r12, np.cross(dr1, dr2)) / denom)
    return total / (4.0 * np.pi)
