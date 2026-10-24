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

The [rebuild comparison](../rebuild_comparison.json) additionally compares regenerated results with the reference library: all scientific source identities and package versions agree, and maximum phase/curve differences are zero across 21 cases. The captured source/algorithm revision remains explicit even when later documentation or MATLAB preparation changes are added.

The test ran on the same Windows computer as the reference run. Source line endings are fixed by `.gitattributes`. Logs are normalized to LF for archiving; numerical values are preserved. Timings and plot bytes need not be identical. Original MATLAB execution and supervisor approval remain separate, pending checks.
