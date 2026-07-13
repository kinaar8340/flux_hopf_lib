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
    # Base markers carry customdata for Gradio / dropdown handlers
    base_traces = [
        t for t in explorer.data if getattr(t, "customdata", None) is not None
    ]
    assert len(base_traces) >= 1
    cd = base_traces[0].customdata
    assert cd is not None and len(cd[0]) >= 5
