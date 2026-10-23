"""Check forward-QSP identities and save measured discrepancies.

Run from the repository root after installing the package:
    python experiments/stage1/check_identities.py
"""

import csv
from pathlib import Path

import numpy as np

from qsp_finite_precision.stage1 import evaluate_qsp


def main():
    seed = 20261022
    degrees = (0, 1, 2, 3, 10, 31, 100, 500)
    trials = 3
    # Chebyshev-Lobatto points include both endpoints and concentrate near them.
    x = np.cos(np.linspace(0, np.pi, 513))
    rng = np.random.default_rng(seed)
    # Conservative absolute smoke-test threshold for this degree range.
    # The measured residuals, not this threshold, describe observed accuracy.
    tolerance = 1e-10
    rows = []

    def record(degree, trial, check, discrepancy):
        rows.append({
            "degree": degree,
            "trial": trial,
            "check": check,
            "max_discrepancy": float(discrepancy),
            "tolerance": tolerance,
            "passed": bool(discrepancy <= tolerance),
            "seed": seed,
            "grid_points": x.size,
            "numpy_version": np.__version__,
        })

    for d in degrees:
        for trial in range(trials):
            phases = rng.uniform(-np.pi, np.pi, d + 1)
            U, P = evaluate_qsp(phases, x)

            residual = U.conj().swapaxes(-1, -2) @ U - np.eye(2)
            record(d, trial, "unitarity", np.linalg.norm(residual, ord=2, axis=(-2, -1)).max())

            expected_endpoint = np.diag(np.exp(1j * np.array([phases.sum(), -phases.sum()])))
            record(d, trial, "endpoint_sum", np.linalg.norm(U[0] - expected_endpoint, ord=2))

            record(d, trial, "boundedness_excess", max(0.0, float(np.abs(P).max() - 1)))

            _, P_negative = evaluate_qsp(phases, -x)
            record(d, trial, "parity", np.abs(P_negative - (-1)**d * P).max())

        _, P_zero = evaluate_qsp(np.zeros(d + 1), x)
        coefficients = np.zeros(d + 1)
        coefficients[d] = 1
        expected_chebyshev = np.polynomial.chebyshev.chebval(x, coefficients)
        record(d, "zero_phases", "chebyshev", np.abs(P_zero - expected_chebyshev).max())

    output = Path(__file__).resolve().parents[2] / "results/stage1/mathematical_checks.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    for check in dict.fromkeys(row["check"] for row in rows):
        worst = max(row["max_discrepancy"] for row in rows if row["check"] == check)
        print(f"{check}: largest discrepancy = {worst:.6e}")
    failures = [row for row in rows if not row["passed"]]
    print(f"{len(rows) - len(failures)}/{len(rows)} checks passed; output: {output}")
    if failures:
        raise SystemExit("Mathematical identity checks failed; inspect the CSV.")


if __name__ == "__main__":
    main()
