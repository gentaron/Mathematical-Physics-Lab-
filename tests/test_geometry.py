from math import comb

import pytest
import sympy as sp


@pytest.mark.parametrize("size", range(3, 8))
def test_triangulations_are_catalan(size):
    from research.positive_geometry.associahedron import triangulations
    ts = triangulations(tuple(range(1, size + 1)))
    assert len(ts) == comb(2 * (size - 2), size - 2) // (size - 1)
    assert all(len(t) == size - 3 for t in ts)


@pytest.mark.parametrize("size,expected", [
    (3, (1,)), (4, (1, 2)), (5, (1, 10, 10)),
    (6, (1, 44, 114, 72)), (7, (1, 196, 952, 1400, 644)),
])
def test_cosmohedron_matches_paper_table_one(size, expected):
    from research.positive_geometry.cosmohedron import codimension_vector, recurrence_vector
    assert codimension_vector(size) == expected
    assert recurrence_vector(size) == expected


def test_five_point_expression_and_all_factorizations():
    from research.positive_geometry.associahedron import amplitude, channel_symbol, verify_residues
    polygon = (1, 2, 3, 4, 5)
    a, b, c, d, e = [channel_symbol(ch) for ch in ((1, 3), (1, 4), (2, 4), (2, 5), (3, 5))]
    expected = 1/(a*b) + 1/(a*e) + 1/(b*c) + 1/(c*d) + 1/(d*e)
    assert sp.cancel(amplitude(polygon) - expected) == 0
    for size in range(4, 8):
        checks = verify_residues(tuple(range(1, size + 1)))
        assert checks and all(check["passed"] for check in checks)


def test_crossing_double_residue_is_zero():
    from research.positive_geometry.associahedron import amplitude, channel_symbol
    expr = amplitude((1, 2, 3, 4, 5, 6))
    a, b = channel_symbol((1, 3)), channel_symbol((2, 4))
    assert sp.residue(sp.residue(expr, a, 0), b, 0) == 0


def test_face_lattice_has_empty_face_and_reverse_inclusion():
    from research.positive_geometry.cosmohedron import face_lattice
    lattice = face_lattice(6)
    nodes = {node["id"]: node for node in lattice["faces"]}
    assert sum(n["dimension"] == 0 for n in nodes.values()) == 72
    assert sum(n["dimension"] == 1 for n in nodes.values()) == 114
    assert sum(n["dimension"] == 2 for n in nodes.values()) == 44
    assert sum(n["dimension"] == 3 for n in nodes.values()) == 1
    assert sum(n["dimension"] == -1 for n in nodes.values()) == 1
    for lower, upper in lattice["covers"]:
        assert nodes[upper]["dimension"] == nodes[lower]["dimension"] + 1
        if lower != "empty":
            lower_polygons = {tuple(p) for p in nodes[lower]["polygons"]}
            upper_polygons = {tuple(p) for p in nodes[upper]["polygons"]}
            assert upper_polygons < lower_polygons
    # Euler relation for the nonempty boundary of a convex 3-polytope.
    assert 72 - 114 + 44 == 2


@pytest.mark.parametrize("size", [2, 8, -1, True, 4.5])
def test_oversized_or_invalid_enumerations_rejected(size):
    from research.positive_geometry.cosmohedron import matryoshkas
    with pytest.raises(ValueError):
        matryoshkas(size)


def test_invalid_chords_and_polygon_labels_rejected():
    from research.positive_geometry.associahedron import subdivision_cells, triangulations
    with pytest.raises(ValueError):
        triangulations((1, 1, 2))
    with pytest.raises(ValueError):
        subdivision_cells((1, 2, 3, 4, 5), ((1, 3), (2, 4)))
    with pytest.raises(ValueError):
        subdivision_cells((1, 2, 3, 4), ((1, 2),))


@pytest.mark.parametrize("size", [10**100, 4.5])
def test_count_vector_validates_before_allocating(size):
    from research.positive_geometry.cosmohedron import codimension_vector
    with pytest.raises(ValueError):
        codimension_vector(size)
