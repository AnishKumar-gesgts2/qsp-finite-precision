# 12 — Sigma-Delta and Sensitivity

Prerequisites: [[11 - Error Bounds and Correlations]]. Derivatives and first-order Taylor approximation are needed for the second half; ask for a calculus refresher if necessary.

## Carry what rounding lost

Direct rounding discards each residual. First-order sigma-delta adds that residual to the next input. With $e_{-1}=0$:

$$
u_j=\phi_j+e_{j-1},\quad
\widehat\phi_j=h\,\operatorname{round}(u_j/h),\quad
e_j=u_j-\widehat\phi_j.
$$

On an unrestricted nearest-rounding lattice, $|e_j|\le h/2$. Use unwrapped representatives and carry states before wrapping phases for storage.

## Worked example

For $(0.24,0.24,0.24)$ with $h=0.1$:

| $j$ | $u_j$ | $\widehat\phi_j$ | $e_j$ | $\delta\phi_j=\widehat\phi_j-\phi_j$ |
| --- | --- | --- | --- | --- |
| 0 | 0.24 | 0.2 | +0.04 | −0.04 |
| 1 | 0.28 | 0.3 | −0.02 | +0.06 |
| 2 | 0.22 | 0.2 | +0.02 | −0.04 |

The errors need not individually lie within $h/2$ of the original angles: the second is $0.06$. Instead, it is the error of rounding the adjusted input $u_j$ that is bounded by $h/2$.

## A telescoping partial-sum identity

Rearrange the recursion:

$$
\delta\phi_j=e_{j-1}-e_j,\qquad
E_k=\sum_{j=0}^k\delta\phi_j=-e_k.
$$

Every partial sum satisfies $|E_k|\le h/2$. At the endpoints, the exact unitary error therefore satisfies

$$
2|\sin(E_d/2)|\le|E_d|\le h/2.
$$

This is independent of degree. One-phase sum correction also controls the total, but generally not all earlier partial sums.

## Interior sensitivity

Define the complex sensitivity

$$
g_j(x)=\frac{\partial P_\Phi(x)}{\partial\phi_j}.
$$

It tells us how much the amplitude changes when phase $j$ changes a little, with the other phases held fixed. To first order,

$$
P_{\Phi+\delta\Phi}(x)-P_\Phi(x)
\approx\sum_{j=0}^d g_j(x)\delta\phi_j.
$$

Since $\delta\phi_j=E_j-E_{j-1}$, where $E_{-1}=0$, rearranging the sum gives

$$
\sum_{j=0}^d g_j\delta\phi_j
=g_dE_d+\sum_{j=0}^{d-1}(g_j-g_{j+1})E_j.
$$

Consequently, sigma-delta's **linearized** amplitude error is at most

$$
\frac h2\left(|g_d|+\underbrace{\sum_{j=0}^{d-1}|g_{j+1}-g_j|}_{\operatorname{TV}(g)}\right).
$$

Smooth sensitivities make the total variation small. Rapidly changing sensitivities can defeat the interior benefit. This first-order expression does not by itself bound the complete finite-perturbation error; inspect the actual circuit differences and the linearization residual.

## Computing a derivative without guessing a step size

Write $U=L_jD(\phi_j)R_j$, where $L_j$ contains everything before that phase factor and $R_j$ everything after it. Since $D'=iZD$,

$$
\frac{\partial U}{\partial\phi_j}=L_j(iZD(\phi_j))R_j.
$$

Take its top-left entry for $g_j$. Prefix and suffix products let you compute all derivatives without rebuilding every full product. Compare a few against central finite differences as a diagnostic. For a real or imaginary target component, use the corresponding component of $g_j$.

Ordinary sigma-delta can break a palindromic phase list. Preserving symmetry is an assigned extension; it does not automatically follow from endpoint cancellation.

## Check your understanding

1. Verify all three partial sums in the table.
2. If all $g_j$ are equal, what does the first-order sum depend on?
3. Why should you compare the derivative prediction with actual error at several grid spacings?

> [!answer]- Check after trying
> 1. $-0.04,+0.02,-0.02$, all within $0.05$.
> 2. Only the total $E_d$; the variation term is zero.
> 3. To see when higher-order terms matter and whether the linearization explains the measured effect.

Next: [[13 - Designing and Interpreting Experiments]].
