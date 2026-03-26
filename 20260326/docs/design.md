# システム開発ドキュメント

---

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | AI Package Threat Monitor CLI - 設計仕様書 |
| 作成日 | 2026-03-26 |
| 作成者 | Claude Code AI System |
| バージョン | 1.0 |
| 更新履歴 | - v1.0: 初版作成 (2026-03-26) |

---

## 2. 要件定義

### 2.1 背景

- TeamPCP による litellm パッケージ侵害（2026年3月）、Trivy セキュリティスキャナーの GitHub Actions 攻撃
- AI エージェント・LLM インフラの急速な普及に伴い、npm/pip パッケージがサプライチェーン攻撃の主要ターゲット化
- 開発者がリアルタイムで依存パッケージの脅威を検知するニーズが急増

### 2.2 目的

- npm/pip パッケージの既知脆弱性・侵害リスクを自動検索・リアルタイム表示する CLI ツール提供
- AI/LLM インフラ (litellm, langflow, huggingface など) の脅威情報を集約
- 開発チームが CI/CD パイプライン内でセキュリティ脅威を即座に判定できる仕組み構築

### 2.3 対象範囲

- npm パッケージマネージャー対応（将来 pip, cargo 拡張予定）
- litellm, langflow, huggingface/transformers など AI 関連パッケージの脅弱性データベース
- GitHub Advisory API との基本連携（シミュレート版）
- CLI インターフェース（REST API 拡張は Future Scope）

### 2.4 用語定義

| 用語 | 説明 |
|------|------|
| サプライチェーン攻撃 | 開発ツール・ライブラリを改ざん・侵害してユーザーシステム侵害を狙う攻撃 |
| CVE | Common Vulnerabilities and Exposures - 共通脆弱性識別子 |
| CRITICAL 脆弱性 | 権限昇格・RCE など最も危険度の高い脆弱性 |
| GitHub Advisory | GitHub が管理する脆弱性アドバイザリデータベース |
| Transitive Dependency | 直接的な依存ではなく、依存パッケージが依存する間接的なライブラリ |

---

### 2.5 利用者

| ユーザー種別 | 説明 |
|-------------|------|
| DevSecOps エンジニア | CI/CD パイプライン内で脅威スキャンを自動実行 |
| アプリケーション開発者 | 本番環境 push 前にパッケージ脅威を検査 |
| セキュリティチーム | 依存パッケージの脅弱性トレンド監視 |
| LLM アプリ開発者 | litellm など AI パッケージの脅威リスク把握 |

---

### 2.6 業務概要

**業務フロー**

1. 開発者が `threat-monitor <package-name>` を実行
2. CLI が脅弱性データベースをクエリ
3. 既知脆弱性が存在する場合、severity レベル別にカラー表示
4. CRITICAL 脆弱性が検出される場合、緊急パッチ推奨メッセージを出力
5. `-g` フラグで GitHub Advisory データベースも同時検索

**業務課題**

- 現状：npm audit, pip-audit などの既存ツールは AI パッケージ専用データベースを持たない
- 脅弱性検出に遅延（GitHub Advisory の収集・公開に時間）
- 開発チーム間でセキュリティ脅威情報の認識がばらつき

---

### 2.7 機能要件

| ID | 機能名 | 概要 | 優先度 |
|----|--------|------|--------|
| FR-01 | パッケージ脅弱性検索 | CLI で指定パッケージ名を入力し、既知脅弱性をデータベースから検索 | 高 |
| FR-02 | Severity レベル判定 | CRITICAL, HIGH, MEDIUM, LOW の4段階で脅弱性を分類・表示 | 高 |
| FR-03 | カラーリング出力 | severity レベル別に色分けして CLI 出力（CRITICAL=赤, HIGH=橙など） | 高 |
| FR-04 | GitHub Advisory 連携 | `-g` フラグで GitHub のアドバイザリデータベースを查詢 | 中 |
| FR-05 | 複数パッケージ対応 | npm, pip, cargo の複数パッケージマネージャー対応（段階実装） | 中 |
| FR-06 | JSON 出力形式 | CI/CD パイプライン統合向けに JSON レポート出力機能 | 低 |

---

### 2.8 非機能要件

**性能**

- 単一パッケージスキャン：100ms 以下
- GitHub Advisory API クエリ（ネットワーク待機含む）：3秒以内
- 大規模依存グラフスキャン（100+ パッケージ）：30秒以内

**可用性**

- CLI バイナリは単体実行可能（外部サービス依存なし）
- GitHub Advisory API 障害時も、ローカルデータベースで最小限の機能提供
- ログ記録により、検索履歴を追跡可能

**セキュリティ**

- API キー・認証情報の不要（公開データのみ使用）
- ネットワークリクエストは HTTPS のみ
- 入力値のサニタイズ（パッケージ名の不正文字フィルタリング）

**運用・保守**

- Rust で実装し、単一バイナリとしてデプロイ
- 脆弱性データベースは定期更新スケジュール（週1回推奨）
- ログ出力で動作状況を可視化

---

### 2.9 制約条件

- Rust 1.70+ の環境必須
- GitHub Advisory API v4 (GraphQL) の仕様遵守
- npm registry は公開 API のみ使用（認証なし）
- 本開発スコープでは litellm, langflow, huggingface の3パッケージのみデータベース化

---

### 2.10 前提条件

- Rust ツールチェーン（cargo）がインストール済み
- インターネット接続は GitHub Advisory API クエリ時のみ必須
- パッケージ名は英数字 + ハイフン に限定（@org/package 形式対応）

---

## 3. 基本設計

### 3.1 システム構成

**システム構成図**

```
┌─────────────────────────────────────────────────────┐
│                CLI User Interface                     │
│         ($ threat-monitor <package-name>)            │
└────────────────┬────────────────────────────────────┘
                 │
         ┌───────▼──────────┐
         │  CLI Argument     │
         │  Parser (clap)    │
         └────────┬──────────┘
                 │
     ┌───────────┴──────────────┐
     │                          │
┌────▼───────────┐    ┌────────▼──────────┐
│ Package Threat │    │ GitHub Advisory   │
│ Database       │    │ API Handler       │
│ (in-memory)    │    │ (optional)        │
└────┬───────────┘    └────────┬──────────┘
     │                         │
     └───────────┬─────────────┘
                 │
         ┌───────▼────────────┐
         │ Severity Coloring  │
         │ & Formatting       │
         │ (colored crate)    │
         └────────┬───────────┘
                 │
        ┌────────▼────────────┐
        │  CLI Output (stdout)│
        └─────────────────────┘
```

**技術スタック**

| 分類 | 内容 |
|------|------|
| 言語 | Rust 2021 Edition |
| フレームワーク | clap (CLI argument parsing) |
| カラーリング | colored (ANSI color output) |
| パッケージ | cargo package manager |
| ビルドツール | rustc + cargo |

---

### 3.2 機能一覧

| ID | 機能名 | 概要 |
|----|--------|------|
| F-01 | パッケージ検索 | 入力パッケージ名から脅弱性データベースをクエリ |
| F-02 | Severity 判定 | CVE ID から severity レベルを特定 |
| F-03 | カラー出力 | severity レベル別に色分けしたテーブル表示 |
| F-04 | GitHub Advisory | -g フラグで GitHub API を非同期クエリ（簡略版） |
| F-05 | エラーハンドリング | パッケージ未検出時の親切なメッセージ表示 |

---

### 3.3 画面設計

| 画面ID | 画面名 | 概要 |
|--------|--------|------|
| SCR-01 | スキャンレポート画面 | パッケージ名 + 脆弱性一覧を表示 |
| SCR-02 | GitHub Advisory 画面 | 公式 Advisory リンクを表示（オプション） |
| SCR-03 | エラーメッセージ画面 | パッケージ未検出・API エラー時 |

**画面遷移図**

```
┌─────────────────────────────┐
│  Start (CLI Invocation)     │
└────────────┬────────────────┘
             │
      ┌──────▼───────┐
      │ Package      │
      │ Input Check  │
      └──────┬───────┘
             │
    ┌────────▼─────────┐
    │ Check -g flag?   │
    └────┬───────────┬─┘
         │ YES       │ NO
    ┌────▼─────┐  ┌──▼──────────────────┐
    │ GitHub   │  │ Show Threat Report   │
    │ Advisory │  │ (colored output)     │
    │ Fetch    │  └─────┬────────────────┘
    └────┬─────┘        │
         │              │
    ┌────▼──────────────▼────────┐
    │ Merge & Display Results     │
    │ (Table + GitHub Links)      │
    └────┬───────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ End (Exit Code 0 or 1)    │
    └───────────────────────────┘
```

---

### 3.4 API設計

**GitHub Advisory API** (簡略版)

| API ID | エンドポイント | 概要 | メソッド |
|--------|--------------|------|---------|
| API-01 | /graphql | GitHub Advisory GraphQL エンドポイント（未実装） | POST |
| API-02 | npm audit API | npm package vulnerability API（未実装） | GET |

現バージョン：シミュレーション実装（ハードコード脅弱性データベース）

---

### 3.5 データ設計

**脆弱性レコードスキーマ**

```rust
struct Vulnerability {
    id: String,              // CVE-XXXX-XXXXX or GHSA-XXXX-XXXX-XXXX
    severity: String,        // CRITICAL, HIGH, MEDIUM, LOW
    description: String,     // 脆弱性説明
    affected_versions: String, // 影響を受けるバージョン範囲
}
```

**脆弱性データベース** (in-memory)

```
litellm:
  - TeamPCP-SUPPLY-CHAIN-001 (CRITICAL)
  - CVE-2026-LITELLM-AUTH (HIGH)

langflow:
  - CVE-2026-33017 (CRITICAL)

@huggingface/transformers:
  - HF-SUPPLY-CHAIN-002 (MEDIUM)
```

---

### 3.6 外部連携

| 連携先 | 概要 |
|--------|------|
| GitHub Advisory API | 公式脆弱性アドバイザリ検索（将来） |
| npm registry API | npm パッケージメタデータ検索（将来） |
| Python Package Index (PyPI) | pip パッケージ検索（将来） |
| NVD (National Vulnerability Database) | CVE データベース（将来） |

---

### 3.7 エラー処理

- **パッケージ未検出**: "No vulnerabilities detected for this package." (緑メッセージ)
- **GitHub API エラー**: GitHub Advisory API へのアクセス失敗時は、ローカルデータベースの結果のみ表示
- **不正なパッケージ名**: パッケージ名に不正文字が含まれる場合、エラーメッセージを出力

---

### 3.8 ログ設計

- stderr への簡潔なログ出力（デバッグモード `-d` で詳細ログ出力予定）
- GitHub Advisory クエリ時のリクエスト/レスポンス情報を記録

---

### 3.9 セキュリティ設計

- **入力値検証**: パッケージ名は `^[a-zA-Z0-9@_/-]+$` 正規表現でチェック
- **API 認証**: GitHub API キーは不要（公開データのみ利用）
- **HTTPS**: すべてのネットワークリクエストは HTTPS のみ

---

## 4. 詳細設計

### 4.1 モジュール一覧

| モジュールID | モジュール名 | 概要 |
|------------|------------|------|
| M-01 | main | CLI エントリーポイント＆引数パース |
| M-02 | scanner | パッケージ脅弱性スキャンロジック |
| M-03 | database | 脆弱性データベース管理 |
| M-04 | formatter | カラーリング & 出力フォーマット |

---

### 4.2 クラス設計（Rust Struct）

**Vulnerability**

| 属性名 | 型 | 説明 |
|--------|-----|------|
| id | String | CVE/GHSA ID |
| severity | String | CRITICAL \| HIGH \| MEDIUM \| LOW |
| description | String | 脆弱性の詳細説明 |
| affected_versions | String | 影響を受けるバージョン |

**メソッド**

| メソッド名 | 引数 | 戻り値 | 説明 |
|-----------|------|--------|------|
| color_severity() | - | ColoredString | severity に応じた色付き文字列を返す |

---

### 4.3 処理フロー

1. **CLI 入力受け取り**
   - `clap` で `--package <NAME>` と `-g` フラグを解析

2. **パッケージ脅弱性検索**
   - `simulate_package_scan()` 関数が脆弱性データベースをクエリ
   - マッチするパッケージがあれば `Vec<Vulnerability>` を返す

3. **Severity カラー化**
   - `print_threat()` で各脆弱性を severity レベル別の色で出力

4. **GitHub Advisory オプション**
   - `-g` フラグが指定されている場合、`check_github_advisory()` を実行
   - GitHub API シミュレーション結果を追加出力

5. **終了**
   - 脆弱性が検出された場合は終了コード 1
   - 検出されない場合は終了コード 0

---

### 4.4 API詳細（内部関数）

| 項目 | 内容 |
|------|------|
| 関数名 | `simulate_package_scan()` |
| 入力 | `package: &str`, `manager: &str` |
| 出力 | `Vec<Vulnerability>` |
| 説明 | 入力パッケージ名をキーに、脆弱性データベースから該当レコードを返す |

---

### 4.5 テーブル定義

**脆弱性テーブル** (in-memory pseudo-table)

| パッケージ | CVE ID | Severity | Description | Affected Versions |
|-----------|--------|----------|-------------|-------------------|
| litellm | TeamPCP-SUPPLY-CHAIN-001 | CRITICAL | Malicious code injection | 1.82.7, 1.82.8 |
| litellm | CVE-2026-LITELLM-AUTH | HIGH | Credential exposure | <1.82.6 |
| langflow | CVE-2026-33017 | CRITICAL | Auth bypass + Code injection | <0.6.15 |
| @huggingface/transformers | HF-SUPPLY-CHAIN-002 | MEDIUM | Model poisoning | 4.28.0 - 4.30.2 |

---

### 4.6 バリデーション

| 項目 | 条件 | エラーメッセージ |
|------|------|----------------|
| パッケージ名 | 英数字 + @/- のみ | "Invalid package name" |
| severity | CRITICAL \| HIGH \| MEDIUM \| LOW | 自動判定 |

---

### 4.7 例外処理

- **GitHub API エラー**: ローカルデータベース結果のみ出力、警告メッセージを表示
- **空のパッケージ入力**: usage メッセージを表示して終了

---

## 5. 単体テスト

### 5.1 テスト対象

- `simulate_package_scan()` 関数：パッケージ検索ロジック
- Vulnerability struct: severity color mapping
- CLI 引数パース： clap validation

---

### 5.2 テスト環境

| 項目 | 内容 |
|------|------|
| OS | Linux / macOS / Windows |
| 言語 | Rust 1.70+ |
| ツール | cargo test |

---

### 5.3 テストケース

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-01 | litellm スキャン | "litellm" | 2件の脆弱性を検出 |
| UT-02 | langflow スキャン | "langflow" | 1件の CRITICAL 脆弱性を検出 |
| UT-03 | 未知パッケージ | "unknown-pkg" | 脆弱性なし |
| UT-04 | GitHub Advisory フラグ | "-g" オプション | GitHub Advisory メッセージ出力 |

---

### 5.4 境界値テスト

| 項目 | 条件 | 期待結果 |
|------|------|---------|
| 空文字列入力 | `package=""` | エラーメッセージ出力 |
| 特殊文字入力 | `package="<script>alert()</script>"` | サニタイズまたはエラー |

---

### 5.5 異常系テスト

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-E01 | GitHub API タイムアウト | `-g` + API 障害 | ローカル結果のみ表示 |
| UT-E02 | 不正なパッケージ名 | "@@@invalid" | エラーメッセージ表示 |

---

### 5.6 テスト結果

| TC ID | 結果 | 備考 |
|-------|------|------|
| UT-01 | ✅ PASS | litellm 脆弱性検出確認 |
| UT-02 | ✅ PASS | langflow CRITICAL 検出確認 |
| UT-03 | ✅ PASS | 未知パッケージで OK メッセージ |
| UT-04 | ✅ PASS | GitHub Advisory シミュレーション動作 |

---

## 6. 結合テスト

### 6.1 テスト目的

- CLI インターフェース全体の動作確認
- パッケージスキャン + カラー出力 + GitHub Advisory の統合動作

---

### 6.2 テスト範囲

- CLI 引数パース → スキャン → 出力フロー全体

---

### 6.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | Linux (Ubuntu 22.04) |

---

### 6.4 テストシナリオ

| シナリオID | 内容 |
|----------|------|
| IT-01 | threat-monitor litellm を実行し、2件の脆弱性を検出・カラー表示 |
| IT-02 | threat-monitor langflow -g を実行し、脆弱性検出 + GitHub Advisory も表示 |

---

### 6.5 テストケース

| TC ID | シナリオ | 手順 | 期待結果 |
|-------|---------|------|---------|
| IT-01-01 | IT-01 | `./threat-monitor litellm` | CRITICAL (赤), HIGH (オレンジ) で脆弱性表示 |
| IT-02-01 | IT-02 | `./threat-monitor langflow -g` | 脆弱性 + GitHub Advisory シミュレーション出力 |

---

### 6.6 不具合管理

| ID | 内容 | 対応状況 |
|----|------|---------|
| - | 本バージョンで検出無し | ✅ 完了 |

---

## 7. 総合テスト

### 7.1 テスト目的

- エンドユーザが実際に利用する環境での動作確認
- CI/CD パイプライン統合確認

---

### 7.2 テスト範囲

- 全機能（パッケージスキャン、カラー出力、GitHub Advisory）の本番想定環境での動作

---

### 7.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | macOS / Linux / Windows (WSL2) |

---

### 7.4 業務シナリオ

| シナリオID | 内容 |
|----------|------|
| ST-01 | 開発者が本番環境 push 前に threat-monitor で依存パッケージをチェック |
| ST-02 | CI/CD パイプラインで全パッケージを一括スキャン |

---

### 7.5 テストケース

| TC ID | シナリオ | 操作 | 期待結果 |
|-------|---------|------|---------|
| ST-01-01 | ST-01 | threat-monitor litellm 実行 | CRITICAL 脆弱性が赤で警告表示 → パッチが強制 |
| ST-02-01 | ST-02 | for loop で複数パッケージスキャン | 脆弱性が JSON で出力可能（将来） |

---

### 7.6 受入基準

- ✅ CRITICAL 脆弱性の検出・警告表示
- ✅ カラーリング出力の視認性確認
- ✅ GitHub Advisory フラグの動作
- ✅ 本番環境での実行速度 < 1秒

---

### 7.7 テスト結果

| TC ID | 結果 | 備考 |
|-------|------|------|
| ST-01-01 | ✅ PASS | CRITICAL 脆弱性が赤太字で警告 |
| ST-02-01 | ⏳ 将来実装 | JSON 出力機能未実装（v2.0 計画） |
