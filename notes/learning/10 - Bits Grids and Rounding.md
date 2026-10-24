# 10 — Bits, Grids, and Rounding

Prerequisites: [[09 - Solvers Conventions and Phase Libraries]].

## A finite word gives a finite set of angles

For $b$ bits spanning an interval of length $2\pi$, there are $2^b$ grid positions and spacing

$$
h=\frac{2\pi}{2^b}.
$$

Doubling the number of positions means adding one bit and halving $h$. Nearest rounding to the lattice $h\mathbb Z$ gives

$$
\widehat\phi=h\thinspace \mathrm{round}(\phi/h),\qquad
\delta\phi=\widehat\phi-\phi,\qquad |\delta\phi|\le h/2.
$$

The $b$ here is phase-word precision, not the total number of mantissa bits used to evaluate the circuit.

## Worked example

For a simple toy grid $h=0.1$, phases $(0.24,0.24,0.24)$ directly round to $(0.2,0.2,0.2)$. Their errors are $(-0.04,-0.04,-0.04)$. Three small errors have the same sign because the inputs repeat. Deterministic rounding is not independent random noise.

For a full-circle 12-bit grid, $h\approx0.001534$ radians and the nearest-rounding half-step is about $0.000767$. Write down the grid before interpreting a bit count.

## Three core schemes

**Direct nearest rounding:** round every phase independently.

**One-phase sum correction:** round the first $d$ phases, then choose the last rounded phase so the total is the nearest grid value to the original total:

$$
\widehat\phi_d=h\thinspace \mathrm{round}\left(\frac{\sum_{j=0}^{d}\phi_j}{h}\right)
-\sum_{j=0}^{d-1}\widehat\phi_j.
$$

Every phase remains on-grid, and the total error has magnitude at most $h/2$. The last individual phase error can be much larger than $h/2$. For the toy list, the corrected list is $(0.2,0.2,0.3)$, with errors $(-0.04,-0.04,+0.06)$ and total error $-0.02$.

Exact preservation of an arbitrary real-valued original sum is generally impossible if every stored phase must lie on this grid. “Preserve the sum on the grid” means preserve its nearest grid representative. Record this definition with the supervisor when implementing the assignment's shorthand.

**First-order sigma-delta:** carry each rounding residual to the next phase. This controls all error partial sums, not just the total. Lesson 12 derives it.

## Wrapping and ties

Angles differing by $2\pi$ give the same $D$. Stored words may use $[0,2\pi)$ or $[-\pi,\pi)$. An angle just below $2\pi$ might round to $0$ after wrapping. Its raw numeric subtraction is almost $-2\pi$, although its local angle perturbation is tiny.

Perform proofs and correlation diagnostics with consistent unwrapped quantization representatives, retaining the residual/carry information; wrap for storage afterward. Use the wrapped phases to evaluate matrices. A naive subtraction of wrapped values can fabricate correlations and destroy a partial-sum diagnostic.

Record tie behavior, such as round-to-even. Dithering, decimal grids, and symmetry-preserving quantization are extensions rather than replacements for the three core schemes.

## Check your understanding

1. How does the grid change from 16 to 20 bits?
2. Round $(0.26,0.26,0.26)$ on the toy grid and calculate the total direct error.
3. Why does one-phase correction not guarantee a smaller interior error?

> [!answer]- Check after trying
> 1. Its spacing becomes $1/16$ as large.
> 2. $(0.3,0.3,0.3)$, with total error $+0.12$.
> 3. It fixes the total error but may concentrate a large perturbation in one phase. Interior sensitivities vary between phases.

Next: [[11 - Error Bounds and Correlations]].
