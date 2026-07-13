"""λt = 2 normalization and survival / residual analogs.

Source lineage: toe ``src/relaxation_survival.py`` (and identical copy in
invariant_hunt). This is the canonical home going forward.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from flux_hopf_lib.constants import (
    DEFAULT_KAPPA,
    DEFAULT_LAMBDA_T,
    E,
    E_INV2,
    GOLDEN_ANGLE_FRACTION,
    PHI,
    PHI_INV2,
    PI,
    R_RESIDUAL,
    theta_crit,
)
from flux_hopf_lib.quaternion.core import q_conj, q_mult, q_normalize, small_rotor
from flux_hopf_lib.simulation.relaxation import simulate_twist_pde

# Re-export constants used by mystery scripts that imported them from toe
__all_constants__ = (
    "PHI",
    "E",
    "PI",
    "R_RESIDUAL",
    "E_INV2",
    "GOLDEN_ANGLE_FRACTION",
    "PHI_INV2",
)


@dataclass
class SurvivalAnalogs:
    """Reference values for comparison tables."""

    r_residual: float = R_RESIDUAL
    e_inv2: float = E_INV2
    golden_angle_fraction: float = GOLDEN_ANGLE_FRACTION
    phi_inv2: float = PHI_INV2


@dataclass
class LambdaTNormalization:
    """Parameters for λt normalization (λ ≈ κ from mean-field gauge)."""

    lambda_t_target: float = DEFAULT_LAMBDA_T
    kappa: float = DEFAULT_KAPPA
    dt: float = 0.001
    characteristic_rate: float = field(init=False)
    t_physical: float = field(init=False)
    n_steps: int = field(init=False)

    def __post_init__(self) -> None:
        self.characteristic_rate = self.kappa
        self.t_physical = self.lambda_t_target / self.characteristic_rate
        self.n_steps = max(1, int(round(self.t_physical / self.dt)))


def steps_for_lambda_t(
    lambda_t_target: float = DEFAULT_LAMBDA_T,
    kappa: float = DEFAULT_KAPPA,
    dt: float = 0.001,
) -> int:
    """Discrete steps to reach λt = lambda_t_target with λ ≈ κ."""
    return LambdaTNormalization(
        lambda_t_target=lambda_t_target, kappa=kappa, dt=dt
    ).n_steps


def compare_to_analogs(
    measured: float,
    label: str = "survival",
    analogs: SurvivalAnalogs | None = None,
) -> dict[str, Any]:
    """Rank measured value against R, e^{−2}, and golden-angle fraction."""
    ref = analogs or SurvivalAnalogs()
    candidates = {
        "R_phi_e_pi": ref.r_residual,
        "e_inv2": ref.e_inv2,
        "golden_angle_over_1000": ref.golden_angle_fraction,
        "phi_inv2": ref.phi_inv2,
    }
    deltas = {name: abs(measured - val) for name, val in candidates.items()}
    best_name = min(deltas, key=deltas.get)  # type: ignore[arg-type]
    best_val = candidates[best_name]

    golden_delta_pct = (
        100.0 * abs(measured - ref.golden_angle_fraction) / abs(ref.golden_angle_fraction)
    )
    e_inv2_delta_pct = 100.0 * abs(measured - ref.e_inv2) / abs(ref.e_inv2)
    hybrid_delta_pct = 0.6 * golden_delta_pct + 0.4 * e_inv2_delta_pct
    golden_closeness = 1.0 / (1.0 + abs(measured - ref.golden_angle_fraction))
    e_inv2_closeness = 1.0 / (1.0 + abs(measured - ref.e_inv2))
    hybrid_score = 0.6 * golden_closeness + 0.4 * e_inv2_closeness

    return {
        "label": label,
        "measured": measured,
        "candidates": candidates,
        "best_match": best_name,
        "best_value": best_val,
        "delta_abs": deltas[best_name],
        "delta_pct_vs_best": 100.0 * deltas[best_name] / abs(best_val) if best_val else 0.0,
        "delta_pct_vs_R": 100.0 * abs(measured - ref.r_residual) / abs(ref.r_residual),
        "delta_pct_vs_e_inv2": e_inv2_delta_pct,
        "delta_pct_vs_golden": golden_delta_pct,
        "hybrid_delta_pct": hybrid_delta_pct,
        "hybrid_score": hybrid_score,
    }


def simulate_twist_pde_survival(
    nx: int = 20,
    nt: int | None = None,
    dt: float = 0.001,
    D: float = 0.05,
    kappa: float = DEFAULT_KAPPA,
    delta_omega: float = 0.002,
    theta_crit_val: float | None = None,
    seed: int = 42,
    normalize_to_lambda_t: float | None = DEFAULT_LAMBDA_T,
    track_interval: int = 50,
) -> dict[str, Any]:
    """
    Run twist-PDE relaxation, optionally stopping at λt = normalize_to_lambda_t.

    Returns survival fractions and analog comparison at the normalized horizon.
    """
    if theta_crit_val is None:
        theta_crit_val = theta_crit(kappa)

    norm: LambdaTNormalization | None = None
    if normalize_to_lambda_t is not None:
        norm = LambdaTNormalization(
            lambda_t_target=normalize_to_lambda_t,
            kappa=kappa,
            dt=dt,
        )
        nt = norm.n_steps
    if nt is None:
        nt = 2000

    result = simulate_twist_pde(
        nx=nx,
        nt=nt,
        dt=dt,
        D=D,
        kappa=kappa,
        delta_omega=delta_omega,
        theta_crit_val=theta_crit_val,
        seed=seed,
        track_interval=track_interval,
    )

    survival = result["survival"]
    comparisons = {
        "mean_survival": compare_to_analogs(survival["mean_survival"], "mean_survival"),
        "std_survival": compare_to_analogs(survival["std_survival"], "std_survival"),
        "fluctuation_survival": compare_to_analogs(
            survival["fluctuation_survival"], "fluctuation_survival"
        ),
    }

    return {
        "normalization": (
            {
                "lambda_t_target": norm.lambda_t_target,
                "kappa": norm.kappa,
                "dt": norm.dt,
                "characteristic_rate": norm.characteristic_rate,
                "t_physical": norm.t_physical,
                "n_steps": norm.n_steps,
                "note": "λ ≈ κ from mean-field gauge −κθ̄; survival at λt=2 should track e^{−2}",
            }
            if norm
            else None
        ),
        "pde_params": result["pde_params"],
        "survival": survival,
        "analog_comparisons": comparisons,
        "mean_history": result["mean_history"],
        "std_history": result["std_history"],
    }


def evolve_gauged_twist_survival(
    n_steps: int,
    kappa: float = DEFAULT_KAPPA,
    gauge_strength: float = 0.88,
    omega_L: float = 0.025,
    omega_R: float = 0.0225,
    n_identities: int = 96,
    seed: int = 42,
    normalize_to_lambda_t: float | None = None,
    dt: float = 1.0,
) -> dict[str, Any]:
    """
    Lightweight two-gyro gauged twist evolution (numpy) for survival probes.

    Identity survival = mean cosine similarity to initial random orientations
    after gauge-restoring steps — the discrete analog of exp(−λt) persistence.
    """
    if normalize_to_lambda_t is not None:
        n_steps = steps_for_lambda_t(normalize_to_lambda_t, kappa, dt)

    rng = np.random.default_rng(seed)
    current_q = np.array([1.0, 0.0, 0.0, 0.0])
    twist_history = np.array([0.0])
    identities = np.array([q_normalize(rng.standard_normal(4)) for _ in range(n_identities)])
    initial_identities = identities.copy()

    identity_survival_trace: list[float] = []
    pointer_trace: list[float] = []
    burst_count = 0
    t_crit = theta_crit(kappa)

    initial_twist = None
    for _ in range(n_steps):
        delta_L = small_rotor(omega_L)
        delta_R = small_rotor(omega_R)
        # q ← δ_L · q · δ_R†
        current_q = q_normalize(q_mult(q_mult(delta_L, current_q), q_conj(delta_R)))

        avg_imbalance = float(np.mean(twist_history) % (2 * PI))
        gauge_alpha = -gauge_strength * avg_imbalance - kappa * avg_imbalance * 0.1
        gauge_rot = np.array([np.cos(gauge_alpha), 0.0, 0.0, np.sin(gauge_alpha)])
        current_q = q_normalize(q_mult(current_q, gauge_rot))

        for i in range(n_identities):
            identities[i] = q_normalize(q_mult(gauge_rot, identities[i]))

        twist = 2.0 * np.arccos(np.clip(current_q[0], -1.0, 1.0))
        twist_history = np.append(twist_history, twist)
        if initial_twist is None and twist > 1e-6:
            initial_twist = twist

        cosines = np.sum(identities * initial_identities, axis=1)
        identity_survival_trace.append(float(np.mean(np.abs(cosines))))
        pointer_trace.append(float(np.tanh(gauge_alpha * 6.0)))

        if twist > t_crit:
            burst_count += 1

    final_identity_survival = identity_survival_trace[-1] if identity_survival_trace else 1.0
    identity_residual = 1.0 - final_identity_survival

    twist_survival = 1.0
    if initial_twist and initial_twist > 1e-8:
        twist_survival = float(twist_history[-1] / initial_twist)

    return {
        "n_steps": n_steps,
        "kappa": kappa,
        "gauge_strength": gauge_strength,
        "omega_L": omega_L,
        "omega_R": omega_R,
        "normalize_to_lambda_t": normalize_to_lambda_t,
        "lambda_t_achieved": kappa * n_steps * dt,
        "final_twist": float(twist_history[-1]),
        "twist_variance": float(np.var(twist_history)),
        "burst_count": burst_count,
        "identity_survival": final_identity_survival,
        "identity_residual": identity_residual,
        "twist_survival": twist_survival,
        "pointer_final": pointer_trace[-1] if pointer_trace else 0.0,
        "analog_comparison_residual": compare_to_analogs(identity_residual, "identity_residual"),
        "analog_comparison_survival": compare_to_analogs(
            final_identity_survival, "identity_survival"
        ),
        "analog_comparison_twist_survival": compare_to_analogs(twist_survival, "twist_survival"),
        "identity_survival_trace": identity_survival_trace[:: max(1, n_steps // 20)],
    }
