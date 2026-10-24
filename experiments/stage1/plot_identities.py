"""Plot recorded identity checks; no new numerical evidence is inferred."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    root=Path(__file__).resolve().parents[2]
    with (root/"results/stage1/mathematical_checks.csv").open(newline="") as file:
        rows=list(csv.DictReader(file))
    if not rows or any(r["passed"]!="True" for r in rows):
        raise ValueError("Identity checks are missing or failing")
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout="constrained")
    panels=[(["unitarity"],"Full-unitary unitarity residual"),
            (["endpoint_sum"],"Endpoint identity: phase sum"),
            (["chebyshev"],"Zero phases: Chebyshev identity"),
            (["parity","boundedness_excess"],"Parity and boundedness excess")]
    for ax,(checks,title) in zip(axes.flat,panels):
        for check in checks:
            group=[r for r in rows if r["check"]==check]
            degrees=sorted({int(r["degree"]) for r in group})
            worst=[max(float(r["max_discrepancy"]) for r in group if int(r["degree"])==d) for d in degrees]
            labels=dict(unitarity="Unitarity",endpoint_sum="Endpoint identity",chebyshev="Chebyshev identity",
                        parity="Parity",boundedness_excess="Boundedness excess")
            ax.plot(degrees,np.maximum(worst,1e-18),marker="o",label=labels[check])
        ax.axhline(float(rows[0]["tolerance"]),color="#ba4a3b",ls="--",label="Recorded acceptance threshold")
        ax.set(title=title,xlabel="Polynomial degree",ylabel="Maximum discrepancy (floor 1e-18)",yscale="log",xscale="symlog")
        ax.set_xlim(0,550)
        ax.set_xticks([0,1,10,100,500]);ax.set_xticklabels(["0","1","10","100","500"])
        ax.grid(alpha=.2);ax.legend(fontsize=8);ax.spines[["top","right"]].set_visible(False)
    fig.suptitle(f"Stage 1 sampled identity checks | {len(rows)}/{len(rows)} passed",fontsize=16)
    fig.supxlabel("Maximum across recorded trials at each degree. Exact zeros use a plotting floor. These checks are not a universal proof.",fontsize=9)
    output=root/"figures/stage1/mathematical_checks.png"
    fig.savefig(output,dpi=160);plt.close(fig)
    print(f"Plotted {len(rows)} recorded passing checks: {output}")


if __name__=="__main__":main()
