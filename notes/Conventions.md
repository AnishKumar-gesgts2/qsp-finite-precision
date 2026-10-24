# Conventions

Status: checked on 2026-10-23 against **pyqsp 0.2.0** and **Python QSPPACK (`qsppack`) 0.4.0**. MATLAB QSPPACK source was inspected at commit `7bc7b7622e05039e4c2cdda7d5739e99c3752be6`; MATLAB itself was not run. Preserve the planned MATLAB numerical cross-check in Stage 2.

## Circuit and readout

All comparisons use $x\in[-1,1]$, phase angles in radians, and

$$
D(\phi)=\operatorname{diag}(e^{i\phi},e^{-i\phi}),\qquad
W(x)=\begin{pmatrix}x&i\sqrt{1-x^2}\\i\sqrt{1-x^2}&x\end{pmatrix},
$$

$$
U_\Phi(x)=D(\phi_0)W(x)D(\phi_1)\cdots W(x)D(\phi_d),
\qquad P_\Phi(x)=[U_\Phi(x)]_{00}.
$$

A degree-$d$ sequence has $d+1$ phases. The written product is built by appending factors on the right; the rightmost factor acts first on a column state. These are $e^{i\phi Z}$ phases, without a half-angle or minus sign. $P$ is a complex amplitude; $|P|^2$ is a probability.

## Package mapping

| Item | pyqsp `sym_qsp` | Python QSPPACK / MATLAB source convention |
| --- | --- | --- |
| Coefficients | Full Chebyshev array $[c_0,c_1,\ldots]$, zeros in opposite parity | Active parity only: $[c_0,c_2,\ldots]$ or $[c_1,c_3,\ldots]$ |
| Parity | `0` even, `1` odd | Same |
| Phases | Returns `(full, reduced, parity)`; evaluator takes `full` | Request `typePhi='full'`, or expand `reduced` using its metadata |
| Target component | $\operatorname{Im}P$ | $\operatorname{Re}P$ if `targetPre=True`; $\operatorname{Im}P$ otherwise |
| Matrices / written order | Exactly those above in the symmetric branch | Same for the full phase list |

For pyqsp response evaluation, use `signal_operator='Wx', sym_qsp=True` (returns the complex $P$), or explicitly `measurement='z'` without symmetric mode. The ordinary `Wx` response defaults to `measurement='x'`, which computes $\langle+|U|+\rangle$, a different amplitude. The `model` field can still say `x` when symmetric mode overrides the selected amplitude. In version 0.2.0 the symmetric synthesis branch is hardwired to this circuit and `crit=1e-12`; it ignores several generic synthesis options, including `tolerance`.

Reduced symmetric phases run **from the center toward the right endpoint**. For $r=(r_0,r_1,r_2)$, base expansion is

$$
\begin{aligned}
\text{even: }&(r_2,r_1,2r_0,r_1,r_2),\\
\text{odd: }&(r_2,r_1,r_0,r_0,r_1,r_2).
\end{aligned}
$$

For even degree zero, the single full phase is $2r_0$. pyqsp uses this base expansion. QSPPACK additionally adds $\pi/4$ to each endpoint when expanding reduced phases with `targetPre=True`; if the endpoints coincide, both additions apply. A **full** QSPPACK list already includes these offsets. Our `qsppack_full_phases` adapter preserves that convention, so select the real or imaginary part directly afterward.

QSPPACK's `get_entry` / MATLAB `QSPGetEntry` implement the imaginary readout by subtracting $\pi/4$ at both endpoints and taking the real part. This gives $P'=-iP$, hence $\operatorname{Re}P'=\operatorname{Im}P$. Do not apply those evaluation shifts and then select the imaginary part again.

## Evidence and limits

[The comparison report](../results/stage1/solver_comparisons.json) records versions, source hashes, full/reduced phases, coefficients, residuals, tolerances, and convergence information. Three built-in pyqsp generators (cosine degree 6, sine degree 7, smoothed sign degree 15) plus the degree-one $0.5x$ diagnostic were checked on 1,025 inputs each. Maximum pyqsp complex-amplitude and full-unitary differences were zero in this run; largest target-polynomial residual was $1.78\times10^{-15}$. All 16 Python QSPPACK synthesis combinations (four examples, two readouts, two phase representations) passed; maximum mapped response difference was $8.89\times10^{-16}$. The [Stage 1B README](../experiments/stage1/README.md) embeds per-example reference graphs and max/RMSE statistics in original-function units, with generator scaling reversed for display only.

These are sampled binary64 checks, not an all-input proof or a measured accuracy floor. Both packages share algorithmic lineage. The sign example approximates a smooth erf surrogate; it does not establish uniform approximation of discontinuous sign or the Stage 2 gap-domain specification. Generator scaling is recorded, not treated as a certified global bound.

Keep separate: function-to-polynomial approximation; synthesis coefficient residual; evaluated response-to-polynomial residual (which also includes evaluation error); and later rounded-to-original phase-response error. **No phase quantization occurs here.** pyqsp's public return omits solver status, so we independently check the returned phase-to-coefficient residual. QSPPACK's `converged` flag is checked explicitly. Quantization interval, step, wrap behavior, and tie rule remain Stage 3 choices.

## Primary sources

- [pyqsp README](https://github.com/ichuang/pyqsp) and the installed 0.2.0 `angle_sequence.py`, `response.py`, `sym_qsp_opt.py` (hashes in the report).
- [Python QSPPACK workflow](https://qsppack.readthedocs.io/en/latest/getting_started.html), [utility definitions](https://qsppack.readthedocs.io/en/latest/utils.html), and installed 0.4.0 sources.
- MATLAB source at the inspected commit: [QSPGetUnitary](https://github.com/qsppack/QSPPACK/blob/7bc7b7622e05039e4c2cdda7d5739e99c3752be6/Solvers/Optimization/QSPGetUnitary.m), [QSPGetEntry](https://github.com/qsppack/QSPPACK/blob/7bc7b7622e05039e4c2cdda7d5739e99c3752be6/Solvers/Optimization/QSPGetEntry.m), and [reduced-to-full expansion](https://github.com/qsppack/QSPPACK/blob/7bc7b7622e05039e4c2cdda7d5739e99c3752be6/Solvers/Optimization/rdc_phase_factor_to_full.m).
