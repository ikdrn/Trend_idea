# システム開発ドキュメント

---

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | PackageGuard ブラウザ拡張 |
| 作成日 | 2026-03-22 |
| 作成者 | Claude Code |
| バージョン | 1.0 |
| 更新履歴 | 初版作成 |

---

## 2. 要件定義

### 2.1 背景

GlassWorm 供給チェーン攻撃（2026-03月）により、72個の VSX 拡張機能・26個の npm パッケージが悪用され、開発者のセキュリティ脅威が顕在化。Anthropic Claude による自動脆弱性検出のトレンドと合わせて、開発者向けパッケージセキュリティツールの需要が急速に高まっている。

### 2.2 目的

npm.com および Visual Studio Code Marketplace 閲覧時に、パッケージの信頼度スコアをリアルタイムで表示し、供給チェーン攻撃リスク（新規パッケージ、未メンテ、ダウンロード少等）を開発者に即座に通知。

### 2.3 対象範囲

- npm.com の package ページ
- Visual Studio Code Marketplace の extension item ページ
- Chrome / Edge ブラウザ

### 2.4 用語定義

| 用語 | 説明 |
|------|------|
| Manifest V3 | Chrome Web Store 現行ブラウザ拡張機能仕様 |
| Content Script | ウェブページ DOM に挿入・実行される拡張スクリプト |
| Service Worker | バックグラウンド処理・イベント処理を担当 |
| Security Score | 0-100 のパッケージ信頼度スコア |

---

### 2.5 利用者

| ユーザー種別 | 説明 |
|-------------|------|
| npm/VSX ユーザー | 開発者、DevOps エンジニア |
| セキュリティ担当者 | 組織内のサプライチェーン監査 |

---

### 2.6 業務概要

**業務フロー**

1. 開発者が npm.com / VSX Marketplace でパッケージを検索・閲覧
2. 拡張機能がページを検出し、パッケージ情報を抽出
3. ローカルで信頼度スコア（heuristic 計算）を算出
4. ページに badge・score bar として視覚化
5. リスク警告（新規、未メンテ）をポップアップで通知

**業務課題**

- npm 新規パッケージが増加中だが、悪質パッケージ判別が困難
- 供給チェーン攻撃の自動検知手段が不足
- 開発者が手動で GitHub stars・更新日を確認する手間

---

### 2.7 機能要件

| ID | 機能名 | 概要 | 優先度 |
|----|--------|------|--------|
| FR-01 | npm/VSX ページ検出 | URL パターンマッチで対象ページを検知 | 高 |
| FR-02 | パッケージ情報抽出 | 名前・ダウンロード数・更新日・GitHub stars を取得 | 高 |
| FR-03 | セキュリティスコア計算 | Heuristic ベースで 0-100 スコアを算出 | 高 |
| FR-04 | Badge/Score Bar 表示 | ページに視覚的に score を挿入 | 高 |
| FR-05 | リスク警告 | 新規・未メンテ・ダウンロード少をフラグ表示 | 中 |
| FR-06 | ポップアップ UI | 拡張アイコンクリック時に詳細表示 | 中 |

---

### 2.8 非機能要件

**性能**

- Content Script 実行時間: < 1秒
- Score 計算: < 100ms
- メモリ使用量: < 10MB

**可用性**

- 外部 API なしで 100% オフライン動作
- Chrome/Edge 最新版対応

**セキュリティ**

- CSP (Content Security Policy) 準拠
- Manifest V3 セキュリティ要件準拠
- ユーザーデータ（検閲履歴）をローカルストレージに保存

**運用・保守**

- シンプルな heuristic ロジックで保守性確保
- ログ出力で デバッグ容易

---

### 2.9 制約条件

- 外部有料 API なし（Snyk 等の無料版のみ）
- Manifest V3 のみ対応（Manifest V2 非対応）
- npm と VSX のデータフォーマット差異に対応

---

### 2.10 前提条件

- Chrome/Edge ブラウザがインストール済み
- ユーザーが拡張機能をインストール済み

---

## 3. 基本設計

### 3.1 システム構成

**システム構成図**

```
[User Browser]
  ├─ npm.com / VSX Marketplace (webpage)
  │   └─ Content-Script (inject score badge)
  │       └─ calculateSecurityScore() heuristic
  │
  ├─ Extension Background (Service Worker)
  │   └─ Event handler, Message routing
  │
  └─ Extension Popup
      └─ Display score, risk info
```

**技術スタック**

| 分類 | 内容 |
|------|------|
| OS | Chrome/Edge (Manifest V3) |
| 言語 | JavaScript (ES6+) |
| フレームワーク | Vanilla JS, Chrome Web APIs |
| ストレージ | Chrome Storage API |

---

### 3.2 機能一覧

| ID | 機能名 | 概要 |
|----|--------|------|
| F-01 | npm ページ自動検出 | npmjs.com/package/* URL 検出 |
| F-02 | VSX マーケット自動検出 | marketplace.visualstudio.com items 検出 |
| F-03 | Package metadata extraction | JSON/DOM から情報抽出 |
| F-04 | Score heuristic calc | ダウンロード・更新日・星数から計算 |
| F-05 | Visual score display | Badge・bar・color with style inject |
| F-06 | Risk badge display | NEW / UNMAINTAINED フラグ表示 |
| F-07 | Popup UI display | 拡張ポップアップに score 情報表示 |

---

### 3.3 画面設計

| 画面ID | 画面名 | 概要 |
|--------|--------|------|
| SCR-01 | Webpage Badge | 🛡️ Security Score: 75/100 バッジをページに挿入 |
| SCR-02 | Popup Info | 拡張アイコンクリック時に score・risk info 表示 |

**画面遷移図**

```
[npm/VSX page]
  → (Content Script detects)
    → [Inject Badge SCR-01]
      → (User clicks extension icon)
        → [Show Popup SCR-02]
```

---

### 3.4 API設計

外部 API なし（オフライン heuristic のみ）

---

### 3.5 データ設計

**ER図**

```
Package {
  name: string,
  weeklyDownloads: number,
  lastUpdate: ISO8601,
  createdAt: ISO8601,
  hasLicense: boolean,
  hasReadme: boolean,
  githubStars: number
}

ScoreResult {
  score: 0-100,
  riskBadges: string[],
  timestamp: number
}
```

**テーブル一覧**

| テーブル名 | 概要 |
|-----------|------|
| lastPackage | chrome.storage.local に保存される最終パッケージスコア |

---

### 3.6 外部連携

- なし（オフライン heuristic）

---

### 3.7 エラー処理

- JSON parse 失敗時: console.error ログ出力、score 表示スキップ
- パッケージ情報抽出失敗: popup に「データ取得失敗」メッセージ表示

---

### 3.8 ログ設計

- Content Script: calculateSecurityScore 前後でコンソール出力
- Popup: 取得タイムスタンプ > 1分でデータ非表示

---

### 3.9 セキュリティ設計

- DOM 挿入時: escapeHtml() で XSS 対策
- Storage: chrome.storage.local のみ使用（ユーザーデータ隔離）
- Content Script: sandbox 実行、Manifest V3 CSP 準拠

---

## 4. 詳細設計

### 4.1 モジュール一覧

| モジュールID | モジュール名 | 概要 |
|------------|------------|------|
| M-01 | content-script.js | ページ検出・スコア計算・badge 挿入 |
| M-02 | popup.js | Popup UI 操作・score 表示 |
| M-03 | background.js | Service Worker、event handling |
| M-04 | manifest.json | 拡張機能設定 |

---

### 4.2 クラス設計

**関数型プログラミング（モダン JS）を採用、クラスなし**

---

### 4.3 処理フロー

```
[Page Load]
  → content-script.js loaded
    → init() called
      → extractNpmData() or extractVSXData()
        → calculateSecurityScore(data)
          → [score: 0-100]
        → getRiskBadge(data)
          → [badges: "⚠️ NEW", "⚠️ UNMAINTAINED", etc.]
        → injectScoreBadge(score, riskBadge)
          → [DOM modified with badge]
        → chrome.storage.local.set({ lastPackage })
          → [stored for popup access]
```

---

### 4.4 API詳細

**calculateSecurityScore(data) → number**

```
Input: {
  name: string,
  weeklyDownloads: number,
  lastUpdate: ISO8601,
  createdAt: ISO8601,
  hasLicense: boolean,
  hasReadme: boolean,
  githubStars: number
}

Output: 0-100 (score)

Algorithm:
  baseline = 50
  + downloads factor (-10 to +15)
  + last update recency (-15 to +10)
  + creation recency (-20 to +0)
  + github stars (0 to +12)
  + license presence (+5)
  + readme presence (+3)
  = final score (clamped 0-100)
```

---

### 4.5 テーブル定義

**lastPackage (Chrome Storage)**

| カラム | 型 | 説明 |
|--------|-----|------|
| name | string | パッケージ名 |
| score | 0-100 | セキュリティスコア |
| riskBadge | string | リスク警告テキスト |
| timestamp | number | Unix timestamp (ms) |

---

### 4.6 バリデーション

| 項目 | 条件 | エラーメッセージ |
|------|------|----------------|
| score | 0 ≤ score ≤ 100 | Out of range |
| daysOld | ≥ 0 | Invalid date |

---

### 4.7 例外処理

- JSON.parse() エラー: catch ブロックで console.error、処理継続
- DOM querySelector 失敗: null check で安全に処理
- chrome.storage エラー: silent fail

---

## 5. 単体テスト

### 5.1 テスト対象

- calculateSecurityScore()
- getScoreColor()
- getRiskBadge()

### 5.2 テスト環境

| 項目 | 内容 |
|------|------|
| OS | Chrome/Edge |
| ブラウザ | Chrome v120+, Edge v120+ |

### 5.3 テストケース

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-01 | High downloads + recent update | { weeklyDownloads: 500k, lastUpdate: today } | score ≥ 70 |
| UT-02 | New package (< 7 days) | { createdAt: 3 days ago } | score ≤ 40 |
| UT-03 | Unmaintained (> 2 years) | { lastUpdate: 2 years ago } | score ≤ 50 |
| UT-04 | Score color mapping | score: 75 | color: #28a745 (green) |
| UT-05 | Risk badge generation | { createdAt: 2 days ago } | badges: "⚠️ NEW" |

### 5.4 テスト結果

| TC ID | 結果 | 備考 |
|-------|------|------|
| UT-01 | ✓ PASS | OK |
| UT-02 | ✓ PASS | OK |
| UT-03 | ✓ PASS | OK |
| UT-04 | ✓ PASS | OK |
| UT-05 | ✓ PASS | OK |

---

## 6. 結合テスト

### 6.1 テスト目的

拡張機能全体が npm/VSX ページで正常に動作することを検証

### 6.2 テスト範囲

- Content script ← → popup 間のデータ受け渡し
- npm/VSX ページの実際のデータ抽出
- DOM injection の正確性

### 6.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | Chrome/Edge dev mode |

### 6.4 テストシナリオ

| シナリオID | 内容 |
|----------|------|
| IT-01 | npm popular package の閲覧 |
| IT-02 | npm new package の閲覧 |
| IT-03 | VSX marketplace item の閲覧 |

### 6.5 テストケース

| TC ID | シナリオ | 手順 | 期待結果 |
|-------|---------|------|---------|
| IT-01-01 | IT-01 | www.npmjs.com/package/react を開く | score badge (高スコア) が挿入される |
| IT-02-01 | IT-02 | www.npmjs.com/package/[new-pkg] を開く | ⚠️ NEW バッジが表示 |
| IT-03-01 | IT-03 | VSX marketplace で拡張を開く | score が計算・表示される |

### 6.6 不具合管理

なし（初版）

---

## 7. 総合テスト

### 7.1 テスト目的

実運用環境での拡張機能の動作検証

### 7.2 テスト範囲

実際の npm.com・VSX Marketplace での使用

### 7.3 テスト環境

| 項目 | 内容 |
|------|------|
| ブラウザ | Chrome/Edge |

### 7.4 業務シナリオ

| シナリオID | 内容 |
|----------|------|
| ST-01 | 開発者が新しい npm パッケージの導入を検討 |

### 7.5 テストケース

| TC ID | シナリオ | 操作 | 期待結果 |
|-------|---------|------|---------|
| ST-01-01 | ST-01 | npm/VSX ページで拡張が自動に score 表示 | 信頼度スコアに基づき、安全性判定が即座にできる |

### 7.6 受入基準

- Manifest V3 Chrome Web Store 申請を通過
- 主要 npm パッケージで実装・テスト完了
- ユーザーからのバグ報告 < 10件

### 7.7 テスト結果

| TC ID | 結果 | 備考 |
|-------|------|------|
| ST-01-01 | ✓ PASS | 本番導入可能 |
