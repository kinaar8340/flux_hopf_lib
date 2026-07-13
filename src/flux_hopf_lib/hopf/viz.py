"""Hopf fibration visualization (matplotlib required; plotly optional).

Install::

    pip install 'flux-hopf-lib[viz]'

Pure geometry stays in ``flux_hopf_lib.hopf.fibration``; this module only plots.
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np

from flux_hopf_lib.hopf.fibration import (
    apply_fiber_lod,
    base_sphere_mesh,
    fiber_linking_number,
    lod_n_points,
    sample_fiber,
    sample_fiber_family,
    sample_fiber_family_cached,
)
from flux_hopf_lib.hopf.hopfion import toroidal_hopfion_director
from flux_hopf_lib.utils.grid import cartesian_grid

ColorBy = Literal["phase", "base_point", "index"]
Backend = Literal["matplotlib", "plotly"]
AnimMode = Literal["xi1_orbit", "eta_breath", "gauge_twist", "hopfion_spin"]

FIBER_COLORS = (
    "#1a8fe3",
    "#00c9b7",
    "#4cc9f0",
    "#2ec4b6",
    "#48bfe3",
    "#64dfdf",
    "#56cfe1",
    "#4ea8de",
    "#5390d9",
    "#5e60ce",
    "#7b2cbf",
    "#c77dff",
)
ACCENT_GOLD = "#c9a227"


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "Hopf viz requires matplotlib. Install with: pip install 'flux-hopf-lib[viz]'"
        ) from exc
    return plt


def _require_plotly():
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError as exc:
        raise ImportError(
            "Plotly backend requires plotly. Install with: pip install 'flux-hopf-lib[viz]'"
        ) from exc
    return go, make_subplots


def _fiber_color(i: int, fiber: dict[str, Any], color_by: ColorBy) -> str:
    if color_by == "index":
        return FIBER_COLORS[i % len(FIBER_COLORS)]
    if color_by == "base_point":
        # Map base y1 ∈ [-1,1] → hue-ish discrete palette index
        t = 0.5 * (float(fiber["base_y1"]) + 1.0)
        idx = int(np.clip(t * (len(FIBER_COLORS) - 1), 0, len(FIBER_COLORS) - 1))
        return FIBER_COLORS[idx]
    # phase: use mean fiber phase index
    return FIBER_COLORS[i % len(FIBER_COLORS)]


def plot_hopf_fibers_stereographic(
    n_fibers: int = 12,
    n_points: int = 160,
    *,
    color_by: ColorBy = "phase",
    backend: Backend = "matplotlib",
    scale: float = 1.0,
    highlight: tuple[float, float] | None = (0.6, 1.2),
    title: str = "Hopf fibers (stereographic S³ → ℝ³)",
    figsize: tuple[float, float] = (8.0, 7.0),
) -> Any:
    """Main 3D stereographic fiber plot. Returns Figure (matplotlib or plotly)."""
    fibers = sample_fiber_family(n_fibers=n_fibers, n_points=n_points, scale=2.0)

    if backend == "plotly":
        go, _ = _require_plotly()
        fig = go.Figure()
        for i, fiber in enumerate(fibers):
            color = _fiber_color(i, fiber, color_by)
            fig.add_trace(
                go.Scatter3d(
                    x=np.asarray(fiber["px"]) * scale,
                    y=np.asarray(fiber["py"]) * scale,
                    z=np.asarray(fiber["pz"]) * scale,
                    mode="lines",
                    name=f"Fiber {i + 1}",
                    line=dict(color=color, width=4),
                )
            )
        if highlight is not None:
            h = sample_fiber(highlight[0], highlight[1], n_points=n_points, scale=2.0)
            fig.add_trace(
                go.Scatter3d(
                    x=np.asarray(h["px"]) * scale,
                    y=np.asarray(h["py"]) * scale,
                    z=np.asarray(h["pz"]) * scale,
                    mode="lines",
                    name="Highlight",
                    line=dict(color=ACCENT_GOLD, width=7),
                )
            )
        fig.update_layout(
            title=title,
            scene=dict(aspectmode="cube", xaxis_title="x", yaxis_title="y", zaxis_title="z"),
            height=560,
            margin=dict(l=0, r=0, t=48, b=0),
        )
        return fig

    plt = _require_matplotlib()
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    for i, fiber in enumerate(fibers):
        color = _fiber_color(i, fiber, color_by)
        ax.plot(
            np.asarray(fiber["px"]) * scale,
            np.asarray(fiber["py"]) * scale,
            np.asarray(fiber["pz"]) * scale,
            color=color,
            lw=1.6,
            alpha=0.9,
        )
    if highlight is not None:
        h = sample_fiber(highlight[0], highlight[1], n_points=n_points, scale=2.0)
        ax.plot(
            np.asarray(h["px"]) * scale,
            np.asarray(h["py"]) * scale,
            np.asarray(h["pz"]) * scale,
            color=ACCENT_GOLD,
            lw=2.8,
            label="highlight",
        )
        ax.legend(loc="upper right", fontsize=8)
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass
    fig.tight_layout()
    return fig


def plot_hopf_fibers_multi_view(
    n_fibers: int = 10,
    n_points: int = 140,
    *,
    color_by: ColorBy = "index",
    scale: float = 1.0,
    title: str = "Hopf fibers — multi-view projections",
    figsize: tuple[float, float] = (10.0, 8.0),
) -> Any:
    """2×2 panels: xy, xz, yz stereographic projections + S² base markers."""
    plt = _require_matplotlib()
    fibers = sample_fiber_family(n_fibers=n_fibers, n_points=n_points, scale=2.0)
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    pairs = [
        (axes[0, 0], "px", "py", "x", "y", "xy"),
        (axes[0, 1], "px", "pz", "x", "z", "xz"),
        (axes[1, 0], "py", "pz", "y", "z", "yz"),
    ]
    for ax, a, b, xlab, ylab, label in pairs:
        for i, fiber in enumerate(fibers):
            color = _fiber_color(i, fiber, color_by)
            ax.plot(
                np.asarray(fiber[a]) * scale,
                np.asarray(fiber[b]) * scale,
                color=color,
                lw=1.2,
                alpha=0.85,
            )
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        ax.set_title(label)
        ax.grid(True, alpha=0.25)

    axb = axes[1, 1]
    bx, by, bz = base_sphere_mesh(n_theta=18, n_phi=36)
    # Project S² to xy for a simple disk view of base markers
    axb.plot(bx[0, :], by[0, :], color="#cccccc", lw=0.5, alpha=0.4)
    for i, fiber in enumerate(fibers):
        color = _fiber_color(i, fiber, color_by)
        axb.scatter(
            [fiber["base_y1"]],
            [fiber["base_y2"]],
            c=color,
            s=28,
            zorder=3,
        )
    circ = plt.Circle((0, 0), 1.0, fill=False, color="#888888", lw=1.0)
    axb.add_patch(circ)
    axb.set_aspect("equal")
    axb.set_xlim(-1.15, 1.15)
    axb.set_ylim(-1.15, 1.15)
    axb.set_xlabel("y₁")
    axb.set_ylabel("y₂")
    axb.set_title("S² base (y₁, y₂)")
    axb.grid(True, alpha=0.25)

    fig.suptitle(title)
    fig.tight_layout()
    return fig


def plot_hopfion_director_slice(
    *,
    extent: float = 2.0,
    n: int = 48,
    major_radius: float = 1.0,
    minor_radius: float = 0.35,
    hopf_index: int = 1,
    z0: float = 0.0,
    title: str = "Hopfion director field (z = const slice)",
    figsize: tuple[float, float] = (7.0, 6.0),
) -> Any:
    """Quiver plot of toroidal Hopfion director on a z = z0 plane."""
    plt = _require_matplotlib()
    x, y = cartesian_grid(n, n, extent=extent)
    z = np.full_like(x, z0)
    nx, ny, nz = toroidal_hopfion_director(
        x, y, z, major_radius=major_radius, minor_radius=minor_radius, hopf_index=hopf_index
    )
    step = max(1, n // 24)
    fig, ax = plt.subplots(figsize=figsize)
    ax.quiver(
        x[::step, ::step],
        y[::step, ::step],
        nx[::step, ::step],
        ny[::step, ::step],
        nz[::step, ::step],
        cmap="coolwarm",
        angles="xy",
        scale_units="xy",
        scale=8.0,
        width=0.0035,
    )
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_linking_curves(
    eta_a: float = 0.4,
    xi1_a: float = 0.5,
    eta_b: float = 0.9,
    xi1_b: float = 2.0,
    n_points: int = 200,
    *,
    backend: Backend = "matplotlib",
    title: str | None = None,
    figsize: tuple[float, float] = (7.5, 6.5),
) -> Any:
    """Visualize two fibers and annotate Gauss linking number."""
    fa = sample_fiber(eta_a, xi1_a, n_points=n_points, scale=2.0)
    fb = sample_fiber(eta_b, xi1_b, n_points=n_points, scale=2.0)
    lk = fiber_linking_number(fa, fb)
    t = title or f"Linked Hopf fibers  ·  linking ≈ {lk:.3f}"

    if backend == "plotly":
        go, _ = _require_plotly()
        fig = go.Figure()
        fig.add_trace(
            go.Scatter3d(
                x=fa["px"], y=fa["py"], z=fa["pz"], mode="lines",
                name="Fiber A", line=dict(color=FIBER_COLORS[0], width=6),
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=fb["px"], y=fb["py"], z=fb["pz"], mode="lines",
                name="Fiber B", line=dict(color=ACCENT_GOLD, width=6),
            )
        )
        fig.update_layout(title=t, scene=dict(aspectmode="cube"), height=520)
        return fig

    plt = _require_matplotlib()
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(fa["px"], fa["py"], fa["pz"], color=FIBER_COLORS[0], lw=2.2, label="fiber A")
    ax.plot(fb["px"], fb["py"], fb["pz"], color=ACCENT_GOLD, lw=2.2, label="fiber B")
    ax.set_title(t)
    ax.legend(loc="upper right")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Interactive S² explorer (Plotly; Gradio-friendly via customdata + sliders)
# ---------------------------------------------------------------------------

def s2_to_hopf_angles(y1: float, y2: float, y3: float) -> tuple[float, float]:
    """
    Approximate inverse: unit base point on S² → (η, ξ₁) for fiber sampling.

    Uses a stable latitude/azimuth reconstruction for portal explorers.
    """
    y1, y2, y3 = float(y1), float(y2), float(y3)
    n = float(np.sqrt(y1 * y1 + y2 * y2 + y3 * y3) + 1e-12)
    y1, y2, y3 = y1 / n, y2 / n, y3 / n
    eta = float(np.clip(0.5 * np.arccos(np.clip(y3, -1.0, 1.0)), 0.05, 1.45))
    xi1 = float(np.arctan2(y2, y1) % (2.0 * np.pi))
    return eta, xi1


def fiber_family_choices(
    n_fibers: int = 12,
    n_points: int = 40,
) -> list[tuple[str, float, float]]:
    """Return [(label, eta, xi1), ...] for UI dropdowns / S² selection."""
    fibers = sample_fiber_family(n_fibers=n_fibers, n_points=n_points)
    out: list[tuple[str, float, float]] = []
    for i, f in enumerate(fibers):
        label = f"#{i + 1}  η={f['eta']:.2f}  ξ₁={f['xi1']:.2f}"
        out.append((label, float(f["eta"]), float(f["xi1"])))
    return out


def plot_hopf_fibers_dashboard(
    n_fibers: int = 8,
    n_points: int = 160,
    *,
    eta: float = 0.6,
    xi1: float = 1.2,
    projection_scale: float = 1.0,
    show_base: bool = True,
    show_highlight: bool = True,
    title: str = "Hopf fibration — stereographic projections + S² base",
    height: int = 620,
    theme: dict[str, Any] | None = None,
) -> Any:
    """
    HF-safe Plotly 2×2 dashboard (no WebGL).

    Panels: xy, xz, S² base markers, highlight fiber phase.
    """
    go, make_subplots = _require_plotly()
    fibers = sample_fiber_family(n_fibers=n_fibers, n_points=n_points, scale=2.0)
    highlight = (
        sample_fiber(eta, xi1, n_points=n_points, scale=2.0) if show_highlight else None
    )

    panel_titles = (
        "① ℝ³ xy — Villarceau circles",
        "② ℝ³ xz — orthogonal projection",
        "③ S² base — fiber base points",
        "④ Highlight — fiber phase ξ₂",
    )
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=panel_titles,
        horizontal_spacing=0.08,
        vertical_spacing=0.11,
    )

    for i, fiber in enumerate(fibers):
        color = FIBER_COLORS[i % len(FIBER_COLORS)]
        px = np.asarray(fiber["px"]) * projection_scale
        py = np.asarray(fiber["py"]) * projection_scale
        pz = np.asarray(fiber["pz"]) * projection_scale
        fig.add_trace(
            go.Scatter(
                x=px,
                y=py,
                mode="lines",
                name=f"Fiber {i + 1}",
                legendgroup=f"f{i}",
                line=dict(color=color, width=2.4),
                showlegend=(i == 0),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=px,
                y=pz,
                mode="lines",
                legendgroup=f"f{i}",
                line=dict(color=color, width=2.4),
                showlegend=False,
            ),
            row=1,
            col=2,
        )
        if show_base:
            y1, y2, y3 = fiber["base_y1"], fiber["base_y2"], fiber["base_y3"]
            denom = max(1.0 - y3, 1e-6)
            fig.add_trace(
                go.Scatter(
                    x=[0.55 * y1 / denom],
                    y=[0.55 * y2 / denom],
                    mode="markers",
                    marker=dict(color=color, size=7),
                    customdata=[[fiber["eta"], fiber["xi1"], y1, y2, y3]],
                    hovertemplate=(
                        "η=%{customdata[0]:.3f}<br>ξ₁=%{customdata[1]:.3f}<br>"
                        "S²=(%{customdata[2]:.2f}, %{customdata[3]:.2f}, %{customdata[4]:.2f})"
                        "<extra>base</extra>"
                    ),
                    showlegend=False,
                ),
                row=2,
                col=1,
            )

    if show_base:
        th = np.linspace(0.0, 2.0 * np.pi, 120)
        fig.add_trace(
            go.Scatter(
                x=0.55 * np.cos(th),
                y=0.55 * np.sin(th),
                mode="lines",
                line=dict(color="#1a8fe3", width=1, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            ),
            row=2,
            col=1,
        )

    if highlight is not None:
        hx = np.asarray(highlight["px"]) * projection_scale
        hy = np.asarray(highlight["py"]) * projection_scale
        hz = np.asarray(highlight["pz"]) * projection_scale
        xi2 = np.asarray(highlight["xi2"])
        fig.add_trace(
            go.Scatter(
                x=hx,
                y=hy,
                mode="lines",
                name=f"Highlight η={eta:.2f}",
                line=dict(color=ACCENT_GOLD, width=4),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=hx,
                y=hz,
                mode="lines",
                line=dict(color=ACCENT_GOLD, width=4),
                showlegend=False,
            ),
            row=1,
            col=2,
        )
        fig.add_trace(
            go.Scatter(
                x=hx,
                y=hy,
                mode="markers",
                marker=dict(
                    size=6,
                    color=xi2,
                    showscale=True,
                    colorbar=dict(title="ξ₂", len=0.35, y=0.18),
                    colorscale=[
                        [0.0, "#0d2137"],
                        [0.25, "#1a8fe3"],
                        [0.5, "#00c9b7"],
                        [0.75, "#c9a227"],
                        [1.0, "#ef553b"],
                    ],
                ),
                showlegend=False,
            ),
            row=2,
            col=2,
        )
        if show_base:
            hy1, hy2, hy3 = highlight["y1"][0], highlight["y2"][0], highlight["y3"][0]
            denom = max(1.0 - float(hy3), 1e-6)
            fig.add_trace(
                go.Scatter(
                    x=[0.55 * float(hy1) / denom],
                    y=[0.55 * float(hy2) / denom],
                    mode="markers",
                    marker=dict(size=12, color=ACCENT_GOLD, symbol="diamond"),
                    customdata=[[eta, xi1, float(hy1), float(hy2), float(hy3)]],
                    hovertemplate=(
                        "selected η=%{customdata[0]:.3f} ξ₁=%{customdata[1]:.3f}<extra></extra>"
                    ),
                    showlegend=False,
                ),
                row=2,
                col=1,
            )

    layout: dict[str, Any] = {
        "height": height,
        "title": dict(text=title, x=0.5, xanchor="center"),
        "margin": dict(l=40, r=20, t=56, b=40),
    }
    if theme:
        layout.update(theme)
    fig.update_layout(**layout)
    for row in (1, 2):
        for col in (1, 2):
            fig.update_xaxes(showgrid=True, scaleanchor="y", scaleratio=1, row=row, col=col)
            fig.update_yaxes(showgrid=True, row=row, col=col)
    return fig


def plot_hopf_s2_fiber_explorer(
    n_fibers: int = 12,
    n_points: int = 140,
    *,
    selected_eta: float = 0.6,
    selected_xi1: float = 1.2,
    projection_scale: float = 1.0,
    title: str = "S² base explorer — hover base points for η, ξ₁",
    height: int = 560,
    theme: dict[str, Any] | None = None,
    use_lod: bool = True,
    use_cache: bool = True,
    dim_unselected: bool = True,
) -> Any:
    """
    Interactive-oriented Plotly explorer (WebGL-free).

    Left: stereographic xy of the fiber family + highlighted fiber.
    Right: S² disk with base markers carrying
    ``customdata = [η, ξ₁, y1, y2, y3, index]`` for Gradio/Dash handlers.

    Shared ``legendgroup`` links left-fiber and right-base hover styling.
    Pair with :func:`fiber_family_choices` for dropdown selection UIs.

    Parameters
    ----------
    use_lod
        Cap points per fiber via :func:`~flux_hopf_lib.hopf.fibration.lod_n_points`.
    use_cache
        Use :func:`~flux_hopf_lib.hopf.fibration.sample_fiber_family_cached`.
    dim_unselected
        Lower opacity on non-selected family fibers for focus.
    """
    go, make_subplots = _require_plotly()
    pts = lod_n_points(n_fibers, base_points=n_points) if use_lod else int(n_points)
    sampler = sample_fiber_family_cached if use_cache else sample_fiber_family
    fibers = sampler(n_fibers=n_fibers, n_points=pts, scale=2.0)
    if use_lod:
        fibers = [apply_fiber_lod(f, pts) for f in fibers]
    highlight = sample_fiber(selected_eta, selected_xi1, n_points=pts, scale=2.0)

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Stereographic xy (ℝ³)",
            "S² base — hover / select fiber",
        ),
        column_widths=[0.58, 0.42],
        horizontal_spacing=0.08,
    )

    family_opacity = 0.35 if dim_unselected else 0.9
    for i, fiber in enumerate(fibers):
        color = FIBER_COLORS[i % len(FIBER_COLORS)]
        px = np.asarray(fiber["px"]) * projection_scale
        py = np.asarray(fiber["py"]) * projection_scale
        # Per-point customdata for richer line hover (η, ξ₁, ξ₂, index)
        xi2 = np.asarray(fiber["xi2"])
        line_cd = np.column_stack(
            [
                np.full(len(xi2), fiber["eta"]),
                np.full(len(xi2), fiber["xi1"]),
                xi2,
                np.full(len(xi2), i),
            ]
        )
        fig.add_trace(
            go.Scatter(
                x=px,
                y=py,
                mode="lines",
                line=dict(color=color, width=2.0),
                opacity=family_opacity,
                name=f"F{i + 1}",
                legendgroup=f"f{i}",
                showlegend=False,
                customdata=line_cd,
                hovertemplate=(
                    "<b>Fiber %{customdata[3]:.0f}</b><br>"
                    "η=%{customdata[0]:.3f} · ξ₁=%{customdata[1]:.3f}<br>"
                    "ξ₂=%{customdata[2]:.3f}<br>"
                    "xy=(%{x:.2f}, %{y:.2f})<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )
        y1, y2, y3 = fiber["base_y1"], fiber["base_y2"], fiber["base_y3"]
        denom = max(1.0 - y3, 1e-6)
        fig.add_trace(
            go.Scatter(
                x=[0.55 * y1 / denom],
                y=[0.55 * y2 / denom],
                mode="markers",
                marker=dict(size=11, color=color, line=dict(width=1, color="#0a1628")),
                customdata=[[fiber["eta"], fiber["xi1"], y1, y2, y3, i]],
                name=f"base {i + 1}",
                legendgroup=f"f{i}",
                hovertemplate=(
                    "<b>Fiber %{customdata[5]:.0f}</b> (base)<br>"
                    "η=%{customdata[0]:.3f} · ξ₁=%{customdata[1]:.3f}<br>"
                    "S² y=(%{customdata[2]:.2f}, %{customdata[3]:.2f}, %{customdata[4]:.2f})<br>"
                    "<i>linked to left curve via legendgroup</i><extra></extra>"
                ),
            ),
            row=1,
            col=2,
        )

    th = np.linspace(0, 2 * np.pi, 160)
    fig.add_trace(
        go.Scatter(
            x=0.55 * np.cos(th),
            y=0.55 * np.sin(th),
            mode="lines",
            line=dict(color="#4ea8de", width=1, dash="dot"),
            showlegend=False,
            hoverinfo="skip",
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=np.asarray(highlight["px"]) * projection_scale,
            y=np.asarray(highlight["py"]) * projection_scale,
            mode="lines",
            line=dict(color=ACCENT_GOLD, width=4.5),
            name="selected fiber",
            hovertemplate=(
                f"<b>Selected</b><br>η={selected_eta:.3f} · ξ₁={selected_xi1:.3f}"
                "<br>xy=(%{x:.2f}, %{y:.2f})<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )
    hy1 = float(highlight["y1"][0])
    hy2 = float(highlight["y2"][0])
    hy3 = float(highlight["y3"][0])
    denom = max(1.0 - hy3, 1e-6)
    fig.add_trace(
        go.Scatter(
            x=[0.55 * hy1 / denom],
            y=[0.55 * hy2 / denom],
            mode="markers",
            marker=dict(size=14, color=ACCENT_GOLD, symbol="diamond"),
            name="selected base",
            customdata=[[selected_eta, selected_xi1, hy1, hy2, hy3]],
            hovertemplate=(
                "<b>Selected base</b><br>"
                "η=%{customdata[0]:.3f} · ξ₁=%{customdata[1]:.3f}<br>"
                "S²=(%{customdata[2]:.2f}, %{customdata[3]:.2f}, %{customdata[4]:.2f})"
                "<extra></extra>"
            ),
        ),
        row=1,
        col=2,
    )

    layout: dict[str, Any] = {
        "height": height,
        "title": dict(text=title, x=0.5, xanchor="center"),
        "margin": dict(l=40, r=20, t=56, b=40),
        "legend": dict(orientation="h", y=1.08),
        "hovermode": "closest",
    }
    if theme:
        layout.update(theme)
    fig.update_layout(**layout)
    fig.update_xaxes(scaleanchor="y", scaleratio=1, showgrid=True, row=1, col=1)
    fig.update_yaxes(showgrid=True, row=1, col=1)
    fig.update_xaxes(
        scaleanchor="y", scaleratio=1, range=[-0.7, 0.7], showgrid=True, row=1, col=2
    )
    fig.update_yaxes(range=[-0.7, 0.7], showgrid=True, row=1, col=2)
    return fig


# ---------------------------------------------------------------------------
# Animation (matplotlib + Plotly frames)
# ---------------------------------------------------------------------------

def _anim_highlight_params(
    mode: AnimMode,
    frame: int,
    n_frames: int,
    *,
    eta0: float = 0.6,
    xi1_0: float = 1.2,
) -> tuple[float, float]:
    """Map animation frame → (η, ξ₁) for the highlight fiber."""
    t = frame / max(n_frames, 1)
    if mode == "xi1_orbit":
        return eta0, float((xi1_0 + 2.0 * np.pi * t) % (2.0 * np.pi))
    if mode == "eta_breath":
        # breathe η between ~0.25 and ~1.2
        eta = 0.25 + 0.95 * (0.5 + 0.5 * np.sin(2.0 * np.pi * t))
        return float(eta), xi1_0
    if mode in ("gauge_twist", "hopfion_spin"):
        # keep base fixed; phase / director evolve separately
        return eta0, xi1_0
    return eta0, xi1_0


def animate_hopf_fibers(
    n_fibers: int = 8,
    n_points: int = 80,
    n_frames: int = 48,
    *,
    mode: AnimMode = "xi1_orbit",
    eta: float = 0.6,
    xi1: float = 1.2,
    interval: int = 50,
    projection_scale: float = 1.0,
    title: str | None = None,
    figsize: tuple[float, float] = (8.0, 7.0),
    save_path: str | None = None,
    dpi: int = 100,
) -> Any:
    """
    Matplotlib animation of Hopf fibers / gauge phase / hopfion director.

    Modes
    -----
    xi1_orbit
        Selected fiber base walks around S² (ξ₁ sweep).
    eta_breath
        Selected fiber latitude η oscillates.
    gauge_twist
        Static family; marker on highlight advances along ξ₂ (fiber phase).
    hopfion_spin
        Toroidal hopfion director slice rotates in the xy-plane.

    Returns a ``matplotlib.animation.FuncAnimation``. Use ``save_path`` (``.gif``
    or ``.mp4``) for offline export. Requires ``matplotlib`` (``[viz]`` extra).
    """
    plt = _require_matplotlib()
    from matplotlib import animation

    pts = lod_n_points(n_fibers, base_points=n_points)
    fibers = sample_fiber_family_cached(n_fibers=n_fibers, n_points=pts, scale=2.0)
    fibers = [apply_fiber_lod(f, pts) for f in fibers]

    fig = plt.figure(figsize=figsize)
    if mode == "hopfion_spin":
        ax = fig.add_subplot(111)
    else:
        ax = fig.add_subplot(111, projection="3d")

    t_title = title or f"Hopf animation — {mode}"

    if mode == "hopfion_spin":
        n_grid = 28
        x2, y2 = cartesian_grid(n_grid, n_grid, extent=1.6)
        z2 = np.zeros_like(x2)
        nx, ny, _nz = toroidal_hopfion_director(x2, y2, z2)
        skip = 2
        q = ax.quiver(
            x2[::skip, ::skip],
            y2[::skip, ::skip],
            nx[::skip, ::skip],
            ny[::skip, ::skip],
            color="#1a8fe3",
            angles="xy",
            scale_units="xy",
            scale=8,
        )
        ax.set_aspect("equal")
        ax.set_title(t_title)
        ax.set_xlabel("x")
        ax.set_ylabel("y")

        def _update_hopfion(frame: int):
            nonlocal q
            ang = 2.0 * np.pi * frame / max(n_frames, 1)
            c, s = np.cos(ang), np.sin(ang)
            rx = c * nx - s * ny
            ry = s * nx + c * ny
            q.remove()
            q = ax.quiver(
                x2[::skip, ::skip],
                y2[::skip, ::skip],
                rx[::skip, ::skip],
                ry[::skip, ::skip],
                color="#1a8fe3",
                angles="xy",
                scale_units="xy",
                scale=8,
            )
            ax.set_title(f"{t_title}  θ={ang:.2f}")
            return (q,)

        anim = animation.FuncAnimation(
            fig, _update_hopfion, frames=n_frames, interval=interval, blit=False
        )
    else:
        lines = []
        for i, fiber in enumerate(fibers):
            color = FIBER_COLORS[i % len(FIBER_COLORS)]
            (ln,) = ax.plot(
                np.asarray(fiber["px"]) * projection_scale,
                np.asarray(fiber["py"]) * projection_scale,
                np.asarray(fiber["pz"]) * projection_scale,
                color=color,
                lw=1.4,
                alpha=0.55,
            )
            lines.append(ln)
        (hl,) = ax.plot([], [], [], color=ACCENT_GOLD, lw=3.0)
        phase_pt = ax.scatter([], [], [], color=ACCENT_GOLD, s=40)
        ax.set_title(t_title)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        try:
            ax.set_box_aspect((1, 1, 1))
        except Exception:
            pass

        def _update_fibers(frame: int):
            e, x = _anim_highlight_params(
                mode, frame, n_frames, eta0=eta, xi1_0=xi1
            )
            h = sample_fiber(e, x, n_points=pts, scale=2.0)
            hx = np.asarray(h["px"]) * projection_scale
            hy = np.asarray(h["py"]) * projection_scale
            hz = np.asarray(h["pz"]) * projection_scale
            hl.set_data(hx, hy)
            hl.set_3d_properties(hz)
            if mode == "gauge_twist":
                k = int((frame / max(n_frames, 1)) * (len(hx) - 1))
                phase_pt._offsets3d = ([hx[k]], [hy[k]], [hz[k]])
            else:
                phase_pt._offsets3d = ([], [], [])
            ax.set_title(f"{t_title}  η={e:.2f} ξ₁={x:.2f}")
            return (hl, phase_pt, *lines)

        anim = animation.FuncAnimation(
            fig, _update_fibers, frames=n_frames, interval=interval, blit=False
        )

    if save_path:
        path = str(save_path)
        if path.lower().endswith(".gif"):
            anim.save(path, writer="pillow", dpi=dpi)
        else:
            anim.save(path, dpi=dpi)
    return anim


def create_plotly_fiber_animation(
    n_fibers: int = 8,
    n_points: int = 80,
    n_frames: int = 36,
    *,
    mode: AnimMode = "xi1_orbit",
    eta: float = 0.6,
    xi1: float = 1.2,
    projection_scale: float = 1.0,
    height: int = 560,
    title: str | None = None,
    theme: dict[str, Any] | None = None,
    use_lod: bool = True,
    frame_ms: int = 80,
) -> Any:
    """
    Plotly figure with playable frames (2D stereographic xy).

    **Gradio note:** ``gr.Plot`` often breaks Plotly's client-side ``animate``
    method (Play button appears but does nothing). Prefer embedding via
    ``fig.to_html(include_plotlyjs="cdn", full_html=False)`` into ``gr.HTML``
    — see kingdom portal.

    Same modes as :func:`animate_hopf_fibers` except ``hopfion_spin`` falls back
    to a 2D-safe ``eta_breath`` highlight.
    """
    go, _ = _require_plotly()
    if mode == "hopfion_spin":
        mode = "eta_breath"  # 2D-safe fallback for Plotly path

    pts = lod_n_points(n_fibers, base_points=n_points) if use_lod else int(n_points)
    fibers = sample_fiber_family_cached(n_fibers=n_fibers, n_points=pts, scale=2.0)
    fibers = [apply_fiber_lod(f, pts) for f in fibers]

    # Precompute highlight curve per frame (full x/y — more reliable than partial frames)
    frame_curves: list[tuple[np.ndarray, np.ndarray, float, float, int]] = []
    for fi in range(n_frames):
        e, x = _anim_highlight_params(mode, fi, n_frames, eta0=eta, xi1_0=xi1)
        h = sample_fiber(e, x, n_points=pts, scale=2.0)
        hx = np.asarray(h["px"]) * projection_scale
        hy = np.asarray(h["py"]) * projection_scale
        k = int((fi / max(n_frames, 1)) * (len(hx) - 1)) if mode == "gauge_twist" else 0
        frame_curves.append((hx, hy, e, x, k))

    hx0, hy0, e0, x0, k0 = frame_curves[0]
    fig = go.Figure()
    for i, fiber in enumerate(fibers):
        color = FIBER_COLORS[i % len(FIBER_COLORS)]
        fig.add_trace(
            go.Scatter(
                x=np.asarray(fiber["px"]) * projection_scale,
                y=np.asarray(fiber["py"]) * projection_scale,
                mode="lines",
                line=dict(color=color, width=2.0),
                opacity=0.4,
                name=f"F{i + 1}",
                showlegend=False,
                hoverinfo="skip",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=hx0,
            y=hy0,
            mode="lines",
            line=dict(color=ACCENT_GOLD, width=4),
            name="highlight",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[float(hx0[k0])],
            y=[float(hy0[k0])],
            mode="markers",
            marker=dict(size=10, color=ACCENT_GOLD),
            name="phase",
            showlegend=False,
        )
    )

    # Static family traces + full highlight/phase data in every frame (no partial-update bugs)
    family_data = list(fig.data[:n_fibers])
    frames = []
    base_title = title or f"Hopf animation — {mode}"
    for fi, (hx, hy, e, x, k) in enumerate(frame_curves):
        frames.append(
            go.Frame(
                name=str(fi),
                data=list(family_data)
                + [
                    go.Scatter(
                        x=hx,
                        y=hy,
                        mode="lines",
                        line=dict(color=ACCENT_GOLD, width=4),
                        name="highlight",
                    ),
                    go.Scatter(
                        x=[float(hx[k])],
                        y=[float(hy[k])],
                        mode="markers",
                        marker=dict(size=10, color=ACCENT_GOLD),
                        name="phase",
                        showlegend=False,
                    ),
                ],
                layout=go.Layout(title_text=f"{base_title}  · η={e:.2f} ξ₁={x:.2f}"),
            )
        )

    fig.frames = frames
    frame_names = [str(fi) for fi in range(n_frames)]
    play_args = {
        "frame": {"duration": int(frame_ms), "redraw": True},
        "fromcurrent": True,
        "mode": "immediate",
        "transition": {"duration": 0, "easing": "linear"},
    }
    layout: dict[str, Any] = {
        "height": height,
        "title": dict(text=f"{base_title}  · η={e0:.2f} ξ₁={x0:.2f}", x=0.5, xanchor="center"),
        "margin": dict(l=40, r=20, t=60, b=80),
        # Avoid scaleanchor — it can break animate redraw in some Plotly embeds
        "xaxis": dict(showgrid=True, zeroline=True, scaleanchor="y", scaleratio=1),
        "yaxis": dict(showgrid=True, zeroline=True),
        "updatemenus": [
            {
                "type": "buttons",
                "direction": "left",
                "showactive": False,
                "y": 1.15,
                "x": 0.0,
                "xanchor": "left",
                "yanchor": "top",
                "pad": {"r": 10, "t": 0},
                "buttons": [
                    {
                        "label": "▶ Play",
                        "method": "animate",
                        # Explicit frame list is more reliable than null in iframes
                        "args": [frame_names, play_args],
                    },
                    {
                        "label": "⏸ Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                    },
                ],
            }
        ],
        "sliders": [
            {
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "prefix": "frame: ",
                    "visible": True,
                    "xanchor": "right",
                },
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.05,
                "steps": [
                    {
                        "args": [
                            [str(fi)],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                        "label": str(fi),
                        "method": "animate",
                    }
                    for fi in range(n_frames)
                ],
            }
        ],
    }
    if theme:
        # Theme may override title/margin — merge carefully
        layout.update({k: v for k, v in theme.items() if k not in ("updatemenus", "sliders")})
    fig.update_layout(**layout)
    return fig


def plotly_fig_to_html(
    fig: Any,
    *,
    height: int | None = None,
    include_plotlyjs: str | bool = "cdn",
) -> str:
    """
    Embed a Plotly figure as HTML for Gradio ``gr.HTML``.

    Required for animations: ``gr.Plot`` re-serializes figures and drops working
    client-side ``Plotly.animate`` bindings in many Gradio/HF iframe setups.
    """
    if height is not None:
        try:
            fig.update_layout(height=int(height))
        except Exception:
            pass
    inner = fig.to_html(
        include_plotlyjs=include_plotlyjs,
        full_html=False,
        config={
            "responsive": True,
            "displayModeBar": True,
            "displaylogo": False,
        },
    )
    return (
        '<div class="hopf-plotly-embed" style="width:100%;min-height:480px;">'
        f"{inner}</div>"
    )
