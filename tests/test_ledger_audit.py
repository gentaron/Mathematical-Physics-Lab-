"""Reproducibility ledger audit (not a formal correctness check)."""
import json
from research.ledger import Ledger
from research.ledger_audit import audit_directory, audit_record

def test_append_only_record_passes_local_integrity_audit(tmp_path):
    file = Ledger(tmp_path).append({"status": "conjecture", "claim": "bounded test"})
    result = audit_directory(tmp_path)
    assert result["ok"] and result["checked"] == 1
    assert not audit_record(json.loads(file.read_text()), file.name)

def test_modified_result_is_detected(tmp_path):
    file = Ledger(tmp_path).append({"status": "counterexample", "test": 10})
    record = json.loads(file.read_text())
    record["payload"]["test"] = 11
    file.write_text(json.dumps(record), encoding="utf-8")
    assert "payload hash does not match content" in audit_record(record, file.name)
    assert not audit_directory(tmp_path)["ok"]

def test_forged_formal_proof_and_missing_ledger_rejected(tmp_path):
    file = Ledger(tmp_path).append({"status": "symbolic_verified", "algebra": True})
    record = json.loads(file.read_text())
    record["status"] = "formally_proved"
    assert any("formal proof" in error for error in audit_record(record, file.name))
    assert not audit_directory(tmp_path / "empty")["ok"]
