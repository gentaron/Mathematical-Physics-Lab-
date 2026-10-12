# Mathematical Physics Lab

**無料のOSSで、数理物理の構造を探索し、計算で候補を検証する研究ラボ。**

Genesis Vaultから独立した研究エンジンです。研究日誌をJSON/Markdownとして
出力します。記事公開や既存の12エージェントへの変更は行いません。

結果を読むための、白地・明朝体・リンク中心のシンプルな
指定した公開URLは **`cosmolab.qd.je`** です。
HTMLと小さなCSSだけで動き、スマホにも対応します。
サイト側へのカスタムドメイン登録と接続先の発行は完了しています。
DigitalPlatでのドメイン取得は、必須のGitHub本人確認待ちです。
ドメイン取得・DNS設定・指定URLでのHTTPS公開はまだ完了していません。
[ローカルで読むページ](docs/index.html) と [公開・更新の記録](docs/publication.md) もあります。

最初の対象は **Cosmohedron Explorer**。AIの文章を正しさの根拠にせず、
論文の既知結果の再現 → 候補生成 → 厳密な反例探索 → 証拠付き記録を実行します。

## すぐ動かす

Python 3.12以上が必要です。必要な実行ライブラリはSymPyだけです。

```bash
git clone https://github.com/gentaron/Mathematical-Physics-Lab-.git
cd Mathematical-Physics-Lab-
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
python -m research run --max-vertices 6
```

Windowsの仮想環境有効化は `.venv\Scripts\Activate.ps1`。

実行ごとに `research/results/run-日時-ID/` が作られます。
`journal.md` が研究日誌、`run.json` が機械可読の結果、`ledger/` が個別の実験記録、
`faces-N.json` が空面を含む面のHasse図です。過去の実行を上書きしません。
`index.html` を直接開くと、数字・その意味・次の問いをまとめたページとして読めます。

```bash
# 既存の参照結果をトップページへ出力（再計算やサーバー起動は不要）
python -m research site
```

```bash
python -m research.positive_geometry.five_point
python -m research faces --vertices 5
python -m research doctor
python -m research verify --candidate research/conjectures/example.json --ledger research/results/manual-ledger
```

`verify` の終了コードは一致=0、反例=1、入力エラー=2。
反例を見つけること自体は研究成果であり、`run` は再現検証が通れば正常終了します。

## 実装済みの研究

| 実験 | 計算と検証 | 範囲 |
| --- | --- | --- |
| Cosmohedron Explorer | 非交差分割・Matryoshkaの列挙、面の包含関係、独立した漸化式との照合 | 多角形3〜7頂点。全Hasse図は6頂点まで |
| 平面的な三次スカラー振幅 | 三角形分割から有理式を生成、全チャネルの留数と因子化を検証 | 3〜7点、独立した形式的運動学変数 |
| 仮説探索 | 個数列から多項式候補を生成し、学習に使わなかったサイズで厳密に反例を探す | 制限された有理係数多項式。一般式の証明・新規性判定はしない |
| Bootstrap入門 | 固定した分母のもとでスケーリング・交換対称性・極の係数から2-site式を再構成 | 平坦時空のスカラー木レベル種。2〜4-site鎖の波動関数係数も生成 |
| 研究台帳 | 再現・反例・予想・記号検証・判定不能を分離、入力と実装のハッシュを保存 | JSON個別ファイル。形式証明扱いへの自動昇格なし |
| ローカルAI | OllamaのJSON提案を同じ制限スキーマで受け取り、計算に渡す | 任意。既に導入済みのローカルモデルだけ |
| Lean証明プロジェクト | 5点式の代数的な項のまとめ直しと極係数の恒等式 | 別の手動ワークフロー。Python実験から証明済みとは判定しない |

参照論文の値と一致するチェックイン済み実行は
[research/results/reference/journal.md](research/results/reference/journal.md) を参照。

| 多角形の頂点数 | 多面体の次元 | 面の個数：余次元0から順に |
| --- | --- | --- |
| 3 | 0 | 1 |
| 4 | 1 | 1, 2 |
| 5 | 2 | 1, 10, 10 |
| 6 | 3 | 1, 44, 114, 72 |
| 7 | 4 | 1, 196, 952, 1400, 644 |

この表は **既知結果の再現**です。新しい定理の発見ではありません。
幾何学的な座標実現や正準微分形式、アンプリチューヘドロン全体の計算は実装範囲に含みません。
Bootstrap種はde Sitter相関関数やKinematic-Flowの再現ではありません。

## 無料のままGitHubで実行

公開リポジトリの **Actions → Mathematical Physics Research → Run workflow**。
5・6・7頂点から選択できます。結果は実行ログとジョブのSummaryに表示します。
push/PRでも同じ再現テストを実行します。定期実行はありません。

- 標準の `ubuntu-latest` のみ。privateに変更された場合はジョブをスキップ。
- APIキー不要。有料API・大型ランナー・Actionsの成果物保存・Actionsキャッシュを使いません。
- checkout時の認証情報を残さず、リポジトリへの書き込み権限を付けません。
- ActionsではローカルLLMを動かしません。モデルなしで再現と候補検証が完了します。
- JSONを長期保存する場合はローカルで実行して、選んだ結果を自分でコミットしてください。

[GitHubの料金説明](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
によると、公開リポジトリの標準ホストランナーは無料です。
クラウドサービスの将来の料金変更までは保証しません。
ローカル実行はサービス契約を必要としません（機材・電気・通信は別）。

## ローカルAIを接続する場合

Ollama自体の導入とモデルの取得は任意です。このラボはモデルを自動ダウンロードしません。
クラウド機能を無効化してサーバーを起動し、`ollama list` のローカルモデル名を指定します。

```bash
OLLAMA_NO_CLOUD=1 ollama serve
# 別ターミナルで、YOUR_LOCAL_MODELを既に取得済みのモデル名に置換
python -m research run --max-vertices 6 --ollama-model YOUR_LOCAL_MODEL
```

接続先はloopbackだけ、クラウドモデル・リダイレクト・HTTPプロキシを拒否します。
既定の生成タイムアウトは45秒です。モデル起動が遅い、応答が不正、候補が巨大な場合は
判定不能として記録し、通常の候補検証は継続します。有料モデルへ切り替えません。
5.8GBのPCではモデルの容量と速度が制約になるため、まずモデルなしで再現実験を使えます。
**標準の候補生成は多項式補間であり、ニューラルAIではありません。**

## 論文・数学・専門ソフト

- [数学的な規約と検証範囲](docs/mathematics.md)
- [無料ツールと任意拡張](docs/free-tools.md)
- [論文・公式実装の出典一覧](research/papers/sources.json)
- [Leanプロジェクトと検証手順](research/proofs/README.md)
- [設計](docs/superpowers/specs/2026-10-12-math-lab-design.md)
- [実装計画](docs/superpowers/plans/2026-10-12-math-lab.md)

実装コードはMITライセンス。論文の本文や外部研究コードは同梱していません。
