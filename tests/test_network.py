import json

from research.network import FEED_SCHEMA, build_feed, collect_leads, find_leads, match_topics
from research.positive_geometry.higher import higher_dimensions


def test_feed_has_the_network_shape_and_only_https_links():
    latest = {"created_at": "2026-10-12T11:00:45+00:00",
              "geometry": [{"polygon_vertices": 6, "polytope_dimension": 3, "codimension_vector": [1, 44, 114, 72], "reference_matches": True}],
              "amplitudes": [{"polygon_vertices": 5, "triangulations": 5, "passed": False}]}
    feed = build_feed(latest, higher_dimensions(9), generated_at="2026-11-11T00:00:00Z")
    assert feed["schema"] == FEED_SCHEMA and feed["repo"] == "Mathematical-Physics-Lab-"
    assert all(i["url"].startswith("https://") for i in feed["items"])
    by_id = {i["id"]: i for i in feed["items"]}
    assert by_id["cosmohedron-n6"]["evidence"] == "verified"
    assert by_id["amplitude-n5"]["evidence"] == "draft", "a failed check must not be published as verified"
    assert {"cosmohedron-higher-n8", "cosmohedron-higher-n9"} <= by_id.keys()


def test_leads_keep_physics_and_drop_ai_news():
    docs = [
        {"title": "Combinatorics of cosmohedra", "url": "https://arxiv.org/abs/1", "date": "2026-11-01", "source": "arXiv math-ph"},
        {"title": "A bootstrap for LLM agents", "url": "https://x.com/2", "date": "2026-11-02", "source": "HN"},
        {"title": "Faster polytope f-vector code", "url": "https://arxiv.org/abs/3", "date": "2026-11-03", "source": "arXiv"},
        {"title": "Lab: cosmohedron n=8", "url": "https://github.com/x", "source": "Network · Mathematical-Physics-Lab-"},
        {"title": "Cosmohedron paper", "url": "https://arxiv.org/abs/known", "date": "2026-10-01"},
    ]
    leads = find_leads(docs, known_urls={"https://arxiv.org/abs/known"})
    assert [l["url"] for l in leads] == ["https://arxiv.org/abs/3", "https://arxiv.org/abs/1"] or \
        sorted(l["url"] for l in leads) == ["https://arxiv.org/abs/1", "https://arxiv.org/abs/3"]
    assert all(l["status"] == "unverified lead" for l in leads)
    assert match_topics("on-shell bootstrap") == ["scattering-amplitudes"]
    assert match_topics("polytopes") == [], "whole words only"


def test_leads_read_a_local_kb_and_survive_a_missing_one(tmp_path):
    kb = tmp_path / "kb"
    (kb / "shards").mkdir(parents=True)
    (kb / "manifest.json").write_text(json.dumps({"shards": [{"key": "2026-11"}]}))
    (kb / "shards" / "2026-11.jsonl").write_text(json.dumps({"title": "New amplituhedron results", "url": "https://arxiv.org/abs/9", "date": "2026-11-05"}) + "\n")
    out = tmp_path / "leads.json"
    result = collect_leads(tmp_path / "none.json", out, kb_url=str(kb))
    assert result["status"] == "ok" and result["leads"][0]["url"] == "https://arxiv.org/abs/9"
    missing = collect_leads(tmp_path / "none.json", out, kb_url=str(tmp_path / "nowhere"))
    assert missing["status"] == "unreachable" and missing["leads"] == []
