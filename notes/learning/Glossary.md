# Glossary

Return to [[Learning Path]].

| Symbol or term | Meaning in these lessons |
| --- | --- |
| $i$ | Imaginary unit, $i^2=-1$ |
| $z^{\ast}$, $A^\dagger$ | Complex conjugate; conjugate transpose |
| $\vert z\vert$, $\Vert v\Vert_2$ | Complex magnitude; Euclidean vector length |
| $\Vert A\Vert_2$ | Operator/spectral norm, largest singular value |
| Unitary | Matrix satisfying $U^\dagger U=I$ |
| Hermitian | Matrix satisfying $A^\dagger=A$ |
| Eigenvalue | $\lambda$ with $Av=\lambda v$ for some nonzero $v$ |
| Singular value | Nonnegative square root of an eigenvalue of $A^\dagger A$ |
| $X,Z$ | Pauli matrices: component swap and second-component sign change |
| $\vert 0\rangle,\vert 1\rangle$ | Basis columns $(1,0)^T,(0,1)^T$ |
| Amplitude | A complex state component; squared magnitude gives a basis probability |
| $x$ | Scalar signal input in $[-1,1]$ |
| $\theta$ | Signal angle $\arccos x$ |
| $D(\phi)$ | Phase matrix $e^{i\phi Z}$; differs from common library $R_z$ angle conventions |
| $W(x)$ | Signal matrix $xI+i\sqrt{1-x^2}X$ |
| $d$ | Number of signal steps; polynomial degree is at most $d$ |
| $\Phi$ | Full ordered phase list with $d+1$ entries |
| $U_\Phi(x)$ | Full $2\times2$ QSP unitary |
| $P_\Phi(x)$ | Top-left complex amplitude $\langle0\vert U_\Phi(x)\vert 0\rangle$ |
| $r_\Phi(x)$ | Chosen real or imaginary part carrying a real target |
| $f$, $p_d$ | Desired function; finite-degree polynomial approximation |
| Baseline residual | Difference between unrounded target readout and desired function |
| Storage error | Rounded-versus-baseline response difference |
| $T_k(x)$ | Chebyshev polynomial defined by $T_k(\cos\theta)=\cos(k\theta)$ |
| Parity | Even or odd symmetry under $x\mapsto-x$ |
| Block encoding | Embedding a normalized matrix as a block of a unitary |
| QSP, QSVT | Quantum signal processing; quantum singular value transformation |
| $b$, $h$ | Phase-word bits; grid spacing $2\pi/2^b$ |
| $\widehat\phi_j$ | Quantized phase, with wrapping convention recorded |
| $\delta\phi_j$ | Quantized minus baseline phase, using consistent unwrapped representatives |
| $e_j$ | Sigma-delta carry residual $u_j-\widehat\phi_j$; not the same sign as accumulated phase error |
| $E_k$ | Phase-error partial sum $\sum_{j=0}^k\delta\phi_j$ |
| $g_j(x)$ | Amplitude sensitivity $\partial P_\Phi(x)/\partial\phi_j$ |
| $\mathrm{TV}(g)$ | Sum of adjacent sensitivity differences in magnitude |
| RMS | Root mean square; a statistical scale, not a worst-case bound |
| Autocorrelation | Dependence between sequence entries at a specified index lag |
| Phase plateau | A run of nearly equal phases; possible rounding-correlation mechanism |
| Application domain | Inputs relevant to a chosen target, potentially excluding a gap |
| Sampled maximum | Largest value on a finite evaluation grid, not a certified continuous supremum |
| Round-trip storage | Saving enough decimal digits to reconstruct the same floating-point values |

See [[10 - Bits Grids and Rounding]] for wrapping and [[12 - Sigma Delta and Sensitivity]] for the residual sign convention.
