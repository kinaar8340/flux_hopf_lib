# Visualization architecture

## Two-layer model

| Layer | Technology | Purpose | Status |
|-------|------------|---------|--------|
| **Core library** (`flux_hopf_lib[viz]`) | Python · Matplotlib · Plotly | Scientific reproducibility, Gradio / HF Spaces, Kingdom portal | **Official supported viz** |
| **Premium explorer** (companion) | WebGPU / shaders.com · Three.js (or similar) | Real-time 3D, large fiber counts, advanced effects | **[flux-hopf-explorer](https://github.com/kinaar8340/flux_hopf_explorer)** — **not** in core |

### Why separate?

- `flux_hopf_lib` stays a **lightweight pure-Python** scientific package.
- WebGPU / shaders.com would drag heavy frontend deps into the core that most consumers never need.
- Matplotlib + Plotly already power Kingdom Come and HF Spaces reliably (including HF-safe 2D Plotly without WebGL).

```
  flux_hopf_lib
  ├── hopf.fibration     geometry + export_fiber_curves  ──┐
  └── hopf.viz [viz]     matplotlib / plotly              │
                                                          │ JSON / arrays
  companion                                               │
  └── flux-hopf-explorer  ◄── Three.js / WebGPU / shaders.com ──┘
```

## Core `[viz]` roadmap

1. **Animation** — `animate_hopf_fibers` (matplotlib), `create_plotly_fiber_animation` (Plotly frames)
2. **S² explorer** — hover metadata, linked legend groups, LOD + cache
3. **Large families** — `lod_n_points`, `apply_fiber_lod`, vectorized `sample_fiber_family`, `sample_fiber_family_cached`
4. **Web export** — `export_fiber_curves` payload for companion frontends

## API quick reference

```python
# Geometry (no viz deps)
from flux_hopf_lib.hopf import (
    sample_fiber_family,
    sample_fiber_family_cached,
    lod_n_points,
    apply_fiber_lod,
    export_fiber_curves,   # → WebGPU / Three.js
)

# Optional plotting
from flux_hopf_lib.hopf.viz import (
    plot_hopf_fibers_stereographic,
    plot_hopf_fibers_dashboard,      # HF-safe 2×2
    plot_hopf_s2_fiber_explorer,    # S² picker
    animate_hopf_fibers,            # matplotlib FuncAnimation
    create_plotly_fiber_animation,  # Plotly play/pause frames
)
```

### Animation modes

| Mode | Behavior |
|------|----------|
| `xi1_orbit` | Highlight fiber base walks around S² (ξ₁) |
| `eta_breath` | Highlight latitude η oscillates |
| `gauge_twist` | Phase marker advances along the fiber (ξ₂) |
| `hopfion_spin` | Director field rotation (matplotlib; Plotly falls back to `eta_breath`) |

### Companion WebGPU path (long-term)

1. Keep exporting fiber data from core via `export_fiber_curves` (stereographic `xyz`, optional S³, S² base).
2. Build a **separate** web app or HF Space that loads that JSON/array payload and renders with shaders.com + WebGPU / Three.js.
3. Never import WebGPU SDKs into `flux_hopf_lib`.

This matches the research-code vs demo-frontend split used by many scientific stacks.

## HF / Gradio policy

- Prefer **2D Plotly** (`plot_hopf_fibers_dashboard`, `plot_hopf_s2_fiber_explorer`, `create_plotly_fiber_animation`) on Spaces.
- Force 2D in Kingdom when `SPACE_ID` is set (see kingdom `hopf_plotly.resolve_view_mode`).
- Use LOD automatically for large `n_fibers` so browser plot payloads stay small.

## Related

- [ECOSYSTEM.md](ECOSYSTEM.md) — dependency graph
- [DEPENDENCIES.md](DEPENDENCIES.md) — import directions
- `examples/hopf_viz_demo.py` — static + optional HTML/animation smoke
