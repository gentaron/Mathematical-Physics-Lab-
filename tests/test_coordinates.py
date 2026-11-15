"""Exact coordinates and boundary residues for the 5-point cosmohedron type."""

from copy import deepcopy

import sympy as sp

from research.positive_geometry.coordinates import (
    canonical_rational_function, compatible_cycle, export_json,
    rational_realization, verify_canonical_form,
)


def test_polygon_is_exact_and_has_correct_labelled_face_incidence():
    obj = rational_realization()
    assert obj["n"] == 5
    assert obj["dimension"] == 2
    assert len(obj["vertices"]) == len(obj["facets"]) == 10
    assert obj["rational_area"] > 0
    assert all(isinstance(x, sp.Rational) for xy in obj["vertices"] for x in xy)
    assert len(set(f["chords"] for f in obj["facets"])) == 10
    assert sorted(len(f["chords"]) for f in obj["facets"]) == [1] * 5 + [2] * 5

    incidence = [0] * 10
    for facet in obj["facets"]:
        assert len(facet["incident_vertices"]) == 2
        for i in facet["incident_vertices"]:
            incidence[i] += 1
        a, b, c = facet["coefficients"]
        slacks = [a * x + b * y + c for x, y in obj["vertices"]]
        assert all(v >= 0 for v in slacks)
        assert sum(v == 0 for v in slacks) == 2
    assert incidence == [2] * 10
    cycle = compatible_cycle()
    assert len(set(cycle)) == 5


def test_canonical_form_has_correct_logarithmic_boundary_poles():
    obj = rational_realization()
    assert verify_canonical_form(obj)
    x, y = sp.symbols("X Y")
    canonical = canonical_rational_function(obj)
    assert canonical.subs({x: sp.Rational(1), y: sp.Rational(1)}) > 0


def test_canonical_form_invariant_under_positive_facet_scalings():
    obj = rational_realization()
    scaled = dict(obj)
    factors = [sp.Rational(i + 1, 3) for i in range(10)]
    scaled["facets"] = tuple(
        dict(f, coefficients=tuple(z * factors[i] for z in f["coefficients"]))
        for i, f in enumerate(obj["facets"])
    )
    assert sp.cancel(canonical_rational_function(scaled) -
                     canonical_rational_function(obj)) == 0


def test_json_export_preserves_exact_rational_coordinates(tmp_path):
    target = tmp_path / "actual-decagon.json"
    import json
    assert export_json(target) == target
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert len(payload["vertices"]) == 10
    assert len(payload["facets"]) == 10
    assert payload["verified"]["all_ten_facet_logarithmic_residues_nonzero"]
    assert "not_claimed" in payload
