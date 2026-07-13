"""Optional torch quaternion helpers (toe conduit style).

Import only when torch is installed::

    from flux_hopf_lib.quaternion.torch_ops import qmul, qnormalize
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import torch


def _require_torch():
    try:
        import torch
    except ImportError as exc:
        raise ImportError(
            "flux_hopf_lib.quaternion.torch_ops requires torch. "
            "Install with: pip install 'flux-hopf-lib[torch]'"
        ) from exc
    return torch


def qmul(q1: "torch.Tensor", q2: "torch.Tensor") -> "torch.Tensor":
    """Batched Hamilton product; last dim is (w, x, y, z)."""
    torch = _require_torch()
    w1, x1, y1, z1 = q1.unbind(-1)
    w2, x2, y2, z2 = q2.unbind(-1)
    return torch.stack(
        [
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ],
        dim=-1,
    )


def qnormalize(q: "torch.Tensor", eps: float = 1e-8) -> "torch.Tensor":
    torch = _require_torch()
    return torch.nn.functional.normalize(q, dim=-1, eps=eps)


def q_conj(q: "torch.Tensor") -> "torch.Tensor":
    torch = _require_torch()
    return torch.stack([q[..., 0], -q[..., 1], -q[..., 2], -q[..., 3]], dim=-1)


def small_rotor(angle_rad, axis: "torch.Tensor") -> "torch.Tensor":
    """Create small rotation quaternion (torch). Accepts float or Tensor angle."""
    torch = _require_torch()
    if not isinstance(angle_rad, torch.Tensor):
        angle_rad = torch.tensor(angle_rad, dtype=torch.float32, device=axis.device)
    half = angle_rad * 0.5
    c = torch.cos(half)
    s = torch.sin(half)
    return torch.stack(
        [c, axis[0] * s, axis[1] * s, axis[2] * s],
        dim=-1,
    ).to(dtype=torch.float32, device=axis.device)
