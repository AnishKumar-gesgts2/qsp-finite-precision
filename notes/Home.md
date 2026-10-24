---
cssclasses:
  - qsp-dashboard
---

# Finite-Precision QSP

Anish Kumar · Professor Itay Hen

Measure how rounding phase angles affects QSP accuracy and whether improved quantization reduces that error.

## Learn the project

Start with [[learning/Learning Path|Learning Path]] for fourteen lessons that build from complex numbers and matrices to QSP, phase quantization, and experimental analysis. Each lesson includes explanations, worked examples, and practice questions with hidden answers.

Begin at [[learning/00 - What the Project Asks|Lesson 00 — What the Project Asks]]. Track understanding in [[learning/Learning Progress|Learning Progress]] and look up notation in [[learning/Glossary|Glossary]]. For a teaching session, ask: **“Teach me the next lesson from my QSP vault, one concept and one question at a time.”**

## Current work

**Stage 2 — Python library verified; MATLAB cross-check and supervisor checkpoint pending**

The [core library index](../data/phases/README.md) now contains 21 unrounded cosine, sine, and sign cases with phase plots, response/error graphs, and saved residuals. See [the measured README summary](../README.md#stage-2-measured-baseline-results) and [Stage 2 methods](../src/qsp_finite_precision/stage2/README.md). Next, execute the prepared original MATLAB QSPPACK cross-check and review the regenerable results with Professor Hen before Stage 3. See [[Roadmap]] for the full plan.

## Workspace

| Resource | Purpose |
| :--- | :--- |
| [[../README|Project overview]] | Goals, methods, and repository structure |
| [[../references/QSP_project.pdf|Project description]] | Professor Hen’s research brief |
| [[Conventions]] | Definitions and solver mappings |
| [[Research Log]] | Progress, observations, and decisions |
| [[templates/Experiment Note|Experiment note]] | Configuration, results, and interpretation |

## Project stages

1. Validate the forward evaluator and conventions.
2. Generate the core phase library and record solver residuals.
3. Compare the three quantization schemes.
4. Measure unitary, matrix-element, and readout error separately.
5. Analyze scaling and precision requirements; prepare figures and report.

Use the [Stage 2 checkpoint guide](Stage%202%20-%20Checkpoint%20Guide.md) to review the evidence and remaining MATLAB sign-in/run requirement. Review the Stage 2 outputs with Professor Hen before beginning quantization.
