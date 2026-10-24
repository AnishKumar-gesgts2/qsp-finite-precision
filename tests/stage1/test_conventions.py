"""Convention identities and optional installed-package integration checks."""

import importlib.util
import unittest

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal

from qsp_finite_precision.stage1 import (
    evaluate_qsp, expand_symmetric_phases, qsppack_full_phases,
)


class ConventionTests(unittest.TestCase):
    def test_even_odd_and_degree_zero_expansion(self):
        assert_array_equal(expand_symmetric_phases([.1, .2, .3], 0), [.3, .2, .2, .2, .3])
        assert_array_equal(expand_symmetric_phases([.1, .2, .3], 1), [.3, .2, .1, .1, .2, .3])
        assert_array_equal(expand_symmetric_phases([.1], 0), [.2])

    def test_endpoint_shift_rotates_amplitude(self):
        # Works without assuming symmetry, including coincident degree-zero ends.
        for phases in ([.2], [.2, -.4], [.2, -.4, .7]):
            x = [-1, -.31, 0, .72, 1]
            _, P = evaluate_qsp(phases, x)
            shifted = np.array(phases)
            shifted[0] -= np.pi / 4
            shifted[-1] -= np.pi / 4
            _, shifted_P = evaluate_qsp(shifted, x)
            assert_allclose(shifted_P, -1j * P, atol=1e-14, rtol=0)
            assert_allclose(shifted_P.real, P.imag, atol=1e-14, rtol=0)

    def test_mapping_validation_and_no_mutation(self):
        p = np.array([.1, .2])
        for parity in (0, 1):
            for target_pre in (False, True):
                full = qsppack_full_phases(p, parity, target_pre=target_pre, type_phi="reduced")
                assert_array_equal(p, [.1, .2])
                saved = full.copy()
                copied = qsppack_full_phases(full, parity, target_pre=target_pre, type_phi="full")
                copied[0] += 1
                assert_array_equal(full, saved)
        for bad in ([], [[.1]], [.1j], [np.nan]):
            with self.assertRaises(ValueError):
                expand_symmetric_phases(bad, 0)
        for bad in (True, -1, 2):
            with self.assertRaises(ValueError):
                expand_symmetric_phases([.1], bad)
        with self.assertRaises(ValueError):
            qsppack_full_phases([.1, .2], 0, target_pre=True, type_phi="full")
        with self.assertRaises(ValueError):
            qsppack_full_phases(p, 0, target_pre=True, type_phi="other")
        with self.assertRaises(TypeError):
            qsppack_full_phases(p, 0, target_pre=1, type_phi="reduced")


@unittest.skipUnless(importlib.util.find_spec("pyqsp"), "install the validation extra")
class PyqspIntegrationTests(unittest.TestCase):
    def test_complex_readout_and_measurement_basis(self):
        from pyqsp.response import ComputeQSPResponse
        rng = np.random.default_rng(20261023)
        x = np.array([.31, -1, 0, -.73, 1])
        for degree in (0, 1, 2, 9, 30):
            phases = rng.uniform(-np.pi, np.pi, degree + 1)
            U, P = evaluate_qsp(phases, x)
            z = ComputeQSPResponse(x, phases, signal_operator="Wx", measurement="z")["pdat"]
            symmetric_readout = ComputeQSPResponse(x, phases, signal_operator="Wx", sym_qsp=True)["pdat"]
            x_readout = ComputeQSPResponse(x, phases, signal_operator="Wx", measurement="x")["pdat"]
            assert_allclose(P, z, atol=5e-13, rtol=0)
            assert_allclose(P, symmetric_readout, atol=5e-13, rtol=0)
            assert_allclose(.5 * U.sum(axis=(1, 2)), x_readout, atol=5e-13, rtol=0)

    def test_symmetric_expansion_and_full_unitary(self):
        from pyqsp.sym_qsp_opt import SymmetricQSPProtocol
        for parity in (0, 1):
            for reduced in ([.17], [.17, -.29, .43]):
                protocol = SymmetricQSPProtocol(reduced_phases=reduced, parity=parity)
                full = expand_symmetric_phases(reduced, parity)
                assert_allclose(full, protocol.full_phases, atol=1e-15, rtol=0)
                U, _ = evaluate_qsp(full, [-1, -.4, 0, .7, 1])
                assert_allclose(U, protocol.gen_unitary([-1, -.4, 0, .7, 1]), atol=5e-13, rtol=0)


@unittest.skipUnless(importlib.util.find_spec("qsppack"), "install the validation extra")
class QsppackIntegrationTests(unittest.TestCase):
    def test_full_reduced_real_imaginary_mapping(self):
        from qsppack.utils import get_entry, reduced_to_full
        x = np.array([.31, -1, 0, -.73, 1])
        for parity in (0, 1):
            for reduced in ([.17], [.17, -.29, .43]):
                for target_pre in (False, True):
                    full = qsppack_full_phases(reduced, parity, target_pre=target_pre, type_phi="reduced")
                    assert_allclose(full, reduced_to_full(reduced, parity, target_pre), atol=1e-15, rtol=0)
                    _, P = evaluate_qsp(full, x)
                    actual = P.real if target_pre else P.imag
                    for type_phi, phases in (("full", full), ("reduced", np.array(reduced))):
                        before = phases.copy()
                        opts = dict(parity=parity, targetPre=target_pre, typePhi=type_phi)
                        reference = get_entry(x, phases, opts)
                        assert_allclose(actual, reference, atol=5e-13, rtol=0)
                        assert_array_equal(phases, before)


if __name__ == "__main__":
    unittest.main()
