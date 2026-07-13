"""Extended PDE mean-mode and gauge utility tests."""

from __future__ import annotations

import numpy as np
import pytest

from flux_hopf_lib.flux import (
    gauge_restoring_alpha,
    lambda_from_kappa,
    mean_field_gauge_torque,
    pointer_damping,
)
from flux_hopf_lib.simulation import (
    mean_cot_grad_flux,
    zero_mode_survival_continuous,
    zero_mode_survival_euler,
)


def test_mean_field_gauge_torque():
    assert mean_field_gauge_torque(1.0, kappa=0.85) == pytest.approx(-0.85)


def test_gauge_and_pointer():
    a = gauge_restoring_alpha(0.2, gauge_strength=0.88, kappa=0.85)
    assert a < 0.0
    p = pointer_damping(a)
    assert -1.0 < p < 1.0
    assert lambda_from_kappa(0.85) == 0.85


def test_zero_mode_continuous_matches_euler_roughly():
    th0 = 1.2
    s_c = zero_mode_survival_continuous(0.85, th0, lambda_t=2.0)
    s_e = zero_mode_survival_euler(0.85, th0, lambda_t=2.0, dt=0.001)
    assert abs(s_c - s_e) < 0.05
    assert 0.0 < s_c < 1.5


def test_mean_cot_grad_flux_finite():
    rng = np.random.default_rng(0)
    theta = rng.uniform(0.2, 1.5, (8, 8, 8))
    m = mean_cot_grad_flux(theta, D=0.05)
    assert np.isfinite(m)
