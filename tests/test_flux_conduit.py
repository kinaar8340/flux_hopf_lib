"""Flux lattice + conduit mixin tests."""

from __future__ import annotations

import numpy as np

from flux_hopf_lib.conduit import (
    ConduitConfig,
    GaugePointerMixin,
    GoldenAngleMixin,
    apply_golden_angle_increment,
)
from flux_hopf_lib.flux import FluxLatticeConfig, gaussian_defect, two_gyro_gauge_step
from flux_hopf_lib.flux.lattice import FluxFlywheel
from flux_hopf_lib.utils import cartesian_grid


def test_flux_lattice_config_theta_crit():
    cfg = FluxLatticeConfig(kappa=0.85)
    assert cfg.theta_crit is not None
    assert abs(cfg.theta_crit - np.pi * 1.85) < 1e-10


def test_two_gyro_step():
    q = np.array([1.0, 0.0, 0.0, 0.0])
    r = two_gyro_gauge_step(q, [0.1, 0.2], FluxLatticeConfig())
    assert abs(np.linalg.norm(r.quaternion) - 1.0) < 1e-9
    assert r.twist >= 0.0


def test_flywheel_run():
    fw = FluxFlywheel()
    results = fw.run(10)
    assert len(results) == 10
    assert len(fw.twist_history) == 11


def test_gaussian_defect():
    x, y = cartesian_grid(32, 32, extent=2.0)
    d = gaussian_defect(x, y, sigma=0.5)
    assert d.max() <= 1.0 + 1e-9
    assert d[16, 16] > d[0, 0]


def test_golden_angle_increment():
    s, phase = apply_golden_angle_increment(0.0, step_index=3)
    assert s >= 0.0
    assert 0.0 <= phase < 2 * np.pi


def test_mixins():
    class Mini(GoldenAngleMixin, GaugePointerMixin):
        pass

    m = Mini()
    m.kappa = 0.85
    assert m.characteristic_rate() == 0.85
    assert m.vortex_is_369_control(3)
    assert m.fib(10) == 55
    steps = m.steps_to_lambda_t(2.0, dt=0.001)
    assert steps > 0


def test_conduit_config():
    c = ConduitConfig(kappa=0.9)
    assert c.characteristic_rate() == 0.9
