# 研究ホームページの公開記録

## 現在の公開先

**https://cosmolab.qd.je/**

独自ドメイン `cosmolab.qd.je` は取得済みです。配信元のSiteは
`https://cosmolab.gvtechno.chatgpt.site` でも同じ内容を表示します。
2026年10月12日にSitesで配信成功を確認しました。公開設定は `public` で、
URLを知っている人は誰でも閲覧できます。APIキー、有料API、データベース、
外部フォント、JavaScript、常駐サーバーは使いません。
掲載したHTMLとJSONは、このリポジトリの `docs/index.html` と `docs/latest.json`
に一致するファイルです。公開日時・配信識別子は [publication.json](publication.json) に記録します。

## 独自URLの状態

`cosmolab.qd.je` はDigitalPlatで取得済みです。Siteへのカスタムドメイン追加も
2026年10月12日に完了しています。DNS・所有権確認・HTTPS証明書の設定値は
[domain-setup.md](domain-setup.md) に記録しています。
DNS値は配信先の応答から取得し、GitHub PagesのIPを流用しません。

## 結果を更新する

```bash
python -m research run --max-vertices 6
# 実際に出力されたrun.jsonのパスを指定する
python -m research site --run research/results/run-日時-ID/run.json
git add docs/index.html docs/latest.json docs/.nojekyll
git commit -m "Update research homepage"
git push origin main
```

GitHub上のHTMLを更新した後、同じHTMLとJSONを既存Siteの `dist/` へコピーし、
Sitesのソース同期・バージョン保存・公開を実行します。Siteを新規作成せず、
publication.jsonに記録したproject_idを再利用します。
GitHubへのpushだけではSitesの公開内容は更新されません。

初期の参照結果は `python -m research site` で再生成できます。
閲覧時に計算やAI生成を実行しません。既知結果の再現、厳密な反例、次に調べたい問いを
実験の出力に基づいて掲載します。

クラウドの将来の継続・料金条件や無料ドメインの永久利用を保証するものではありません。
