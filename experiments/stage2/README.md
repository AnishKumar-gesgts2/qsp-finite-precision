# Regenerate and verify the Stage 2 library

Use Python 3.11 and the pinned environment already used for Stage 1B. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r experiments/stage1/requirements.lock.txt -e ".[validation]"
.\.venv\Scripts\python.exe -m unittest discover -s tests/stage1 -v
.\.venv\Scripts\python.exe -m unittest discover -s tests/stage2 -v
.\.venv\Scripts\python.exe experiments/stage2/build_library.py
.\.venv\Scripts\python.exe experiments/stage2/verify_library.py
.\.venv\Scripts\python.exe experiments/stage2/audit_repository.py
```

The generator uses [config.json](config.json), writes the Stage 2 library/results/figures and their documented indexes, and refreshes the Stage 2 result block in the project README. If a genuine MATLAB report exists, it also verifies/publishes the Stage 1 MATLAB cross-check data and figures. No phase quantization is performed.

To reuse unchanged, hash-checked cases while regenerating figures and summaries:

```powershell
.\.venv\Scripts\python.exe experiments/stage2/build_library.py --resume
```

The reuse fingerprint includes the target configuration, solver options, package versions, and scientific source-file hashes. Cached curve/audit/log hashes must match; the final verifier reconstructs all saved phases again. A full regeneration may change recorded timings or last-bit numerical results on another numerical environment; byte-identical fresh outputs are not promised. Existing archived files must pass their saved hashes and reconstruction checks when verified. Generated text artifacts have LF line endings so Git conversion does not invalidate their hashes.

## Clean-clone regeneration check

A separate clone and newly created Python environment regenerated Stage 1 and all 21 Stage 2 cases from scratch. Its test suites passed (12 Stage 1 tests and 9 Stage 2 tests), along with all 104 identity checks. The current suite adds one report-consistency test: 12 Stage 1 plus 10 Stage 2 tests, all passing. The [rebuild comparison](../../results/stage2/rebuild_comparison.json) records its tested revision, source/version identity, and phase/curve differences; [the checkpoint guide](../../notes/Stage%202%20-%20Checkpoint%20Guide.md) explains the scope.

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

## Original MATLAB cross-check — unable to complete

Original MATLAB execution was **unable to complete** because the free online workspace repeatedly disconnected before code ran. The user authorized documenting the limitation and proceeding with cleanup. [Execution-attempt record](../../results/stage2/matlab_execution_status.json). The files below remain a prepared workflow, not execution evidence. Python `qsppack` results do not silently replace original MATLAB.

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

The argument is the user's actual original-QSPPACK checkout path. The runner uses `results/stage2/matlab_input.json` and writes `results/stage2/matlab_output.json`. It checks the normalized SHA256 hashes of six entry/evaluation/Newton functions against the pinned [source hashes](matlab_source_hashes.json). Those hashes identify the checked functions; use the pinned checkout for the full dependency tree as well. It runs eight supplementary Stage 1 full-phase checks (four fixtures, real and imaginary readouts) and all 21 Stage 2 core cases. Each core result includes both the package-audit responses and MATLAB's own response on the complete validation grid. Completed cases are saved after each case and reused only for the same input/source/runtime on resumption.

3. Verify the actual report with Python:

```powershell
.\.venv\Scripts\python.exe experiments/stage2/verify_matlab.py
.\.venv\Scripts\python.exe experiments/stage2/publish_matlab.py
.\.venv\Scripts\python.exe experiments/stage2/audit_repository.py
```

The verifier requires a report identifying MATLAB and its version, the pinned source hashes, every requested case, finite full phases, a successful solver residual, matching audit inputs, and agreement between the original MATLAB response and our evaluator. It also reconstructs the MATLAB phases on the full validation grid. Successful verification writes `results/stage2/matlab_verification.json`.

The current library manifest and READMEs explicitly record this check as unable to complete. `publish_matlab.py` is the prepared publication step: it first verifies an actual report, then writes complete MATLAB curves/error columns to CSV, a summary CSV, dedicated phase JSONs, one four-panel graph per core case, an overview, and four Stage 1 graphs. It updates the generated main/index README summaries using measured results. Its source exists before execution; that does not imply those original-MATLAB numerical outputs exist.

After successful publication, `technical_complete` and `stage2_complete` mean the technical Stage 2 deliverables passed. `supervisor_checkpoint` remains pending and `ready_for_stage3` remains false. Supervisor approval is a separate event. The generator reruns this verification/publication when an actual `matlab_output.json` is present; a stale or inconsistent report fails instead of silently preserving a completion claim.

## Current online execution issue

On 2026-10-24, free MATLAB Online access was enabled and the account was signed in, but repeated launches failed before code execution with “Requested service is not found.” MathWorks' status page reported the service operational. [MathWorks' recovery guidance](https://www.mathworks.com/matlabcentral/answers/2035374-why-do-i-receive-the-matlab-session-you-are-trying-to-connect-to-is-not-responding-requested-servi) was checked; the account's `.session` folder was initially empty, and no session files were removed. Fresh sessions and a fresh landing page were tried. The user manually retried and reported enabling file-URL access, but workspace reconnection and the upload file chooser still failed. The user then authorized deferral. These are access failures, not numerical test results; the manifest records `unable_to_complete` and `executed: false`.

## Publication-code test without MATLAB

The report parser has positive/negative fixture tests in the Stage 2 suite. To exercise the full CSV/graph publication path without claiming MATLAB execution:

```powershell
.\.venv\Scripts\python.exe experiments/stage2/check_publication.py
```

This explicitly labeled test builds synthetic responses from Python data in a temporary directory, checks the publication pipeline there, and removes all fixture outputs. It never imports a simulated MATLAB report into the real library. Its separate QA record is `results/stage2/publication_code_test.json`; this is software-test evidence, not original-MATLAB numerical evidence. A genuine MATLAB run remains required to resolve the unavailable cross-check.
