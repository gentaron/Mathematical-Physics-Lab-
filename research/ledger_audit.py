"""Offline tamper-evidence audit for mathematical research records.

Matching hashes only show consistency with the saved payload; they DO NOT
prove an asserted mathematical theorem, a dataset's authenticity, or code safety.
"""
from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from .ledger import ALLOWED_STATUSES

HEX32 = re.compile(r"[a-f0-9]{32}\Z")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")

def audit_record(record: object, filename: str = "") -> list[str]:
    if not isinstance(record, dict):
        return ["record is not a JSON object"]
    errors = []
    if record.get("schema_version") != 1:
        errors.append("unsupported schema")
    rid = record.get("record_id")
    if not isinstance(rid, str) or not HEX32.fullmatch(rid):
        errors.append("invalid record_id")
    elif filename and filename != f"{rid}.json":
        errors.append("record id differs from filename")
    status, payload = record.get("status"), record.get("payload")
    if not isinstance(payload, dict) or status not in ALLOWED_STATUSES or payload.get("status") != status:
        errors.append("invalid status or unsupported formal proof claim")
    digest = record.get("payload_sha256")
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        errors.append("invalid payload hash")
    else:
        try:
            encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()
            if sha256(encoded).hexdigest() != digest:
                errors.append("payload hash does not match content")
        except (TypeError, ValueError):
            errors.append("payload is not canonical JSON")
    code_digest = record.get("code_sha256")
    if not isinstance(code_digest, str) or not HEX64.fullmatch(code_digest):
        errors.append("invalid implementation fingerprint")
    env = record.get("environment")
    if not isinstance(env, dict) or any(not isinstance(env.get(k), str) or not env[k] for k in ("lab", "sympy", "python")):
        errors.append("missing environment provenance")
    try:
        stamp = datetime.fromisoformat(record["created_at"])
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            errors.append("creation time has no timezone")
    except (KeyError, TypeError, ValueError):
        errors.append("invalid creation timestamp")
    return errors

def audit_directory(directory: Path) -> dict:
    files = sorted(Path(directory).glob("*.json"))
    errors = []
    if not files:
        errors.append("zero ledger records")
    for file in files:
        try:
            obj = json.loads(file.read_text(encoding="utf-8"))
            errors.extend(f"{file.name}: {message}" for message in audit_record(obj, file.name))
        except (OSError, ValueError) as exc:
            errors.append(f"{file.name}: cannot read JSON ({type(exc).__name__})")
    return {"checked": len(files), "ok": not errors, "errors": errors}
