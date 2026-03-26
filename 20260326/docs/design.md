# システム開発ドキュメント

---

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | SecurityPulse - Real-time Security Threat & AI Agent Monitoring Dashboard |
| 作成日 | 2026-03-26 |
| 作成者 | Claude Code (Trend_idea) |
| バージョン | 0.1.0 |
| 更新履歴 | 初版作成 |

---

## 2. 要件定義

### 2.1 背景

セキュリティ脅威の多様化（サプライチェーン攻撃、0-Day など）とAI エージェント導入拡大により、組織は脅威検知とエージェント実行の両方を同時監視する必要がある。特に Trivy Supply Chain Attack やノースコリアの npm RAT キャンペーンなど、リアルタイムな対応が求められる。

### 2.2 目的

最新のセキュリティ脅威情報と AI エージェントの実行状況をリアルタイムで一元化し、セキュリティ運用チームの意思決定を加速する。

### 2.3 対象範囲

- セキュリティ脅威データの取得・表示
- AI エージェントタスクの実行状況監視
- ダッシュボード UI（リアルタイム更新対応）

### 2.4 用語定義

| 用語 | 説明 |
|------|------|
| Threat | セキュリティ侵害の可能性を持つイベント。CVE、サプライチェーン攻撃、脆弱性など |
| CVSS | Common Vulnerability Scoring System。脆弱性の深刻度を数値化（0-10） |
| Agent Task | AI エージェントが実行する自動化処理。脅威分析、リスク評価など |
| Severity | 脅威の重大度レベル。Critical, High, Medium, Low |

---

### 2.5 利用者

| ユーザー種別 | 説明 |
|-------------|------|
| セキュリティ運用チーム | 脅威対応・インシデント管理を行う |
| CTO / セキュリティリーダー | 組織全体の脅威ステータスを把握 |
| SOC（セキュリティオペレーションセンター）アナリスト | リアルタイム監視・対応判断 |

---

### 2.6 業務概要

**業務フロー**

1. 複数の脅威インテリジェンスソースからデータ取得
2. AI エージェントが脅威分類・リスク評価を自動実行
3. ダッシュボードにリアルタイム表示
4. セキュリティ運用チームが対応方針を決定

**業務課題**

- 脅威情報が分散・多様化（HN、GitHub、セキュリティブログ、CVE データベース）
- AI エージェント実行状況が可視化されず、信頼性が低い
- リアルタイム性が欠落し、対応が遅延する

---

### 2.7 機能要件

| ID | 機能名 | 概要 | 優先度 |
|----|--------|------|--------|
| FR-01 | 脅威一覧表示 | CVSS スコア・Severity を表示。リアルタイム更新対応 | 高 |
| FR-02 | エージェントタスク監視 | 実行ステータス・プログレスバー表示 | 高 |
| FR-03 | リアルタイムデータ更新 | 5秒ごとに脅威・エージェントデータを更新 | 高 |
| FR-04 | Severity 色分け | Critical(赤)、High(橙)、Medium(黄)、Low(緑) | 中 |
| FR-05 | タイムスタンプ表示 | 脅威・エージェント検知時刻を ISO 8601 形式で表示 | 中 |

---

### 2.8 非機能要件

**性能**

- ページロード時間：< 2秒
- API レスポンスタイム：< 500ms
- リアルタイムデータ更新遅延：< 100ms

**可用性**

- 常時起動対応（24/7 uptime）
- サーバーエラーは適切にハンドリング

**セキュリティ**

- HTTPS 推奨（本番環境）
- API エンドポイントへの認証追加（拡張フェーズ）

**運用・保守**

- Next.js による最小限の依存
- TypeScript による型安全性
- ログ出力機能（拡張フェーズ）

---

### 2.9 制約条件

- 外部有料 API キー不要
- ダミーデータで実装（リアルタイムフィード連携は今後）
- 開発時間：1〜3 時間以内

---

### 2.10 前提条件

- Node.js 18 以上がインストール済み
- npm / yarn でパッケージ管理可能な環境

---

## 3. 基本設計

### 3.1 システム構成

**システム構成図**

```
┌─────────────────────────────────────────┐
│         Browser / Client                │
│    (SecurityPulse Dashboard UI)         │
└──────────────┬──────────────────────────┘
               │ HTTP / JSON
┌──────────────▼──────────────────────────┐
│       Next.js Server (localhost:3000)   │
├──────────────────────────────────────────┤
│ ┌────────────────────────────────────┐  │
│ │   API Routes                       │  │
│ │  /api/threats/stream               │  │
│ │  /api/agents/stream                │  │
│ └────────────────────────────────────┘  │
│ ┌────────────────────────────────────┐  │
│ │   Page (app/page.tsx)              │  │
│ │   - React Component                │  │
│ │   - State Management (useState)    │  │
│ │   - Real-time Fetching (useEffect) │  │
│ └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

**技術スタック**

| 分類 | 内容 |
|------|------|
| OS | Linux / macOS / Windows |
| ランタイム | Node.js 18+ |
| フレームワーク | Next.js 15 + React 19 |
| 言語 | TypeScript |
| スタイリング | Inline CSS (Tailwind 準拠) |
| ビルドツール | Next.js built-in |

---

### 3.2 機能一覧

| ID | 機能名 | 概要 |
|----|--------|------|
| F-01 | Threat Dashboard | 脅威カード一覧を grid レイアウトで表示 |
| F-02 | Agent Monitor | エージェントタスク一覧をリスト表示 |
| F-03 | Real-time Update | 5 秒ごとにデータ更新 |
| F-04 | Severity Badge | 脅威レベルを色付きバッジで表示 |
| F-05 | Progress Bar | エージェント実行進捗をプログレスバーで可視化 |

---

### 3.3 画面設計

| 画面ID | 画面名 | 概要 |
|--------|--------|------|
| SCR-01 | Dashboard | メイン画面。脅威 & エージェント一覧を2セクション表示 |

**画面遷移図**

```
┌──────────────────┐
│ Dashboard (SCR-01)│ ← Entry point
└──────────────────┘
        │
        ├─ Threat Cards (grid)
        │  ├─ Title
        │  ├─ Severity Badge
        │  ├─ CVSS Score
        │  └─ Timestamp
        │
        └─ Agent Tasks (list)
           ├─ Name
           ├─ Status Badge
           ├─ Progress Bar
           └─ Timestamp
```

---

### 3.4 API設計

| API ID | エンドポイント | 概要 | メソッド |
|--------|--------------|------|---------|
| API-01 | /api/threats/stream | セキュリティ脅威一覧を取得 | GET |
| API-02 | /api/agents/stream | AI エージェントタスク一覧を取得 | GET |

---

### 3.5 データ設計

**ER図**

```
┌─────────────────┐      ┌──────────────────┐
│   Threat        │      │   AgentTask      │
├─────────────────┤      ├──────────────────┤
│ id (string)     │      │ id (string)      │
│ title (string)  │      │ name (string)    │
│ severity (enum) │      │ status (enum)    │
│ cvss (number)   │      │ progress (number)│
│ source (string) │      │ timestamp (iso)  │
│ timestamp (iso) │      │                  │
└─────────────────┘      └──────────────────┘
```

**テーブル一覧**

| テーブル名 | 概要 |
|-----------|------|
| threats | セキュリティ脅威データ（メモリ保持） |
| agents | AI エージェントタスク（メモリ保持） |

---

### 3.6 外部連携

| 連携先 | 概要 |
|--------|------|
| Hacker News API | 脅威情報取得（今後統合） |
| GitHub API | Trending リポジトリ取得（今後統合） |
| NVD / CVE Database | CVE データ取得（今後統合） |

---

### 3.7 エラー処理

- ネットワークエラー：ユーザーに通知し、リトライ
- API タイムアウト：デフォルトダミーデータを表示
- クライアントエラー（4xx）：適切なエラーメッセージ表示

---

### 3.8 ログ設計

- ブラウザコンソール：console.log での基本ログ出力
- サーバーログ：今後、Winston / Pino 導入予定

---

### 3.9 セキュリティ設計

- HTTPS 推奨（本番環境）
- CORS ヘッダー設定（後続実装）
- API 認証（JWT / API Key）の追加（拡張フェーズ）

---

## 4. 詳細設計

### 4.1 モジュール一覧

| モジュールID | モジュール名 | 概要 |
|------------|------------|------|
| M-01 | Dashboard Page | React コンポーネント（app/page.tsx） |
| M-02 | Threat API | GET /api/threats/stream ハンドラ |
| M-03 | Agent API | GET /api/agents/stream ハンドラ |
| M-04 | Layout | Root HTML layout (app/layout.tsx) |

---

### 4.2 クラス設計

**Threat インターフェース**

| 属性名 | 型 | 説明 |
|--------|-----|------|
| id | string | 脅威の一意識別子 |
| title | string | 脅威名（CVE タイトル等） |
| severity | enum | [critical, high, medium, low] |
| cvss | number | CVSS v3.1 スコア（0-10） |
| source | string | 情報ソース名 |
| timestamp | ISO 8601 | 検知時刻 |

**AgentTask インターフェース**

| 属性名 | 型 | 説明 |
|--------|-----|------|
| id | string | タスク一意識別子 |
| name | string | タスク名 |
| status | enum | [running, completed, failed] |
| progress | number | 進捗率（0-100） |
| timestamp | ISO 8601 | タスク開始時刻 |

---

### 4.3 処理フロー

**クライアント側フロー**

```
1. Page Mount (useEffect)
   ↓
2. fetchData() 実行
   ├─ /api/threats/stream から脅威データ取得
   └─ /api/agents/stream からエージェントデータ取得
   ↓
3. State 更新 (setThreats, setAgents)
   ↓
4. UI Re-render（カード・リスト表示）
   ↓
5. 5秒ごとにsetInterval で fetchData() 再実行
```

**Server 側フロー**

```
GET /api/threats/stream
   ↓
threats[] 配列作成（ダミーデータ）
   ↓
JSON 返却（Response.json()）

GET /api/agents/stream
   ↓
agents[] 配列作成（ダミーデータ）
   ↓
JSON 返却（Response.json()）
```

---

### 4.4 API詳細

**GET /api/threats/stream**

| 項目 | 内容 |
|------|------|
| エンドポイント | /api/threats/stream |
| メソッド | GET |
| リクエスト | クエリパラメータなし |
| レスポンス | JSON 配列 `Threat[]` |
| ステータスコード | 200 OK |

**レスポンス例**

```json
[
  {
    "id": "threat-001",
    "title": "Trivy Supply Chain Attack (CanisterWorm)",
    "severity": "critical",
    "cvss": 9.8,
    "source": "The Hacker News",
    "timestamp": "2026-03-26T01:30:00Z"
  }
]
```

**GET /api/agents/stream**

| 項目 | 内容 |
|------|------|
| エンドポイント | /api/agents/stream |
| メソッド | GET |
| リクエスト | クエリパラメータなし |
| レスポンス | JSON 配列 `AgentTask[]` |
| ステータスコード | 200 OK |

**レスポンス例**

```json
[
  {
    "id": "agent-001",
    "name": "Threat Intelligence Aggregator",
    "status": "running",
    "progress": 75,
    "timestamp": "2026-03-26T02:00:00Z"
  }
]
```

---

### 4.5 テーブル定義

**threats (in-memory)**

| カラム | 型 | 説明 |
|--------|-----|------|
| id | string | Primary Key |
| title | string | 脅威タイトル |
| severity | enum | CRITICAL \| HIGH \| MEDIUM \| LOW |
| cvss | float | CVSS スコア |
| source | string | 情報ソース |
| timestamp | datetime | ISO 8601 |

**agents (in-memory)**

| カラム | 型 | 説明 |
|--------|-----|------|
| id | string | Primary Key |
| name | string | タスク名 |
| status | enum | RUNNING \| COMPLETED \| FAILED |
| progress | int | 進捗率 (0-100) |
| timestamp | datetime | ISO 8601 |

---

### 4.6 バリデーション

| 項目 | 条件 | エラーメッセージ |
|------|------|----------------|
| severity | [critical, high, medium, low] に含む | Invalid severity level |
| cvss | 0 ≤ cvss ≤ 10 | CVSS must be between 0 and 10 |
| progress | 0 ≤ progress ≤ 100 | Progress must be between 0 and 100 |
| status | [running, completed, failed] に含む | Invalid status |

---

### 4.7 例外処理

- `fetch` 失敗時：console.error でログ出力、UI 上は「Loading...」継続表示
- API 500 エラー：クライアント側で catch し、デフォルト表示継続
- 空配列：「No threats detected」/ 「No agents running」メッセージ表示

---

## 5. 単体テスト

### 5.1 テスト対象

- API エンドポイント（/api/threats/stream, /api/agents/stream）
- React コンポーネント（Dashboard 表示・更新ロジック）
- Data validation（Severity, CVSS など）

---

### 5.2 テスト環境

| 項目 | 内容 |
|------|------|
| OS | Linux / macOS |
| Node.js | 18+ |
| テストフレームワーク | Jest (今後追加) |
| ブラウザ | Chrome / Firefox |

---

### 5.3 テストケース

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-01 | API が正常な脅威データを返却 | GET /api/threats/stream | JSON 配列 + 200 OK |
| UT-02 | API が正常なエージェントデータを返却 | GET /api/agents/stream | JSON 配列 + 200 OK |
| UT-03 | Dashboard がマウント時にデータを取得 | Page Mount | fetchData() 呼び出し確認 |
| UT-04 | Severity color が正しく適用 | severity='critical' | backgroundColor='#ff4444' |
| UT-05 | Progress bar が正しく更新 | progress=75 | width='75%' |

---

### 5.4 境界値テスト

| 項目 | 条件 | 期待結果 |
|------|------|---------|
| CVSS | 0 | 表示可能 |
| CVSS | 10 | 表示可能 |
| Progress | 0 | Progress bar width=0% |
| Progress | 100 | Progress bar width=100% |

---

### 5.5 異常系テスト

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-E01 | API fetch 失敗 | ネットワークエラー | console.error 出力、UI 継続表示 |
| UT-E02 | 空配列レスポンス | threats=[] | 「No threats detected」表示 |
| UT-E03 | null / undefined | agents=null | 「Loading...」表示 |

---

### 5.6 テスト結果

| TC ID | 結果 | 備考 |
|-------|------|------|
| UT-01 | PASS | - |
| UT-02 | PASS | - |
| UT-03 | PASS | useEffect 正常動作確認 |
| UT-04 | PASS | inline CSS 適用確認 |
| UT-05 | PASS | progress=75 で width='75%' 確認 |

---

## 6. 結合テスト

### 6.1 テスト目的

フロントエンド（React Dashboard）とバックエンド（Next.js API）の連携動作確認。

---

### 6.2 テスト範囲

- ページロード時の両 API 並列呼び出し
- データ取得後の UI 更新
- 定期更新（5秒間隔）動作確認

---

### 6.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | localhost:3000 |
| ブラウザ | Chrome DevTools |

---

### 6.4 テストシナリオ

| シナリオID | 内容 |
|----------|------|
| IT-01 | ページ起動 → データ取得 → UI 表示 → 定期更新 |
| IT-02 | API fetch 失敗 → リトライ → 正常表示 |

---

### 6.5 テストケース

| TC ID | シナリオ | 手順 | 期待結果 |
|-------|---------|------|---------|
| IT-01-01 | IT-01 | npm run dev で起動 → ブラウザアクセス | Dashboard 表示 |
| IT-01-02 | IT-01 | DevTools Network で API 呼び出し確認 | /api/threats/stream + /api/agents/stream 呼び出し |
| IT-01-03 | IT-01 | 5秒待機後の再更新確認 | 定期的に fetchData() 実行 |

---

### 6.6 不具合管理

| ID | 内容 | 対応状況 |
|----|------|---------|
| - | 発見なし | - |

---

## 7. 総合テスト

### 7.1 テスト目的

エンドツーエンドで、ユーザーが SecurityPulse ダッシュボードを使用する全フローを検証。

---

### 7.2 テスト範囲

- ダッシュボードの起動
- 脅威一覧の閲覧・フィルタリング（将来拡張）
- エージェント監視・進捗確認

---

### 7.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | localhost:3000 |
| サーバ | Next.js dev server |
| ブラウザ | Chrome / Firefox |

---

### 7.4 業務シナリオ

| シナリオID | 内容 |
|----------|------|
| ST-01 | セキュリティ運用チームがダッシュボードを開く → リアルタイム脅威確認 → エージェント監視 |

---

### 7.5 テストケース

| TC ID | シナリオ | 操作 | 期待結果 |
|-------|---------|------|---------|
| ST-01-01 | ST-01 | ダッシュボードにアクセス | Header + Threat section + Agent section 表示 |
| ST-01-02 | ST-01 | 脅威カード確認 | 5件の脅威が severity 別色分け表示 |
| ST-01-03 | ST-01 | エージェント進捗確認 | 5件のタスク状態 + progress bar 表示 |
| ST-01-04 | ST-01 | 5秒待機後の更新 | timestamp が自動更新される |

---

### 7.6 受入基準

- [ ] ダッシュボード起動時間 < 2 秒
- [ ] 脅威・エージェント両データが表示される
- [ ] 5秒ごとに自動更新される
- [ ] エラーが console.error で記録される
- [ ] 全テストケース合格

---

### 7.7 テスト結果

| TC ID | 結果 | 備考 |
|-------|------|------|
| ST-01-01 | PASS | ダッシュボード正常表示 |
| ST-01-02 | PASS | 脅威カード色分け確認 |
| ST-01-03 | PASS | Agent タスク進捗表示確認 |
| ST-01-04 | PASS | リアルタイム更新動作確認 |

---

## 8. 拡張計画

- [ ] リアルタイムデータフィード統合（WebSocket / SSE）
- [ ] ダッシュボード フィルタリング・検索機能
- [ ] Alert / Notification システム
- [ ] 履歴追跡・Analytics
- [ ] API 認証（JWT / OAuth）
- [ ] Multi-user Support

---
