"""Definite-parity core targets and explicitly recorded approximation domains."""

import numpy as np
from scipy.fft import dct
from scipy.optimize import brentq
from scipy.special import erf, jv


def global_bound(coefficients):
    """Upper estimate from a theta grid and a between-node curvature bound.

    q(theta)=sum c_k cos(k theta) has |q''| <= sum k^2 |c_k|.
    An interior maximum of |q| is stationary; its nearest grid point is
    at distance at most delta_theta/2. Thus max|q| <= sampled_max +
    sum(k^2 |c_k|)*delta_theta^2/8 in exact arithmetic. Endpoints are sampled.
    The numerical estimate includes a float margin, not interval arithmetic.
    """
    c = np.asarray(coefficients)
    if c.ndim != 1 or c.size == 0 or c.dtype.kind not in "iuf" or not np.all(np.isfinite(c)):
        raise ValueError("coefficients must be a finite real vector")
    c = c.astype(float)
    n = max(8193, 64 * (len(c) - 1) + 1)
    theta = np.linspace(0, np.pi, n)
    sampled = float(np.max(np.abs(np.polynomial.chebyshev.chebval(np.cos(theta), c))))
    curvature = float(np.sum(np.arange(len(c), dtype=float) ** 2 * np.abs(c)))
    remainder = curvature * (np.pi / (n - 1)) ** 2 / 8
    margin = 1e-12 + 64 * np.finfo(float).eps * float(np.sum(np.abs(c)))
    return dict(method="theta_grid_plus_second_derivative_bound", points=n,
                sampled_max=sampled, between_node_allowance=remainder,
                arithmetic_margin=margin, upper_estimate=sampled + remainder + margin,
                interval_arithmetic=False)


def build_target(family, degree, *, tail_goal=1e-7, hamiltonian_scale=.5,
                 sign_scale=.9, sign_degree_per_delta=6., sign_gap_product=2.):
    """Construct one parity-compatible polynomial and its target metadata.

    Hamiltonian time is chosen so the numerically summed omitted Bessel
    coefficient tail is tail_goal. Sign uses an erf construction but is
    evaluated against sign(x), outside its explicitly recorded gap.
    """
    if isinstance(degree, bool) or not isinstance(degree, (int, np.integer)) or degree < 1:
        raise ValueError("degree must be a positive integer")
    if family not in ("cosine", "sine", "sign"):
        raise ValueError("family must be cosine, sine, or sign")
    parity = 0 if family == "cosine" else 1
    if degree % 2 != parity:
        raise ValueError("degree parity does not match the target family")
    if not (0 < tail_goal < .1 and 0 < hamiltonian_scale < 1 and 0 < sign_scale < 1):
        raise ValueError("invalid approximation goal or amplitude scale")
    if not np.isfinite(sign_degree_per_delta) or not np.isfinite(sign_gap_product) or sign_degree_per_delta <= 0 or sign_gap_product <= 0:
        raise ValueError("sign sharpness and gap settings must be positive")
    c = np.zeros(degree + 1)
    target = dict(family=family, requested_degree=int(degree), degree=int(degree), parity=parity,
                  coefficient_basis="Chebyshev", signal_interval=[-1., 1.])
    if family != "sign":
        # The finite sum is explicitly an estimate, not a rigorous tail proof.
        omitted_k = np.arange(degree + 2, degree + 1026, 2)
        def tail(tau):
            return float(2 * np.sum(np.abs(jv(omitted_k, tau))))
        tau = float(brentq(lambda t: tail(t) - tail_goal, 0., float(degree), xtol=1e-13))
        k = np.arange(parity, degree + 1, 2)
        c[k] = 2 * (-1.) ** ((k - parity) // 2) * jv(k, tau)
        if parity == 0:
            c[0] *= .5
        c *= hamiltonian_scale
        target.update(parameters=dict(tau=tau), target_scale=hamiltonian_scale,
                      polynomial_scale=hamiltonian_scale, application_domain=[[-1., 1.]],
                      construction=dict(method="truncated_Jacobi_Anger", omitted_tail_goal=tail_goal,
                                        estimated_unscaled_tail_l1=tail(tau),
                                        omitted_terms_summed=len(omitted_k), rigorous_tail_bound=False),
                      baseline_accuracy_goal=1e-6)
    else:
        delta = max(3., degree / sign_degree_per_delta)
        gap = sign_gap_product / delta
        if gap >= 1:
            raise ValueError("sign gap must be smaller than one")
        n = 2 ** int(np.ceil(np.log2(max(256, 8 * (degree + 1)))))
        def sample_coefficients(count):
            theta = np.pi * (np.arange(count) + .5) / count
            coefficients = dct(erf(delta * np.cos(theta)), type=2) / count
            coefficients[0] *= .5
            return coefficients
        raw = sample_coefficients(n)
        refined = sample_coefficients(2 * n)
        c[:] = raw[:degree + 1]
        c[0::2] = 0.
        unscaled_bound = global_bound(c)
        scale = (sign_scale - 1e-10) / unscaled_bound["upper_estimate"]
        c *= scale
        target.update(parameters=dict(delta=delta, gap=gap, inverse_gap=1 / gap),
                      target_scale=sign_scale, polynomial_scale=float(scale),
                      application_domain=[[-1., -gap], [gap, 1.]],
                      construction=dict(method="erf_surrogate_DCT_II_truncation", samples=n,
                                        refined_samples=2 * n, sign_degree_per_delta=sign_degree_per_delta,
                                        gap_times_delta=sign_gap_product,
                                        retained_coefficient_refinement_l1=float(np.sum(np.abs(raw[:degree+1] - refined[:degree+1]))),
                                        estimated_omitted_coefficient_l1=float(np.sum(np.abs(raw[degree+1:]))),
                                        unscaled_bound=unscaled_bound), baseline_accuracy_goal=1e-2)
    target["coefficients"] = c.tolist()
    target["boundedness"] = global_bound(c)
    target["case_id"] = f"{family}_d{degree:04d}"
    return target


def target_values(target, x):
    """The desired scaled application target, including true sign for sign cases."""
    x = np.asarray(x, dtype=float)
    if target["family"] == "cosine":
        return target["target_scale"] * np.cos(target["parameters"]["tau"] * x)
    if target["family"] == "sine":
        return target["target_scale"] * np.sin(target["parameters"]["tau"] * x)
    return target["target_scale"] * np.sign(x)


def application_mask(target, x):
    x = np.asarray(x)
    if target["family"] == "sign":
        return np.abs(x) >= target["parameters"]["gap"]
    return np.ones(x.shape, dtype=bool)


def validation_grid(target):
    """Chebyshev endpoints/zero, independent interior midpoints, and exact gap edges."""
    n = max(2049, 10 * target["degree"] + 1)
    x = np.cos(np.linspace(0, np.pi, n))
    x[n // 2] = 0.
    midpoint_count = max(1024, 2 * target["degree"])
    midpoints = -1 + (2 * np.arange(midpoint_count) + 1) / midpoint_count
    if target["family"] == "sign":
        gap = target["parameters"]["gap"]
        x = np.r_[x, -gap, gap]
    return np.unique(np.r_[x, midpoints])


def audit_grid(target):
    x = np.cos(np.linspace(0, np.pi, 129))
    x[64] = 0.
    if target["family"] == "sign":
        gap = target["parameters"]["gap"]
        x = np.r_[x, -gap, gap]
    return np.unique(np.r_[x, np.linspace(-.99, .99, 64)])
