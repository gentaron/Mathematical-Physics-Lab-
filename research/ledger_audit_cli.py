"""Run: python -m research.ledger_audit_cli PATH_TO_LEDGER"""
import json
import sys
from pathlib import Path
from .ledger_audit import audit_directory

def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python -m research.ledger_audit_cli PATH_TO_LEDGER", file=sys.stderr)
        return 2
    result = audit_directory(Path(args[0]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
