# Stage 2: full-precision core phase library

The Python workflow constructs and saves realistic solver-generated phase lists for both core application families. These are unrounded baselines for later storage-error measurements. The original MATLAB QSPPACK numerical cross-check and Professor Hen's supervisor checkpoint remain pending; no Stage 3 quantization has started.

[Measured summary in the project README](../../../README.md#stage-2-measured-baseline-results) · [Browse all cases and graphs](../../../data/phases/README.md) · [Summary CSV](../../../results/stage2/library_summary.csv) · [Manifest](../../../results/stage2/summary.json) · [Reload verification](../../../results/stage2/verification.json)

The authoritative requirements are “Stage 2: a library of real phase lists” and “Checkpoint” in [Professor Hen's original description](../../../references/QSP_project.docx). The target parameters and numerical acceptance thresholds below are implementation choices that make those requirements reproducible; they are not additional instructions from the professor.

## Inputs, outputs, and workflow

```mermaid
flowchart TD
    C["Configuration<br/>family, degrees, approximation settings"] --> T["Build target and Chebyshev coefficients<br/>Record scale, parity, and application domain"]
    T --> B["Check polynomial boundedness<br/>Theta samples + between-node allowance"]
    B --> S["Production pyqsp symmetric Newton solver<br/>Save full and reduced phases"]
    S --> E["Stage 1 evaluator<br/>Full U and complex P on validation grid"]
    E --> M["Separate approximation, synthesis,<br/>baseline target error, and package agreement"]
    M --> Q["Supplementary Python QSPPACK check<br/>Real-part readout, full phases"]
    Q --> A{"All acceptance checks pass?"}
    A -- No --> F["Record failure in manifest<br/>No successful phase archive for this case"]
    A -- Yes --> J["Archive binary64 phase JSON + curves CSV<br/>Record hashes and solver metadata"]
    J --> V["Reload archives and reconstruct<br/>Verify curves, domains, metrics, and hashes"]
    V --> R["Per-case reference graphs<br/>Library index + measurable README summary"]
    R --> X["Pending: original MATLAB QSPPACK execution<br/>Then required review with Professor Hen"]
```

Implementation files:

- `targets.py`: core target definitions, Jacobi–Anger / erf polynomial construction, parity, domain, and boundedness estimates.
- `library.py`: production-solver calls, independent returned-phase checks, full-precision archives, residuals, and supplementary Python QSPPACK evaluation.
- [build_library.py](../../../experiments/stage2/build_library.py): regeneration, per-case figures, tables, manifest, and summary.
- [verify_library.py](../../../experiments/stage2/verify_library.py): re-evaluate the saved phases without repeating phase synthesis.

## Chosen core cases

The [configuration](../../../experiments/stage2/config.json) requests:

| Waveform | Achieved degrees requested | Parameterization | Desired target / application domain |
| --- | --- | --- | --- |
| Cosine | 10, 20, 40, 80, 160, 320, 500 | Choose evolution time so the numerically summed omitted Jacobi–Anger coefficient tail is 1e-7 | $0.5\cos(\tau x)$ on $[-1,1]$ |
| Sine | 11, 21, 41, 81, 161, 321, 499 | Same omitted-tail target, with odd degrees | $0.5\sin(\tau x)$ on $[-1,1]$ |
| Sign | 11, 21, 41, 81, 161, 321, 499 | $\delta=\max(3,d/6)$; gap $\gamma=2/\delta$ | $0.9\operatorname{sign}(x)$ on $[-1,-\gamma]\cup[\gamma,1]$ |

Cosine and sine are the two waveforms in the Hamiltonian-simulation family; sign is the second required family. Degree parity is preserved, so the odd sequences end near 500 at 499. Leading coefficients are retained rather than padding lower-degree examples with zeros. Actual degrees, phase counts, and target parameters are stored per case.

For Hamiltonian cases the coefficients come directly from Bessel-function Jacobi–Anger expansions. The omitted-tail sum is a numerical estimate over 512 omitted active-parity coefficients, not a rigorous infinite-tail certificate. Actual target errors are checked independently on the validation grid. The 0.5 scale keeps the target comfortably inside the admissible range.

For sign cases the construction starts with a Chebyshev expansion of the smooth surrogate $\operatorname{erf}(\delta x)$. A DCT-II on first-kind Chebyshev nodes gives coefficients; opposite-parity coefficients are set to zero, and the degree-$d$ truncation is scaled to stay below 0.9 using the recorded global-bound estimate. Coefficients are compared with those from twice as many samples to expose finite-sampling sensitivity.

**The sign target remains $0.9\operatorname{sign}(x)$.** Its approximation and baseline errors are measured against that discontinuous target on the gap-excluded domain, not against the erf surrogate. Gap edges are included exactly in the evaluation grid. The native target scale is 0.9; the polynomial-construction scale can be slightly smaller and is recorded separately.

Target difficulty changes with degree: evolution time increases and the sign gap shrinks. These are realistic family sweeps at the stated construction settings. Future degree-scaling interpretations must account for that parameter covariation; the library does not establish an isolated causal degree effect.

## Boundedness assessment

For a real Chebyshev polynomial, set $q(\theta)=p(\cos\theta)$. Its second derivative obeys

$$
|q''(\theta)|\le M_2=\sum_{k=0}^{d}k^2|c_k|.
$$

With an endpoint-including uniform theta grid of spacing $\Delta\theta$, an interior maximum of $|q|$ is stationary and lies within $\Delta\theta/2$ of a sample. Taylor's bound then gives

$$
\max|p|\le \max_{\text{samples}}|p|+\frac{M_2\Delta\theta^2}{8}
$$

in exact arithmetic. The code uses at least 8,193 points (or $64d+1$), adds a floating-point margin, and records every term. This is stronger than a sampled maximum alone, but it is a **numerical upper estimate, not a directed-rounding interval certificate**. Sign scaling includes a small additional safety margin. Cosine/sine estimates must be below one; sign estimates must be at most 0.9 within the stated numerical allowance.

## Residuals, grids, and pass criteria

Let $f$ include the desired amplitude scale, $p$ be the supplied polynomial, and $r=\operatorname{Im}P$ the pyqsp phase response. Native circuit-unit metrics are:

- Approximation: maximum and sample-weighted RMSE of $p-f$ on the application domain.
- Synthesis: maximum and sample-weighted RMSE of $r-p$ on the full signal interval.
- Baseline: maximum and sample-weighted RMSE of $r-f$ on the application domain.
- Package agreement: complex $P$ from our evaluator versus pyqsp's own response, with identical phases and audit inputs.
- Supplementary Python QSPPACK: real-part response for its own full phases versus its own `get_entry`, plus synthesis / target residuals.
- Structural checks: full phase count, unitarity, polynomial boundedness, and descriptive phase symmetry/adjacency measurements.

Each validation grid has at least 2,049 Chebyshev-Lobatto samples or $10d+1$, whichever is larger, plus uniform interior midpoints and exact gap edges. The separate package audit grid includes Chebyshev points, interior points, endpoints, zero, and sign-gap edges. The full validation-grid curves and audit-grid responses are archived separately. All reported maxima are sampled maxima. RMSE gives equal weight to the actual samples and is not a uniform-domain integral norm.

Acceptance choices:

| Check | Acceptance |
| --- | --- |
| pyqsp stopping residual and independently recomputed returned-phase coefficient L1 residual | Both below 1e-12 |
| Response-to-polynomial error, package-evaluator agreement, and unitarity residual | At most 1e-10 |
| Cosine/sine baseline target error | At most 1e-6 |
| Sign baseline target error on the declared application domain | At most 1e-2 |
| Python QSPPACK | Converged, and passes the same response checks |

The installed pyqsp high-level symmetric wrapper omits convergence metadata. We call its documented `sym_qsp_opt.newton_solver` directly, using the same production algorithm, and record both its pre-update stopping residual and a fresh residual from the returned phases. A failed case is recorded in the manifest and is not saved as a successful phase archive.

These tolerances are regression and library-acceptance settings, not measured accuracy floors. Floating-point evaluation contributes to the measured synthesis residual. No rounding-error conclusion follows from these baseline numbers.

## Saved data and figures

Each successful case has:

- `data/phases/stage2/<case>.json`: target, coefficients, all full/reduced phases, conventions, scales, domains, versions/options, convergence, metrics, and artifact hashes. Python's full float representation preserves binary64 round-trip values. No phase wrapping or quantization is applied.
- `results/stage2/<case>_response.csv`: validation inputs, scaled target, polynomial, reconstructed real/imaginary amplitude, application mask, Python QSPPACK readout, and separate errors. Values inside a sign gap are retained for diagnostics but excluded from application-error metrics.
- `results/stage2/<case>_audit.csv`: each package's own response versus the corresponding local response on the audit grid.
- `results/stage2/<case>_solver.log`: solver iteration output.
- `figures/stage2/<case>.png`: original function / reconstruction, full phase sequence, separated errors, and max/RMSE table. Curves are displayed in original-function units by dividing by the target scale; metric tables retain native circuit units.

The overview plots residuals, target parameters, and median neighboring phase changes. High-frequency Hamiltonian response panels use a central zoom with a full-interval inset; the errors and archived curves still cover the full validation grid. “Nearly equal adjacent” in the archive means an absolute neighboring phase difference at most 1e-8 radians; its threshold and longest run are recorded. At that particular threshold, the current cosine lists have no such adjacent pairs; the odd-degree sine/sign lists have only the forced duplicated center pair from symmetric expansion (longest run two). This does not establish extended phase plateaus or rounding correlations. Other thresholds could give different descriptive counts.

## Original MATLAB QSPPACK and completion boundary

The original MATLAB runtime is unavailable locally. [The supplied runner](../../../experiments/stage2/crosscheck_matlab.m) consumes the exported coefficients and audit inputs, checks six original MATLAB source-function hashes at the pinned revision, and saves the phases and native MATLAB responses. [The verifier](../../../experiments/stage2/verify_matlab.py) checks the returned source identity, coverage, convergence, and reconstructed response. The runner itself has not been executed here. Python QSPPACK has shared algorithmic lineage and is supplementary; it does not establish original MATLAB execution.

The manifest deliberately retains `stage2_complete: false`, pending original MATLAB comparison and the professor's required checkpoint. Before Stage 3, review the Stage 1 convention note, reproduced solver outputs, and this regenerable library with Professor Hen. A successful Python run does not mark that review complete.

## Sources

- [Original assignment](../../../references/QSP_project.docx), Stage 2 and checkpoint.
- [pyqsp README](https://github.com/ichuang/pyqsp): symmetric readout and documented direct Newton interface; installed version 0.2.0 is used.
- [Original MATLAB QSPPACK](https://github.com/qsppack/QSPPACK/tree/7bc7b7622e05039e4c2cdda7d5739e99c3752be6) and [Python QSPPACK documentation](https://qsppack.readthedocs.io/en/latest/getting_started.html).
- [Concept guide](../../../notes/Stage%202%20-%20Phase%20Library%20Concept.md) and [convention note](../../../notes/Conventions.md).
