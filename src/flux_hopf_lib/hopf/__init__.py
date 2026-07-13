"""Hopf fibration mappings, fibers, hopfions, and linking diagnostics."""

from flux_hopf_lib.hopf.fibration import (
    hopf_coordinates,
    hopf_map,
    hopf_map_from_angles,
    linking_number_pair,
    s3_from_quaternion,
)
from flux_hopf_lib.hopf.hopfion import (
    charge_modulated_hopfion,
    hopf_charge_density,
    toroidal_hopfion_director,
)

__all__ = [
    "hopf_coordinates",
    "hopf_map",
    "hopf_map_from_angles",
    "linking_number_pair",
    "s3_from_quaternion",
    "toroidal_hopfion_director",
    "hopf_charge_density",
    "charge_modulated_hopfion",
]
