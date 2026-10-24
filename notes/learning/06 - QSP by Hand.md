# 06 — QSP by Hand

Prerequisites: [[04 - Norms and Measuring Error]], [[05 - Polynomials and Chebyshev]].

## Assemble the building blocks

For $d+1$ phases, use the written product

$$
U_\Phi(x)=D(\phi_0)W(x)D(\phi_1)\cdots W(x)D(\phi_d),
\qquad P_\Phi(x)=\langle0|U_\Phi(x)|0\rangle.
$$

The input $x$ is variable. The phase list is fixed while you sweep over inputs. Changing the list changes the response function. This distinction is central: $x$ is not another phase to be rounded.

## Degree zero

With one phase and no signal steps, $U=D(\phi_0)$, so $P=e^{i\phi_0}$. The response is constant in $x$. Depending on which component carries a target, its real or imaginary part is $\cos\phi_0$ or $\sin\phi_0$.

## Degree one: multiply explicitly

Let $s=\sqrt{1-x^2}$. Multiplying $D(\phi_0)WD(\phi_1)$ gives

$$
U=\begin{pmatrix}
xe^{i(\phi_0+\phi_1)}&is e^{i(\phi_0-\phi_1)}\cr
is e^{-i(\phi_0-\phi_1)}&xe^{-i(\phi_0+\phi_1)}
\end{pmatrix}.
$$

Thus $P(x)=xe^{i(\phi_0+\phi_1)}$. For $\phi_0=\phi_1=\pi/4$, $P(x)=ix$ and its imaginary part is $x$.

The amplitude alone depends on the phase sum in this example, but the off-diagonal entries depend on the difference. Two phase lists can give the same $P$ while giving different full matrices. This explains why the project measures both.

## Degree two and interference

With all phases zero, $U=W^2$ and $P=2x^2-1$. For a general three-phase list, multiplication gives

$$
P(x)=e^{i(\phi_0+\phi_2)}
\left[x^2e^{i\phi_1}-(1-x^2)e^{-i\phi_1}\right].
$$

The negative term comes from the product of two imaginary off-diagonal entries. Both ways of reaching the top-left entry contribute. Their complex phases determine interference.

## What QSP promises, and what it does not

The top-left response is a bounded polynomial with parity $d$. The off-diagonal response generally also contains a $\sqrt{1-x^2}$ factor. Do not infer that every entry is an ordinary polynomial.

Degree, parity, and boundedness are necessary properties, but are not by themselves a full synthesis theorem for an arbitrary complex $P$. For example, $|P(1)|=1$ in this convention, so a constant complex top-left response $P=1/2$ is impossible. A **real component** equal to $1/2$ can be realized with $d=0$ by choosing $\phi_0=\pi/3$. Distinguish the whole complex response from the target component; use the solver's admissibility checks for synthesis.

## Check your understanding

1. For degree one and phases $(\pi/4,\pi/4)$, find $P(1/2)$ and its real and imaginary parts.
2. Why is $P$ bounded by one in magnitude?
3. Derive $P$ for degree two with all phases zero.

> [!answer]- Check after trying
> 1. $i/2$, with real part $0$ and imaginary part $1/2$.
> 2. $U$ is unitary; each normalized column has squared entry magnitudes summing to one.
> 3. The two contributions are $x^2$ and $-(1-x^2)$, yielding $2x^2-1$.

Next: [[07 - Why QSP Matters and Core Targets]].
