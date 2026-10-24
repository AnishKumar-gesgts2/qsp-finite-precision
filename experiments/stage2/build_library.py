"""Generate the core baseline library, figures, audit data, and README summaries.

Run: python experiments/stage2/build_library.py [--resume]
No phase quantization or Stage 3 work is performed.
"""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import os
import tempfile
import time
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from qsp_finite_precision.stage2 import build_target, generate_case, load_case, write_case


ROOT = Path(__file__).resolve().parents[2]
FAMILIES = ("cosine", "sine", "sign")
COLORS = dict(cosine="#277d83", sine="#b77432", sign="#7c5c99")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_columns(path, columns):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file,lineterminator="\n")
        writer.writerow(columns)
        for row in zip(*columns.values()):
            writer.writerow([int(v) if isinstance(v, (bool, np.bool_)) else v for v in row])


def read_columns(path):
    table = np.genfromtxt(path, delimiter=",", names=True, encoding="utf-8")
    return {name: table[name] for name in table.dtype.names}


def save_figure(fig, path, dpi):
    """Publish a complete image despite short Windows file-scanner locks."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(suffix=".png", dir=path.parent)
    os.close(fd)
    try:
        fig.savefig(temporary, dpi=dpi)
        for attempt in range(4):
            try:
                os.replace(temporary, path)
                break
            except OSError as error:
                if attempt == 3 or error.errno not in (13, 22):
                    raise
                time.sleep(.25 * (attempt + 1))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def style(ax):
    ax.grid(alpha=.18)
    ax.spines[["top", "right"]].set_visible(False)


def plot_case(case, curves, path):
    target = case["target"]
    family = target["family"]
    scale = target["target_scale"]
    x = curves["x"]
    mask = curves["application_mask"].astype(bool)
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), layout="constrained")
    a, b, c, table_ax = axes.flat
    # All displayed response errors are divided by target_scale; native
    # circuit-unit values remain in the CSV/JSON and are used for acceptance.
    a.plot(x, np.where(mask, curves["target"] / scale, np.nan), lw=3, color="#253a4c", label="Original application function")
    a.plot(x, curves["polynomial"] / scale, ls="-.", lw=1.6, color="#8a6f9f", label="Target polynomial / target scale")
    a.plot(x, curves["readout"] / scale, ls="--", lw=1.9, color="#16837b", label="pyqsp phases, reconstructed locally")
    a.plot(x, curves["qsppack_readout"] / scale, ls=":", lw=1.5, color="#ce7435", label="Python QSPPACK phases, local readout")
    a.set(title="Original function and phase reconstruction", xlabel="Signal input x", ylabel="Original-function units")
    a.legend(fontsize=7.8)
    if family != "sign" and target["parameters"]["tau"] > 30:
        half_width=min(1.,4*np.pi/target["parameters"]["tau"])
        a.set_xlim(-half_width,half_width)
        a.set_title("Function reconstruction: central zoom")
        inset=a.inset_axes([.66,.05,.31,.25])
        inset.plot(x,curves["target"]/scale,color="#253a4c",lw=.35)
        inset.plot(x,curves["readout"]/scale,color="#16837b",ls=":",lw=.4)
        inset.set_title("Full interval",fontsize=7)
        inset.set_xticks([-1,0,1]);inset.set_yticks([-1,1]);inset.tick_params(labelsize=6)
    full = np.asarray(case["full_phases"])
    b.plot(np.arange(full.size), full, color=COLORS[family], lw=1, marker=".", ms=2.5)
    b.set(title=f"Full unrounded phase list ({full.size} phases)", xlabel="Phase index j", ylabel="Radians")
    for key, label, color, ls in (
        ("approximation_error", "Polynomial vs original target", "#8a6f9f", "-"),
        ("baseline_error", "Reconstructed vs original target", "#16837b", "--"),
        ("synthesis_error", "Reconstructed vs polynomial (full interval)", "#ce7435", "-"),
    ):
        error = np.maximum(curves[key] / scale, 1e-18)
        if key != "synthesis_error":
            error = np.where(mask, error, np.nan)
        c.semilogy(x, error, color=color, ls=ls, lw=1.1, label=label)
    c.set(title="Approximation and synthesis remain separate", xlabel="Signal input x", ylabel="Absolute error / target scale (floor: 1e-18)")
    c.legend(fontsize=7.7)
    if family == "sign":
        gap = target["parameters"]["gap"]
        for ax in (a, c):
            ax.axvspan(-gap, gap, color="#cad1d7", alpha=.3)
        a.text(.5, .05, f"Excluded application gap: |x| < {gap:.5g}", transform=a.transAxes, ha="center", fontsize=8,
               bbox=dict(facecolor="white",alpha=.9,edgecolor="none",pad=3))
    metrics = case["metrics"]
    qmetrics = case["python_qsppack"]["metrics"]
    data = [
        ["Approximation (application domain)", metrics["approximation"]],
        ["Reconstruction vs target (application)", metrics["baseline_application"]],
        ["Synthesis (full interval)", metrics["synthesis"]],
        ["Local vs pyqsp complex amplitude", metrics["pyqsp_evaluator_agreement"]],
        ["Local vs Python QSPPACK response", qmetrics["evaluator_agreement"]],
    ]
    table_ax.axis("off")
    table_ax.set_title("Measured errors in native circuit units")
    table = table_ax.table(cellText=[[label, f"{s['max_abs']:.3e}", f"{s['rmse']:.3e}"] for label, s in data],
                          colLabels=["Comparison", "Max abs error", "RMSE"],colWidths=[.58,.21,.21],
                          cellLoc="left",bbox=[0,.3,1,.55])
    table.auto_set_font_size(False)
    table.set_fontsize(8.1)
    for (row, _), cell in table.get_celld().items():
        cell.set_edgecolor("#e1e7ec")
        if row == 0:
            cell.set_facecolor("#e8f1f3")
            cell.set_text_props(weight="bold")
    table_ax.text(0,.07,
                  f"pyqsp coefficient residual (L1): {case['solver']['returned_coefficient_l1_residual']:.3e}\n"
                  f"Validation inputs: {case['grid']['total_validation_points']:,}; application inputs: {case['grid']['application_points']:,}\n"
                  f"Target scale: {scale:.8g}; polynomial construction scale: {target['polynomial_scale']:.8g}\n"
                  "Sampled maxima; sample-weighted RMSE. No phase rounding. MATLAB status: see manifest.",
                  transform=table_ax.transAxes,fontsize=8.4,va="bottom")
    for ax in (a,b,c):
        style(ax)
    parameters = target["parameters"]
    detail = f"tau={parameters['tau']:.6g}" if family != "sign" else f"delta={parameters['delta']:.6g}, gap={parameters['gap']:.6g}"
    fig.suptitle(f"Stage 2 | {family.title()} | degree {target['degree']} | {detail}",fontsize=15)
    save_figure(fig,path,dpi=150)
    plt.close(fig)


def plot_overview(cases, path):
    fig, axes = plt.subplots(2,2,figsize=(13,8),layout="constrained")
    for family in FAMILIES:
        group = [c for c in cases if c["target"]["family"] == family]
        d = [c["target"]["degree"] for c in group]
        for key,ls,label in [("baseline_application","-","Baseline vs target"),("synthesis","--","Synthesis vs polynomial")]:
            axes[0,0].loglog(d,[c["metrics"][key]["max_abs"] for c in group],ls=ls,marker="o",ms=4,color=COLORS[family],label=f"{family}: {label}")
        axes[1,0].semilogx(d,[c["solver"]["returned_coefficient_l1_residual"] for c in group],marker="o",color=COLORS[family],label=family)
        axes[1,1].loglog(d,[float(np.median(np.abs(np.diff(c["full_phases"])))) for c in group],marker="o",color=COLORS[family],label=family)
        if family != "sign":
            axes[0,1].loglog(d,[c["target"]["parameters"]["tau"] for c in group],marker="o",color=COLORS[family],label=f"{family}: evolution time")
        else:
            axes[0,1].loglog(d,[c["target"]["parameters"]["inverse_gap"] for c in group],marker="o",color=COLORS[family],label="sign: inverse gap")
    axes[0,0].set(title="Baseline error and synthesis error",xlabel="Achieved polynomial degree",ylabel="Sampled max error (native circuit units)")
    axes[0,1].set(title="Target difficulty varies with degree",xlabel="Achieved polynomial degree",ylabel="Evolution time or inverse gap")
    axes[1,0].set(title="Returned-phase coefficient residual",xlabel="Achieved polynomial degree",ylabel="Coefficient L1 residual",yscale="log")
    axes[1,0].axhline(1e-12,color="#ba4a3b",ls=":",label="Stopping criterion: 1e-12")
    axes[1,1].set(title="Median neighboring phase change",xlabel="Achieved polynomial degree",ylabel="Median absolute adjacent difference (radians)")
    for ax in axes.flat:
        style(ax)
        ax.legend(fontsize=7)
    fig.suptitle("Stage 2: unrounded core phase library",fontsize=16)
    save_figure(fig,path,dpi=160)
    plt.close(fig)


def publish_summary(manifest, cases, root=ROOT):
    matlab = manifest.get("matlab_qsppack", {})
    matlab_passed = matlab.get("status") == "passed" and matlab.get("executed") is True
    if matlab_passed:
        checkpoint = (f"**Stage 2 technical deliverables complete:** original QSPPACK ran in MATLAB {matlab['runtime_version']}; "
                      f"{matlab['verified_cases']} core cases and {matlab['convention_checks']} Stage 1 full-phase readout checks passed. "
                      f"Worst native MATLAB/local evaluator difference: {matlab['evaluator_max']:.3e}; "
                      f"worst MATLAB synthesis error: {matlab['synthesis_max']:.3e}. "
                      "[MATLAB data and graphs](results/stage2/matlab/README.md). "
                      "**Professor Hen's supervisor checkpoint remains pending before Stage 3.**")
    elif matlab.get("status") == "unable_to_complete":
        checkpoint = ("**Python Stage 2 deliverables complete; original MATLAB cross-check unable to complete.** "
                      "MATLAB Online failed before code execution; [the attempt record](results/stage2/matlab_execution_status.json) "
                      "documents the limitation. MATLAB test code and publication tools are prepared, not executed evidence. "
                      "Professor Hen's checkpoint remains pending before Stage 3.")
    else:
        checkpoint = ("**Remaining technical check:** original MATLAB QSPPACK execution is pending. "
                      "The supplied runner/input bundle is preparation; Python QSPPACK is supplementary. "
                      "Professor Hen's required review before Stage 3 also remains pending.")
    groups = {family:[c for c in cases if c["target"]["family"]==family] for family in FAMILIES}
    lines = ["<!-- BEGIN STAGE 2 RESULTS -->", "", "## Stage 2 measured baseline results", "",
             f"**{len(cases)}/{manifest['configured_cases']} configured cases generated and independently reloaded**; {sum(len(c['full_phases']) for c in cases):,} full-precision phases saved. No phases were quantized. The counts and metrics below come from the saved [manifest](results/stage2/summary.json) and [results CSV](results/stage2/library_summary.csv).", "",
             "| Target | Cases | Degrees | Worst target error on application domain | Worst synthesis error on full interval |",
             "| --- | ---: | --- | ---: | ---: |"]
    for family, group in groups.items():
        if group:
            lines.append(f"| {family.title()} | {len(group)} | {min(c['target']['degree'] for c in group)}–{max(c['target']['degree'] for c in group)} | {max(c['metrics']['baseline_application']['max_abs'] for c in group):.3e} | {max(c['metrics']['synthesis']['max_abs'] for c in group):.3e} |")
    lines += ["", "Errors above are sampled maxima in native scaled circuit units. Hamiltonian targets use scale 0.5; the sign target is 0.9 times sign(x) on each recorded gap-excluded domain. The sign polynomial is constructed from a smooth erf surrogate, but target errors are measured against the sign function itself. The target-accuracy acceptance goals (1e-6 for cosine/sine; 1e-2 for sign) are documented implementation choices, not tolerances specified by the professor.", "",
              f"All {len(cases)} returned-phase coefficient checks and supplementary Python QSPPACK checks passed. Maximum pyqsp/local complex-amplitude difference on the recorded audit grids: {manifest['aggregate']['pyqsp_agreement_max']:.3e}. Reload verification checks archive hashes, full phase counts, reconstruction, and curve/metric consistency.", "",
              "![Stage 2 overview](figures/stage2/overview.png)", "",
              "[Stage 2 implementation and results guide](src/qsp_finite_precision/stage2/README.md) · [Browse all cases, phase plots, and response/error graphs](data/phases/README.md) · [Regeneration commands](experiments/stage2/README.md)", "",
              checkpoint, "", "<!-- END STAGE 2 RESULTS -->"]
    path = root/"README.md"
    content = path.read_text(encoding="utf-8")
    start,end=lines[0],lines[-1]
    block="\n".join(lines)
    if start in content:
        before,tail=content.split(start,1)
        _,after=tail.split(end,1)
        content=before+block+after
    else:
        content=content.replace("## Repository layout",block+"\n\n## Repository layout")
    path.write_text(content,encoding="utf-8")
    index=["# Full-precision core phase library", "", "Generated Stage 2 Python baselines. All angles are in radians, unwrapped and unquantized, saved as round-trip binary64 JSON numbers. Only cases listed in the [manifest](../../results/stage2/summary.json) belong to this generated library.", "",
           ("Original MATLAB cross-check passed; supervisor review remains pending. " if matlab_passed else
            "Python library complete; original MATLAB cross-check unavailable in this environment; supervisor review pending. "
            if matlab.get("status")=="unable_to_complete" else "Original MATLAB QSPPACK execution and supervisor review remain pending. ")+
           "[Methods and acceptance criteria](../../src/qsp_finite_precision/stage2/README.md) · [Regenerate / verify](../../experiments/stage2/README.md)", "",
           "![Library overview](../../figures/stage2/overview.png)", "",
           "Each case graph includes the original target, target polynomial, phase-reconstructed response, full phase list, separate error curves, and max/RMSE table. Response curves are displayed in original-function units; figure tables and the summary below retain native scaled circuit units. For sign cases the excluded application gap is shaded.", "",
           "| Case | Degree | Parameter | Max target error | Max synthesis error | Artifacts |", "| --- | ---: | --- | ---: | ---: | --- |"]
    for case in cases:
        ident=case["case_id"];t=case["target"];p=t["parameters"]
        parameter=f"tau={p['tau']:.5g}" if t["family"]!="sign" else f"gap={p['gap']:.5g}; delta={p['delta']:.5g}"
        links=f"[Phases](stage2/{ident}.json) · [Graph](../../figures/stage2/{ident}.png) · [Curves CSV](../../results/stage2/{ident}_response.csv)"
        if matlab_passed:
            links += f" · [MATLAB phases](stage2_matlab/{ident}.json) · [MATLAB graph](../../figures/stage2/matlab/{ident}.png) · [MATLAB CSV](../../results/stage2/matlab/{ident}_response.csv)"
        index.append(f"| {ident} | {t['degree']} | {parameter} | {case['metrics']['baseline_application']['max_abs']:.3e} | {case['metrics']['synthesis']['max_abs']:.3e} | {links} |")
    for family in FAMILIES:
        group=groups[family]
        if group:
            index += ["",f"## {family.title()} reference examples", ""]
            for case in [group[0],group[-1]]:
                index += [f"### {case['case_id']}","",f"![{case['case_id']} reference graph](../../figures/stage2/{case['case_id']}.png)",""]
    (root/"data/phases/README.md").write_text("\n".join(index).rstrip()+"\n",encoding="utf-8")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume",action="store_true",help="reuse matching, hash-checked cases; regenerate plots and summaries")
    args=parser.parse_args()
    config_path=Path(__file__).with_name("config.json")
    config=json.loads(config_path.read_text())
    output=ROOT/"results/stage2";figures=ROOT/"figures/stage2";phase_dir=ROOT/"data/phases/stage2"
    for folder in (output,figures,phase_dir):folder.mkdir(parents=True,exist_ok=True)
    attempt_path=output/"matlab_execution_status.json"
    matlab_unavailable=attempt_path.exists() and not (output/"matlab_output.json").exists() and json.loads(
        attempt_path.read_text()).get("status")=="unable_to_complete"
    versions={name:importlib.metadata.version(name) for name in ("numpy","scipy","pyqsp","qsppack","matplotlib")}
    science_sources={name:sha(ROOT/name) for name in ("src/qsp_finite_precision/stage1/forward.py","src/qsp_finite_precision/stage1/conventions.py","src/qsp_finite_precision/stage2/targets.py","src/qsp_finite_precision/stage2/library.py")}
    cases=[];rows=[];failures=[];entries=[];matlab_cases=[]
    for family,degrees in config["families"].items():
        for degree in degrees:
            target=build_target(family,degree,**config["target_options"])
            ident=target["case_id"];path=phase_dir/f"{ident}.json"
            curve_path=output/f"{ident}_response.csv";audit_path=output/f"{ident}_audit.csv";log_path=output/f"{ident}_solver.log"
            fingerprint=hashlib.sha256(json.dumps(dict(target=target,solver=config["solver"],versions=versions,sources=science_sources),sort_keys=True).encode()).hexdigest()
            cached=False
            try:
                if args.resume and path.exists():
                    case=load_case(path)
                    cached=case.get("generation_fingerprint")==fingerprint and all(
                        (ROOT/name).exists() and sha(ROOT/name)==digest for name,digest in case.get("artifact_sha256",{}).items())
                    cached=cached and len(case.get("artifact_sha256",{}))==3
                if cached:
                    curves=read_columns(curve_path);audit=read_columns(audit_path)
                else:
                    case,curves,audit,log=generate_case(target,**config["solver"])
                    if not case["passed"]:
                        raise RuntimeError(f"Failed acceptance: {case['acceptance']['checks']}")
                    write_columns(curve_path,curves);write_columns(audit_path,audit)
                    log_path.write_text(log,encoding="utf-8",newline="\n")
                    case["generation_fingerprint"]=fingerprint
                    case["artifact_sha256"]={p.relative_to(ROOT).as_posix():sha(p) for p in (curve_path,audit_path,log_path)}
                    write_case(path,case)
                if matlab_unavailable:
                    case["matlab_qsppack"]=dict(status="unable_to_complete",executed=False,
                                                attempt_report="results/stage2/matlab_execution_status.json")
                    write_case(path,case)
                plot_case(case,curves,figures/f"{ident}.png")
                cases.append(case)
                entries.append(dict(case_id=ident,file=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
                t=case["target"];m=case["metrics"];p=t["parameters"]
                rows.append(dict(case_id=ident,family=family,degree=degree,phase_count=len(case["full_phases"]),
                                 tau=p.get("tau",""),delta=p.get("delta",""),gap=p.get("gap",""),target_scale=t["target_scale"],
                                 polynomial_scale=t["polynomial_scale"],solver_converged=case["solver"]["converged"],
                                 coefficient_l1_residual=case["solver"]["returned_coefficient_l1_residual"],
                                 approximation_max=m["approximation"]["max_abs"],approximation_rmse=m["approximation"]["rmse"],
                                 synthesis_max=m["synthesis"]["max_abs"],synthesis_rmse=m["synthesis"]["rmse"],
                                 baseline_application_max=m["baseline_application"]["max_abs"],baseline_application_rmse=m["baseline_application"]["rmse"],
                                 pyqsp_agreement_max=m["pyqsp_evaluator_agreement"]["max_abs"],
                                 python_qsppack_agreement_max=case["python_qsppack"]["metrics"]["evaluator_agreement"]["max_abs"],
                                 python_qsppack_converged=case["python_qsppack"]["converged"],unitarity_max=m["unitarity_max"],
                                 boundedness_upper_estimate=t["boundedness"]["upper_estimate"],
                                 nearly_equal_adjacent_fraction=case["phase_structure"]["nearly_equal_adjacent_fraction"],
                                 median_phase_step=float(np.median(np.abs(np.diff(case["full_phases"])))),
                                 longest_nearly_equal_run=case["phase_structure"]["longest_nearly_equal_run"],passed=case["passed"],
                                 matlab_executed=False,matlab_status=case["matlab_qsppack"]["status"]))
                matlab_cases.append(dict(case_id=ident,parity=t["parity"],coefficients=t["coefficients"][t["parity"]::2],
                                         audit_x=audit["x"].tolist(),validation_x=curves["x"].tolist()))
                print(f"{ident}: {'reused' if cached else 'generated'}; coefficient={case['solver']['returned_coefficient_l1_residual']:.2e}; synthesis={m['synthesis']['max_abs']:.2e}; target={m['baseline_application']['max_abs']:.2e}",flush=True)
            except Exception as error:
                failures.append(dict(case_id=ident,error=f"{type(error).__name__}: {error}"))
                print(f"FAILED {ident}: {error}",flush=True)
    if not cases:
        (output/"failures.json").write_text(json.dumps(failures,indent=2)+"\n")
        raise SystemExit("No successful library cases")
    with (output/"library_summary.csv").open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    matlab_sources=json.loads(Path(__file__).with_name("matlab_source_hashes.json").read_text())
    stage1=json.loads((ROOT/"results/stage1/solver_comparisons.json").read_text())
    stage1_grid=read_columns(ROOT/"results/stage1/solver_responses.csv")["x"]
    # The Stage 1 CSV repeats x for each example; use the documented unique grid.
    stage1_grid=np.unique(stage1_grid)
    convention_cases=[dict(case_id=f"{e['name']}__{'real' if real else 'imag'}",name=e["name"],
                           parity=e["parity"],targetPre=real,typePhi="full",
                           coefficients=e["chebyshev_coefficients"][e["parity"]::2],x=stage1_grid.tolist())
                      for e in stage1["examples"] for real in (True,False)]
    matlab_input=dict(source_revision=config["matlab_qsppack_revision"],expected_source_hashes=matlab_sources["functions"],
                      criteria=config["solver"]["criteria"],maxiter=config["solver"]["maxiter"],
                      convention_cases=convention_cases,cases=matlab_cases)
    (output/"matlab_input.json").write_text(json.dumps(matlab_input,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
    plot_overview(cases,figures/"overview.png")
    manifest=dict(schema_version=1,python=platform.python_version(),versions=versions,
                  configured_cases=sum(map(len,config["families"].values())),successful_cases=len(cases),failures=failures,
                  python_validation_passed=not failures,stage2_complete=False,
                  matlab_qsppack=dict(status="pending",executed=False,input_file="results/stage2/matlab_input.json"),
                  supervisor_checkpoint="pending; required before Stage 3",config_sha256=sha(config_path),
                  assignment_sha256=sha(ROOT/"references/QSP_project.docx"),
                  science_source_sha256=science_sources,builder_sha256=sha(__file__),cases=entries,
                  aggregate=dict(synthesis_max=max(c["metrics"]["synthesis"]["max_abs"] for c in cases),
                                 pyqsp_agreement_max=max(c["metrics"]["pyqsp_evaluator_agreement"]["max_abs"] for c in cases),
                                 coefficient_l1_max=max(c["solver"]["returned_coefficient_l1_residual"] for c in cases),
                                 python_qsppack_agreement_max=max(c["python_qsppack"]["metrics"]["evaluator_agreement"]["max_abs"] for c in cases)))
    attempt_path=output/"matlab_execution_status.json"
    if attempt_path.exists() and not (output/"matlab_output.json").exists():
        attempt=json.loads(attempt_path.read_text())
        if attempt.get("status")=="unable_to_complete" and attempt.get("executed") is False:
            manifest["matlab_qsppack"].update(status="unable_to_complete",attempt_report="results/stage2/matlab_execution_status.json")
    manifest["python_deliverables_complete"]=not failures and len(cases)==manifest["configured_cases"]
    manifest["technical_complete"]=False
    manifest["ready_for_stage3"]=False
    (output/"summary.json").write_text(json.dumps(manifest,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
    from verify_library import verify
    verified=verify(ROOT)
    (output/"verification.json").write_text(json.dumps(verified,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
    publish_summary(manifest,cases)
    if failures:
        raise SystemExit(f"{len(failures)} cases failed; see summary.json")
    report_path=output/"matlab_output.json"
    if report_path.exists():
        from publish_matlab import publish
        publish(ROOT,report_path)
        print(f"Verified {len(cases)} Python and original MATLAB cases. Supervisor checkpoint remains pending.")
    else:
        print(f"Verified {len(cases)} successful unrounded cases. Original MATLAB status: {manifest['matlab_qsppack']['status']}; supervisor review pending.")


if __name__=="__main__":
    main()
