"""A deliberately small data language for untrusted conjecture proposals.

Coefficients describe sum(c[k] * N**k); N is the polygon vertex count.
No arbitrary expression parser, eval, exec or dynamically supplied code.
"""

from fractions import Fraction
import re

FIELDS = {"schema_version", "id", "target", "coefficients", "fit_vertices",
          "test_vertices", "source", "description"}
RATIONAL = re.compile(r"[+-]?\d{1,12}(?:/[1-9]\d{0,11})?\Z", re.ASCII)


def _sizes(value: object, label: str) -> list[int]:
    if (not isinstance(value, list) or not 1 <= len(value) <= 5
            or any(type(n) is not int or not 3 <= n <= 7 for n in value)
            or sorted(set(value)) != value):
        raise ValueError(f"{label} must be distinct increasing integers in 3..7")
    return value


def validate_candidate(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError("Candidate has missing or unknown fields")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("Only candidate schema_version 1 is supported")
    if not isinstance(value["id"], str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", value["id"]):
        raise ValueError("Candidate id must be 1–64 alphanumeric, underscore or dash characters")
    if value["target"] not in ("vertices", "facets"):
        raise ValueError("Supported targets: vertices, facets")
    if value["source"] not in ("template", "ollama", "manual"):
        raise ValueError("Supported proposal sources: template, ollama, manual")
    if not isinstance(value["description"], str) or not 1 <= len(value["description"]) <= 1000:
        raise ValueError("Description must be 1–1000 characters")
    coeffs = value["coefficients"]
    if (not isinstance(coeffs, list) or not 1 <= len(coeffs) <= 6
            or any(not isinstance(c, str) or not RATIONAL.fullmatch(c) for c in coeffs)):
        raise ValueError("Need 1–6 short exact rational coefficient strings; no code or expressions")
    # Constructing Fractions is safe only after length and syntax bounds are checked.
    normalized = [str(Fraction(c)) for c in coeffs]
    fit = _sizes(value["fit_vertices"], "fit_vertices")
    held_out = _sizes(value["test_vertices"], "test_vertices")
    if set(fit) & set(held_out) or min(held_out) <= max(fit):
        raise ValueError("Held-out sizes must be larger than all fitting sizes")
    return {**value, "coefficients": normalized, "fit_vertices": list(fit),
            "test_vertices": list(held_out)}


def predict(candidate: dict, vertices: int) -> Fraction:
    return sum((Fraction(c) * vertices**power for power, c in enumerate(candidate["coefficients"])),
               start=Fraction(0))
