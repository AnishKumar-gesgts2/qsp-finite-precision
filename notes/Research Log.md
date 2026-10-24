# Research Log

Use [[templates/Experiment Note|Experiment Note]] to record a reproducible experiment, or add dated progress entries here.

## 2026-10-24 — Stage 2 delivery audit and original MATLAB limitation

- Reread the original Stage 1–2 requirements and checkpoint. Preserved the full core project, separate error definitions, and supervisor gate before Stage 3.
- Extended the original MATLAB runner to all 21 core validation grids and eight Stage 1 full-phase real/imaginary checks. Added per-case progress saves, resumable execution for identical input/source/runtime, and a runtime diary in the portable bundle.
- Added a stricter report verifier and prepared CSV/phase/figure publication step. Python tests exercise successful parsing of explicitly labeled temporary fixtures and rejection of changed grids, responses, phase counts, readouts, convergence, and coverage. These tests do not constitute original MATLAB execution.
- Free MATLAB Online repeatedly disconnected before code execution. Checked official recovery guidance and service status, retried fresh sessions, and inspected an initially empty session folder without deleting files. The user also manually retried and reported enabling browser upload access. Connection/upload problems persisted; [the attempt record](../results/stage2/matlab_execution_status.json) states `executed: false`.
- Anish authorized marking the original MATLAB cross-check unable to complete and proceeding with cleanup. No original-MATLAB numerical output, CSV, or graph is invented. The prepared tools remain available for a working runtime.
- Added a figure of the existing 104 Stage 1 identity checks, expanded the Stage 2 Mermaid workflow to include source/runtime checks, CSV/graph publication, failure/unavailable outcomes, regeneration, and the separate supervisor checkpoint. Added the [[Stage 2 - Delivery Note]] with the measured results, error-budget distinction, and follow-up.
- Python phase-library deliverables are complete; original MATLAB is explicitly unavailable, full technical Stage 2 completion remains false, and professor approval/Stage 3 remain pending. The recorded clean-clone zero-difference result is retained with its exact tested revision and environment scope.

## 2026-10-23 — Stage 1B package validation

- Created an isolated Python 3.11.9 validation environment and recorded its dependency lock. Used pyqsp 0.2.0, Python QSPPACK 0.4.0, NumPy 2.4.6, SciPy 1.17.1, and Matplotlib 3.11.2.
- Reproduced built-in cosine (degree 6), sine (degree 7), and smoothed-sign (degree 15) examples on 1,025 inputs each. The same full phase arrays gave zero sampled complex-amplitude and full-unitary difference between our evaluator and pyqsp. Largest response-to-target-polynomial residual: 1.78e-15.
- All 12 Python QSPPACK combinations (three examples, full/reduced, real/imaginary) converged and matched the local mapped response within 8.89e-16. These packages share algorithmic lineage; this is implementation/convention agreement, not independent mathematical proof.
- All 12 unit/integration tests passed with no skips. Re-ran all 104 mathematical identity checks through degree 500 in the expanded environment; all passed, with the same recorded largest discrepancies as before.
- Added explicit symmetric-phase expansion and QSPPACK adapters, measurement-basis checks, degree-zero endpoint-offset checks, [[Conventions]], [regeneration instructions](../experiments/stage1/README.md), and [response plots](../figures/stage1/solver_comparisons.png).
- Inspected original MATLAB QSPPACK source at commit `7bc7b7622e05039e4c2cdda7d5739e99c3752be6`. MATLAB was not available on the command path and was not executed. Keep its numerical cross-check in Stage 2; the Python implementation does not silently replace that deliverable.
- Stage 1's pinned Python validation is complete. Stage 2's core library and supervisor checkpoint remain pending. No phase rounding or finite-precision scaling claims were made. Learning/mastery checkboxes were not changed.

### Reference graphs and original-function errors

- Added a four-panel reference graph for each Stage 1B example: linear `0.5x`, cosine, sine, and smoothed sign `erf(3x)`. Each includes original-function and phase-reconstructed curves, the full phase sequence, separate error curves, and maximum/RMSE tables.
- Reversed generator scaling for display and original-function statistics only; retained native scaled circuit metrics separately. The figures separate function-to-polynomial approximation, phase reconstruction, and package-evaluator differences. RMSE uses equal weights on the sampled nonuniform grid.
- Embedded the graphs and automatically regenerated per-example tables in the [Stage 1B README](../experiments/stage1/README.md), linked from the main Stage 1 README. Added explicit original-function samples and pointwise errors to the CSV.
- The linear diagnostic extends the experiment to four examples and 16 Python QSPPACK full/reduced and real/imaginary comparisons. All passed on the same 1,025 inputs; the original three examples retained their earlier residuals. No additional learning-mastery claims were made.

## 2026-10-23 — Stage 2 Python baseline library

- Rechecked the original Stage 2 and checkpoint requirements before implementation. Anish explicitly authorized code, repository changes, explanatory graphs/data, and a measurable README summary.
- Generated 21 successful cases: seven cosine, seven sine, and seven sign cases, covering achieved degrees about 10–500 with parity respected. Saved 3,421 unrounded full phases, full/reduced representations, Chebyshev coefficients, target parameters/scales/domains, versions/options, convergence, residuals, and source/config hashes.
- Hamiltonian evolution time varies with degree to keep the numerically estimated omitted Jacobi–Anger coefficient tail at 1e-7; the targets are scaled by 0.5. Worst sampled target errors are approximately 5.00e-8. Sign targets are 0.9 times sign(x) outside the recorded gap, with an erf construction and numerical boundedness margin; worst sampled application error is 4.784e-3 against a chosen 1e-2 acceptance goal.
- Worst full-interval synthesis residual across the library is 5.007e-14; largest returned-phase coefficient L1 residual is 1.411e-14. Every case matches its own pyqsp response on the package audit grid, and supplementary Python QSPPACK comparisons pass. Shared algorithmic lineage remains explicit.
- Saved one reference graph per case, a library overview, phase-index plots, per-input curves/audits, and a one-row-per-case summary CSV. The main README reports counts, achieved degrees, native-unit errors, and pending checks. High-frequency response plots include a readable central zoom and full-interval inset.
- Reloaded all archives and reconstructed their saved curves, application masks, and metrics. Archive/artifact hashes and binary64 phase counts are verified. Generated text uses LF end-of-line rules to preserve hashes through Git checkouts.
- At the descriptive 1e-8-radian adjacency threshold, cosine lists have no qualifying neighboring pair; odd-degree lists contain only the required identical center pair (longest run two). These data do not establish long plateaus, coherent rounding, or a scaling exponent. Target parameters co-vary with degree, which must be considered in later interpretations.
- Twelve Stage 1 tests and nine Stage 2 tests pass. Tests cover parity, analytic target accuracy, true-sign application domains, between-node boundedness estimates, phase serialization/reconstruction, iteration-limit rejection, archive tampering, and rejection of non-MATLAB or mismatched-source reports.
- Original MATLAB is unavailable locally. Prepared a source-pinned MATLAB runner, full case inputs, normalized hashes of six original functions, and an output verifier. The runner is not executed; original MATLAB cross-check and Professor Hen's review remain pending. Stage 3 remains untouched, and the manifest explicitly does not mark Stage 2 complete.
