#!/usr/bin/env python3
"""Minimal consumer-style usage of flux_hopf_lib.

Run from repo root after:  pip install -e ".[dev]"
    python examples/quickstart.py
"""

from __future__ import annotations

from flux_hopf_lib import DEFAULT_KAPPA, E_INV2, PHI, R_RESIDUAL
from flux_hopf_lib.conduit import ConduitConfig, GoldenAngleMixin, GaugePointerMixin
from flux_hopf_lib.flux import FluxLatticeConfig, FluxFlywheel
from flux_hopf_lib.hopf import hopf_map_from_angles
from flux_hopf_lib.quaternion import Quaternion, small_rotor
from flux_hopf_lib.simulation import (
    compare_to_analogs,
    evolve_gauged_twist_survival,
    steps_for_lambda_t,
)
from flux_hopf_lib.utils import cartesian_grid


def main() -> None:
    print("=== constants ===")
    print(f"  φ={PHI:.10f}  R={R_RESIDUAL:.6f}  e^{{-2}}={E_INV2:.6f}  κ={DEFAULT_KAPPA}")

    print("=== quaternion + Hopf ===")
    q = Quaternion.from_axis_angle([0.0, 0.0, 1.0], 0.4).normalize()
    y1, y2, y3 = hopf_map_from_angles(0.5, 1.0, 0.2)
    print(f"  rotor={q}  hopf_base=({float(y1):.4f}, {float(y2):.4f}, {float(y3):.4f})")
    print(f"  small_rotor={small_rotor(0.1)}")

    print("=== λt survival ===")
    n = steps_for_lambda_t(2.0, DEFAULT_KAPPA, 0.001)
    out = evolve_gauged_twist_survival(n_steps=n, n_identities=24, seed=0)
    cmp_ = compare_to_analogs(out["identity_residual"], "identity_residual")
    print(f"  n_steps={n}  identity_survival={out['identity_survival']:.4f}")
    print(f"  residual best_match={cmp_['best_match']}  hybrid_score={cmp_['hybrid_score']:.4f}")

    print("=== flux flywheel ===")
    fw = FluxFlywheel(config=FluxLatticeConfig(kappa=DEFAULT_KAPPA))
    fw.run(20)
    print(f"  twist_final={fw.twist_history[-1]:.4f}  bursts={fw.burst_count}")

    print("=== conduit mixins (composition pattern) ===")

    class MiniConduit(GoldenAngleMixin, GaugePointerMixin):
        def __init__(self) -> None:
            self.kappa = DEFAULT_KAPPA
            self.gauge_strength = 0.88
            self.max_depth = 56.0
            self.golden_angle_mode = "golden"

    cfg = ConduitConfig(kappa=DEFAULT_KAPPA, golden_angle_steps=True)
    mini = MiniConduit()
    s, phase = mini.golden_phase_at(1.0, step_index=3)
    print(f"  ConduitConfig.κ={cfg.kappa}  golden s={s:.4f} phase={phase:.4f}")
    print(f"  steps_to_λt2={mini.steps_to_lambda_t(2.0, 0.001)}")

    x, y = cartesian_grid(8, 8, extent=1.0)
    print(f"  grid shape={x.shape}")
    print("ok")


if __name__ == "__main__":
    main()
