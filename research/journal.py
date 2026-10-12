"""Markdown export suitable for a Genesis Vault research journal input."""


def render_journal(report: dict) -> str:
    lines = ["# Mathematical Physics Lab — research journal", "",
             "Reproduction and exact finite experiments; no claim of new mathematics.", "",
             f"Run: `{report['run_id']}`", f"Implementation SHA-256: `{report['code_sha256']}`", "",
             "## Cosmohedron reproduction", "",
             "| Polygon vertices | Polytope dimension | Faces by codimension (whole → vertices) | Reference match |",
             "| --- | --- | --- | --- |"]
    for row in report["geometry"]:
        lines.append(f"| {row['polygon_vertices']} | {row['polytope_dimension']} | "
                     f"{row['codimension_vector']} | {row['reference_matches']} |")
    lines += ["", "[Reference: arXiv:2603.03425v3, Table 1](https://arxiv.org/html/2603.03425v3#S5)",
              "", "Counts exclude the empty face. Exported face lattices include it explicitly.",
              "The outer polygon is a bookkeeping root. Inclusion of polygon sets reverses face containment.",
              "", "## Exact scalar amplitude checks", ""]
    for row in report["amplitudes"]:
        lines.append(f"- {row['polygon_vertices']}-point: {row['triangulations']} triangulations; "
                     f"all {len(row['residue_checks'])} channel factorizations passed: {row['passed']}")
    lines += ["", "These rational scalar amplitudes are not amplituhedron canonical forms.", "",
              "## Hypotheses and counterexamples", "",
              "Fitting inputs and held-out inputs are disjoint. Polynomial fits are a deliberate",
              "baseline to expose invalid extrapolation. Passing finitely many cases is a conjecture.", ""]
    for result in report["hypotheses"]:
        lines.append(f"- `{result['candidate']['id']}`: **{result['status']}**")
        counterexample = result["counterexample"]
        if counterexample:
            lines.append(f"  N={counterexample['polygon_vertices']}: predicted {counterexample['predicted']}, "
                         f"actual {counterexample['actual']} ({counterexample['phase']}).")
    if report["ai_error"]:
        lines.append("- Local AI proposal step was inconclusive; see ai_error in run.json. No paid fallback.")
    lines += ["", "## Bootstrap seed", "",
              "Two-site reconstruction is unique within the supplied denominator and linear-numerator ansatz.",
              "Scaling, exchange symmetry and the normalized total-energy pole are checked exactly.",
              "The 2–4-site expressions are flat-space scalar tree wavefunction coefficients.",
              "They are not inflationary correlators and are not a Kinematic-Flow reproduction.", "",
              "## Evidence and proof boundary", "",
              "- `run.json`: machine-readable results and provenance.",
              "- `faces-N.json`: full Hasse diagram through six polygon vertices.",
              "- `ledger/*.json`: individual records with payload and implementation hashes.",
              "- Lean kernel proofs were not checked by this Python experiment.",
              "- No novelty assessment or automated publication to Genesis Vault was performed.", ""]
    return "\n".join(lines)
