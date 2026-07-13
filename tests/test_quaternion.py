"""Quaternion core tests."""

from __future__ import annotations

import numpy as np

from flux_hopf_lib.quaternion import (
    Quaternion,
    encode_shard,
    q_conj,
    q_mult,
    q_normalize,
    rodrigues_rotation,
    small_rotor,
)


def test_identity_multiply():
    q = Quaternion.from_axis_angle(np.array([0.0, 0.0, 1.0]), 0.3)
    i = Quaternion.identity()
    r = q.multiply(i).normalize()
    assert r.chordal_distance(q.normalize()) < 1e-10


def test_q_mult_unit():
    a = small_rotor(0.5)
    b = small_rotor(-0.5)
    p = q_normalize(q_mult(a, b))
    assert abs(p[0] - 1.0) < 1e-9
    assert np.linalg.norm(p[1:]) < 1e-9


def test_q_conj_norm():
    q = np.array([0.5, 0.5, 0.5, 0.5])
    q = q_normalize(q)
    assert abs(np.linalg.norm(q) - 1.0) < 1e-10
    c = q_conj(q)
    assert c[0] == q[0]
    assert np.allclose(c[1:], -q[1:])


def test_rodrigues_90deg():
    v = np.array([1.0, 0.0, 0.0])
    k = np.array([0.0, 0.0, 1.0])
    out = rodrigues_rotation(v, k, np.pi / 2)
    assert np.allclose(out, [0.0, 1.0, 0.0], atol=1e-10)


def test_encode_shard_unit():
    q = encode_shard(b"hello world!!!!")
    assert abs(q.norm() - 1.0) < 1e-10
