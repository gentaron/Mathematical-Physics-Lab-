"""One reproducible command path for laptops and GitHub Actions."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import uuid

import sympy as sp

from .cosmological_bootstrap.correlators import reconstruct_two_site, verify_two_site, wavefunction
from .decision import decide
from .director import propose
from .evaluator import evaluate
from .journal import render_journal
from .ledger import Ledger, code_fingerprint
from .ollama import propose_with_ollama
from .positive_geometry.associahedron import amplitude, triangulations, verify_residues
from .positive_geometry.cosmohedron import (
    REFERENCE_VECTORS, codimension_vector, face_lattice, recurrence_vector,
)


def _write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def _read_candidate(path: Path) -> object:
    """Bound actual bytes read, including when the file changes after opening.

    Nonblocking open prevents waiting for a FIFO writer; descriptor inspection
    binds the regular-file check to the object actually being read.
    """
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descriptor, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("Candidate must be a regular file")
        data = handle.read(65537)
    if len(data) > 65536:
        raise ValueError("Candidate file exceeds 64 KiB")
    return json.loads(data.decode("utf-8"))


def run_experiments(max_vertices: int, output: Path, model: str | None = None) -> Path:
    if type(max_vertices) is not int or not 3 <= max_vertices <= 7:
        raise ValueError("max_vertices must be in 3..7")
    if model and max_vertices < 4:
        raise ValueError("Local AI requires at least four vertices for held-out evaluation")
    run_id = "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:12]
    directory = output / run_id
    directory.mkdir(parents=True, exist_ok=False)
    ledger = Ledger(directory / "ledger")
    geometry, amplitudes = [], []
    for n in range(3, max_vertices + 1):
        vector, recurrence = codimension_vector(n), recurrence_vector(n)
        matches = vector == recurrence == REFERENCE_VECTORS[n]
        if not matches:
            raise RuntimeError(f"Cosmohedron reference reproduction failed at {n} vertices")
        row = {"polygon_vertices": n, "polytope_dimension": n - 3,
               "codimension_vector": list(vector), "independent_recurrence": list(recurrence),
               "reference_matches": matches}
        geometry.append(row)
        ledger.append({"status": "reproduced", "experiment": "cosmohedral_face_counts",
                       "source": "https://arxiv.org/html/2603.03425v3#S5", "evidence": row})
        if n <= 6:
            _write_json(directory / f"faces-{n}.json", face_lattice(n))
        polygon = tuple(range(1, n + 1))
        residues = verify_residues(polygon)
        passed = all(check["passed"] for check in residues)
        if not passed:
            raise RuntimeError(f"Amplitude factorization failed at {n} points")
        algebra = {"polygon_vertices": n, "triangulations": len(triangulations(polygon)),
                   "expression": str(amplitude(polygon)), "residue_checks": residues, "passed": passed}
        amplitudes.append(algebra)
        ledger.append({"status": "symbolic_verified", "experiment": "planar_scalar_amplitude",
                       "scope": "formal independent channel variables, simple poles", "evidence": algebra})

    reconstruction = reconstruct_two_site()
    checks = verify_two_site()
    if not all(check["passed"] for check in checks):
        raise RuntimeError("Two-site bootstrap reproduction failed")
    wavefunctions = []
    for sites in range(2, 5):
        xs, ys = sp.symbols(f"x1:{sites+1}"), sp.symbols(f"y1:{sites}")
        edges = tuple((i, i+1, ys[i]) for i in range(sites - 1))
        wavefunctions.append({"sites": sites, "topology": "chain", "expression": str(wavefunction(xs, edges))})
    bootstrap = {"scope": "flat_space_scalar_tree_seed", "reconstruction": reconstruction,
                 "two_site_checks": checks, "wavefunctions": wavefunctions}
    ledger.append({"status": "symbolic_verified", "experiment": "bootstrap_seed", "evidence": bootstrap})

    hypotheses, decisions, ai_error = [], [], None
    if max_vertices >= 4:
        fit = list(range(3, min(5, max_vertices - 1) + 1))
        held_out = list(range(max(fit) + 1, max_vertices + 1))
        candidates = propose(fit, held_out)
        if model:
            try:
                candidates.extend(propose_with_ollama(model, fit, held_out))
            except (ValueError, RuntimeError, json.JSONDecodeError) as exc:
                ai_error = str(exc)
                ledger.append({"status": "inconclusive", "experiment": "local_ai_proposals", "error": ai_error})
        for candidate in candidates:
            decisions.append(decide(candidate))
            result = evaluate(candidate)
            hypotheses.append(result)
            ledger.append(result)

    report = {"schema_version": 1, "run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(),
              "code_sha256": code_fingerprint(), "max_vertices": max_vertices,
              "proposal_mode": "template+ollama" if model else "template",
              "geometry": geometry, "amplitudes": amplitudes, "bootstrap": bootstrap,
              "decisions": decisions, "hypotheses": hypotheses, "ai_error": ai_error,
              "all_reproductions_passed": True, "formal_proofs_checked": False,
              "novelty_assessed": False, "paid_services_used": False}
    _write_json(directory / "run.json", report)
    (directory / "journal.md").write_text(render_journal(report), encoding="utf-8")
    return directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Free exact mathematical-physics research experiments")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Reproduce geometry, residues, bootstrap seed and finite hypotheses")
    run.add_argument("--max-vertices", type=int, choices=range(3, 8), default=6)
    run.add_argument("--output", type=Path, default=Path("research/results"))
    run.add_argument("--ollama-model", help="Optional existing local model; never downloads or uses paid fallbacks")
    verify = commands.add_parser("verify", help="Evaluate a bounded polynomial candidate JSON file")
    verify.add_argument("--candidate", type=Path, required=True)
    verify.add_argument("--ledger", type=Path, help="Optional append-only record output directory")
    faces = commands.add_parser("faces", help="Print the cosmohedral Hasse diagram as JSON")
    faces.add_argument("--vertices", type=int, choices=range(3, 7), default=5)
    commands.add_parser("doctor", help="Read-only required/optional tool inventory")
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            directory = run_experiments(args.max_vertices, args.output, args.ollama_model)
            print(f"Research run: {directory}")
            print(f"Journal: {directory / 'journal.md'}")
            return 0
        if args.command == "verify":
            result = evaluate(_read_candidate(args.candidate))
            if args.ledger:
                Ledger(args.ledger).append(result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1 if result["status"] == "counterexample" else 0
        if args.command == "faces":
            print(json.dumps(face_lattice(args.vertices), indent=2))
            return 0
        if args.command == "doctor":
            print(json.dumps({"required": {"sympy": sp.__version__},
                              "optional": {name: shutil.which(name) for name in
                                           ("lean", "lake", "polymake", "sage", "ollama")},
                              "paid_services_required": False}, indent=2))
            return 0
    except (ValueError, RuntimeError, OSError, UnicodeError) as exc:
        print(f"math-lab: {exc}", file=sys.stderr)
        return 2
    return 2
