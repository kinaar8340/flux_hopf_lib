#!/usr/bin/env python3
"""How a leaf repo (e.g. toe) should compose conduit mixins.

Specialized torch modules stay in the leaf; shared κ / golden-angle / λt
logic comes from flux_hopf_lib.

    from flux_hopf_lib.conduit import ConduitConfig, GoldenAngleMixin, GaugePointerMixin
    from flux_hopf_lib.constants import DEFAULT_KAPPA, W_G_LOCK
"""

from __future__ import annotations

from flux_hopf_lib.conduit import ConduitConfig, GaugePointerMixin, GoldenAngleMixin
from flux_hopf_lib.constants import DEFAULT_GAUGE_STRENGTH, DEFAULT_KAPPA, W_G_LOCK
from flux_hopf_lib.simulation import evolve_gauged_twist_survival


class ToySpecializedConduit(GoldenAngleMixin, GaugePointerMixin):
    """Stand-in for RubikConeConduit-style classes.

    Real toe conduits also subclass ``torch.nn.Module`` and keep training /
    ring topology local. Mixins supply only shared theory knobs.
    """

    def __init__(
        self,
        kappa: float = DEFAULT_KAPPA,
        gauge_strength: float = DEFAULT_GAUGE_STRENGTH,
        max_depth: float = 56.0,
        golden_angle_steps: bool = False,
    ) -> None:
        self.kappa = kappa
        self.gauge_strength = gauge_strength
        self.max_depth = max_depth
        self.golden_angle_steps = golden_angle_steps
        self.golden_angle_mode = "golden"
        self.w_g_lock = W_G_LOCK

    def run_survival_probe(self, normalize_to_lambda_t: float = 2.0, dt: float = 0.001):
        """Delegate numpy survival to the shared simulation API."""
        return evolve_gauged_twist_survival(
            n_steps=0,
            kappa=self.kappa,
            gauge_strength=self.gauge_strength,
            normalize_to_lambda_t=normalize_to_lambda_t,
            dt=dt,
            n_identities=16,
            seed=0,
        )


def main() -> None:
    cfg = ConduitConfig(kappa=0.85, golden_angle_steps=True)
    c = ToySpecializedConduit(kappa=cfg.kappa, golden_angle_steps=cfg.golden_angle_steps)
    print("rate λ≈κ:", c.characteristic_rate())
    print("steps @ λt=2, dt=0.001:", c.steps_to_lambda_t(2.0, 0.001))
    s, phase = c.golden_phase_at(0.0, step_index=5)
    print(f"golden step: s={s:.6f} phase={phase:.4f}")
    probe = c.run_survival_probe()
    print("identity_survival:", round(probe["identity_survival"], 6))
    print("ok")


if __name__ == "__main__":
    main()
