"""Vectorized forward QSP evaluation in the Wx signal / Z phase convention."""

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _real_vector(values: ArrayLike, name: str) -> NDArray[np.float64]:
    """Validate a real vector before converting to double precision."""
    values = np.asarray(values)
    if values.ndim != 1 or values.dtype.kind not in "iuf":
        raise ValueError(f"{name} must be a one-dimensional array of real numbers")
    values = values.astype(np.float64)
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{name} must contain only finite values")
    return values


def _phase_matrix(phi: float) -> NDArray[np.complex128]:
    """Return D(phi) = diag(exp(i phi), exp(-i phi)); phi is in radians."""
    return np.diag(np.exp(1j * np.array([phi, -phi])))


def evaluate_qsp(
    phases: ArrayLike, x_values: ArrayLike
) -> tuple[NDArray[np.complex128], NDArray[np.complex128]]:
    """Return the full QSP matrices U and their upper-left entries P.

    For d+1 phases, evaluate the written product
        U(x) = D(phi_0) W(x) D(phi_1) ... W(x) D(phi_d),
    where D(phi) = diag(exp(i phi), exp(-i phi)) and
    W(x) = [[x, i sqrt(1-x^2)], [i sqrt(1-x^2), x]].

    Parameters
    ----------
    phases : one-dimensional array-like
        Nonempty, finite real phase angles in radians. The same phase list
        is used at every x. Phases are neither rounded nor wrapped here.
    x_values : one-dimensional array-like
        Finite real inputs in [-1, 1]. An empty array is allowed.

    Returns
    -------
    U : complex128 ndarray, shape (N, 2, 2)
        Full matrix for each input, preserving input order.
    P : complex128 ndarray, shape (N,)
        P(x) = U(x)[0, 0], a complex amplitude, not a probability.
        This is a view into U. A solver-specific real/imaginary readout
        must be selected separately.

    Raises
    ------
    ValueError
        If inputs violate the shape, realness, finiteness, phase-count,
        or signal-domain requirements. Out-of-domain x values are rejected,
        not clipped.

    Notes
    -----
    Uses double precision, O(N*d) work, and O(N) working storage. Only
    the phase index is looped over; all x values are evaluated together.
    """
    phases = _real_vector(phases, "phases")
    x = _real_vector(x_values, "x_values")
    if phases.size == 0:
        raise ValueError("phases must contain at least one angle")
    if np.any(np.abs(x) > 1):
        raise ValueError("x_values must lie in [-1, 1]")

    s = np.sqrt(1 - x * x)
    W = np.empty((x.size, 2, 2), dtype=np.complex128)
    W[:, 0, 0] = W[:, 1, 1] = x
    W[:, 0, 1] = W[:, 1, 0] = 1j * s

    U = np.broadcast_to(_phase_matrix(phases[0]), W.shape).copy()
    for phi in phases[1:]:
        U = U @ W
        U = U @ _phase_matrix(phi)

    P = U[:, 0, 0]
    return U, P
