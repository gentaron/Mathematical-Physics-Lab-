"""Route computationally bounded candidates; never certify mathematical truth."""

from .hypothesis import validate_candidate


def decide(candidate: object) -> dict:
    normalized = validate_candidate(candidate)
    return {"candidate_id": normalized["id"], "route": "exact_counterexample_search",
            "reason": "Bounded rational polynomial, supported count target, disjoint held-out sizes",
            "correctness_judgement": "deferred_to_exact_evaluator"}
