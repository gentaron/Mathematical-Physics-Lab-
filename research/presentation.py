"""A readable, buildless research homepage. No JavaScript or web server."""

from html import escape
import json
import os
from pathlib import Path
import stat

from .positive_geometry.cosmohedron import REFERENCE_VECTORS

REPOSITORY = "https://github.com/gentaron/Mathematical-Physics-Lab-"
PAPER = "https://arxiv.org/html/2603.03425v3"
POLYGON_NAMES = {3: "三角形", 4: "四角形", 5: "五角形", 6: "六角形", 7: "七角形"}

STYLE = """
* { box-sizing: border-box; }
html { background: #fff; color: #161616; }
body { max-width: 46rem; margin: 0 auto; padding: 2.8rem 1.4rem 2rem;
  font-family: 'Times New Roman', 'Yu Mincho', 'Hiragino Mincho ProN',
    'Noto Serif CJK JP', serif; font-size: 17px; line-height: 1.9; }
header { text-align: center; }
h1 { margin: 0; font-size: clamp(1.8rem, 5vw, 2.4rem); line-height: 1.2;
  font-variant: small-caps; }
header p { margin: .8rem 0 .4rem; }
.date, .note, footer { color: #555; font-size: .86rem; }
a { color: #142e88; text-underline-offset: .18em; overflow-wrap: anywhere; }
a:visited { color: #503070; }
a:hover { text-decoration-thickness: 2px; }
a:focus-visible, summary:focus-visible { outline: 2px solid #142e88; outline-offset: 5px; }
hr { border: 0; border-top: 1px solid #aaa; margin: 1.8rem 0; }
nav ul { display: grid; grid-template-columns: 1fr 1fr; gap: .35rem 2rem;
  padding-left: 1.4rem; margin: 0; }
main { margin-top: 2.5rem; }
section { margin: 2.5rem 0; scroll-margin-top: 1rem; }
h2 { font-size: 1.35rem; line-height: 1.6; margin: 0 0 1rem; }
h3 { font-size: 1.12rem; line-height: 1.7; margin: 1.9rem 0 .5rem; }
p { margin: .7rem 0; }
.numbers { margin: 1rem 0; font-size: 1.22rem; line-height: 1.8; }
.numbers span { display: inline-block; margin-right: 1.3rem; }
.numbers strong { font-size: 1.6rem; font-weight: normal; }
.equation { margin: 1rem 0; text-align: center; font-size: 1.2rem; }
summary { cursor: pointer; text-decoration: underline; text-underline-offset: .2em; }
details[open] summary { margin-bottom: 1rem; }
table { width: 100%; border-collapse: collapse; font-size: .91rem; margin: 1rem 0; }
th, td { padding: .65rem .4rem; border-bottom: 1px solid #ddd; text-align: left; }
th { font-weight: normal; border-bottom-color: #999; }
td:last-child { overflow-wrap: anywhere; }
ul.questions { padding-left: 1.4rem; }
ul.questions li { margin: .75rem 0; }
.record-id { overflow-wrap: anywhere; }
footer { text-align: center; margin-top: 2rem; }
@media (max-width: 520px) {
  body { padding: 2rem 1.15rem 1.5rem; font-size: 16px; }
  nav ul { grid-template-columns: 1fr; gap: .55rem; }
  main { margin-top: 2rem; }
  th, td { padding: .55rem .2rem; }
  .numbers span { margin-right: .85rem; }
}
"""


def _geometry(report: dict) -> list[dict]:
    if not isinstance(report, dict) or report.get("all_reproductions_passed") is not True:
        raise ValueError("Only a successful reproduction report can be published")
    rows = report.get("geometry")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 5:
        raise ValueError("Missing or unsupported geometry results")
    for expected_size, row in enumerate(rows, start=3):
        if not isinstance(row, dict):
            raise ValueError("Invalid geometry row")
        n = row.get("polygon_vertices")
        vector = row.get("codimension_vector")
        if (type(n) is not int or n != expected_size or n not in REFERENCE_VECTORS
                or not isinstance(vector, list) or any(type(x) is not int for x in vector)
                or tuple(vector) != REFERENCE_VECTORS[n]
                or row.get("independent_recurrence") != vector
                or row.get("reference_matches") is not True
                or row.get("polytope_dimension") != n - 3):
            raise ValueError("Geometry figures are not a consistent verified reference reproduction")
    return rows


def render_homepage(report: dict, data_href: str = "run.json") -> str:
    rows = _geometry(report)
    if data_href not in ("run.json", "latest.json"):
        raise ValueError("Use a local report filename")
    latest = rows[-1]
    n, dimension = latest["polygon_vertices"], latest["polytope_dimension"]
    vector = latest["codimension_vector"]
    vertices = vector[-1]
    counts = f'<span><strong>{vertices:,}</strong> 頂点</span>'
    if dimension >= 1:
        counts += f'<span><strong>{vector[-2]:,}</strong> 辺</span>'
    if dimension >= 3:
        counts += f'<span><strong>{vector[-3]:,}</strong> 2次元の面</span>'
    if dimension == 3:
        meaning = (f'<p class="equation">{vertices} − {vector[-2]} + {vector[-3]} = 2</p>'
                   '<p>これは凸多面体の表面で成り立つオイラーの関係です。'
                   '複雑な入れ子を数えた結果にも、古典的な幾何学の秩序が現れます。</p>')
    else:
        meaning = ('<p>多角形の内側をどのように分け、どの順序で包むか。'
                   'その組合せが、多面体の面の構造として読み取れます。</p>')

    amplitude = next((r for r in report.get("amplitudes", [])
                      if r.get("polygon_vertices") == 5 and r.get("passed") is True), None)
    amplitude_section = ""
    if amplitude:
        amplitude_section = f"""
        <article>
          <h3>分け方が、式の分解につながる。</h3>
          <p>五角形を三角形に分ける方法は{int(amplitude['triangulations'])}通り。
          それぞれから散乱振幅の式を組み立て、すべてのチャネルで極の係数を調べました。
          小さな二つの多角形から作った式の積と、厳密に一致しています。</p>
          <p class="note">扱ったのは、平面的な三次スカラー理論の木レベル振幅です。
          変数は形式的に独立として計算しています。</p>
        </article>"""

    counterexample = next((r.get("counterexample") for r in report.get("hypotheses", [])
                           if r.get("status") == "counterexample"
                           and r.get("candidate", {}).get("target") == "vertices"
                           and r.get("counterexample")), None)
    hypothesis_section = ""
    if counterexample:
        sample = counterexample["polygon_vertices"]
        hypothesis_section = f"""
        <article>
          <h3>外れた予測から、次の問いへ。</h3>
          <p>小さな例に合う多項式で頂点数を予測すると、{escape(str(sample))}頂点の多角形では
          {escape(str(counterexample['predicted']))}。実際の計算結果は
          <strong>{escape(str(counterexample['actual']))}</strong>でした。
          この候補には、具体的な反例が見つかりました。</p>
          <p>いくつかの例が同じ規則に見えても、その先で成立するとは限りません。
          反例を記録することで、次に探す式の条件が明確になります。</p>
        </article>"""

    table_rows = "\n".join(
        f'<tr><th scope="row">{r["polygon_vertices"]}</th>'
        f'<td>{r["polytope_dimension"]}次元</td><td>'
        + ' · <wbr>'.join(str(x) for x in r["codimension_vector"]) + '</td></tr>'
        for r in rows)
    date = escape(str(report.get("created_at", ""))[:10])
    run_id = escape(str(report.get("run_id", "")))
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="数理物理の研究記録。多角形の入れ子、散乱振幅、仮説と反例を、検証した結果から読み解く。">
  <title>Mathematical Physics Lab — 研究の記録</title>
  <style>{STYLE}</style>
</head>
<body>
  <header>
    <h1>Mathematical Physics Lab</h1>
    <p>数学の構造を探索し、確かめ、記録する。</p>
    <p class="date">掲載実験：<time datetime="{date}">{date}</time></p>
  </header>
  <hr>
  <nav aria-label="目次">
    <ul>
      <li><a href="#findings">今回わかったこと</a></li>
      <li><a href="#questions">次に調べたい問い</a></li>
      <li><a href="#evidence">数字と検証の記録</a></li>
      <li><a href="#about">この研究所について</a></li>
    </ul>
  </nav>
  <main>
    <section id="findings" aria-labelledby="findings-title">
      <h2 id="findings-title">{POLYGON_NAMES[n]}の入れ子から、{vertices:,}の頂点。</h2>
      <p>{POLYGON_NAMES[n]}の内側を分割し、隣り合う多角形を大きな多角形で包む。
      この入れ子を「Matryoshka」と呼びます。その組合せを列挙すると、
      {dimension}次元のコスモヘドロンの面の構造が現れました。</p>
      <p class="numbers">{counts}</p>
      <p class="note">既知結果の再現。論文の参照値と、独立した漸化式による計算に一致しています。</p>
      {meaning}
      {amplitude_section}
      {hypothesis_section}
    </section>
    <hr>
    <section id="questions" aria-labelledby="questions-title">
      <h2 id="questions-title">次に調べたい問い</h2>
      <ul class="questions">
        <li>入れ子の列挙と漸化式が同じ数を返す理由を、小さな多角形から追えるだろうか。</li>
        <li>多面体の面の分解から、波動関数の式をどこまで再構成できるだろうか。</li>
        <li>反例を減らすために、候補生成へどんな数学的構造を与えるとよいだろうか。</li>
      </ul>
      <p>対称性やスケーリングから小さな式を再構成する実験も進めています。
      現段階で扱ったのは、平坦時空のスカラー木レベルモデルです。
      初期宇宙の相関関数への拡張は、次の段階になります。</p>
    </section>
    <hr>
    <section id="evidence" aria-labelledby="evidence-title">
      <h2 id="evidence-title">数字と検証の記録</h2>
      <details>
        <summary>面の個数と、計算の根拠を見る</summary>
        <table>
          <thead><tr><th scope="col">多角形の頂点</th><th scope="col">多面体</th>
          <th scope="col">面の個数</th></tr></thead>
          <tbody>{table_rows}</tbody>
        </table>
        <p class="note">面の個数は、全体から頂点まで余次元の順。空の面は含みません。</p>
        <p><a href="{PAPER}">Combinatorics of the Cosmohedron</a> の参照値と照合しています。</p>
        <p><a href="{data_href}">掲載実験の原データ</a> ·
        <a href="{REPOSITORY}/tree/main/research/results/reference">再現実験の記録</a></p>
        <p class="note record-id">実験番号：{run_id}</p>
        <p class="note">このページは一つの実験結果を掲載したものです。
        一般的な主張の形式証明と、結果の新規性の判断には別の検証が必要です。</p>
      </details>
    </section>
    <hr>
    <section id="about" aria-labelledby="about-title">
      <h2 id="about-title">この研究所について</h2>
      <p>幾何学の構造から物理の式へ。そのつながりを、再現可能な計算で少しずつ調べる場所です。
      AIの提案も、人の直感も、候補として扱い、計算や証明で確かめます。
      成立した関係と、外れた予想の両方を研究の記録として残します。</p>
      <p><a href="{REPOSITORY}">研究所のコードと実行方法</a></p>
    </section>
  </main>
  <hr>
  <footer>Mathematical Physics Lab · Gentaro<br>考えたことを、確かめられる形で。</footer>
</body>
</html>
"""


def export_site(report_path: Path, directory: Path) -> Path:
    """Select a verified snapshot for branch-based Pages publication."""
    descriptor = os.open(report_path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descriptor, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("Run report must be a regular file")
        raw = handle.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError("Run report exceeds 1 MiB")
    report = json.loads(raw.decode("utf-8"))
    html = render_homepage(report, data_href="latest.json")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "latest.json").write_bytes(raw)
    (directory / "index.html").write_text(html, encoding="utf-8")
    (directory / ".nojekyll").touch()
    return directory / "index.html"
