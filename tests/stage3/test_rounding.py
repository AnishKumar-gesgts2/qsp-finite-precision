import sys
import unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'experiments/stage3'))
from qsp_finite_precision.stage3 import quantize, nearest_index
from qsp_finite_precision.stage1.forward import evaluate_qsp
from run import response


class RoundingTests(unittest.TestCase):
    def test_ties_and_wrap(self):
        np.testing.assert_array_equal(nearest_index(np.array([-1.5, -.5, .5, 1.5])), [-1, 0, 1, 2])
        step = 2*np.pi/4096
        words, _, e = quantize(np.array([0., 2*np.pi, -step*.25, 2*np.pi-step*.25]), 12, 'nearest')
        np.testing.assert_array_equal(words, [0, 0, 0, 0])
        self.assertTrue(np.all(np.abs(e) <= step/2 + 1e-14))

    def test_grid_sum_and_carry(self):
        rng = np.random.default_rng(123)
        p = rng.uniform(-10, 10, 500)
        for bits in (12, 16, 20, 24, 28, 32):
            step=2*np.pi/(1 << bits)
            for scheme in ('nearest','corrected','sigma_delta'):
                words, rounded, e=quantize(p,bits,scheme)
                np.testing.assert_array_equal(rounded, words*step)
                self.assertTrue(np.all((words >= 0) & (words < 1 << bits)))
                if scheme != 'nearest':
                    self.assertLessEqual(abs(sum(e)), step*.5001 + 1e-13)
                if scheme == 'nearest':
                    self.assertLessEqual(max(abs(e)), step*.5001 + 1e-13)
                if scheme == 'sigma_delta':
                    self.assertLessEqual(max(abs(np.cumsum(e))), step*.5001 + 1e-13)

    def test_fast_response_matches_full_matrix(self):
        rng=np.random.default_rng(4)
        p=rng.normal(size=(4,51)); x=np.r_[-1,1,rng.uniform(-1,1,30)]
        a,b=response(p,x)
        for i in range(len(p)):
            u,_=evaluate_qsp(p[i],x)
            np.testing.assert_allclose(a[i],u[:,0,0],atol=2e-14)
            np.testing.assert_allclose(b[i],u[:,0,1],atol=2e-14)
        u0,_=evaluate_qsp(p[0],x); u1,_=evaluate_qsp(p[1],x)
        measured=np.linalg.norm(u1-u0,ord=2,axis=(-2,-1))
        np.testing.assert_allclose(measured,np.sqrt(abs(a[1]-a[0])**2+abs(b[1]-b[0])**2),atol=2e-14)


if __name__ == '__main__': unittest.main()
