# Roadmap

Learning preparation: follow [[learning/Learning Path|Learning Path]] and record understanding in [[learning/Learning Progress|Learning Progress]]. Lessons 01–06 provide the mathematical foundations, 07–09 prepare Stages 1–2, and 10–13 prepare the quantization and analysis stages. Reading a lesson does not mark an implementation milestone complete.

- [ ] Read the starred background sources in the project description.
- [ ] Stage 1: implement and validate the forward evaluator.
  - [x] Part A: implement the vectorized evaluator and basic checks. See the [Stage 1 README](../src/qsp_finite_precision/stage1/README.md) for the implementation diagram and usage.
  - [ ] Part B: reproduce solver examples and complete mathematical/convention validation.
    - [x] Run reproducible mathematical identity checks through degree 500; 104 recorded checks pass.
    - [ ] Reproduce pyqsp examples and complete the pyqsp/QSPPACK convention note.
- [ ] Document solver conventions in [[Conventions]].
- [ ] Stage 2: generate and inspect the two core phase families.
- [ ] Review the Stage 2 checkpoint with Professor Hen.
- [ ] Stage 3: implement the three core quantization schemes.
- [ ] Stage 4: measure separate error metrics and validate numerical precision.
- [ ] Stage 5: analyze scaling, correlations, noise shaping, and required bits.
- [ ] Produce regenerable figures and the research report.

Track progress by completed milestones. Extensions follow the reproducible core.
