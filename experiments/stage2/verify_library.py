"""Verify hashes and reconstruct every saved baseline without re-running synthesis."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from qsp_finite_precision.stage1 import evaluate_qsp
from qsp_finite_precision.stage2 import load_case
from qsp_finite_precision.stage2.targets import application_mask, target_values


def verify(root):
    root=Path(root)
    manifest=json.loads((root/"results/stage2/summary.json").read_text())
    verified=[]
    for entry in manifest["cases"]:
        path=root/entry["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest()!=entry["sha256"]:
            raise ValueError(f"Archive hash mismatch: {entry['case_id']}")
        case=load_case(path)
        for rel,digest in case["artifact_sha256"].items():
            if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=digest:
                raise ValueError(f"Artifact hash mismatch: {rel}")
        curve=np.genfromtxt(root/f"results/stage2/{entry['case_id']}_response.csv",delimiter=",",names=True)
        x=curve["x"]
        _,P=evaluate_qsp(case["full_phases"],x)
        target=case["target"]
        p=np.polynomial.chebyshev.chebval(x,target["coefficients"])
        f=target_values(target,x)
        mask=application_mask(target,x)
        if not np.array_equal(mask,curve["application_mask"].astype(bool)):
            raise ValueError("Application mask mismatch")
        for key,expected in [("readout",P.imag),("amplitude_real",P.real),("polynomial",p),("target",f)]:
            np.testing.assert_allclose(curve[key],expected,atol=1e-15,rtol=0,err_msg=f"{entry['case_id']}: {key}")
        for key,values in [("approximation",(p-f)[mask]),("synthesis",P.imag-p),("baseline_application",(P.imag-f)[mask])]:
            expected=case["metrics"][key]
            actual=dict(max_abs=float(np.max(np.abs(values))),rmse=float(np.sqrt(np.mean(np.abs(values)**2))))
            for metric in actual:
                if not np.isclose(actual[metric],expected[metric],rtol=1e-12,atol=1e-30):
                    raise ValueError(f"Metric mismatch: {entry['case_id']} {key} {metric}")
        verified.append(dict(case_id=entry["case_id"],phase_count=len(case["full_phases"]),validation_points=int(x.size)))
    return dict(passed=True,verified_cases=len(verified),full_precision_phases=sum(c["phase_count"] for c in verified),
                checks="archive and artifact SHA256; full phase counts; saved-response reconstruction; target/domain and metric consistency",cases=verified)


if __name__=="__main__":
    result=verify(Path(__file__).resolve().parents[2])
    print(json.dumps(result,indent=2))
