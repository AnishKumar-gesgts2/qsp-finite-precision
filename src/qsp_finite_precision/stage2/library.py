"""Generate and archive full-precision baseline cases with explicit pass criteria."""

import contextlib
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import time

import numpy as np
from pyqsp.response import ComputeQSPResponse
from pyqsp.sym_qsp_opt import newton_solver
from qsppack import get_entry, solve

from ..stage1 import evaluate_qsp
from .targets import application_mask, audit_grid, target_values, validation_grid


def stats(values):
    values = np.asarray(values)
    if not values.size or not np.all(np.isfinite(values)):
        raise ValueError("metric input must be nonempty and finite")
    return dict(max_abs=float(np.max(np.abs(values))),
                rmse=float(np.sqrt(np.mean(np.abs(values) ** 2))))


def generate_case(target, *, criteria=1e-12, maxiter=100, evaluator_tolerance=1e-10):
    """Use pyqsp's documented symmetric Newton solver, then independently verify it.

    Direct access to newton_solver supplies the convergence information omitted
    by pyqsp 0.2.0's high-level sym_qsp return. No inverse solver is implemented here.
    """
    c = np.asarray(target["coefficients"], dtype=float)
    parity = target["parity"]
    log = io.StringIO()
    started = time.perf_counter()
    with contextlib.redirect_stdout(log):
        reduced, reported, iterations, protocol = newton_solver(c[parity::2], parity, crit=criteria, maxiter=maxiter)
    full = protocol.full_phases.copy()
    solver_seconds = time.perf_counter() - started
    actual_coefficients, _ = protocol.gen_jacobian()
    returned_residual = float(np.linalg.norm(actual_coefficients - c[parity::2], ord=1))
    # This installed solver checks its pre-update residual before returning its
    # updated phases. Record both, and require its own stop and our post-check.
    solver_converged = bool(reported < criteria and returned_residual < criteria)
    x = validation_grid(target)
    f = target_values(target, x)
    p = np.polynomial.chebyshev.chebval(x, c)
    U, P = evaluate_qsp(full, x)
    mask = application_mask(target, x)
    xa = audit_grid(target)
    _, Pa = evaluate_qsp(full, xa)
    package_P = ComputeQSPResponse(xa, full, signal_operator="Wx", measurement="z", sym_qsp=True)["pdat"]
    unitary_error = float(np.linalg.norm(U.conj().swapaxes(-1,-2) @ U - np.eye(2), ord=2, axis=(-2,-1)).max())
    metrics = dict(approximation=stats((p-f)[mask]), synthesis=stats(P.imag-p),
                   baseline_application=stats((P.imag-f)[mask]),
                   pyqsp_evaluator_agreement=stats(Pa-package_P),
                   unitarity_max=unitary_error, phase_symmetry_max=float(np.max(np.abs(full-full[::-1]))),
                   sampled_polynomial_max=float(np.max(np.abs(p))), sampled_amplitude_max=float(np.max(np.abs(P))))
    # Supplementary Python cross-check. The original MATLAB check stays pending.
    with contextlib.redirect_stdout(log):
        qphases, qinfo = solve(c[parity::2], parity, opts=dict(method="Newton",criteria=criteria,
                              maxiter=maxiter,targetPre=True,typePhi="full",print=False))
    _, qP = evaluate_qsp(qphases, x)
    _, qPa = evaluate_qsp(qphases, xa)
    qreference = get_entry(xa, qphases, qinfo)
    qmetrics = dict(evaluator_agreement=stats(qPa.real-qreference),
                    synthesis=stats(qP.real-p), baseline_application=stats((qP.real-f)[mask]),
                    pyqsp_readout_difference=stats(qP.real-P.imag))
    adjacent = np.abs(np.diff(full))
    flags = adjacent <= 1e-8
    longest, current = 1, 1
    for flag in flags:
        current = current + 1 if flag else 1
        longest = max(longest, current)
    threshold = .9 + 1e-12 if target["family"] == "sign" else 1.
    checks = dict(
        solver_converged=solver_converged,
        phase_count=bool(full.size == target["degree"]+1),
        bounded_polynomial=bool(target["boundedness"]["upper_estimate"] <= threshold),
        synthesis=bool(metrics["synthesis"]["max_abs"] <= evaluator_tolerance),
        baseline_accuracy=bool(metrics["baseline_application"]["max_abs"] <= target["baseline_accuracy_goal"]),
        package_agreement=bool(metrics["pyqsp_evaluator_agreement"]["max_abs"] <= evaluator_tolerance),
        unitarity=bool(unitary_error <= evaluator_tolerance),
        python_qsppack=bool(qinfo["converged"] and qmetrics["evaluator_agreement"]["max_abs"] <= evaluator_tolerance
                           and qmetrics["synthesis"]["max_abs"] <= evaluator_tolerance
                           and qmetrics["baseline_application"]["max_abs"] <= target["baseline_accuracy_goal"]),
    )
    case = dict(schema_version=1, case_id=target["case_id"], target=target,
                solver=dict(name="pyqsp",method="sym_qsp_opt.newton_solver (sym_qsp)",
                            version=importlib.metadata.version("pyqsp"),criteria=criteria,maxiter=maxiter,
                            reported_preupdate_residual=float(reported),returned_coefficient_l1_residual=returned_residual,
                            iterations=int(iterations),converged=solver_converged,seconds=solver_seconds),
                convention=dict(signal="Wx",phase="exp(i phi Z)",order="D0 W D1 ... W Dd",readout="imag(U[0,0])",
                                phases="full",units="radians",wrapped=False,quantized=False),
                full_phases=full.tolist(),reduced_phases=np.asarray(reduced).tolist(),
                grid=dict(chebyshev_lobatto_points=max(2049,10*target["degree"]+1),
                          total_validation_points=int(x.size),application_points=int(mask.sum()),
                          additional_points="uniform midpoints and exact sign-gap edges",audit_points=int(xa.size),
                          maxima="sampled",rmse="equal weight over stated sampled points; not a domain integral"),
                metrics=metrics,
                phase_structure=dict(adjacent_threshold_radians=1e-8,
                                     nearly_equal_adjacent_fraction=float(np.mean(flags)),
                                     longest_nearly_equal_run=int(longest),interpretation="descriptive only; no rounding/correlation conclusion"),
                python_qsppack=dict(version=importlib.metadata.version("qsppack"),method="Newton",targetPre=True,typePhi="full",
                                    phases=np.asarray(qphases).tolist(),converged=bool(qinfo["converged"]),
                                    residual=float(qinfo["value"]),iterations=int(qinfo["iter"]),metrics=qmetrics),
                matlab_qsppack=dict(status="pending",executed=False),
                acceptance=dict(evaluator_tolerance=evaluator_tolerance,coefficient_tolerance=criteria,checks=checks),
                passed=all(checks.values()))
    curves = dict(x=x,target=f,polynomial=p,readout=P.imag,amplitude_real=P.real,
                  application_mask=mask,qsppack_readout=qP.real,
                  approximation_error=np.abs(p-f),synthesis_error=np.abs(P.imag-p),baseline_error=np.abs(P.imag-f))
    audit = dict(x=xa,local_real=Pa.real,local_imag=Pa.imag,pyqsp_real=package_P.real,pyqsp_imag=package_P.imag,
                 qsppack_local=qPa.real,qsppack_package=qreference)
    return case, curves, audit, log.getvalue()


def write_case(path, case):
    """JSON preserves Python binary64 round-trip values; no phase shortening."""
    path = Path(path)
    if not case["passed"]:
        raise ValueError("failed cases must be recorded as failures, not successful library files")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(case, indent=2, allow_nan=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_case(path):
    case = json.loads(Path(path).read_text(encoding="utf-8"))
    if case.get("schema_version") != 1 or not case.get("passed"):
        raise ValueError("not a successful supported library case")
    phases = np.asarray(case["full_phases"], dtype=float)
    target = case["target"]
    if phases.ndim != 1 or phases.size != target["degree"] + 1 or not np.all(np.isfinite(phases)):
        raise ValueError("invalid saved full phase list")
    if case["convention"]["quantized"] or case["convention"]["readout"] != "imag(U[0,0])":
        raise ValueError("unexpected baseline convention")
    if len(target["coefficients"]) != phases.size or not np.all(np.isfinite(target["coefficients"])) or not all(case["acceptance"]["checks"].values()):
        raise ValueError("invalid saved coefficients or acceptance results")
    return case
