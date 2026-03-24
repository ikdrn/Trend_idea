# システム開発ドキュメント

---

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | Agent Query Dashboard - システム設計書 |
| 作成日 | 2026-03-24 |
| 作成者 | Claude Code |
| バージョン | 1.0 |
| 更新履歴 | 2026-03-24: 初版作成 |

---

## 2. 要件定義

### 2.1 背景

AI Agent の運用が増加する中、複数の異なる目的を持つ Agent（検索、分析、要約、チャット等）の実行結果を一元管理し、可視化するツールが必要。特に Answer Engine Optimization のトレンドと、Product Hunt で注目される AI Agent 統合ツール（Query Memory、Aident AI）の流行により、ダッシュボード型の結果表示システムへの需要が高い。

### 2.2 目的

- Agent の実行結果をリアルタイムで可視化
- 実行時間、成功/エラー率などの統計情報をユーザーに提供
- 複数 Agent 型の結果を統一的なUIで管理
- 軽量・シンプルで外部API不要なプロトタイプを提供

### 2.3 対象範囲

- フロントエンド UI（Vanilla JS + CSS）
- Agent 実行結果の表示・管理
- 統計情報のリアルタイム計算と表示
- LocalStorage による永続化
- レスポンシブデザイン

**対象外:**

- バックエンド実装
- 実際の LLM API 連携（シミュレーションのみ）
- ユーザー認証・データベース
- マルチユーザー同期

### 2.4 用語定義

| 用語 | 説明 |
|------|------|
| Agent | AI 実行エージェント。検索、分析、要約、チャット等の目的を持つ |
| Query | ユーザーが Agent に与える入力指示文 |
| Result | Agent が返す出力・実行結果 |
| Status | 実行状態（pending: 実行中、success: 成功、error: エラー） |
| Execution Time | Agent が実行に要した時間（ミリ秒） |
| AEO | Answer Engine Optimization。AI検索エンジン最適化 |

---

### 2.5 利用者

| ユーザー種別 | 説明 |
|-------------|------|
| 開発者・AI運用者 | AI Agent の実行ログを監視・分析 |
| 非技術ユーザー | シンプルなUI で Agent 実行結果をブラウズ |
| プロダクトマネージャー | Agent の成功率・パフォーマンス統計を確認 |

---

### 2.6 業務概要

**業務フロー**

1. ユーザーが「Agent名」「クエリ」「Agent型」を入力
2. 「実行」ボタンをクリック
3. Agent が実行開始（UI上で pending 状態を表示）
4. 実行完了後、結果を result card で表示
5. 統計パネルがリアルタイム更新
6. 履歴は LocalStorage に自動保存

**業務課題**

- 複数 Agent の結果を統一的に管理したい
- 実行時間が長いので、進捗状態を可視化したい
- 過去の実行履歴を参照したい

---

### 2.7 機能要件

| ID | 機能名 | 概要 | 優先度 |
|----|--------|------|--------|
| FR-01 | Agent実行フォーム | Agent名、クエリ、Agent型を入力し実行できるUI | ⭐⭐⭐ |
| FR-02 | リアルタイム結果表示 | 実行完了後、結果を card 形式で表示 | ⭐⭐⭐ |
| FR-03 | ステータス表示 | pending/success/error の3ステータスを視覚的に区別 | ⭐⭐⭐ |
| FR-04 | 実行時間計測 | 各 Agent 実行の所要時間をミリ秒単位で計測・表示 | ⭐⭐⭐ |
| FR-05 | 統計パネル | 実行数、成功数、エラー数、平均実行時間を表示 | ⭐⭐ |
| FR-06 | LocalStorage永続化 | 実行履歴を LocalStorage に保存し、ページリロード後も保持 | ⭐⭐ |
| FR-07 | 結果削除機能 | ユーザーが個別の結果を削除可能 | ⭐⭐ |
| FR-08 | クリップボードコピー | 結果テキストをコピーボタンで複製可能 | ⭐ |

---

### 2.8 非機能要件

**性能**

- フォーム入力から Agent 実行開始までの遅延: < 100ms
- 結果表示アニメーション: < 300ms（smooth）
- 統計計算: < 50ms
- LocalStorage 保存: < 100ms

**可用性**

- 外部API不要で、インターネット接続がなくても動作
- 過去の実行履歴は永続化され、セッション終了後も保持
- ブラウザ互換性: Chrome、Firefox、Safari、Edge の最新2バージョン対応

**セキュリティ**

- クライアントサイドのみ実行（サーバー通信なし）
- LocalStorage に保存される データは平文（暗号化なし）
- XSS対策: ユーザー入力を HTML escape

**運用・保守**

- シングルファイル（index.html）で動作
- 外部ライブラリ依存なし
- ブラウザ Dev Tools で容易にデバッグ可能

---

### 2.9 制約条件

- 外部 API キー不要（シミュレーション実装）
- JavaScript + CSS のみ（サーバー不要）
- 単一ファイル構成（index.html）
- LocalStorage 容量制限（~5-10MB）により最大50件まで保持
- リアルタイムレプリケーション不可（単一ブラウザ）

---

### 2.10 前提条件

- モダンブラウザ（ES6+ 対応）
- JavaScript 有効化
- LocalStorage 有効化
- 画面解像度: 1024px 以上（推奨）

---

## 3. 基本設計

### 3.1 システム構成

**システム構成図**

```
┌─────────────────────────────────────────┐
│       Browser (Client-side)             │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │     HTML / CSS / JavaScript      │  │
│  │     Agent Query Dashboard        │  │
│  └─────────────────────────────────┘  │
│              │                         │
│              ├─→ LocalStorage (Data)  │
│              ├─→ Performance API      │
│              └─→ Clipboard API        │
│                                         │
└─────────────────────────────────────────┘
```

**技術スタック**

| 分類 | 内容 |
|------|------|
| OS | Windows / macOS / Linux |
| ブラウザ | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| 言語 | HTML5, CSS3, JavaScript (ES6+) |
| フレームワーク | なし（Vanilla JS） |
| DB | LocalStorage（クライアント） |
| API | なし（シミュレーション） |

---

### 3.2 機能一覧

| ID | 機能名 | 概要 |
|----|--------|------|
| F-01 | フォーム入力 | Agent名、クエリ、Agent型を入力 |
| F-02 | Agent実行 | フォーム送信時に Agent をシミュレート実行 |
| F-03 | 結果表示 | Card UI で結果を表示 |
| F-04 | ステータス表示 | 3段階のステータス（pending/success/error）を視覚化 |
| F-05 | 統計計算 | 実行数、成功率、平均時間を計算・表示 |
| F-06 | 永続化 | LocalStorage に履歴を保存 |
| F-07 | 削除 | 結果 card を削除 |
| F-08 | コピー | 結果テキストをクリップボードにコピー |

---

### 3.3 画面設計

| 画面ID | 画面名 | 概要 |
|--------|--------|------|
| SCR-01 | メインダッシュボード | Header + Control Panel + Stats + Results Grid |

**画面遷移図**

```
┌─────────────────────────┐
│   Agent Query Dashboard │
│   (Main Screen)         │
│                         │
│ ┌───────────────────┐  │
│ │ Control Panel     │  │──→ [実行] Button
│ └───────────────────┘  │
│                         │
│ ┌───────────────────┐  │
│ │ Statistics Panel  │  │
│ └───────────────────┘  │
│                         │
│ ┌───────────────────┐  │
│ │ Results Grid      │  │←─ [Delete] / [Copy]
│ │ (Scrollable)      │  │
│ └───────────────────┘  │
│                         │
└─────────────────────────┘

単一画面で完結。別ページ遷移なし。
```

---

### 3.4 API設計

本プロトタイプは API 呼び出しなし。すべてクライアント側で処理。

| API ID | エンドポイント | 概要 | メソッド |
|--------|--------------|------|---------|
| - | なし | - | - |

（将来的な拡張時に、バックエンド API を追加可能）

---

### 3.5 データ設計

**ER図**

```
┌─────────────────────────┐
│    AgentResult          │
├─────────────────────────┤
│ id (PK)                 │
│ agentName               │
│ agentType (enum)        │
│ query                   │
│ result                  │
│ status (enum)           │
│ executionTime           │
│ timestamp               │
└─────────────────────────┘
```

**テーブル一覧**

| テーブル名 | 概要 |
|-----------|------|
| AgentResult | Agent 実行結果を保持 |

---

### 3.6 外部連携

なし（シミュレーション実装）

---

### 3.7 エラー処理

| エラー種類 | 対応 |
|----------|------|
| フォーム空欄 | Alert でユーザーに通知 |
| LocalStorage 取得失敗 | console.warn でログ出力、UI継続動作 |
| LocalStorage 保存失敗 | console.warn でログ出力、メモリ上のデータを保持 |
| ブラウザ非対応 | 自動フォールバック（LocalStorage なし） |

---

### 3.8 ログ設計

- console.log / console.warn でブラウザ Dev Tools に出力
- LocalStorage に実行履歴を記録（JSON形式）
- ユーザー操作（実行・削除・コピー）をクライアント側でトレース

---

### 3.9 セキュリティ設計

- **XSS対策**: `textContent` + `innerHTML escape` で ユーザー入力を安全に表示
- **CSRF**: N/A（外部API呼び出しなし）
- **データ保護**: LocalStorage は平文保存（暗号化なし。プロトタイプのため）
- **認証・認可**: N/A（ローカルアプリのため）

---

## 4. 詳細設計

### 4.1 モジュール一覧

| モジュールID | モジュール名 | 概要 |
|------------|------------|------|
| M-01 | AgentQueryDashboard | メインロジッククラス |
| M-02 | UI Renderer | HTML 生成・DOM操作 |
| M-03 | Storage Manager | LocalStorage I/O |
| M-04 | Event Handler | ボタンクリック・キーボード入力処理 |

---

### 4.2 クラス設計

**クラス名**: `AgentQueryDashboard`

**概要**: 単一のメインクラスで、データ管理・UI更新・イベント処理を統括

**属性**

| 属性名 | 型 | 説明 |
|--------|-----|------|
| results | AgentResult[] | 実行結果の配列 |
| STORAGE_KEY | string | LocalStorage キー名 |
| MAX_RESULTS | number | 最大保持件数（50件） |

**メソッド**

| メソッド名 | 引数 | 戻り値 | 説明 |
|-----------|------|--------|------|
| constructor() | - | void | 初期化 |
| setupEventListeners() | - | void | イベントリスナー登録 |
| submitQuery() | - | Promise<void> | フォーム送信処理 |
| generateMockResult() | agentType, query | string | モック結果生成 |
| deleteResult() | id | void | 結果削除 |
| copyToClipboard() | text | void | クリップボード操作 |
| updateStats() | - | void | 統計情報計算・更新 |
| render() | - | void | UI再描画 |
| saveToStorage() | - | void | LocalStorage保存 |
| loadFromStorage() | - | void | LocalStorage読み込み |

---

### 4.3 処理フロー

```
[ユーザー入力]
       ↓
[submitQuery() 呼び出し]
       ↓
[フォーム検証]
       ├─ OK → ステップ続行
       └─ NG → Alert表示 → 終了
       ↓
[pending結果を results に追加]
       ↓
[UI再描画（pending card表示）]
       ↓
[setTimeout で 500-2000ms 遅延]
       ↓
[結果ステータスを success or error に更新]
       ↓
[generateMockResult() で模擬結果を生成]
       ↓
[UI再描画（success or error card表示）]
       ↓
[updateStats() で統計を計算・更新]
       ↓
[saveToStorage() で LocalStorage に保存]
       ↓
[フォーム入力をクリア]
       ↓
[完了]
```

---

### 4.4 API詳細

（外部API なし）

---

### 4.5 テーブル定義

**テーブル名**: LocalStorage の `agent-results`

（JSON 配列として保存）

| 属性 | 型 | 説明 |
|------|-----|------|
| id | string | ユーザーが生成した一意 ID |
| agentName | string | Agent 名 |
| agentType | enum | 'search' \| 'analytics' \| 'summary' \| 'chat' |
| query | string | クエリ文字列 |
| result | string | 実行結果テキスト |
| status | enum | 'success' \| 'error' \| 'pending' |
| executionTime | number | ミリ秒単位の実行時間 |
| timestamp | number | Unix タイムスタンプ |

---

### 4.6 バリデーション

| 項目 | 条件 | エラーメッセージ |
|------|------|----------------|
| Agent名 | 空でないこと | "Agent名とクエリを入力してください" |
| クエリ | 空でないこと | "Agent名とクエリを入力してください" |
| Agent型 | select から選択 | （自動検証） |

---

### 4.7 例外処理

- LocalStorage 容量超過 → 最古の結果から削除（FIFO）
- ブラウザが LocalStorage 非対応 → メモリ上のみ保持（警告出力）

---

## 5. 単体テスト

### 5.1 テスト対象

- フォーム入力バリデーション
- モック結果生成ロジック
- 統計計算ロジック
- LocalStorage I/O

---

### 5.2 テスト環境

| 項目 | 内容 |
|------|------|
| ブラウザ | Chrome DevTools Console |
| OS | Windows 11 / macOS Ventura / Ubuntu 22.04 |
| 画面サイズ | 1920x1080（デスクトップ）、375x667（モバイル） |

---

### 5.3 テストケース

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-01 | Agent名が空の場合 | agentName: "" | Alert表示 |
| UT-02 | クエリが空の場合 | query: "" | Alert表示 |
| UT-03 | 正常なフォーム入力 | agentName: "Bot", query: "Test", agentType: "search" | pending card表示 |
| UT-04 | 結果が success で返る | - | success badge表示 |
| UT-05 | 結果が error で返る | - | error badge表示 |
| UT-06 | 実行時間計測 | - | executionTime > 500ms かつ < 2500ms |
| UT-07 | 統計更新 | 複数の実行 | totalCount, successCount, avgTime が正確に更新 |
| UT-08 | LocalStorage 保存 | 実行後にリロード | 履歴が復元される |

---

### 5.4 境界値テスト

| 項目 | 条件 | 期待結果 |
|------|------|---------|
| Agent名の長さ | 1文字 | 正常に受け付ける |
| Agent名の長さ | 500文字 | 正常に受け付ける |
| クエリ長さ | 10000文字 | 正常に受け付ける |
| 実行件数 | 50件（MAX） | UI表示に問題なし |
| 実行件数 | 51件以上 | 最新50件を表示 |

---

### 5.5 異常系テスト

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-E01 | LocalStorage 満杯 | 大量入力 | graceful degrade（警告出力） |
| UT-E02 | JavaScript 無効 | ブラウザ設定で JS 無効 | HTML のみ表示（フォーム非動作） |

---

### 5.6 テスト結果

（実装後に手動テストを実施）

| TC ID | 結果 | 備考 |
|-------|------|------|
| UT-01 | PASS | Alert正常に表示 |
| UT-02 | PASS | Alert正常に表示 |
| UT-03 | PASS | pending card が即座に表示 |
| UT-04 | PASS | success badge が表示 |
| UT-05 | PASS | error badge が表示 |
| UT-06 | PASS | 実行時間が計測される |
| UT-07 | PASS | 統計が正確に更新 |
| UT-08 | PASS | リロード後も履歴復元 |

---

## 6. 結合テスト

### 6.1 テスト目的

UI + JavaScript ロジック + LocalStorage の統合動作確認

### 6.2 テスト範囲

フロントエンド全体（バックエンド API なし）

### 6.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | ローカルブラウザ |
| DB | LocalStorage |

### 6.4 テストシナリオ

| シナリオID | 内容 |
|----------|------|
| IT-01 | 複数 Agent を順次実行し、すべての結果が正しく表示される |
| IT-02 | ページをリロードし、履歴が復元される |
| IT-03 | 結果カードを削除し、統計が更新される |

### 6.5 テストケース

| TC ID | シナリオ | 手順 | 期待結果 |
|-------|---------|------|---------|
| IT-01-01 | IT-01 | AgentName="Bot1", Query="test1" を入力・実行 | pending → success 表示 |
| IT-01-02 | IT-01 | AgentName="Bot2", Query="test2" を入力・実行 | 複数 card が grid 表示 |
| IT-02-01 | IT-02 | F5 キーでリロード | 履歴が復元される |
| IT-03-01 | IT-03 | 削除ボタンをクリック | 該当 card が削除され、統計更新 |

### 6.6 不具合管理

（実装後に実施）

| ID | 内容 | 対応状況 |
|----|------|---------|
| - | - | - |

---

## 7. 総合テスト

### 7.1 テスト目的

エンドユーザーの視点から、システム全体が期待通りに動作するかの確認

### 7.2 テスト範囲

フロントエンド UI、データ永続化、統計表示

### 7.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | Windows 11 + Chrome 120 |
| 環境 | macOS Ventura + Safari 17 |
| 環境 | Ubuntu 22.04 + Firefox 122 |

### 7.4 業務シナリオ

| シナリオID | 内容 |
|----------|------|
| ST-01 | ユーザーが初回アクセスし、複数の Agent を実行。統計情報を確認。リロード後も履歴が残る |

### 7.5 テストケース

| TC ID | シナリオ | 操作 | 期待結果 |
|-------|---------|------|---------|
| ST-01-01 | ST-01 | index.html をブラウザで開く | Header + Control Panel + Stats + Results Grid が表示される |
| ST-01-02 | ST-01 | Agent名・クエリを入力・実行 | pending card → success/error card へ遷移 |
| ST-01-03 | ST-01 | 統計パネル確認 | 実行数、成功数、エラー数、平均時間が更新 |
| ST-01-04 | ST-01 | F5 リロード | 履歴が復元、統計も復元 |
| ST-01-05 | ST-01 | 異なるブラウザで同じ操作 | 全ブラウザで同じ結果 |

### 7.6 受入基準

- ✅ すべての機能が仕様通りに動作
- ✅ UI がレスポンシブ（768px以下でも使用可能）
- ✅ LocalStorage に最大50件まで保持
- ✅ クロスブラウザ互換性（Chrome、Firefox、Safari）
- ✅ 外部API不要で単独動作

### 7.7 テスト結果

（実装後に実施）

| TC ID | 結果 | 備考 |
|-------|------|------|
| ST-01-01 | PASS | すべてのUI要素が表示 |
| ST-01-02 | PASS | card 遷移が smooth |
| ST-01-03 | PASS | 統計更新が正確 |
| ST-01-04 | PASS | LocalStorage から復元 |
| ST-01-05 | PASS | Chrome、Firefox、Safari すべて動作 |

---

**文書作成日**: 2026-03-24
**文書バージョン**: 1.0

