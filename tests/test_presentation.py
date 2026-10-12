import copy
from html.parser import HTMLParser
import json
from pathlib import Path

import pytest


@pytest.fixture
def report():
    return json.loads(Path('research/results/reference/run.json').read_text())


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def test_homepage_explains_actual_results_without_runtime_dependencies(report):
    from research.presentation import render_homepage
    html = render_homepage(report)
    page = Page()
    page.feed(html)
    text = ''.join(page.text)
    assert '72' in text and '114' in text and '44' in text
    assert '25' in text and '反例' in text
    assert '次に調べたい問い' in text and '既知結果の再現' in text
    assert 'script' not in page.tags and 'img' not in page.tags
    assert ('meta', {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}) in page.attrs
    assert 'details' in page.tags and 'summary' in page.tags
    assert not any(tag == 'link' and attrs.get('rel') == 'stylesheet' for tag, attrs in page.attrs)
    anchors = {attrs['id'] for tag, attrs in page.attrs if 'id' in attrs}
    assert all(attrs['href'][1:] in anchors for tag, attrs in page.attrs
               if tag == 'a' and attrs.get('href', '').startswith('#'))


def test_homepage_escapes_report_text(report):
    from research.presentation import render_homepage
    report['run_id'] = '<script>alert(1)</script>'
    html = render_homepage(report)
    assert '<script>' not in html
    assert '&lt;script&gt;' in html


def test_unverified_or_inconsistent_figures_are_not_published(report):
    from research.presentation import render_homepage
    for mutation in ('unverified', 'wrong_count'):
        bad = copy.deepcopy(report)
        if mutation == 'unverified':
            bad['all_reproductions_passed'] = False
        else:
            bad['geometry'][-1]['codimension_vector'][-1] = 999
        with pytest.raises(ValueError):
            render_homepage(bad)


def test_site_export_is_a_selected_static_snapshot(report, tmp_path):
    from research.presentation import export_site
    source = tmp_path / 'run.json'
    source.write_text(json.dumps(report))
    output = tmp_path / 'site'
    export_site(source, output)
    assert (output / 'index.html').exists()
    assert (output / '.nojekyll').exists()
    assert json.loads((output / 'latest.json').read_text()) == report
    assert 'href="latest.json"' in (output / 'index.html').read_text()
    assert source.read_text() == json.dumps(report)
