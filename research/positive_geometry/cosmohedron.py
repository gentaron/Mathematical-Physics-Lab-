"""Cosmohedral face combinatorics from nested polygon partitions.

Reference: arXiv:2603.03425v3, Sections 2.1 and 5.2.
The outer polygon is ALWAYS present in our representation as a bookkeeping
root. A singleton root denotes the full face (codimension zero). Counts exclude
the empty face, which is added explicitly to the exported Hasse diagram.
"""

from functools import lru_cache
from itertools import product

from .associahedron import Polygon, dissections, subdivision_cells

Matryoshka = frozenset[Polygon]
REFERENCE_VECTORS = {
    3: (1,), 4: (1, 2), 5: (1, 10, 10),
    6: (1, 44, 114, 72), 7: (1, 196, 952, 1400, 644),
}
SOURCE = "https://arxiv.org/html/2603.03425v3#S5"


def validate_size(vertices: int, maximum: int = 7) -> None:
    if type(vertices) is not int or not 3 <= vertices <= maximum:
        raise ValueError(f"Polygon vertex count must be an integer in 3..{maximum}")


@lru_cache(maxsize=256)
def _nested(polygon: Polygon) -> tuple[Matryoshka, ...]:
    root = frozenset((polygon,))
    families = {root}
    for chords in dissections(polygon):
        if not chords:
            continue
        cells = subdivision_cells(polygon, chords)
        for refinements in product(*(_nested(cell) for cell in cells)):
            families.add(root.union(*refinements))
    return tuple(sorted(families, key=lambda m: (len(m), tuple(sorted(m)))))


def matryoshkas(vertices: int) -> tuple[Matryoshka, ...]:
    validate_size(vertices)
    return _nested(tuple(range(1, vertices + 1)))


def codimension(family: Matryoshka) -> int:
    """Rank in the rooted representation: number of internally subdivided polygons."""
    sets = [frozenset(p) for p in family]
    return sum(any(other < polygon for other in sets) for polygon in sets)


def codimension_vector(vertices: int) -> tuple[int, ...]:
    validate_size(vertices)
    counts = [0] * (vertices - 2)
    for family in matryoshkas(vertices):
        counts[codimension(family)] += 1
    return tuple(counts)


def _multiply(left: list[int], right: tuple[int, ...]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


@lru_cache(maxsize=5)
def recurrence_vector(vertices: int) -> tuple[int, ...]:
    """Independent count via the subdivision/product recurrence, no families built."""
    validate_size(vertices)
    counts = [1] + [0] * (vertices - 3)
    polygon = tuple(range(1, vertices + 1))
    for chords in dissections(polygon):
        if not chords:
            continue
        contribution = [1]
        for cell in subdivision_cells(polygon, chords):
            contribution = _multiply(contribution, recurrence_vector(len(cell)))
        for index, count in enumerate(contribution):
            counts[index + 1] += count
    return tuple(counts)


def face_lattice(vertices: int) -> dict:
    """Hasse edges [lower face, upper face]; dimensions include whole and empty faces."""
    validate_size(vertices, maximum=6)
    families = matryoshkas(vertices)
    ranks = [codimension(family) for family in families]
    faces = [{"id": str(index), "dimension": vertices - 3 - ranks[index],
              "codimension": ranks[index], "polygons": [list(p) for p in sorted(family)]}
             for index, family in enumerate(families)]
    faces.append({"id": "empty", "dimension": -1, "codimension": vertices - 2,
                  "polygons": []})
    covers = []
    for lower_index, lower in enumerate(families):
        if ranks[lower_index] == vertices - 3:
            covers.append(["empty", str(lower_index)])
        for upper_index, upper in enumerate(families):
            if ranks[lower_index] == ranks[upper_index] + 1 and upper < lower:
                covers.append([str(lower_index), str(upper_index)])
    return {"polygon_vertices": vertices, "polytope_dimension": vertices - 3,
            "root_convention": "outer polygon included; singleton root is the full face",
            "covers_direction": "lower face -> upper face",
            "faces": faces, "covers": covers}
