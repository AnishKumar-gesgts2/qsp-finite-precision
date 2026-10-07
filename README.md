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

## Repository layout

| Folder | Purpose |
| --- | --- |
| references/ | Original project description and PDF copy |
| notes/ | Research dashboard, conventions, decisions, and progress |
| src/ | Future QSP evaluation, quantization, and measurement code |
| experiments/ | Experiment configurations and reproducibility instructions |
| data/phases/ | Full-precision phase library and metadata |
| data/quantized/ | Rounded phase lists and rounding errors |
| results/ | Measurement tables |
| figures/ | Generated analysis figures |
| report/ | Written research report |

This repository currently contains the project setup; scientific code, measurements, and results are pending. Reproduction commands and a dependency lockfile should be added alongside the implementation.

## Project description

- [Project description (PDF)](references/QSP_project.pdf)
- [Original email attachment (DOCX)](references/QSP_project.docx)

Professor Itay Hen authored the project description, dated September 26, 2026. The email attachment was a DOCX; the PDF is a local export of that document.

## Obsidian and Git

Open this repository folder as an Obsidian vault, then open [the research dashboard](notes/Home.md). The vault includes the [Minimal theme](https://github.com/kepano/obsidian-minimal) by kepano, with its upstream MIT license, and the existing Vault Git plugin.

In Obsidian's Command Palette use **Vault Git: Pull** before editing and **Vault Git: Commit and push** after editing. The plugin uses this vault folder's Git repository and origin; credentials are provided by the existing GitHub CLI authentication. Workspace layout, caches, and local secrets are excluded from version control.

The repository is private. AnishKumar-gesgts2 owns it; AnishKumar-gesgts is invited with write access. GitHub displays contributor activity after an account authors commits.
