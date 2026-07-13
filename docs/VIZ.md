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

1. **Animation (recommended)** — `create_hopf_fiber_animation_frames` + Gradio slider (precomputed Plotly figures)
2. **Animation (native Plotly)** — `create_plotly_fiber_animation` (client Play often broken under `gr.Plot`)
3. **Animation (export)** — `export_hopf_fiber_animation_mp4` for `gr.Video` / offline
4. **S² explorer** — hover metadata, linked legend groups, LOD + cache
5. **Large families** — `lod_n_points`, `apply_fiber_lod`, vectorized sampling + cache
6. **Web export** — `export_fiber_curves` payload for companion frontends

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
    plot_hopf_fibers_dashboard,           # HF-safe 2×2
    plot_hopf_s2_fiber_explorer,         # S² picker
    create_hopf_fiber_animation_frames,  # ★ Gradio: bake once, scrub
    plot_hopf_fiber_animation_slider,    # frames + selected + meta
    export_hopf_fiber_animation_mp4,     # gr.Video / offline
    animate_hopf_fibers,                 # matplotlib (avoid in Gradio)
    create_plotly_fiber_animation,       # native Play (often broken in gr.Plot)
)
```

### Gradio animation pattern (best quality on Spaces)

```python
frames = create_hopf_fiber_animation_frames(n_fibers=12, n_frames=60, mode="xi1_orbit")
frame_slider.change(lambda i: frames[int(i)], inputs=slider, outputs=plot)
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

- Prefer **2D Plotly** dashboards / explorers on Spaces.
- **Animations:** precompute with `create_hopf_fiber_animation_frames` and scrub via `gr.Slider` (not Matplotlib FuncAnimation; not client Play under `gr.Plot`).
- Optional high-quality offline: `export_hopf_fiber_animation_mp4` → `gr.Video`.
- Force 2D in Kingdom when `SPACE_ID` is set.
- Use LOD for large `n_fibers` so plot payloads stay small.

## Related

- [ECOSYSTEM.md](ECOSYSTEM.md) — dependency graph
- [DEPENDENCIES.md](DEPENDENCIES.md) — import directions
- `examples/hopf_viz_demo.py` — static + optional HTML/animation smoke
