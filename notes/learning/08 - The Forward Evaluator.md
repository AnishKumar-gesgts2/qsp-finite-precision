# 08 — The Forward Evaluator

Prerequisites: [[06 - QSP by Hand]] and basic Python. If arrays, functions, or loops are new, ask for a Python/NumPy warm-up before this lesson.

## Translate the formula literally

Start with $D(\phi_0)$. For each remaining phase, append $W(x)D(\phi_j)$ on the right. In NumPy, `@` means matrix multiplication; `*` multiplies corresponding entries and would be wrong here.

The following is a teaching example at one input, not the completed Stage 1 module:

```python
import numpy as np

def D(phi):
    return np.diag([np.exp(1j * phi), np.exp(-1j * phi)])

def qsp_at_x(phases, x):
    if len(phases) == 0:
        raise ValueError("At least one phase is required")
    if not -1 <= x <= 1:
        raise ValueError("x must lie in [-1, 1]")
    s = np.sqrt(1 - x*x)
    W = np.array([[x, 1j*s], [1j*s, x]], dtype=complex)
    U = D(phases[0])
    for phi in phases[1:]:
        U = U @ W @ D(phi)
    return U, U[0, 0]
```

`1j` is Python's imaginary unit. `U[0, 0]` selects the top-left entry. `U.conj().T` is the conjugate transpose. For a matrix difference `delta_U`, `np.linalg.norm(delta_U, ord=2)` computes the spectral norm; the default norm for a matrix is not this project metric.

## Worked prediction before execution

For `phases=[0, 0, 0]` and `x=0.5`, predict $P=T_2(0.5)=-0.5$. For `phases=[np.pi/4, np.pi/4]`, predict $P=0.5i$. A numerical value is more useful when you know independently what it should be.

## Vectorization

Stage 1 should evaluate an array of inputs together. Conceptually, make one $W$ per input in an array of shape `(N, 2, 2)`. NumPy's `@` can multiply the last two dimensions while batching over the first. Keep a loop over phases. Establish correctness at one input before adding batching; compare the batched output to the scalar version on a small grid.

## The meaningful checks

- All-zero phases reproduce $T_d(x)$ in the top-left entry.
- At $x=1$, reproduce $D(\sum_j\phi_j)$; at $x=-1$, reproduce $(-1)^dD(\sum_j\phi_j)$.
- Verify $U^\dagger U\approx I$ and $|P|\le1$ within floating-point tolerance.
- Verify $P(-x)=(-1)^dP(x)$.
- Reproduce two or three solver response curves in each solver's convention, including the component carrying the target.

The algebraic checks catch basic mistakes. Solver agreement is also needed: a perfectly unitary evaluator can still use the wrong phase mapping.

## Check your understanding

1. Why do three phases mean degree parameter $d=2$?
2. What changes if you replace `U = U @ W @ D(phi)` with `U = D(phi) @ W @ U`?
3. Why is boundedness alone insufficient validation?

> [!answer]- Check after trying
> 1. There are two signal factors between three phase factors.
> 2. You build a different ordered product. It need not match the intended circuit even if some special cases agree.
> 3. Many incorrect products are still unitary and bounded. They can have the wrong response.

Next: [[09 - Solvers Conventions and Phase Libraries]].
