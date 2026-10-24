# Alignment with Professor Hen's original assignment

Source reviewed: **2026-10-23**. Authority: [the original project description](../references/QSP_project.docx), authored by Professor Itay Hen on September 26, 2026; [PDF export](../references/QSP_project.pdf). Section names below refer to that document. This note is a navigation and status aid, not a replacement specification.

Before each new stage and completion claim, reread the corresponding source section and its output requirement. When package behavior or an implementation convenience suggests a change, keep the source requirement visible and label the change explicitly.

## Core objective

Measure finite-precision **phase-storage error on phase lists produced by production solvers for real target functions**. Determine whether actual rounding errors add coherently or partly cancel, and how the required bit precision and noise-shaping benefits vary with degree. The original description explicitly separates storage error from solver and gate-synthesis error. Evaluator validation is preparation for that question, not the research result itself.

## Required stages and current alignment

| Original section | Required work / output | Current status and boundary |
| --- | --- | --- |
| Stage 1: forward QSP code and convention check | Vectorized forward module returning full unitaries and upper-left amplitudes; reproduce two or three built-in pyqsp curves; test the random-phase endpoint identity, boundedness, and parity; tested module and concise convention note mapping pyqsp and QSPPACK. | Implemented and checked for pinned Python packages. Three built-in examples plus a supplementary linear diagnostic, mathematical checks, phase/readout adapters, reference graphs, and convention note are saved locally. Original MATLAB mapping source-inspected; MATLAB execution is not claimed. Our 1A/1B labels subdivide this original stage. |
| Stage 2: a library of real phase lists | Use pyqsp `sym_qsp` by default and QSPPACK as a cross-check. Both core families, approximately logarithmic degrees from about 10 to 500. Full-double-precision phase files with target, parameters, degree, solver and residual; representative phase-index plots and observations about plateaus. | Python workflow implemented: 21 cases, 3,421 phases, both core families, all cases reloaded and verified, with graphs/CSVs/metadata. Low-degree Stage 1 fixtures remain separate. Python QSPPACK checks are supplementary; the prepared original MATLAB numerical cross-check and supervisor checkpoint remain pending. |
| Checkpoint after Stage 2 | Supervisor review of the convention note, reproduction of each solver's own output, and the core library with residuals and phase plots. All must regenerate cleanly before moving on. | [Evidence guide](Stage%202%20-%20Checkpoint%20Guide.md) prepared. Separate-clone regeneration and numerical comparison pass for all 21 Python cases; original MATLAB execution awaits sign-in and supervisor review remains pending. Implementation completion alone is not approval. |
| Stage 3: quantize | Binary words spanning one full turn, at 12, 16, 20, 24, 28, and 32 bits. Direct nearest rounding, nearest plus one-phase sum correction, and first-order sigma-delta. Record each phase-error sequence and save rounded files. | Pending; begins after the checkpoint. Quantization details and tie/wrap conventions must be recorded. |
| Stage 4: measure the realized error | At least ten times the degree plus one Chebyshev-grid samples per case. Separate maximum full-unitary, complex matrix-element, and selected readout errors, globally and on the application domain. Rounding-error autocorrelation; sensitivity profiles and their total variation for a subset. High-degree spot-checks with at least 30-digit mpmath. One results CSV covering every case. | Pending. Stage 1's 1,025-point validation grid is not the eventual degree-dependent Stage 4 grid. |
| Stage 5: analysis | Degree-scaling fits; correlation/plateau predictors; endpoint versus interior maxima; equal-grid scheme comparisons and sensitivity-variation connection; bits required for accuracies 1e-4, 1e-6, and 1e-8; the degree where 21-bit phases cease meeting 1e-4. One or two figures for each of the five questions. | Pending. Novelty and publishability are decided after measurements, not assumed. |
| Deliverables / what counts as success | Repository instructions regenerating every figure from scratch, phase library, results CSV, and an 8–12 page report. All five stages for both core families, with a reproducible answer to coherent versus cancelling rounding. | Core assignment remains intact. Documentation and validation additions support these deliverables. |

## Core target families

1. Hamiltonian simulation: cosine and sine via Jacobi–Anger approximation, varying evolution time.
2. Sign or step, scaled to a maximum of 0.9, varying sharpness / inverse gap.

Targets must respect the assignment's magnitude bounds on their approximation domains. Stage 1's smooth erf test is a built-in validation example; it does not decide the Stage 2 sign/step approximation domain or establish its error specification.

## Extensions explicitly deferred by the source

- Scaled inversion and eigenstate/bandpass filters.
- Degrees up to 2,000.
- Decimal grids and dithered rounding.
- Symmetry-preserving noise shaping and possible higher-order refinements (stretch goal).

Keep these separate from the core when proposing ideas or allocating time. The original timeline assumes roughly ten hours per week over fifteen weeks; it is a planning assumption, not a guarantee that a stage takes a fixed number of hours.

## Supplementary choices made so far

- Isolated, pinned Python environment and source hashes for reproducibility.
- Python QSPPACK compatibility checks in addition to the original MATLAB source review.
- A simple linear diagnostic, per-example phase graphs, RMSE alongside maximum errors, and reversal of generator scaling for display in original-function units.

These additions do not replace source requirements. Native scaled residuals are retained, and no phase rounding is performed in Stage 1.
