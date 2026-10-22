# src

Research code lives in `qsp_finite_precision/`, separated by stage.

- [Stage 1: forward evaluator](qsp_finite_precision/stage1/README.md) — Part A implemented; Part B pending.
- Stages 2–5 will get their own `stage2/` through `stage5/` packages as implemented. See the [stage map](../README.md#stage-map).

Later stages should import the Stage 1 evaluator rather than copy it. Dependencies and installation are defined in the root `pyproject.toml`.
