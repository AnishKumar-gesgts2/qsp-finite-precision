# Stage 2 delivery note

Date: 2026-10-24

## Question

Do the core full-precision phase lists reproduce their target polynomials, have the required metadata and interpretive figures, and regenerate from the repository? Can the original MATLAB QSPPACK implementation be executed for the remaining cross-check?

## Configuration

Authority: Professor Hen's [original Stage 2 requirements and supervisor checkpoint](../references/QSP_project.docx), reread before this closeout. The library uses the [recorded configuration](../experiments/stage2/config.json), pyqsp 0.2.0, supplementary Python QSPPACK 0.4.0, NumPy 2.4.6, and SciPy 1.17.1. The [manifest](../results/stage2/summary.json) retains scientific source hashes, exact settings, scales, domains, and versions.

- Seven even cosine degrees from 10 to 500, and seven odd sine/sign degrees from 11 to 499: 21 cases and 3,421 full phases.
- Hamiltonian targets use scale 0.5; evolution time varies with degree. Sign uses maximum 0.9, an erf polynomial construction, and explicit gap-excluded application domains.
- Newton coefficient stopping criterion: 1e-12; evaluator/synthesis acceptance: 1e-10. Target-accuracy goals: 1e-6 for cosine/sine and 1e-2 for sign. These are documented implementation choices.
- All phase values are unquantized binary64 round-trip values. No Stage 3 rounding experiment was performed.

## Results and artifacts

| Result | Recorded outcome | Evidence |
| --- | --- | --- |
| Python core library | 21/21 cases verified; 3,421 full phases | [Phase files, per-case graphs, and CSVs](../data/phases/README.md) |
| Largest synthesis residual | 5.007e-14 | [Summary CSV](../results/stage2/library_summary.csv) |
| Largest returned-phase coefficient L1 residual | 1.411e-14 | [Manifest](../results/stage2/summary.json) |
| Worst cosine/sine target error | Approximately 5.000e-8 in native scaled units | [Overview](../figures/stage2/overview.png) |
| Worst sign application error | 4.784e-3 against the actual sign target outside its recorded gap | [Summary CSV](../results/stage2/library_summary.csv) |
| Clean regeneration | All 21 cases reproduced with zero phase/curve difference in the recorded separate clone and pinned environment | [Rebuild comparison](../results/stage2/rebuild_comparison.json) |
| Stage 1 mathematical diagnostics | 104/104 passing sampled checks through degree 500 | [CSV](../results/stage1/mathematical_checks.csv), [new diagnostic graph](../figures/stage1/mathematical_checks.png) |
| Original MATLAB QSPPACK | **Unable to complete; no MATLAB code ran** | [Execution-attempt record](../results/stage2/matlab_execution_status.json) |

Every Python library case already has the original target, polynomial, reconstructed response, full phase-index plot, separate pointwise errors, and max/RMSE statistics. The Stage 1B examples have the same reference-graph treatment. The new identity figure makes the existing 104-check CSV interpretable by degree; it does not create a new mathematical guarantee.

The prepared MATLAB runner now covers all 21 core cases on both audit and full validation grids, plus eight Stage 1 full-phase checks (four examples, real and imaginary readouts). It verifies runtime/source/input identity and saves completed cases for resumption. The prepared report verifier rejects missing/duplicate cases, changed inputs/grids, failed convergence, wrong readouts, invalid phases, and inconsistent native/local responses. Its Python tests use explicitly labeled temporary synthetic fixtures; these tests are not MATLAB execution evidence.

The prepared publisher will create native-MATLAB CSVs, dedicated full-phase JSONs, 21 core comparison graphs, four Stage 1 graphs, an overview, a summary CSV, and measured README/status updates **after a genuine report passes verification**. Those original-MATLAB numerical outputs do not currently exist. [Run and publication instructions](../experiments/stage2/README.md).

The current unit/integration suites pass **22 tests** (12 Stage 1 and 10 Stage 2). A separate [publication-code smoke test](../results/stage2/publication_code_test.json) exercised 21 case archives, CSVs, and 26 generated comparison PNGs in a temporary directory using explicitly synthetic Python fixtures. Those temporary outputs were removed, and the real README/library were unchanged. This validates reporting software behavior; it supplies no original-MATLAB numerical evidence. The [artifact audit](../results/stage2/artifact_audit.json) checks the actual saved library, image integrity, source/artifact hashes, and local documentation links.

## Interpretation and error budget

Stage 2 establishes an unrounded numerical baseline. Distinguish the desired function $f$, supplied polynomial $p$, and phase response $r_\Phi$. Function-approximation and synthesis residuals are recorded separately. Later storage error compares the same case before and after rounding:

$$
E_{\mathrm{storage}}(x)=|r_{\widehat\Phi}(x)-r_\Phi(x)|.
$$

The existing function-approximation error can exceed this additional change without preventing its direct measurement. Numerical **evaluation** error must be much smaller than the smallest change we claim to resolve. If each evaluated response has absolute numerical error at most $\varepsilon$, the difference has error at most $2\varepsilon$. This is a conditional error bound, not a measured or certified value of $\varepsilon$ for our implementation.

Package agreement and small synthesis residuals alone do not certify that numerical error floor. Professor Hen's Stage 4 high-degree spot-checks with at least 30-digit mpmath remain required future work. No detectable-error threshold, rounding advantage, coherent accumulation, or scaling exponent is inferred from Stage 2.

At the recorded 1e-8-radian adjacency threshold, cosine lists have no qualifying neighboring pair; odd-degree sine/sign lists contain only the forced identical center pair. Target difficulty varies with degree, so later scaling interpretations must account for that covariation.

## MATLAB limitation and closeout decision

The free account was signed in, but MATLAB Online repeatedly failed to establish a usable workspace connection. Fresh sessions/pages, a service-status check, and the documented session-cache inspection did not resolve it. No session files were removed. The user manually retried and reported enabling browser upload access; reconnection and upload still failed. The [machine-readable record](../results/stage2/matlab_execution_status.json) distinguishes these attempts from numerical testing.

Anish explicitly authorized recording MATLAB as unable to complete and proceeding with cleanup. The roadmap marks **Python deliverables complete** and preserves the unavailable original-MATLAB check separately. The manifest keeps `stage2_complete: false`, `technical_complete: false`, and `ready_for_stage3: false`; it does not infer professor approval or silently replace original MATLAB with the Python port.

## Next step

Review the [checkpoint evidence and limitation](Stage%202%20-%20Checkpoint%20Guide.md) with Professor Hen. A working MATLAB session can later run the pinned bundle and publish its actual results. Begin Stage 3 only after the required supervisor checkpoint. Learning-mastery records remain unchanged.
