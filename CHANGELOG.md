# Changelog

All notable changes to **flux-hopf-lib** are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Companion WebGPU / shaders.com explorer consuming `export_fiber_curves` (scaffolded)

## [0.2.6] — 2026-07-12

### Fixed
- **gauge_twist** looked frozen (η/ξ₁ fixed; only a tiny phase marker moved). Now draws a
  growing red phase trail + large diamond head so motion is obvious.
- Stronger **gauge_evolution** breathing amplitude; clearer **twist** family spin offsets.

## [0.2.5] — 2026-07-12

### Added / Changed
- **Production animation API:** `create_hopf_fiber_animation_frames` now first-class supports
  `twist` (z-rotation of fiber family) and `gauge_evolution` (κ radial breathing), plus
  highlight modes (`xi1_orbit`, `eta_breath`, `gauge_twist`)
- Tunables: `opacity`, `line_width`; fixed axis ranges; HF-safe 2D stereographic figures
- Gradio pattern: bake → `gr.State` (plotly JSON) → slider index (instant scrub)

## [0.2.4] — 2026-07-12

### Added
- **hopf/viz.py**: `create_hopf_fiber_animation_frames` — precomputed Plotly figure list (Gradio slider path)
- **hopf/viz.py**: `plot_hopf_fiber_animation_slider` — frames + selected figure + meta
- **hopf/viz.py**: `export_hopf_fiber_animation_mp4` — kaleido + imageio video export for `gr.Video`
- Fixed axis ranges across frames for stable scrubbing; mode aliases (`twist`, `gauge_evolution`, …)

### Notes
- Kingdom Animate uses bake-once + instant frame index (not re-sample per tick).

## [0.2.3] — 2026-07-12

### Fixed
- **hopf/viz.py**: Plotly fiber animation Play reliability — full frame data, explicit frame list, `mode: immediate`
- **hopf/viz.py**: `plotly_fig_to_html` helper for Gradio/HF (``gr.Plot`` drops working `Plotly.animate`)

### Notes
- Kingdom Animate view embeds HTML, not `gr.Plot`, so ▶ Play works on Spaces.

## [0.2.2] — 2026-07-12

Visualization layer push: animation, LOD/cache, explorer polish, web export.

### Added
- **hopf/fibration.py**: vectorized `sample_fiber_family`; `sample_fiber_family_cached` + `clear_fiber_family_cache`
- **hopf/fibration.py**: `lod_n_points`, `downsample_curve`, `apply_fiber_lod` for large families
- **hopf/fibration.py**: `export_fiber_curves` — JSON-friendly payload for WebGPU / Three.js companions
- **hopf/viz.py**: `animate_hopf_fibers` (matplotlib) and `create_plotly_fiber_animation` (Play/Pause frames)
- Animation modes: `xi1_orbit`, `eta_breath`, `gauge_twist`, `hopfion_spin`
- **docs/VIZ.md** — two-layer architecture (core Plotly/MPL vs premium WebGPU companion)

### Changed
- `plot_hopf_s2_fiber_explorer`: richer hover tooltips, dim unselected fibers, optional LOD + cache

## [0.2.1] — 2026-07-12

HF-safe Plotly dashboards and interactive S² fiber explorer.

### Added
- **hopf/viz.py**: `plot_hopf_fibers_dashboard` — 2×2 WebGL-free multi-panel (xy, xz, S² base, highlight phase)
- **hopf/viz.py**: `plot_hopf_s2_fiber_explorer` — stereographic + S² disk with `customdata` for Gradio/Dash selection
- **hopf/viz.py**: `s2_to_hopf_angles`, `fiber_family_choices` helpers for portal dropdown UIs
- Theme dict support on new Plotly builders (kingdom dark theme passthrough)

### Notes
- Consumers / HF Spaces that use the kingdom Hopf portal should pin `flux-hopf-lib==0.2.1` (or newer).

## [0.2.0] — 2026-07-13

Hopf visualization + fiber sampling, invariants, and PDE mean-mode helpers.

### Added
- **hopf/** fiber toolkit: `stereographic_project`, `sample_fiber`, `sample_fiber_family`, `base_sphere_mesh`, `hopf_map_quaternion`, `fiber_linking_number`
- **hopf/invariants.py**: `wg_from_base`, `wg_relative_residual`, `holonomy_phase_proxy`, `fiber_pair_diagnostics`
- **hopf/viz.py** (extra `[viz]`): stereographic 3D fibers, multi-view 2D projections, Hopfion director quiver, linking curves (matplotlib + plotly backends)
- **simulation/**: `mean_cot_grad_flux`, `zero_mode_survival_euler`, `zero_mode_survival_continuous`
- **flux/**: `mean_field_gauge_torque`, `pointer_damping`, `lambda_from_kappa` / `kappa_from_lambda`
- Example: `examples/hopf_viz_demo.py`

### Changed
- `[viz]` extra now includes `plotly>=5.0` in addition to matplotlib

## [0.1.0] — 2026-07-13

Initial public foundation for the Hopf / flux / quaternion / conduit ecosystem.

### Added
- **constants** — φ, e, π, R residual, e⁻², golden-angle, DEFAULT_KAPPA, W_G_LOCK, θ_crit
- **quaternion** — unit `Quaternion`, Hamilton product, rotors, Rodrigues, encode/decode shard; optional torch ops
- **hopf** — S³ coordinates, Hopf map, linking number, hopfion directors
- **flux** — `FluxLatticeConfig`, two-gyro gauge step, `FluxFlywheel`, defect densities
- **simulation** — λt normalization, survival analogs, twist PDE, κ sweeps
- **conduit** — `ConduitConfig`, `GoldenAngleMixin`, `GaugePointerMixin`, golden-angle increment
- **utils** — cartesian/polar grids, FFT Laplacian, gradients
- Packaging: hatchling `src/` layout, optional extras `[dev]`, `[torch]`, `[viz]`
- Docs: README, DEPENDENCIES, ECOSYSTEM, MIGRATION
- Examples: `quickstart.py`, `consumer_mixin_pattern.py`
- CI: test workflow; Trusted Publishing workflows for TestPyPI + PyPI

### Notes
- Consumer repos and HF Spaces pin `@v0.1.0` (git) until PyPI install is preferred.
- Breaking changes to κ / R / PDE conventions require a minor or major bump and pin updates.

[Unreleased]: https://github.com/kinaar8340/flux_hopf_lib/compare/v0.2.5...HEAD
[0.2.5]: https://github.com/kinaar8340/flux_hopf_lib/releases/tag/v0.2.5
[0.2.4]: https://github.com/kinaar8340/flux_hopf_lib/releases/tag/v0.2.4
[0.2.3]: https://github.com/kinaar8340/flux_hopf_lib/releases/tag/v0.2.3
[0.2.2]: https://github.com/kinaar8340/flux_hopf_lib/releases/tag/v0.2.2
[0.2.1]: https://github.com/kinaar8340/flux_hopf_lib/releases/tag/v0.2.1
[0.2.0]: https://github.com/kinaar8340/flux_hopf_lib/releases/tag/v0.2.0
[0.1.0]: https://github.com/kinaar8340/flux_hopf_lib/releases/tag/v0.1.0
