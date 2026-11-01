"""Plot representative saved phase lists without synthesis or quantization.

Run from the repository root: python experiments/stage2/plot_phase_structure.py
"""

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

from build_library import COLORS, save_figure, style


ROOT = Path(__file__).resolve().parents[2]
SELECTION = {
    "cosine": (10, 80, 500),
    "sine": (11, 81, 499),
    "sign": (11, 81, 499),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT / "results/stage2/summary.json").read_text())
    archives = {entry["case_id"]: entry for entry in manifest["cases"]}
    figures = ROOT / "figures/stage2/phase_structure"
    results = ROOT / "results/stage2/phase_structure"
    figures.mkdir(parents=True, exist_ok=True)
    results.mkdir(parents=True, exist_ok=True)
    records, points = [], []

    for family, degrees in SELECTION.items():
        selected = []
        for degree in degrees:
            case_id = f"{family}_d{degree:04d}"
            entry = archives[case_id]
            path = ROOT / entry["file"]
            if digest(path) != entry["sha256"]:
                raise ValueError(f"Archive hash mismatch: {case_id}")
            case = json.loads(path.read_text())
            phases = np.asarray(case["full_phases"], dtype=float)
            if phases.shape != (degree + 1,) or not np.all(np.isfinite(phases)):
                raise ValueError(f"Invalid phase list: {case_id}")
            if case["target"]["degree"] != degree or case["target"]["family"] != family:
                raise ValueError(f"Wrong target identity: {case_id}")
            if case["convention"]["quantized"] or case["convention"]["wrapped"]:
                raise ValueError(f"Expected unwrapped, unquantized phases: {case_id}")
            selected.append((case, phases, entry))

        # A shared full-sequence scale makes peak heights comparable within a family.
        extent = max(float(np.max(np.abs(p))) for _, p, _ in selected) * 1.10
        fig, axes = plt.subplots(3, 2, figsize=(12, 10), layout="constrained")
        for row, (case, phases, entry) in enumerate(selected):
            degree = case["target"]["degree"]
            case_id = case["case_id"]
            indices = np.arange(phases.size)
            # This window is fixed before inspecting values, not chosen to find a plateau.
            zoom_count = max(3, int(np.ceil(0.20 * phases.size)))
            left, right = axes[row]
            left.plot(indices, phases, color=COLORS[family], lw=1.1, marker=".", ms=2.8)
            left.axvspan(0, zoom_count - 1, color=COLORS[family], alpha=.10, lw=0)
            left.set(xlim=(0, degree), ylim=(-extent, extent),
                     title=f"Degree {degree}: full sequence ({phases.size} phases)")
            right.plot(indices[:zoom_count], phases[:zoom_count], color=COLORS[family],
                       lw=1.1, marker=".", ms=4)
            right.set(xlim=(0, zoom_count - 1),
                      title=f"Same data: indices 0-{zoom_count - 1}, vertical scale adjusted")
            right.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2), useMathText=True)
            for ax in (left, right):
                ax.set(xlabel="Phase index j", ylabel="Phase angle (radians)")
                ax.xaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
                style(ax)
            parameters = case["target"]["parameters"]
            parameter = (f"tau = {parameters['tau']:.5g}" if family != "sign"
                         else f"gap = {parameters['gap']:.5g}, delta = {parameters['delta']:.5g}")
            left.text(.02, .94, parameter, transform=left.transAxes, va="top", fontsize=9,
                      bbox=dict(facecolor="white", edgecolor="none", alpha=.85))

            threshold = case["phase_structure"]["adjacent_threshold_radians"]
            flags = np.abs(np.diff(phases)) <= threshold
            longest = run = 1
            for flag in flags:
                run = run + 1 if flag else 1
                longest = max(longest, run)
            if longest != case["phase_structure"]["longest_nearly_equal_run"]:
                raise ValueError(f"Phase-structure mismatch: {case_id}")
            records.append(dict(
                case_id=case_id, family=family, degree=degree, phase_count=int(phases.size),
                archive=entry["file"], archive_sha256=entry["sha256"], parameters=parameters,
                zoom_start_index=0, zoom_end_index=zoom_count - 1,
                zoom_phase_min=float(phases[:zoom_count].min()),
                zoom_phase_max=float(phases[:zoom_count].max()),
                adjacent_threshold_radians=threshold,
                longest_adjacent_run_phases=longest,
                interpretation="Adjacent-pair threshold only; not a rounding-error measurement.",
            ))
            points.extend(dict(case_id=case_id, phase_index=int(j), phase_radians=float(phi),
                               in_zoom=bool(j < zoom_count)) for j, phi in enumerate(phases))

        fig.suptitle(f"{family.title()}: phase angles at low, middle, and high degree", fontsize=16)
        fig.supxlabel("Left: shared angle scale; shaded window appears at right. Right: first ~20% (at least 3 phases).\n"
                      "Unrounded saved angles. A visually flat segment is not proof of equal phases or correlated rounding.",
                      fontsize=10)
        save_figure(fig, figures / f"{family}.png", dpi=180)
        plt.close(fig)

    with (results / "phase_points.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(points[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(points)
    report = dict(
        source="Saved Stage 2 pyqsp full phases; no phase synthesis or quantization performed.",
        selection="Low, middle (fourth of seven), and high degree in each saved family.",
        zoom_rule="First ceil(20% of phase count), at least 3 phases; independently scaled y axis.",
        full_scale="Common symmetric y limits within each family; actual integer phase indices.",
        script_sha256=digest(Path(__file__)),
        cases=records,
        plotted_phase_values=len(points),
        figures={str(p.relative_to(ROOT)).replace("\\", "/"): digest(p)
                 for p in sorted(figures.glob("*.png"))},
        points_sha256=digest(results / "phase_points.csv"),
        limits="Descriptive phase structure only. Correlated rounding, sensitivity, and error scaling remain later measurements.",
    )
    (results / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Plotted {len(records)} verified phase lists ({len(points)} exact saved phase values) in 3 figures.")
    print("Longest adjacent runs at the archived 1e-8-radian threshold:")
    for record in records:
        print(f"  {record['case_id']}: {record['longest_adjacent_run_phases']} phase(s)")


if __name__ == "__main__":
    main()
