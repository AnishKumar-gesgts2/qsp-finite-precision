# 05 — Polynomials and Chebyshev

Prerequisites: [[03 - Qubits and Rotations]], basic trigonometry.

## Degree and parity

A polynomial is a finite sum of powers, such as $p(x)=2x^2-1$. Its degree is the highest power with a nonzero coefficient. A function is even if $f(-x)=f(x)$ and odd if $f(-x)=-f(x)$. Here $2x^2-1$ is even, while $4x^3-3x$ is odd.

Parity matters because a standard QSP sequence with $d$ signal steps has response parity $d\bmod2$. A sequence can have degree less than $d$, but its nonzero polynomial powers have that parity.

## Chebyshev polynomials

Define $T_k$ by

$$
T_k(\cos\theta)=\cos(k\theta).
$$

The cosine addition identity gives the recurrence

$$
T_0(x)=1,\quad T_1(x)=x,\quad
T_{k+1}(x)=2xT_k(x)-T_{k-1}(x).
$$

Thus $T_2=2x^2-1$, $T_3=4x^3-3x$, and $T_4=8x^4-8x^2+1$. On $[-1,1]$, each satisfies $|T_k(x)|\le1$.

## Why this basis appears in QSP

With all phase angles zero, the QSP product is $W(x)^d$. Since each signal rotates about the same $X$ axis,

$$
W(x)^d=e^{id\theta X}
=\cos(d\theta)I+i\sin(d\theta)X.
$$

Its top-left entry is $\cos(d\theta)=T_d(x)$. Chebyshev polynomials are built into the simplest QSP circuit.

## Worked example: basis coefficients are different

The polynomial $x^2$ can be written as

$$
x^2=\tfrac12T_0(x)+\tfrac12T_2(x).
$$

Its monomial coefficient list is $[0,0,1]$. Its Chebyshev coefficient list is $[1/2,0,1/2]$. Passing one list into a solver expecting the other changes the requested function.

## A grid that resolves endpoint behavior

An endpoint-including Chebyshev grid with $N$ points is

$$
x_\ell=\cos\left(\frac{\pi\ell}{N-1}\right),\qquad
\ell=0,\ldots,N-1.
$$

It is uniform in $\theta$, not $x$, and places more points near $\pm1$. The assignment calls for at least $10d+1$ sample points. A maximum on that grid is still a sampled maximum; narrow peaks may require refinement. Other Chebyshev grids exist, so record which one you use.

## Check your understanding

1. Derive $T_3$ from the recurrence and state its parity.
2. Find $T_2(1/2)$ in two ways: the polynomial formula and the cosine formula.
3. For $N=5$, list the grid points.

> [!answer]- Check after trying
> 1. $2x(2x^2-1)-x=4x^3-3x$, odd.
> 2. $-1/2$ in both cases; $\arccos(1/2)=\pi/3$.
> 3. $1,\sqrt2/2,0,-\sqrt2/2,-1$.

Project connection: degree, parity, coefficient basis, and evaluation grids are needed before asking a solver for phases. Next: [[06 - QSP by Hand]].
