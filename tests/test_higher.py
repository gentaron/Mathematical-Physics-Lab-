import pytest

from research.positive_geometry.cosmohedron import REFERENCE_VECTORS, codimension_vector
from research.positive_geometry.higher import (
    all_passed, euler_characteristic, higher_dimensions, transfer_vector, validate_higher, walk_vector,
)


def test_both_methods_reproduce_the_paper_table():
    for n, ref in REFERENCE_VECTORS.items():
        assert tuple(walk_vector(n)[: n - 2]) == ref
        assert tuple(transfer_vector(n)[: n - 2]) == ref


def test_transfer_agrees_with_full_enumeration_where_enumeration_is_cheap():
    for n in range(3, 8):
        assert tuple(transfer_vector(n)[: n - 2]) == codimension_vector(n)


def test_beyond_the_table_two_methods_agree_and_euler_holds():
    rows = higher_dimensions(10)
    assert all_passed(rows)
    beyond = [r for r in rows if r["beyond_reference"]]
    assert [r["polytope_dimension"] for r in beyond] == [5, 6, 7]
    # facets of the n-gon cosmohedron = non-empty dissections = little Schroeder number - 1
    assert [r["codimension_vector"][1] for r in beyond] == [902, 4278, 20792]


def test_euler_check_rejects_a_wrong_vector():
    assert euler_characteristic((1, 44, 114, 72)) == 1
    assert euler_characteristic((1, 44, 114, 71)) != 1


def test_size_is_bounded():
    with pytest.raises(ValueError):
        validate_higher(13)
    with pytest.raises(ValueError):
        validate_higher(2)
