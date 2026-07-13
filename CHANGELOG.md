# Changelog

All notable changes to **flux-hopf-lib** are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Additional shared PDE / topological invariant helpers as they prove common across consumers

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

[Unreleased]: https://github.com/kinaar8340/flux_hopf_lib/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kinaar8340/flux_hopf_lib/releases/tag/v0.1.0
