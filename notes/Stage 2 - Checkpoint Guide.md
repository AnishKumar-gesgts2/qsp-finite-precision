# Stage 2 checkpoint guide

**Technical status:** the Python baseline library and clean-clone regeneration are verified. **Original MATLAB QSPPACK execution remains pending access to a signed-in MATLAB session. Professor Hen's review remains pending.** Stage 3 has not started.

Authority: Professor Hen's [original assignment](../references/QSP_project.docx), Stage 2 and the checkpoint immediately afterward. This page collects the review evidence; it does not replace the assignment or record approval.

## Review the three required items

| Checkpoint item | Evidence to open | Current boundary |
| --- | --- | --- |
| Exact QSP convention and package mapping | [Convention note](Conventions.md) | Written factor order, radians, phase counts, target readout, reduced-phase expansion, and endpoint offsets are explicit. MATLAB mapping is source-inspected; its runtime check is still pending. |
| Reproduce each solver's own output | [Stage 1B reference graphs and error tables](../experiments/stage1/README.md), [Stage 2 manifest](../results/stage2/summary.json) | pyqsp and Python QSPPACK checks pass. Python QSPPACK is supplementary. [The original MATLAB workflow and ZIP](../experiments/stage2/README.md#original-matlab-cross-check--pending) are prepared, not executed. |
| Regenerable core phase library, residuals, and phase plots | [All 21 case graphs, phase files, and CSVs](../data/phases/README.md), [methods](../src/qsp_finite_precision/stage2/README.md), [fresh rebuild comparison](../results/stage2/rebuild_comparison.json) | Both core families cover degrees about 10–500. A separate clone and new pinned environment regenerated every case and its graph. The original MATLAB run must still pass before all technical prerequisites are complete. |

## What the library establishes

There are **21 cases and 3,421 unquantized full phases**: seven cosine, seven sine, and seven sign cases. Cosine degrees span 10–500; sine and sign degrees span 11–499 to preserve odd parity. Every archive records its target and parameters, Chebyshev coefficients, phase convention, solver/version/options, convergence, and separate residuals.

| Family | Worst reconstructed-to-target error on its application domain | Worst reconstructed-to-polynomial error on the full interval |
| --- | ---: | ---: |
| Cosine | 5.000e-8 | 3.915e-14 |
| Sine | 5.000e-8 | 5.007e-14 |
| Sign | 4.784e-3 | 4.019e-14 |

These are sampled maximum absolute errors in native circuit units. Cosine and sine use amplitude scale 0.5. The sign reference is 0.9 times sign(x), evaluated outside each recorded gap; an erf surrogate constructs the polynomial. The sign gap narrows as degree increases, so degree and difficulty vary together. These results do not measure the effect of changing degree at fixed difficulty.

The largest independently recomputed pyqsp coefficient L1 residual is **1.411e-14**, below the chosen 1e-12 criterion. All package-response audits and saved-phase reconstruction checks pass. Finite grids and binary64 arithmetic support numerical validation, not a proof over every input or a measured accuracy floor. Target accuracy goals (1e-6 for cosine/sine and 1e-2 for sign) and the numerical boundedness procedure are our [documented implementation choices](../src/qsp_finite_precision/stage2/README.md), not professor-specified tolerances.

At the recorded neighboring-phase threshold of 1e-8 radians, cosine lists show no nearly equal adjacent pairs. Odd sine/sign lists show only the forced identical central pair (longest run two). This is a descriptive observation; rounding correlations and noise-shaping benefits have not yet been measured.

## Fresh regeneration evidence

The [machine-readable comparison](../results/stage2/rebuild_comparison.json) records the exact tested revision, package versions, scientific source hashes, case coverage, and maximum differences in both solvers' phase lists and saved curves. [The captured validation logs](../results/stage2/rebuild-validation/) document the dependency check, both test suites, 104 identity checks, Stage 1 comparison generation, Stage 2 generation without a cache, and archive reload. The rebuild uses a new environment on the same computer; it does not establish cross-platform reproducibility.

**Observed maximum differences: 0.0 radians for both solvers' phase lists and 0.0 for all compared response curves, across all 21 cases.** This is numerical equality in this pinned run, not a promise of byte-identical fresh outputs on other environments.

The first clean-check attempt exposed Windows source-file line-ending conversion, which changed source hashes. The repository now fixes Python/MATLAB sources and hashed output text to LF. The recorded successful rebuild follows that correction. Timings and generated image bytes are not required to be identical; the numerical comparison and archive checks are explicit.

To repeat the check, follow [the regeneration instructions](../experiments/stage2/README.md#clean-clone-regeneration-check). The complete archived phase lists remain the unrounded numerical baseline for later storage-error experiments.

## Finish the original MATLAB check

1. Obtain a MATLAB session, locally or through MATLAB Online. Current access is waiting on user sign-in.
2. Extract [the prepared bundle](../results/stage2/qsp-stage2-matlab.zip) and run `run_stage2` in MATLAB. The bundle includes the original source, license, and all numerical inputs; no private GitHub authentication is needed inside MATLAB.
3. Save its actual `matlab_output.json` into `results/stage2/`, then run `experiments/stage2/verify_matlab.py` with the project's Python environment.
4. Inspect the resulting verification and update the manifest, READMEs, alignment note, and roadmap using the measured result. Preserve the actual report and any new comparison figures. Do not mark this check complete from the prepared ZIP, Python results, or an Octave run.

## Items for Professor Hen's review

- Confirm the convention/readout mapping and the actual solver-output comparisons once MATLAB has run.
- Confirm that the chosen evolution times, sign gaps, amplitude scales, and baseline-error goals provide an appropriate core library for the storage-error study.
- Review the phase-index plots and the precise threshold used for the current plateau observations.
- Review regeneration evidence and decide whether the library is sufficient to proceed to Stage 3.

Approval must come from the professor's review. It has not been inferred from passing tests, the existence of this guide, or completion of implementation work.
