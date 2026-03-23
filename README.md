# Trend_idea

このリポジトリは、**毎日のトレンド調査**と、そこから作る**小さなシステム試作**を記録する場所です。

非エンジニアの方でも追いやすいように、まずは以下の2つだけ覚えればOKです。

- `CLAUDE.md`：**毎日の作業手順書**（どう進めるか）
- `YYYYMMDD/readme.md`：**その日の成果物メモ**（何を調べて何を作ったか）

---

## 過去の実施記録（履歴）

> これまで `CLAUDE.md` にあった履歴を、ここ（ルート README）へ移動しました。

| 日付 | カテゴリ | 言語/FW | システム名 | 主なトレンド | 成果ディレクトリ |
|------|---------|---------|-----------|------------|------------------|
| 20260227 | [D] セキュリティ／ネットワーク | Python | `ai-repo-auditor` | Claude Code RCE (CVE-2025-59536)、OpenClaw/ClawHavoc | `20260227/` |
| 20260228 | [H] AIインテグレーション | Python | `mini-deerflow` | ByteDance DeerFlow 2.0、Google TimesFM、PicoLM | `20260228/` |
| 20260301 | [A] フロントエンドUI | Vanilla JS | `csi-motion-detector` | wifi-densepose (GitHub Trending #1)、Claude in Excel (PH #1)、Cisco SD-WAN CISA緊急指令 | `20260301/` |
| 20260302 | [B] フルスタックWebアプリ | Node.js + Express | `ai-red-lines` | Anthropic Pentagon 追放・AI レッドライン、FortiGate 600 台 AI 支援攻撃、Deno v2.7 / TypeScript #1 | `20260302/` |
| 20260303 | [C] CLIツール | Go | `trend-mixer-cli` | AIエージェント運用の継続注目、セキュリティ優先度整理、Trending可視化需要 | `20260303/` |
| 20260305 | [D] セキュリティ／ネットワーク | Python | `ThreatPulse` | MacBook Neo $599、Cisco CVE-2026-20127 CVSS 10.0、ハクティビスト DDoS 149件、Wi-Fi センシング（RuView） | `20260305/` |
| 20260307 | [C] CLIツール | Rust | `vulntriage` | Windsurf/Cursor マルチエージェント並列開発、nearai/ironclaw Rust セキュリティ、Android 129件 CVE パッチ | `20260307/` |
| 20260309 | [D] セキュリティ／ネットワーク | Python | `AgentAudit` | Agent Safehouse (HN Top)、MCP2CLI、Anthropic×Firefox 22件脆弱性発見、NIST AI エージェントセキュリティ | `20260309/` |
| 20260319 | [E] データ可視化 | Vanilla JS (Canvas API) | `gravity-playground` | HN「三体問題ブラウザシミュレーター」急上昇、GitHub Trending newton-physics/newton、claude-hud 1851★/day | `20260319/` |
| 20260321 | [H] AIインテグレーション | Node.js + Express | `agentic-trend-classifier` | Google Sashiko (Agentic AI Code Review)、NemoClaw/OpenClaw 210k+ stars、Product Hunt AI Agents支配、CVE-2026-3888 Ubuntu systemd | `20260321/` |
| 20260322 | [F] ブラウザ拡張 / ユーザースクリプト | Manifest V3 (JavaScript) | `PackageGuard` | GlassWorm サプライチェーン攻撃（VSX/npm 72拡張悪用）、North Korean npm パッケージ RAT、Anthropic Claude Firefox 脆弱性自動検出 | `20260322/` |
| 20260323 | [A] フロントエンドUI | Svelte + TypeScript | `AgentMonitor` | TradingAgents（マルチエージェント LLM 金融取引）、pentagi（自動ペネテスト）、everything-claude-code（エージェント最適化 98k+ ⭐） | `20260323/` |

---

## 使い方（かんたん版）

1. 今日の日付フォルダ（例：`20260303/`）を開く
2. `readme.md` を読むと、その日の調査内容とアイデアがわかる
3. `src/` に動くコード、`docs/` に補足資料がある

