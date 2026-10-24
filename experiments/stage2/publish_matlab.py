"""Verify a genuine MATLAB report, then publish its CSVs, figures, and status.

No report is manufactured here. Failed or incomplete reports cannot mark Stage 2
technically complete. Supervisor approval remains a separate pending checkpoint.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from qsp_finite_precision.stage1 import evaluate_qsp
from qsp_finite_precision.stage2 import load_case, write_case
from build_library import COLORS, FAMILIES, publish_summary, read_columns, save_figure, sha, style, write_columns
from verify_library import verify
from verify_matlab import case_data, metrics, verify_matlab


ROOT = Path(__file__).resolve().parents[2]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")


def table(ax, rows, note):
    ax.axis("off")
    ax.set_title("Sampled errors in native circuit units")
    artist = ax.table(cellText=[[label,f"{m['max_abs']:.3e}",f"{m['rmse']:.3e}"] for label,m in rows],
                      colLabels=["Comparison","Max abs error","RMSE"],colWidths=[.6,.2,.2],
                      cellLoc="left",bbox=[0,.3,1,.57])
    artist.auto_set_font_size(False)
    artist.set_fontsize(8)
    for (row,_),cell in artist.get_celld().items():
        cell.set_edgecolor("#dce3e9")
        if row == 0:
            cell.set_facecolor("#e8f1f3")
            cell.set_text_props(weight="bold")
    ax.text(0,.03,note,transform=ax.transAxes,fontsize=8.2,va="bottom")


def plot_case(case, output, columns, statistics, destination):
    t = case["target"]
    family, scale = t["family"], t["target_scale"]
    x, mask = columns["x"], columns["application_mask"]
    fig, axes = plt.subplots(2,2,figsize=(13,8.5),layout="constrained")
    response, phases, errors, tab = axes.flat
    curves = [(np.where(mask,columns["target"],np.nan),"Original application function","#253a4c","-",2.8),
              (columns["polynomial"],"Target polynomial","#8a6f9f","-.",1.6),
              (columns["matlab_native"],"Original MATLAB QSPPACK response","#ce7435","-",1.4),
              (columns["matlab_local"],"Same MATLAB phases, Python reconstruction","#277d83","--",1.4),
              (columns["pyqsp_local"],"pyqsp phases, imaginary readout","#7c5c99",":",1.5)]
    for values,label,color,ls,lw in curves:
        response.plot(x,values/scale,label=label,color=color,ls=ls,lw=lw)
    response.set(title="Original function and two solver reconstructions",xlabel="Signal input x",ylabel="Original-function units")
    response.legend(fontsize=7.3)
    if family != "sign" and t["parameters"]["tau"] > 30:
        width = min(1.,4*np.pi/t["parameters"]["tau"])
        response.set_xlim(-width,width)
        response.set_title("Function reconstruction: central zoom")
        inset = response.inset_axes([.66,.05,.31,.24])
        for values,label,color,ls,lw in curves[:3]:
            inset.plot(x,values/scale,color=color,ls=ls,lw=.4)
        inset.set_title("Full interval",fontsize=7)
        inset.set_xticks([-1,0,1]);inset.set_yticks([-1,1]);inset.tick_params(labelsize=6)
    phases.plot(case["full_phases"],color="#7c5c99",lw=1,label="pyqsp: imaginary-target phases")
    phases.plot(output["full_phases"],color="#ce7435",ls="--",lw=1,label="MATLAB: real-target phases")
    phases.set(title="Unrounded phase lists: distinct conventions",xlabel="Phase index j",ylabel="Radians")
    phases.legend(fontsize=8)
    for key,label,color,application in [
            ("matlab_target_error","MATLAB vs original target","#277d83",True),
            ("matlab_synthesis_error","MATLAB vs polynomial","#8a6f9f",False),
            ("matlab_evaluator_error","MATLAB vs Python, same MATLAB phases","#ce7435",False),
            ("solver_readout_difference","MATLAB vs pyqsp target readouts","#536b82",False)]:
        values = np.maximum(columns[key]/scale,1e-18)
        errors.semilogy(x,np.where(mask,values,np.nan) if application else values,
                        label=label,color=color,lw=1)
    errors.set(title="Application error and numerical checks are separate",xlabel="Signal input x",ylabel="Absolute error / target scale (floor 1e-18)")
    errors.legend(fontsize=7.3)
    if family == "sign":
        gap = t["parameters"]["gap"]
        for ax in (response,errors):ax.axvspan(-gap,gap,color="#cad1d7",alpha=.3)
        response.text(.5,.04,f"Application excludes |x| < {gap:.5g}",transform=response.transAxes,
                      ha="center",fontsize=8,bbox=dict(facecolor="white",edgecolor="none",alpha=.9))
    table(tab,[("MATLAB vs original target (application)",statistics["baseline_application"]),
               ("MATLAB vs polynomial (full interval)",statistics["synthesis"]),
               ("MATLAB vs Python, same phases",statistics["evaluator_agreement"]),
               ("MATLAB vs pyqsp target readouts",statistics["solver_readout_difference"])],
          f"Original MATLAB solver coefficient L1 residual: {output['solver_value']:.3e}\n"
          f"Validation inputs: {x.size:,}; target scale: {scale:g}\n"
          "Curves use original-function units; this table retains native units.\n"
          "No phase rounding. Agreement is sampled, not an error-floor proof.")
    for ax in (response,phases,errors):style(ax)
    fig.suptitle(f"Original MATLAB QSPPACK cross-check | {family.title()} | degree {t['degree']}",fontsize=15)
    save_figure(fig,destination,150)
    plt.close(fig)


def plot_overview(verified, destination):
    fig,axes = plt.subplots(2,2,figsize=(13,8),layout="constrained")
    for family in FAMILIES:
        group = sorted((c for c in verified["cases"] if c["family"]==family),key=lambda c:c["degree"])
        d = [c["degree"] for c in group]
        for ax,key,title in [(axes[0,0],"evaluator_agreement","Same MATLAB phases: native vs Python evaluator"),
                             (axes[0,1],"synthesis","MATLAB reconstruction vs target polynomial"),
                             (axes[1,0],"baseline_application","MATLAB vs original application target"),
                             (axes[1,1],"solver_readout_difference","MATLAB and pyqsp target-readout difference")]:
            ax.loglog(d,[max(c[key]["max_abs"],1e-18) for c in group],marker="o",color=COLORS[family],label=family)
            ax.set(title=title,xlabel="Achieved polynomial degree",ylabel="Sampled max error, native units (floor 1e-18)")
    for ax in axes.flat:style(ax);ax.legend(fontsize=8)
    fig.suptitle(f"Original QSPPACK in MATLAB {verified['runtime_version']} | all 21 core cases",fontsize=14)
    save_figure(fig,destination,160)
    plt.close(fig)


def publish_stage1(root, report, verified):
    """Archive actual MATLAB full-phase real/imaginary convention checks."""
    originals=json.loads((root/"results/stage1/solver_comparisons.json").read_text())["examples"]
    with (root/"results/stage1/solver_responses.csv").open(newline="") as file:
        existing=list(csv.DictReader(file))
    outputs={e["case_id"]:e for e in report["convention_cases"]}
    rows=[]
    folder=root/"figures/stage1/matlab";folder.mkdir(parents=True,exist_ok=True)
    for example in originals:
        fig,axes=plt.subplots(2,2,figsize=(13,8.5),layout="constrained")
        a,b,c,tab=axes.flat
        entries=[r for r in existing if r["example"]==example["name"]]
        reference={float(r["x"]):float(r["original_function"]) for r in entries}
        errors=[]
        for label,real,color in [("real",True,"#ce7435"),("imag",False,"#277d83")]:
            output=outputs[f"{example['name']}__{label}"]
            x=np.asarray(output["x"]);native=np.asarray(output["response"])
            desired=np.array([reference[float(v)] for v in x]);scale=example["generator_scale"]
            _,P=evaluate_qsp(output["full_phases"],x)
            local=P.real if real else P.imag
            polynomial=np.polynomial.chebyshev.chebval(x,example["chebyshev_coefficients"])
            if real:
                a.plot(x,desired,color="#253a4c",lw=2.5,label="Original function")
                a.plot(x,polynomial/scale,color="#8a6f9f",ls="-.",label="Target polynomial / scale")
            a.plot(x,native/scale,color=color,ls="--",label=f"MATLAB {label} target readout / scale")
            a.plot(x,local/scale,color=color,ls=":",lw=.8)
            b.plot(output["full_phases"],color=color,marker=".",label=f"MATLAB {label}-target phases")
            c.semilogy(x,np.maximum(np.abs(native/scale-desired),1e-18),color=color,label=f"{label}: original-function error")
            c.semilogy(x,np.maximum(np.abs(native-local)/scale,1e-18),color=color,ls=":",label=f"{label}: evaluator difference")
            errors.extend([(f"{label}: MATLAB vs original function",metrics(native/scale-desired)),
                           (f"{label}: MATLAB vs Python, same phases",metrics((native-local)/scale))])
            for values in zip(x,desired,polynomial,native,local):
                rows.append(dict(case_id=output["case_id"],x=values[0],original_function=values[1],
                                 polynomial=values[2],matlab_native=values[3],local=values[4],
                                 generator_scale=scale,original_function_error=abs(values[3]/scale-values[1]),
                                 evaluator_error=abs(values[3]-values[4])))
        a.set(title="Original function and MATLAB phase reconstructions",xlabel="Signal input x",ylabel="Original-function units")
        b.set(title="Full unrounded phases",xlabel="Phase index j",ylabel="Radians")
        c.set(title="Function accuracy and evaluator agreement",xlabel="Signal input x",ylabel="Absolute error, original units (floor 1e-18)")
        for ax in (a,b,c):style(ax);ax.legend(fontsize=7.5)
        table(tab,errors,"This table uses original-function units (divide by generator scale).\n"
              "Solid/dashed curves: MATLAB; dotted overlays: local reconstruction.\n"
              "Full phases only. Existing Python tests also cover reduced phases.\n"
              "Sampled maxima and sample-weighted RMSE; no phase rounding.")
        tab.set_title("Measured errors in original-function units")
        fig.suptitle(f"Stage 1 original MATLAB check | {example['name']} | degree {example['degree']}",fontsize=15)
        save_figure(fig,folder/f"{example['name']}.png",150);plt.close(fig)
    with (root/"results/stage1/matlab_responses.csv").open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=rows[0],lineterminator="\n");writer.writeheader();writer.writerows(rows)
    write_json(root/"results/stage1/matlab_verification.json",dict(
        passed=True,runtime=verified["runtime"],runtime_version=verified["runtime_version"],
        source_revision=verified["source_revision"],input_sha256=verified["input_sha256"],
        cases=verified["convention_cases"],scope="Four fixtures, full phases, real and imaginary readouts; eight checks"))


def write_result_guide(root, verified):
    lines=["# Original MATLAB QSPPACK results", "",
           f"Actual runtime: **MATLAB {verified['runtime_version']}**. All **{len(verified['cases'])} core cases** and "
           f"**{len(verified['convention_cases'])} Stage 1 full-phase readout checks** passed.", "",
           "[Raw MATLAB output](../matlab_output.json) · [Input and source identity](../matlab_input.json) · "
           "[Verification JSON](../matlab_verification.json) · [Summary CSV](../matlab_summary.csv)", "",
           "![MATLAB overview](../../../figures/stage2/matlab/overview.png)", "",
           "The original QSPPACK solver receives the same saved Chebyshev polynomials as pyqsp. "
           "MATLAB's own response is compared with our Python reconstruction using the **same MATLAB phases**. "
           "The two solvers' target readouts are also compared, with their different real/imaginary conventions respected. "
           "Their phase lists and full complex amplitudes are not required to coincide.", "",
           "Every core case has a native-MATLAB response on the full validation grid, a separately reconstructed response, "
           "original target and polynomial samples, an application-domain mask, and separate errors. "
           "Graphs show response overlays, both phase sequences, pointwise errors, and maximum/RMSE tables. "
           "Sign gaps are shaded; oscillatory targets have a central zoom and full-interval inset.", "",
           "Curves reverse target scaling for display only. Tables and CSV errors retain native circuit units. "
           "Maxima are sampled; RMSE weights the sampled inputs equally. These are unrounded baselines and "
           "implementation checks, not measurements of phase-storage error or a high-precision error-floor certificate.", "",
           "| Case | Native vs Python max | Native vs polynomial max | Original target max on application domain | Files |",
           "| --- | ---: | ---: | ---: | --- |"]
    for row in verified["cases"]:
        ident=row["case_id"]
        lines.append(f"| {ident} | {row['evaluator_agreement']['max_abs']:.3e} | {row['synthesis']['max_abs']:.3e} | "
                     f"{row['baseline_application']['max_abs']:.3e} | [Graph](../../../figures/stage2/matlab/{ident}.png) · "
                     f"[Curves]({ident}_response.csv) · [Phases](../../../data/phases/stage2_matlab/{ident}.json) |")
    lines += ["", "## Stage 1 real/imaginary readout checks", "",
              "These supplementary checks use all four existing Stage 1 fixtures, in full-phase real and imaginary conventions "
              "(eight checks on 1,025 inputs each). The existing Python suite separately checks full/reduced mappings. "
              "[Native MATLAB curves](../../stage1/matlab_responses.csv) · "
              "[Stage 1 MATLAB verification](../../stage1/matlab_verification.json)", ""]
    for name in ("linear","cosine","sine","smoothed_sign"):
        lines += [f"### {name}","",f"![{name} original MATLAB check](../../../figures/stage1/matlab/{name}.png)",""]
    lines += ["## Reproduce", "", "Run the supplied MATLAB bundle, preserve its actual `matlab_output.json`, then run:", "",
              "```powershell", ".\\.venv\\Scripts\\python.exe experiments/stage2/publish_matlab.py", "```", "",
              "Publication verifies source/input identity, coverage, convergence, phase counts, both native-response grids, "
              "full-grid synthesis, target accuracy, and unitarity before completion is recorded. "
              "A later library regeneration reruns publication against the actual report and current inputs; stale reports fail. "
              "Professor Hen's checkpoint remains pending before Stage 3.", ""]
    (root/"results/stage2/matlab/README.md").write_text("\n".join(lines),encoding="utf-8")


def publish(root, report_path):
    root,report_path=Path(root),Path(report_path)
    report=json.loads(report_path.read_text())
    verified=verify_matlab(root,report)  # Validate all coverage and numerics before publishing.
    canonical_report=root/"results/stage2/matlab_output.json"
    if report_path.resolve()!=canonical_report.resolve():
        canonical_report.write_bytes(report_path.read_bytes())
        report_path=canonical_report
    figures=root/"figures/stage2/matlab";figures.mkdir(parents=True,exist_ok=True)
    phase_dir=root/"data/phases/stage2_matlab";phase_dir.mkdir(parents=True,exist_ok=True)
    output_dir=root/"results/stage2/matlab";output_dir.mkdir(parents=True,exist_ok=True)
    rows=[];cases=[]
    for output in report["cases"]:
        case,columns,statistics=case_data(root,output)
        ident=case["case_id"]
        write_columns(output_dir/f"{ident}_response.csv",columns)
        plot_case(case,output,columns,statistics,figures/f"{ident}.png")
        phase_path=phase_dir/f"{ident}.json"
        write_json(phase_path,dict(case_id=ident,target=case["target"],full_phases=output["full_phases"],
                                  solver=dict(name="Original MATLAB QSPPACK",runtime_version=report["runtime_version"],
                                              source_revision=report["source_revision"],method="Newton",
                                              residual=output["solver_value"],iterations=output["iterations"]),
                                  convention=dict(targetPre=True,typePhi="full",readout="real",quantized=False),
                                  metrics=statistics,input_sha256=verified["input_sha256"]))
        case["matlab_qsppack"]=dict(status="passed",executed=True,runtime_version=report["runtime_version"],
                                    input_sha256=verified["input_sha256"],
                                    phase_file=phase_path.relative_to(root).as_posix(),metrics=statistics)
        write_case(root/f"data/phases/stage2/{ident}.json",case)
        cases.append(case)
        rows.append(dict(case_id=ident,family=case["target"]["family"],degree=case["target"]["degree"],
                         solver_value=output["solver_value"],iterations=output["iterations"],
                         validation_points=len(columns["x"]),
                         **{f"{key}_{metric}":value for key,m in statistics.items() if isinstance(m,dict)
                            for metric,value in m.items()},unitarity_max=statistics["unitarity_max"]))
    with (root/"results/stage2/matlab_summary.csv").open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=rows[0],lineterminator="\n");writer.writeheader();writer.writerows(rows)
    plot_overview(verified,figures/"overview.png")
    publish_stage1(root,report,verified)
    write_result_guide(root,verified)
    with (root/"results/stage2/library_summary.csv").open(newline="") as file:summary=list(csv.DictReader(file))
    by_id={r["case_id"]:r for r in rows}
    for row in summary:
        m=by_id[row["case_id"]]
        row.update(matlab_executed=True,matlab_status="passed",matlab_solver_value=m["solver_value"],
                   matlab_synthesis_max=m["synthesis_max_abs"],matlab_evaluator_max=m["evaluator_agreement_max_abs"])
    with (root/"results/stage2/library_summary.csv").open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=summary[0],lineterminator="\n");writer.writeheader();writer.writerows(summary)
    write_json(root/"results/stage2/matlab_verification.json",verified)
    manifest_path=root/"results/stage2/summary.json"
    manifest=json.loads(manifest_path.read_text())
    manifest["matlab_qsppack"]=dict(status="passed",executed=True,runtime_version=report["runtime_version"],
                                    input_file="results/stage2/matlab_input.json",report_file="results/stage2/matlab_output.json",
                                    input_sha256=verified["input_sha256"],
                                    report_file_sha256=sha(report_path),verified_cases=len(verified["cases"]),
                                    convention_checks=len(verified["convention_cases"]),
                                    evaluator_max=max(c["evaluator_agreement"]["max_abs"] for c in verified["cases"]),
                                    synthesis_max=max(c["synthesis"]["max_abs"] for c in verified["cases"]))
    manifest["technical_complete"]=manifest["python_validation_passed"] and len(rows)==manifest["configured_cases"]
    manifest["stage2_complete"]=manifest["technical_complete"]
    manifest["stage2_completion_scope"]="Technical Stage 2 deliverables; supervisor checkpoint remains separate"
    manifest["ready_for_stage3"]=False
    for entry in manifest["cases"]:entry["sha256"]=sha(root/entry["file"])
    # Hash every published cross-check artifact, excluding the manifest itself.
    artifacts=[report_path,root/"results/stage2/matlab_verification.json",root/"results/stage2/matlab_summary.csv",
               root/"results/stage1/matlab_verification.json",root/"results/stage1/matlab_responses.csv"]
    for folder in (figures,phase_dir,output_dir,root/"figures/stage1/matlab"):
        artifacts.extend(p for p in folder.iterdir() if p.is_file())
    manifest["matlab_artifact_sha256"]={p.relative_to(root).as_posix():sha(p) for p in sorted(artifacts)}
    write_json(manifest_path,manifest)
    write_json(root/"results/stage2/verification.json",verify(root))
    publish_summary(manifest,cases,root=root)
    return verified


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report",nargs="?",type=Path,default=ROOT/"results/stage2/matlab_output.json")
    args=parser.parse_args()
    result=publish(ROOT,args.report)
    print(f"Published {len(result['cases'])} actual MATLAB core cases and {len(result['convention_cases'])} convention checks.")
