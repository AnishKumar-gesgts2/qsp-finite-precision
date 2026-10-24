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

## Clean-clone regeneration check

A separate clone and newly created Python environment regenerated Stage 1 and all 21 Stage 2 cases from scratch. Both test suites passed (12 Stage 1 tests and 9 Stage 2 tests), along with all 104 mathematical identity checks. The [rebuild comparison](../../results/stage2/rebuild_comparison.json) records source/version identity and differences between rebuilt phases and curves; [the checkpoint guide](../../notes/Stage%202%20-%20Checkpoint%20Guide.md) explains its scope.

Run the commands above in a separate clone **without `--resume`**, and also regenerate Stage 1 with its [documented commands](../stage1/README.md). Then compare that clone with this library:

```powershell
.\.venv\Scripts\python.exe experiments/stage2/compare_rebuild.py C:/path/to/regenerated-clone --output results/stage2/rebuild_comparison.json
```

The recorded comparison uses the same computer and pinned package versions. It is evidence of fresh regeneration, not cross-platform certification or a claim that timings and image bytes must match. Python and MATLAB source files, as well as hashed generated artifacts, use LF line endings through `.gitattributes`; this prevents Windows checkout conversion from changing their recorded source identity.

## Browse the results

- [Measured README summary](../../README.md#stage-2-measured-baseline-results).
- [All phase archives and individual reference graphs](../../data/phases/README.md).
- [One-row-per-case results CSV](../../results/stage2/library_summary.csv).
- [Manifest](../../results/stage2/summary.json) and [archive-reload verification](../../results/stage2/verification.json).
- [Methods, grids, error definitions, and acceptance criteria](../../src/qsp_finite_precision/stage2/README.md).

Every successful archive contains all unrounded full phases, target parameters, achieved degree, coefficients, solver/version/options, convergence, and residuals. Per-case CSVs retain the reconstructed curves and the application-domain mask. Figures reverse the target scale for display only; native scaled residuals are retained separately. Sign accuracy is measured against 0.9 times sign(x) outside the recorded gap, even though the polynomial construction uses an erf surrogate.

## Original MATLAB cross-check — pending

No MATLAB runtime was available during the current run. The files below are a prepared cross-check workflow, not evidence that MATLAB was executed. The Python `qsppack` results do not replace this check.

### Portable bundle, including MATLAB Online

[Download the prepared ZIP](../../results/stage2/qsp-stage2-matlab.zip). It contains the unmodified original QSPPACK source tree at the pinned revision, its license, all 21 inputs, the runner, and file hashes. Extract it in MATLAB or MATLAB Online, open the `qsp-stage2-matlab` folder, and run `run_stage2`. Save the resulting `matlab_output.json` in this repository's `results/stage2/` folder and run the verifier below. The ZIP is preparation, not a MATLAB result.

To regenerate the bundle from a local Git clone of original QSPPACK:

```powershell
.\.venv\Scripts\python.exe experiments/stage2/prepare_matlab.py C:/path/to/QSPPACK results/stage2/qsp-stage2-matlab.zip
```

The packager reads the pinned committed tree with Git, so uncommitted changes in the source clone are excluded. It checks all six pinned function hashes before packaging. The runner checks them again, rejects Octave rather than labeling it MATLAB, and records the exact input-file hash in its result. The verifier rejects a report from an older or altered request.

MATLAB Online requires a MathWorks account. [MathWorks documents free basic access](https://www.mathworks.com/products/matlab-online/matlab-online-versions.html); sign-in is still required. Account creation and login are not part of the numerical evidence.

### Existing local MATLAB installation

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
