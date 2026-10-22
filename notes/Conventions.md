# Conventions

Status: Part A uses the $W_x$ signal / $Z$ phase convention and returns the complex upper-left matrix entry. The exact definitions and product order are in the [Stage 1 README](../src/qsp_finite_precision/stage1/README.md). Solver mappings and the complete one-page convention note remain pending for Part B.

Record the signal rotation, phase rotation, multiplication order, phase indexing, target readout, and mappings to pyqsp and QSPPACK. Verify mappings against each solver's own response before using its phases.

Keep solver residuals separate from phase-storage error. Record the bit-grid interval, step, wrap behavior, and rounding tie rule before quantization.
