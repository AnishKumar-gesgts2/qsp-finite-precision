# Project authority and scope

- Professor Itay Hen's original assignment, `references/QSP_project.docx` (September 26, 2026), is the authoritative project specification. `references/QSP_project.pdf` is its local PDF export. READMEs, roadmap notes, chat plans, and package examples are summaries or implementation choices and do not override the original description.
- Before implementing a new stage, changing scope, or declaring a milestone complete, reread the relevant stage and output requirements in the original document. Review its core/extension distinction and checkpoint when applicable. Use `notes/Assignment Alignment.md` as a source map, not a substitute for rereading the source.
- Preserve the entire core assignment: all five stages, both core target families, and the specified measurements and analysis questions. Do not replace the scientific question with solver benchmarking, evaluator validation, or a new phase-synthesis algorithm.
- Distinguish the professor's explicit requirements from our implementation choices and optional additions. `Stage 1A` and `Stage 1B` are internal subdivisions of his Stage 1.
- Keep original MATLAB QSPPACK execution distinct from validation against the Python `qsppack` implementation. The Python port is supplementary and does not silently replace the assignment's MATLAB cross-check. Record what actually ran.
- Before Stage 3, preserve the specified supervisor checkpoint: review the convention note, reproduction of solver outputs, and regenerable core phase library with residuals and phase plots. Do not mark supervisor review complete without evidence.
- Keep function-approximation, solver, floating-point-evaluation, and phase-storage errors separate. Distinguish sampled checks from proofs, validation fixtures from the core phase library, and implementation completion from the student's understanding or the supervisor's approval.
- Leave extensions until the core result is reproducible. Update the alignment note and roadmap when verified work changes; do not silently revise the original assignment.

The user's instructions about local-helper routing also apply. Keep scientific reasoning, source checks, and final decisions with the primary assistant; use deterministic scripts for exact extraction and operations.
