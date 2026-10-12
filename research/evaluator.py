"""Exact finite counterexample search, with explicit proof boundaries."""

from .director import count_target
from .hypothesis import predict, validate_candidate


def evaluate(value: object) -> dict:
    candidate = validate_candidate(value)
    checks = []
    first_counterexample = None
    for phase, sizes in (("fit", candidate["fit_vertices"]), ("held_out", candidate["test_vertices"])):
        for n in sizes:
            predicted = predict(candidate, n)
            actual = count_target(candidate["target"], n)
            checks.append({"polygon_vertices": n, "phase": phase,
                           "predicted": str(predicted), "actual": str(actual),
                           "passed": predicted == actual})
            if predicted != actual and first_counterexample is None:
                first_counterexample = {"polygon_vertices": n, "predicted": str(predicted),
                                        "actual": str(actual), "phase": phase}
    return {"status": "counterexample" if first_counterexample else "conjecture",
            "experiment": "polynomial_count_candidate", "candidate": candidate,
            "checks": checks, "counterexample": first_counterexample,
            "tested_vertices": list(candidate["test_vertices"]),
            "proof_scope": "finite_cases_only", "novelty": "not_assessed",
            "oracle": "independent subdivision recurrence (arXiv:2603.03425v3 Eq.11)"}
