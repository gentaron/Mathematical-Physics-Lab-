from math import comb

from hypothesis import given, settings, strategies as st

from research.positive_geometry.associahedron import (
    crosses,
    diagonals,
    dissections,
    subdivision_cells,
    triangulations,
)

# Small enough for free CPU GitHub Actions, but adversarially generated rather
# than hard-coded examples. A failing case is minimized by Hypothesis.
POLYGONS = st.lists(
    st.integers(min_value=1, max_value=1000),
    min_size=3,
    max_size=7,
    unique=True,
).map(lambda labels: tuple(sorted(labels)))


@settings(max_examples=60, deadline=None, derandomize=True)
@given(POLYGONS)
def test_relabeling_preserves_triangulations_and_catalan_count(polygon):
    size = len(polygon)
    standard = tuple(range(1, size + 1))
    remap = dict(zip(standard, polygon, strict=True))
    transformed = {
        tuple((remap[a], remap[b]) for a, b in triangulation)
        for triangulation in triangulations(standard)
    }
    observed = set(triangulations(polygon))
    expected = comb(2 * (size - 2), size - 2) // (size - 1)
    assert len(observed) == expected
    assert observed == transformed
    assert all(
        not crosses(a, b)
        for triangulation in observed
        for i, a in enumerate(triangulation)
        for b in triangulation[i + 1 :]
    )


@settings(max_examples=50, deadline=None, derandomize=True)
@given(POLYGONS, st.data())
def test_every_noncrossing_dissection_satisfies_euler_cell_identity(polygon, data):
    choices = dissections(polygon)
    selected = data.draw(st.sampled_from(choices))
    cells = subdivision_cells(polygon, selected)
    assert len(cells) == len(selected) + 1
    assert sum(len(cell) - 2 for cell in cells) == len(polygon) - 2
    assert all(len(cell) >= 3 for cell in cells)
    assert all(all(vertex in polygon for vertex in cell) for cell in cells)
    assert len(set(vertex for cell in cells for vertex in cell)) == len(polygon)


@settings(max_examples=60, deadline=None, derandomize=True)
@given(POLYGONS)
def test_all_diagonals_exclude_polygon_edges(polygon):
    n = len(polygon)
    ds = diagonals(polygon)
    boundary = {tuple(sorted((polygon[i], polygon[(i + 1) % n]))) for i in range(n)}
    assert len(ds) == n * (n - 3) // 2
    assert not any(d in boundary for d in ds)
    assert len(set(ds)) == len(ds)
