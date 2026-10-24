# 00 — What the Project Asks

Prerequisites: none. Return to [[Learning Path]].

## Start with a familiar idea

Suppose you calculate $1/3$ and save it as $0.33$. The saved value is close, but not exact. A later calculation uses $0.33$, so the storage decision changes its answer. If a calculation uses hundreds of saved numbers, those changes might add together or partly cancel.

This project asks that question for a list of angles. QSP means **quantum signal processing**. For now, think of it as a recipe that takes an input number $x$ and produces a response. Its adjustable settings are phase angles:

$$
\Phi=(\phi_0,\phi_1,\ldots,\phi_d).
$$

There are $d+1$ angles and $d$ signal steps. Later we will see why the response is related to a degree $d$ polynomial. We can calculate the response on an ordinary computer using $2\times2$ matrices.

## Three different questions

1. **Approximation:** can the response made from a full-precision phase list resemble the desired function?
2. **Storage:** how much does that response change after rounding the angles?
3. **Evaluation:** how accurately does our computer calculate either response?

Your main research question is the second. Let $f(x)$ be the desired target, $r_\Phi(x)$ the chosen real or imaginary response, and $r_{\widehat\Phi}(x)$ the response after rounding. At a particular input:

$$
r_{\widehat\Phi}(x)-f(x)
=\underbrace{r_{\widehat\Phi}(x)-r_\Phi(x)}_{\text{phase-storage change}}
+\underbrace{r_\Phi(x)-f(x)}_{\text{baseline residual}}.
$$

The baseline residual includes the polynomial approximation and phase synthesis. We measure it separately. Finite computer arithmetic introduces another layer that must also be checked.

## Worked example

At one input, suppose the target is $0.5000$, the baseline response is $0.4990$, and the rounded response is $0.4988$.

- Baseline residual magnitude: $0.0010$.
- Storage change magnitude: $0.0002$.
- Rounded response's total target error: $0.0012$.

Calling $0.0012$ the storage error would answer the wrong question.

## What you will eventually do

You will evaluate QSP, obtain realistic phase lists from established solvers, round those lists in three ways, measure the changed responses, and analyze how the error depends on degree and bits. The assignment includes cosine/sine and sign/step targets. Better rounding may help, but that is something to measure, not an outcome to assume.

## Check your understanding

1. The target is $0.7$, the baseline is $0.699$, and the rounded response is $0.6995$. What is the storage change? Did rounding improve the total target error?
2. Why would measuring only the rounded response against the target be insufficient?
3. Does this project require a quantum processor?

> [!answer]- Check after trying
> 1. The signed storage change is $+0.0005$, with magnitude $0.0005$. Total target error decreased from $0.001$ to $0.0005$: storage error can accidentally cancel baseline error.
> 2. It combines the pre-existing residual with the change due to rounding.
> 3. No. The assigned study is classical and numerical; it studies an ingredient used in quantum algorithms.

Move on when you can explain these three error sources in your own words. Next: [[01 - Complex Numbers and Phase]].
