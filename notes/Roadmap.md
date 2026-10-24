# Roadmap

[Professor Hen's original description](../references/QSP_project.docx) is authoritative. Before each stage and completion claim, reread its corresponding section; use [[Assignment Alignment]] to track required outputs, extensions, and the supervisor checkpoint.

Learning preparation: follow [[learning/Learning Path|Learning Path]] and record understanding in [[learning/Learning Progress|Learning Progress]]. Lessons 01–06 provide the mathematical foundations, 07–09 prepare Stages 1–2, and 10–13 prepare the quantization and analysis stages. Reading a lesson does not mark an implementation milestone complete.

- [ ] Read the starred background sources in the project description.
- [x] Stage 1: implement and validate the forward evaluator for the pinned Python packages.
  - [x] Part A: implement the vectorized evaluator and basic checks. See the [Stage 1 README](../src/qsp_finite_precision/stage1/README.md) for the implementation diagram and usage.
  - [x] Part B: reproduce solver examples and complete mathematical/convention validation for pyqsp 0.2.0 and Python QSPPACK 0.4.0.
    - [x] Run reproducible mathematical identity checks through degree 500; 104 recorded checks pass.
    - [x] Reproduce three built-in pyqsp examples and a linear diagnostic on 1,025 inputs; check all 16 Python QSPPACK full/reduced and real/imaginary combinations. Save per-example reference graphs, phase plots, and maximum/RMSE error tables in the Stage 1B README.
- [x] Document solver conventions in [[Conventions]], including the source-inspected MATLAB mapping and execution boundary.
- [ ] Stage 2: generate and inspect the two core phase families.
  - [x] Generate and independently reload 21 Python baseline cases across degrees about 10–500; save full phases, target parameters, coefficients, versions, convergence, and separate residuals.
  - [x] Publish per-case original/reconstructed response graphs, phase-index plots, error tables, library index, and a measurable project README summary.
  - [x] Validate every case against its package response and supplementary Python QSPPACK output.
  - [x] Regenerate both stages from a separate clone/new pinned environment and compare all 21 rebuilt phase lists and curves; see the [checkpoint guide](Stage%202%20-%20Checkpoint%20Guide.md).
  - [x] Package the pinned original QSPPACK source and all inputs for local MATLAB or MATLAB Online; preparation is not execution evidence.
  - [ ] Run the original MATLAB QSPPACK numerical cross-check; Python QSPPACK validation does not replace it.
- [ ] Review the Stage 2 checkpoint with Professor Hen.
- [ ] Stage 3: implement the three core quantization schemes.
- [ ] Stage 4: measure separate error metrics and validate numerical precision.
- [ ] Stage 5: analyze scaling, correlations, noise shaping, and required bits.
- [ ] Produce regenerable figures and the research report.

Track progress by completed milestones. Extensions follow the reproducible core.
