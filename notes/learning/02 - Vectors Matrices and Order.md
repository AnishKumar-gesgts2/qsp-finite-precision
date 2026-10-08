# 02 — Vectors, Matrices, and Order

Prerequisites: [[01 - Complex Numbers and Phase]].

## A vector stores components

A two-component vector is a column:

$$
v=\begin{pmatrix}a\\b\end{pmatrix},\qquad
\|v\|_2=\sqrt{|a|^2+|b|^2}.
$$

A matrix tells us how to mix those components:

$$
\begin{pmatrix}p&q\\r&s\end{pmatrix}
\begin{pmatrix}a\\b\end{pmatrix}
=\begin{pmatrix}pa+qb\\ra+sb\end{pmatrix}.
$$

The identity matrix $I$ leaves a vector unchanged. Matrix multiplication represents applying transformations in sequence. In $ABv$, apply $B$ to the state first, then $A$.

## Worked example: order matters

Use

$$
X=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
Z=\begin{pmatrix}1&0\\0&-1\end{pmatrix},\qquad
v=\begin{pmatrix}1\\0\end{pmatrix}.
$$

$X$ swaps components; $Z$ changes the sign of the second component. Therefore

$$
XZv=\begin{pmatrix}0\\1\end{pmatrix},\qquad
ZXv=\begin{pmatrix}0\\-1\end{pmatrix}.
$$

In fact $XZ=-ZX$. We cannot reorder a matrix product as if it were a product of ordinary numbers. Reordering QSP factors changes the computation.

## Conjugate transpose and unitary matrices

$A^\dagger$ means transpose $A$ and conjugate its entries. If

$$
A=\begin{pmatrix}a&b\\c&d\end{pmatrix},
\quad A^\dagger=\begin{pmatrix}a^*&c^*\\b^*&d^*\end{pmatrix}.
$$

A unitary matrix satisfies $U^\dagger U=I$. It preserves vector lengths:

$$
\|Uv\|_2^2=v^\dagger U^\dagger Uv=v^\dagger v=\|v\|_2^2.
$$

This is why unitary matrices are useful for quantum states: a normalized state remains normalized. A product of unitary matrices is also unitary, since $(AB)^\dagger=B^\dagger A^\dagger$.

## Check your understanding

1. Find $X^2$ and $Z^2$.
2. Is a diagonal matrix with entries $e^{i\phi}$ and $e^{-i\phi}$ unitary? Explain with its conjugate transpose.
3. In $D_0WD_1v$, which factor acts on $v$ first? In code that constructs the written product from left to right, which side should receive each new factor?

> [!answer]- Check after trying
> 1. Both equal $I$.
> 2. Yes. Multiplying by its conjugate transpose yields diagonal entries $1,1$.
> 3. $D_1$ acts first on the state. To construct the written matrix product, append factors on the right: first $D_0$, then $D_0W$, then $D_0WD_1$.

Project connection: matrix construction order and state-action order are related but different descriptions. Keep both straight when implementing the evaluator. Next: [[03 - Qubits and Rotations]].
