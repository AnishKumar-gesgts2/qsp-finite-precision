"""Reproduce three built-in pyqsp examples and a linear diagnostic.

Run from the repository root with the locked validation environment:
    python experiments/stage1/compare_solvers.py
Outputs are validation fixtures, not the Stage 2 phase library.
"""

import contextlib
import csv
import hashlib
import importlib.metadata
import io
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erf

import pyqsp.angle_sequence as angle_sequence
import pyqsp.poly as poly
import pyqsp.response as response
import pyqsp.sym_qsp_opt as sym_qsp_opt
import qsppack.solver as qsppack_solver
import qsppack.utils as qsppack_utils
from qsp_finite_precision.stage1 import (
    evaluate_qsp, expand_symmetric_phases, qsppack_full_phases,
)


ROOT = Path(__file__).resolve().parents[2]
EVALUATOR_TOLERANCE = 5e-13
TARGET_TOLERANCE = 1e-10
COEFFICIENT_TOLERANCE = 1e-12


def max_abs(values):
    values = np.asarray(values)
    if not np.all(np.isfinite(values)):
        raise ValueError("Non-finite comparison result")
    return float(np.max(np.abs(values)))


def error_stats(difference):
    """Sampled maximum absolute error and root mean square error."""
    maximum = max_abs(difference)
    return dict(max_abs=maximum, rmse=float(np.sqrt(np.mean(np.abs(difference) ** 2))))


def reference_graph(figures, name, x, original, target, P, package_P,
                    full, scale, reference_label, function_errors, agreement_errors):
    """Display function, decomposition phases, reconstruction, and errors."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), layout="constrained")
    curve_ax, phase_ax, error_ax, metric_ax = axes.flat
    curve_ax.plot(x, original, color="#24364b", lw=3, label="Original function f(x)")
    curve_ax.plot(x, target / scale, color="#8966a8", ls="-.", lw=1.6, label="Target polynomial / scale")
    curve_ax.plot(x, P.imag / scale, color="#16837b", ls="--", lw=2, label="Reconstructed from phases: Im P / scale")
    curve_ax.plot(x, package_P.imag / scale, color="#ce7435", ls=":", lw=1.8, label="pyqsp reconstruction / scale")
    curve_ax.set(title="Original function and reconstructed response", xlabel="Signal input x", ylabel="Original-function units")
    curve_ax.legend(fontsize=8, loc="best")
    markerline, stemlines, baseline = phase_ax.stem(np.arange(full.size), full)
    plt.setp(markerline, color="#16837b", markersize=5)
    plt.setp(stemlines, color="#16837b", linewidth=1.4)
    plt.setp(baseline, color="#8e9ba7", linewidth=.8)
    phase_ax.set(title=f"Decomposed sequence: {full.size} full phase angles", xlabel="Phase index j", ylabel="Phase angle (radians)")
    phase_ax.set_xticks(np.arange(full.size))
    phase_ax.margins(y=.2)
    phase_ax.text(.5, .97, r"$D(\phi_0)W(x)D(\phi_1)\cdots W(x)D(\phi_d)$", transform=phase_ax.transAxes, ha="center", va="top", fontsize=9)
    for difference, label, color, style in (
        ((target / scale) - original, "Polynomial approximation", "#8966a8", "-"),
        ((P.imag / scale) - original, "Total reconstruction vs original", "#16837b", "--"),
        ((P.imag - target) / scale, "Phase reconstruction vs polynomial", "#ce7435", "-"),
        ((P - package_P) / scale, "Local vs pyqsp (complex amplitude)", "#64798d", ":"),
    ):
        error_ax.semilogy(x, np.maximum(np.abs(difference), 1e-18), label=label, color=color, ls=style, lw=1.2)
    error_ax.set(title="Separate error sources (sampled grid)", xlabel="Signal input x", ylabel="Absolute error (display floor: 1e-18)")
    error_ax.legend(fontsize=7.7, loc="best")
    metric_ax.axis("off")
    metric_rows = [
        ["Polynomial vs original", function_errors["polynomial"]],
        ["Reconstruction vs original", function_errors["local_reconstruction"]],
        ["Reconstruction vs polynomial", function_errors["phase_vs_polynomial"]],
    ] + [[key, stats] for key, stats in agreement_errors.items()]
    table = metric_ax.table(
        cellText=[[label, f"{stats['max_abs']:.3e}", f"{stats['rmse']:.3e}"] for label, stats in metric_rows],
        colLabels=["Comparison", "Max abs error", "RMSE"],
        colWidths=[.58, .21, .21], cellLoc="left", bbox=[0, .17, 1, .72],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.2)
    table.scale(1, 1.65)
    for (row, _), cell in table.get_celld().items():
        cell.set_edgecolor("#e1e7ec")
        if row == 0:
            cell.set_facecolor("#e8f1f3")
            cell.set_text_props(weight="bold")
    metric_ax.set_title("Error metrics in original-function units", pad=14)
    metric_ax.text(0, .02, "Package rows compare each package with our evaluator using its own phases.\nRMSE uses equal weights on the 1,025 sampled inputs; it is not an integral norm.", transform=metric_ax.transAxes, fontsize=8, va="bottom")
    for ax in (curve_ax, phase_ax, error_ax):
        ax.grid(alpha=.18)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Stage 1B | {name.replace('_', ' ').title()} | {reference_label}\nDegree {full.size - 1}; solver scale = {scale:.10g}; readout = Im P", fontsize=14)
    path = figures / f"{name}_reference.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path.name


def write_reference_readme(examples):
    """Refresh only the generated graph/metric section in the Stage 1B README."""
    path = ROOT / "experiments/stage1/README.md"
    start, end = "<!-- BEGIN REFERENCE GRAPHS -->", "<!-- END REFERENCE GRAPHS -->"
    content = path.read_text(encoding="utf-8")
    if content.count(start) != 1 or content.count(end) != 1:
        raise RuntimeError("Stage 1B README reference markers missing or duplicated")
    lines = [start, "", "## Reference graphs and error metrics", "",
             "Every graph includes the original function, target polynomial, response reconstructed from the synthesized phases, the full phase sequence, and separate error curves. The function curves and tables below use original-function units: divide the polynomial and reconstructed readouts by the recorded generator scale. This is a display conversion, not an additional quantum operation. QSPPACK function-accuracy rows use its synthesized phases reconstructed by our evaluator; separate agreement rows compare that reconstruction with the package's own response. Native scaled metrics and all phases remain in the JSON report.", "",
             "Max error and RMSE are sampled statistics on the same 1,025-point grid. RMSE gives equal weight to each sampled point; because the grid is nonuniform, it is not a uniform-domain integral norm. Exact zero errors use a labeled plotting floor of `1e-18`; tables retain zero.", ""]
    for example in examples:
        title = example["name"].replace("_", " ").title()
        lines += [f"### {title}", "", f"Original reference: {example['reference_function_label']}. Degree **{example['degree']}**; generator scale **{example['generator_scale']:.10g}**.", "",
                  f"![{title}: original function, phases, reconstruction, and errors](../../figures/stage1/{example['reference_graph']})", "",
                  "| Response vs original function | Max absolute error | RMSE |", "| --- | ---: | ---: |"]
        for key, label in [("polynomial", "Target polynomial / scale"), ("local_reconstruction", "Our phase reconstruction / scale"), ("pyqsp_reconstruction", "pyqsp reconstruction / scale")]:
            stats = example["original_function_errors"][key]
            lines.append(f"| {label} | {stats['max_abs']:.6e} | {stats['rmse']:.6e} |")
        for check in example["qsppack_checks"]:
            label = f"QSPPACK {'real' if check['targetPre'] else 'imaginary'}, {check['typePhi']}"
            stats = check["original_function_error"]
            lines.append(f"| {label} / scale | {stats['max_abs']:.6e} | {stats['rmse']:.6e} |")
        lines += ["", "| Reconstruction / evaluator check | Max absolute error | RMSE |", "| --- | ---: | ---: |"]
        stats = example["original_function_errors"]["phase_vs_polynomial"]
        lines.append(f"| Our reconstruction vs polynomial | {stats['max_abs']:.6e} | {stats['rmse']:.6e} |")
        for label, stats in example["evaluator_agreement_errors"].items():
            lines.append(f"| {label} | {stats['max_abs']:.6e} | {stats['rmse']:.6e} |")
        if example["name"] == "smoothed_sign":
            lines += ["", "The original reference for this built-in test is the smooth function `erf(3x)`. This graph does not claim uniform approximation of discontinuous `sign(x)`; the gap-domain sign specification belongs to Stage 2."]
        lines.append("")
    lines.append(end)
    before, remaining = content.split(start)
    _, after = remaining.split(end)
    path.write_text(before + "\n".join(lines) + after, encoding="utf-8")


def main():
    results = ROOT / "results/stage1"
    figures = ROOT / "figures/stage1"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    # Endpoints, exact zero, clustered endpoint samples, and interior midpoints.
    lobatto = np.cos(np.linspace(0, np.pi, 513))
    lobatto[256] = 0.0
    midpoints = -1 + (2 * np.arange(512) + 1) / 512
    x = np.unique(np.concatenate((lobatto, midpoints)))
    configs = [
        ("linear", None, {"slope": .5}),
        ("cosine", poly.PolyCosineTX, {"tau": 2.0, "epsilon": 1e-3}),
        ("sine", poly.PolySineTX, {"tau": 2.0, "epsilon": 1e-3}),
        ("smoothed_sign", poly.PolySign, {"degree": 15, "delta": 3.0, "max_scale": .9}),
    ]
    rows, examples = [], []
    log = io.StringIO()
    fig, axes = plt.subplots(2, 4, figsize=(17, 7), sharex="col", layout="constrained")
    for column, (name, factory, parameters) in enumerate(configs):
        log.write(f"\n=== {name} ===\n")
        with contextlib.redirect_stdout(log):
            if factory is None:
                coefficients, scale = np.array([0., parameters["slope"]]), 1.0
            else:
                coefficients, scale = factory().generate(
                    **parameters, ensure_bounded=True, return_scale=True, chebyshev_basis=True,
                )
            # 0.2.0 returns (full phases, reduced phases, parity). Its symmetric
            # branch hardcodes crit=1e-12 and does not return convergence metadata.
            full, reduced, parity = angle_sequence.QuantumSignalProcessingPhases(
                coefficients, method="sym_qsp", chebyshev_basis=True,
            )
        coefficients = np.asarray(coefficients)
        full = np.asarray(full)
        protocol = sym_qsp_opt.SymmetricQSPProtocol(reduced_phases=reduced, parity=parity)
        actual_coefficients, _ = protocol.gen_jacobian()
        coefficient_residual = float(np.linalg.norm(actual_coefficients - coefficients[parity::2], ord=1))
        target = np.polynomial.chebyshev.chebval(x, coefficients)
        U, P = evaluate_qsp(full, x)
        package_P = response.ComputeQSPResponse(
            x, full, signal_operator="Wx", measurement="z", sym_qsp=True,
        )["pdat"]
        package_U = protocol.gen_unitary(x)
        metrics = {
            "complex_amplitude_difference": max_abs(P - package_P),
            "full_unitary_spectral_difference": float(np.linalg.norm(U - package_U, ord=2, axis=(-2, -1)).max()),
            "reduced_expansion_difference": max_abs(full - expand_symmetric_phases(reduced, parity)),
            "solver_polynomial_residual": max_abs(P.imag - target),
            "returned_coefficient_l1_residual": coefficient_residual,
            "unitarity_residual": float(np.linalg.norm(U.conj().swapaxes(-1, -2) @ U - np.eye(2), ord=2, axis=(-2, -1)).max()),
        }
        if name == "linear":
            original_function = parameters["slope"] * x
            reference_label = "f(x) = 0.5 x"
        elif name == "cosine":
            original_function = np.cos(parameters["tau"] * x)
            reference_label = "f(x) = cos(2x)"
        elif name == "sine":
            original_function = np.sin(parameters["tau"] * x)
            reference_label = "f(x) = sin(2x)"
        else:
            # This is the smooth erf surrogate, NOT a claim of uniform sign
            # approximation across its discontinuity. Gap-domain work is Stage 2.
            original_function = erf(parameters["delta"] * x)
            reference_label = "f(x) = erf(3x)"
        smooth_function = scale * original_function
        metrics["polynomial_vs_smooth_function_residual"] = max_abs(target - smooth_function)
        function_errors = dict(
            polynomial=error_stats(target / scale - original_function),
            local_reconstruction=error_stats(P.imag / scale - original_function),
            pyqsp_reconstruction=error_stats(package_P.imag / scale - original_function),
            phase_vs_polynomial=error_stats((P.imag - target) / scale),
        )
        agreement_errors = {"Local vs pyqsp (complex)": error_stats((P - package_P) / scale)}
        qchecks, qcurves = [], {}
        for target_pre in (True, False):
            for type_phi in ("full", "reduced"):
                opts = dict(method="Newton", criteria=COEFFICIENT_TOLERANCE,
                            maxiter=100, targetPre=target_pre, typePhi=type_phi, print=False)
                with contextlib.redirect_stdout(log):
                    qphases, info = qsppack_solver.solve(coefficients[parity::2], parity, opts=opts)
                before = np.array(qphases, copy=True)
                qresponse = qsppack_utils.get_entry(x, qphases, info)
                if not np.array_equal(qphases, before):
                    raise RuntimeError("QSPPACK evaluation changed caller phases")
                mapped = qsppack_full_phases(qphases, parity, target_pre=target_pre, type_phi=type_phi)
                _, qP = evaluate_qsp(mapped, x)
                selected = qP.real if target_pre else qP.imag
                discrepancy = max_abs(selected - qresponse)
                residual = max_abs(selected - target)
                passed = bool(info["converged"] and discrepancy <= EVALUATOR_TOLERANCE and residual <= TARGET_TOLERANCE)
                key = ("real" if target_pre else "imag") + "_" + type_phi
                qcurves[key] = qresponse
                agreement_errors[f"QSP {'Re' if target_pre else 'Im'}/{type_phi}: local vs package"] = error_stats((selected - qresponse) / scale)
                qchecks.append(dict(
                    targetPre=target_pre, typePhi=type_phi, phases=before.tolist(),
                    converged=bool(info["converged"]), solver_value=float(info["value"]),
                    iterations=int(info["iter"]), evaluator_difference=discrepancy,
                    polynomial_residual=residual, passed=passed,
                    original_function_error=error_stats(selected / scale - original_function),
                    evaluator_rmse=error_stats(selected - qresponse)["rmse"],
                    polynomial_rmse=error_stats(selected - target)["rmse"],
                ))
        passed = bool(
            all(np.isfinite(list(metrics.values())))
            and all(metrics[k] <= EVALUATOR_TOLERANCE for k in (
                "complex_amplitude_difference", "full_unitary_spectral_difference",
                "reduced_expansion_difference", "unitarity_residual"))
            and metrics["solver_polynomial_residual"] <= TARGET_TOLERANCE
            and coefficient_residual <= COEFFICIENT_TOLERANCE
            and all(check["passed"] for check in qchecks)
        )
        graph = reference_graph(figures, name, x, original_function, target, P, package_P,
                                full, scale, reference_label, function_errors, agreement_errors)
        examples.append(dict(
            name=name, generator=factory.__name__ if factory else "explicit_linear_coefficients", generator_parameters=parameters,
            generator_scale=float(scale), degree=int(full.size - 1), parity=int(parity),
            chebyshev_coefficients=coefficients.tolist(), full_phases=full.tolist(),
            reduced_phases=np.asarray(reduced).tolist(), metrics=metrics,
            qsppack_checks=qchecks, passed=passed,
            reference_function_label=reference_label, reference_graph=graph,
            original_function_errors=function_errors, evaluator_agreement_errors=agreement_errors,
        ))
        for k, value in enumerate(x):
            rows.append(dict(
                example=name, x=float(value), polynomial=float(target[k]),
                smooth_function=float(smooth_function[k]),
                original_function=float(original_function[k]),
                original_units_polynomial=float(target[k] / scale),
                original_units_reconstruction=float(P[k].imag / scale),
                approximation_error=float(abs(target[k] / scale - original_function[k])),
                phase_reconstruction_error=float(abs(P[k].imag - target[k]) / scale),
                total_original_function_error=float(abs(P[k].imag / scale - original_function[k])),
                local_real=float(P[k].real), local_imag=float(P[k].imag),
                pyqsp_real=float(package_P[k].real), pyqsp_imag=float(package_P[k].imag),
                **{f"qsppack_{key}": float(curve[k]) for key, curve in qcurves.items()},
            ))
        axes[0, column].plot(x, original_function, color="#24364b", lw=2.8, label="Original function")
        axes[0, column].plot(x, target / scale, color="#8966a8", ls="-.", lw=1.5, label="Target polynomial / scale")
        axes[0, column].plot(x, P.imag / scale, color="#16837b", ls="--", lw=1.8, label="Our reconstruction / scale")
        axes[0, column].plot(x, package_P.imag / scale, color="#ce7435", ls=":", lw=1.6, label="pyqsp reconstruction / scale")
        axes[0, column].set_title(f"{name.replace('_', ' ').title()} | degree {full.size - 1}")
        axes[0, column].set_ylabel("Original-function units")
        axes[1, column].semilogy(x, np.maximum(np.abs(target / scale - original_function), 1e-18), color="#8966a8", label="Polynomial approximation")
        axes[1, column].semilogy(x, np.maximum(np.abs(P.imag / scale - original_function), 1e-18), color="#16837b", ls="--", label="Total error vs original")
        axes[1, column].semilogy(x, np.maximum(np.abs(P.imag - target) / scale, 1e-18), color="#ce7435", alpha=.8, label="Phase reconstruction residual")
        axes[1, column].semilogy(x, np.maximum(np.abs(P - package_P) / scale, 1e-18), color="#64798d", label="Evaluator difference")
        axes[1, column].set_ylabel("Absolute difference (floor: 1e-18)")
        axes[1, column].set_xlabel("Signal input x")
        for ax in axes[:, column]:
            ax.grid(alpha=.18)
            ax.spines[["top", "right"]].set_visible(False)
        print(f"{name}: degree={full.size - 1}; evaluator={metrics['complex_amplitude_difference']:.3e}; polynomial={metrics['solver_polynomial_residual']:.3e}; passed={passed}")
    axes[0, 0].legend(fontsize=8)
    axes[1, 0].legend(fontsize=8)
    fig.suptitle("Stage 1B: original functions and reconstructed phase responses", fontsize=15)
    fig.savefig(figures / "solver_comparisons.png", dpi=160)
    plt.close(fig)
    source_files = {
        "pyqsp.angle_sequence": Path(angle_sequence.__file__),
        "pyqsp.response": Path(response.__file__),
        "pyqsp.sym_qsp_opt": Path(sym_qsp_opt.__file__),
        "pyqsp.poly": Path(poly.__file__),
        "qsppack.solver": Path(qsppack_solver.__file__),
        "qsppack.utils": Path(qsppack_utils.__file__),
        "local.forward": ROOT / "src/qsp_finite_precision/stage1/forward.py",
        "local.conventions": ROOT / "src/qsp_finite_precision/stage1/conventions.py",
        "experiment": Path(__file__),
    }
    report = dict(
        python=platform.python_version(), platform=platform.platform(),
        versions={key: importlib.metadata.version(key) for key in ("numpy", "scipy", "pyqsp", "qsppack", "matplotlib")},
        grid=dict(points=int(x.size), description="513 Chebyshev-Lobatto points with exact zero plus 512 uniform midpoints"),
        tolerances=dict(evaluator=EVALUATOR_TOLERANCE, polynomial=TARGET_TOLERANCE, coefficient_l1=COEFFICIENT_TOLERANCE),
        source_sha256={key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in source_files.items()},
        matlab_source_inspected_commit="7bc7b7622e05039e4c2cdda7d5739e99c3752be6",
        matlab_executed=False,
        scope="Unrounded binary64, low-degree convention validation. Python QSPPACK is a separate implementation with shared algorithm lineage; not a MATLAB execution or Stage 2 library.",
        examples=examples, passed=all(example["passed"] for example in examples),
    )
    (results / "solver_comparisons.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (results / "solver_output.log").write_text(log.getvalue(), encoding="utf-8")
    with (results / "solver_responses.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    if not report["passed"]:
        raise SystemExit("Solver validation failed; inspect results/stage1/solver_comparisons.json")
    write_reference_readme(examples)
    print(f"All {len(examples)} examples and all {sum(len(e['qsppack_checks']) for e in examples)} Python QSPPACK solver mappings passed on {x.size} inputs.")


if __name__ == "__main__":
    main()
