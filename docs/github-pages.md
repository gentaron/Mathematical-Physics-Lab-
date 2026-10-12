# 文字だけの研究ホームページ

HTMLと小さなCSSだけで表示します。JavaScript、フレームワーク、データベース、
外部フォント、常駐サーバーは不要です。スマホでは目次が1列になり、本文の幅と文字が
自動調整されます。検証の詳細は標準のHTMLで開閉します。

## 公開先

**https://cosmolab.qd.je/**

DigitalPlatの無料ドメイン枠とGitHub Pagesを組み合わせます。
常駐サーバー、有料プラン、APIキーは不要です。ドメインと公開サービスの
将来の継続・無料条件まで保証するものではありません。

## 公開設定

GitHubでこのリポジトリの [Settings → Pages](https://github.com/gentaron/Mathematical-Physics-Lab-/settings/pages)
を開き、次の設定を使います。

| 設定 | 値 |
| --- | --- |
| Source | Deploy from a branch |
| Branch | main |
| Folder | /docs |
| Custom domain | cosmolab.qd.je |

`docs/CNAME` にも `cosmolab.qd.je` を保存します。
DNS設定と証明書の発行が完了したら、**Enforce HTTPS** を有効にします。

DigitalPlat DNSの `cosmolab.qd.je` ゾーンには以下を設定します。
名前 `@` はゾーンのルートを表します。ワイルドカードは設定しません。

| 種類 | 名前 | 値 |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

GitHubにカスタムドメインを設定してからDNSを向けます。
ドメイン所有権確認が求められた場合は、GitHubが表示するTXTレコードも追加します。
DNSの反映やHTTPS証明書の発行には最大24時間かかる場合があります。
この文書だけでは、実際の登録・配信・証明書発行の完了を示しません。

[GitHubのカスタムドメイン設定](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)

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
