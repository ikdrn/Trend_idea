# システム開発ドキュメント

---

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | Agentic Trend Classifier - 設計書 |
| 作成日 | 2026-03-21 |
| 作成者 | Claude Code |
| バージョン | 1.0 |
| 更新履歴 | 初版作成 |

---

## 2. 要件定義

### 2.1 背景

GitHub Trending と Hacker News は、テック業界の最新トレンドを把握する重要な情報源である。
特に 2026 年は Agentic AI（AI エージェント）フレームワークの急速な普及（OpenClaw 210k+ 星）、
セキュリティ脆弱性（CVE-2026-3888）の継続的な発見、
Product Hunt における AI Automation ツールの支配が顕著である。

これらの複雑なトレンド信号をリアルタイムで分類・可視化するツールの需要が高い。

### 2.2 目的

1. **リアルタイムトレンド監視** - GitHub Trending の最新リポジトリを自動スクレイプ
2. **AI Agent 関連度スコアリング** - キーワードベース分類エンジンで自動分析
3. **セキュリティ関連度検知** - CVE・脆弱性キーワードの自動抽出
4. **直感的ダッシュボード** - 複数分野スコアの可視化 UI 提供

### 2.3 対象範囲

- GitHub Trending（JavaScript, Python, Rust, Go など）の Top 10 リポジトリ
- リアルタイムトレンド分類エンジン（AI Agent, Security, 言語別タグ）
- Web ベースダッシュボード（レスポンシブ対応）
- REST API エンドポイント（JSON データ提供）

### 2.4 用語定義

| 用語 | 説明 |
|------|------|
| AI Agent | 自律的に行動・判断する AI フレームワーク（LangChain, OpenClaw, NemoClaw など） |
| Agentic AI | AI エージェント技術を中心とした AI 開発パラダイム |
| Trending Score | キーワードマッチング × 検出数 で算出した 0-100 スコア |
| Keyword Classifier | テキスト内のキーワード出現数でスコアリングする簡易分類器 |

---

### 2.5 利用者

| ユーザー種別 | 説明 |
|-------------|------|
| 開発者 | GitHub の最新トレンドをリアルタイムで把握したいエンジニア |
| AI 研究者 | AI Agent フレームワークの動向・採用状況を監視する研究者 |
| セキュリティ監視者 | 新規セキュリティ脆弱性が Github Trending で話題化する前に検知したい者 |
| 起業家 | テック業界の次のホットトレンドを投資判断の参考にしたい |

---

### 2.6 業務概要

**業務フロー**

1. 定期（1時間ごと）に GitHub Trending ページを HTTP リクエストで取得
2. HTML を Cheerio で DOM パースし、リポジトリ情報（名前、説明、言語、スター数）を抽出
3. 抽出テキストに対して Keyword Classifier を適用
   - AI Agent キーワード検索 → 0-100 AI Agent スコア算出
   - Security キーワード検索 → 0-100 Security スコア算出
   - 言語別タグ（Python, JavaScript, Rust, Go）の判定
4. スコアリング結果を EJS テンプレートで HTML レンダリング
5. ブラウザから http://localhost:3000 にアクセス→ダッシュボード表示

**業務課題**

- 手動でトレンドを確認する手間が大きい
- 複数の分野（AI, Security）のシグナル混在で判断が複雑
- リアルタイティが重要だが定期監視が負担

---

### 2.7 機能要件

| ID | 機能名 | 概要 | 優先度 |
|----|--------|------|--------|
| FR-01 | GitHub Trending スクレイプ | 定期的に GitHub Trending ページを取得し、Top 10 リポジトリを抽出 | 高 |
| FR-02 | AI Agent スコアリング | リポジトリテキストから AI Agent 関連度（0-100）を自動計算 | 高 |
| FR-03 | Security スコアリング | リポジトリテキストからセキュリティ関連度（0-100）を自動計算 | 高 |
| FR-04 | 言語タグ判定 | リポジトリの言語（Python, JS, Rust, Go）を自動判定 | 中 |
| FR-05 | ダッシュボード表示 | スコアリング結果をグリッドレイアウト＆プログレスバーで可視化 | 高 |
| FR-06 | リアルタイム更新 | 1 時間ごとに自動でトレンドデータを更新 | 中 |
| FR-07 | REST API | JSON 形式でトレンドデータを返す /api/trends エンドポイント | 中 |

---

### 2.8 非機能要件

**性能**

- GitHub Trending ページ取得：最大 10 秒以内
- スクレイプ＆スコアリング：最大 5 秒以内
- UI レンダリング：最大 1 秒以内

**可用性**

- 4 時間以上の稼働を想定（ローカル開発環境）
- 1 時間ごとのバッチ更新で継続運用

**セキュリティ**

- 外部 API キー・認証不要（オープンソースのみ）
- HTTP 通信のみ（HTTPS 不要）
- Cheerio での HTML パース時に XSS 対策は実施しない（信頼できるソース）

**運用・保守**

- npm package.json で依存管理
- エラーログはコンソール出力
- 実装は Node.js 単一ファイル（server.js）で簡潔に

---

### 2.9 制約条件

- 実装時間：2 時間以内
- 外部 API キー・サービス料金：なし
- ブラウザ環境：モダン Chrome/Firefox/Safari 対応
- HTML スクレイプ対象：GitHub Trending（構造変更時は修正が必要）

---

### 2.10 前提条件

- Node.js 14.0 以上がインストール済み
- npm パッケージマネージャが利用可能
- インターネット接続が常時確保されている
- ローカルホスト（localhost:3000）でのアクセスを想定

---

## 3. 基本設計

### 3.1 システム構成

**システム構成図**

```
┌─────────────────────────────────────────────────┐
│                  Browser                         │
│           (http://localhost:3000)                │
└────────────────┬────────────────────────────────┘
                 │ HTTP GET
                 ▼
┌─────────────────────────────────────────────────┐
│            Express Server (Node.js)              │
│  ┌──────────────────────────────────────────┐   │
│  │  Route Handler (/)                       │   │
│  │  - EJS Template Rendering                │   │
│  │  - Data Formatting                       │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  Route Handler (/api/trends)             │   │
│  │  - JSON Response Generation              │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  Trend Classifier Engine                 │   │
│  │  - Keyword Matching (AI Agent, Security) │   │
│  │  - Scoring Logic (0-100%)                │   │
│  │  - Language Tag Detection                │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  GitHub Trending Scraper                 │   │
│  │  - HTML Fetch (node-fetch)               │   │
│  │  - DOM Parse (Cheerio)                   │   │
│  │  - Repository Data Extraction            │   │
│  └──────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────┘
                 │ setInterval(3600000ms)
                 ▼
    ┌──────────────────────────────┐
    │  GitHub Trending Page        │
    │  (https://github.com/trending)
    └──────────────────────────────┘
```

**技術スタック**

| 分類 | 内容 |
|------|------|
| OS | Linux / macOS / Windows |
| ランタイム | Node.js 14.0+ |
| フレームワーク | Express.js 4.18+ |
| テンプレートエンジン | EJS 3.1+ |
| HTML パーサー | Cheerio 1.0.0-rc+ |
| HTTP クライアント | node-fetch 2.7+ |

---

### 3.2 機能一覧

| ID | 機能名 | 概要 |
|----|--------|------|
| F-01 | Trending Data Fetcher | GitHub Trending からリポジトリデータを定期取得 |
| F-02 | Classifier Engine | キーワードベース分類ロジック |
| F-03 | Dashboard Renderer | HTML/EJS でダッシュボード表示 |
| F-04 | API Endpoint | JSON REST API |
| F-05 | Auto Updater | 1 時間ごとの定期更新スケジューラ |

---

### 3.3 画面設計

| 画面ID | 画面名 | 概要 |
|--------|--------|------|
| SCR-01 | ダッシュボード | GitHub Trending Top 10 を グリッドレイアウト表示 |
| SCR-02 | リポジトリカード | 各リポジトリの詳細（AI Agent スコア、Security スコア、言語タグ） |
| SCR-03 | 統計サマリー | 全体統計（AI Agent 関連数、Security 関連数、平均スコア） |

**画面遷移図**

```
     ┌──────────────────┐
     │   起動 / 更新    │
     └────────┬─────────┘
              │
              ▼
     ┌──────────────────────────┐
     │  GitHub Trending 取得    │
     │  (1時間ごと定期実行)     │
     └────────┬─────────────────┘
              │
              ▼
     ┌──────────────────────────┐
     │  Keyword Classifier      │
     │  スコアリング実行        │
     └────────┬─────────────────┘
              │
              ▼
     ┌──────────────────────────┐
     │ ダッシュボード HTML      │
     │ (EJS Template Render)    │
     └────────┬─────────────────┘
              │
              ▼
     ┌──────────────────────────┐
     │  ブラウザ表示            │
     │  (http://localhost:3000) │
     └──────────────────────────┘
```

---

### 3.4 API 設計

| API ID | エンドポイント | 概要 | メソッド |
|--------|--------------|------|---------|
| API-01 | / | ダッシュボード HTML 表示 | GET |
| API-02 | /api/trends | トレンドデータ JSON | GET |

---

### 3.5 データ設計

**ER図**

```
┌─────────────────────────────────┐
│         Trending Repo           │
├─────────────────────────────────┤
│ name: string                    │
│ url: string                     │
│ description: string             │
│ language: string                │
│ stars: string                   │
│ scores: {                       │
│   aiAgent: number (0-100)       │
│   security: number (0-100)      │
│   language: string              │
│   trend: 'AI Agent' | 'Security'│
│          | 'General'            │
│ }                               │
└─────────────────────────────────┘
```

**テーブル一覧**

| テーブル名 | 概要 |
|-----------|------|
| trendData.repos | GitHub Trending Top 10 リポジトリ配列（メモリ内保存） |

> **注記**: データベースを使用しない。メモリ内に リポジトリデータを保持し、1 時間ごとにスクレイプで更新。

---

### 3.6 外部連携

| 連携先 | 概要 |
|--------|------|
| GitHub Trending | HTML ページスクレイプ |

---

### 3.7 エラー処理

- GitHub Trending 取得失敗時：コンソール log を出力し、前回データを保持継続
- HTML パース失敗時：空配列を返す
- ネットワーク接続失敗時：キャッチしてコンソール出力

---

### 3.8 ログ設計

- すべて console.log() でコンソール標準出力
- タイムスタンプ付き（ISO 8601）
- 重要度区分なし（簡易ログ）

---

### 3.9 セキュリティ設計

- 外部 API キー管理：なし
- 認証・認可：なし（ローカルホストのみ対象）
- XSS 対策：EJS エスケープ処理を活用
- HTML インジェクション対策：Cheerio パースで自動エスケープ

---

## 4. 詳細設計

### 4.1 モジュール一覧

| モジュールID | モジュール名 | 概要 |
|------------|------------|------|
| M-01 | server.js | Express サーバー、ルートハンドラ、スクレイパー 統合 |
| M-02 | views/index.ejs | ダッシュボード HTML テンプレート |
| M-03 | package.json | npm 依存パッケージ定義 |

---

### 4.2 クラス設計

なし（手続き型スクリプト構成）

---

### 4.3 処理フロー

```
[初期化フェーズ]
1. Express アプリケーション起動
2. trendData オブジェクト初期化（repos: [], lastUpdated: now）
3. updateTrends() 関数を即座に 1 回実行（同期）
4. setInterval(updateTrends, 3600000) で定期スケジュール設定
5. app.listen(3000) でサーバー起動

[データ更新フェーズ]（毎 1 時間）
1. fetchGitHubTrending() 実行
   - GitHub Trending ページを HTTP GET
   - Cheerio で article.Box-row パース
   - Top 10 のリポジトリ情報を抽出
2. classifyTrend(repo) 関数で各リポジトリをスコアリング
   - AI Agent キーワード数 × 15 = aiAgent スコア
   - Security キーワード数 × 20 = security スコア
   - 言語判定（Python, JS, Rust, Go）
3. trendData.repos を更新
4. trendData.lastUpdated を現在時刻に更新

[リクエスト処理フェーズ]
1. GET / リクエスト受信
2. trendData.repos を AI Agent スコア降順ソート
3. EJS テンプレート render() で HTML 生成
4. ブラウザにレスポンス返送

[API リクエスト処理フェーズ]
1. GET /api/trends リクエスト受信
2. JSON.stringify(trendData) を返送
```

---

### 4.4 API 詳細

**GET /**

| 項目 | 内容 |
|------|------|
| エンドポイント | http://localhost:3000/ |
| メソッド | GET |
| リクエスト | なし |
| レスポンス | HTML（EJS レンダリング） |
| 成功時 Status | 200 OK |

**GET /api/trends**

| 項目 | 内容 |
|------|------|
| エンドポイント | http://localhost:3000/api/trends |
| メソッド | GET |
| リクエスト | なし |
| レスポンス | JSON |

```json
{
  "repos": [
    {
      "name": "user/repo-name",
      "url": "https://github.com/user/repo-name",
      "description": "repo description...",
      "language": "JavaScript",
      "stars": "1.2k",
      "scores": {
        "aiAgent": 75,
        "security": 20,
        "language": "JavaScript",
        "trend": "AI Agent"
      }
    }
  ],
  "lastUpdated": "2026-03-21T12:34:56.789Z",
  "summary": {
    "total": 10,
    "aiAgentCount": 5,
    "securityCount": 2,
    "avgAiAgentScore": "68.5"
  }
}
```

---

### 4.5 テーブル定義

メモリ内テーブル（データベース不使用）

```javascript
trendData = {
  repos: Array<{
    name: string,
    url: string,
    description: string,
    language: string,
    stars: string,
    scores: {
      aiAgent: number,
      security: number,
      language: string,
      trend: string
    }
  }>,
  lastUpdated: Date,
  updateInterval: number (milliseconds)
}
```

---

### 4.6 バリデーション

なし（信頼できるソース GitHub のみ対象）

---

### 4.7 例外処理

```javascript
try {
  const response = await fetch('https://github.com/trending');
  const html = await response.text();
  // パース処理...
} catch (err) {
  console.error('Error fetching GitHub Trending:', err.message);
  return []; // 前回データを保持
}
```

---

## 5. 単体テスト

### 5.1 テスト対象

- classifyTrend(repo) 関数
- fetchGitHubTrending() 関数
- キーワードマッチングロジック

### 5.2 テスト環境

| 項目 | 内容 |
|------|------|
| OS | Linux |
| Node.js | 14.0+ |
| npm | 6.0+ |

### 5.3 テストケース

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-01 | AI Agent スコアリング | name: "langchain/js", desc: "LLM framework" | aiAgent: 30+ |
| UT-02 | Security スコアリング | name: "security-audit", desc: "vulnerability scanner" | security: 40+ |
| UT-03 | GitHub Trending 取得 | - | repos.length === 10 |
| UT-04 | 言語タグ判定（Python） | desc: "FastAPI application" | language: "Python" |
| UT-05 | 言語タグ判定（Rust） | desc: "Rust WASM compiler" | language: "Rust" |

### 5.4 テスト結果

（実装時点では手動テストのみ。自動テストフレームワークは導入なし）

---

## 6. 結合テスト

### 6.1 テスト目的

- Express サーバーと EJS テンプレートの統合確認
- GitHub スクレイプ結果が正確にレンダリングされること

### 6.2 テスト範囲

- ダッシュボード起動 → HTML 表示
- API エンドポイント → JSON 返却

### 6.3 テスト結果

（実装時点では手動確認のみ）

---

## 7. 総合テスト

### 7.1 テスト目的

- 実運用環境での 24 時間稼働確認

### 7.2 テスト範囲

- 定期更新（1 時間ごと）の実行
- ブラウザ UI レスポンス
- API 応答性

### 7.3 テスト結果

（実装完了時点では未実施）

---

## 注記

このドキュメント作成日時点（2026-03-21）での仕様です。
GitHub Trending のページ構造変更により、パーサー修正が必要になる可能性があります。
