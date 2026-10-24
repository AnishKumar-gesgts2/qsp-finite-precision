# 07 — Why QSP Matters and Core Targets

Prerequisites: [[06 - QSP by Hand]].

## From a number to a matrix function

An eigenvector $v$ of $A$ satisfies $Av=\lambda v$. For a polynomial $p$, repeated multiplication gives

$$
p(A)v=p(\lambda)v.
$$

For example, if $A=\mathrm{diag}(0.2,-0.5)$ and $p(x)=2x^2-1$, then $p(A)=\mathrm{diag}(-0.92,-0.5)$. A polynomial transforms the eigenvalues while keeping these eigenvectors.

For a Hermitian matrix, $A=V\Lambda V^\dagger$ with unitary $V$. If two scalar functions differ by at most $\epsilon$ on the spectrum, their corresponding matrix functions differ in operator norm by at most $\epsilon$. This is a spectral statement; it does not apply unchanged to arbitrary nonnormal matrices.

## The quantum connection

A block encoding embeds a normalized matrix $A/\alpha$ in part of a larger unitary. Qubitization and related constructions reduce appropriate spectral transformations to small invariant subspaces; QSP shapes the response there. QSVT extends polynomial transformations to singular values, with parity-dependent left/right singular-vector structure. It is not generally the same as simply writing $p(A)$ for a non-Hermitian matrix.

For this project, know why the scalar problem matters. You do not need to implement the full encoding or quantum algorithm. The assigned [Martyn tutorial](https://arxiv.org/abs/2105.02859) introduces these connections; [Lin's notes](https://arxiv.org/abs/2201.08309) provide the mathematical development.

## Core family 1: cosine and sine

Hamiltonian time evolution involves $e^{-i\tau x}=\cos(\tau x)-i\sin(\tau x)$. Cosine is even, sine is odd. The core phase library uses these as separate real targets, with the corresponding degree parity.

The Jacobi–Anger expansions give Chebyshev coefficients:

$$
\cos(\tau x)=J_0(\tau)
+2\sum_{k=1}^{\infty}(-1)^kJ_{2k}(\tau)T_{2k}(x),
$$

$$
\sin(\tau x)=2\sum_{k=0}^{\infty}(-1)^kJ_{2k+1}(\tau)T_{2k+1}(x).
$$

$J_k$ is a Bessel function of the first kind; you can use a library to evaluate it. Truncating these series produces polynomial approximations. Greater oscillation usually needs greater degree for a fixed accuracy. Truncation can overshoot: check boundedness and record any scaling rather than assuming the truncated polynomial stays below one.

## Core family 2: sign or threshold response

A sign target distinguishes positive from negative inputs. A discontinuity cannot be approximated uniformly to arbitrarily small error by a continuous polynomial across the jump. Specify a gap, such as $[-1,-\gamma]\cup[\gamma,1]$, or specify a smooth transition. The assignment scales the sign/step family to a maximum of $0.9$.

Odd sign targets fit odd-parity sequences. A generic step $(1+\mathrm{sign}(x))/2$ mixes even and odd parts, so it does not directly fit a single fixed-parity real response. Record the parity-compatible target construction and verify what the solver actually generates. “Sign” and “step” are application descriptions, not permission to ignore parity.

## Check your understanding

1. Why does a scalar error bound control a Hermitian matrix-function error?
2. Which degree parity is appropriate for cosine? For sine?
3. Why should sign-target errors be recorded both on the full interval and on the application domain?

> [!answer]- Check after trying
> 1. Unitary diagonalization reduces the norm to the largest scalar error at an eigenvalue.
> 2. Even for cosine and odd for sine.
> 3. The application may exclude the transition gap, while full-interval behavior still matters for boundedness and diagnostics. Storage change and target approximation remain separate in either domain.

Next: [[08 - The Forward Evaluator]].
