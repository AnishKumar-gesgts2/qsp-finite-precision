# Captured clean-regeneration checks

These logs were captured from a separate Git clone at revision `9a4ff6e0661923f472aa7cc3dfebfdf55ea9c385`, with a newly created Python 3.11.9 environment and packages installed from the pinned lock. Every command exited successfully. Stage 2 was generated without `--resume`.

| Log | Command / evidence |
| --- | --- |
| [dependency-check.log](dependency-check.log) | `python -m pip check` |
| [stage1-tests.log](stage1-tests.log) | `python -m unittest discover -s tests/stage1 -v` — 12 tests pass |
| [stage2-tests.log](stage2-tests.log) | `python -m unittest discover -s tests/stage2 -v` — 9 tests pass |
| [stage1-identities.log](stage1-identities.log) | `python experiments/stage1/check_identities.py` — 104 checks pass |
| [stage1-rebuild.log](stage1-rebuild.log) | `python experiments/stage1/compare_solvers.py` — reproduces the reference comparisons/graphs |
| [stage2-rebuild.log](stage2-rebuild.log) | `python experiments/stage2/build_library.py` — generates all 21 cases and graphs |
| [stage2-reload.log](stage2-reload.log) | `python experiments/stage2/verify_library.py` — checks hashes, phases, curves, domains, and metrics |
| [matlab-verifier-tests.log](matlab-verifier-tests.log) | Current Stage 2 suite after adding rejection of stale MATLAB input reports — 9 tests pass; no MATLAB execution is implied |
| [current-stage1-tests.log](current-stage1-tests.log) | Stage 1 suite at the 2026-10-24 closeout — 12 tests pass |
| [current-stage2-tests.log](current-stage2-tests.log) | Stage 2 suite at the 2026-10-24 closeout — 10 tests pass, including full-grid report consistency/rejection fixtures; no MATLAB execution is implied |

The [rebuild comparison](../rebuild_comparison.json) additionally compares regenerated results with the reference library: all scientific source identities and package versions agree, and maximum phase/curve differences are zero across 21 cases. The captured source/algorithm revision remains explicit even when later documentation or MATLAB preparation changes are added.

The clean-regeneration test ran on the same Windows computer as the reference run. The two `current-` logs are later closeout checks and do not change the historical tested revision above. Source line endings are fixed by `.gitattributes`; Git stores archived logs as LF, preserving numerical values. Timings and plot bytes need not be identical. The original MATLAB attempt is now [recorded as unable to complete](../matlab_execution_status.json), and supervisor approval remains pending.
