# flux_hopf_lib

[![PyPI](https://img.shields.io/pypi/v/flux-hopf-lib)](https://pypi.org/project/flux-hopf-lib/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flux-hopf-lib)](https://pypi.org/project/flux-hopf-lib/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/kinaar8340/flux_hopf_lib/actions/workflows/ci.yml/badge.svg)](https://github.com/kinaar8340/flux_hopf_lib/actions/workflows/ci.yml)

**Shared core library** for the Hopf / flux / quaternion / conduit ecosystem
([kinaar8340](https://github.com/kinaar8340)).

**Version:** [`0.2.2`](https://github.com/kinaar8340/flux_hopf_lib) · **Role:** single source of truth for foundational math.

Specialized experiments, Gradio portals, and full model stacks stay in consumer
repos. Consumers depend on **this package**, not on each other, for shared
primitives.

## Dependency direction

```text
                    flux_hopf_lib  (core / SoT)
                           │
     ┌─────────┬───────────┼───────────┬──────────┬────────────┐
     ▼         ▼           ▼           ▼          ▼            ▼
  mystery     toe      vqc_proto      hfb     kingdom   vqc_sims_public
   HF ✓                HF ✓         HF ✓     HF ✓      (parent OAM suite)
```

- **Allowed:** `from flux_hopf_lib…`, optional sibling imports of specialized models only.
- **Forbidden:** `sys.path` into `../toe` for survival/κ math; copy-pasted R residual / Hopf maps.

See [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md), [docs/ECOSYSTEM.md](docs/ECOSYSTEM.md),
and [docs/VIZ.md](docs/VIZ.md) (core Plotly/MPL vs WebGPU companion split).

## Install

```bash
# Editable (local ecosystem development)
cd ~/Projects/flux_hopf_lib
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Optional torch quaternion helpers
pip install -e ".[torch]"
```

**Consumer repos:**

```bash
# Production / HF Spaces / paper reproduction
pip install flux-hopf-lib==0.2.2

# Local core development (editable)
pip install -e ../flux_hopf_lib
```

```text
# requirements.txt / pyproject.toml / HF Space
flux-hopf-lib==0.2.2
```

- PyPI: https://pypi.org/project/flux-hopf-lib/
- Publishing: [docs/PUBLISHING.md](docs/PUBLISHING.md) · [CHANGELOG.md](CHANGELOG.md)

## Recommended import style

Keep the namespace **flat and predictable**:

```python
from flux_hopf_lib import PHI, R_RESIDUAL, E_INV2, DEFAULT_KAPPA
from flux_hopf_lib.quaternion import Quaternion, small_rotor, q_mult
from flux_hopf_lib.hopf import (
    hopf_map,
    hopf_map_from_angles,
    sample_fiber_family,
    stereographic_project,
    toroidal_hopfion_director,
    wg_from_base,
)
from flux_hopf_lib.flux import FluxLatticeConfig, FluxFlywheel, gaussian_defect
from flux_hopf_lib.simulation import (
    steps_for_lambda_t,
    evolve_gauged_twist_survival,
    simulate_twist_pde_survival,
    compare_to_analogs,
    zero_mode_survival_continuous,
)

# Optional visualizations (pip install 'flux-hopf-lib[viz]')
# from flux_hopf_lib.hopf.viz import (
#     plot_hopf_fibers_stereographic,
#     plot_hopf_fibers_dashboard,      # HF-safe 2×2 Plotly
#     plot_hopf_s2_fiber_explorer,    # S² base picker
#     create_plotly_fiber_animation,  # Play/Pause frames
# )
# Geometry export for a future WebGPU companion (no viz deps):
# from flux_hopf_lib.hopf import export_fiber_curves
from flux_hopf_lib.conduit import (
    ConduitConfig,
    GoldenAngleMixin,
    GaugePointerMixin,
    apply_golden_angle_increment,
)
from flux_hopf_lib.utils import cartesian_grid, laplacian_fft
```

Leaf repos may keep **thin re-export shims** for one release cycle
(`toe.relaxation_survival`, `hfb.hopf`, `orbital_braille.quaternion_codec`) so old
imports keep working while you migrate.

## Package layout

```text
src/flux_hopf_lib/
  constants.py          # φ, e, π, R residual, κ defaults, W_g lock
  quaternion/           # Quaternion, q_mult, rotors, encode_shard (+ torch_ops)
  hopf/                 # maps, fibers, stereographic, hopfions, invariants, viz
  flux/                 # FluxLatticeConfig, gauge steps, defect densities
  simulation/           # λt survival, twist PDE, mean-mode ODE, κ sweeps
  conduit/              # ConduitConfig, GoldenAngleMixin, GaugePointerMixin
  utils/                # cartesian/polar grids, FFT Laplacian
examples/
  quickstart.py
  consumer_mixin_pattern.py
  hopf_viz_demo.py      # requires [viz]
```

## Quick start

```bash
python examples/quickstart.py
```

```python
from flux_hopf_lib.simulation import steps_for_lambda_t, evolve_gauged_twist_survival

n = steps_for_lambda_t(lambda_t_target=2.0, kappa=0.85, dt=0.001)
out = evolve_gauged_twist_survival(n_steps=n, n_identities=32, seed=42)
print(out["identity_survival"])
```

## What belongs where

| In **flux_hopf_lib** (core) | In **leaf** repos |
|-----------------------------|-------------------|
| Quaternion / Rodrigues | Full `RubikConeConduit` + training (toe) |
| Hopf maps, hopfions, linking | VQC/OAM encoding, ICA demixing (vqc_*) |
| Flux lattice / gauge / defects | Analog-gravity / warp solvers (hfb) |
| λt survival, twist PDE, κ sweeps | Gradio / Streamlit UIs (kingdom, HF Spaces) |
| ConduitConfig + mixins | HF Space storytelling, papers, Ray demos |
| Grids / FFT Laplacian | |

## Migration status

| Repo | Status |
|------|--------|
| **mystery** | ✓ `flux_hopf_lib.simulation` (no toe path hacks for survival) |
| **toe** | ✓ `relaxation_survival` shim; golden-angle + GaugePointerMixin |
| **vqc_proto** | ✓ Quaternion codec re-export |
| **vqc_sims_public** | ✓ `quaternion_core` re-export |
| **hfb** | ✓ hopf / grid / defect shims |
| **kingdom** | ✓ constants + hopf + quaternion for portal demos |

Details: [docs/MIGRATION.md](docs/MIGRATION.md).

## Development workflow

1. Change foundational math **only** in this repo.
2. Run `pytest` and `python examples/quickstart.py`.
3. Update [CHANGELOG.md](CHANGELOG.md); bump version in `pyproject.toml` + `__init__.py`.
4. Tag a release (`v0.1.x` / `v0.2.0`); CI publishes via Trusted Publishing.
5. Consumers: `pip install -e ../flux_hopf_lib` while iterating; pin `==0.1.0` (PyPI) or `@v0.1.0` (git) for HF / papers.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Ecosystem links

| Repo | URL |
|------|-----|
| flux_hopf_lib | https://github.com/kinaar8340/flux_hopf_lib |
| toe | https://github.com/kinaar8340/toe |
| mystery | https://github.com/kinaar8340/mystery |
| hfb | https://github.com/kinaar8340/hfb |
| vqc_proto | https://github.com/kinaar8340/vqc_proto |
| vqc_sims_public | https://github.com/kinaar8340/vqc_sims_public |
| kingdom_come | https://github.com/kinaar8340/kingdom_come |
