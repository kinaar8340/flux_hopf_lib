"""Hopf map S³ → S², stereographic projection, fiber sampling, linking.

Source lineage: hfb ``hfb.hopf.fibration`` + kingdom ``kingdom.core.hopf``.
"""

from __future__ import annotations

from typing import Any

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


def hopf_map_quaternion(w: float, x: float, y: float, z: float) -> tuple[float, float, float]:
    """Hopf map via unit quaternion (w, x, y, z) ≡ (x₁, x₂, x₃, x₄)."""
    y1, y2, y3 = hopf_map(
        np.array([w], dtype=float),
        np.array([x], dtype=float),
        np.array([y], dtype=float),
        np.array([z], dtype=float),
    )
    return float(y1[0]), float(y2[0]), float(y3[0])


def s3_from_quaternion(q: Array) -> tuple[Array, Array, Array, Array]:
    """Interpret quaternion components (w, x, y, z) as S³ coordinates."""
    q = np.asarray(q, dtype=float)
    n = np.linalg.norm(q, axis=-1, keepdims=True) + 1e-12
    q = q / n
    return q[..., 0], q[..., 1], q[..., 2], q[..., 3]


def stereographic_project(
    x1: Array,
    x2: Array,
    x3: Array,
    x4: Array,
    *,
    scale: float = 2.0,
) -> tuple[Array, Array, Array]:
    """Stereographic projection S³ → ℝ³ (pole at x₄ = −1, TOE-compatible)."""
    denom = 1.0 - x4 + 1e-12
    return scale * x2 / denom, scale * x3 / denom, scale * x1 / denom


def sample_fiber(
    eta: float,
    xi1: float,
    n_points: int = 200,
    *,
    scale: float = 2.0,
) -> dict[str, Any]:
    """Sample one Hopf fiber: fix base (η, ξ₁), sweep fiber phase ξ₂ ∈ [0, 2π)."""
    xi2 = np.linspace(0.0, 2.0 * np.pi, n_points, endpoint=False)
    x1, x2, x3, x4 = hopf_coordinates(
        np.full(n_points, eta), np.full(n_points, xi1), xi2
    )
    y1, y2, y3 = hopf_map(x1, x2, x3, x4)
    px, py, pz = stereographic_project(x1, x2, x3, x4, scale=scale)
    return {
        "eta": float(eta),
        "xi1": float(xi1),
        "xi2": xi2,
        "x1": x1,
        "x2": x2,
        "x3": x3,
        "x4": x4,
        "y1": y1,
        "y2": y2,
        "y3": y3,
        "px": px,
        "py": py,
        "pz": pz,
        "base_y1": float(y1[0]),
        "base_y2": float(y2[0]),
        "base_y3": float(y3[0]),
        "curve_xyz": np.column_stack([px, py, pz]),
    }


def sample_fiber_family(
    n_fibers: int = 12,
    n_points: int = 160,
    eta_range: tuple[float, float] = (0.15, 1.35),
    *,
    scale: float = 2.0,
) -> list[dict[str, Any]]:
    """Sample a family of linked Hopf fibers over a spread of base points on S²."""
    n_eta = max(1, int(np.sqrt(n_fibers)) + 1)
    n_xi1 = max(1, int(np.ceil(n_fibers / n_eta)))
    eta_vals = np.linspace(eta_range[0], eta_range[1], n_eta)
    xi1_vals = np.linspace(0.0, 2.0 * np.pi, n_xi1, endpoint=False)
    fibers: list[dict[str, Any]] = []
    for eta in eta_vals:
        for xi1 in xi1_vals:
            if len(fibers) >= n_fibers:
                return fibers
            fibers.append(sample_fiber(float(eta), float(xi1), n_points=n_points, scale=scale))
    return fibers


def base_sphere_mesh(
    n_theta: int = 24,
    n_phi: int = 48,
) -> tuple[Array, Array, Array]:
    """Unit S² mesh for the Hopf base space."""
    theta = np.linspace(0.0, np.pi, n_theta)
    phi = np.linspace(0.0, 2.0 * np.pi, n_phi)
    tt, pp = np.meshgrid(theta, phi, indexing="ij")
    return np.sin(tt) * np.cos(pp), np.sin(tt) * np.sin(pp), np.cos(tt)


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


def fiber_linking_number(
    fiber_a: dict[str, Any],
    fiber_b: dict[str, Any],
) -> float:
    """Linking number between two ``sample_fiber`` results (stereographic curves)."""
    return linking_number_pair(fiber_a["curve_xyz"], fiber_b["curve_xyz"])
