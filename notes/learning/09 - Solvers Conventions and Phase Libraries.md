# 09 — Solvers, Conventions, and Phase Libraries

Prerequisites: [[07 - Why QSP Matters and Core Targets]], [[08 - The Forward Evaluator]].

## Two directions of the same problem

The forward direction takes phases and evaluates a response. The inverse direction takes an admissible target polynomial and finds phases. Our research studies rounded phases produced by established inverse solvers. Writing a new inverse solver is outside the core assignment.

The pipeline has distinct objects:

$$
f(x)\ \longrightarrow\ p_d(x)\ \longrightarrow\ \Phi
\ \longrightarrow\ r_\Phi(x)\ \longrightarrow\ r_{\widehat\Phi}(x).
$$

They are the desired function, finite-degree polynomial, synthesized phase list, baseline response, and rounded response. Each arrow can introduce a different discrepancy.

## Convention is part of the data

Our teaching convention uses $W_x$, $D(\phi)=e^{i\phi Z}$, left-to-right construction of the written product, and top-left amplitude $P$. In the documented pyqsp `sym_qsp` convention, the target is in $\operatorname{Im}P$, not in the whole complex amplitude. This is explicitly stated in the [pyqsp README](https://github.com/ichuang/pyqsp).

The assignment identifies MATLAB QSPPACK as the cross-check with a real-part target convention. The newer [Python QSPPACK documentation](https://qsppack.readthedocs.io/en/latest/getting_started.html) also exposes real/imaginary and full/reduced options. Identify which implementation and version you actually use. Do not replace the planned cross-check or assume a conversion without testing it.

Record signal operator, phase sign and scale, ordering, indexing, full versus reduced list, any endpoint offsets, coefficient basis, parity, and target component in [[../Conventions]]. These lessons define examples; they do not establish a verified mapping for a package that has not yet been run.

## Worked diagnostic

Suppose a solver targets $f(x)=x$ and returns full phases $(\pi/4,\pi/4)$ in our example convention. Lesson 06 gives $P=ix$. Comparing $P$ directly to $x$ reports a large discrepancy; comparing $\operatorname{Im}P$ to $x$ reports zero. A wrong readout can look like a bad solver.

## Saving a phase library

For each case, retain the full phase list at full double precision, target parameters and scaling, approximation domain, achieved degree, coefficient basis, solver name/version/options, convergence status, and baseline residual. Saving decimal strings should preserve binary64 round-trip values; a deliberately shortened printout is already a quantization step.

Measure both the solver's coefficient/convergence residual and the evaluated target residual when available; they need not be the same metric. Full double precision is a baseline, not a promise that all stored digits are scientifically reliable.

Stage 2 covers both core families at roughly logarithmic degrees from about 10 to 500. Respect parity and record achieved degrees. Phase plots should show structure such as plateaus, but structure is a hypothesis for correlation, not a measured storage-error result.

## Check your understanding

1. Why is a reduced symmetric phase list insufficient input for our evaluator without expansion?
2. If synthesis stops without convergence, is a returned phase array enough to include the case as successful?
3. What is required before beginning Stage 3?

> [!answer]- Check after trying
> 1. The evaluator expects all $d+1$ factors; a reduced list uses a package-specific reconstruction.
> 2. No. Record the status, inspect the residual, and identify failures explicitly.
> 3. The assignment requires a supervisor review of the convention note, reproduced solver curves, and regenerable core library with residuals and phase plots.

Next: [[10 - Bits Grids and Rounding]].
