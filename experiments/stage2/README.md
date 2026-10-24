# Regenerate and verify the Stage 2 library

Use Python 3.11 and the pinned environment already used for Stage 1B. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r experiments/stage1/requirements.lock.txt -e ".[validation]"
.\.venv\Scripts\python.exe -m unittest discover -s tests/stage1 -v
.\.venv\Scripts\python.exe -m unittest discover -s tests/stage2 -v
.\.venv\Scripts\python.exe experiments/stage2/build_library.py
.\.venv\Scripts\python.exe experiments/stage2/verify_library.py
```

The generator uses [config.json](config.json), writes only the Stage 2 library/results/figures and their documented indexes, and refreshes the Stage 2 result block in the project README. No phase quantization is performed.

To reuse unchanged, hash-checked cases while regenerating figures and summaries:

```powershell
.\.venv\Scripts\python.exe experiments/stage2/build_library.py --resume
```

The reuse fingerprint includes the target configuration, solver options, package versions, and scientific source-file hashes. Cached curve/audit/log hashes must match; the final verifier reconstructs all saved phases again. A full regeneration may change recorded timings or last-bit numerical results on another numerical environment; byte-identical fresh outputs are not promised. Existing archived files must pass their saved hashes and reconstruction checks when verified. Generated text artifacts have LF line endings so Git conversion does not invalidate their hashes.

## Browse the results

- [Measured README summary](../../README.md#stage-2-measured-baseline-results).
- [All phase archives and individual reference graphs](../../data/phases/README.md).
- [One-row-per-case results CSV](../../results/stage2/library_summary.csv).
- [Manifest](../../results/stage2/summary.json) and [archive-reload verification](../../results/stage2/verification.json).
- [Methods, grids, error definitions, and acceptance criteria](../../src/qsp_finite_precision/stage2/README.md).

Every successful archive contains all unrounded full phases, target parameters, achieved degree, coefficients, solver/version/options, convergence, and residuals. Per-case CSVs retain the reconstructed curves and the application-domain mask. Figures reverse the target scale for display only; native scaled residuals are retained separately. Sign accuracy is measured against 0.9 times sign(x) outside the recorded gap, even though the polynomial construction uses an erf surrogate.

## Original MATLAB cross-check — pending

No MATLAB runtime was available during the current run. The files below are a prepared cross-check workflow, not evidence that MATLAB was executed. The Python `qsppack` results do not replace this check.

1. Obtain the original [QSPPACK repository](https://github.com/qsppack/QSPPACK) in a separate local folder and check out revision `7bc7b7622e05039e4c2cdda7d5739e99c3752be6`.
2. In MATLAB, with this project's folder as the current directory, run:

```matlab
addpath('experiments/stage2');
crosscheck_matlab('C:/path/to/original/QSPPACK');
```

The argument is the user's actual original-QSPPACK checkout path. The runner uses `results/stage2/matlab_input.json` and writes `results/stage2/matlab_output.json`. It checks the normalized SHA256 hashes of six entry/evaluation/Newton functions against the pinned [source hashes](matlab_source_hashes.json). Those hashes identify the checked functions; use the pinned checkout for the full dependency tree as well.

3. Verify the actual report with Python:

```powershell
.\.venv\Scripts\python.exe experiments/stage2/verify_matlab.py
```

The verifier requires a report identifying MATLAB and its version, the pinned source hashes, every requested case, finite full phases, a successful solver residual, matching audit inputs, and agreement between the original MATLAB response and our evaluator. It also reconstructs the MATLAB phases on the full validation grid. Successful verification writes `results/stage2/matlab_verification.json`.

The current library manifest and READMEs intentionally keep this check pending. Once a genuine MATLAB report has passed verification, review it and update those status records explicitly; a prepared runner or a Python-generated substitute cannot mark original MATLAB execution complete. Professor Hen's checkpoint still comes before Stage 3.
