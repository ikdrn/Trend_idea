# 20260302 — 過去24時間のトレンドまとめ & 本日のシステム開発

> 取得日時: 2026-03-02
> 対象期間: 過去24時間以内に公開・話題になった情報のみ

---

## 【過去24時間のトレンドまとめ】

### 🏛️ AI 政策・ガバナンス — Anthropic Pentagon 追放が世界を震撼

#### 1. Trump、全連邦機関に Anthropic の使用禁止を命令（最大のニュース）
- **概要**: トランプ大統領が Truth Social に投稿し、全連邦機関に Anthropic の技術の即時使用停止を命じた。Hegseth 国防長官が Anthropic を「国家安全保障へのサプライチェーンリスク」に指定——通常は中国・ロシアなど外国敵対勢力にのみ使用される極めて重い指定。
- **原因**: Anthropic が「自律型兵器への AI 利用禁止」「米国市民の大量監視への AI 利用禁止」という利用規約上の「レッドライン」を Pentagon に課そうとしたことへの反発。Pentagon は「すべての合法的用途に使える」ことを契約条件とし、交渉が決裂。
- **Anthropic の反応**: 「直接通知を受けていない。指定を法廷で争う。現役の AI モデルが完全自律型兵器に使えるほど信頼性が高いとは言えない」と声明。
- **余波**: 多くの AI 企業幹部が Anthropic 側を支持。なお U.S. Central Command は禁止命令が出た後も Claude を標的識別・戦闘シミュレーションに使用継続中と WSJ が報道。

#### 2. OpenAI、Pentagon 追放から数時間後に国防総省と契約締結
- OpenAI CEO の Sam Altman が Anthropic 禁止の数時間後に Pentagon との秘密ネットワーク向け AI 契約を発表。Altman 自身が「急いで締結した、見栄えがよくない」と認める。
- OpenAI も「自律型兵器・大量監視・高リスク自動意思決定への使用は禁止」というレッドラインを設定し「多層的なアプローチで保護する」と主張するが、同じレッドラインを持ちながら契約した点で批判を受けている。

---

### 📡 GitHub Trending — TypeScript / Rust が躍進

#### 3. system-prompts-collection — GitHub Trending 急上昇（TypeScript/Markdown）
- 主要 AI コーディングツール（Cursor・Claude Code・Windsurf・NotionAI 等）の内部システムプロンプトと隠し指示を収集・公開したリポジトリが急浮上。「ブラックボックスな AI ツールの中身を覗きたい」開発者の関心が爆発。

#### 4. bytebot/bytebot — 自己ホスト型 AI デスクトップエージェント（TypeScript, 14.2k⭐）
- Docker コンテナで動作する AI デスクトップエージェント。ブラウザ操作・ファイル管理・コード実行を自律実行。Apache 2.0 ライセンスで完全自己ホスト可能。TypeScript + VNC over noVNC の構成。

#### 5. RuVector — Rust 製ベクトル + グラフ DB（Rust, 8.1k⭐）
- HNSW（Hierarchical Navigable Small World）アルゴリズムによる高速ベクトル検索 + グラフインテリジェンスを組み合わせた Rust 製 DB。AI エージェントの記憶バックエンドとして注目。

---

### 🛍️ Product Hunt — AI ソーシャルメディア管理・収益分析

#### 6. PostSyncer — AI コンテンツメーカー × ソーシャルメディア自動公開（PH 上位）
- AI が複数 SNS 向けの投稿を自動生成・スケジューリング・公開まで一気通貫で実行。

#### 7. DataFast — 収益ファーストの分析ツール（PH 上位）
- SaaS 向けリアルタイム収益分析。MRR・チャーン・LTV を一画面で可視化。

---

### 🔐 セキュリティ — AI 悪用・旧型ルーター・PDF ゼロデイ

#### 8. AI 支援型サイバー攻撃が FortiGate 600 台超を侵害（Amazon Threat Intelligence）
- 1 月〜2 月にかけ、技術力が低い脅威アクターが **Anthropic Claude と DeepSeek を利用して攻撃計画を立案・コマンド生成**し、55 ヵ国 600 台超の FortiGate デバイスを侵害。管理ポートの露出と弱い認証情報を突いた攻撃。「AI で攻撃コストが劇的に下がった」実証例として注目。

#### 9. D-Link EOL ルーター RCE CVE-2026-0625 が現在進行形で悪用中
- EOL モデル（DSL-526B 等）の `dnscfg.cgi` エンドポイントに未認証 RCE。パッチなし。FBIが「ルーターをボットネット化して代理ネットワークに使用」と警告継続中。

#### 10. Chrome 拡張機能マルウェアが 90 万ユーザーの AI チャット履歴を流出
- 悪意ある Chrome 拡張が AI チャットボット（ChatGPT・Claude 等）との会話内容・ブラウジングデータを窃取。Ox Security が数ヵ月分の被害を確認。

#### 11. Foxit PDF SDK に OS コマンドインジェクション（CVSS 9.8）他 16 件
- Foxit PDF SDK for Web の Node.js サーバーで `process.execSync()` に無検証でパラメータを渡す致命的実装。未認証の単一 POST リクエストで RCE 達成可能。Foxit はパッチ済み。

---

### 🤖 AI & ツール — Deno 2.7 リリース・TypeScript ファースト

#### 12. Deno v2.7 リリース（2026-02-25）
- Deno 2.7 が公開。`deno audit` コマンド（依存関係を GitHub CVE DB でスキャン）、TLS キーロギング、`--compile` フラグ強化。TypeScript ファーストな開発体験がさらに磨かれた。

#### 13. Zenn「TypeScript the Minimum: Deno で始めるミニマム TypeScript」が継続人気
- `tsconfig.json` も `npm install` も不要で即 TypeScript が使える Deno の入門書が Zenn でトレンド継続。TypeScript が GitHub 言語ランキング #1 になった流れと呼応。

#### 14. はてなブックマーク「AI が 600 台の FortiGate を侵害——防御側への教訓」
- AI を使った攻撃の具体的手法と防御策（MFA・管理ポートを VPN 内に限定・EOL デバイス廃棄）が技術者コミュニティで話題。

---

## 【参照URL一覧】

| # | タイトル | URL |
|---|--------|-----|
| 1 | OpenAI strikes deal with Pentagon after Trump bans Anthropic — NBC News | https://www.nbcnews.com/tech/tech-news/trump-bans-anthropic-government-use-rcna261055 |
| 2 | Hegseth declares Anthropic a supply chain risk — CBS News | https://www.cbsnews.com/news/hegseth-declares-anthropic-supply-chain-risk/ |
| 3 | OpenAI reveals more details about its Pentagon agreement — TechCrunch | https://techcrunch.com/2026/03/01/openai-shares-more-details-about-its-agreement-with-the-pentagon/ |
| 4 | Trump orders agencies to stop using Anthropic — Federal News Network | https://federalnewsnetwork.com/artificial-intelligence/2026/02/anthropic-refuses-to-bend-to-pentagon-on-ai-safeguards-as-dispute-nears-deadline/ |
| 5 | GitHub Trending — trending repositories | https://github.com/trending |
| 6 | Product Hunt — March 2, 2026 | https://www.producthunt.com/leaderboard/daily/2026/3/2 |
| 7 | AI-Assisted Threat Actor Compromises 600+ FortiGate Devices — The Hacker News | https://thehackernews.com/2026/02/ai-assisted-threat-actor-compromises.html |
| 8 | D-Link RCE CVE-2026-0625 — GovInfoSecurity | https://www.govinfosecurity.com/breach-roundup-firewalls-headed-for-obsolesce-a-30472 |
| 9 | ThreatsDay Bulletin: OpenSSL RCE, Foxit 0-Days — The Hacker News | https://thehackernews.com/2026/02/threatsday-bulletin-openssl-rce-foxit-0.html |
| 10 | Deno v2.7 Release Notes | https://github.com/denoland/deno/releases/tag/v2.7.0 |
| 11 | Deno 2.6: dx is the new npx — Deno Blog | https://deno.com/blog/v2.6 |
| 12 | TypeScript the Minimum: Deno で始めるミニマム TypeScript — Zenn | https://zenn.dev/estra/books/ts-the-minimum |
| 13 | CISA Flags Four Security Flaws Under Active Exploitation — The Hacker News | https://thehackernews.com/2026/02/cisa-flags-four-security-flaws-under.html |
| 14 | Hacker News Front Page | https://news.ycombinator.com/front |
| 15 | Hunted.space — Product Hunt Launch History | https://hunted.space/history |

---

## 【本日のシステムアイデア】

### アイデアの着想プロセス

本日のトレンドを横断すると、1 つの強烈なテーマが浮かび上がる：

1. **Anthropic の「レッドライン」と Pentagon の衝突** — Anthropic が「自律型兵器に AI を使ってはならない」「市民の大量監視に使ってはならない」というレッドラインを設け、Pentagon に受け入れを迫った。これは「AI の利用ポリシーをコードとして定義し、強制する」という発想そのもの。

2. **AI が攻撃に悪用されている** (FortiGate 600 台侵害) — 攻撃者が Claude・DeepSeek を使って攻撃計画を立案。AI の「使われ方」の監査が急務になっている。

3. **Deno v2.7 + TypeScript #1** — TypeScript が GitHub 言語ランキング 1 位になり、Deno 2.7 が新鮮なリリースとして登場。Python 以外の言語で CLI ツールを作る最高のタイミング。

掛け合わせると：「**Anthropic のレッドライン精神を、Deno/TypeScript の CLI ツールとして実装する**」——ソースコードを走査して AI ベンダーの API 呼び出しを検出し、ユーザー定義の利用ポリシー（レッドライン）に違反していないかチェックするコンプライアンス監査ツール。

---

### 本日のシステム: `ai-red-lines` — AI 利用ポリシー準拠チェッカー

#### システム概要
ソースコードを走査して AI ベンダー SDK の利用パターンを検出し、JSON で定義した「レッドライン（使用禁止ポリシー）」に準拠しているかを確認する **Deno/TypeScript CLI ツール**。

- **AI SDK 検出**: `@anthropic-ai/sdk`・`openai`・`@google/generative-ai` 等のインポート、モデル名文字列、API エンドポイント参照を正規表現で検出
- **ポリシー評価エンジン**: JSON 形式のポリシーファイルで禁止パターンを定義（CRITICAL/HIGH/MEDIUM/LOW の 4 段階）
- **カラーコード出力**: 🔴 CRITICAL / 🟡 HIGH / 🟢 PASS を ANSI カラーで一覧表示
- **JSON 出力対応**: CI/CD 連携のため `--json` フラグでマシン可読な結果を出力
- **デモモード**: `--demo` フラグで内蔵サンプルコードをスキャンし、即座に動作確認

#### 技術選定の理由
- **Deno/TypeScript**: Python 連続を脱却し、v2.7 がリリースされたばかりの最新 Deno を採用。`deno run --allow-read main.ts` の 1 コマンドで依存インストール不要で動作。TypeScript の型安全性で政策ルールの構造を明確に表現。
- **ゼロ外部依存**: Deno 組み込み API のみ使用。`policy.json` の差し替えだけで企業ごとのポリシーに対応可能。
- **「Policy as Code」思想**: Anthropic のレッドライン文書を JSON として形式化した例が標準同梱。組織が AI 利用ポリシーをコードとして管理・バージョン管理できる。

#### 動作イメージ

```
$ deno run --allow-read src/main.ts --demo

ai-red-lines v1.0 — AI Usage Policy Compliance Checker
Inspired by: Anthropic "red lines" stance (2026-02-27 Pentagon dispute)
Policy: AI Usage Policy — Red Lines v1.0  (5 rules loaded)
Scanning: [demo mode]  (2 virtual files)

────────────────────────────────────────────────────────────────────
 File: samples/risky_app.ts
────────────────────────────────────────────────────────────────────
  [CRITICAL] NO_AUTONOMOUS_WEAPONS — Line 14
    → AI models must not be used for fully autonomous weapons targeting
    → Matched: "autonomousTargetSelection(model: claude-3-7-sonnet)"

  [HIGH]     NO_MASS_SURVEILLANCE — Line 31
    → AI models must not power mass surveillance of civilians
    → Matched: "bulkSurveillanceEndpoint"

  [MEDIUM]   NO_HARDCODED_KEYS — Line 5
    → API keys must not be hardcoded in source files
    → Matched: "sk-ant-api03-XXXXXXXXXXXX"

────────────────────────────────────────────────────────────────────
 File: samples/safe_app.ts
────────────────────────────────────────────────────────────────────
  ✓ No policy violations found

────────────────────────────────────────────────────────────────────
 Summary
────────────────────────────────────────────────────────────────────
  Files scanned:   2
  Total findings:  3  (1 CRITICAL, 1 HIGH, 1 MEDIUM)
  Compliant files: 1 / 2

  Result: ✗ POLICY VIOLATION DETECTED — review required
```

#### 実行方法

```bash
# bun インストール（未インストールの場合）
curl -fsSL https://bun.sh/install | bash

# デモモードで即動作確認
bun src/main.ts --demo

# ディレクトリを指定してスキャン
bun src/main.ts /path/to/project

# カスタムポリシーを指定
bun src/main.ts --policy src/policy.json /path/to/project

# JSON 出力（CI/CD 向け）
bun src/main.ts --json --demo | python3 -m json.tool
```

> **注**: Deno と bun はどちらも TypeScript ネイティブランタイム。Deno 2.7 がリリースされた直後のタイミングで、互換 API を使って実装。`bun src/main.ts` で設定ゼロで動作する。
