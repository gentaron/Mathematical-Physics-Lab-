# cosmolab.qd.je の接続設定

2026年10月12日に、公開済みSiteへ `cosmolab.qd.je` を追加しました。
これは配信サービス側の接続先設定です。DigitalPlatでの名前の取得は未完了で、
DNSゾーンやDNSレコードはまだ作成していません。

| 設定 | 状態 |
| --- | --- |
| Siteのカスタムドメイン登録 | 完了 |
| DigitalPlatのドメイン取得 | GitHub本人確認待ち |
| DNS設定 | 未設定 |
| DNS所有権確認 | pending |
| HTTPS証明書 | pending_validation |
| 指定URLの公開確認 | 未完了 |

## 発行済みのDNS設定

DigitalPlatでドメインを取得し、DigitalPlat DNSにゾーンが作成された後に適用します。
以下のルートゾーン用AレコードはSitesの応答から取得した値です。
`@` は `cosmolab.qd.je` を表します。

| 種類 | 名前 | 値 |
| --- | --- | --- |
| A | @ | 162.159.143.30 |
| A | @ | 172.66.3.26 |
| TXT | _openai-site-verification | Sitesが発行した所有権確認値 |
| TXT | _cf-custom-hostname | Sitesが発行した所有権確認値 |

検証用TXTの実際の値は、同じSiteのカスタムドメイン管理画面・応答から取得します。
レコード名の末尾にはDNS管理画面側で `cosmolab.qd.je` が追加されるため、
二重に付けないよう設定します。

接続先CNAMEは `custom-domains.chatgpt.site.` です。ルートゾーンで通常のCNAMEを
SOA・NSと併用せず、ここでは上記のAレコードを使用します。
DNS反映後に同じカスタムドメインの状態を更新し、DNS確認・SSLが有効になったことと
`https://cosmolab.qd.je/` に研究ページが表示されることを確認します。

GitHubの案内を「指定URLで公開済み」に変更するのは、その確認が済んだ後です。
