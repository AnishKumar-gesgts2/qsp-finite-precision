# 13 — Designing and Interpreting Experiments

Prerequisites: [[09 - Solvers Conventions and Phase Libraries]] through [[12 - Sigma Delta and Sensitivity]].

## A fair comparison changes one thing

For a given target and degree, hold the baseline phase list, input grid, target readout, and domain fixed. Change only the grid precision and quantization scheme. Measure rounded-versus-baseline circuit error separately from baseline-versus-target residual.

The core study crosses both target families, degrees of about 10–500, bits $12,16,20,24,28,32$, and all three schemes. Add a direct 21-bit evaluation for the specific practical check; do not infer it solely by interpolating 20- and 24-bit measurements. Record failures and excluded cells with reasons.

## What to measure

Use at least $10d+1$ Chebyshev points, including both endpoints. For full-unitary, complex-amplitude, and target-readout error, record sampled maxima over the full interval and the relevant application domain. Also record the maximizing input, endpoint errors, and interior maxima. Compare endpoint calculations to their exact sum formulas.

Refine grids around large errors in representative cases and call grid maxima “sampled maxima” unless a continuous maximum is certified. Spot-check high-degree or tiny-error cases at 30 or more digits using a higher-precision evaluator. Distinguish error from storing the baseline phases from error introduced by later quantization; increased evaluation precision cannot recover digits already missing from the baseline file.

## Correlations need more than one statistic

For an error sequence $\delta_j$, record its mean, raw partial sums, and the centered autocorrelation. One explicit definition for lag $k$ is

$$
\rho(k)=\frac{\sum_{j=0}^{n-k-1}(\delta_j-\bar\delta)(\delta_{j+k}-\bar\delta)}
{\sum_{j=0}^{n-1}(\delta_j-\bar\delta)^2},\qquad n=d+1.
$$

State this normalization. If the denominator is zero, report the centered statistic as undefined. A constant nonzero error sequence has perfect coherent accumulation but zero centered variance: autocorrelation alone cannot capture its effect. Connect phase plots to actual errors, sums, and sensitivities.

## Scaling fits are descriptions

If $E(d)\approx C(d+1)^\alpha$, then $\log E\approx\log C+\alpha\log(d+1)$. Fit a stated range, inspect the points and residuals, and compare with the linear and square-root reference slopes from Lesson 11.

Do not log zero values, include a numerical floor in a meaningful power-law fit, or mistake saturation at error $2$ for a scaling law. If target parameters change with degree, say so: a slope over different targets is not purely a fixed-target degree dependence. Define whether you hold parameters fixed or compare a controlled accuracy-matched family. Check how conclusions change with the fit range; a slope is not proof of the mechanism.

## A precision budget you can derive

For direct rounding, a sufficient worst-case full-unitary guarantee is

$$
(d+1)\frac{\pi}{2^b}\le\epsilon,
\qquad
b\ge\left\lceil\log_2\left(\frac{(d+1)\pi}{\epsilon}\right)\right\rceil.
$$

For $d=100$ and $\epsilon=10^{-4}$, this bound requires $22$ bits. At 21 bits, it guarantees this accuracy up to $d=65$. Failure of this bound above that degree is **not** proof that an actual phase list fails. Measure the empirical threshold per target, scheme, domain, and metric. Sigma-delta has a different endpoint guarantee, and no identical all-input guarantee follows from it.

## Tie results to the five assigned questions

1. How does error scale with degree?
2. Which phase/error structures predict the observed behavior?
3. Are the largest errors at endpoints or in the interior?
4. How much do the alternative schemes help, and does sensitivity variation explain it?
5. How many bits meet $10^{-4},10^{-6},10^{-8}$, including the direct 21-bit check?

The report needs supported answers, including unsuccessful cases and limitations. Favorable endpoint behavior alone is not a result about the whole circuit or an entire quantum algorithm.

## Check your understanding

1. A log-log plot gives slope $0.95$. Does that prove rounding errors are correlated?
2. At $d=100$, a 21-bit direct-rounding case measures error $3\times10^{-5}$. Does this contradict the worst-case bound?
3. What should you do if raising evaluation precision changes the smallest reported errors substantially?

> [!answer]- Check after trying
> 1. No. Examine actual sequences, sums, target changes, and sensitivity profiles; alternative explanations remain.
> 2. No. A bound is an upper guarantee, not a lower prediction. That case can perform better.
> 3. Identify evaluation error, recompute affected cells or report the numerical limitation, and avoid fitting the unreliable region.

You are ready to discuss the experimental design when you can explain each metric and predict what each control would reveal. Return to [[Learning Path]] and [[Learning Progress]].
