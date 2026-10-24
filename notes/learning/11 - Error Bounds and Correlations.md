# 11 — Error Bounds and Correlations

Prerequisites: [[04 - Norms and Measuring Error]], [[10 - Bits Grids and Rounding]].

## One phase, then many phases

Lesson 01 gives the exact size of a changed phase factor:

$$
\Vert D(\phi+\delta)-D(\phi)\Vert_2
=2|\sin(\delta/2)|\le|\delta|.
$$

For two factors, insert and subtract a mixed product:

$$
\widehat A\widehat B-AB
=(\widehat A-A)\widehat B+A(\widehat B-B).
$$

If the surrounding factors are unitary, they do not increase the operator norm. Applying the triangle inequality and repeating this replacement one phase at a time gives

$$
\Vert U_{\Phi+\delta\Phi}(x)-U_\Phi(x)\Vert_2
\le\sum_{j=0}^d2|\sin(\delta\phi_j/2)|
\le\sum_{j=0}^d|\delta\phi_j|.
$$

For direct nearest rounding, every error is at most $h/2$, so the bound is $(d+1)h/2$. This is a guarantee for all inputs, not a prediction that every case grows at that rate. The difference of two unitaries is also at most $2$, so linear growth cannot continue without limit.

## Endpoints simplify the whole circuit

At $x=1$, $W=I$. All phase factors commute and combine. Write $S=\sum_j\phi_j$ and $E=\sum_j\delta\phi_j$. Then

$$
U_\Phi(1)=D(S),\qquad
\Vert U_{\Phi+\delta\Phi}(1)-U_\Phi(1)\Vert_2
=2|\sin(E/2)|.
$$

At $x=-1$, $W=-I$ adds the factor $(-1)^d$ to both matrices, so the same norm formula holds. For $|E|\ll1$, endpoint error is approximately $|E|$.

## Worked comparison

For the three identical toy phases in Lesson 10, direct error is $E=-0.12$. The endpoint unitary error is $2|\sin(0.06)|\approx0.11993$. The nearest-rounding bound is $3(0.05)=0.15$.

If the errors were instead $(-0.04,+0.04,0)$, the endpoint error would vanish. Interior error need not vanish: different phases have different influence away from the endpoints.

## Where the square root comes from

Let $n=d+1$. In a hypothetical model of independent uniform errors on $[-h/2,h/2]$, each has mean zero and variance $h^2/12$. Variances add:

$$
\mathbb E[E^2]=\frac{nh^2}{12},\qquad
\sqrt{\mathbb E[E^2]}=h\sqrt{n/12}.
$$

This gives the small-error endpoint RMS scale. It is a reference model, not a theorem about deterministic solver-phase rounding or the maximum over an input grid. For correlated errors,

$$
\mathrm{Var}\left(\sum_j\delta\phi_j\right)
=\sum_j\mathrm{Var}(\delta\phi_j)
+2\sum_{j<k}\mathrm{Cov}(\delta\phi_j,\delta\phi_k).
$$

Positive covariance can make the sum grow much faster. Repeated phases give an intuitive mechanism for correlated deterministic errors. A plateau can also lie exactly on-grid and produce zero error, so inspect the errors themselves.

## Check your understanding

1. Why is a sum bound valid even though QSP matrices generally do not commute?
2. Why is “error must grow linearly with degree” too strong?
3. Can a vanishing endpoint error prove that the rounded circuit is correct everywhere?

> [!answer]- Check after trying
> 1. The telescoping proof preserves order and uses norm invariance under surrounding unitary factors; it does not reorder them.
> 2. The bound is worst-case. Cancellation, changing phase families, readout choice, and saturation can change observed growth.
> 3. No. The endpoints only probe the total phase error.

Next: [[12 - Sigma Delta and Sensitivity]].
