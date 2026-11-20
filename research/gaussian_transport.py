"""Affine transports separating a Gaussian conditional block.

For ``x ~ N(mean, covariance)`` and ``z ~ N(0, I)``, each returned map has
the form ``x = matrix @ z + bias``. Its ``inverse`` sends ``x`` back to the
standard-normal block. The conditional precision is the inverse covariance,
so pass the inverted precision when starting from a precision matrix.
Symbolic entries are kept when available; an irreducible 3D eigenproblem
falls back to a high-precision numerical diagonalization.
"""

from __future__ import annotations

import sympy as sp
from sympy.matrices.exceptions import MatrixError, NonPositiveDefiniteMatrixError


def _column(values, name: str) -> sp.Matrix:
    vector = sp.Matrix(values)
    if vector.rows == 1 and vector.cols > 1:
        vector = vector.T
    if vector.cols != 1 or vector.rows not in (2, 3):
        raise ValueError(f"{name} must be a 2- or 3-dimensional column vector")
    return vector


def _covariance(values) -> sp.Matrix:
    matrix = sp.Matrix(values)
    if matrix.shape not in ((2, 2), (3, 3)):
        raise ValueError("covariance must be a 2x2 or 3x3 matrix")
    if sp.simplify(matrix - matrix.T) != sp.zeros(*matrix.shape):
        raise ValueError("covariance must be symmetric")
    try:
        matrix.cholesky()
    except NonPositiveDefiniteMatrixError as exc:
        raise ValueError("covariance must be positive definite") from exc
    return matrix


def _orthonormal_columns(matrix: sp.Matrix) -> sp.Matrix:
    columns = []
    for index in range(matrix.cols):
        vector = matrix[:, index]
        for basis in columns:
            vector -= basis * (basis.T * vector)[0]
        length = sp.sqrt(sp.simplify((vector.T * vector)[0]))
        if length != 0:
            columns.append(sp.simplify(vector / length))
    if len(columns) != matrix.rows:
        raise ValueError("covariance eigendecomposition is incomplete")
    return sp.Matrix.hstack(*columns)


def _symmetric_sqrt(matrix: sp.Matrix) -> sp.Matrix:
    try:
        eigenvectors, eigenvalues = matrix.diagonalize(
            normalize=True, reals_only=True, sort=True
        )
    except MatrixError:
        eigenvectors, eigenvalues = matrix.evalf(30).diagonalize(
            normalize=True, reals_only=True, sort=True
        )
    basis = _orthonormal_columns(eigenvectors)
    roots = sp.diag(*[sp.sqrt(eigenvalues[i, i]) for i in range(matrix.rows)])
    result = basis * roots * basis.T
    result = (result + result.T) / 2
    return result.applyfunc(sp.simplify)


def _map_payload(matrix: sp.Matrix, bias: sp.Matrix) -> dict:
    inverse = matrix.inv()
    return {
        "matrix": matrix,
        "bias": bias,
        "inverse": {
            "matrix": inverse,
            "bias": sp.simplify(-inverse * bias),
        },
    }


def gaussian_affine_transports(mean, covariance) -> dict:
    """Return symmetric Brenier and triangular Knothe-Rosenblatt maps.

    The Brenier matrix is the symmetric positive-definite square root of the
    covariance. The Knothe-Rosenblatt matrix is its lower Cholesky factor.
    Both maps send a standard-normal block to the Gaussian block; their
    ``inverse`` entries whiten the Gaussian block back to standard normal.
    """
    bias = _column(mean, "mean")
    covariance = _covariance(covariance)
    if covariance.rows != bias.rows:
        raise ValueError("mean and covariance dimensions must agree")
    return {
        "dimension": bias.rows,
        "brenier": _map_payload(_symmetric_sqrt(covariance), bias),
        "knothe_rosenblatt": _map_payload(covariance.cholesky(), bias),
    }
