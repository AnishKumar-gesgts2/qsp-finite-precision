"""Verify an actually produced MATLAB report; never manufacture a runtime result."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from qsp_finite_precision.stage1 import evaluate_qsp
from qsp_finite_precision.stage2 import load_case
from qsp_finite_precision.stage2.targets import validation_grid


def verify_matlab(root, report):
    root=Path(root)
    input_path=root/"results/stage2/matlab_input.json"
    request=json.loads(input_path.read_text())
    if report.get("runtime")!="MATLAB" or not report.get("runtime_version"):
        raise ValueError("Report must identify the actually used MATLAB runtime")
    if report.get("source_revision")!=request["source_revision"] or report.get("source_hashes")!=request["expected_source_hashes"]:
        raise ValueError("Original MATLAB source identity does not match")
    expected={entry["case_id"]:entry for entry in request["cases"]}
    outputs=report["cases"]
    if isinstance(outputs,dict):outputs=[outputs]
    if len(outputs)!=len(expected) or {e["case_id"] for e in outputs}!=set(expected):
        raise ValueError("Missing, duplicated, or unexpected MATLAB cases")
    results=[]
    for output in outputs:
        ident=output["case_id"];entry=expected[ident]
        case=load_case(root/f"data/phases/stage2/{ident}.json")
        phases=np.asarray(output["full_phases"],dtype=float).reshape(-1)
        x=np.asarray(output["audit_x"],dtype=float).reshape(-1)
        response=np.asarray(output["response"],dtype=float).reshape(-1)
        solver_value=output["solver_value"]
        if phases.size!=case["target"]["degree"]+1 or not np.all(np.isfinite(phases)):
            raise ValueError(f"Invalid MATLAB phases: {ident}")
        if output["targetPre"] is not True or output["typePhi"]!="full":
            raise ValueError("Unexpected MATLAB phase/readout convention")
        if not np.array_equal(x,np.asarray(entry["audit_x"])) or response.shape!=x.shape or not np.all(np.isfinite(response)):
            raise ValueError("MATLAB audit inputs/outputs do not match the request")
        if solver_value is None or not np.isfinite(solver_value) or solver_value<0 or solver_value>=request["criteria"]:
            raise ValueError(f"MATLAB synthesis did not converge: {ident}")
        _,P=evaluate_qsp(phases,x)
        agreement=float(np.max(np.abs(P.real-response)))
        grid=validation_grid(case["target"])
        _,baseline=evaluate_qsp(phases,grid)
        polynomial=np.polynomial.chebyshev.chebval(grid,case["target"]["coefficients"])
        residual=float(np.max(np.abs(baseline.real-polynomial)))
        tolerance=case["acceptance"]["evaluator_tolerance"]
        if agreement>tolerance or residual>tolerance:
            raise ValueError(f"MATLAB/local response mismatch: {ident}")
        results.append(dict(case_id=ident,evaluator_difference=agreement,synthesis_residual=residual))
    return dict(passed=True,executed=True,runtime="MATLAB",runtime_version=report["runtime_version"],
                source_revision=report["source_revision"],input_sha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),cases=results)


if __name__=="__main__":
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report",nargs="?",type=Path,default=root/"results/stage2/matlab_output.json")
    args=parser.parse_args()
    result=verify_matlab(root,json.loads(args.report.read_text()))
    (root/"results/stage2/matlab_verification.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
