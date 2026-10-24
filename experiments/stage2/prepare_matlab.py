"""Package pinned original QSPPACK and Stage 2 inputs for MATLAB, including Online.

Preparation is not execution evidence. No credentials or private repository access
are needed inside MATLAB: all runtime inputs are included in the ZIP.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(source_root, output):
    request_bytes = (ROOT / "results/stage2/matlab_input.json").read_bytes()
    request = json.loads(request_bytes)
    revision = request["source_revision"]
    # git archive reads the pinned committed tree, not potentially modified files.
    archive_bytes = subprocess.run(
        ["git", "-C", str(source_root), "archive", "--format=zip", revision],
        check=True, capture_output=True,
    ).stdout
    files = {}
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as source:
        for entry in source.infolist():
            if not entry.is_dir():
                files["QSPPACK/" + entry.filename] = source.read(entry)
    for name, expected in request["expected_source_hashes"].items():
        matches = [data for path, data in files.items() if Path(path).name == name + ".m"]
        if len(matches) != 1:
            raise ValueError(f"Missing or ambiguous original source: {name}")
        normalized = matches[0].decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        if sha(normalized) != expected:
            raise ValueError(f"Pinned source hash mismatch: {name}")
    files["matlab_input.json"] = request_bytes
    files["crosscheck_matlab.m"] = (Path(__file__).with_name("crosscheck_matlab.m")).read_bytes()
    files["run_stage2.m"] = b"""function run_stage2
% Run after extracting this bundle in MATLAB or MATLAB Online.
% All numerical inputs and original QSPPACK source are included locally.
bundle_root = fileparts(mfilename('fullpath'));
addpath(bundle_root);
diary(fullfile(bundle_root, 'matlab_run.log'));
cleanup = onCleanup(@() diary('off')); %#ok<NASGU>
fprintf('Actual MATLAB runtime: %s\\n', version);
crosscheck_matlab(fullfile(bundle_root, 'QSPPACK'), ...
    fullfile(bundle_root, 'matlab_input.json'), ...
    fullfile(bundle_root, 'matlab_output.json'));
end
"""
    files["README.txt"] = b"""PREPARED MATLAB CROSS-CHECK, NOT EXECUTION EVIDENCE

Extract the ZIP in MATLAB or MATLAB Online, open its folder, then run:
    run_stage2
The console prints convergence for 21 core cases and 8 Stage 1 readout checks.
Preserve matlab_output.json and matlab_run.log. Completed cases are saved as
the run proceeds; rerun run_stage2 to resume the same request after interruption.
Copy/download that file into the project's results/stage2 folder, then run:
    .\\.venv\\Scripts\\python.exe experiments/stage2/publish_matlab.py
Only a verified actual MATLAB report completes the runtime check.
QSPPACK is included unchanged from the pinned Git commit, with its LICENSE.
The MATLAB runner verifies six source hashes again before computation.
No account credentials or private GitHub access are included or needed.
"""
    manifest = dict(
        status="prepared; MATLAB execution still required",
        source_repository="https://github.com/qsppack/QSPPACK",
        source_revision=revision,
        case_count=len(request["cases"]),
        convention_check_count=len(request["convention_cases"]),
        input_sha256=sha(request_bytes),
        files={name: sha(data) for name, data in sorted(files.items())},
    )
    files["bundle_manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo("qsp-stage2-matlab/" + name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, data)
    return dict(output=str(output.resolve()), sha256=sha(output.read_bytes()),
                files=len(files), case_count=len(request["cases"]),
                source_revision=revision, status=manifest["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("qsppack_root", type=Path, help="Local Git clone of original MATLAB QSPPACK")
    parser.add_argument("output", type=Path, help="Destination ZIP")
    args = parser.parse_args()
    print(json.dumps(prepare(args.qsppack_root, args.output), indent=2))
