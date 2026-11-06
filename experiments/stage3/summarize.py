"""Summarize existing Stage 3 outputs without rerunning circuit evaluation."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SCHEMES = ('nearest', 'corrected', 'sigma_delta')
LABELS = ('Nearest', 'Last-phase correction', 'Sigma-delta')


def main():
    out = ROOT / 'results/stage3'
    fig = ROOT / 'figures/stage3'
    rows = list(csv.DictReader((out / 'measurements.csv').open(encoding='utf8')))
    diagnostics = []
    for row in rows:
        path = ROOT / 'data/quantized/stage3' / (
            f"{row['case_id']}_{row['solver']}_{row['bits']}_{row['scheme']}.json")
        data = json.loads(path.read_text(encoding='utf8'))
        errors = np.asarray(data['phase_errors'])
        h = data['step']
        diagnostics.append(dict(case_id=row['case_id'], solver=row['solver'],
            bits=int(row['bits']), scheme=row['scheme'],
            max_phase_error_steps=float(np.max(np.abs(errors)) / h),
            max_prefix_error_steps=float(np.max(np.abs(np.cumsum(errors))) / h),
            total_error_steps=float(np.sum(errors) / h),
            endpoint_unitary_from_sum=float(2 * abs(np.sin(np.sum(errors) / 2)))))
    with (out / 'quantization_diagnostics.csv').open('w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=diagnostics[0], lineterminator='\n')
        writer.writeheader()
        writer.writerows(diagnostics)

    f, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True, constrained_layout=True)
    for scheme, label in zip(SCHEMES, LABELS):
        data = json.loads((ROOT / 'data/quantized/stage3' /
            f'cosine_d0500_pyqsp_16_{scheme}.json').read_text(encoding='utf8'))
        normalized = np.asarray(data['phase_errors']) / data['step']
        style = dict(label=label, lw=2 if scheme=='nearest' else 1.1,
                     ls='--' if scheme=='corrected' else '-', alpha=.9)
        axes[0].plot(normalized, **style)
        axes[1].plot(np.cumsum(normalized), **style)
    for ax in axes:
        ax.axhline(.5, color='black', ls=':', lw=1)
        ax.axhline(-.5, color='black', ls=':', lw=1)
        ax.grid(alpha=.2)
    axes[0].set_ylabel('Individual phase error / grid step')
    axes[0].legend(fontsize=8)
    axes[1].set(xlabel='Phase index (zero based)', ylabel='Cumulative phase error / grid step')
    f.suptitle('Cosine degree 500, pyqsp, 16 bits: stored phase errors\n'
               'Dotted lines: half a grid step; sum correction changes only the last phase')
    f.savefig(fig / 'rounding_diagnostics.png', dpi=150)
    plt.close(f)

    f, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True, constrained_layout=True)
    for ax, family in zip(axes, ('cosine', 'sine', 'sign')):
        degree = max(int(r['degree']) for r in rows if r['family'] == family)
        for scheme, label in zip(SCHEMES, LABELS):
            chosen = sorted((r for r in rows if r['family'] == family and
                int(r['degree']) == degree and r['solver'] == 'pyqsp' and
                r['scheme'] == scheme), key=lambda r: int(r['bits']))
            ax.semilogy([int(r['bits']) for r in chosen],
                        [float(r['unitary_max']) for r in chosen], 'o-', label=label)
        ax.set(title=f'{family}, degree {degree}', xlabel='Bits per phase', xticks=[12, 16, 20, 24, 28, 32])
        ax.grid(which='both', alpha=.2)
    axes[0].set_ylabel('Sampled max unitary storage error')
    axes[0].legend(fontsize=8)
    f.suptitle('Precision sweep on fixed pyqsp phase lists')
    f.savefig(fig / 'precision_sweep.png', dpi=150)
    plt.close(f)

    groups = {}
    for row in rows:
        key = (row['case_id'], row['solver'], row['scheme'])
        groups.setdefault(key, {})[int(row['bits'])] = float(row['unitary_max'])
    summary = dict(configurations=len(rows), fixed_list_groups=len(groups),
        groups_with_32bit_less_than_12bit=sum(g[32] < g[12] for g in groups.values()),
        maximum_32bit_sampled_unitary_error=max(g[32] for g in groups.values()),
        max_sigma_delta_prefix_error_steps=max(d['max_prefix_error_steps'] for d in diagnostics
            if d['scheme'] == 'sigma_delta'),
        max_corrected_total_error_steps=max(abs(d['total_error_steps']) for d in diagnostics
            if d['scheme'] == 'corrected'),
        scope='Sampled binary64 storage errors; no fixed-difficulty degree-scaling fit or full Stage 4/5 claim.')
    (out / 'interpretation.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
