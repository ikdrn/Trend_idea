# 20260307 — 過去24時間のトレンドまとめ & 本日のシステム開発

## 【過去24時間のトレンドまとめ】

### AI & エージェント / 開発ツール

#### 1. Agentic Coding が主流に — Windsurf Wave 13 / Cursor 2.0 / Kimi Code
- Windsurf Wave 13 が「Arena Mode」（モデルの匿名比較投票）「Plan Mode」「並列マルチエージェントセッション」を搭載し首位を主張
- Cursor 2.0 が最大8エージェント並列、Composer モデル（4倍高速）を発表
- OpenAI Codex がリリース後すぐに Cursor 使用率の60%に到達
- Apple Xcode 26.3 がアジェンティックコーディング対応（Anthropic・OpenAI のエージェントを組み込み）
- Kimi Code が Kimi K2.5 のパートナーツールとして登場（VSCode/Cursor/Zed 対応、マルチエージェント swarm）
- 調査によると開発者の95%が週1回以上 AI ツールを使用、55%が AI エージェントを定期利用

#### 2. GitHub Trending — Elixir/Rust/TypeScript が台頭
- **openai/symphony** (Elixir, 7.4k★) — 「プロジェクト作業を孤立した自律実装ランに変換する」チーム向け AI ワークフロー基盤
- **paperclipai/paperclip** (TypeScript, 4.3k★) — 「ゼロ・ヒューマン・カンパニー」向けオープンソースオーケストレーション
- **nearai/ironclaw** (Rust, 4.3k★) — プライバシーと安全性に特化した OpenClaw インスパイアの実装
- **msitarzewski/agency-agents** (7k★) — 専門エージェントによる完全 AI エージェンシー
- llama.cpp が CPU 推論の速度改善・ハードウェア対応拡張でリリース

#### 3. AI モデル — Qwen 3.5 小型モデルシリーズ発表
- Alibaba が Qwen 3.5 (0.8B/2B/4B/9B) を発表、ネイティブ 262K コンテキスト（最大1Mへ拡張可）
- 「より高い知性、より少ない計算量」— エッジデバイス・軽量エージェント向け
- Meta の「Effective Theory of Wide and Deep Transformers」が ML コミュニティで再注目

### セキュリティ

#### 4. Android 2026年3月セキュリティパッチ — 129件の脆弱性修正
- CVE-2026-21385 が限定的な標的型攻撃に悪用されていると Google が確認
- CVE-2026-0006（System コンポーネント）: ユーザー操作不要のリモートコード実行
- MediaTek 20件・Qualcomm 14件の CVE を含む大規模パッチ
- pKVM サブシステムに複数の特権昇格の脆弱性（CVE-2026-0027〜0031）

#### 5. Cisco SD-WAN ゼロデイ CVE-2026-20127 — CVSS 10.0、2023年から悪用継続
- Cisco Catalyst SD-WAN Controller/Manager の認証バイパス（CVSS 最大値 10.0）
- 未認証の攻撃者がリモートから管理者権限を取得可能
- 2023年から継続的に悪用されていたことが判明
- CISA が緊急指令 26-03 を発令、連邦機関に即時対応を要求

#### 6. ClickFix ソーシャルエンジニアリング — Windows Terminal を悪用
- Microsoft が新たな ClickFix キャンペーンの詳細を公開
- 従来の「Windows Run ダイアログ」ではなく Windows Terminal アプリを悪用
- Lumma Stealer マルウェアを展開する高度な攻撃チェーン

### AI 実装フェーズ（Zenn / 国内エンジニア動向）

#### 7. 「推論モデルの時代」から「実装の時代」へ
- 2025年のパラダイムシフト（RLVR・GRPO）が2026年に企業実装フェーズへ移行
- 銀行顧客サービス・製造プロセス最適化・医療診断補助での導入事例増加
- 「最適化スケーリング」— 推論時間増加ではなく計算効率と精度のバランスを最適化
- マルチモーダル推論（画像・音声・ビデオ）が本格化

#### 8. 開発環境 2026 — マルチエージェント並列開発スタイルが浸透
- Git worktree + tmux での複数エージェント同時実行が標準化
- Claude Code Agent Teams（リサーチプレビュー）が注目
- Google Antigravity（元 Windsurf チームによる自社 IDE）が登場

### Product Hunt

#### 9. Anything API / NOVA — ブラウザタスクの API 化、コーディングループ自動化
- **Anything API** (Notte): 公開 API のないサイトのブラウザ操作を呼び出し可能な API に変換
- **NOVA**: 「実行→失敗→修正→繰り返し」のコーディングループを自動化
- **OpenClaw for Teams**: チーム向け AI アシスタント管理基盤

---

## 【参照 URL 一覧】

| # | タイトル | URL |
|---|---------|-----|
| 1 | GitHub Trending (Trendshift) | https://trendshift.io/ |
| 2 | openai/symphony (GitHub) | https://github.com/openai/symphony |
| 3 | nearai/ironclaw (GitHub) | https://github.com/nearai/ironclaw |
| 4 | Xcode 26.3 Agentic Coding (Apple) | https://www.apple.com/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/ |
| 5 | 2026 Agentic Coding Trends Report (Anthropic) | https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf |
| 6 | Cursor 2.0 Update (CNBC) | https://www.cnbc.com/2026/02/24/cursor-announces-major-update-as-ai-coding-agent-battle-heats-up.html |
| 7 | AI Dev Tool Power Rankings Feb 2026 (LogRocket) | https://blog.logrocket.com/ai-dev-tool-power-rankings/ |
| 8 | Android March 2026 Security Patch (Help Net Security) | https://www.helpnetsecurity.com/2026/03/03/android-march-2026-security-patch-cve-2026-21385/ |
| 9 | CVE-2026-21385 Exploitation Confirmed (The Hacker News) | https://thehackernews.com/2026/03/google-confirms-cve-2026-21385-in.html |
| 10 | Cisco SD-WAN Zero-Day CVE-2026-20127 (The Hacker News) | https://thehackernews.com/2026/02/cisco-sd-wan-zero-day-cve-2026-20127.html |
| 11 | March 2026 Patch Tuesday Forecast (Help Net Security) | https://www.helpnetsecurity.com/2026/03/06/march-2026-patch-tuesday-forecast/ |
| 12 | 2026年のAIトレンド記事 (Zenn) | https://zenn.dev/7788/articles/af11fbce6c3379 |
| 13 | 開発環境2026年 (Zenn) | https://zenn.dev/pura/articles/c33a0aec7ff339 |
| 14 | Product Hunt March 2026 | https://www.producthunt.com/leaderboard/daily/2026/3/4 |
| 15 | Hacker News Front Page | https://news.ycombinator.com/front |

---

## 【本日のシステムアイデア】

### アイデアの着想プロセス

今日のトレンドを眺めると、2つの強い潮流が浮かび上がった。

**潮流 A — AI エージェントの並列オーケストレーション**
Windsurf の「複数エージェント並列セッション」、Cursor の「8エージェント同時実行」、openai/symphony の「孤立した自律実装ランの管理」——いずれも「複数の AI エージェントが役割分担して問題を解く」パラダイムが2026年の中心にある。

**潮流 B — セキュリティパッチの爆増と手動トリアージの限界**
Android 129件、Cisco CVSS 10.0、Microsoft 59件——毎月押し寄せる CVE の海をセキュリティチームが手動でトリアージするのはすでに限界に近い。

**掛け合わせ**:
「マルチエージェントアーキテクチャ」×「CVE トリアージ自動化」= エージェントが役割分担して脆弱性の優先度付けを行うシミュレーター

**言語選定理由（Rust）**:
GitHub Trending で `nearai/ironclaw`（Rust, セキュリティ特化）が急上昇中。Rust はメモリ安全性・並行性でセキュリティツールと親和性が高く、本リポジトリで未使用の言語のため採用。

---

### 本日のシステム: `vulntriage` — マルチエージェント CVE 優先度付け CLI

#### システム概要

CVE データ（CVSS スコア・影響範囲・悪用状況）を内蔵データから読み込み、3つの専門エージェント（Analyzer / Scorer / Reporter）が並列処理でトリアージを実行する CLI シミュレーター。

- **Analyzer エージェント**: CVE の影響コンポーネントと攻撃ベクターを解析
- **Scorer エージェント**: CVSS スコア + 悪用情報 + 影響システム数を組み合わせてリスクスコアを算出
- **Reporter エージェント**: トリアージ結果を優先度別（CRITICAL / HIGH / MEDIUM）にレポート出力

実際の外部 API は使わず、内蔵サンプル CVE データ（本日の実際の CVE に基づく）で動作確認できる。

#### 技術選定の理由

- **Rust**: `nearai/ironclaw`（セキュリティ×Rust）が GitHub Trending 急上昇中。所有権モデルによるメモリ安全性はセキュリティツールに最適。`std::thread` + `std::sync::mpsc` でマルチエージェント並列処理を外部依存なしに実現
- **外部依存ゼロ**: 標準ライブラリのみで完結、インターネット接続不要

#### 動作イメージ

```
$ cargo run

=== VulnTriage — Multi-Agent CVE Triage System ===
Date: 2026-03-07

[Analyzer]  CVE-2026-20127 | Vector: Network | Auth: None  | Component: Cisco SD-WAN
[Analyzer]  CVE-2026-21385 | Vector: Local   | Auth: None  | Component: Qualcomm/Android
[Analyzer]  CVE-2026-0006  | Vector: Network | Auth: None  | Component: Android System
[Analyzer]  CVE-2026-0037  | Vector: Local   | Auth: Low   | Component: Android pKVM
[Analyzer]  CVE-2026-0031  | Vector: Local   | Auth: Low   | Component: Android pKVM

[Scorer]    CVE-2026-20127 | CVSS:10.0 | Exploited:YES | Affected:45000 | RiskScore:100
[Scorer]    CVE-2026-0006  | CVSS: 9.8 | Exploited:NO  | Affected:92000 | RiskScore: 88
[Scorer]    CVE-2026-21385 | CVSS: 7.8 | Exploited:YES | Affected:31000 | RiskScore: 75
[Scorer]    CVE-2026-0037  | CVSS: 7.0 | Exploited:NO  | Affected:18000 | RiskScore: 52
[Scorer]    CVE-2026-0031  | CVSS: 6.5 | Exploited:NO  | Affected:18000 | RiskScore: 46

=== [Reporter] Triage Report 2026-03-07 ===

CRITICAL (RiskScore >= 90):
  [!!!] CVE-2026-20127 | CVSS=10.0 | Cisco SD-WAN認証バイパス — 即時パッチ (CISA ED 26-03)
  [!!!] CVE-2026-0006  | CVSS= 9.8 | Android RCE無認証 — 3月パッチ最優先適用

HIGH (RiskScore 70-89):
  [!]   CVE-2026-21385 | CVSS= 7.8 | Qualcomm Android 悪用確認済 — 早急対応推奨

MEDIUM (RiskScore < 70):
  [ ]   CVE-2026-0037  | CVSS= 7.0 | Android pKVM 特権昇格 — 計画的対応
  [ ]   CVE-2026-0031  | CVSS= 6.5 | Android pKVM 特権昇格 — 計画的対応

Summary: 5 CVEs | CRITICAL: 2 | HIGH: 1 | MEDIUM: 2
Triage completed (3 agents, parallel execution)
```

#### セットアップ & 実行（3ステップ）

```bash
# 1. ディレクトリに移動
cd 20260307/src/vulntriage

# 2. ビルド & 実行
cargo run

# (任意) リリースビルドで高速実行
cargo run --release
```

前提: Rust ツールチェーン（rustc 1.70+）がインストール済みであること。
インストールは `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh` で可能。
