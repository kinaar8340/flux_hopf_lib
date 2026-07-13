"""κ-parameter grids and survival sweeps used across mystery / toe probes."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray

from flux_hopf_lib.constants import DEFAULT_KAPPA, R_RESIDUAL
from flux_hopf_lib.simulation.survival import compare_to_analogs, simulate_twist_pde_survival

Array = NDArray[np.floating]


def kappa_grid(
    k_min: float = 0.80,
    k_max: float = 0.92,
    n: int = 25,
) -> NDArray[np.float64]:
    """Uniform κ grid (inclusive endpoints)."""
    return np.linspace(k_min, k_max, n)


def kappa_survival_curve(
    kappas: Array | None = None,
    *,
    nx: int = 16,
    seed: int = 42,
    normalize_to_lambda_t: float = 2.0,
    survival_key: str = "mean_survival",
    runner: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Sweep κ → survival fraction and distance to R residual.

    Default runner is the shared twist-PDE survival probe (small nx for tests).
    """
    if kappas is None:
        kappas = kappa_grid()
    kappas = np.asarray(kappas, dtype=float)
    run = runner or simulate_twist_pde_survival

    survivals: list[float] = []
    deltas_r: list[float] = []
    best_matches: list[str] = []

    for k in kappas:
        out = run(
            nx=nx,
            kappa=float(k),
            seed=seed,
            normalize_to_lambda_t=normalize_to_lambda_t,
        )
        s = float(out["survival"][survival_key])
        cmp_ = compare_to_analogs(s, survival_key)
        survivals.append(s)
        deltas_r.append(abs(s - R_RESIDUAL))
        best_matches.append(cmp_["best_match"])

    surv_arr = np.array(survivals)
    delta_arr = np.array(deltas_r)
    best_idx = int(np.argmin(delta_arr))

    return {
        "kappas": kappas.tolist(),
        "survivals": surv_arr.tolist(),
        "delta_vs_R": delta_arr.tolist(),
        "best_matches": best_matches,
        "best_kappa": float(kappas[best_idx]),
        "best_survival": float(surv_arr[best_idx]),
        "best_delta_R": float(delta_arr[best_idx]),
        "reference_kappa": DEFAULT_KAPPA,
        "R_residual": R_RESIDUAL,
        "survival_key": survival_key,
    }
