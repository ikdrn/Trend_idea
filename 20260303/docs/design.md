# KEV-Watch — 設計ドキュメント

> 作成日: 2026-03-03

---

## 1. システム概要

**KEV-Watch** は、CISA（米国サイバーセキュリティ・インフラセキュリティ庁）が管理する **Known Exploited Vulnerabilities (KEV) カタログ** を取得・フィルタリングし、ターミナルに美しく表示するGoのCLIツールです。

### 対象ユーザー

- セキュリティエンジニア・PSIRT担当者
- インフラ管理者（パッチ優先順位決定のため）
- CTI（Cyber Threat Intelligence）アナリスト

---

## 2. アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                        KEV-Watch CLI                         │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────────┐  │
│  │  flag解析    │──▶│ データ取得   │──▶│ フィルタリング│  │
│  │  (main)      │   │ (fetchKEV /  │   │ (filterVulns) │  │
│  └──────────────┘   │  loadSample) │   └───────┬───────┘  │
│                      └──────────────┘           │           │
│                                                 ▼           │
│                      ┌──────────────────────────────────┐  │
│                      │    表示レイヤー (ANSI Terminal)   │  │
│                      │  printHeader / printSummary       │  │
│                      │  printVulnList / printVendorStats │  │
│                      │  printFooter                      │  │
│                      └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │
         ▼ (ネットワーク接続あり時)
┌─────────────────────────────────────────────────────────────┐
│  CISA KEV Catalog API (公式 JSON エンドポイント)             │
│  https://www.cisa.gov/sites/default/files/feeds/            │
│           known_exploited_vulnerabilities.json               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. データモデル

### KEVCatalog

```go
type KEVCatalog struct {
    Title           string          // カタログ名称
    CatalogVersion  string          // バージョン (YYYY.MM.DD形式)
    DateReleased    string          // リリース日時 (ISO 8601)
    Count           int             // 総CVE件数
    Vulnerabilities []Vulnerability // 脆弱性一覧
}
```

### Vulnerability

```go
type Vulnerability struct {
    CveID             string // CVE識別子 (CVE-YYYY-NNNNN)
    VendorProject     string // ベンダー/プロジェクト名
    Product           string // 製品名
    VulnerabilityName string // 脆弱性の通称
    DateAdded         string // KEVカタログへの追加日 (YYYY-MM-DD)
    ShortDescription  string // 短い説明文
    RequiredAction    string // 必要な対応アクション
    DueDate           string // 対応期限 (YYYY-MM-DD)
    Notes             string // 補足情報
}
```

---

## 4. データフロー

```
1. ユーザーがオプションを指定してコマンド実行
   go run src/main.go [-days N] [-vendor NAME] [-detail] [-offline]

2. fetchKEV() がCISA APIにHTTP GETリクエスト
   - User-Agent: kev-watch/1.0
   - Accept: application/json
   - Timeout: 30秒

3. ネットワーク失敗時はloadSampleData()にフォールバック
   - 内蔵JSONデータを使用（今日のニュースに基づくサンプル）

4. filterVulns() でフィルタリング
   - cutoff = time.Now() - N日前
   - DateAdded > cutoff のエントリのみ残す
   - vendor指定時は VendorProject に部分一致フィルタ

5. DateAdded降順でソート（最新が先頭）

6. ターミナルに表示
   - 🔴 赤: 追加から3日以内（最優先対応）
   - 🟡 黄: 追加から4-7日以内（早急対応）
   - ─ 白: 8日以上前（通常優先度）
```

---

## 5. CLIオプション仕様

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `-days N` | 30 | 直近N日以内のCVEを表示 |
| `-vendor NAME` | なし | ベンダー名で部分一致フィルタ（大文字小文字無視） |
| `-detail` | false | 詳細説明・対応アクション・期限を表示 |
| `-offline` | false | オフラインモード（内蔵サンプルデータを使用） |

---

## 6. 表示仕様

### カラーコーディング

| 色 | ANSI | 意味 |
|----|------|------|
| 赤 | `\033[31m` | 追加3日以内のCVE（最緊急）|
| 黄 | `\033[33m` | 追加4-7日のCVE（緊急）/ 脆弱性名称 |
| 緑（Bold）| `\033[32m` | ヘッダー / 完了メッセージ |
| シアン（Bold）| `\033[36m` | バナー / テーブルヘッダー |
| Dim | `\033[2m` | 補助情報・メタデータ |

### バーチャート（ベンダー統計）

- 最大25文字分（25件超は「+」で示す）
- 件数降順でTOP5を表示
- 同件数の場合はアルファベット順

---

## 7. エラーハンドリング

| エラーケース | 処理 |
|------------|------|
| ネットワーク接続失敗 | Warn表示後、サンプルデータにフォールバック |
| HTTPステータス非200 | エラーメッセージ + フォールバック |
| JSONデコード失敗 | エラーメッセージ + フォールバック |
| DateAdded パース失敗 | そのエントリをスキップ |
| サンプルデータパース失敗 | ERRORで終了（exit 1）|

---

## 8. 技術選定詳細

### なぜGoか

本日（2026-03-03）のトレンド:
- **Hacker News**: 「A case for Go as the best language for AI agents」がフロントページ掲載
- **GitHub Trending**: LocalAGI・Crush・LangChainGoなどGo製AIエージェントフレームワークが多数
- **Google Cloud Report**: GoベースのマイクロサービスはPython比でレイテンシ30%改善

Go言語がこのユースケースに最適な理由:
1. **標準ライブラリのみで完結** — `net/http`, `encoding/json`, `time`, `sort`, `strings` で全機能実装
2. **シングルバイナリ** — `go build` でクロスコンパイル可能な実行ファイルを生成
3. **高速起動** — CLIツールとしてほぼ即座に起動
4. **型安全** — JSONの構造体マッピングが安全

### なぜCISA KEVか

本日（2026-03-03）のセキュリティニュース:
- Android 3月2026パッチ: 過去最大129件のCVE（CVE-2026-21385ゼロデイ含む）
- Cisco CVSS 10.0: CVE-2026-20127が野外で積極的に悪用
- APT28: CVE-2026-21513 MSHTML 0-dayを悪用

CISAのKEVカタログ:
- **公式データソース** — 米国政府機関が管理
- **APIキー不要** — 完全無料のJSON API
- **実用的** — Federal Civilian Executive Branchに対してKEVへの対応が義務付け
- **リアルタイム更新** — 新たな悪用確認と同時に追加

---

## 9. 拡張アイデア（将来）

1. **NVD（National Vulnerability Database）との連携** — CVSS scoreを取得して表示
2. **Slack/Discord通知** — 新CVE追加時にWebhookで通知
3. **JSONエクスポート** — `-output json` で機械読み取り可能な出力
4. **定期実行モード** — `-watch 1h` で1時間ごとに差分チェック
5. **AIエージェント連携** — MCP (Model Context Protocol) サーバーとして実装し、AI agentがCVE情報を参照できるようにする（本日トレンド: Community Figma MCP Server）
