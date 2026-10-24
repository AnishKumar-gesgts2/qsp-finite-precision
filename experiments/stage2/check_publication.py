"""Exercise publication with synthetic Python fixtures in a temporary directory.

THIS DOES NOT RUN MATLAB. Temporary responses come from our Python evaluator
and saved Python-port phases. No simulated MATLAB output enters the real library.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import numpy as np
from PIL import Image

from qsp_finite_precision.stage1 import evaluate_qsp
from publish_matlab import publish


ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    watched=[ROOT/"README.md",ROOT/"results/stage2/summary.json"]
    before=[sha(p) for p in watched]
    with tempfile.TemporaryDirectory(prefix="qsp-publication-fixture-") as folder:
        root=Path(folder)
        if not root.resolve().is_relative_to(Path(tempfile.gettempdir()).resolve()) or not root.name.startswith("qsp-publication-fixture-"):
            raise ValueError("Unexpected temporary fixture directory")
        shutil.copy2(ROOT/"README.md",root/"README.md")
        shutil.copytree(ROOT/"data/phases",root/"data/phases")
        shutil.copytree(ROOT/"results/stage1",root/"results/stage1")
        shutil.copytree(ROOT/"results/stage2",root/"results/stage2")
        request=json.loads((root/"results/stage2/matlab_input.json").read_text())
        report=dict(runtime="MATLAB",runtime_version="TEST FIXTURE ONLY - MATLAB NOT EXECUTED",
                    source_revision=request["source_revision"],source_hashes=request["expected_source_hashes"],
                    input_sha256=sha(root/"results/stage2/matlab_input.json"),cases=[],convention_cases=[])
        for entry in request["cases"]:
            case=json.loads((root/f"data/phases/stage2/{entry['case_id']}.json").read_text())
            # Existing Python QSPPACK phases supply a known-good synthetic input.
            phases=case["python_qsppack"]["phases"]
            _,audit=evaluate_qsp(phases,entry["audit_x"])
            _,curve=evaluate_qsp(phases,entry["validation_x"])
            report["cases"].append(dict(case_id=entry["case_id"],full_phases=phases,
                audit_x=entry["audit_x"],response=audit.real.tolist(),validation_x=entry["validation_x"],
                validation_response=curve.real.tolist(),solver_value=case["python_qsppack"]["residual"],
                iterations=case["python_qsppack"]["iterations"],targetPre=True,typePhi="full",solver_seconds=0.))
        original=json.loads((root/"results/stage1/solver_comparisons.json").read_text())
        examples={e["name"]:e for e in original["examples"]}
        for entry in request["convention_cases"]:
            check=next(c for c in examples[entry["name"]]["qsppack_checks"]
                       if c["typePhi"]=="full" and c["targetPre"]==entry["targetPre"])
            _,P=evaluate_qsp(check["phases"],entry["x"])
            report["convention_cases"].append(dict(case_id=entry["case_id"],full_phases=check["phases"],
                x=entry["x"],response=(P.real if entry["targetPre"] else P.imag).tolist(),
                solver_value=check["solver_value"],iterations=check["iterations"],
                targetPre=entry["targetPre"],typePhi="full"))
        fixture=root/"results/stage2/matlab_output.json"
        fixture.write_text(json.dumps(report),encoding="utf-8")
        checked=publish(root,fixture)
        graphs=list((root/"figures").rglob("*.png"))
        if len(graphs)!=26:raise AssertionError(f"Expected 26 comparison graphs, got {len(graphs)}")
        for graph in graphs:
            with Image.open(graph) as picture:picture.verify()
        rows=np.genfromtxt(root/"results/stage2/matlab_summary.csv",delimiter=",",names=True)
        if len(rows)!=21:raise AssertionError("Wrong CSV case count")
        if len(list((root/"data/phases/stage2_matlab").glob("*.json")))!=21:
            raise AssertionError("Wrong phase-archive count")
        if len(checked["convention_cases"])!=8:raise AssertionError("Wrong convention coverage")
    if [sha(p) for p in watched]!=before:
        raise AssertionError("Fixture test changed the real README or manifest")
    result=dict(passed=True,recorded_at_utc=datetime.now(timezone.utc).isoformat(),
                scope="Publication code smoke test using temporary synthetic Python fixtures; MATLAB NOT EXECUTED",
                matlab_executed=False,temporary_core_cases=21,temporary_convention_cases=8,
                temporary_graphs_verified=26,temporary_phase_archives=21,
                real_library_and_readme_unchanged=True,temporary_fixture_outputs_removed=True)
    path=ROOT/"results/stage2/publication_code_test.json"
    path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
