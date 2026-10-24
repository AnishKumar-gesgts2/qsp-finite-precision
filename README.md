# Finite-Precision Phases in Quantum Signal Processing

**Anish Kumar · Professor Itay Hen**

The [original project description](references/QSP_project.docx) is the authoritative assignment. Check its stage requirements before new work; [Assignment Alignment](notes/Assignment%20Alignment.md) maps the required outputs, current boundaries, and deferred extensions.

## Project goal

Measure how storing quantum signal processing (QSP) phase angles at finite precision changes the accuracy of the realized circuit. Using phase lists from production solvers for realistic target functions, this classical numerical study will determine how rounding error scales with polynomial degree and bit precision, whether correlated errors approach coherent linear growth rather than square-root growth, and how noise-shaped quantization improves accuracy.

The study isolates phase-storage error. Solver approximation residuals, numerical evaluation error, and hardware gate-synthesis error must remain separate from this quantity.

## Core scope

- Generate Hamiltonian-simulation targets (cosine and sine via Jacobi–Anger approximations) and sign/step targets scaled to a maximum of 0.9.
- Use pyqsp's symmetric-QSP method as the default phase solver and QSPPACK as a cross-check.
- Cover degrees of approximately 10–500, spaced roughly logarithmically, and phase precisions of 12, 16, 20, 24, 28, and 32 bits.
- Compare nearest rounding, nearest rounding with a one-phase sum correction, and first-order sigma-delta noise shaping.
- Measure full-unitary, matrix-element, and application-readout error separately, including endpoint and interior behavior.
- Relate error scaling to phase plateaus, rounding-error autocorrelation, and the total variation of sensitivity profiles.
- Determine precision requirements and examine the practical 21-bit regime.

## Workflow and planned deliverables

1. **Forward evaluator and conventions:** implement vectorized QSP evaluation; reproduce solver response curves; validate unitarity, boundedness, and parity; document conventions.
2. **Phase library:** save full-double-precision phases with target parameters, degree, solver version, and approximation residual; plot representative phase sequences.
3. **Quantization:** generate rounded phase lists and record their error sequences.
4. **Measurements:** evaluate error on Chebyshev grids, record application-domain metrics, and spot-check high-degree cases with extended precision.
5. **Analysis:** produce scaling fits, correlation and location analyses, scheme comparisons, precision-budget plots, and an 8–12 page report.

**Checkpoint:** review the convention note, reproduced solver output, and regenerable core phase library with Professor Hen before beginning Stage 3.

Extensions include scaled inversion, eigenstate/bandpass filters, degrees up to 2,000, decimal grids, dithering, and symmetry-preserving noise shaping. These follow a reproducible core result.

## Stage map

Each stage gets its own code package and README under `src/qsp_finite_precision/`, with matching checks under `tests/stageN/`. Planned paths are created when their implementation begins; shared outputs retain the existing data/results/figures layout.

| Stage | Code and documentation | Scope | Status |
| --- | --- | --- | --- |
| 1 | [stage1/](src/qsp_finite_precision/stage1/README.md) | **Part A:** forward evaluator. **Part B:** pyqsp comparisons and solver-convention validation. | Complete for pinned Python packages; MATLAB source mapping documented |
| 2 | [stage2/](src/qsp_finite_precision/stage2/README.md) | Target polynomials, solver phases, and metadata; phase library in `data/phases/` | Python library verified: 21 cases; original MATLAB and supervisor checkpoint pending |
| 3 | `src/qsp_finite_precision/stage3/` (planned) | Quantization schemes; rounded phases in `data/quantized/` | Pending |
| 4 | `src/qsp_finite_precision/stage4/` (planned) | Error measurements; tables in `results/` | Pending |
| 5 | `src/qsp_finite_precision/stage5/` (planned) | Scaling analysis and plots; final writing in `report/` | Pending |

### Stage 1 quick start

From this repository's root, install the package and run the Part A checks:

```shell
python -m pip install -e .
python -m unittest discover -s tests/stage1 -v
```

```python
import numpy as np
from qsp_finite_precision.stage1 import evaluate_qsp

x = np.linspace(-1, 1, 101)
U, P = evaluate_qsp([0.2, 0.7, -0.4], x)
# U.shape == (101, 2, 2); P.shape == (101,)
```

The [Stage 1 README](src/qsp_finite_precision/stage1/README.md) contains the implementation diagrams and mathematical definitions. [The Stage 1B README](experiments/stage1/README.md) embeds reference graphs and error tables for the three built-in examples and linear diagnostic, plus the locked environment and regeneration commands for all 12 tests, 104 identity checks, and 16 Python QSPPACK convention comparisons.

<!-- BEGIN STAGE 2 RESULTS -->

## Stage 2 measured baseline results

**21/21 configured cases generated and independently reloaded**; 3,421 full-precision phases saved. No phases were quantized. The counts and metrics below come from the saved [manifest](results/stage2/summary.json) and [results CSV](results/stage2/library_summary.csv).

| Target | Cases | Degrees | Worst target error on application domain | Worst synthesis error on full interval |
| --- | ---: | --- | ---: | ---: |
| Cosine | 7 | 10–500 | 5.000e-08 | 3.915e-14 |
| Sine | 7 | 11–499 | 5.000e-08 | 5.007e-14 |
| Sign | 7 | 11–499 | 4.784e-03 | 4.019e-14 |

Errors above are sampled maxima in native scaled circuit units. Hamiltonian targets use scale 0.5; the sign target is 0.9 times sign(x) on each recorded gap-excluded domain. The sign polynomial is constructed from a smooth erf surrogate, but target errors are measured against the sign function itself. The target-accuracy acceptance goals (1e-6 for cosine/sine; 1e-2 for sign) are documented implementation choices, not tolerances specified by the professor.

All 21 returned-phase coefficient checks and supplementary Python QSPPACK checks passed. Maximum pyqsp/local complex-amplitude difference on the recorded audit grids: 0.000e+00. Reload verification checks archive hashes, full phase counts, reconstruction, and curve/metric consistency.

![Stage 2 overview](figures/stage2/overview.png)

[Stage 2 implementation and results guide](src/qsp_finite_precision/stage2/README.md) · [Browse all cases, phase plots, and response/error graphs](data/phases/README.md) · [Regeneration commands](experiments/stage2/README.md)

**Remaining checkpoint:** original MATLAB QSPPACK execution is pending (a runner and input file are supplied); Python QSPPACK is supplementary. Professor Hen's required review before Stage 3 is also pending. This is a working Python baseline library, not a claim that those two checks have been completed.

<!-- END STAGE 2 RESULTS -->

## Repository layout

| Folder | Purpose |
| --- | --- |
| references/ | Original project description and PDF copy |
| notes/ | Research dashboard, conventions, decisions, and progress |
| notes/learning/ | Lessons from mathematical foundations through QSP and finite-precision analysis |
| src/qsp_finite_precision/ | Stage 1 evaluator/conventions and Stage 2 core-library implementation |
| tests/ | Checks organized by stage |
| experiments/ | Experiment configurations and reproducibility instructions |
| data/phases/ | Full-precision phase library and metadata |
| data/quantized/ | Rounded phase lists and rounding errors |
| results/ | Measurement tables |
| figures/ | Generated analysis figures |
| report/ | Written research report |

Stage 1 is validated against pyqsp 0.2.0 and Python QSPPACK 0.4.0, with [response overlays](figures/stage1/solver_comparisons.png), [recorded metrics](results/stage1/solver_comparisons.json), and the [convention note](notes/Conventions.md). Stage 2 now supplies a verified Python phase library and its baseline results above. MATLAB QSPPACK was source-inspected, not executed; the original MATLAB comparison and supervisor checkpoint remain pending. Quantization experiments and finite-precision scaling results have not started.

## Project description

- [Project description (PDF)](references/QSP_project.pdf)
- [Original email attachment (DOCX)](references/QSP_project.docx)

Professor Itay Hen authored the project description, dated September 26, 2026. The email attachment was a DOCX; the PDF is a local export of that document.

## Obsidian and Git

Open this repository folder as an Obsidian vault, then open [the research dashboard](notes/Home.md). The vault includes the [Minimal theme](https://github.com/kepano/obsidian-minimal) by kepano, with its upstream MIT license, and the existing Vault Git plugin.

In Obsidian's Command Palette use **Vault Git: Pull** before editing and **Vault Git: Commit and push** after editing. The plugin uses this vault folder's Git repository and origin; credentials are provided by the existing GitHub CLI authentication. Workspace layout, caches, and local secrets are excluded from version control.

The repository is private. AnishKumar-gesgts2 owns it; AnishKumar-gesgts is invited with write access. GitHub displays contributor activity after an account authors commits.
