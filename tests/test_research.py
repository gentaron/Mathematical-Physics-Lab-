import json

import pytest
import sympy as sp


def candidate(**changes):
    value = {"schema_version": 1, "id": "trial", "target": "vertices",
             "coefficients": ["40", "-47/2", "7/2"],
             "fit_vertices": [3, 4], "test_vertices": [5],
             "source": "template", "description": "Quadratic extrapolation"}
    return value | changes


def test_exact_finite_agreement_stays_conjecture():
    from research.evaluator import evaluate
    result = evaluate(candidate())
    assert result["status"] == "conjecture"
    assert result["tested_vertices"] == [5]
    assert result["proof_scope"] == "finite_cases_only"


def test_counterexample_is_exact_and_reproducible():
    from research.evaluator import evaluate
    result = evaluate(candidate(test_vertices=[5, 6, 7]))
    assert result["status"] == "counterexample"
    assert result["counterexample"] == {
        "polygon_vertices": 6, "predicted": "25", "actual": "72", "phase": "held_out"}


@pytest.mark.parametrize("changes", [
    {"coefficients": ["__import__('os').system('echo bad')"]},
    {"coefficients": ["1/0"]}, {"coefficients": ["9" * 100]},
    {"coefficients": ["1"] * 7}, {"coefficients": []},
    {"test_vertices": [4]}, {"test_vertices": []},
    {"test_vertices": [8]}, {"fit_vertices": [True]},
    {"target": "arbitrary_expression"}, {"status": "formally_proved"},
    {"schema_version": True},
])
def test_untrusted_candidate_rejected(changes):
    from research.hypothesis import validate_candidate
    with pytest.raises(ValueError):
        validate_candidate(candidate(**changes))


def test_director_generates_and_decision_routes_bounded_proposals():
    from research.director import propose
    from research.decision import decide
    from research.evaluator import evaluate
    proposals = propose([3, 4, 5], [6, 7])
    assert {p["target"] for p in proposals} == {"vertices", "facets"}
    assert all(decide(p)["route"] == "exact_counterexample_search" for p in proposals)
    assert all(evaluate(p)["status"] == "counterexample" for p in proposals)


def test_two_site_wavefunction_and_total_energy_residue():
    from research.cosmological_bootstrap.correlators import wavefunction, verify_two_site
    x1, x2, y = sp.symbols("x1 x2 y")
    expr = wavefunction((x1, x2), ((0, 1, y),))
    expected = 1 / ((x1 + x2) * (x1 + y) * (x2 + y))
    assert sp.cancel(expr - expected) == 0
    assert all(check["passed"] for check in verify_two_site())


def test_three_site_recursion_matches_explicit_cut_sum():
    from research.cosmological_bootstrap.correlators import wavefunction
    a, b, c, u, v = sp.symbols("a b c u v")
    expr = wavefunction((a, b, c), ((0, 1, u), (1, 2, v)))
    left_cut = 1/(a+u) / ((b+u+c)*(b+u+v)*(c+v))
    right_cut = 1/(c+v) / ((a+b+v)*(a+u)*(b+v+u))
    assert sp.cancel(expr - (left_cut + right_cut)/(a+b+c)) == 0


def test_invalid_tree_rejected():
    from research.cosmological_bootstrap.correlators import wavefunction
    x = sp.symbols("x0:3")
    with pytest.raises(ValueError):
        wavefunction(x, ((0, 1, sp.Symbol("y")), (1, 0, sp.Symbol("z"))))


def test_ledger_preserves_identical_runs_and_hashes(tmp_path):
    from research.ledger import Ledger
    ledger = Ledger(tmp_path)
    payload = {"status": "reproduced", "experiment": "reference-counts", "evidence": [1, 10, 10]}
    a, b = ledger.append(payload), ledger.append(payload)
    assert a != b
    first = json.loads(a.read_text())
    assert first["payload_sha256"] == json.loads(b.read_text())["payload_sha256"]
    assert first["environment"]["sympy"] == "1.14.0"
    assert first["status"] == "reproduced"
    assert "code_sha256" in first and "created_at" in first


def test_ledger_cannot_promote_finite_checks_to_formal_proof(tmp_path):
    from research.ledger import Ledger
    with pytest.raises(ValueError):
        Ledger(tmp_path).append({"status": "formally_proved", "evidence": {"passed": True}})
