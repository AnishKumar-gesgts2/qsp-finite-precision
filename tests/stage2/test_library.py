"""Scientific target/domain checks, convergence failure, and archive integrity."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal

from qsp_finite_precision.stage1 import evaluate_qsp
from qsp_finite_precision.stage2 import build_target, generate_case, load_case, write_case
from qsp_finite_precision.stage2.targets import application_mask, global_bound, target_values, validation_grid


class TargetTests(unittest.TestCase):
    def test_jacobi_anger_even_odd_targets_and_accuracy(self):
        for family,degree in (("cosine",10),("sine",11)):
            target=build_target(family,degree)
            c=np.asarray(target["coefficients"])
            assert_array_equal(c[1-target["parity"]::2],0)
            self.assertNotEqual(c[-1],0)
            x=np.linspace(-1,1,10001)
            p=np.polynomial.chebyshev.chebval(x,c)
            self.assertLess(np.max(np.abs(p-target_values(target,x))),5.01e-8)
            self.assertLess(target["boundedness"]["upper_estimate"],1)

    def test_sign_is_measured_against_sign_not_erf(self):
        target=build_target("sign",11)
        gap=target["parameters"]["gap"]
        x=np.array([-1,-gap,-gap/2,0,gap/2,gap,1])
        assert_array_equal(application_mask(target,x),[1,1,0,0,0,1,1])
        assert_allclose(target_values(target,x),.9*np.sign(x),rtol=0,atol=0)
        self.assertLessEqual(target["boundedness"]["upper_estimate"],.9)
        grid=validation_grid(target)
        self.assertTrue(np.any(grid==gap) and np.any(grid==-gap) and np.any(grid==0))
        c=target["coefficients"]
        mask=application_mask(target,grid)
        self.assertLess(np.max(np.abs(np.polynomial.chebyshev.chebval(grid,c)[mask]-.9*np.sign(grid[mask]))),1e-2)

    def test_between_node_bound_against_stationary_points(self):
        rng=np.random.default_rng(20261023)
        for degree in (2,7,14):
            c=rng.normal(size=degree+1)/20
            roots=np.polynomial.chebyshev.chebroots(np.polynomial.chebyshev.chebder(c))
            stationary=np.array([r.real for r in roots if abs(r.imag)<1e-12 and abs(r.real)<1])
            exact_candidates=np.r_[-1.,stationary,1.]
            maximum=np.max(np.abs(np.polynomial.chebyshev.chebval(exact_candidates,c)))
            bound=global_bound(c)
            self.assertGreaterEqual(bound["upper_estimate"],maximum)
        for bad in ([1j],[],[[1]], [np.inf]):
            with self.assertRaises(ValueError):global_bound(bad)

    def test_invalid_family_parity_and_gap_are_rejected(self):
        for family,degree in (("other",10),("cosine",11),("sine",10),("sign",10),("cosine",True)):
            with self.assertRaises(ValueError):build_target(family,degree)
        with self.assertRaises(ValueError):build_target("sign",11,sign_gap_product=10)


class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.target=build_target("cosine",10)
        cls.case,cls.curves,cls.audit,_=generate_case(cls.target)

    def test_solver_to_saved_phases_to_response_round_trip(self):
        case=self.case
        self.assertTrue(case["passed"] and case["solver"]["converged"])
        self.assertTrue(case["python_qsppack"]["converged"])
        self.assertLess(case["metrics"]["synthesis"]["max_abs"],1e-12)
        self.assertFalse(case["convention"]["quantized"])
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"case.json"
            write_case(path,case)
            loaded=load_case(path)
            assert_array_equal(np.asarray(loaded["full_phases"]).view(np.uint64),np.asarray(case["full_phases"]).view(np.uint64))
            _,P=evaluate_qsp(loaded["full_phases"],[-1,-.12345,0,.6789,1])
            p=np.polynomial.chebyshev.chebval([-1,-.12345,0,.6789,1],loaded["target"]["coefficients"])
            assert_allclose(P.imag,p,atol=1e-12,rtol=0)

    def test_iteration_limit_cannot_be_archived_as_success(self):
        case,_,_,_=generate_case(self.target,maxiter=1)
        self.assertFalse(case["solver"]["converged"])
        self.assertFalse(case["passed"])
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):write_case(Path(folder)/"failed.json",case)

    def test_invalid_archive_phase_count_and_coefficients(self):
        for modify in (lambda c:c["full_phases"].pop(),lambda c:c["target"]["coefficients"].__setitem__(0,float("nan"))):
            case=copy.deepcopy(self.case);modify(case)
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/"bad.json";path.write_text(json.dumps(case))
                with self.assertRaises(ValueError):load_case(path)

    def test_verifier_rejects_tampered_archive_hash(self):
        path=Path(__file__).resolve().parents[2]/"experiments/stage2/verify_library.py"
        spec=importlib.util.spec_from_file_location("stage2_verify",path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/"results/stage2").mkdir(parents=True);(root/"data").mkdir()
            archive=root/"data/case.json";archive.write_text("{}")
            manifest=dict(cases=[dict(case_id="test",file="data/case.json",sha256="wrong")])
            (root/"results/stage2/summary.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,"Archive hash mismatch"):module.verify(root)


class MatlabReportTests(unittest.TestCase):
    def test_non_matlab_runtime_and_unmatched_source_cannot_complete_check(self):
        path=Path(__file__).resolve().parents[2]/"experiments/stage2/verify_matlab.py"
        spec=importlib.util.spec_from_file_location("stage2_verify_matlab",path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/"results/stage2").mkdir(parents=True)
            request=dict(source_revision="expected",expected_source_hashes={"function":"hash"})
            (root/"results/stage2/matlab_input.json").write_text(json.dumps(request))
            with self.assertRaisesRegex(ValueError,"actually used MATLAB runtime"):
                module.verify_matlab(root,dict(runtime="Python",runtime_version="test fixture"))
            with self.assertRaisesRegex(ValueError,"source identity"):
                module.verify_matlab(root,dict(runtime="MATLAB",runtime_version="test fixture",source_revision="wrong"))


if __name__=="__main__":
    unittest.main()
