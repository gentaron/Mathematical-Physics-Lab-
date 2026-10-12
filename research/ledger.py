"""Append-only JSON records with input and implementation fingerprints.

Hashes aid reproducibility; they are not signatures or mathematical proof.
Formal proof is intentionally unavailable through this general append API.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import uuid

import sympy

from . import __version__

ALLOWED_STATUSES = {"reproduced", "counterexample", "conjecture", "symbolic_verified", "inconclusive"}


def code_fingerprint() -> str:
    root = Path(__file__).parent
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


class Ledger:
    def __init__(self, directory: Path):
        self.directory = Path(directory)

    def append(self, payload: dict) -> Path:
        if not isinstance(payload, dict) or payload.get("status") not in ALLOWED_STATUSES:
            raise ValueError("Unrecognized status; formally_proved requires separate Lean kernel evidence")
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False)
        record_id = uuid.uuid4().hex
        record = {"schema_version": 1, "record_id": record_id,
                  "created_at": datetime.now(timezone.utc).isoformat(),
                  "environment": {"python": platform.python_version(), "sympy": sympy.__version__,
                                  "lab": __version__},
                  "code_sha256": code_fingerprint(),
                  "payload_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
                  "payload": payload, "status": payload["status"]}
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self.directory / f"{record_id}.json"
        with target.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        return target
