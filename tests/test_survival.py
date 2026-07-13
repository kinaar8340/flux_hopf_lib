"""Survival / λt / relaxation tests."""

from __future__ import annotations

import math

import numpy as np

from flux_hopf_lib import E_INV2, PHI, R_RESIDUAL
from flux_hopf_lib.simulation import (
    LambdaTNormalization,
    compare_to_analogs,
    evolve_gauged_twist_survival,
    simulate_twist_pde_survival,
    steps_for_lambda_t,
)
from flux_hopf_lib.simulation.kappa import kappa_grid


def test_constants():
    assert abs(PHI - (1 + math.sqrt(5)) / 2) < 1e-12
    assert abs(E_INV2 - math.exp(-2)) < 1e-12
    assert abs(R_RESIDUAL - (PHI**2 + math.e**2 - math.pi**2)) < 1e-12


def test_lambda_t_steps():
    norm = LambdaTNormalization(lambda_t_target=2.0, kappa=0.85, dt=0.001)
    assert norm.n_steps == steps_for_lambda_t(2.0, 0.85, 0.001)
    assert abs(norm.t_physical - 2.0 / 0.85) < 1e-12
    assert norm.n_steps == max(1, int(round(norm.t_physical / 0.001)))


def test_compare_to_analogs():
    out = compare_to_analogs(E_INV2, "test")
    assert out["best_match"] == "e_inv2"
    assert out["delta_abs"] < 1e-12


def test_evolve_gauged_short():
    out = evolve_gauged_twist_survival(
        n_steps=50,
        n_identities=16,
        seed=0,
    )
    assert 0.0 <= out["identity_survival"] <= 1.0
    assert "analog_comparison_survival" in out


def test_pde_survival_small():
    out = simulate_twist_pde_survival(
        nx=8,
        normalize_to_lambda_t=0.5,  # short horizon for speed
        seed=1,
        track_interval=20,
    )
    assert "survival" in out
    assert "mean_survival" in out["survival"]
    assert out["normalization"]["n_steps"] > 0


def test_kappa_grid():
    g = kappa_grid(0.8, 0.9, 5)
    assert len(g) == 5
    assert np.isclose(g[0], 0.8)
    assert np.isclose(g[-1], 0.9)
