"""Exact 5-point cosmohedron-type convex polygon with labelled facets.

The 5-point cosmohedron is combinatorially a decagon obtained by
truncating the pentagonal associahedron. This module builds ONE rational
coordinate realization and its true canonical logarithmic 2-form.

This is not the distinguished coordinate/kinematics realization from the
physics paper. Numerical agreement or structural equivalence does not
establish the cosmological wavefunction/canonical form of that realization.
"""
from __future__ import annotations

from itertools import permutations
import json
from pathlib import Path

import sympy as sp

from .cosmohedron import codimension_vector

PolygonPoint = tuple[sp.Rational, sp.Rational]
Chord = tuple[int, int]


def chords() -> tuple[Chord, ...]:
    return tuple(
        (a, b) for a in range(1, 6) for b in range(a + 1, 6)
        if b - a > 1 and (a, b) != (1, 5)
    )


def crosses(first: Chord, second: Chord) -> bool:
    a, b = first
    c, d = second
    return (a < c < b < d) or (c < a < d < b)


def compatible_cycle() -> tuple[Chord, ...]:
    """Assign the pentagon's five edges cyclically to compatible diagonals."""
    ds = chords()
    assert len(ds) == 5
    for perm in permutations(ds[1:]):
        cycle = (ds[0],) + perm
        if all(not crosses(cycle[i], cycle[(i + 1) % 5]) for i in range(5)):
            return cycle
    raise AssertionError("The pentagon associahedron compatibility graph is not a 5-cycle")


def rational_realization() -> dict:
    q = sp.Rational
    pentagon: tuple[PolygonPoint, ...] = (
        (q(0), q(0)), (q(2), q(0)), (q(3), q(1)),
        (q(2), q(2)), (q(0), q(2)),
    )
    step = q(1, 4)

    def toward(p: PolygonPoint, target: PolygonPoint) -> PolygonPoint:
        return (
            p[0] + step * (target[0] - p[0]),
            p[1] + step * (target[1] - p[1]),
        )

    vertices: list[PolygonPoint] = []
    for i, p in enumerate(pentagon):
        vertices += [
            toward(p, pentagon[(i - 1) % 5]),
            toward(p, pentagon[(i + 1) % 5]),
        ]
    assert len(vertices) == len(set(vertices)) == 10
    cycle = compatible_cycle()

    facets = []
    for i, p in enumerate(vertices):
        nxt = vertices[(i + 1) % 10]
        dx, dy = nxt[0] - p[0], nxt[1] - p[1]
        a, b, c = -dy, dx, dy * p[0] - dx * p[1]
        slacks = [a * vx + b * vy + c for vx, vy in vertices]
        assert all(s >= 0 for s in slacks), (i, slacks)
        assert sum(s == 0 for s in slacks) == 2
        if i % 2 == 0:
            j = i // 2
            label = tuple(sorted((cycle[(j - 1) % 5], cycle[j])))
        else:
            label = (cycle[i // 2],)
        facets.append({"coefficients": (a, b, c), "chords": label,
                       "incident_vertices": (i, (i + 1) % 10)})

    # Five singleton facets and five complete dissections (triangulations).
    expected = {(d,) for d in chords()}
    expected.update(
        tuple(sorted((a, b)))
        for i, a in enumerate(chords())
        for b in chords()[i + 1:] if not crosses(a, b)
    )
    assert len(expected) == 10
    assert {facet["chords"] for facet in facets} == expected
    assert all(any(a * x + b * y + c < 0 for f in facets
                   for a, b, c in [f["coefficients"]]) for x, y in pentagon)
    assert codimension_vector(5) == (1, 10, 10)
    signed_twice_area = sum(
        x * vertices[(i + 1) % 10][1]
        - vertices[(i + 1) % 10][0] * y
        for i, (x, y) in enumerate(vertices)
    )
    assert signed_twice_area > 0

    return {
        "n": 5, "dimension": 2, "vertices": tuple(vertices),
        "facets": tuple(facets), "rational_area": signed_twice_area / 2,
        "source": "https://doi.org/10.1007/JHEP11(2025)029",
        "scope": "one exact rational coordinate realization of the combinatorial type",
    }


def canonical_rational_function(polytope: dict | None = None) -> sp.Expr:
    """Canonical 2-form coefficient, Omega = F(X,Y) dX wedge dY.

    The vertex sum uses normal determinants and consecutive facet forms.
    It is independent of positive rescalings of each facet inequality.
    """
    polytope = polytope or rational_realization()
    x, y = sp.symbols("X Y")
    facets = polytope["facets"]
    result = sp.S.Zero
    for i, facet in enumerate(facets):
        before = facets[(i - 1) % len(facets)]["coefficients"]
        current = facet["coefficients"]
        a0, b0, c0 = before
        a1, b1, c1 = current
        det = a0 * b1 - a1 * b0
        assert det > 0
        result += det / ((a0*x + b0*y + c0) * (a1*x + b1*y + c1))
    return sp.cancel(result)


def verify_canonical_form(polytope: dict | None = None) -> bool:
    """Algebraically check each of the ten facet logarithmic residues."""
    polytope = polytope or rational_realization()
    x, y = sp.symbols("X Y")
    f = canonical_rational_function(polytope)
    facets = polytope["facets"]
    center = (
        sum(p[0] for p in polytope["vertices"]) / 10,
        sum(p[1] for p in polytope["vertices"]) / 10,
    )
    assert f.subs({x: center[0], y: center[1]}) > 0
    for facet in facets:
        a, b, c = facet["coefficients"]
        va, vb = (polytope["vertices"][i] for i in facet["incident_vertices"])
        middle = ((va[0] + vb[0]) / 2, (va[1] + vb[1]) / 2)
        # Multiplying by the boundary equation removes its simple pole;
        # all other facet equations stay nonzero at the relative interior.
        finite_residue = sp.cancel(f * (a*x + b*y + c)).subs({
            x: middle[0], y: middle[1]
        })
        assert finite_residue.is_finite and finite_residue > 0
    return True


def export_json(output: Path) -> Path:
    geometry = rational_realization()
    verify_canonical_form(geometry)
    payload = {
        "schema": "gentaron.math-physics.polytope/1",
        "object": "5-point cosmohedron combinatorial type",
        "scope": geometry["scope"],
        "not_claimed": "physical canonical embedding or cosmological amplitude",
        "source": geometry["source"],
        "dimension": geometry["dimension"],
        "vertices": [[str(v) for v in p] for p in geometry["vertices"]],
        "rational_area": str(geometry["rational_area"]),
        "facets": [{
            "inequality": [str(v) for v in facet["coefficients"]],
            "chords": [list(chord) for chord in facet["chords"]],
            "incident_vertices": list(facet["incident_vertices"]),
        } for facet in geometry["facets"]],
        "canonical_2_form_coefficient": str(canonical_rational_function(geometry)),
        "verified": {
            "all_facet_halfspaces": True,
            "all_facet_labels_match_polygon_dissections": True,
            "all_ten_facet_logarithmic_residues_nonzero": True,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    print(export_json(Path("research/results/cosmohedron-5-coordinates.json")))
