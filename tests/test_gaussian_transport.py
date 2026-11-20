"""Affine Gaussian transports for conditional blocks."""

import random

import pytest
import sympy as sp

from research.gaussian_transport import gaussian_affine_transports


CASES = [
    (sp.Matrix([1, -1]), sp.Matrix([[5, 4], [4, 5]])),
    (sp.Matrix([1, -2, sp.Rational(1, 2)]),
     sp.Matrix([[5, 5, 1], [5, 11, 5], [1, 5, 5]])),
]


def _sample_covariance(vectors):
    size = len(vectors)
    dimension = len(vectors[0])
    means = [sum(row[i] for row in vectors) / size for i in range(dimension)]
    return [
        [sum((row[i] - means[i]) * (row[j] - means[j]) for row in vectors) / size
         for j in range(dimension)]
        for i in range(dimension)
    ]


def _assert_covariance_close(actual, expected, tolerance=0.08):
    for i in range(expected.rows):
        for j in range(expected.cols):
            assert abs(actual[i][j] - float(expected[i, j])) < tolerance


def _assert_matrix_close(actual, expected, tolerance=1e-9):
    difference = actual - expected
    for i in range(expected.rows):
        for j in range(expected.cols):
            assert sp.Abs(sp.N(difference[i, j])) < tolerance


@pytest.mark.parametrize("mean,covariance", CASES)
def test_maps_reproduce_covariance_and_invert_exactly(mean, covariance):
    transports = gaussian_affine_transports(mean, covariance)
    for name in ("brenier", "knothe_rosenblatt"):
        block = transports[name]
        matrix, bias = block["matrix"], block["bias"]
        inverse, inverse_bias = block["inverse"]["matrix"], block["inverse"]["bias"]
        _assert_matrix_close(matrix * matrix.T, covariance)
        _assert_matrix_close(inverse * matrix, sp.eye(covariance.rows))
        _assert_matrix_close(inverse * bias, -inverse_bias)
    brenier = transports["brenier"]["matrix"]
    triangular = transports["knothe_rosenblatt"]["matrix"]
    _assert_matrix_close(brenier, brenier.T)
    assert all(triangular[i, j] == 0 for i in range(triangular.rows)
               for j in range(i + 1, triangular.cols))


def test_standard_normal_block_whitens_and_round_trips():
    rng = random.Random(20261119)
    covariance = sp.Matrix([
        [2, sp.Rational(1, 2), 0],
        [sp.Rational(1, 2), 1, sp.Rational(1, 4)],
        [0, sp.Rational(1, 4), sp.Rational(3, 2)],
    ])
    mean = [1.0, -0.5, 0.25]
    transports = gaussian_affine_transports(mean, covariance)
    standard_normal = [[rng.gauss(0.0, 1.0) for _ in range(3)] for _ in range(8000)]

    for name in ("brenier", "knothe_rosenblatt"):
        block = transports[name]
        matrix = [[float(block["matrix"][i, j]) for j in range(3)] for i in range(3)]
        bias = [float(block["bias"][i]) for i in range(3)]
        inverse = [[float(block["inverse"]["matrix"][i, j]) for j in range(3)] for i in range(3)]
        inverse_bias = [float(block["inverse"]["bias"][i]) for i in range(3)]
        samples, separated, error = [], [], 0.0
        for row in standard_normal:
            x = [sum(matrix[i][j] * row[j] for j in range(3)) + bias[i] for i in range(3)]
            z = [sum(inverse[i][j] * x[j] for j in range(3)) + inverse_bias[i] for i in range(3)]
            samples.append(x)
            separated.append(z)
            error = max(error, max(abs(z[i] - row[i]) for i in range(3)))
        assert error < 1e-9
        _assert_covariance_close(_sample_covariance(separated), sp.eye(3))
        _assert_covariance_close(_sample_covariance(samples), covariance, tolerance=0.1)


def test_invalid_dimensions_and_covariances_are_rejected():
    with pytest.raises(ValueError):
        gaussian_affine_transports([0], [[1]])
    with pytest.raises(ValueError):
        gaussian_affine_transports([0, 0], [[1, 0], [0, 1, 0]])
    with pytest.raises(ValueError):
        gaussian_affine_transports([0, 0, 0], [[1, 0], [0, 1]])
    with pytest.raises(ValueError):
        gaussian_affine_transports([0, 0], [[1, 1], [0, 1]])
    with pytest.raises(ValueError):
        gaussian_affine_transports([0, 0], [[1, 2], [2, 1]])
