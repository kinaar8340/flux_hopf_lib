# Ecosystem map

## Dependency graph (authoritative)

All arrows point **to the core**. Sibling arrows are optional specialized
integrations only (never for shared math).

```
                         flux_hopf_lib  (core, SoT)
                    quaternion · hopf · flux · simulation · conduit
                                      │
          ┌───────────────┬───────────┼───────────┬──────────────┬──────────────┐
          ▼               ▼           ▼           ▼              ▼              ▼
       mystery           toe      vqc_proto      hfb          kingdom    vqc_sims_public
     φ-e-π probes   RubikCone     Orbital      flux bubbles   Gradio      parent OAM
     survival UI    gauged Hopf   Braille OAM  analog gravity  portal      L_max pipeline
       HF ✓         flywheels      HF ✓          HF ✓           HF ✓
```

## Responsibility split

| Layer | Package | Owns |
|-------|---------|------|
| Core | **flux_hopf_lib** | Constants, quaternions, Hopf maps, gauge/flux primitives, λt survival, PDE step, conduit mixins, grids |
| Core viz | **flux_hopf_lib[viz]** | Matplotlib + Plotly (HF-safe 2D dashboards, S² explorer, animations); geometry export for web |
| Premium 3D | **[flux-hopf-explorer](https://github.com/kinaar8340/flux_hopf_explorer)** | WebGPU / shaders.com / Three.js — loads `export_fiber_curves` JSON |
| Theory / lattice | **toe** | Full conduit NN stack, epoch clock, papers, Ray demos |
| Emergent signatures | **mystery** | Probes, residual synthesis, HF Space storytelling |
| Photonic VQC demos | **vqc_proto** | Encoding pipelines, LG/OAM, typehead, QEC stubs |
| Parent OAM stack | **vqc_sims_public** | Full L_max pipeline, knots, Isomap, patent-era public suite |
| Analog gravity | **hfb** | Bubbles, defects solvers, BEC, craft, optics export |
| Portal | **kingdom** | Unified visualization UX (consumes core viz; no WebGPU in core) |

See [VIZ.md](VIZ.md) for the full visualization architecture and roadmap.

## HF Spaces

Install `flux-hopf-lib` via git URL (or tag) in Space `requirements.txt`:

| Space | URL |
|-------|-----|
| Mystery | https://huggingface.co/spaces/kinaar111/mystery |
| Hopf Flux Bubble | https://huggingface.co/spaces/kinaar111/hopf-flux-bubble |
| Orbital Braille VQC | https://huggingface.co/spaces/kinaar111/orbital-braille-vqc |
| Kingdom Come | https://huggingface.co/spaces/kinaar111/kingdom |

## Versioning policy

- **Patch** (`0.1.x`): bugfixes, docs, tests; no API breaks.
- **Minor** (`0.x.0`): new modules / functions; deprecations allowed with re-exports.
- **Major** (`x.0.0`): breaking changes to κ defaults, residual definitions, or PDE conventions.

When changing `R_RESIDUAL`, `DEFAULT_KAPPA`, or λt conventions, **tag a release**
and update mystery RESULTS / notes so historical JSON remains interpretable.

Current baseline: **v0.2.2** (PyPI).

## Related docs

- [VIZ.md](VIZ.md) — core viz vs WebGPU companion architecture
- [DEPENDENCIES.md](DEPENDENCIES.md) — allowed/forbidden import directions
- [MIGRATION.md](MIGRATION.md) — per-repo import rewrites (mostly complete)
