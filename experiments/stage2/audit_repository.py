"""Audit saved Stage 1-2 evidence and report technical completion truthfully.

This is a local artifact audit. It does not run MATLAB, imply supervisor approval,
or treat prepared MATLAB scripts as executed numerical evidence.
"""

import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
from urllib.parse import unquote
import zipfile

from PIL import Image

from verify_library import verify


ROOT=Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root):
    root=Path(root)
    stage1=json.loads((root/"results/stage1/solver_comparisons.json").read_text())
    if not stage1["passed"] or len(stage1["examples"])!=4:
        raise ValueError("Stage 1 solver examples are incomplete or failing")
    if sum(len(e["qsppack_checks"]) for e in stage1["examples"])!=16:
        raise ValueError("Stage 1 Python QSPPACK mapping coverage is incomplete")
    with (root/"results/stage1/mathematical_checks.csv").open(newline="") as file:identities=list(csv.DictReader(file))
    if len(identities)!=104 or any(r["passed"]!="True" for r in identities):
        raise ValueError("Stage 1 identity checks are incomplete or failing")
    manifest=json.loads((root/"results/stage2/summary.json").read_text())
    for name,expected in manifest["science_source_sha256"].items():
        if digest(root/name)!=expected:raise ValueError(f"Scientific source hash mismatch: {name}")
    for name,key in [("experiments/stage2/build_library.py","builder_sha256"),
                     ("experiments/stage2/config.json","config_sha256"),
                     ("references/QSP_project.docx","assignment_sha256")]:
        if digest(root/name)!=manifest[key]:raise ValueError(f"Recorded source/config hash mismatch: {name}")
    for name,version in manifest["versions"].items():
        if importlib.metadata.version(name)!=version:raise ValueError(f"Package version mismatch: {name}")
    reconstructed=verify(root)
    if reconstructed["verified_cases"]!=21 or reconstructed["full_precision_phases"]!=3421:
        raise ValueError("Core library coverage/phase count is incomplete")
    request=json.loads((root/"results/stage2/matlab_input.json").read_text())
    if len(request["cases"])!=21 or len(request["convention_cases"])!=8:
        raise ValueError("Prepared original MATLAB test coverage is incomplete")
    for entry in request["cases"]:
        case=json.loads((root/f"data/phases/stage2/{entry['case_id']}.json").read_text())
        if len(entry["validation_x"])<10*case["target"]["degree"]+1:
            raise ValueError("Prepared MATLAB validation grid is too small")
    with zipfile.ZipFile(root/"results/stage2/qsp-stage2-matlab.zip") as bundle:
        if bundle.testzip() is not None:raise ValueError("Corrupt MATLAB bundle")
        prefix="qsp-stage2-matlab/"
        bm=json.loads(bundle.read(prefix+"bundle_manifest.json"))
        for name,expected in bm["files"].items():
            if hashlib.sha256(bundle.read(prefix+name)).hexdigest()!=expected:
                raise ValueError(f"Bundle member hash mismatch: {name}")
        if bundle.read(prefix+"matlab_input.json")!=(root/"results/stage2/matlab_input.json").read_bytes():
            raise ValueError("MATLAB bundle contains stale inputs")
        if bundle.read(prefix+"crosscheck_matlab.m")!=(root/"experiments/stage2/crosscheck_matlab.m").read_bytes():
            raise ValueError("MATLAB bundle contains a stale runner")
    images=[root/"figures/stage1/mathematical_checks.png",root/"figures/stage1/solver_comparisons.png",
            root/"figures/stage2/overview.png"]
    images.extend(root/f"figures/stage1/{e['name']}_reference.png" for e in stage1["examples"])
    images.extend(root/f"figures/stage2/{e['case_id']}.png" for e in manifest["cases"])
    matlab_passed=manifest["matlab_qsppack"].get("status")=="passed"
    if matlab_passed:
        images.append(root/"figures/stage2/matlab/overview.png")
        images.extend(root/f"figures/stage2/matlab/{e['case_id']}.png" for e in manifest["cases"])
        images.extend(root/f"figures/stage1/matlab/{e['name']}.png" for e in stage1["examples"])
    for path in images:
        with Image.open(path) as picture:picture.verify()
    broken=[];checked_links=0;mermaid_blocks=0
    markdown=[p for folder in ("notes","src","experiments","data","results") for p in (root/folder).rglob("*.md")]
    markdown.append(root/"README.md")
    for path in markdown:
        content=path.read_text(encoding="utf-8")
        mermaid_blocks+=content.count("```mermaid")
        for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)",content):
            if "://" in link or link.startswith(("#","mailto:")):continue
            target=unquote(link.split("#")[0]).strip("<>")
            if target:
                checked_links+=1
                if not (path.parent/target).exists():broken.append(dict(file=str(path.relative_to(root)),target=target))
    if broken:raise ValueError(f"Broken local Markdown links: {broken}")
    return dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(),python_artifacts_passed=True,
                stage1_examples=4,python_qsppack_mapping_checks=16,mathematical_checks=104,
                core_cases=reconstructed["verified_cases"],full_precision_phases=reconstructed["full_precision_phases"],
                readable_pngs=len(images),local_markdown_links_checked=checked_links,broken_local_links=[],
                mermaid_blocks_found=mermaid_blocks,matlab_bundle_integrity_passed=True,
                prepared_matlab_core_cases=21,prepared_matlab_convention_checks=8,
                matlab_executed=bool(manifest["matlab_qsppack"].get("executed")),
                all_technical_requirements_passed=bool(matlab_passed and manifest.get("technical_complete")),
                supervisor_checkpoint=manifest["supervisor_checkpoint"],
                ready_for_stage3=manifest.get("ready_for_stage3",False),
                limits="Local hashes, numerical reconstruction, file coverage, image integrity, and link existence. "
                       "Does not establish all-input mathematical bounds, high-precision error floors, or professor approval.")


if __name__=="__main__":
    result=audit(ROOT)
    (ROOT/"results/stage2/artifact_audit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result,indent=2))
