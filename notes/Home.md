---
cssclasses:
  - qsp-dashboard
---

# Finite-Precision QSP

Anish Kumar

Measure how rounding phase angles affects QSP accuracy and whether improved quantization reduces that error.

## Learn the project

Start with [[learning/Learning Path|Learning Path]] for fourteen lessons that build from complex numbers and matrices to QSP, phase quantization, and experimental analysis. Each lesson includes explanations, worked examples, and practice questions with hidden answers.

Begin at [[learning/00 - What the Project Asks|Lesson 00 — What the Project Asks]]. Track understanding in [[learning/Learning Progress|Learning Progress]] and look up notation in [[learning/Glossary|Glossary]]. For a teaching session, ask: **“Teach me the next lesson from my QSP vault, one concept and one question at a time.”**

## Current work

**Stage 3 — experimental quantization complete; original MATLAB cross-check and supervisor checkpoint pending**

The [core library index](../data/phases/README.md) contains 21 unrounded cosine, sine, and sign cases. The user authorized an experimental Stage 3 run while the supervisor checkpoint remains pending: see the [results summary](../README.md#stage-3-experimental-results), [methods and graphs](../experiments/stage3/README.md), and [[Roadmap]]. The original MATLAB attempt failed before code execution and is [recorded as unavailable](../results/stage2/matlab_execution_status.json). The pending review has not been obtained.

## Workspace

| Resource | Purpose |
| :--- | :--- |
| [[../README|Project overview]] | Goals, methods, and repository structure |
| Project description | Project scope and requirements |
| [[Conventions]] | Definitions and solver mappings |
| [[Research Log]] | Progress, observations, and decisions |
| [[templates/Experiment Note|Experiment note]] | Configuration, results, and interpretation |

## Project stages

1. Validate the forward evaluator and conventions.
2. Generate the core phase library and record solver residuals.
3. Compare the three quantization schemes.
4. Measure unitary, matrix-element, and readout error separately.
5. Analyze scaling and precision requirements; prepare figures and report.

Use the [Stage 2 checkpoint guide](Stage%202%20-%20Checkpoint%20Guide.md) to review the evidence and remaining MATLAB connection/run requirement with the project supervisor. The experimental quantization run does not constitute checkpoint approval.
