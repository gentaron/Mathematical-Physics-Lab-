import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


def run_cli(*args):
    return subprocess.run([sys.executable, "-m", "research", *args],
                          capture_output=True, text=True, timeout=45, env=os.environ.copy())


def test_complete_cli_run_preserves_records(tmp_path):
    first = run_cli("run", "--max-vertices", "6", "--output", str(tmp_path))
    assert first.returncode == 0, first.stderr
    second = run_cli("run", "--max-vertices", "5", "--output", str(tmp_path))
    assert second.returncode == 0, second.stderr
    runs = sorted(tmp_path.glob("run-*"))
    assert len(runs) == 2
    six = next(json.loads((r / "run.json").read_text()) for r in runs
               if json.loads((r / "run.json").read_text())["max_vertices"] == 6)
    assert six["geometry"][-1]["codimension_vector"] == [1, 44, 114, 72]
    assert six["all_reproductions_passed"] is True
    assert six["formal_proofs_checked"] is False
    assert all(r["status"] == "counterexample" for r in six["hypotheses"])
    assert all((r / "journal.md").exists() and list((r / "ledger").glob("*.json")) for r in runs)


def test_cli_rejects_oversized_request_before_creating_output(tmp_path):
    result = run_cli("run", "--max-vertices", "8", "--output", str(tmp_path / "out"))
    assert result.returncode == 2
    assert not (tmp_path / "out").exists()


def test_cli_verify_reports_counterexample(tmp_path):
    from research.director import propose
    file = tmp_path / "candidate.json"
    file.write_text(json.dumps(propose([3, 4, 5], [6])[0]))
    result = run_cli("verify", "--candidate", str(file))
    assert result.returncode == 1
    assert json.loads(result.stdout)["counterexample"]["polygon_vertices"] == 6


def test_cli_malformed_json_and_executable_payload_fail_cleanly(tmp_path):
    file = tmp_path / "bad.json"
    for content in ("{", '{"coefficients":["__import__(\\"os\\")"]}'):
        file.write_text(content)
        result = run_cli("verify", "--candidate", str(file))
        assert result.returncode == 2
        assert "Traceback" not in result.stderr


def test_optional_ai_uses_local_structured_api_and_does_not_execute_text():
    from research.ollama import propose_with_ollama
    from research.director import propose
    requests = []
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append((self.path, body))
            if self.path == "/api/show":
                value = {"model_info": {"general.architecture": "test"}}
            else:
                proposal = propose([3, 4, 5], [6])[0]
                proposal["source"] = "ollama"
                value = {"response": json.dumps({"candidates": [proposal]})}
            data = json.dumps(value).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        def log_message(self, *args):
            pass
    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        proposals = propose_with_ollama("local-model", [3, 4, 5], [6],
                                       base_url=f"http://127.0.0.1:{server.server_port}")
        server.shutdown()
        thread.join(timeout=5)
    assert proposals[0]["source"] == "ollama"
    assert requests[-1][1]["stream"] is False
    assert requests[-1][1]["format"] == "json"


@pytest.mark.parametrize("url,model", [
    ("https://paid.example.com", "local"), ("http://127.0.0.1:11434", "qwen3:cloud"),
    ("http://localhost:11434/api", "local"), ("http://user:pass@localhost:11434", "local"),
])
def test_ai_rejects_cloud_targets_without_network(url, model):
    from research.ollama import propose_with_ollama
    with pytest.raises(ValueError):
        propose_with_ollama(model, [3, 4, 5], [6], base_url=url)


def test_doctor_is_read_only_and_lists_optional_tools():
    result = run_cli("doctor")
    assert result.returncode == 0
    value = json.loads(result.stdout)
    assert value["required"]["sympy"] == "1.14.0"
    assert {"lean", "lake", "polymake", "sage", "ollama"} <= set(value["optional"])


def test_reconstruct_two_site_from_constraints():
    from research.cosmological_bootstrap.correlators import reconstruct_two_site
    result = reconstruct_two_site()
    assert result["unique_within_ansatz"] is True
    assert result["coefficients"] == {"c0": "1", "c1": "0", "c2": "0", "c3": "0"}
    assert result["scope"] == "linear_numerator_fixed_denominator_flat_space_scalar_tree"


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="POSIX FIFO input check")
def test_cli_rejects_fifo_candidate_without_blocking(tmp_path):
    fifo = tmp_path / "candidate-pipe"
    os.mkfifo(fifo)
    result = subprocess.run([sys.executable, "-m", "research", "verify", "--candidate", str(fifo)],
                            capture_output=True, text=True, timeout=3)
    assert result.returncode == 2
    assert "regular file" in result.stderr


def test_candidate_reader_checks_actual_read_size(tmp_path):
    from research.cli import _read_candidate
    candidate = tmp_path / "oversized.json"
    candidate.write_bytes(b" " * 65537)
    # The read bound is independent of the stale/preflight file size.
    with pytest.raises(ValueError, match="64 KiB"):
        _read_candidate(candidate)


def test_incompatible_ai_arguments_rejected_without_partial_output(tmp_path):
    output = tmp_path / "out"
    result = run_cli("run", "--max-vertices", "3", "--ollama-model", "local", "--output", str(output))
    assert result.returncode == 2
    assert not output.exists()


def test_malformed_local_http_becomes_optional_ai_error():
    from research.ollama import propose_with_ollama
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.connection.sendall(b"not-an-http-status\r\n\r\n")
            self.close_connection = True
        def log_message(self, *args):
            pass
    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with pytest.raises(RuntimeError, match="unavailable"):
                propose_with_ollama("local-model", [3, 4, 5], [6],
                    base_url=f"http://127.0.0.1:{server.server_port}", timeout=1)
        finally:
            server.shutdown()
            thread.join(timeout=5)
