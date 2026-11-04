"""Deterministic binary phase-word quantizers; all phase quantities in radians."""
import numpy as np


def nearest_index(x):
    """Round to nearest integer with exact half ties toward positive infinity."""
    return np.floor(x + 0.5).astype(np.int64)


def quantize(phases, bits, scheme):
    p = np.asarray(phases, dtype=float)
    if p.ndim != 1 or not p.size or not np.isfinite(p).all():
        raise ValueError('phases must be a nonempty finite vector')
    if bits not in (12, 16, 20, 24, 28, 32):
        raise ValueError('unsupported bit depth')
    if scheme not in ('nearest', 'corrected', 'sigma_delta'):
        raise ValueError('unsupported scheme')
    n = 1 << bits
    step = 2 * np.pi / n
    # Reduce the input to [0, 2pi); retain an unwrapped integer lift so
    # errors describe the locally chosen representative, including at wrap.
    wrapped = np.remainder(p, 2 * np.pi)
    scaled = wrapped / step
    k = nearest_index(scaled)
    if scheme == 'corrected':
        # Preserve total to the nearest available grid point. Only last word
        # changes, and its error can exceed half a step.
        k[-1] += int(nearest_index(np.array([np.sum(scaled - k)]))[0])
    elif scheme == 'sigma_delta':
        carry = 0.0
        for j, value in enumerate(scaled):
            k[j] = int(nearest_index(np.array([value + carry]))[0])
            carry += value - k[j]
    errors = (k - scaled) * step
    words = np.mod(k, n)
    return words, words.astype(float) * step, errors
