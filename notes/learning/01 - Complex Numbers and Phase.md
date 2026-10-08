# 01 — Complex Numbers and Phase

Prerequisites: [[00 - What the Project Asks]], ordinary algebra, sine and cosine.

## A number with two coordinates

A complex number is $z=a+ib$, where $i^2=-1$. Think of $(a,b)$ as a point in a plane. Its conjugate is $z^*=a-ib$; its magnitude is its distance from the origin:

$$
|z|=\sqrt{a^2+b^2},\qquad z^*z=|z|^2.
$$

For example, $|3+4i|=5$. A complex number does not have an ordinary real-number order: “positive” is not the right concept for $3+4i$.

## An angle gives a unit complex number

Euler's formula is

$$
e^{i\phi}=\cos\phi+i\sin\phi.
$$

Its magnitude is one because $\cos^2\phi+\sin^2\phi=1$. Multiplying by $e^{i\phi}$ rotates a complex number by angle $\phi$ without changing its magnitude. Angles in this vault are in **radians**: $\pi$ radians is $180^\circ$.

The rules $e^{i\alpha}e^{i\beta}=e^{i(\alpha+\beta)}$ and $(e^{i\phi})^*=e^{-i\phi}$ will simplify many matrix products.

## Worked example

With $\phi=\pi/2$, $e^{i\phi}=i$. Multiplying $1$ by it gives $i$. Multiplying again gives $-1$. Four such multiplications return to $1$. This is rotation, not an increase in size.

To compare nearby phases, factor their difference:

$$
e^{i(\phi+\delta)}-e^{i\phi}
=e^{i\phi}(e^{i\delta}-1).
$$

The first factor has magnitude one. Using the half-angle identity gives

$$
|e^{i(\phi+\delta)}-e^{i\phi}|
=2|\sin(\delta/2)|\le |\delta|.
$$

For a small change, the difference is approximately $|\delta|$. Notice that it depends on the change, not the original angle. This will become the single-phase error bound.

## Relative phase

Two components might have phases $e^{i\phi}$ and $e^{-i\phi}$. Their phase difference is $2\phi$. A shared factor multiplying both components is a global phase; a change in their relative phase can change later interference. Our full-unitary metric compares matrices directly and is not a metric that removes global phase automatically.

## Check your understanding

1. Calculate $e^{i\pi}$ and $e^{-i\pi/2}$.
2. Find the conjugate and squared magnitude of $(1+i)/\sqrt2$.
3. If an angle changes by $0.001$ radians, approximately how much does its unit phase factor change in magnitude of the difference?

> [!answer]- Check after trying
> 1. $-1$ and $-i$.
> 2. Conjugate $(1-i)/\sqrt2$; squared magnitude $1$.
> 3. About $0.001$; the exact difference is $2|\sin(0.0005)|$.

Project connection: rounded angles alter complex phase factors, even though each factor still has magnitude one. Next: [[02 - Vectors Matrices and Order]].
