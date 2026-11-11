"""Cosmohedron face counts beyond the paper's table: dimension 5 to 9.

The paper's Table 1 stops at the heptagon (dimension 4), and building every
Matryoshka stops being cheap after that. Here the counts are taken two ways
that share no code, and a count is only reported when they agree:

* ``walk``: visit every dissection of a labelled n-gon and multiply the counts
  of its cells (the recurrence of Eq. 11, with its own dissection enumerator,
  so it is not bound by the 7-vertex limit of the symbolic amplitude code);
* ``transfer``: never builds a dissection. Root the polygon at one side; the
  cell on that side has m vertices, and each of its other m-1 sides is either
  a side of the polygon or a diagonal cutting off a smaller polygon. That turns
  the count into a sum over compositions of the n-1 remaining sides.

Both are checked against the paper for n <= 7, and every vector must satisfy
the Euler-Poincare relation sum_k (-1)^k f_k = 1 (f_k = faces of dimension k,
the polytope itself included), which holds for any convex polytope.

Counts are plain integers; nothing here is floating point or AI output.
"""

from functools import lru_cache

from .cosmohedron import REFERENCE_VECTORS

MAX_VERTICES = 12  # dimension 9; ``walk`` visits 518,859 dissections at n = 12
Poly = tuple[int, ...]  # coefficients in t, index = codimension


def validate_higher(vertices: int, maximum: int = MAX_VERTICES) -> None:
    if type(vertices) is not int or not 3 <= vertices <= maximum:
        raise ValueError(f"Polygon vertex count must be an integer in 3..{maximum}")


def _add(a: Poly, b: Poly) -> Poly:
    out = [0] * max(len(a), len(b))
    for i, x in enumerate(a):
        out[i] += x
    for i, x in enumerate(b):
        out[i] += x
    return tuple(out)


def _mul(a: Poly, b: Poly) -> Poly:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return tuple(out)


def _shift(a: Poly) -> Poly:
    """Multiply by t: every face of a proper dissection sits one codimension deeper."""
    return (0,) + a


# --- method 1: walk every dissection -------------------------------------

def _cells_of_dissections(n: int):
    """Yield the multiset of cell sizes of every non-empty dissection of an n-gon.

    Vertices are 0..n-1 on a circle. A dissection is grown chord by chord in a
    fixed order, so each non-crossing chord set is produced exactly once.
    """
    chords = [(a, b) for a in range(n) for b in range(a + 2, n) if not (a == 0 and b == n - 1)]

    def crosses(p, q):
        (a, b), (c, d) = p, q
        return a < c < b < d or c < a < d < b

    def cell_sizes(selected):
        cells = [list(range(n))]
        for a, b in selected:
            for k, cell in enumerate(cells):
                if a in cell and b in cell:
                    i, j = cell.index(a), cell.index(b)
                    cells[k:k + 1] = [cell[i:j + 1], cell[:i + 1] + cell[j:]]
                    break
        return [len(c) for c in cells]

    def extend(selected, start):
        if selected:
            yield cell_sizes(selected)
        for i in range(start, len(chords)):
            if all(not crosses(chords[i], s) for s in selected):
                yield from extend(selected + [chords[i]], i + 1)

    yield from extend([], 0)


@lru_cache(maxsize=None)
def walk_vector(vertices: int) -> Poly:
    validate_higher(vertices)
    total: Poly = (1,)
    for sizes in _cells_of_dissections(vertices):
        term: Poly = (1,)
        for size in sizes:
            term = _mul(term, walk_vector(size))
        total = _add(total, _shift(term))
    return total


# --- method 2: transfer over the boundary ---------------------------------

@lru_cache(maxsize=None)
def _all_dissections(vertices: int) -> Poly:
    """A_n: sum over every dissection (empty one included) of the product of cell counts."""
    return _add(transfer_vector(vertices), _proper(vertices))


@lru_cache(maxsize=None)
def _segment(sides: int) -> Poly:
    """One side of the root cell: a polygon side, or a diagonal cutting off sides+1 vertices."""
    return (1,) if sides == 1 else _all_dissections(sides + 1)


@lru_cache(maxsize=None)
def _compositions(length: int, parts: int) -> Poly:
    """Sum over compositions of `length` into `parts` positive pieces of prod _segment(piece)."""
    if parts == 0:
        return (1,) if length == 0 else (0,)
    out: Poly = (0,)
    for first in range(1, length - parts + 2):
        out = _add(out, _mul(_segment(first), _compositions(length - first, parts - 1)))
    return out


@lru_cache(maxsize=None)
def _proper(vertices: int) -> Poly:
    """Sum over non-empty dissections: the root cell is smaller than the polygon."""
    out: Poly = (0,)
    for m in range(3, vertices):
        out = _add(out, _mul(transfer_vector(m), _compositions(vertices - 1, m - 1)))
    return out


@lru_cache(maxsize=None)
def transfer_vector(vertices: int) -> Poly:
    validate_higher(vertices)
    return _add((1,), _shift(_proper(vertices)))


# --- checks and report ----------------------------------------------------

def _trim(v: Poly, vertices: int) -> tuple[int, ...]:
    out = list(v) + [0] * (vertices - 2)
    if any(out[vertices - 2:]):
        raise RuntimeError("count has a face below the vertices")
    return tuple(out[:vertices - 2])


def euler_characteristic(codimension_counts: tuple[int, ...]) -> int:
    """sum_k (-1)^k f_k over faces of dimension k = d - codimension, polytope included."""
    d = len(codimension_counts) - 1
    return sum((-1) ** (d - c) * f for c, f in enumerate(codimension_counts))


def higher_dimensions(max_vertices: int = 10) -> list[dict]:
    validate_higher(max_vertices)
    rows = []
    for n in range(3, max_vertices + 1):
        walk = _trim(walk_vector(n), n)
        transfer = _trim(transfer_vector(n), n)
        reference = REFERENCE_VECTORS.get(n)
        chi = euler_characteristic(transfer)
        rows.append({
            "polygon_vertices": n,
            "polytope_dimension": n - 3,
            "codimension_vector": list(transfer),
            "f_vector": list(reversed(transfer)),
            "vertices_of_polytope": transfer[-1],
            "methods_agree": walk == transfer,
            "euler_characteristic": chi,
            "euler_ok": chi == 1,
            "reference_matches": None if reference is None else tuple(reference) == transfer,
            "beyond_reference": reference is None,
        })
    return rows


def all_passed(rows: list[dict]) -> bool:
    return all(r["methods_agree"] and r["euler_ok"] and r["reference_matches"] is not False for r in rows)
