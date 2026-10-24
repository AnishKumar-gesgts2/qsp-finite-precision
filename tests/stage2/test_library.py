"""Scientific target/domain checks, convergence failure, and archive integrity."""

import copy
import hashlib
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
    def test_full_grid_report_verification_and_inconsistent_results(self):
        """Synthetic reports stay in a temporary directory; no runtime evidence."""
        path=Path(__file__).resolve().parents[2]/"experiments/stage2/verify_matlab.py"
        spec=importlib.util.spec_from_file_location("stage2_report_fixture",path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        target=build_target("cosine",10)
        case,curves,audit,_=generate_case(target)
        phases=case["python_qsppack"]["phases"]
        x=curves["x"];ax=audit["x"]
        _,P=evaluate_qsp(phases,x);_,A=evaluate_qsp(phases,ax)
        entry=dict(case_id=case["case_id"],parity=0,coefficients=target["coefficients"][::2],
                   audit_x=ax.tolist(),validation_x=x.tolist())
        convention=dict(case_id="fixture__real",name="fixture",targetPre=True,typePhi="full",x=ax.tolist())
        request=dict(source_revision="TEST_FIXTURE",expected_source_hashes={"fixture":"not-runtime-evidence"},
                     criteria=1e-12,cases=[entry],convention_cases=[convention])
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"results/stage2").mkdir(parents=True)
            (root/"results/stage1").mkdir(parents=True)
            (root/"data/phases/stage2").mkdir(parents=True)
            write_case(root/f"data/phases/stage2/{case['case_id']}.json",case)
            (root/"results/stage1/solver_comparisons.json").write_text(json.dumps(dict(examples=[dict(
                name="fixture",degree=10,chebyshev_coefficients=target["coefficients"])])))
            request_path=root/"results/stage2/matlab_input.json"
            request_path.write_text(json.dumps(request))
            output=dict(case_id=case["case_id"],full_phases=phases,audit_x=ax.tolist(),response=A.real.tolist(),
                        validation_x=x.tolist(),validation_response=P.real.tolist(),solver_value=0.,iterations=4,
                        targetPre=True,typePhi="full")
            report=dict(runtime="MATLAB",runtime_version="TEST FIXTURE - NOT EXECUTION EVIDENCE",
                        source_revision=request["source_revision"],source_hashes=request["expected_source_hashes"],
                        input_sha256=hashlib.sha256(request_path.read_bytes()).hexdigest(),cases=[output],
                        convention_cases=[dict(case_id="fixture__real",full_phases=phases,x=ax.tolist(),
                                               response=A.real.tolist(),solver_value=0.,iterations=4,targetPre=True,typePhi="full")])
            checked=module.verify_matlab(root,report)
            self.assertTrue(checked["passed"])
            self.assertEqual(checked["cases"][0]["evaluator_agreement"]["max_abs"],0.)
            mutations=[lambda r:r["cases"][0]["validation_response"].__setitem__(0,.123),
                       lambda r:r["cases"][0]["validation_x"].pop(),
                       lambda r:r["cases"][0]["full_phases"].pop(),
                       lambda r:r["cases"][0].__setitem__("solver_value",1e-3),
                       lambda r:r["convention_cases"][0].__setitem__("targetPre",False),
                       lambda r:r["cases"].append(copy.deepcopy(r["cases"][0]))]
            for mutate in mutations:
                bad=copy.deepcopy(report);mutate(bad)
                with self.assertRaises(ValueError):module.verify_matlab(root,bad)

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
            with self.assertRaisesRegex(ValueError,"input identity"):
                module.verify_matlab(root,dict(runtime="MATLAB",runtime_version="test fixture",source_revision="expected",
                                              source_hashes={"function":"hash"},input_sha256="stale request"))


if __name__=="__main__":
    unittest.main()
