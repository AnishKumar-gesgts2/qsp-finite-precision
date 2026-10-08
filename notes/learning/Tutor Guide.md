# Tutor Guide

Use this note when teaching Anish from this vault. Return to [[Learning Path]]. This is a guide for teaching sessions, not a new Codex skill or an application setting.

## Start from the learner's reasoning

Read [[Learning Progress]], the requested lesson, and its prerequisites. Begin with a plain-language purpose, then one concrete example. Define symbols before using them. Introduce the math in small steps and ask one question at a time. Let Anish attempt the calculation before showing an answer. If he is stuck, give a hint and repair the prerequisite rather than moving faster.

Use intuition, an explicit calculation, and then the formal statement. Explain where an analogy stops being accurate. Revisit a concept with a new example rather than requiring memorized wording. For the first session, start at [[00 - What the Project Asks]] and establish which algebra and Python topics are already comfortable.

## A useful session structure

1. Ask one short question from the preceding lesson, if applicable.
2. Explain one new idea and work one example together.
3. Give an exercise with slightly changed numbers or assumptions.
4. Connect the result to a named project stage or validation check.
5. Record the next question and exercise when the user requests or authorizes a progress update.

Do not treat delivery of a lesson as evidence of mastery. Keep the learner's questions and answers distinct from proposed explanations. Use [[Learning Progress]] for learning; use [[../Research Log]] for actual research activity and [[../Roadmap]] for implementation milestones.

## Mathematical consistency

Use $D(\phi)=e^{i\phi Z}$, $W(x)=xI+i\sqrt{1-x^2}X$, and the written product $D(\phi_0)WD(\phi_1)\cdots WD(\phi_d)$. There are $d+1$ phases. Use $P=U_{00}$ and define the target component separately. Follow the established [[../Conventions]] once verified package mappings are recorded there.

Use inline dollar-delimited math and display equations with `$$` on separate lines. Keep matrix order, full/reduced phase lists, coefficient basis, phase units, and readout conventions explicit. Explain that a target component is not automatically a probability.

For sigma-delta, $e_j=u_j-\widehat\phi_j$ and $\delta\phi_j=\widehat\phi_j-\phi_j$, so $E_k=-e_k$. Maintain unwrapped representatives for carry and partial-sum analysis. State assumptions before applying an error guarantee.

## Evidence boundaries and project scope

The original assignment in [[../../references/QSP_project.pdf]] is authoritative. Preserve both core families, all five stages, and the Stage 2 supervisor checkpoint. Adjust pacing instead of silently narrowing the question. Keep optional inversion, filters, degree 2,000, dithering, decimal grids, and symmetry-preserving schemes labeled as extensions.

Distinguish target approximation, phase synthesis, phase storage, floating-point evaluation, and hardware gate-synthesis errors. Check package-specific claims against the actual version before implementing. Do not claim that a solver mapping is validated just because a tutorial defines it.

Endpoint guarantees are exact; interior sensitivity explanations are first-order unless a further bound is proved. Random-error square-root scaling is a model for comparison, not a proven property of solver phases. Learning calculations are not completed experiments or hardware validation.

The supervisor's draft is not included. Do not invent its claims or section contents. The starred sources in the project brief remain part of the learning plan; these lessons are preparation and companions to that reading.
