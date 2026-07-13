"""Numpy quaternion primitives shared across toe, vqc_proto, and probes.

API mirrors the numpy helpers used in ``toe`` gauged-twist survival and the
``Quaternion`` dataclass from ``vqc_proto`` orbital braille codec.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


Array = NDArray[np.floating]


@dataclass
class Quaternion:
    """Unit (or general) quaternion q = w + xi + yj + zk."""

    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def norm(self) -> float:
        return float(np.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2))

    def conjugate(self) -> Quaternion:
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def inverse(self) -> Quaternion:
        n2 = self.norm() ** 2
        if n2 < 1e-16:
            raise ZeroDivisionError("cannot invert near-zero quaternion")
        return Quaternion(self.w / n2, -self.x / n2, -self.y / n2, -self.z / n2)

    def multiply(self, other: Quaternion) -> Quaternion:
        return Quaternion(
            self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
            self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
            self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
            self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w,
        )

    def normalize(self) -> Quaternion:
        n = self.norm()
        if n < 1e-12:
            return Quaternion(1.0, 0.0, 0.0, 0.0)
        return Quaternion(self.w / n, self.x / n, self.y / n, self.z / n)

    def as_array(self) -> NDArray[np.float64]:
        return np.array([self.w, self.x, self.y, self.z], dtype=np.float64)

    def chordal_distance(self, other: Quaternion) -> float:
        """Chordal distance on S³, identifying q ~ −q for rotation equivalence."""
        a = self.as_array()
        b = other.as_array()
        return float(min(np.linalg.norm(a - b), np.linalg.norm(a + b)))

    @classmethod
    def from_array(cls, arr: Array | list[float]) -> Quaternion:
        a = np.asarray(arr, dtype=float).reshape(-1)
        if a.size < 4:
            a = np.pad(a, (0, 4 - a.size))
        return cls(float(a[0]), float(a[1]), float(a[2]), float(a[3]))

    @classmethod
    def from_axis_angle(cls, axis: Array, theta: float) -> Quaternion:
        axis = np.asarray(axis, dtype=float)
        n = np.linalg.norm(axis)
        if n < 1e-12:
            return cls(1.0, 0.0, 0.0, 0.0)
        axis = axis / n
        half = theta / 2.0
        s = np.sin(half)
        return cls(float(np.cos(half)), float(axis[0] * s), float(axis[1] * s), float(axis[2] * s))

    @classmethod
    def identity(cls) -> Quaternion:
        return cls(1.0, 0.0, 0.0, 0.0)


def q_mult(q1: Array, q2: Array) -> NDArray[np.float64]:
    """Hamilton product of two quaternion arrays shaped (…, 4) or (4,)."""
    q1 = np.asarray(q1, dtype=float)
    q2 = np.asarray(q2, dtype=float)
    w1, x1, y1, z1 = q1[..., 0], q1[..., 1], q1[..., 2], q1[..., 3]
    w2, x2, y2, z2 = q2[..., 0], q2[..., 1], q2[..., 2], q2[..., 3]
    return np.stack(
        [
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ],
        axis=-1,
    )


def q_conj(q: Array) -> NDArray[np.float64]:
    q = np.asarray(q, dtype=float)
    out = np.array(q, copy=True, dtype=float)
    out[..., 1:] = -out[..., 1:]
    return out


def q_normalize(q: Array, eps: float = 1e-12) -> NDArray[np.float64]:
    """Normalize quaternion(s); near-zero inputs map to identity."""
    q = np.asarray(q, dtype=float)
    n = np.linalg.norm(q, axis=-1, keepdims=True)
    # Avoid dividing by ~0 without systematically biasing unit norms
    safe = np.maximum(n, eps)
    out = q / safe
    # Collapse pure zeros to identity
    if out.ndim == 1:
        if n.item() < eps:
            return np.array([1.0, 0.0, 0.0, 0.0])
        return out
    zero_mask = (n[..., 0] < eps)
    if np.any(zero_mask):
        out = np.array(out, copy=True)
        out[zero_mask] = np.array([1.0, 0.0, 0.0, 0.0])
    return out


def small_rotor(angle_rad: float, axis: Array | None = None) -> NDArray[np.float64]:
    """Unit quaternion for a rotation of ``angle_rad`` about ``axis`` (default z)."""
    if axis is None:
        axis = np.array([0.0, 0.0, 1.0])
    axis = np.asarray(axis, dtype=float)
    n = np.linalg.norm(axis)
    if n < 1e-12:
        return np.array([1.0, 0.0, 0.0, 0.0])
    axis = axis / n
    half = angle_rad * 0.5
    s = np.sin(half)
    return np.array([np.cos(half), axis[0] * s, axis[1] * s, axis[2] * s], dtype=float)


def rodrigues_rotation(v: Array, k: Array, theta: float) -> NDArray[np.float64]:
    """Rotate vector ``v`` about unit axis ``k`` by angle ``theta`` (Rodrigues)."""
    v = np.asarray(v, dtype=float)
    k = np.asarray(k, dtype=float)
    kn = np.linalg.norm(k)
    if kn < 1e-12:
        return v.copy()
    k = k / kn
    c, s = np.cos(theta), np.sin(theta)
    return v * c + np.cross(k, v) * s + k * np.dot(k, v) * (1.0 - c)


def encode_shard(payload: bytes | Array) -> Quaternion:
    """Map payload bytes / array to a unit quaternion (compression proxy)."""
    if isinstance(payload, (bytes, bytearray)):
        arr = np.frombuffer(bytes(payload)[:16].ljust(16, b"\x00"), dtype=np.uint8).astype(float)
    else:
        arr = np.asarray(payload, dtype=float).flatten()
    if arr.size < 4:
        arr = np.pad(arr, (0, 4 - arr.size))
    vec = arr[:4]
    vec = vec / (np.linalg.norm(vec) + 1e-12)
    return Quaternion(float(vec[0]), float(vec[1]), float(vec[2]), float(vec[3]))


def decode_shard(q: Quaternion, n_bytes: int = 4) -> NDArray[np.uint8]:
    """Recover approximate byte values from quaternion components."""
    raw = q.as_array()
    raw = raw / (np.linalg.norm(raw) + 1e-12)
    scaled = ((raw + 1.0) / 2.0 * 255.0).clip(0, 255)
    return scaled[:n_bytes].astype(np.uint8)
