# システム開発ドキュメント

---

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | VulnWatch - AI Security Vulnerability Dashboard |
| 作成日 | 2026-03-25 |
| 作成者 | Claude Code |
| バージョン | 1.0.0 |
| 更新履歴 | 初版作成 |

---

## 2. 要件定義

### 2.1 背景

Microsoft と Google がそれぞれ複数の zero-day 脆弱性を公開し、セキュリティ担当者向けの脆弱性情報の自動分析と優先度付けのニーズが高まっている。同時に Claude Computer Use などの AI エージェント技術が注目を集めており、セキュリティ分野での AI 活用が推進されている。

### 2.2 目的

AI エージェント（Claude API）を活用して、最新の CVE/Patch 情報をリアルタイムで取得・分析し、セキュリティ担当者が意思決定しやすいダッシュボード UI を提供する。AI の思考プロセス（メモリ・呼び出し履歴）を可視化することで、AI-Human のトラスト醸成を目指す。

### 2.3 対象範囲

- CVE データベース（最新の Patch Tuesday データを含む）への接続と取得
- Claude API エージェント ループによる脆弱性自動分析
- 分析結果とメモリ情報の Web UI で可視化
- ローカル開発環境での実行（外部API キー設定による拡張可能）

### 2.4 用語定義

| 用語 | 説明 |
|------|------|
| CVE | Common Vulnerabilities and Exposures。脆弱性識別子 |
| CVSS | Common Vulnerability Scoring System。脆弱性の重要度スコア |
| Zero-Day | 未公開のセキュリティ脆弱性 |
| AI Agent | 自律的に行動・思考する AI モデル（Claude API） |
| Patch Tuesday | Microsoft の定期脆弱性修正月次リリース（毎月第2火曜日） |

---

### 2.5 利用者

| ユーザー種別 | 説明 |
|-------------|------|
| セキュリティエンジニア | CVE 情報を確認し、組織の対策優先度を決定 |
| インフラチーム | パッチの適用計画立案と実行 |
| マネジメント | リスク評価資料の作成用途 |

---

### 2.6 業務概要

**業務フロー**

1. ユーザーがダッシュボードを開く → CVE 一覧が自動ロード
2. 「Analyze All CVEs」ボタンをクリック
3. バックエンド（Node.js/Hono）が Claude API エージェント ループを実行
4. 各 CVE に対して AI が影響範囲・対策優先度を自動分析
5. UI にリアルタイムで分析結果・AI メモリ（思考プロセス）が表示
6. ユーザーが分析結果を参考に、対策計画を策定

**業務課題**

- CVE 数が多すぎて人間の判断では対応できない
- セキュリティ関連情報は常に最新化が必要
- AI 分析を信頼するには、AI の思考プロセスの可視化が重要

---

### 2.7 機能要件

| ID | 機能名 | 概要 | 優先度 |
|----|--------|------|--------|
| FR-01 | CVE データ取得 | 最新の CVE 情報をメモリに保持し、API で取得可能にする | 高 |
| FR-02 | AI エージェント分析 | Claude API を使用して各 CVE の影響度・対策優先度を自動算出 | 高 |
| FR-03 | メモリ可視化 | AI エージェントの思考プロセス・呼び出し履歴を UI で表示 | 中 |
| FR-04 | リアルタイムUI更新 | 分析完了時にダッシュボードが自動更新される | 中 |
| FR-05 | モバイル対応 | レスポンシブデザインで PC / タブレット / スマートフォンに対応 | 低 |

---

### 2.8 非機能要件

**性能**

- CVE 分析: 平均 2-3 秒/件（Claude API レイテンシ依存）
- UI レンダリング: 100ms 以内（Vanilla JS）
- 同時接続: 10 ユーザー以上想定

**可用性**

- 平日 9:00-18:00 の可用性 99% 以上を目指す
- API キーなし時は demo mode で動作

**セキュリティ**

- API キーは環境変数から読み込み（.env, process.env）
- HTTPS 推奨（本開発ではローカルのため HTTP）
- CORS 設定は不要（同一オリジン）

**運用・保守**

- ログ出力: console で充分
- 定期メンテナンス: なし（ステートレス設計）
- 拡張性: API エンドポイント追加で対応可能

---

### 2.9 制約条件

- Claude API キーが必須（なし時は demo mode）
- 外部 CVE API（NVD など）との連携は段階 1 では非サポート
- リアルタイム更新は polling（Server-Sent Events 未実装）
- データベース不要（メモリ内保持）

---

### 2.10 前提条件

- Node.js 18.0 以上がインストール済み
- npm がインストール済み
- npm run dev でローカル開発サーバー起動可能
- ブラウザは Chrome/Safari/Firefox 最新版

---

## 3. 基本設計

### 3.1 システム構成

**システム構成図**

```
┌─────────────────────────────────────────┐
│     ブラウザ（フロントエンド）              │
│  HTML + Vanilla JS + CSS (Responsive)   │
│                                         │
│  - CVE テーブル表示                      │
│  - 統計情報（Critical/High count）       │
│  - AI メモリ・分析結果表示                 │
└────────────────┬────────────────────────┘
                 │ HTTP (fetch)
                 ↓
┌─────────────────────────────────────────┐
│  Node.js + Hono（バックエンド）           │
│                                         │
│  ├─ GET  / (HTML serve)                 │
│  ├─ GET  /api/cves (CVE list)           │
│  └─ POST /api/analyze-all (AI analysis) │
└────────────────┬────────────────────────┘
                 │ HTTP (API call)
                 ↓
        ┌────────────────────┐
        │  Claude API (REST) │
        │  (anthropic.com)   │
        └────────────────────┘
```

**技術スタック**

| 分類 | 内容 |
|------|------|
| OS | Linux/macOS/Windows |
| 言語 | TypeScript |
| フレームワーク | Hono (Web フレームワーク) |
| AI SDK | @anthropic-ai/sdk (Claude API) |
| フロント | HTML5 + Vanilla JavaScript + CSS3 |
| サーバー実行 | Node.js v18+ |
| 開発環境 | tsx (TypeScript executor) |

---

### 3.2 機能一覧

| ID | 機能名 | 概要 |
|----|--------|------|
| F-01 | CVE 取得 API | GET /api/cves でハードコード CVE リスト返却 |
| F-02 | AI 分析 API | POST /api/analyze-all で Claude API エージェント実行 |
| F-03 | 静的 HTML | GET / で UI を inline HTML で返却 |
| F-04 | メモリ管理 | 分析履歴・トークン数を in-memory で保持 |

---

### 3.3 画面設計

| 画面ID | 画面名 | 概要 |
|--------|--------|------|
| SCR-01 | ダッシュボード（メイン） | CVE 一覧・統計・分析結果・AI メモリを一画面で表示 |

**画面遷移図**

```
[ ダッシュボード ]
     ↓ (ユーザー: "Analyze All CVEs"ボタン)
[ 分析実行中 ] (ローディング表示)
     ↓ (API 応答)
[ 分析結果表示 ] (テーブル・メモリログ更新)
```

**画面要素**

- **ヘッダー**: VulnWatch タイトル・説明文
- **統計パネル**: Total CVEs / Critical / High の数値表示
- **CVE テーブル**: ID、Product、Severity、CVSS スコア
- **AI メモリ**: Invocations / Tokens Used / Analyses count
- **分析結果テーブル**: CVE ID・AI 推奨事項・詳細ボタン
- **メモリログ**: AI の思考プロセス（thinking）と推奨内容を時系列表示

---

### 3.4 API設計

| API ID | エンドポイント | 概要 | メソッド |
|--------|--------------|------|---------|
| API-01 | / | HTML UI を返却 | GET |
| API-02 | /api/cves | CVE リスト（JSON） | GET |
| API-03 | /api/analyze-all | AI エージェント実行・分析結果返却 | POST |

**API-02 レスポンス例**

```json
[
  {
    "id": "CVE-2026-26127",
    "title": "Microsoft Windows Print Queue RCE",
    "product": "Windows Print Spooler",
    "severity": "CRITICAL",
    "cvss": 9.8,
    "description": "Remote Code Execution in Windows Print Queue",
    "affected": "Windows 10, 11, Server 2019/2022"
  }
]
```

**API-03 リクエスト**

```json
{}  // Empty POST body
```

**API-03 レスポンス例**

```json
{
  "analyses": [
    {
      "cve_id": "CVE-2026-26127",
      "priority": "IMMEDIATE",
      "recommendation": "Priority: IMMEDIATE\n\n..."
    }
  ],
  "memory": {
    "invocation_count": 1,
    "total_tokens": 2500,
    "last_analysis_time": "2026-03-25T14:30:00.000Z",
    "analyses": [
      {
        "cve_id": "CVE-2026-26127",
        "timestamp": "2026-03-25T14:30:01.000Z",
        "thinking_process": "Analyzed CVE-2026-26127: CVSS 9.8 (CRITICAL)",
        "recommendation": "Priority: IMMEDIATE\n\nSince this is a remote code execution..."
      }
    ]
  }
}
```

---

### 3.5 データ設計

**ER図**

```
CVE Entity:
  - id (PK)
  - title
  - product
  - severity
  - cvss
  - description
  - affected

AgentMemory Entity:
  - invocation_count
  - total_tokens
  - last_analysis_time
  - analyses[] (array of Analysis)
    - cve_id (FK)
    - timestamp
    - thinking_process
    - recommendation
```

**テーブル一覧**

| テーブル名 | 概要 |
|-----------|------|
| CVE | 脆弱性情報（ハードコード） |
| AgentMemory | AI エージェント呼び出し履歴（in-memory） |

---

### 3.6 外部連携

| 連携先 | 概要 |
|--------|------|
| Claude API (Anthropic) | AI エージェント分析実行（HTTP/REST） |

---

### 3.7 エラー処理

- API キー未設定: "test-key" で demo 実行（結果は generic response）
- Claude API エラー: catch して UI に "Error: ..." と表示
- ネットワークエラー: fetch error をコンソール出力・UI に表示

---

### 3.8 ログ設計

- console.log で標準出力（本開発段階）
- 本番環境では Winston/Pino などのロギングライブラリへの移行推奨

---

### 3.9 セキュリティ設計

- **API キー管理**: ANTHROPIC_API_KEY 環境変数から読み込み（.env ファイル use）
- **CORS**: 同一オリジンのみ（ブラウザから localhost:3000 への接続）
- **入力検証**: CVE ID は ユーザー入力なし（バックエンド固定値）
- **output escaping**: HTML template で innerHTML 使用のため、テンプレートリテラル（backtick）で構造化

---

## 4. 詳細設計

### 4.1 モジュール一覧

| モジュールID | モジュール名 | 概要 |
|------------|------------|------|
| M-01 | Hono Server | HTTP サーバー・ルーティング |
| M-02 | CVE Database | 脆弱性情報メモリ管理 |
| M-03 | AI Agent | Claude API 連携ロジック |
| M-04 | Agent Memory | 分析履歴・トークン管理 |
| M-05 | HTML UI | インライン HTML テンプレート |
| M-06 | Client JavaScript | フロント側 API 呼び出し・UI 更新 |

---

### 4.2 クラス設計

**AgentMemory Class**

| 属性名 | 型 | 説明 |
|--------|-----|------|
| invocation_count | number | エージェント呼び出し回数 |
| total_tokens | number | 累計使用トークン数 |
| last_analysis_time | string | 最後の分析実行時刻（ISO 8601） |
| analyses | Array | 個別分析履歴 |

**メソッド**

| メソッド名 | 引数 | 戻り値 | 説明 |
|-----------|------|--------|------|
| recordAnalysis | cve_id, thinking, recommendation | void | 分析記録を履歴に追加 |

---

### 4.3 処理フロー

**API-03 /api/analyze-all フロー**

```
1. クライアント: POST /api/analyze-all
2. サーバー: agentMemory.invocation_count++
3. ループ: CVE_DATABASE の各 CVE に対して
   a. Claude API に分析リクエスト送信
   b. レスポンス（recommendation）を解析
   c. agentMemory に記録（thinking_process, recommendation）
   d. analyses 配列に追加
4. レスポンス返却: { analyses, memory }
5. クライアント: UI 更新（テーブル・メモリログ）
```

---

### 4.4 API詳細

**POST /api/analyze-all**

| 項目 | 内容 |
|------|------|
| エンドポイント | /api/analyze-all |
| メソッド | POST |
| リクエスト | 空（body なし）|
| レスポンス | JSON: { analyses: Array, memory: AgentMemory } |
| 説明 | Claude AI エージェントが全 CVE を分析し、優先度・推奨事項を返却 |

---

### 4.5 テーブル定義

**CVE Table**

| カラム | 型 | PK | NN | 説明 |
|--------|-----|----|----|------|
| id | string | ✓ | ✓ | CVE ID（例: CVE-2026-26127） |
| title | string | | ✓ | 脆弱性タイトル |
| product | string | | ✓ | 影響を受ける製品 |
| severity | string | | ✓ | 重要度（CRITICAL/HIGH/MEDIUM） |
| cvss | number | | ✓ | CVSS スコア（0-10） |
| description | string | | ✓ | 詳細説明 |
| affected | string | | ✓ | 影響を受けるバージョン |

---

### 4.6 バリデーション

| 項目 | 条件 | エラーメッセージ |
|------|------|----------------|
| API キー | ANTHROPIC_API_KEY 環境変数 | "test-key" で fallback |
| CVE ID | 正規表現 CVE-\d{4}-\d+ | （バックエンド固定値なため不要） |

---

### 4.7 例外処理

- Claude API 呼び出しエラー: try-catch で捕捉 → UI に "Analysis failed: [error message]" と表示
- ネットワークエラー: fetch reject → コンソール出力・UI alert
- JSON パース失敗: Response.json() 失敗 → "Invalid JSON response"

---

## 5. 単体テスト

### 5.1 テスト対象

- CVE データ取得（GET /api/cves）
- AI 分析 API（POST /api/analyze-all）
- メモリ管理（invocation_count, total_tokens increment）

### 5.2 テスト環境

| 項目 | 内容 |
|------|------|
| OS | macOS / Linux |
| 言語 | TypeScript |
| テストフレームワーク | (未実装、Jest 推奨) |

### 5.3 テストケース

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-01 | CVE 取得 API | GET /api/cves | CVE_DATABASE 配列が返却される |
| UT-02 | AI 分析 API | POST /api/analyze-all | { analyses, memory } を返却 |
| UT-03 | メモリカウント | 分析実行後 | invocation_count が 1 増加 |

---

## 6. 結合テスト

### 6.1 テスト目的

ブラウザから API 呼び出し → AI 分析実行 → UI 更新の一連フローが正常に動作することを確認

### 6.2 テスト範囲

- GET / で HTML 返却
- GET /api/cves で CVE リスト取得
- POST /api/analyze-all 実行 → AI 分析完了 → レスポンス返却
- ブラウザ JS で API 応答を処理 → UI テーブル・メモリログ更新

### 6.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | localhost:3000 |
| ブラウザ | Chrome 最新 |

### 6.4 テストシナリオ

| シナリオID | 内容 |
|----------|------|
| IT-01 | ダッシュボード起動 → CVE テーブル表示 → 「Analyze All」実行 → 分析結果・メモリ表示 |

---

## 7. 総合テスト

### 7.1 テスト目的

エンドユーザーの観点から、ダッシュボードが期待通り動作することを確認

### 7.2 テスト範囲

- ダッシュボード UI の初期ロード
- CVE 統計の正確性
- AI 分析ボタン動作
- メモリ可視化の正確性
- モバイルレスポンシブ対応

### 7.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | localhost:3000 |
| サーバ | Node.js 18+ |
| ブラウザ | Chrome, Safari, Firefox 最新 |

### 7.4 業務シナリオ

| シナリオID | 内容 |
|----------|------|
| ST-01 | セキュリティエンジニアが朝時点でダッシュボードを開き、最新の Patch Tuesday CVE を確認・分析して対応優先度を決定 |

---

## 7.5 受入基準

- CVE 一覧が正確に表示される
- AI 分析が実行でき、推奨事項が得られる
- メモリ（invocation_count, tokens）が正確に更新される
- UI がレスポンシブで、モバイルでも操作可能

---
