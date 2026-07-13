"""Twist-field PDE primitives on the 3-torus.

Source lineage: toe ``scripts/pde_relaxation.py`` and
``src/relaxation_survival.simulate_twist_pde_survival``.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from flux_hopf_lib.constants import DEFAULT_KAPPA, PI, theta_crit

Array = NDArray[np.floating]


def twist_pde_step(
    theta: Array,
    *,
    dt: float = 0.001,
    D: float = 0.05,
    kappa: float = DEFAULT_KAPPA,
    delta_omega: float = 0.002,
    theta_crit_val: float | None = None,
    nx: int | None = None,
) -> Array:
    """Single finite-difference step of the nonlinear twist PDE.

    ∂θ/∂t = D Δθ + (D/2) cot(θ/2) |∇θ|² + Δω − κ θ̄ + B(θ)
    """
    if theta_crit_val is None:
        theta_crit_val = theta_crit(kappa)
    if nx is None:
        nx = theta.shape[0]

    lap = (
        np.roll(theta, 1, 0)
        + np.roll(theta, -1, 0)
        + np.roll(theta, 1, 1)
        + np.roll(theta, -1, 1)
        + np.roll(theta, 1, 2)
        + np.roll(theta, -1, 2)
        - 6 * theta
    ) / (1.0 / nx) ** 2

    with np.errstate(divide="ignore", invalid="ignore"):
        cot_term = (
            (D / 2.0)
            * np.cos(theta / 2.0)
            / np.maximum(np.sin(theta / 2.0), 1e-8)
            * (
                np.gradient(theta, axis=0) ** 2
                + np.gradient(theta, axis=1) ** 2
                + np.gradient(theta, axis=2) ** 2
            ).sum(axis=0)
        )

    bar_theta = float(theta.mean())
    gauge = -kappa * bar_theta
    burst = np.where(theta > theta_crit_val, -50.0 * (theta - theta_crit_val), 0.0)
    theta = theta + dt * (D * lap + cot_term + delta_omega + gauge + burst)
    return np.clip(theta, 0.01, 2 * PI - 0.01)


def simulate_twist_pde(
    nx: int = 20,
    nt: int = 2000,
    dt: float = 0.001,
    D: float = 0.05,
    kappa: float = DEFAULT_KAPPA,
    delta_omega: float = 0.002,
    theta_crit_val: float | None = None,
    seed: int = 42,
    track_interval: int = 50,
    theta0: Array | None = None,
) -> dict[str, Any]:
    """Evolve the twist PDE; return survival stats and histories."""
    if theta_crit_val is None:
        theta_crit_val = theta_crit(kappa)

    rng = np.random.default_rng(seed)
    if theta0 is None:
        theta = rng.uniform(0.1, 2.0, (nx, nx, nx))
    else:
        theta = np.array(theta0, dtype=float, copy=True)

    theta0_mean = float(theta.mean())
    theta0_std = float(theta.std())
    theta0_fluct = float(np.sqrt(np.mean((theta - theta0_mean) ** 2)))

    mean_history: list[float] = []
    std_history: list[float] = []
    fluct_history: list[float] = []

    for step in range(nt):
        theta = twist_pde_step(
            theta,
            dt=dt,
            D=D,
            kappa=kappa,
            delta_omega=delta_omega,
            theta_crit_val=theta_crit_val,
            nx=nx,
        )
        if step % track_interval == 0 or step == nt - 1:
            bar = float(theta.mean())
            mean_history.append(bar)
            std_history.append(float(theta.std()))
            fluct_history.append(float(np.sqrt(np.mean((theta - bar) ** 2))))

    final_mean = float(theta.mean())
    final_std = float(theta.std())
    final_fluct = float(np.sqrt(np.mean((theta - final_mean) ** 2)))

    def safe_ratio(num: float, denom: float) -> float:
        return float(num / denom) if abs(denom) > 1e-12 else 0.0

    survival = {
        "mean_survival": safe_ratio(final_mean, theta0_mean),
        "std_survival": safe_ratio(final_std, theta0_std),
        "fluctuation_survival": safe_ratio(final_fluct, theta0_fluct),
        "theoretical_e_inv2": float(np.exp(-2.0)),
        "theta0_mean": theta0_mean,
        "final_mean": final_mean,
        "final_std": final_std,
    }

    return {
        "pde_params": {
            "nx": nx,
            "nt": nt,
            "dt": dt,
            "D": D,
            "kappa": kappa,
            "delta_omega": delta_omega,
            "theta_crit": theta_crit_val,
            "seed": seed,
        },
        "survival": survival,
        "mean_history": mean_history,
        "std_history": std_history,
        "fluct_history": fluct_history,
        "theta_final": theta,
    }
