"""Core evaluator checks only; full Stage 1 Part B validation is pending."""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from qsp_finite_precision.stage1 import evaluate_qsp


class ForwardTests(unittest.TestCase):
    def test_degree_zero(self):
        U, P = evaluate_qsp([0.37], [-1, 0, 1])
        expected = np.diag([np.exp(0.37j), np.exp(-0.37j)])
        assert_allclose(U, np.tile(expected, (3, 1, 1)), atol=1e-14)
        assert_allclose(P, np.exp(0.37j), atol=1e-14)

    def test_degree_one_full_matrix(self):
        a, b = 0.23, -0.61
        x = np.array([-1, -0.4, 0, 0.8, 1])
        U, P = evaluate_qsp([a, b], x)
        expected = np.empty_like(U)
        expected[:, 0, 0] = x * np.exp(1j * (a + b))
        expected[:, 1, 1] = x * np.exp(-1j * (a + b))
        expected[:, 0, 1] = 1j * np.sqrt(1 - x*x) * np.exp(1j * (a - b))
        expected[:, 1, 0] = 1j * np.sqrt(1 - x*x) * np.exp(-1j * (a - b))
        assert_allclose(U, expected, atol=1e-14, rtol=0)
        assert_allclose(P, expected[:, 0, 0], atol=1e-14, rtol=0)

    def test_degree_two_polynomial(self):
        a, b, c = 0.2, 0.7, -0.4
        x = np.linspace(-1, 1, 11)
        _, P = evaluate_qsp([a, b, c], x)
        expected = np.exp(1j * (a + c)) * (
            x*x * np.exp(1j * b) - (1 - x*x) * np.exp(-1j * b)
        )
        assert_allclose(P, expected, atol=1e-14, rtol=0)

    def test_batched_product_against_scalar_rotation_formulas(self):
        # A scalar path uses cos/sin and explicitly written W D entries,
        # rather than batched matrix construction and multiplication.
        phases = [0.13, -0.7, 0.22, 1.1]
        x_values = [0.9, -1, 0.2, 1, -0.6]
        U, _ = evaluate_qsp(phases, x_values)
        for k, x in enumerate(x_values):
            theta = np.arccos(x)
            expected = np.diag(np.exp(1j * np.array([phases[0], -phases[0]])))
            for phi in phases[1:]:
                factor = np.array([
                    [np.cos(theta)*np.exp(1j*phi), 1j*np.sin(theta)*np.exp(-1j*phi)],
                    [1j*np.sin(theta)*np.exp(1j*phi), np.cos(theta)*np.exp(-1j*phi)],
                ])
                expected = expected @ factor
            assert_allclose(U[k], expected, atol=1e-14, rtol=0)

    def test_empty_signal_array(self):
        U, P = evaluate_qsp([0.1, 0.2], [])
        self.assertEqual(U.shape, (0, 2, 2))
        self.assertEqual(P.shape, (0,))
        self.assertEqual(U.dtype, np.complex128)

    def test_invalid_inputs(self):
        for phases in ([], 0.1, [[0.1]], [np.nan], [np.inf], [0.1j], ["0.1"]):
            with self.subTest(phases=phases), self.assertRaises(ValueError):
                evaluate_qsp(phases, [0])
        for x in (0.1, [[0.1]], [np.nan], [np.inf], [1.001], [-1.001], [0.1j], ["0.1"]):
            with self.subTest(x=x), self.assertRaises(ValueError):
                evaluate_qsp([0], x)


if __name__ == "__main__":
    unittest.main()
