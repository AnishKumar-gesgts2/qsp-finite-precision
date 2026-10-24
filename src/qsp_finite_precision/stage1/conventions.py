"""Convert symmetric solver phases to the evaluator's full phase list.

Mappings are checked against pyqsp 0.2.0 and Python QSPPACK 0.4.0.
See notes/Conventions.md for definitions and the MATLAB source boundary.
"""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .forward import _real_vector


def expand_symmetric_phases(
    reduced: ArrayLike, parity: int
) -> NDArray[np.float64]:
    """Expand the center-to-right, imaginary-target symmetric convention.

    Even: [r2, r1, 2*r0, r1, r2] for reduced [r0, r1, r2].
    Odd:  [r2, r1, r0, r0, r1, r2] for the same reduced list.
    A single even reduced phase gives the degree-zero phase [2*r0].
    """
    r = _real_vector(reduced, "reduced")
    if r.size == 0:
        raise ValueError("reduced must be nonempty")
    if isinstance(parity, (bool, np.bool_)) or parity not in (0, 1):
        raise ValueError("parity must be 0 (even) or 1 (odd)")
    if parity == 1:
        return np.concatenate((r[::-1], r))
    return np.concatenate((r[:0:-1], [2 * r[0]], r[1:]))


def qsppack_full_phases(
    phases: ArrayLike, parity: int, *, target_pre: bool, type_phi: str
) -> NDArray[np.float64]:
    """Map QSPPACK output to full phases, preserving its target component.

    Pass raw solve() output with the corresponding targetPre/typePhi.
    The result goes directly into evaluate_qsp: select P.real when
    target_pre=True, P.imag otherwise. Do not also apply get_entry's
    -pi/4 endpoint shifts; those only implement Im(P) via Re(-i*P).
    """
    p = _real_vector(phases, "phases")
    if p.size == 0:
        raise ValueError("phases must be nonempty")
    if isinstance(parity, (bool, np.bool_)) or parity not in (0, 1):
        raise ValueError("parity must be 0 (even) or 1 (odd)")
    if not isinstance(target_pre, (bool, np.bool_)):
        raise TypeError("target_pre must be a boolean")
    if type_phi not in ("full", "reduced"):
        raise ValueError("type_phi must be 'full' or 'reduced'")
    if type_phi == "full":
        if (p.size - 1) % 2 != parity:
            raise ValueError("full phase count does not match parity")
        return p.copy()
    full = expand_symmetric_phases(p, parity)
    if target_pre:
        # Two additions also handle degree zero, where both ends coincide.
        full[0] += np.pi / 4
        full[-1] += np.pi / 4
    return full
