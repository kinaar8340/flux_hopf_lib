"""Hopf fibration mappings, fibers, hopfions, invariants, and optional viz."""

from flux_hopf_lib.hopf.fibration import (
    base_sphere_mesh,
    fiber_linking_number,
    hopf_coordinates,
    hopf_map,
    hopf_map_from_angles,
    hopf_map_quaternion,
    linking_number_pair,
    s3_from_quaternion,
    sample_fiber,
    sample_fiber_family,
    stereographic_project,
)
from flux_hopf_lib.hopf.hopfion import (
    charge_modulated_hopfion,
    hopf_charge_density,
    toroidal_hopfion_director,
)
from flux_hopf_lib.hopf.invariants import (
    base_point_chordal_distance,
    fiber_pair_diagnostics,
    holonomy_phase_proxy,
    wg_from_base,
    wg_relative_residual,
)

__all__ = [
    "hopf_coordinates",
    "hopf_map",
    "hopf_map_from_angles",
    "hopf_map_quaternion",
    "linking_number_pair",
    "s3_from_quaternion",
    "stereographic_project",
    "sample_fiber",
    "sample_fiber_family",
    "base_sphere_mesh",
    "fiber_linking_number",
    "toroidal_hopfion_director",
    "hopf_charge_density",
    "charge_modulated_hopfion",
    "wg_from_base",
    "wg_relative_residual",
    "holonomy_phase_proxy",
    "base_point_chordal_distance",
    "fiber_pair_diagnostics",
]
