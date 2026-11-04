"""Check saved coverage, grid words, error identities, curves, and CSV."""
import csv
import json
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from qsp_finite_precision.stage3 import quantize
from qsp_finite_precision.stage1.forward import evaluate_qsp

rows=list(csv.DictReader((ROOT/'results/stage3/measurements.csv').open(encoding='utf8')))
assert len(rows)==756 and len({(r['case_id'],r['solver'],r['bits'],r['scheme']) for r in rows})==756
manifest=json.loads((ROOT/'results/stage2/summary.json').read_text(encoding='utf8'))
assert len(manifest['cases'])==21
max_csv=0.; max_endpoint=0.; max_eval=0.
for row in rows:
    caseid,solver,bits,scheme=row['case_id'],row['solver'],int(row['bits']),row['scheme']
    source=json.loads((ROOT/f'data/phases/stage2/{caseid}.json').read_text(encoding='utf8'))
    baseline=np.array(source['full_phases'] if solver=='pyqsp' else source['python_qsppack']['phases'])
    artifact=json.loads((ROOT/f'data/quantized/stage3/{caseid}_{solver}_{bits}_{scheme}.json').read_text(encoding='utf8'))
    words,rounded,err=quantize(baseline,bits,scheme)
    np.testing.assert_array_equal(words,artifact['words']); np.testing.assert_array_equal(err,artifact['phase_errors'])
    step=2*np.pi/(1<<bits)
    np.testing.assert_allclose(rounded,artifact['rounded_phases'],rtol=0,atol=0)
    if scheme=='nearest': assert np.max(abs(err)) <= step/2+1e-13
    if scheme=='corrected': assert abs(np.sum(err)) <= step/2+1e-13
    if scheme=='sigma_delta': assert max(abs(np.cumsum(err))) <= step/2+1e-13
    with np.load(ROOT/f'results/stage3/{caseid}_{solver}_curves.npz') as d:
        x=d['x']; mask=d['application_mask']; i=(bits//4-3)*3+('nearest','corrected','sigma_delta').index(scheme)
        assert np.count_nonzero(np.diff(x))==len(x)-1 and len(x)>=10*int(row['degree'])+1
        for metric,key in [('unitary','unitary_error'),('matrix_element','matrix_element_error'),('readout','readout_error')]:
            vals=d[key][i]
            max_csv=max(max_csv,abs(max(vals)-float(row[metric+'_max'])),abs(max(vals[mask])-float(row[metric+'_application_max'])))
        expected=2*abs(np.sin(sum(err)/2))
        end=np.argmin(abs(x-1)); max_endpoint=max(max_endpoint,abs(d['unitary_error'][i,end]-expected))
        if caseid in ('sign_d0499','cosine_d0500') and bits==32 and scheme=='sigma_delta':
            inds=np.linspace(0,len(x)-1,11,dtype=int)
            u0,_=evaluate_qsp(baseline,x[inds]); u1,_=evaluate_qsp(rounded,x[inds])
            actual=np.linalg.norm(u1-u0,ord=2,axis=(-2,-1))
            max_eval=max(max_eval,float(max(abs(actual-d['unitary_error'][i,inds]))))
assert max_csv<1e-18 and max_endpoint<1e-12 and max_eval<1e-12
print(json.dumps(dict(rows=len(rows), quantized_files=len(list((ROOT/'data/quantized/stage3').glob('*.json'))),
    csv_max_difference=max_csv, endpoint_identity_max_difference=max_endpoint,
    high_degree_full_evaluator_max_difference=max_eval),indent=2))
