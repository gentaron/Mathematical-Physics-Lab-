"""Flat-space scalar tree wavefunction coefficient from an edge-cut recursion.

Independent x_i are external energy sums; y_e are internal edge energies.
This rational toy seed is NOT a primordial correlator or Kinematic-Flow port.
It uses the energy recursion described in arXiv:2603.03425v3 Section 1.5.
"""

from functools import lru_cache

import sympy as sp


def wavefunction(energies: tuple[sp.Expr, ...], edges: tuple[tuple[int, int, sp.Expr], ...]) -> sp.Expr:
    """Return the rational coefficient for a connected tree with 1–4 sites."""
    if not 1 <= len(energies) <= 4 or len(edges) != len(energies) - 1:
        raise ValueError("Need 1–4 sites and exactly sites-1 edges")
    normalized = []
    seen = set()
    for left, right, energy in edges:
        if (type(left) is not int or type(right) is not int or left == right
                or not 0 <= left < len(energies) or not 0 <= right < len(energies)):
            raise ValueError("Invalid tree endpoints")
        key = tuple(sorted((left, right)))
        if key in seen:
            raise ValueError("Duplicate tree edge")
        seen.add(key)
        normalized.append((key[0], key[1], sp.sympify(energy)))
    adjacency = {i: set() for i in range(len(energies))}
    for a, b, _ in normalized:
        adjacency[a].add(b)
        adjacency[b].add(a)
    connected = {0}
    stack = [0]
    while stack:
        for neighbor in adjacency[stack.pop()] - connected:
            connected.add(neighbor)
            stack.append(neighbor)
    if len(connected) != len(energies):
        raise ValueError("Graph must be a connected tree")

    @lru_cache(maxsize=256)
    def cut(xs: tuple[sp.Expr, ...], es: tuple[tuple[int, int, sp.Expr], ...]) -> sp.Expr:
        if not es:
            return 1 / xs[0]
        terms = []
        for index, (a, b, y) in enumerate(es):
            remaining = es[:index] + es[index + 1:]
            component = {a}
            pending = [a]
            while pending:
                vertex = pending.pop()
                for left, right, _ in remaining:
                    neighbor = right if left == vertex else left if right == vertex else None
                    if neighbor is not None and neighbor not in component:
                        component.add(neighbor)
                        pending.append(neighbor)
            shifted = list(xs)
            shifted[a] += y
            shifted[b] += y
            factors = []
            for vertices in (sorted(component), sorted(set(range(len(xs))) - component)):
                mapping = {v: i for i, v in enumerate(vertices)}
                sub_edges = tuple((mapping[l], mapping[r], e) for l, r, e in remaining
                                  if l in mapping and r in mapping)
                factors.append(cut(tuple(shifted[v] for v in vertices), sub_edges))
            terms.append(factors[0] * factors[1])
        return sp.Add(*terms) / sp.Add(*xs)

    return sp.cancel(cut(tuple(sp.sympify(x) for x in energies), tuple(sorted(normalized))))


def verify_two_site() -> list[dict]:
    x1, x2, y, scale = sp.symbols("x1 x2 y scale")
    expr = wavefunction((x1, x2), ((0, 1, y),))
    expected = 1 / ((x1 + x2) * (x1 + y) * (x2 + y))
    pole_coefficient = sp.cancel((x1 + x2) * expr).subs(x2, -x1)
    identities = {
        "known_two_site_formula": expr - expected,
        "exchange_symmetry": expr - expr.xreplace({x1: x2, x2: x1}),
        "homogeneity_degree_minus_three": expr.xreplace(
            {x1: scale*x1, x2: scale*x2, y: scale*y}) - expr / scale**3,
        "total_energy_pole_coefficient": pole_coefficient - 1/((x1+y)*(y-x1)),
    }
    return [{"constraint": key, "passed": sp.cancel(value) == 0} for key, value in identities.items()]


def reconstruct_two_site() -> dict:
    """Solve a bounded ansatz from scaling and a normalized total-energy pole.

    The allowed denominator is supplied as physical input. Uniqueness holds
    ONLY within a linear-numerator ansatz, not all cosmological correlators.
    """
    x1, x2, y = sp.symbols("x1 x2 y")
    coefficients = sp.symbols("c0:4")
    c0, c1, c2, c3 = coefficients
    numerator = c0 + c1*x1 + c2*x2 + c3*y
    denominator = (x1+x2)*(x1+y)*(x2+y)
    ansatz = numerator / denominator
    scaling = sum(v*sp.diff(ansatz, v) for v in (x1, x2, y)) + 3*ansatz
    scaling_numerator = sp.together(scaling).as_numer_denom()[0]
    symmetry_numerator = sp.together(ansatz - ansatz.xreplace({x1: x2, x2: x1})).as_numer_denom()[0]
    residue_normalization = numerator.subs(x2, -x1) - 1
    equations = []
    for expression in (scaling_numerator, symmetry_numerator, residue_normalization):
        equations.extend(sp.Poly(expression, x1, x2, y).coeffs())
    solutions = sp.solve(equations, coefficients, dict=True)
    if len(solutions) != 1 or set(solutions[0]) != set(coefficients):
        raise RuntimeError("Constraints did not uniquely determine this ansatz")
    solution = solutions[0]
    return {"status": "symbolic_verified", "unique_within_ansatz": True,
            "coefficients": {str(c): str(solution[c]) for c in coefficients},
            "expression": str(sp.factor(ansatz.subs(solution))),
            "scope": "linear_numerator_fixed_denominator_flat_space_scalar_tree",
            "constraints": ["degree -3", "site exchange symmetry", "normalized total-energy pole"],
            "assumptions": "generic independent energies, tree level, supplied denominator, flat space"}
