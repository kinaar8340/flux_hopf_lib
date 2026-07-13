"""Defect density profiles for conformal sources and flux-bubble walls.

Source lineage: hfb ``hfb.defects.densities``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.floating]


def gaussian_defect(
    x: Array,
    y: Array,
    amplitude: float = 1.0,
    sigma: float = 0.5,
    x0: float = 0.0,
    y0: float = 0.0,
) -> Array:
    """Isotropic Gaussian defect density."""
    r2 = (x - x0) ** 2 + (y - y0) ** 2
    return amplitude * np.exp(-r2 / (2.0 * sigma**2))


def exponential_ring(
    x: Array,
    y: Array,
    radius: float = 1.0,
    width: float = 0.2,
    amplitude: float = 1.0,
) -> Array:
    """Toroidal wall density peaked at |r| = radius."""
    r = np.sqrt(x**2 + y**2)
    return amplitude * np.exp(-((r - radius) ** 2) / (2.0 * width**2))


def vortex_core(
    x: Array,
    y: Array,
    winding: int = 1,
    core_radius: float = 0.15,
    amplitude: float = 1.0,
) -> Array:
    """Regularized vortex core density with quantized winding k."""
    r = np.sqrt(x**2 + y**2)
    return amplitude * (r / core_radius) ** (2 * abs(winding)) * np.exp(-(r / core_radius) ** 2)


def winding_density(
    x: Array,
    y: Array,
    winding: int = 1,
    core_radius: float = 0.15,
) -> Array:
    """Phase winding proxy used as a smooth defect source."""
    theta = np.arctan2(y, x)
    r = np.sqrt(x**2 + y**2)
    phase = winding * theta
    envelope = np.exp(-(r / core_radius) ** 2)
    return np.sin(phase) ** 2 * envelope


def torus_tube_distance(
    x: Array,
    y: Array,
    z_slice: float,
    major_radius: float,
) -> Array:
    """Distance from (x, y, z_slice) to the major-radius centerline of a 3D torus."""
    rho = np.sqrt(x**2 + y**2)
    return np.sqrt((rho - major_radius) ** 2 + z_slice**2)


def toroidal_bubble_wall(
    x: Array,
    y: Array,
    major_radius: float = 1.0,
    minor_radius: float = 0.35,
    amplitude: float = 1.0,
    wall_width: float = 0.25,
    use_3d_torus: bool = False,
    z_slice: float = 0.0,
    hopf_index: int = 1,
) -> Array:
    """Toroidal defect density for Hopf flux bubble wall."""
    if use_3d_torus:
        d = torus_tube_distance(x, y, z_slice, major_radius)
        tube = np.exp(-(d**2) / (2.0 * wall_width**2))
        theta = np.arctan2(y, x)
        rho = np.sqrt(x**2 + y**2)
        poloidal = np.arctan2(z_slice, rho - major_radius + 1e-12)
        hopf_texture = 0.5 * (1.0 + np.cos(hopf_index * theta + poloidal))
        return amplitude * tube * hopf_texture

    r = np.sqrt(x**2 + y**2)
    radial_dist = np.abs(r - major_radius)
    wall = np.exp(-(radial_dist**2) / (2.0 * wall_width**2))
    envelope = np.exp(-((y / minor_radius) ** 2))
    return amplitude * wall * envelope
