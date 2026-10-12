"""A free deterministic baseline; optional neural proposals live in ollama.py."""

import sympy as sp

from .hypothesis import validate_candidate
from .positive_geometry.cosmohedron import recurrence_vector


def count_target(target: str, vertices: int) -> int:
    counts = recurrence_vector(vertices)
    if target == "vertices":
        return counts[-1]
    if target == "facets":
        return counts[1] if vertices > 3 else 0
    raise ValueError("Unknown sequence target")


def propose(fit_vertices: list[int], test_vertices: list[int]) -> list[dict]:
    """Fit a low-degree polynomial, then ask the evaluator to try to refute it.

    This is hypothesis generation, not an AI model or a novelty detector.
    """
    proposals = []
    variable = sp.Symbol("N")
    for target in ("vertices", "facets"):
        # Validate the input sizes before any symbolic interpolation.
        base = validate_candidate({"schema_version": 1, "id": f"poly-{target}",
            "target": target, "coefficients": ["0"], "fit_vertices": fit_vertices,
            "test_vertices": test_vertices, "source": "template",
            "description": "Polynomial interpolation baseline; attempt to refute extrapolation"})
        polynomial = sp.Poly(sp.interpolate(
            [(n, count_target(target, n)) for n in fit_vertices], variable), variable)
        base["coefficients"] = [str(polynomial.nth(k)) for k in range(len(fit_vertices))]
        proposals.append(validate_candidate(base))
    return proposals
