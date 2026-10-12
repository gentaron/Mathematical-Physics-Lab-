# 文字だけの研究ホームページ

HTMLと小さなCSSだけで表示します。JavaScript、フレームワーク、データベース、
外部フォント、常駐サーバーは不要です。スマホでは目次が1列になり、本文の幅と文字が
自動調整されます。検証の詳細は標準のHTMLで開閉します。

## 最初の一回だけ設定

GitHubでこのリポジトリの [Settings → Pages](https://github.com/gentaron/Mathematical-Physics-Lab-/settings/pages)
を開き、次のように設定してください。

| 設定 | 値 |
| --- | --- |
| Source | Deploy from a branch |
| Branch | main |
| Folder | /docs |

**Save** を押すと、GitHub側の公開処理が始まります。設定後の公開先は
https://gentaron.github.io/Mathematical-Physics-Lab-/ です。
この文書は公開設定の完了を示すものではありません。

今回のGitHub接続にはPagesの管理設定を変更する操作がないため、この一回の設定は
GitHubの画面で行う必要があります。サイト本体と掲載データはリポジトリにあります。

公開リポジトリのGitHub PagesはGitHub Freeで利用できます。
[公式説明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)

## 結果を差し替える

新しい実験では、JSON・Markdownと一緒に `index.html` も自動生成されます。
このファイルを直接開けば、公開前でも結果を読めます。

```bash
python -m research run --max-vertices 6
```

出力された実行フォルダーの `run.json` を指定して、公開するスナップショットを選びます。

```bash
# 実際に出力されたrun.jsonのパスを指定
python -m research site --run research/results/run-日時-ID/run.json
git add docs/index.html docs/latest.json docs/.nojekyll
git commit -m "Update research homepage"
git push origin main
```

Pagesを一度設定した後は、mainへのpushが公開更新になります。
閲覧のたびに計算やAI生成を行いません。表示内容は、選択して公開した実験の結果です。
AIに解説文を生成させるAPIも使っていません。

初期ページは次のコマンドで再生成できます。

```bash
python -m research site
```

## 内容のルール

数字は実験の出力から取り、「何がわかったか」「なぜ面白いか」「次の問い」を
短く添えています。既知結果の再現と、反例が見つかった候補を明記します。
未検証の数値を確定した結果として公開しないよう、参照値との一致も確認します。
