# Finite-Precision Phases in Quantum Signal Processing

**Anish Kumar · Professor Itay Hen**

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
| 1 | [stage1/](src/qsp_finite_precision/stage1/README.md) | **Part A:** forward evaluator. **Part B:** solver comparisons and full convention validation. | Part A implemented; Part B pending |
| 2 | `src/qsp_finite_precision/stage2/` (planned) | Target polynomials, solver phases, and metadata; phase library in `data/phases/` | Pending |
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

The [Stage 1 README](src/qsp_finite_precision/stage1/README.md) contains the Part A Mermaid pseudocode diagram, mathematical definitions, and remaining validation work.

## Repository layout

| Folder | Purpose |
| --- | --- |
| references/ | Original project description and PDF copy |
| notes/ | Research dashboard, conventions, decisions, and progress |
| notes/learning/ | Lessons from mathematical foundations through QSP and finite-precision analysis |
| src/qsp_finite_precision/ | Research code separated into stage packages; Stage 1 Part A currently implemented |
| tests/ | Checks organized by stage |
| experiments/ | Experiment configurations and reproducibility instructions |
| data/phases/ | Full-precision phase library and metadata |
| data/quantized/ | Rounded phase lists and rounding errors |
| results/ | Measurement tables |
| figures/ | Generated analysis figures |
| report/ | Written research report |

Stage 1 Part A is implemented with NumPy and basic evaluator checks. Solver-response comparisons, the complete convention note, experiment measurements, and scientific results are pending. Record solver versions and lock the expanded environment when adding solver comparisons.

## Project description

- [Project description (PDF)](references/QSP_project.pdf)
- [Original email attachment (DOCX)](references/QSP_project.docx)

Professor Itay Hen authored the project description, dated September 26, 2026. The email attachment was a DOCX; the PDF is a local export of that document.

## Obsidian and Git

Open this repository folder as an Obsidian vault, then open [the research dashboard](notes/Home.md). The vault includes the [Minimal theme](https://github.com/kepano/obsidian-minimal) by kepano, with its upstream MIT license, and the existing Vault Git plugin.

In Obsidian's Command Palette use **Vault Git: Pull** before editing and **Vault Git: Commit and push** after editing. The plugin uses this vault folder's Git repository and origin; credentials are provided by the existing GitHub CLI authentication. Workspace layout, caches, and local secrets are excluded from version control.

The repository is private. AnishKumar-gesgts2 owns it; AnishKumar-gesgts is invited with write access. GitHub displays contributor activity after an account authors commits.
