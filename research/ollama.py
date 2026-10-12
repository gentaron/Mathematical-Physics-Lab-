"""Optional localhost-only Ollama proposals: JSON data, no model downloads."""

import json
from http.client import HTTPException
import re
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .director import count_target
from .hypothesis import validate_candidate


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Ollama redirects are disabled")


def propose_with_ollama(model: str, fit_vertices: list[int], test_vertices: list[int],
                        base_url: str = "http://127.0.0.1:11434", timeout: int = 45) -> list[dict]:
    parsed = urlsplit(base_url)
    if (parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1")
            or parsed.username or parsed.password or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment):
        raise ValueError("Ollama must use an HTTP loopback URL without credentials or paths")
    if (not isinstance(model, str) or not re.fullmatch(r"[a-zA-Z0-9_./:-]{1,128}", model)
            or "cloud" in model.lower()):
        raise ValueError("Select an existing local model; cloud models are disabled")
    if type(timeout) is not int or not 1 <= timeout <= 60:
        raise ValueError("Ollama timeout must be in 1..60 seconds")
    template = validate_candidate({"schema_version": 1, "id": "local-proposal", "target": "vertices",
        "coefficients": ["0"], "fit_vertices": fit_vertices, "test_vertices": test_vertices,
        "source": "ollama", "description": "Propose a polynomial and try to refute it"})
    opener = build_opener(ProxyHandler({}), _NoRedirect())

    def post(path: str, payload: dict) -> dict:
        request = Request(base_url.rstrip("/") + path, data=json.dumps(payload).encode(),
                          headers={"Content-Type": "application/json"}, method="POST")
        try:
            with opener.open(request, timeout=timeout) as response:
                data = response.read(65537)
            if len(data) > 65536:
                raise ValueError("Ollama response exceeds 64 KiB")
            decoded = json.loads(data)
            if not isinstance(decoded, dict):
                raise ValueError("Ollama response must be a JSON object")
            return decoded
        except (URLError, OSError, HTTPException) as exc:
            raise RuntimeError("Local Ollama is unavailable or timed out; no paid fallback used") from exc

    metadata = post("/api/show", {"model": model})
    if (metadata.get("remote_host") or metadata.get("remote_model")
            or not isinstance(metadata.get("model_info"), dict) or not metadata["model_info"]):
        raise ValueError("Model is remote or does not provide local model metadata")
    observations = {target: {str(n): count_target(target, n) for n in fit_vertices}
                    for target in ("vertices", "facets")}
    prompt = ("Return JSON only: {\"candidates\": [candidate, ...]}. Propose at most two rational "
              "polynomials for these cosmohedral counts. N means polygon vertex count. "
              "coefficients are constant term first, at most six short rational strings. "
              "No code. No claims of proof or novelty. Use exactly the fields of this template, "
              "retain fit_vertices and test_vertices, set source=ollama. Template: "
              + json.dumps(template) + " Observed fitting data: " + json.dumps(observations))
    generated = post("/api/generate", {"model": model, "prompt": prompt, "format": "json",
                                       "stream": False, "options": {"temperature": 0,
                                                                       "num_predict": 1200}})
    answer = generated.get("response")
    if not isinstance(answer, str) or len(answer) > 32000:
        raise ValueError("Ollama did not return a bounded JSON response string")
    value = json.loads(answer)
    if not isinstance(value, dict) or set(value) != {"candidates"}:
        raise ValueError("Expected JSON with exactly one candidates field")
    candidates = value["candidates"]
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 2:
        raise ValueError("Ollama must propose one or two candidates")
    normalized = [validate_candidate(c) for c in candidates]
    for candidate in normalized:
        if (candidate["source"] != "ollama" or candidate["fit_vertices"] != fit_vertices
                or candidate["test_vertices"] != test_vertices):
            raise ValueError("Ollama changed source or the held-out experimental protocol")
    return normalized
