"""Hopf fibration tests."""

from __future__ import annotations

import numpy as np

from flux_hopf_lib.hopf import hopf_coordinates, hopf_map, hopf_map_from_angles
from flux_hopf_lib.hopf.hopfion import toroidal_hopfion_director
from flux_hopf_lib.utils import cartesian_grid


def test_hopf_coordinates_on_s3():
    eta = np.array(0.7)
    xi1 = np.array(0.3)
    xi2 = np.array(1.1)
    x1, x2, x3, x4 = hopf_coordinates(eta, xi1, xi2)
    n2 = x1**2 + x2**2 + x3**2 + x4**2
    assert abs(float(n2) - 1.0) < 1e-10


def test_hopf_map_on_s2():
    y1, y2, y3 = hopf_map_from_angles(np.array(0.4), np.array(0.2), np.array(0.9))
    n = np.sqrt(y1**2 + y2**2 + y3**2)
    assert abs(float(n) - 1.0) < 1e-9


def test_hopf_map_vectorized():
    eta = np.linspace(0.1, 1.0, 5)
    xi1 = np.linspace(0.0, 2.0, 5)
    xi2 = np.linspace(0.0, 1.5, 5)
    y1, y2, y3 = hopf_map(*hopf_coordinates(eta, xi1, xi2))
    norms = np.sqrt(y1**2 + y2**2 + y3**2)
    assert np.allclose(norms, 1.0, atol=1e-8)


def test_hopfion_unit():
    x, y = cartesian_grid(16, 16, extent=2.0)
    z = np.zeros_like(x)
    nx, ny, nz = toroidal_hopfion_director(x, y, z)
    norms = np.sqrt(nx**2 + ny**2 + nz**2)
    assert np.allclose(norms, 1.0, atol=1e-8)
