# 03 — Qubits and Rotations

Prerequisites: [[02 - Vectors Matrices and Order]].

## A qubit is a normalized two-component state

The basis states are

$$
|0\rangle=\begin{pmatrix}1\cr 0\end{pmatrix},\qquad
|1\rangle=\begin{pmatrix}0\cr 1\end{pmatrix}.
$$

A general state is $|\psi\rangle=a|0\rangle+b|1\rangle$, with $|a|^2+|b|^2=1$. A computational-basis measurement gives $0$ with probability $|a|^2$ and $1$ with probability $|b|^2$. The amplitudes $a,b$ contain phase information that matters before measurement.

$\langle0|$ is the conjugate transpose of $|0\rangle$. Thus $\langle0|U|0\rangle$ selects the top-left entry of $U$.

## The phase rotation

Using the Pauli $Z$ matrix from Lesson 02, define

$$
D(\phi)=e^{i\phi Z}
=\begin{pmatrix}e^{i\phi}&0\cr 0&e^{-i\phi}\end{pmatrix}.
$$

It gives opposite phases to the two components. This follows either from diagonal exponentiation or from expanding the exponential series and using $Z^2=I$.

**Angle convention:** many circuit libraries define $R_z(\theta)=e^{-i\theta Z/2}$. In those libraries our $D(\phi)$ is $R_z(-2\phi)$. An angle named “rotation” is not enough to identify its convention.

## The signal rotation

Set $x=\cos\theta$, with $\theta=\arccos x$ for $x\in[-1,1]$. Since $X^2=I$, the even and odd terms of the exponential series give

$$
W(x)=e^{i\theta X}=\cos\theta\thinspace I+i\sin\theta\thinspace X
=\begin{pmatrix}x&i\sqrt{1-x^2}\cr i\sqrt{1-x^2}&x\end{pmatrix}.
$$

The input $x$ controls this rotation. The adjustable phases control $D$. Both are unitary. QSP alternates these two kinds of transformation.

## Worked example

At $x=1/2$, $\sqrt{1-x^2}=\sqrt3/2$. Applying $W$ to $|0\rangle$ gives

$$
W(1/2)|0\rangle=\tfrac12|0\rangle+i\tfrac{\sqrt3}{2}|1\rangle.
$$

The measurement probabilities are $1/4$ and $3/4$. Their sum is one. The imaginary factor is an amplitude phase, not a negative or imaginary probability.

## Check your understanding

1. Calculate $W(1)$, $W(-1)$, and $W(0)$.
2. What is $D(\phi)|0\rangle$? Does this alone change the probability of measuring $0$?
3. Why can $D$ still affect a circuit when it does not change the component magnitudes by itself?

> [!answer]- Check after trying
> 1. $I$, $-I$, and $iX$.
> 2. $e^{i\phi}|0\rangle$; the probability stays one.
> 3. Relative phases affect interference when a later matrix mixes the components.

Next: [[04 - Norms and Measuring Error]].
