# 20260315 — patch-pulse: March 2026 CVE Landscape Visualizer

## 本日のスタック選定
- カテゴリ: [E] データ可視化
- 言語/FW: D3.js v7 + Vanilla JS + HTML/CSS
- 選定理由: Microsoft Patch Tuesday (2026-03-10) で83件CVEが公開、n8n CVE-2026-21858 (CVSS 10.0) が~10万サーバーを直撃、さらにCISA KEVがChromium V8/Skia フローを追加。セキュリティデータが爆発的に増えたタイミングで可視化需要が高まっており、Eカテゴリ（データ可視化）が最適。直近でEは未使用のため選定。
- 実行方法: `src/index.html` をブラウザで開く（CDN経由でD3.js読み込み、ローカルサーバー不要）

---

## 収集トレンド

### Hacker News
- タイトル: Making WebAssembly a first-class language on the Web
- URL: https://news.ycombinator.com/front?day=2026-03-12
- 概要: WASM をブラウザの第一級言語として扱う提案がHN上位。Web標準の転換点として議論が加速。

- タイトル: 1M context is now generally available for Opus 4.6 and Sonnet 4.6
- URL: https://claude.com
- 概要: Claude 4.6 Opus / Sonnet の1Mトークンコンテキストウィンドウが一般公開。154点・434コメントで大きな反響。

- タイトル: After outages, Amazon to make senior engineers sign off on AI-assisted changes
- URL: https://news.ycombinator.com/front?day=2026-03-10
- 概要: AI生成コードによる本番障害を受け、Amazonがシニアエンジニアのレビュー必須化を導入。AIコード信頼性の議論が再燃。

### Reddit (r/netsec / r/devops)
- タイトル: ni8mare — Unauthenticated RCE in n8n (CVE-2026-21858)
- URL: https://www.cyera.com/research/ni8mare-unauthenticated-remote-code-execution-in-n8n-cve-2026-21858
- 概要: 人気ワークフロー自動化ツール n8n に CVSS 10.0 の認証不要RCE。約10万サーバーが脆弱。

- タイトル: Microsoft March 2026 Patch Tuesday: 83 CVEs including PrintNightmare-style bug
- URL: https://securityboulevard.com/2026/03/microsofts-march-2026-patch-tuesday-addresses-83-cves-cve-2026-21262-cve-2026-26127/
- 概要: EoP55%・RCE21%の内訳。印刷スプーラー再来(CVE-2026-23669)、OfficeプレビューRCE(CVE-2026-26110/26113)が特に危険。

### GitHub Trending
- タイトル: n8n — Workflow automation
- URL: https://github.com/n8n-io/n8n
- 概要: CVE公開後に逆に注目が集まり GitHub Trending 入り。400+ インテグレーション、AIネイティブ対応。

- タイトル: OpenClaw — Local AI assistant
- URL: https://github.com/trending
- 概要: ローカルAIアシスタント。210,000+スター。全データがローカル処理、50+インテグレーション対応。Cisco供給チェーン攻撃の脆弱性も発覚。

### セキュリティブログ (The Hacker News / CISA)
- タイトル: CISA KEV Adds Critical Skia and Chromium V8 Flaws (CVE-2026-3909, CVE-2026-3910)
- URL: https://windowsforum.com/threads/cisa-kev-adds-critical-skia-and-chromium-v8-flaws-cve-2026-3909-cve-2026-3910-patch-now.405045/
- 概要: 2026-03-13 にCISA KEVへ追加。V8エンジンのメモリ破壊は実環境で悪用確認済み。全連邦機関に即時パッチ適用義務。

- タイトル: Broadcom VMware Aria Operations CVE-2026-22719 added to CISA KEV
- URL: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- 概要: VMware Aria Operations のコマンドインジェクション。CISA KEV 掲載、期限 2026-03-24。

### Product Hunt
- タイトル: Windsurf Arena Mode — Side-by-side AI model comparison
- URL: https://www.producthunt.com
- 概要: AI開発ツール Windsurf がArena Modeを発表。2つのモデルを匿名比較・投票する機能。

---

## 本日のアイデア

- 組み合わせたトレンド:
  1. Microsoft Patch Tuesday 83 CVEs (2026-03-10) — セキュリティの大量データ
  2. n8n CVE-2026-21858 (CVSS 10.0) — 単体で世界的インシデント規模
  3. CISA KEV Chromium V8/Skia 追加 — ブラウザ脅威の可視化需要
  4. AI dev tools power rankings 急変 — セキュリティツールのデータドリブン需要

- システム概要:
  **patch-pulse** — インタラクティブ CVE ランドスケープ可視化ダッシュボード。
  3月Patch Tuesday の83件CVEと注目脆弱性を D3.js でリアルタイム可視化。
  ドーナツチャート（タイプ別分布）・スキャッタープロット（製品×CVSSスコア）・バブルチャート（タイプ×平均CVSS）・フィルタブルCVEテーブルを提供。
  実環境悪用済み・CISA KEV掲載CVEを視覚的に強調表示。

- スコープ:
  - 外部APIキー不要（データはJSファイルに内包）
  - ブラウザで `index.html` を開くだけで即起動
  - D3.js はCDN経由
  - レスポンシブ対応（Grid CSS + viewBox スケーリング）

---

## 実装メモ

- 工夫した点:
  - CVSS スコアに応じてカラーグラデーション（赤10.0 → 緑7.0）をD3で計算
  - バブルチャートはバブルサイズ＝件数（平方根スケール）でCVEタイプの重みを視覚化
  - ツールチップはビューポート端でのはみ出しを防ぐ計算式を実装
  - フィルターボタン（全表示/Critical/実環境悪用/CISA KEV）でテーブルを動的切り替え
  - モジュール形式（ESモジュール）で data.js / main.js を分離
  - ダークモード専用配色（GitHubインスパイア）

- 今後の拡張案:
  - NVD API連携でリアルタイムCVEデータフェッチ
  - 週次トレンドの折れ線グラフ追加
  - CVSSv4.0 スコアへの対応（v3.1 → v4.0 移行期）
  - EPSS（Exploit Prediction Scoring System）スコアの組み込み
  - Shodan APIと連携して脆弱製品の公開サーバー数を表示
