"""Generate quantized words, sampled response measurements, and figures."""
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from qsp_finite_precision.stage3 import quantize

BITS = (12, 16, 20, 24, 28, 32)
SCHEMES = ('nearest', 'corrected', 'sigma_delta')
CONFIGS = [(b, s) for b in BITS for s in SCHEMES]


def response(phases, x):
    """Batched SU(2) first row, same written product as stage1.forward."""
    phases = np.asarray(phases)
    x = x[None, :]
    s = np.sqrt(np.maximum(0., 1 - x*x))
    a = np.broadcast_to(np.exp(1j*phases[:, 0, None]), (len(phases), x.shape[1])).copy()
    b = np.zeros_like(a)
    for j in range(1, phases.shape[1]):
        z = np.exp(1j*phases[:, j, None])
        a, b = (a*x + 1j*b*s)*z, (1j*a*s + b*x)*z.conj()
    return a, b


def main():
    manifest_path = ROOT / 'results/stage2/summary.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf8'))
    out = ROOT / 'results/stage3'; out.mkdir(parents=True, exist_ok=True)
    qdir = ROOT / 'data/quantized/stage3'; qdir.mkdir(parents=True, exist_ok=True)
    fig = ROOT / 'figures/stage3'; fig.mkdir(parents=True, exist_ok=True)
    rows = []
    for entry in manifest['cases']:
        source = ROOT / entry['file']
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != entry['sha256']:
            raise ValueError(f'baseline hash mismatch: {source}')
        case = json.loads(source.read_text(encoding='utf8'))
        target = case['target']; degree = target['degree']; caseid = case['case_id']
        # 10d+1 Lobatto points, plus sign gap edges for application coverage.
        x = np.cos(np.linspace(0, np.pi, max(10*degree+1, 1025)))
        if target['family'] == 'sign':
            gap = target['parameters']['gap']; x = np.unique(np.r_[x, -gap, gap])
        mask = np.ones(len(x), dtype=bool) if target['family'] != 'sign' else np.abs(x) >= gap
        for solver, key, readout in [('pyqsp', 'full_phases', 'imag'), ('python_qsppack', 'python_qsppack', 'real')]:
            p = np.asarray(case[key] if solver == 'pyqsp' else case[key]['phases'])
            phase_sets = [p]; errors = []
            for bits, scheme in CONFIGS:
                words, rounded, err = quantize(p, bits, scheme)
                errors.append(err); phase_sets.append(rounded)
                obj = dict(schema_version=1, case_id=caseid, solver=solver, source=entry['file'], source_sha256=digest,
                    bits=bits, scheme=scheme, step=float(2*np.pi/(1 << bits)), word_range=f'0..{(1 << bits)-1}',
                    tie='half toward positive infinity in unwrapped grid coordinates',
                    wrap='input and output modulo 2*pi; errors use unwrapped quantizer lift minus wrapped input',
                    correction='last phase chosen so total is nearest grid multiple' if scheme == 'corrected' else None,
                    words=words.tolist(), rounded_phases=rounded.tolist(), phase_errors=err.tolist())
                (qdir / f'{caseid}_{solver}_{bits}_{scheme}.json').write_text(json.dumps(obj, allow_nan=False, separators=(',', ':'))+'\n', encoding='utf8', newline='\n')
            a, b = response(np.array(phase_sets), x)
            da = a[1:] - a[0]; db = b[1:] - b[0]
            unitary = np.sqrt(np.abs(da)**2 + np.abs(db)**2)
            matrix = np.abs(da)
            r = a.imag if readout == 'imag' else a.real
            re = np.abs(r[1:] - r[0])
            np.savez_compressed(out / f'{caseid}_{solver}_curves.npz', x=x, application_mask=mask,
                baseline_readout=r[0], rounded_readout=r[1:], unitary_error=unitary,
                matrix_element_error=matrix, readout_error=re)
            for i, ((bits, scheme), err) in enumerate(zip(CONFIGS, errors)):
                row = dict(case_id=caseid, family=target['family'], degree=degree, solver=solver, readout=readout,
                           bits=bits, scheme=scheme, points=len(x), phase_error_sum=float(np.sum(err)),
                           phase_error_max=float(np.max(np.abs(err))))
                for name, array in [('unitary',unitary[i]),('matrix_element',matrix[i]),('readout',re[i])]:
                    row[name+'_max'] = float(np.max(array)); row[name+'_application_max'] = float(np.max(array[mask]))
                rows.append(row)
            print(caseid, solver, flush=True)
    with (out / 'measurements.csv').open('w', encoding='utf8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
    meta = dict(configurations=CONFIGS, baseline_cases=len(manifest['cases']), lists=2*len(manifest['cases']),
                rows=len(rows), python=platform.python_version(), numpy=np.__version__, matplotlib=matplotlib.__version__,
                grid='max(10*degree+1,1025) Chebyshev-Lobatto; sign adds exact gap edges',
                unitary='operator 2-norm from SU(2) first row; rounded minus baseline',
                note='Sampled binary64 exploratory storage errors; not solver/target error or completed Stage 4/5')
    (out / 'metadata.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf8',newline='\n')
    plot(rows, out, fig)
    # These diagnostics use saved artifacts, and can also be refreshed alone.
    from summarize import main as summarize
    summarize()


def plot(rows, out, fig):
    colors = dict(nearest='C0', corrected='C1', sigma_delta='C2')
    f, axs = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True, constrained_layout=True)
    for ax, family in zip(axs, ('cosine','sine','sign')):
        for scheme in SCHEMES:
            subset = sorted((r for r in rows if r['family']==family and r['solver']=='pyqsp' and r['bits']==16 and r['scheme']==scheme), key=lambda r:r['degree'])
            ax.loglog([r['degree'] for r in subset], [r['unitary_max'] for r in subset], 'o-', label=scheme, color=colors[scheme])
        ax.set(title=family, xlabel='Polynomial degree', ylabel='Sampled max unitary error' if family=='cosine' else None)
        ax.grid(True, which='both', alpha=.25)
    axs[0].legend(fontsize=8); f.suptitle('16-bit storage error vs unrounded pyqsp baseline'); f.savefig(fig/'unitary_error_16bit.png',dpi=150); plt.close(f)
    data=np.load(out/'sign_d0161_pyqsp_curves.npz'); x=data['x']; i=CONFIGS.index((12,'nearest'))
    f, axs=plt.subplots(2,1,figsize=(8,6),sharex=True,constrained_layout=True)
    axs[0].plot(x,data['baseline_readout'],label='Unrounded',lw=1.4)
    axs[0].plot(x,data['rounded_readout'][i],label='12-bit nearest',lw=1,ls='--')
    axs[0].set_ylabel('Imaginary part of U[0,0]'); axs[0].legend()
    axs[1].plot(x,data['rounded_readout'][i]-data['baseline_readout']); axs[1].set(xlabel='Signal x',ylabel='Rounded - baseline')
    for ax in axs: ax.grid(alpha=.25)
    f.suptitle('Sign, degree 161: sampled response comparison'); f.savefig(fig/'sign_response_comparison.png',dpi=150); plt.close(f)


if __name__ == '__main__':
    main()
