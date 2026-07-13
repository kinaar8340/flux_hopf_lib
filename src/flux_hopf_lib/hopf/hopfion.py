"""Hopfion director textures for nematic / flux-bubble walls.

Source lineage: hfb ``hfb.hopf.hopfion``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.floating]


def toroidal_hopfion_director(
    x: Array,
    y: Array,
    z: Array,
    major_radius: float = 1.0,
    minor_radius: float = 0.35,
    hopf_index: int = 1,
) -> tuple[Array, Array, Array]:
    """Smooth toroidal Hopfion-like director field (unit vector)."""
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    theta = np.arctan2(z, rho - major_radius)

    nx = np.sin(theta) * np.cos(hopf_index * phi)
    ny = np.sin(theta) * np.sin(hopf_index * phi)
    nz = np.cos(theta)

    dist = np.sqrt((rho - major_radius) ** 2 + z**2)
    envelope = np.exp(-(dist / minor_radius) ** 2)
    nx = nx * envelope
    ny = ny * envelope
    nz = nz * envelope + (1.0 - envelope)

    norm = np.sqrt(nx**2 + ny**2 + nz**2) + 1e-12
    return nx / norm, ny / norm, nz / norm


def hopf_charge_density(
    nx: Array,
    ny: Array,
    nz: Array,
    dx: float,
) -> float:
    """Proxy Hopf charge Q_H ∝ ∫ A · B d³x from director gradients (2D slice)."""
    dnx_dy, dnx_dx = np.gradient(nx, dx, edge_order=2)
    dny_dy, dny_dx = np.gradient(ny, dx, edge_order=2)
    dnz_dy, dnz_dx = np.gradient(nz, dx, edge_order=2)

    bx = dnz_dy - dny_dx
    by = dnx_dx - dnz_dy
    ax, ay = nx, ny
    integrand = ax * bx + ay * by
    return float(np.sum(integrand) * dx**2)


def charge_modulated_hopfion(
    x: Array,
    y: Array,
    z: Array,
    charge_density: Array,
    major_radius: float = 1.0,
    minor_radius: float = 0.35,
    hopf_index: int = 1,
    polarization: float = 0.4,
) -> tuple[Array, Array, Array]:
    """Hopfion director polarized by a dual-shell electrostatic charge field."""
    nx, ny, nz = toroidal_hopfion_director(
        x, y, z, major_radius=major_radius, minor_radius=minor_radius, hopf_index=hopf_index
    )
    rho = np.sqrt(x**2 + y**2) + 1e-12
    rx, ry = x / rho, y / rho
    c_norm = charge_density / (np.max(np.abs(charge_density)) + 1e-12)
    strength = polarization * c_norm
    nx = nx + strength * rx
    ny = ny + strength * ry
    nz = nz * (1.0 - 0.25 * np.abs(strength))
    norm = np.sqrt(nx**2 + ny**2 + nz**2) + 1e-12
    return nx / norm, ny / norm, nz / norm
