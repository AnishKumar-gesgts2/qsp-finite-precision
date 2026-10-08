# 04 — Norms and Measuring Error

Prerequisites: [[03 - Qubits and Rotations]].

## Size depends on the question

For a scalar, error magnitude is $|a-b|$. For a matrix, we need a norm. The operator norm used here asks how much the matrix can stretch any unit-length vector:

$$
\|A\|_2=\max_{\|v\|_2=1}\|Av\|_2.
$$

It equals the largest singular value of $A$. Singular values are the square roots of the eigenvalues of $A^\dagger A$. An eigenvalue $\lambda$ satisfies $Av=\lambda v$ for a nonzero vector $v$; singular values measure stretching even when $A$ has complex or poorly informative eigenvalues.

For a diagonal matrix $\operatorname{diag}(a,b)$, the operator norm is $\max(|a|,|b|)$. A unitary has operator norm one. Also

$$
\|AB\|_2\le\|A\|_2\|B\|_2,\qquad
\|UAV\|_2=\|A\|_2
$$

when $U,V$ are unitary. The second identity will make the phase-error proof manageable.

## Four related quantities

At one input, let $\Delta U=U_{\widehat\Phi}-U_\Phi$, $P=U_{00}$, and let $r$ be the chosen real or imaginary part of $P$.

| Quantity | Definition | What it compares |
| --- | --- | --- |
| Full-unitary error | $\|\Delta U\|_2$ | All input states and both output components |
| Matrix-element error | $|\widehat P-P|$ | One complex amplitude |
| Readout error | $|\widehat r-r|$ | The component carrying the target |
| Probability change | $\big||\widehat P|^2-|P|^2\big|$ | A computational-basis measurement probability |

These are not interchangeable. For normalized basis vectors, $|\langle0|\Delta U|0\rangle|\le\|\Delta U\|_2$, so

$$
|\widehat r-r|\le|\widehat P-P|\le\|\Delta U\|_2.
$$

“Readout” here is a mathematical target component. It is not automatically a probability measured directly in one shot.

## Worked example

Compare $U=I$ with $\widehat U=D(\delta)$. The unitary and top-left amplitude errors both equal $2|\sin(\delta/2)|$. The real-part readout error is $|\cos\delta-1|$, approximately $\delta^2/2$. The probability of measuring $0$ from $|0\rangle$ is unchanged.

One perturbation therefore gives a first-order matrix error, a second-order real-part error, and zero probability change for that state. A small readout error does not imply a small full-unitary error of the same size.

## Check your understanding

1. Find $\|\operatorname{diag}(3,4i)\|_2$.
2. For $A=\begin{pmatrix}0&1\\0&0\end{pmatrix}$, both eigenvalues are zero. Is its operator norm zero?
3. Can a computed readout error exceed the matrix-element error at the same input?

> [!answer]- Check after trying
> 1. $4$.
> 2. No; applying it to $(0,1)^T$ gives $(1,0)^T$, so its operator norm is $1$. This is why we use singular values.
> 3. Mathematically no. A violation beyond numerical tolerance suggests mismatched definitions or an implementation problem.

Next: [[05 - Polynomials and Chebyshev]].
