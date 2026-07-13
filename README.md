# flux_hopf_lib

**Shared core library** for the Hopf / flux / quaternion / conduit ecosystem
([kinaar8340](https://github.com/kinaar8340)).

This package is the **single source of truth** for foundational math and shared
probes. Specialized experiments, Gradio portals, and full model stacks stay in
consumer repos (`toe`, `mystery`, `vqc_proto`, `hfb`, `kingdom`, …).

## Why this exists

Across the ecosystem the same ideas appear repeatedly:

| Theme | Where it lived before | Now |
|-------|----------------------|-----|
| Quaternion ops / rotors | toe `conduit.py`, vqc_proto `quaternion_codec` | `flux_hopf_lib.quaternion` |
| Hopf map / hopfions | hfb `hopf/` | `flux_hopf_lib.hopf` |
| Flux lattice / gauge / defects | toe + hfb | `flux_hopf_lib.flux` |
| λt survival, κ, twist PDE | toe `relaxation_survival.py` (path-hacked by mystery) | `flux_hopf_lib.simulation` |
| Conduit base / golden-angle | toe `conduit.py` helpers | `flux_hopf_lib.conduit` |

Consumer repos install this package instead of `sys.path` hacks into sibling
checkouts.

## Install

```bash
# Editable (development — recommended while the ecosystem is in flux)
cd ~/Projects/flux_hopf_lib
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Optional torch quaternion helpers
pip install -e ".[torch]"
```

From another repo during active development:

```bash
# requirements.txt
-e ../flux_hopf_lib

# or pyproject.toml
# dependencies = ["flux-hopf-lib @ file:///${PROJECT_ROOT}/../flux_hopf_lib"]
pip install -e ../flux_hopf_lib
```

Pinned release (after publishing):

```text
flux-hopf-lib==0.1.0
```

## Package layout

```text
src/flux_hopf_lib/
  constants.py          # φ, e, π, R residual, κ defaults, W_g lock
  quaternion/           # Quaternion, q_mult, rotors, encode_shard (+ torch_ops)
  hopf/                 # Hopf map, linking, hopfion directors
  flux/                 # FluxLatticeConfig, gauge steps, defect densities
  simulation/           # λt normalization, survival, twist PDE, κ sweeps
  conduit/              # ConduitConfig, GoldenAngleMixin, GaugePointerMixin
  utils/                # cartesian/polar grids, FFT Laplacian
```

## Quick start

```python
from flux_hopf_lib import PHI, R_RESIDUAL, E_INV2, DEFAULT_KAPPA
from flux_hopf_lib.quaternion import Quaternion, small_rotor, q_mult
from flux_hopf_lib.hopf import hopf_map_from_angles
from flux_hopf_lib.flux import FluxLatticeConfig, FluxFlywheel
from flux_hopf_lib.simulation import (
    steps_for_lambda_t,
    simulate_twist_pde_survival,
    evolve_gauged_twist_survival,
    compare_to_analogs,
)
from flux_hopf_lib.conduit import apply_golden_angle_increment, ConduitConfig

# Survival horizon at λt = 2
n = steps_for_lambda_t(lambda_t_target=2.0, kappa=0.85, dt=0.001)

# Lightweight gauged-twist probe (numpy)
out = evolve_gauged_twist_survival(n_steps=200, n_identities=32, seed=42)
print(out["identity_survival"], compare_to_analogs(out["identity_residual"]))

# Twist PDE on a small T³ (for tests; use larger nx in research scripts)
pde = simulate_twist_pde_survival(nx=12, normalize_to_lambda_t=2.0, seed=0)
print(pde["survival"]["mean_survival"], "vs e^{-2} =", E_INV2)
```

## What stays in consumer repos

| Repo | Keeps |
|------|--------|
| **toe** | Full `RubikConeConduit` / `TwistedHelicalConduit` (torch, Ray, TNN stack), training configs, papers |
| **mystery** | φ-e-π analysis scripts, Gradio space, synthesis notes — import survival/κ from this lib |
| **vqc_proto** | Orbital Braille pipelines, LG modes, QEC, typehead SLM |
| **hfb** | Analog gravity, BEC, craft, electro-vibrational, bubble solvers |
| **kingdom** | Unifying Gradio portal / visualization |

## Migration order

1. **mystery** (biggest path-hack pain → toe)
2. **toe** (re-export or thin-wrap core; keep full conduit classes)
3. **vqc_proto** / **vqc_sims_public**
4. **hfb**
5. **kingdom**

See [docs/MIGRATION.md](docs/MIGRATION.md) for concrete import rewrites.

## Development workflow

```text
                    ┌─────────────────────┐
                    │   flux_hopf_lib     │  ← single source of truth
                    │   (this package)    │
                    └──────────┬──────────┘
           pip install -e .    │
     ┌─────────────┬───────────┼───────────┬──────────────┐
     ▼             ▼           ▼           ▼              ▼
   mystery        toe      vqc_proto      hfb          kingdom
  (probes)     (conduit)   (OAM/VQC)   (bubbles)      (portal)
```

- Evolve foundational math **only** here.
- Bump version when κ defaults, residual formulas, or PDE conventions change.
- Prefer editable installs while iterating; pin versions for HF Spaces / papers.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Ecosystem

| Repo | URL |
|------|-----|
| toe | https://github.com/kinaar8340/toe |
| mystery | https://github.com/kinaar8340/mystery |
| hfb | https://github.com/kinaar8340/hfb |
| vqc_proto | https://github.com/kinaar8340/vqc_proto |
| kingdom | https://github.com/kinaar8340/kingdom (local portal) |
