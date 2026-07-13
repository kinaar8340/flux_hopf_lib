# Ecosystem map

```
                         flux_hopf_lib  (core, SoT)
                    quaternion · hopf · flux · simulation · conduit
                                      │
          ┌───────────────┬───────────┼───────────┬──────────────┐
          ▼               ▼           ▼           ▼              ▼
       mystery           toe      vqc_proto      hfb          kingdom
     φ-e-π probes   RubikCone     Orbital      flux bubbles   Gradio
     survival UI    gauged Hopf   Braille OAM  analog gravity  portal
                    flywheels     QEC/SLM      craft/BEC
```

## Responsibility split

| Layer | Package | Owns |
|-------|---------|------|
| Core | **flux_hopf_lib** | Constants, quaternions, Hopf maps, gauge/flux primitives, λt survival, PDE step, conduit mixins |
| Theory / lattice | **toe** | Full conduit NN stack, epoch clock, papers, Ray demos |
| Emergent signatures | **mystery** | Probes, residual synthesis, HF Space storytelling |
| Photonic VQC | **vqc_proto** | Encoding pipelines, LG/OAM, typehead, QEC stubs |
| Parent OAM stack | **vqc_sims_public** | Full L_max pipeline, knots, Isomap, patent-era public suite |
| Analog gravity | **hfb** | Bubbles, defects solvers, BEC, craft, optics export |
| Portal | **kingdom** | Unified visualization UX |

**HF Spaces** (install `flux-hopf-lib` via git URL in Space `requirements.txt`):

| Space | URL |
|-------|-----|
| Mystery | https://huggingface.co/spaces/kinaar111/mystery |
| Hopf Flux Bubble | https://huggingface.co/spaces/kinaar111/hopf-flux-bubble |
| Orbital Braille VQC | https://huggingface.co/spaces/kinaar111/orbital-braille-vqc |
| Kingdom Come | https://huggingface.co/spaces/kinaar111/kingdom |

## Versioning policy

- **Patch** (`0.1.x`): bugfixes, docs, tests; no API breaks.
- **Minor** (`0.x.0`): new modules / functions; deprecations allowed with re-exports.
- **Major** (`x.0.0`): breaking changes to κ defaults, residual definitions, or PDE conventions — bump consumers and note in paper reproduction scripts.

When changing `R_RESIDUAL`, `DEFAULT_KAPPA`, or λt conventions, tag a release and
update mystery RESULTS / notes so historical JSON remains interpretable.
