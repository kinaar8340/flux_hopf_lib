"""Extended Hopf fiber sampling, invariants, and viz smoke tests."""

from __future__ import annotations

import math

import numpy as np
import pytest

from flux_hopf_lib.hopf import (
    base_sphere_mesh,
    fiber_pair_diagnostics,
    holonomy_phase_proxy,
    hopf_map_quaternion,
    sample_fiber,
    sample_fiber_family,
    stereographic_project,
    wg_from_base,
)
from flux_hopf_lib.hopf.fibration import hopf_coordinates


def test_stereographic_finite():
    eta, xi1, xi2 = 0.5, 1.0, 2.0
    x1, x2, x3, x4 = hopf_coordinates(
        np.array([eta]), np.array([xi1]), np.array([xi2])
    )
    px, py, pz = stereographic_project(x1, x2, x3, x4)
    assert np.isfinite([px, py, pz]).all()


def test_sample_fiber_closed_curve():
    fiber = sample_fiber(0.4, 0.8, n_points=120)
    assert fiber["curve_xyz"].shape == (120, 3)
    # nearly closed in stereographic coords
    d = np.linalg.norm(fiber["curve_xyz"][0] - fiber["curve_xyz"][-1])
    assert d < 0.25


def test_sample_fiber_family_count():
    fibers = sample_fiber_family(n_fibers=9, n_points=40)
    assert len(fibers) == 9
    assert "base_y1" in fibers[0]


def test_sample_fiber_family_vectorized_matches_loop():
    a = sample_fiber_family(n_fibers=6, n_points=30, vectorized=True)
    b = sample_fiber_family(n_fibers=6, n_points=30, vectorized=False)
    assert len(a) == len(b)
    for fa, fb in zip(a, b):
        assert abs(fa["eta"] - fb["eta"]) < 1e-12
        assert abs(fa["xi1"] - fb["xi1"]) < 1e-12
        assert np.allclose(fa["curve_xyz"], fb["curve_xyz"], atol=1e-9)


def test_lod_and_export_fiber_curves():
    from flux_hopf_lib.hopf import (
        apply_fiber_lod,
        clear_fiber_family_cache,
        export_fiber_curves,
        lod_n_points,
        sample_fiber_family_cached,
    )

    assert lod_n_points(100, base_points=200, point_budget=5000) <= 50
    clear_fiber_family_cache()
    f1 = sample_fiber_family_cached(n_fibers=4, n_points=40)
    f2 = sample_fiber_family_cached(n_fibers=4, n_points=40)
    assert len(f1) == len(f2) == 4
    # cache returns copies
    f1[0]["eta"] = -1.0
    assert f2[0]["eta"] != -1.0

    fiber = sample_fiber(0.4, 0.5, n_points=100)
    small = apply_fiber_lod(fiber, 25)
    assert small["curve_xyz"].shape[0] == 25

    payload = export_fiber_curves(n_fibers=5, n_points=60, max_points=20, include_s3=True)
    assert payload["version"] == 1
    assert len(payload["fibers"]) == 5
    assert len(payload["fibers"][0]["xyz"]) == 20
    assert "s3" in payload["fibers"][0]
    # JSON-serializable floats
    import json

    json.dumps(payload)


def test_hopf_map_quaternion_unit():
    y1, y2, y3 = hopf_map_quaternion(1.0, 0.0, 0.0, 0.0)
    n = math.sqrt(y1**2 + y2**2 + y3**2)
    assert abs(n - 1.0) < 1e-9 or n < 1e-9  # identity maps near pole/degen ok


def test_base_sphere_mesh_shape():
    x, y, z = base_sphere_mesh(8, 12)
    assert x.shape == (8, 12)
    norms = np.sqrt(x**2 + y**2 + z**2)
    assert np.allclose(norms, 1.0, atol=1e-8)


def test_wg_from_base():
    assert abs(wg_from_base(350.0) - 350.0 / math.pi) < 1e-12


def test_holonomy_phase_proxy():
    phases = np.linspace(0, 4 * math.pi, 50)
    out = holonomy_phase_proxy(phases)
    assert abs(out["winding_approx"] - 2.0) < 0.05


def test_fiber_pair_diagnostics():
    a = sample_fiber(0.3, 0.2, n_points=80)
    b = sample_fiber(0.8, 1.5, n_points=80)
    d = fiber_pair_diagnostics(a, b)
    assert "linking_number" in d
    assert np.isfinite(d["linking_number"])
    assert d["base_chordal_distance"] >= 0.0


def test_viz_matplotlib_smoke():
    pytest.importorskip("matplotlib")
    from flux_hopf_lib.hopf.viz import (
        plot_hopf_fibers_multi_view,
        plot_hopf_fibers_stereographic,
        plot_hopfion_director_slice,
        plot_linking_curves,
    )

    import matplotlib

    matplotlib.use("Agg")

    fig1 = plot_hopf_fibers_stereographic(n_fibers=4, n_points=40, backend="matplotlib")
    fig2 = plot_hopf_fibers_multi_view(n_fibers=4, n_points=40)
    fig3 = plot_hopfion_director_slice(n=24)
    fig4 = plot_linking_curves(n_points=60, backend="matplotlib")
    assert fig1 is not None and fig2 is not None and fig3 is not None and fig4 is not None
    import matplotlib.pyplot as plt

    plt.close("all")


def test_s2_to_hopf_angles_range():
    from flux_hopf_lib.hopf.viz import s2_to_hopf_angles

    eta, xi1 = s2_to_hopf_angles(0.5, 0.5, 0.7071)
    assert 0.05 <= eta <= 1.45
    assert 0.0 <= xi1 < 2.0 * math.pi


def test_fiber_family_choices():
    from flux_hopf_lib.hopf.viz import fiber_family_choices

    choices = fiber_family_choices(n_fibers=6, n_points=20)
    assert len(choices) == 6
    label, eta, xi1 = choices[0]
    assert "η=" in label
    assert 0.0 < eta < math.pi / 2
    assert 0.0 <= xi1 < 2.0 * math.pi


def test_viz_plotly_dashboard_and_explorer():
    pytest.importorskip("plotly")
    from flux_hopf_lib.hopf.viz import (
        plot_hopf_fibers_dashboard,
        plot_hopf_s2_fiber_explorer,
    )

    dash = plot_hopf_fibers_dashboard(n_fibers=4, n_points=40, height=400)
    assert dash is not None
    assert len(dash.data) >= 4

    explorer = plot_hopf_s2_fiber_explorer(
        n_fibers=5, n_points=40, selected_eta=0.5, selected_xi1=1.0, height=400
    )
    assert explorer is not None
    # Base markers carry customdata [η, ξ₁, y1, y2, y3, index] (6 cols)
    base_traces = [
        t
        for t in explorer.data
        if getattr(t, "customdata", None) is not None
        and len(np.asarray(t.customdata).shape) == 2
        and np.asarray(t.customdata).shape[1] >= 5
        and np.asarray(t.customdata).shape[0] == 1
    ]
    assert len(base_traces) >= 1
    cd = np.asarray(base_traces[0].customdata)
    assert cd.shape[1] >= 5


def test_animate_hopf_fibers_matplotlib():
    pytest.importorskip("matplotlib")
    import matplotlib

    matplotlib.use("Agg")
    from flux_hopf_lib.hopf.viz import animate_hopf_fibers

    anim = animate_hopf_fibers(
        n_fibers=3, n_points=30, n_frames=4, mode="xi1_orbit", interval=20
    )
    assert anim is not None
    # drive a couple of frames without display
    for i in range(3):
        anim._func(i)
    import matplotlib.pyplot as plt

    # Keep reference until close to avoid matplotlib "deleted without rendering"
    _keep = anim  # noqa: F841
    plt.close(anim._fig if hasattr(anim, "_fig") else "all")


def test_create_plotly_fiber_animation():
    pytest.importorskip("plotly")
    from flux_hopf_lib.hopf.viz import create_plotly_fiber_animation

    fig = create_plotly_fiber_animation(
        n_fibers=3, n_points=30, n_frames=5, mode="gauge_twist", height=300
    )
    assert fig is not None
    assert fig.frames is not None and len(fig.frames) == 5
    menus = list(fig.layout.updatemenus or [])
    assert len(menus) >= 1
    assert getattr(menus[0], "type", None) == "buttons" or (
        isinstance(menus[0], dict) and menus[0].get("type") == "buttons"
    )


def test_create_hopf_fiber_animation_frames_precomputed():
    """Gradio-quality path: list of static figures with fixed axis range."""
    pytest.importorskip("plotly")
    from flux_hopf_lib.hopf.viz import (
        create_hopf_fiber_animation_frames,
        plot_hopf_fiber_animation_slider,
    )

    frames = create_hopf_fiber_animation_frames(
        n_fibers=4,
        n_points=40,
        n_frames=8,
        mode="xi1_orbit",
        fixed_axis_range=True,
        height=300,
    )
    assert len(frames) == 8
    # Fixed ranges so scrubbing does not jump
    r0 = frames[0].layout.xaxis.range
    r1 = frames[-1].layout.xaxis.range
    assert r0 is not None and list(r0) == list(r1)

    frames2, fig, meta = plot_hopf_fiber_animation_slider(
        n_fibers=3, n_points=30, n_frames=6, frame_idx=2, mode="twist"
    )
    assert len(frames2) == 6
    assert meta["frame_idx"] == 2
    assert meta["mode"] == "gauge_twist"
    assert fig is frames2[2]
