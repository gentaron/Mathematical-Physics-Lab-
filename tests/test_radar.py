"""Deep-tech radar: parsing, hostile-input refusal, ranking, search and outputs (offline)."""

from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

import pytest

from research.radar import engine
from research.radar.__main__ import main as radar_main

NOW = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)
CONFIG_PATH = Path("research/radar/sources.json")

ARXIV_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:arxiv="http://arxiv.org/schemas/atom" xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
<channel><title>math.NT updates on arXiv.org</title>
<item><title>A proof of the local Langlands correspondence for GL(n) in families</title>
<link>https://arxiv.org/abs/2611.01234</link>
<description>arXiv:2611.01234v1 Announce Type: new
Abstract: We prove a long-standing conjecture on automorphic forms.</description>
<guid isPermaLink="false">oai:arXiv.org:2611.01234v1</guid>
<category>math.NT</category><pubDate>Tue, 18 Nov 2026 00:00:00 -0500</pubDate>
<arxiv:announce_type>new</arxiv:announce_type>
<dc:creator>Peter Scholze, Laurent Fargues</dc:creator></item>
<item><title>Old paper, new version</title><link>https://arxiv.org/abs/2001.00001</link>
<description>arXiv:2001.00001v4 Announce Type: replace Abstract: Langlands again.</description>
<pubDate>Tue, 18 Nov 2026 00:00:00 -0500</pubDate><arxiv:announce_type>replace</arxiv:announce_type></item>
<item><title>Bounds for sums of divisor functions</title><link>https://arxiv.org/abs/2611.09999</link>
<description>Abstract: Elementary estimates.</description><pubDate>Tue, 18 Nov 2026 00:00:00 -0500</pubDate></item>
</channel></rss>"""

ATOM = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>Blog</title>
<entry><title type="html">&lt;b&gt;Kakeya&lt;/b&gt; in three dimensions</title>
<link rel="alternate" href="https://terrytao.wordpress.com/2026/11/17/kakeya/?utm_source=rss&amp;p=1"/>
<id>tag:blog,2026:1</id><updated>2026-11-17T10:00:00Z</updated>
<author><name>Terence Tao</name></author>
<summary type="html">&lt;p&gt;Hong Wang and Joshua Zahl&lt;script&gt;alert(1)&lt;/script&gt; settle it.&lt;/p&gt;</summary></entry>
</feed>""".encode()

RDF = b"""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
<item rdf:about="https://www.nature.com/articles/s41567-026-0001-x">
<title>Holographic dark matter from AdS/CFT</title><link>https://www.nature.com/articles/s41567-026-0001-x</link>
<description>A new particle candidate.</description><dc:date>2026-11-16</dc:date>
<dc:identifier>doi:10.1038/s41567-026-0001-x</dc:identifier></item>
<item rdf:about="https://www.nature.com/articles/x2"><title>Author Correction: Holographic dark matter</title>
<link>https://www.nature.com/articles/x2</link><dc:date>2026-11-16</dc:date></item>
</rdf:RDF>"""


def small_config(**changes) -> dict:
    config = {
        "schema": "deeptech.radar.config/1", "id": "test-radar", "title": "Test Radar", "description": "test",
        "site_url": "https://example.org", "public_path": "radar",
        "allow_hosts": ["rss.arxiv.org", "terrytao.wordpress.com", "www.nature.com"],
        "topics": {"nt": {"label": "数論", "keywords": ["Langlands", "automorphic"]},
                   "an": {"label": "解析", "keywords": ["Kakeya"]},
                   "hep": {"label": "HEP", "keywords": ["AdS/CFT", "dark matter"]}},
        "signals": {"long-standing": 1.0, "settle": 1.5}, "demote": {"author correction": -4},
        "watch_authors": ["Peter Scholze", "Hong Wang"],
        "limits": {"min_score": 0},
        "sources": [
            {"id": "arxiv-nt", "name": "arXiv math.NT", "url": "https://rss.arxiv.org/rss/math.NT", "tier": 2,
             "topics": ["nt"], "require_topic": True},
            {"id": "tao", "name": "Tao", "url": "https://terrytao.wordpress.com/feed/", "tier": 1, "topics": ["an"]},
            {"id": "nphys", "name": "Nature Physics", "url": "https://www.nature.com/nphys.rss", "tier": 1,
             "topics": ["hep"], "require_topic": True},
        ],
    }
    config.update(changes)
    return engine.validate_config(config)


def fixtures(tmp_path: Path) -> Path:
    d = tmp_path / "fixtures"
    d.mkdir()
    (d / "arxiv-nt.xml").write_bytes(ARXIV_RSS)
    (d / "tao.xml").write_bytes(ATOM)
    (d / "nphys.xml").write_bytes(RDF)
    return d


def run_small(tmp_path: Path, config: dict | None = None) -> tuple[dict, Path]:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config or small_config()), encoding="utf-8")
    out = tmp_path / "out"
    radar = engine.run(path, out, fixtures=fixtures(tmp_path), site=True, now=NOW, log=lambda *_: None)
    return radar, out


# --------------------------------------------------------------------------- parsing

def test_three_feed_dialects_parse_and_clean():
    rss, atom, rdf = engine.parse_feed(ARXIV_RSS), engine.parse_feed(ATOM), engine.parse_feed(RDF)
    assert len(rss) == 3 and len(atom) == 1 and len(rdf) == 2
    source = {"id": "tao", "url": "https://terrytao.wordpress.com/feed/", "tier": 1}
    item = engine.normalise(atom[0], source, NOW)
    assert item["title"] == "Kakeya in three dimensions"
    assert "alert" not in item["summary"] and "<" not in item["summary"]
    assert item["url"] == "https://terrytao.wordpress.com/2026/11/17/kakeya/?p=1", "tracking parameters are removed"
    arxiv = engine.normalise(rss[0], {"id": "a", "url": "https://rss.arxiv.org/rss/math.NT", "tier": 2}, NOW)
    assert arxiv["arxiv"] == "2611.01234" and arxiv["key"] == "arxiv:2611.01234"
    assert arxiv["summary"].startswith("We prove"), "the arXiv announce prefix is stripped"
    assert arxiv["authors"] == ["Peter Scholze", "Laurent Fargues"]
    assert engine.normalise(rss[1], {"id": "a", "url": "https://rss.arxiv.org/x", "tier": 2}, NOW) is None, \
        "replacement announcements are not frontier news"
    nature = engine.normalise(rdf[0], {"id": "n", "url": "https://www.nature.com/nphys.rss", "tier": 1}, NOW)
    assert nature["doi"] == "10.1038/s41567-026-0001-x"


@pytest.mark.parametrize("payload", [
    b'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;">]><rss><channel><item><title>&b;</title></item></channel></rss>',
    b'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><rss><channel><item><title>&x;</title></item></channel></rss>',
    b'<?xml version="1.0"?><!doctype r [<!entity x SYSTEM "https://evil.example/">]><rss/>',
    b"<rss><channel><item><title>unterminated",
])
def test_hostile_or_broken_xml_is_refused(payload):
    with pytest.raises(engine.RadarError):
        engine.parse_feed(payload)


def test_plain_doctype_without_entities_is_tolerated():
    data = b'<?xml version="1.0"?><!DOCTYPE rss PUBLIC "-//Netscape//DTD RSS 0.91//EN" "http://x/rss.dtd"><rss><channel><item><title>t</title><link>https://a.example/1</link></item></channel></rss>'
    assert engine.parse_feed(data)[0]["title"] == "t"


def test_dangerous_links_and_invisible_characters_never_survive():
    for bad in ("javascript:alert(1)", "data:text/html,x", "/relative", "https://user:pw@a.example/",
                "https://a.example:8443/x", "ftp://a.example/", "https://a.exa‮mple/"):
        assert engine.safe_link(bad) is None, bad
    text = engine.clean_text("Safe‮ txt.exe​ \x00 title⁦", 100)
    assert text == "Safe txt.exe title"
    long = engine.clean_text("word " * 500, 50)
    assert len(long) <= 50 and long.endswith("…")


def test_only_https_to_allowed_hosts_is_fetchable():
    allow = frozenset({"rss.arxiv.org"})
    assert engine.check_url("https://rss.arxiv.org/rss/math.NT", allow)
    for bad in ("http://rss.arxiv.org/rss", "https://evil.example/", "file:///etc/passwd",
                "https://rss.arxiv.org:8080/", "https://u@rss.arxiv.org/"):
        with pytest.raises(engine.RadarError):
            engine.check_url(bad, allow)
    opener = engine.build_opener(allow)
    kinds = {type(h).__name__ for h in opener.handlers}
    assert "HTTPHandler" not in kinds and "FileHandler" not in kinds and "FTPHandler" not in kinds
    assert "DataHandler" not in kinds and "HTTPSHandler" in kinds
    redirect = next(h for h in opener.handlers if isinstance(h, engine._CheckedRedirect))
    request = urllib.request.Request("https://rss.arxiv.org/rss/math.NT")
    with pytest.raises(engine.RadarError):
        redirect.redirect_request(request, None, 302, "Found", {}, "https://evil.example/steal")
    with pytest.raises(engine.RadarError):
        redirect.redirect_request(request, None, 302, "Found", {}, "http://rss.arxiv.org/downgrade")


def test_decompression_bomb_is_refused():
    bomb = gzip.compress(b"\0" * (engine.MAX_FEED_BYTES + 10))
    with pytest.raises(engine.RadarError):
        engine._decode_body(bomb, "gzip")
    assert engine._decode_body(gzip.compress(b"<rss/>"), "gzip") == b"<rss/>"
    with pytest.raises(engine.RadarError):
        engine._decode_body(b"x", "br")


def test_config_validation_refuses_unsafe_sources():
    base = small_config()
    with pytest.raises(engine.RadarError):
        small_config(sources=[dict(base["sources"][0], url="http://rss.arxiv.org/rss/math.NT")])
    with pytest.raises(engine.RadarError):
        small_config(sources=[dict(base["sources"][0], url="https://not-allowed.example/feed")])
    with pytest.raises(engine.RadarError):
        small_config(sources=[dict(base["sources"][0], topics=["nope"])])
    with pytest.raises(engine.RadarError):
        small_config(allow_hosts=["*.arxiv.org"])


# --------------------------------------------------------------------------- ranking & archive

def test_ranking_is_explained_and_off_topic_items_are_dropped(tmp_path):
    radar, _ = run_small(tmp_path)
    titles = [i["title"] for i in radar["items"]]
    assert "Bounds for sums of divisor functions" not in titles, "arXiv items must hit a topic"
    assert "Old paper, new version" not in titles
    top = next(i for i in radar["items"][:2] if i["title"].startswith("A proof of the local Langlands"))
    assert top["rank"] < top["score"], "older items decay"
    assert any("watched author Peter Scholze" in w for w in top["why"])
    correction = next(i for i in radar["items"] if i["title"].startswith("Author Correction"))
    assert correction["score"] < next(i for i in radar["items"] if i["title"].startswith("Holographic"))["score"]
    kakeya = next(i for i in radar["items"] if "Kakeya" in i["title"])
    assert any("mentions Hong Wang" in w for w in kakeya["why"]) and "an" in kakeya["topics"]
    assert radar["trust"] == engine.TRUST_LABEL and radar["health"] == {"sources": 3, "ok": 3, "failed": 0}


def test_cross_source_duplicates_merge_and_archive_persists(tmp_path):
    radar, out = run_small(tmp_path)
    first = {i["key"]: i for i in radar["items"]}
    again = engine.parse_feed(ARXIV_RSS)
    twin = engine.normalise(again[0], {"id": "nphys", "url": "https://www.nature.com/nphys.rss", "tier": 1}, NOW)
    archive = engine.load_archive(out / "radar.json")
    rebuilt = engine.build(small_config(), [twin], archive, radar["sources"], NOW)
    merged = next(i for i in rebuilt["items"] if i["key"] == "arxiv:2611.01234")
    assert merged["sources"] == ["arxiv-nt", "nphys"] and merged["tier"] == 1
    assert merged["score"] > first["arxiv:2611.01234"]["score"]
    assert len(rebuilt["items"]) == len(radar["items"]), "nothing is lost between runs"


def test_failed_sources_keep_the_archive(tmp_path):
    radar, out = run_small(tmp_path)
    path = tmp_path / "config.json"
    empty = tmp_path / "nofixtures"
    empty.mkdir()
    again = engine.run(path, out, fixtures=empty, now=NOW, log=lambda *_: None)
    assert again["health"]["ok"] == 0 and len(again["items"]) == len(radar["items"])


def test_tampered_archive_is_re_sanitised(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    evil = {"schema": engine.SCHEMA, "items": [
        {"key": "url:x", "title": "<img src=x onerror=alert(1)>Langlands", "url": "javascript:alert(1)",
         "date": "2026-11-18T00:00:00Z", "sources": ["arxiv-nt"]},
        {"key": "url:y", "title": "Langlands ‮evil", "url": "https://a.example/y",
         "date": "2026-11-18T00:00:00Z", "sources": ["arxiv-nt", "../../etc"]}]}
    (out / "radar.json").write_text(json.dumps(evil))
    archive = engine.load_archive(out / "radar.json")
    assert [i["url"] for i in archive["items"]] == ["https://a.example/y"]
    assert archive["items"][0]["title"] == "Langlands evil" and archive["items"][0]["sources"] == ["arxiv-nt"]


# --------------------------------------------------------------------------- search & outputs

def test_search_language(tmp_path):
    radar, out = run_small(tmp_path)
    titles = lambda q: [i["title"] for i in engine.search(radar, q, now=NOW)]  # noqa: E731
    assert titles("langlands")[0].startswith("A proof")
    assert titles('"local langlands" au:scholze') and not titles("au:tao langlands")
    assert all("Correction" not in t for t in titles("holographic -correction"))
    assert titles("topic:an") == ["Kakeya in three dimensions"]
    assert titles("tier:1 since:3d") and not titles("tier:1 since:2d") and not titles("since:2026-11-19")
    assert titles("kakéya"), "accents are folded"
    assert radar_main(["search", "langlands", "--data", str(out / "radar.json"), "--json"]) == 0


def test_outputs_are_well_formed_and_escaped(tmp_path):
    radar, out = run_small(tmp_path)
    for name in ("feed.xml", "feed-nt.xml", "feed-an.xml", "feed-hep.xml", "sources.opml"):
        ET.fromstring((out / name).read_bytes())
    feed = ET.fromstring((out / "feed.xml").read_bytes())
    assert feed.find("channel/{http://www.w3.org/2005/Atom}link").get("href") == "https://example.org/radar/feed.xml"
    page = (out / "index.html").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in page and "script-src 'self'" in page and "<script>alert" not in page
    assert 'rel="noopener noreferrer nofollow"' in page and "application/ld+json" in page
    data = json.loads((out / "radar.json").read_text(encoding="utf-8"))
    assert data["schema"] == engine.SCHEMA and all(i["url"].startswith("https://") for i in data["items"])


def test_page_escapes_hostile_titles():
    config = small_config()
    radar = {"title": "T", "description": "D", "generated_at": "2026-11-19T00:00:00Z", "health": {"ok": 1, "sources": 1},
             "ranking": {"half_life_days": 10}, "topics": [{"id": "nt", "label": "<b>x</b>", "count": 1}],
             "items": [{"id": "1", "title": '"><script>alert(1)</script>', "url": 'https://a.example/"onmouseover=x',
                        "date": "2026-11-19T00:00:00Z", "source_names": ["s"], "score": 1, "authors": [],
                        "summary": "</p><iframe>", "topics": ["nt"]}]}
    page = engine.render_page(config, radar)
    assert "<script>alert" not in page and "<iframe>" not in page and "<b>x</b>" not in page
    assert 'href="https://a.example/"' not in page and "&quot;onmouseover" in page


def test_shipped_config_is_valid_and_https_only():
    config = engine.load_config(CONFIG_PATH)
    assert all(s["url"].startswith("https://") for s in config["sources"])
    assert {"prizes", "math-ai", "number-theory", "hep-gravity"} <= set(config["topics"])
    assert radar_main(["validate", "--config", str(CONFIG_PATH)]) == 0


# --------------------------------------------------------------------------- v2: APIs, paging, archive shards

BIORXIV_JSON = json.dumps({"messages": [{"status": "ok"}], "collection": [
    {"title": "Prime editing of <i>HBB</i> in vivo", "authors": "Liu, D. R.; Doe, J.", "doi": "10.1101/2026.11.10.000001",
     "date": "2026-11-12", "version": "2", "category": "genomics", "abstract": "We prove a long-standing Langlands conjecture.",
     "server": "bioRxiv"},
    {"title": "Bad doi", "doi": "javascript:alert(1)", "date": "2026-11-12"}, "not-a-dict"]}).encode()

EPMC_JSON = json.dumps({"nextCursorMark": "AoJ1", "resultList": {"result": [
    {"id": "123", "source": "MED", "doi": "10.1038/s41586-026-0001-1", "title": "Automorphic forms at scale",
     "authorString": "Scholze P, Fargues L.", "journalTitle": "Nature", "firstPublicationDate": "2026-11-01",
     "citedByCount": 250, "abstractText": "<h4>Abstract</h4>Langlands programme."},
    {"id": "../../x", "source": "MED", "title": "No link at all", "firstPublicationDate": "2026-11-01"}]}}).encode()


def test_json_apis_are_parsed_and_sanitised():
    rows, count = engine.parse_biorxiv(BIORXIV_JSON)
    assert count == 3 and len(rows) == 2
    assert rows[0]["link"] == "https://www.biorxiv.org/content/10.1101/2026.11.10.000001v2"
    assert rows[0]["authors"] == ["Liu, D. R.", "Doe, J."] and rows[1]["link"] == ""
    epmc, cursor = engine.parse_europepmc(EPMC_JSON)
    assert cursor == "AoJ1" and epmc[0]["cited_by"] == 250 and epmc[0]["venue"] == "Nature"
    assert epmc[0]["link"] == "https://doi.org/10.1038/s41586-026-0001-1" and epmc[1]["link"] == ""
    item = engine.normalise(epmc[0], {"id": "e", "url": "https://www.ebi.ac.uk/x", "tier": 2}, NOW)
    assert item["summary"] == "Abstract Langlands programme." and item["key"] == "doi:10.1038/s41586-026-0001-1"
    for bad in (b"[]", b"{", b'{"collection": 3}', b"\xff"):
        with pytest.raises(engine.RadarError):
            engine.parse_biorxiv(bad)
    with pytest.raises(engine.RadarError):
        engine.parse_europepmc(b'{"resultList": {}}')


def test_url_templates_and_unknown_placeholders():
    url = engine.expand_url("https://api.biorxiv.org/details/biorxiv/{since:3}/{today}/{cursor}?o={offset}", NOW, "a b/c", 400)
    assert url == "https://api.biorxiv.org/details/biorxiv/2026-11-16/2026-11-19/a%20b%2Fc?o=400"
    base = small_config()
    with pytest.raises(engine.RadarError):
        small_config(sources=[dict(base["sources"][0], url="https://rss.arxiv.org/{host}")])
    with pytest.raises(engine.RadarError):
        small_config(sources=[dict(base["sources"][0], max_pages=99)])
    with pytest.raises(engine.RadarError):
        small_config(sources=[dict(base["sources"][0], format="html")])


def test_archive_is_sharded_by_month_and_reloaded(tmp_path):
    config = small_config(limits={"min_score": 0, "index_max": 100})
    old = dict(engine.normalise(engine.parse_feed(ARXIV_RSS)[0], {"id": "arxiv-nt", "url": "https://rss.arxiv.org/x", "tier": 2}, NOW),
               date="2025-06-01T00:00:00Z", key="url:https://example.org/old", title="Langlands in 2025")
    radar = engine.build(config, [old], {"items": []}, [], NOW)
    out = tmp_path / "out"
    engine.write_outputs(config, radar, out)
    index = json.loads((out / "archive" / "index.json").read_text())
    assert [m["file"] for m in index["months"]] == ["2025-06.json"]
    (out / "archive" / "1999-01.json").write_text("{}")
    archive = engine.load_archive(out / "radar.json")
    assert [i["title"] for i in archive["items"]] == ["Langlands in 2025"]
    engine.write_outputs(config, engine.build(config, [], archive, [], NOW), out)
    assert not (out / "archive" / "1999-01.json").exists(), "stale shards are pruned"
    found = engine.load_search(out / "radar.json")
    assert len(found["items"]) == 1


def test_corroboration_counts_publishers_not_feeds():
    config = small_config(sources=small_config()["sources"] + [
        {"id": "arxiv-nt2", "name": "arXiv math.AG", "url": "https://rss.arxiv.org/rss/math.AG", "tier": 2, "topics": ["nt"]}])
    item = engine.normalise(engine.parse_feed(ARXIV_RSS)[0], {"id": "arxiv-nt", "url": "https://rss.arxiv.org/x", "tier": 2}, NOW)
    twin = dict(item, sources=["arxiv-nt2"])
    merged = engine.merge([item, twin])[0]
    scored = engine.Scorer(config).score(merged)
    assert not any("reported by" in w for w in scored["why"])
    assert engine._detex(r"Erd\H{o}s") == "Erdos"


def test_general_topics_count_for_less():
    base = small_config()
    topics = dict(base["topics"], general={"label": "全般", "weight": 0.3, "keywords": ["mathematics"]})
    config = small_config(topics=topics)
    raw = {"title": "Mathematics of everything", "link": "https://a.example/1", "date": "2026-11-18"}
    item = engine.normalise(raw, {"id": "tao", "url": "https://terrytao.wordpress.com/feed/", "tier": 1}, NOW)
    scored = engine.Scorer(config).score(item)
    assert scored["topics"] == ["general"] and "topics general +0.3" in scored["why"]
    with pytest.raises(engine.RadarError):
        small_config(topics=dict(topics, general=dict(topics["general"], weight=9)))
