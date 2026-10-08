# Learning Path

Learn the project from the ground up. Start with Lesson 00; you do not need a quantum computing course first. The aim is to understand what each mathematical object does, then use it in the finite-precision study.

These are teaching notes, not completed research results. The assignment in [[../../references/QSP_project.pdf|Professor Hen's project description]] defines the research scope. The lessons supply explanations, small examples, and exercises to prepare you for it.

## How we will learn

Use one lesson at a time. Ask: **“Teach me Lesson 01 from my QSP vault. Start simply, work through an example, and ask me one question at a time.”** I should explain an idea, check your reasoning, and adapt the pace. You can request a hint before revealing a solution. Reading a page is preparation; being able to explain and use it is the checkpoint.

Allow about 20–40 minutes for an initial discussion, with additional time for exercises. This is a suggested session size, not a deadline. Follow the prerequisites rather than a fixed calendar. Keep the full core project intact as the learning timeline changes.

## Part I — Mathematical foundations

| Lesson | Main question | You are ready when you can… |
| --- | --- | --- |
| [[00 - What the Project Asks]] | What are we trying to measure? | Distinguish target approximation from phase-storage error. |
| [[01 - Complex Numbers and Phase]] | What does an angle do to a complex number? | Calculate a phase factor and explain its magnitude. |
| [[02 - Vectors Matrices and Order]] | How do matrices transform a state? | Multiply a small matrix product in the right order. |
| [[03 - Qubits and Rotations]] | What are the two QSP building blocks? | Explain $D(\phi)$ and $W(x)$ and the angle convention. |
| [[04 - Norms and Measuring Error]] | How do we measure the size of a matrix error? | Separate unitary, amplitude, readout, and probability errors. |
| [[05 - Polynomials and Chebyshev]] | Why do rotations lead to polynomials? | Use the Chebyshev recurrence, parity, and sampling grid. |

## Part II — Understanding and evaluating QSP

| Lesson | Main question | Project connection |
| --- | --- | --- |
| [[06 - QSP by Hand]] | How do phases shape a response? | Derive degree-0, degree-1, and zero-phase checks. |
| [[07 - Why QSP Matters and Core Targets]] | Why does a scalar polynomial matter for a large matrix? | Understand both core target families and approximation domains. |
| [[08 - The Forward Evaluator]] | How do we translate the formula into code? | Prepare Stage 1 and verify multiplication order. |
| [[09 - Solvers Conventions and Phase Libraries]] | Where do realistic phase lists come from? | Prepare Stage 2 and its supervisor checkpoint. |

## Part III — Finite precision and the research question

| Lesson | Main question | Project connection |
| --- | --- | --- |
| [[10 - Bits Grids and Rounding]] | What does storing an angle in $b$ bits mean? | Define the three core quantization schemes. |
| [[11 - Error Bounds and Correlations]] | When do small phase errors add or cancel? | Derive endpoint formulas and linear versus square-root benchmarks. |
| [[12 - Sigma Delta and Sensitivity]] | Why can carrying a residual improve accuracy? | Understand partial sums, sensitivities, and interior limitations. |
| [[13 - Designing and Interpreting Experiments]] | How do we answer the question fairly? | Prepare Stages 4–5 and interpret precision budgets. |

## Navigation and continued teaching

- [[Learning Progress]] — track understanding and unresolved questions.
- [[Glossary]] — definitions and symbols without opening every lesson.
- [[Tutor Guide]] — instructions for teaching from this vault in future chats.
- [[../Roadmap|Research roadmap]] — implementation milestones, separate from learning progress.

## Sources and further reading

The lesson equations follow the convention in the local project description; worked examples and elementary derivations are provided here for instruction. Package-specific facts should be checked against the installed version when implementation begins.

- [[../../references/QSP_project.pdf|Project description]] and [[../../references/QSP_project.docx|original DOCX]] — project scope, core methods, and starred reading list.
- [Martyn et al., A Grand Unification of Quantum Algorithms](https://arxiv.org/abs/2105.02859) — the assigned tutorial connecting QSP to quantum algorithms.
- [Lin, Lecture Notes on Quantum Algorithms for Scientific Computation](https://arxiv.org/abs/2201.08309) — the assigned mathematical background.
- [pyqsp repository](https://github.com/ichuang/pyqsp) — current package conventions and examples.
- [QSPPACK repository](https://github.com/qsppack/QSPPACK) — the assignment's cross-check implementation.

The supervisor's draft manuscript is mentioned in the assignment but is not included in this vault. These lessons do not claim to reproduce its unpublished results. Ask for it when studying the research-specific proofs in depth.
