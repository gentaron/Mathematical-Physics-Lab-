"""The lab as a node of the gentaron network.

Out: ``feed`` writes docs/feed.json (gentaron.feed/1). The hub's knowledge base
pulls it daily, so a verified count here can be found from any repository.

In: ``leads`` reads the hub's knowledge base (arXiv math-ph / hep-th and
everything else it collects) and keeps the papers that mention this lab's
subjects. They are leads, not sources: nothing in a lead is used as evidence
until it has been reproduced here (see papers/sources.json for what was).

Standard library only, and fail-soft: no network means no leads, not an error.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen

FEED_SCHEMA = "gentaron.feed/1"
REPO = "Mathematical-Physics-Lab-"
BLOB = f"https://github.com/gentaron/{REPO}/blob/HEAD"
KB_URL = os.environ.get("MATHLAB_KB_URL", "https://raw.githubusercontent.com/gentaron/infocollect/HEAD/docs/kb")

# What this lab studies. A lead must hit one of these; generic AI news must not.
TOPICS = {
    "cosmohedron": ["cosmohedron", "cosmohedra"],
    "positive-geometry": ["positive geometry", "amplituhedron", "associahedron", "canonical form"],
    "cosmological-correlators": ["cosmological correlator", "wavefunction of the universe", "cosmological bootstrap", "kinematic flow"],
    "scattering-amplitudes": ["scattering amplitude", "on-shell", "bootstrap"],
    "polytopes": ["polytope", "f-vector", "face lattice", "matryoshka"],
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_feed(latest: dict | None, higher: list[dict] | None, generated_at: str | None = None) -> dict:
    items = []
    day = (generated_at or _now())[:10]
    if latest:
        run_day = str(latest.get("created_at", day))[:10]
        for g in latest.get("geometry", []):
            n = g["polygon_vertices"]
            items.append({
                "id": f"cosmohedron-n{n}",
                "title": f"コスモヘドロン（{n}頂点・{g['polytope_dimension']}次元）の面の数 {g['codimension_vector']}",
                "url": f"{BLOB}/docs/latest.json",
                "date": run_day,
                "kind": "research",
                "summary": "全 Matryoshka の列挙と独立した漸化式が一致し、論文の表とも一致" if g.get("reference_matches")
                           else "列挙と論文の表が一致しない（要確認）",
                "tags": ["cosmohedron", "positive-geometry", "polytopes"],
                "evidence": "verified" if g.get("reference_matches") else "draft",
            })
        for a in latest.get("amplitudes", []):
            items.append({
                "id": f"amplitude-n{a['polygon_vertices']}",
                "title": f"平面三次スカラー振幅（{a['polygon_vertices']}点・三角形分割 {a['triangulations']} 個）の留数と因子化",
                "url": f"{BLOB}/docs/latest.json",
                "date": run_day,
                "kind": "research",
                "summary": "全チャネルの留数が因子化と一致" if a.get("passed") else "留数の検査が通らない",
                "tags": ["scattering-amplitudes", "positive-geometry"],
                "evidence": "verified" if a.get("passed") else "draft",
            })
    for r in higher or []:
        if not r["beyond_reference"]:
            continue
        ok = r["methods_agree"] and r["euler_ok"]
        items.append({
            "id": f"cosmohedron-higher-n{r['polygon_vertices']}",
            "title": f"論文の表の先: {r['polygon_vertices']}頂点・{r['polytope_dimension']}次元コスモヘドロンの面の数",
            "url": f"{BLOB}/docs/higher.json",
            "date": day,
            "kind": "research",
            "summary": (f"頂点 {r['vertices_of_polytope']}、余次元ごと {r['codimension_vector']}。"
                        "解き方を共有しない2つの数え方が一致し、オイラー＝ポアンカレ関係も成立。"
                        "論文に参照値は無いので、独立計算による値"),
            "tags": ["cosmohedron", "polytopes", "higher-dimension"],
            "evidence": "verified" if ok else "draft",
        })
    return {"schema": FEED_SCHEMA, "repo": REPO, "generatedAt": generated_at or _now(), "items": items}


def write_feed(latest_path: Path, higher_rows: list[dict], out: Path) -> Path:
    latest = json.loads(latest_path.read_text(encoding="utf-8")) if latest_path.exists() else None
    feed = build_feed(latest, higher_rows)
    out.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


# --- in: leads from the hub's knowledge base ------------------------------

def _get(url: str, timeout: float = 20.0) -> bytes:
    if not url.startswith(("https://", "file://")) and Path(url).exists():
        return Path(url).read_bytes()
    with urlopen(Request(url, headers={"user-agent": "math-lab"}), timeout=timeout) as res:
        return res.read()


def _kb_docs(kb_url: str, months: int) -> list[dict]:
    manifest = json.loads(_get(f"{kb_url}/manifest.json"))
    keys = sorted(s["key"] for s in manifest.get("shards", []))[-months:]
    docs = []
    for key in keys:
        for line in _get(f"{kb_url}/shards/{key}.jsonl").decode("utf-8").splitlines():
            if line.strip():
                docs.append(json.loads(line))
    return docs


def match_topics(text: str) -> list[str]:
    low = text.lower()
    return [topic for topic, words in TOPICS.items()
            if any(re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low) for w in words)]


def find_leads(docs: list[dict], known_urls: set[str], limit: int = 30) -> list[dict]:
    leads = []
    for d in docs:
        text = " ".join(str(d.get(k, "")) for k in ("title", "summary", "body"))
        topics = match_topics(text)
        # "bootstrap" or "on-shell" alone are too broad; ask for a second, specific hit.
        specific = [t for t in topics if t != "scattering-amplitudes"]
        if not specific or d.get("url") in known_urls or "Network · " in str(d.get("source", "")):
            continue
        leads.append({"title": d.get("title"), "url": d.get("url"), "date": d.get("date"),
                      "source": d.get("source"), "topics": topics, "status": "unverified lead"})
    leads.sort(key=lambda x: (len(x["topics"]), str(x["date"])), reverse=True)
    return leads[:limit]


def collect_leads(sources_path: Path, out: Path, kb_url: str = KB_URL, months: int = 3) -> dict:
    known = set()
    if sources_path.exists():
        for s in json.loads(sources_path.read_text(encoding="utf-8")).get("sources", []):
            known.update(v for k, v in s.items() if k in ("url", "html", "paper") and isinstance(v, str))
    try:
        docs = _kb_docs(kb_url, months)
        result = {"status": "ok", "kb": kb_url, "scanned": len(docs)}
    except (OSError, ValueError) as exc:  # offline, 404, broken JSON: no leads today
        docs, result = [], {"status": "unreachable", "kb": kb_url, "error": str(exc)[:200], "scanned": 0}
    result.update({"checked_at": _now(), "leads": find_leads(docs, known),
                   "note": "Leads only. Reproduce before citing; add to sources.json once reproduced."})
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
