"""Planar polygon dissections; channels are independent formal variables.

This constructs rational scalar amplitudes, not canonical differential forms.
No particular ABHY kinematic-space embedding is imposed here.
"""

from functools import lru_cache
from itertools import combinations
from math import prod

import sympy as sp

Polygon = tuple[int, ...]
Chord = tuple[int, int]


def validate_polygon(polygon: Polygon) -> None:
    if (not 3 <= len(polygon) <= 7
            or any(type(v) is not int or v < 1 for v in polygon)
            or tuple(sorted(set(polygon))) != polygon):
        raise ValueError("Polygon must have 3–7 distinct increasing positive integer labels")


def diagonals(polygon: Polygon) -> tuple[Chord, ...]:
    validate_polygon(polygon)
    return tuple((a, b) for i, a in enumerate(polygon) for j, b in enumerate(polygon)
                 if j > i + 1 and (i, j) != (0, len(polygon) - 1))


def crosses(left: Chord, right: Chord) -> bool:
    a, b = sorted(left)
    c, d = sorted(right)
    return a < c < b < d or c < a < d < b


def subdivision_cells(polygon: Polygon, chords: tuple[Chord, ...]) -> tuple[Polygon, ...]:
    """Split an ordered convex polygon along a validated non-crossing chord set."""
    allowed = set(diagonals(polygon))
    if (len(set(chords)) != len(chords) or any(ch not in allowed for ch in chords)
            or any(crosses(a, b) for a, b in combinations(chords, 2))):
        raise ValueError("Subdivision needs distinct non-crossing internal diagonals")
    cells = [polygon]
    for a, b in sorted(chords):
        for index, cell in enumerate(cells):
            if a in cell and b in cell:
                i, j = cell.index(a), cell.index(b)
                first = cell[i:j + 1]
                second = cell[:i + 1] + cell[j:]
                if len(first) >= 3 and len(second) >= 3:
                    cells[index:index + 1] = [first, second]
                    break
        else:
            raise ValueError("Could not split polygon along diagonal")
    return tuple(sorted(cells))


@lru_cache(maxsize=256)
def dissections(polygon: Polygon) -> tuple[tuple[Chord, ...], ...]:
    """All non-crossing subsets of diagonals, including the empty subset."""
    choices = diagonals(polygon)
    result = []

    def extend(selected: tuple[Chord, ...], start: int) -> None:
        result.append(selected)
        for i in range(start, len(choices)):
            if all(not crosses(choices[i], chord) for chord in selected):
                extend(selected + (choices[i],), i + 1)

    extend((), 0)
    return tuple(result)


def triangulations(polygon: Polygon) -> tuple[tuple[Chord, ...], ...]:
    return tuple(chords for chords in dissections(polygon) if len(chords) == len(polygon) - 3)


def channel_symbol(chord: Chord) -> sp.Symbol:
    a, b = sorted(chord)
    return sp.Symbol(f"X{a}_{b}")


def amplitude(polygon: Polygon) -> sp.Expr:
    return sp.Add(*(sp.Integer(1) / prod(channel_symbol(ch) for ch in triangulation)
                    for triangulation in triangulations(polygon)))


def verify_residues(polygon: Polygon) -> list[dict]:
    """Every channel residue must equal the product of the two smaller amplitudes."""
    expr = amplitude(polygon)
    checks = []
    for chord in diagonals(polygon):
        symbol = channel_symbol(chord)
        # Clearing this single simple pole avoids an expensive generic series.
        residue = sp.cancel(symbol * expr).subs(symbol, 0)
        cells = subdivision_cells(polygon, (chord,))
        expected = prod(amplitude(cell) for cell in cells)
        checks.append({"channel": list(chord), "residue": str(residue),
                       "expected": str(expected),
                       "passed": sp.cancel(residue - expected) == 0})
    return checks
