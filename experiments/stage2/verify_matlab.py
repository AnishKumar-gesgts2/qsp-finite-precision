"""Verify actual original-MATLAB results against saved targets and our evaluator."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from qsp_finite_precision.stage1 import evaluate_qsp
from qsp_finite_precision.stage2 import load_case
from qsp_finite_precision.stage2.targets import application_mask, target_values, validation_grid


def metrics(values):
    values = np.asarray(values)
    return dict(max_abs=float(np.max(np.abs(values))),
                rmse=float(np.sqrt(np.mean(np.abs(values) ** 2))))


def vector(values, name):
    result = np.asarray(values, dtype=float).reshape(-1)
    if not result.size or not np.all(np.isfinite(result)):
        raise ValueError(f"Invalid MATLAB {name}")
    return result


def coverage(outputs, expected, label):
    if isinstance(outputs, dict):
        outputs = [outputs]
    if len(outputs) != len(expected) or {e["case_id"] for e in outputs} != set(expected):
        raise ValueError(f"Missing, duplicated, or unexpected MATLAB {label}")
    return outputs


def check_solver(output, criteria):
    value = output["solver_value"]
    if value is None or not np.isfinite(value) or not 0 <= value < criteria:
        raise ValueError(f"MATLAB synthesis did not converge: {output['case_id']}")


def check_grid(actual, expected, name):
    actual = vector(actual, name)
    if not np.array_equal(actual, np.asarray(expected)):
        raise ValueError(f"MATLAB {name} does not match the request")
    return actual


def case_data(root, output):
    """Reconstruct MATLAB phases on their complete archived validation grid."""
    root = Path(root)
    case = load_case(root / f"data/phases/stage2/{output['case_id']}.json")
    x = vector(output["validation_x"], "validation inputs")
    native = vector(output["validation_response"], "validation response")
    phases = vector(output["full_phases"], "phases")
    if native.shape != x.shape:
        raise ValueError("MATLAB validation response shape mismatch")
    U, P = evaluate_qsp(phases, x)
    _, primary = evaluate_qsp(case["full_phases"], x)
    target = case["target"]
    polynomial = np.polynomial.chebyshev.chebval(x, target["coefficients"])
    desired = target_values(target, x)
    mask = application_mask(target, x)
    columns = dict(x=x, target=desired, polynomial=polynomial,
                   application_mask=mask, matlab_native=native,
                   matlab_local=P.real, pyqsp_local=primary.imag,
                   approximation_error=np.abs(polynomial - desired),
                   matlab_target_error=np.abs(native - desired),
                   matlab_synthesis_error=np.abs(native - polynomial),
                   matlab_evaluator_error=np.abs(native - P.real),
                   solver_readout_difference=np.abs(native - primary.imag))
    statistics = dict(evaluator_agreement=metrics(native - P.real),
                      synthesis=metrics(native - polynomial),
                      local_synthesis=metrics(P.real - polynomial),
                      baseline_application=metrics((native - desired)[mask]),
                      approximation=metrics((polynomial - desired)[mask]),
                      solver_readout_difference=metrics(native - primary.imag),
                      unitarity_max=float(np.max(np.linalg.norm(
                          U.conj().swapaxes(-1, -2) @ U - np.eye(2), ord=2, axis=(-2, -1)))))
    return case, columns, statistics


def verify_matlab(root, report):
    root = Path(root)
    input_path = root / "results/stage2/matlab_input.json"
    request = json.loads(input_path.read_text())
    if report.get("runtime") != "MATLAB" or not report.get("runtime_version"):
        raise ValueError("Report must identify the actually used MATLAB runtime")
    if (report.get("source_revision") != request["source_revision"]
            or report.get("source_hashes") != request["expected_source_hashes"]):
        raise ValueError("Original MATLAB source identity does not match")
    input_sha256 = hashlib.sha256(input_path.read_bytes()).hexdigest()
    if report.get("input_sha256") != input_sha256:
        raise ValueError("MATLAB input identity does not match the current request")
    expected = {entry["case_id"]: entry for entry in request["cases"]}
    results = []
    for output in coverage(report["cases"], expected, "cases"):
        ident = output["case_id"]
        entry = expected[ident]
        case = load_case(root / f"data/phases/stage2/{ident}.json")
        phases = vector(output["full_phases"], "phases")
        if phases.size != case["target"]["degree"] + 1:
            raise ValueError(f"Invalid MATLAB phase count: {ident}")
        if output["targetPre"] is not True or output["typePhi"] != "full":
            raise ValueError("Unexpected MATLAB phase/readout convention")
        target = case["target"]
        if entry["parity"] != target["parity"] or not np.array_equal(
                entry["coefficients"], target["coefficients"][target["parity"]::2]):
            raise ValueError(f"MATLAB request differs from archived polynomial: {ident}")
        x = check_grid(output["audit_x"], entry["audit_x"], "audit inputs")
        response = vector(output["response"], "audit response")
        if response.shape != x.shape:
            raise ValueError("MATLAB audit response shape mismatch")
        check_solver(output, request["criteria"])
        _, P = evaluate_qsp(phases, x)
        audit = metrics(P.real - response)
        grid = check_grid(output["validation_x"], entry["validation_x"], "validation inputs")
        if not np.array_equal(grid, validation_grid(target)):
            raise ValueError(f"MATLAB validation grid differs from archived target: {ident}")
        _, _, statistics = case_data(root, output)
        tolerance = case["acceptance"]["evaluator_tolerance"]
        checks = [audit["max_abs"], statistics["unitarity_max"]] + [
            statistics[name]["max_abs"] for name in ("evaluator_agreement", "synthesis", "local_synthesis")]
        if max(checks) > tolerance:
            raise ValueError(f"MATLAB/local response mismatch: {ident}")
        if statistics["baseline_application"]["max_abs"] > target["baseline_accuracy_goal"]:
            raise ValueError(f"MATLAB application target accuracy failed: {ident}")
        results.append(dict(case_id=ident, degree=target["degree"], family=target["family"],
                            phase_count=int(phases.size), validation_points=int(grid.size),
                            solver_value=float(output["solver_value"]), iterations=int(output["iterations"]),
                            audit_evaluator_agreement=audit, **statistics))
    stage1 = json.loads((root / "results/stage1/solver_comparisons.json").read_text())
    originals = {e["name"]: e for e in stage1["examples"]}
    conventions = {e["case_id"]: e for e in request["convention_cases"]}
    convention_results = []
    for output in coverage(report["convention_cases"], conventions, "convention cases"):
        entry = conventions[output["case_id"]]
        example = originals[entry["name"]]
        if output["targetPre"] is not entry["targetPre"] or output["typePhi"] != "full":
            raise ValueError("MATLAB Stage 1 readout convention mismatch")
        phases = vector(output["full_phases"], "Stage 1 phases")
        if phases.size != example["degree"] + 1:
            raise ValueError("MATLAB Stage 1 phase count mismatch")
        x = check_grid(output["x"], entry["x"], "Stage 1 inputs")
        native = vector(output["response"], "Stage 1 response")
        if native.shape != x.shape:
            raise ValueError("MATLAB Stage 1 response shape mismatch")
        check_solver(output, request["criteria"])
        _, P = evaluate_qsp(phases, x)
        local = P.real if entry["targetPre"] else P.imag
        polynomial = np.polynomial.chebyshev.chebval(x, example["chebyshev_coefficients"])
        agreement, synthesis = metrics(local - native), metrics(native - polynomial)
        if max(agreement["max_abs"], synthesis["max_abs"]) > 1e-10:
            raise ValueError(f"MATLAB Stage 1 convention failed: {entry['case_id']}")
        convention_results.append(dict(case_id=entry["case_id"],degree=example["degree"],
                                       evaluator_agreement=agreement,synthesis=synthesis,
                                       solver_value=float(output["solver_value"])))
    return dict(passed=True,executed=True,runtime="MATLAB",runtime_version=report["runtime_version"],
                source_revision=report["source_revision"],input_sha256=input_sha256,
                report_sha256=hashlib.sha256(json.dumps(report,sort_keys=True,allow_nan=False).encode()).hexdigest(),
                cases=results,convention_cases=convention_results)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report",nargs="?",type=Path,default=root/"results/stage2/matlab_output.json")
    args = parser.parse_args()
    result = verify_matlab(root,json.loads(args.report.read_text()))
    (root/"results/stage2/matlab_verification.json").write_text(
        json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result,indent=2))
