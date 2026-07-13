#!/usr/bin/env python3
"""Demo Hopf fiber visualizations (requires flux-hopf-lib[viz]).

    pip install -e ".[viz]"
    python examples/hopf_viz_demo.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from flux_hopf_lib.hopf.viz import (
    plot_hopf_fibers_dashboard,
    plot_hopf_fibers_multi_view,
    plot_hopf_fibers_stereographic,
    plot_hopf_s2_fiber_explorer,
    plot_hopfion_director_slice,
    plot_linking_curves,
)

OUT = Path(__file__).resolve().parent.parent / "outputs"
OUT.mkdir(exist_ok=True)


def main() -> None:
    fig1 = plot_hopf_fibers_stereographic(n_fibers=10, n_points=120, color_by="index")
    fig1.savefig(OUT / "hopf_fibers_stereo.png", dpi=120)
    fig2 = plot_hopf_fibers_multi_view(n_fibers=8, n_points=100)
    fig2.savefig(OUT / "hopf_fibers_multiview.png", dpi=120)
    fig3 = plot_hopfion_director_slice(n=40)
    fig3.savefig(OUT / "hopfion_director_slice.png", dpi=120)
    fig4 = plot_linking_curves(n_points=160)
    fig4.savefig(OUT / "hopf_linking.png", dpi=120)

    # HF-safe Plotly builders (HTML snapshots)
    try:
        dash = plot_hopf_fibers_dashboard(n_fibers=8, n_points=80, height=500)
        dash.write_html(str(OUT / "hopf_dashboard.html"), include_plotlyjs="cdn")
        exp = plot_hopf_s2_fiber_explorer(n_fibers=10, n_points=80, height=480)
        exp.write_html(str(OUT / "hopf_s2_explorer.html"), include_plotlyjs="cdn")
        print("Wrote Plotly HTML dashboards")
    except ImportError:
        print("plotly not installed — skipped dashboard/explorer HTML")

    print(f"Wrote figures under {OUT}")


if __name__ == "__main__":
    main()
