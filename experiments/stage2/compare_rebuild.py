"""Compare a separately regenerated Stage 2 library with the reference library.

This checks numerical reproduction, not byte-identical timings or images. Run
the documented clean-clone regeneration first; this script does not install
dependencies or establish how the comparison directory was created.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

from qsp_finite_precision.stage2 import load_case
from verify_library import verify


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def revision(root):
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()


def compare(reference, rebuilt):
    reference, rebuilt = Path(reference), Path(rebuilt)
    if reference.resolve() == rebuilt.resolve():
        raise ValueError("Use a separate regenerated directory")
    left = json.loads((reference / "results/stage2/summary.json").read_text())
    right = json.loads((rebuilt / "results/stage2/summary.json").read_text())
    for key in ("versions", "config_sha256", "assignment_sha256", "science_source_sha256"):
        if left[key] != right[key]:
            raise ValueError(f"Rebuild configuration/source mismatch: {key}")
    for root, manifest in ((reference, left), (rebuilt, right)):
        for name, digest in manifest["science_source_sha256"].items():
            if sha(root / name) != digest:
                raise ValueError(f"Scientific source has changed: {name}")
        if not manifest["python_validation_passed"] or manifest["failures"]:
            raise ValueError("A library reports failed generation")
        if manifest["successful_cases"] != manifest["configured_cases"]:
            raise ValueError("A library is incomplete")
        verify(root)
    expected = {entry["case_id"] for entry in left["cases"]}
    if {entry["case_id"] for entry in right["cases"]} != expected:
        raise ValueError("Different case coverage")
    tolerance = 1e-12
    cases = []
    for ident in sorted(expected):
        a = load_case(reference / f"data/phases/stage2/{ident}.json")
        b = load_case(rebuilt / f"data/phases/stage2/{ident}.json")
        if a["target"] != b["target"]:
            raise ValueError(f"Target metadata differs: {ident}")
        phases = float(np.max(np.abs(np.array(a["full_phases"]) - b["full_phases"])))
        crosscheck = float(np.max(np.abs(np.array(a["python_qsppack"]["phases"]) - b["python_qsppack"]["phases"])))
        curves = []
        for root in (reference, rebuilt):
            curves.append(np.genfromtxt(root / f"results/stage2/{ident}_response.csv", delimiter=",", names=True))
        if not np.array_equal(curves[0]["x"], curves[1]["x"]):
            raise ValueError(f"Different response grids: {ident}")
        difference = max(float(np.max(np.abs(curves[0][key] - curves[1][key])))
                         for key in ("target", "polynomial", "readout", "amplitude_real", "qsppack_readout"))
        if max(phases, crosscheck, difference) > tolerance:
            raise ValueError(f"Numerical rebuild differs beyond {tolerance}: {ident}")
        if not (rebuilt / f"figures/stage2/{ident}.png").is_file():
            raise ValueError(f"Missing rebuilt graph: {ident}")
        cases.append(dict(case_id=ident,pyqsp_phase_max_difference=phases,
                          python_qsppack_phase_max_difference=crosscheck,curve_max_difference=difference))
    return dict(passed=True,recorded_at_utc=datetime.now(timezone.utc).isoformat(),
                reference_revision=revision(reference),rebuilt_revision=revision(rebuilt),
                scope="Separate directory, pinned environment, same computer; numerical comparison, not cross-platform proof",
                compared_cases=len(cases),versions=right["versions"],
                science_source_sha256=right["science_source_sha256"],
                rebuilt_manifest_sha256=sha(rebuilt / "results/stage2/summary.json"),
                comparison_tolerance=tolerance,
                max_pyqsp_phase_difference=max(c["pyqsp_phase_max_difference"] for c in cases),
                max_python_qsppack_phase_difference=max(c["python_qsppack_phase_max_difference"] for c in cases),
                max_curve_difference=max(c["curve_max_difference"] for c in cases),
                rebuilt_aggregate=right["aggregate"],cases=cases)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rebuilt", type=Path)
    parser.add_argument("--reference", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compare(args.reference, args.rebuilt)
    encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded)
