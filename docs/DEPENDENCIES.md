# Dependency direction

**Rule:** every consumer depends on **`flux_hopf_lib`**. Consumers do **not**
depend on each other for shared math.

```
                    flux_hopf_lib  (foundation)
                           │
     ┌─────────┬───────────┼───────────┬──────────┬────────────┐
     ▼         ▼           ▼           ▼          ▼            ▼
  mystery     toe      vqc_proto      hfb     kingdom   vqc_sims_public
     │         │           │           │          │            │
     └─────────┴───────────┴───────────┴──────────┴────────────┘
              optional *sibling* integration only
         (e.g. hfb → vqc_proto for SLM LG modes,
          mystery → toe for full RubikConeConduit torch model)
```

## Allowed vs forbidden

| Allowed | Forbidden |
|---------|-----------|
| `from flux_hopf_lib.quaternion import Quaternion` | `sys.path` into `../toe/src` for survival math |
| `pip install -e ../flux_hopf_lib` or pin `==0.1.0` | Copy-paste of κ / R / Hopf map between repos |
| Sibling import of **specialized** models (conduit NN, LG typehead) | Sibling import for **core** primitives (quaternions, Hopf, λt, defects) |
| Thin re-export shims in consumers (`relaxation_survival`, `hfb.hopf`) | Divergent local copies of residual / κ defaults |

## Pinning

While iterating locally:

```bash
pip install -e ../flux_hopf_lib
```

For HF Spaces / paper reproduction:

```text
flux-hopf-lib @ git+https://github.com/kinaar8340/flux_hopf_lib.git@v0.1.0
# or once on PyPI:
# flux-hopf-lib==0.1.0
```

## Consumer → core mapping

| Consumer | Uses from core |
|----------|----------------|
| **mystery** | `simulation`, `constants` (survival, κ, R residual) |
| **toe** | `simulation` (via shim), `conduit` helpers/mixins, golden-angle |
| **vqc_proto** | `quaternion` (codec re-export) |
| **vqc_sims_public** | `quaternion` (via `quaternion_core` shim) |
| **hfb** | `hopf`, `flux.defects`, `utils.grid` |
| **kingdom** | `constants`, `hopf`, `quaternion` |

## Version bumps that force consumer updates

Changing any of these is a **semver event** — tag a release and note in
consumer RESULTS / papers:

- `DEFAULT_KAPPA`, `W_G_LOCK`, `theta_crit()`
- `R_RESIDUAL`, `E_INV2`, golden-angle fractions
- `simulate_twist_pde_survival` / λt conventions
- Hopf map formula / quaternion conventions
