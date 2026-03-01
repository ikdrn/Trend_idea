# 20260301 — 過去24時間のトレンドまとめ & 本日のシステム開発

> 取得日時: 2026-03-01
> 対象期間: 過去24時間以内に公開・話題になった情報のみ

---

## 【過去24時間のトレンドまとめ】

### 📡 GitHub Trending — WiFi で壁越し人体追跡が爆発的バズ

#### 1. ruvnet/wifi-densepose — GitHub Trending デイリー #1 (7.7k⭐)
- **概要**: WiFi 信号の CSI（Channel State Information: チャネル状態情報）を解析して、カメラ不要で壁越しに人体の全身ポーズをリアルタイム追跡するシステム。Carnegie Mellon の 2023 年研究 (InvisPose) を Rust で実装した本番品質版。
- **精度**: 94.2% のカメラ同等精度。30fps・レイテンシ 50ms 以下。最大 10 人同時追跡。
- **技術**: WiFi ルーター 3 台の送受信局ペアで 30周波数・150×3×3 テンソルを生成 → 改造 DensePose-RCNN が人体領域 24 ヶ所を推定。Rust コアで 800 倍高速化。
- **用途**: プライバシー保護型見守り（映像なし）・災害救助（瓦礫越しの生存者探知）・病院での非接触患者モニタリング。
- **注目点**: 画像・映像を一切記録しない「ゼロビジュアルデータ」で HIPAA 準拠という逆転の発想。

#### 2. VoltAgent/awesome-openclaw-skills (21.8k⭐) · hesamsheikh/awesome-openclaw-usecases (10.9k⭐)
- OpenClaw のスキルレジストリ・ユースケース集が急増。月間スター数は obra/superpowers (64.2k⭐) と並んでエージェントスキルエコシステムが確立フェーズに。

---

### 🛍️ Product Hunt — AI が Excel に上陸・PR レビュー自動化

#### 3. Claude in Excel — Product Hunt デイリー #1 (1,025 upvotes)
- Excel アドイン。スプレッドシートを開いたまま Claude とチャット → 数式生成・データ整形・分析を自然言語で操作可能。「普段使いのツールに AI が溶け込む」トレンドの象徴。

#### 4. Kilo Code Reviewer — Product Hunt #2 (836 upvotes)
- PR をオープンした瞬間に AI コードレビューを自動実行するツール。GitHub Actions / GitLab CI と統合。オープンソース・無料プランあり。

#### 5. Moltbot — "The AI that actually does things" (584 upvotes)
- 「実際に作業をこなす AI」。タスクを与えると自律的にブラウザ操作・コード実行・ファイル管理を実行。OpenClaw の競合に位置づけ。

#### 6. ShapedQL (224 upvotes)
- 検索・フィード・AI エージェント向けの SQL エンジン。クエリをベクトル類似度検索・ランキング・パーソナライズと組み合わせて実行可能。

---

### 🔐 セキュリティ — Chrome ゼロデイ・Cisco 緊急指令・OpenClaw ClawJacked

#### 7. Chrome Zero-Day (CVE-2026-2441) — 現在進行形の攻撃
- Chrome の V8 エンジンに未初期化メモリ参照の脆弱性。すでに野良エクスプロイトを確認。Google はパッチをリリース済みだが適用率が低く攻撃継続中。

#### 8. Cisco SD-WAN 認証バイパス → CISA 緊急指令 26-03
- Cisco Catalyst SD-WAN Controller / Manager のピアリング認証機構の不備により、未認証リモートから管理者権限を取得可能。CISA が Emergency Directive 26-03 を発令し連邦機関に即時パッチを義務付け。

#### 9. OpenClaw "ClawJacked" 脆弱性 (Oasis Security)
- ローカルで動作する OpenClaw エージェントに悪意ある Web サイトから接続・制御できる高リスク脆弱性。修正版リリース済みだがパッチ未適用インスタンスが多数残存。

#### 10. Match Group (Hinge/OkCupid) 1,000 万件超データ漏洩
- ShinyHunters グループが 1,000 万件超のユーザーレコードを窃取したと主張。ソーシャルエンジニアリング経由で Okta SSO を侵害後にデータ抽出。

#### 11. 北朝鮮 ScarCruft "Ruby Jumper" キャンペーン
- Zoho WorkDrive を C2 通信に悪用するバックドア + 気密ネットワーク侵入のリムーバブルメディア型インプラントを展開。複数マルウェアファミリを組み合わせた高度な諜報キャンペーン。

#### 12. Google Cloud API キー 3,000 件がクライアントコードに露出
- 研究者がクライアントサイドコードに埋め込まれた Google API キーを約 3,000 件発見。これらを悪用して Gemini エンドポイントに認証しプライベートデータにアクセス可能と報告。

---

### 🤖 AI & ツール — Fireship が ui.dev と合流・内製 AI エージェント

#### 13. Fireship × ui.dev 合流 (X で大きな反響)
- 人気 YouTube チャンネル Fireship (410 万 ch) が ui.dev と合流を発表。「100 Seconds of Code」「Code Report」シリーズ継続・チーム拡大で制作本数増加予定。バーンアウト防止が理由。

#### 14. Zenn 「Build, Don't Buy — 2026年、AIエージェントは内製する時代へ」
- ノーコードツールでの AI 内製化が競争優位の鍵。受託開発はモデル切り替えに数週間かかる一方、内製なら数時間で本番反映。国内大手でも内製 AI により業務時間 70% 削減の事例。

#### 15. はてなブックマーク 「2026年 AI Coding Agent 活用 ── スピードと安全性を両立」
- Zenn 公式記事。Claude Code・Codex CLI・GitHub Copilot・Cursor を横断比較し、AI エージェントで「1.5〜3倍の生産性向上」を達成するための実践的なガイドが話題。

---

## 【参照URL一覧】

| # | タイトル | URL |
|---|--------|-----|
| 1 | GitHub - ruvnet/wifi-densepose | https://github.com/ruvnet/wifi-densepose |
| 2 | WiFi DensePose Tutorial: Track Poses Through Walls 2026 | https://byteiota.com/wifi-densepose-tutorial-track-poses-through-walls-2026/ |
| 3 | WiFi DensePose: See Through Walls with WiFi Signals and Rust — YUV.AI | https://yuv.ai/blog/wifi-densepose |
| 4 | GitHub Trending Daily 2026-02-25 — sejiwork | https://sejiwork.com/en/blog/post/github-trending-daily-2026-02-25 |
| 5 | Trendshift — Open-Source Repository Trends | https://trendshift.io/ |
| 6 | Product Hunt — March 1, 2026 Daily Leaderboard | https://www.producthunt.com/leaderboard/daily/2026/3/1 |
| 7 | Hunted.space — Product Hunt Launch History | https://hunted.space/history |
| 8 | Chrome Zero-Day CVE-2026-2441 — The Hacker News | https://thehackernews.com/ |
| 9 | CISA Emergency Directive 26-03 — Cisco SD-WAN | https://www.cisa.gov/known-exploited-vulnerabilities-catalog |
| 10 | OpenClaw ClawJacked Vulnerability — Oasis Security | https://thehackernews.com/ |
| 11 | Match Group / Hinge / OkCupid Data Breach — SecurityWeek | https://www.securityweek.com/ |
| 12 | Google Cloud API Key Exposure (3,000 keys) | https://thehackernews.com/ |
| 13 | Fireship merges with ui.dev — X Post | https://x.com/fireship_dev/status/2011513209321320671 |
| 14 | Build, Don't Buy — 2026年、AIエージェントは内製する時代へ — Zenn | https://zenn.dev/satoshissss/articles/5be253a330896c |
| 15 | 2026年 AI Coding Agent 活用 — Zenn | https://zenn.dev/team_zenn/articles/ai-agent-security |
| 16 | Cybersecurity Predictions for 2026 — The Hacker News | https://thehackernews.com/2026/02/cybersecurity-tech-predictions-for-2026.html |
| 17 | Hacker News Front Page | https://news.ycombinator.com/front |

---

## 【本日のシステムアイデア】

### アイデアの着想プロセス

本日のトレンドを横断すると、3つの強い流れが重なっている:

1. **WiFi DensePose が GitHub Trending #1** に躍り出た核心技術は「CSI（チャネル状態情報）の時系列信号から異常を検出する」というシグナル処理パターン。WiFi 信号が人体に当たると振幅・位相が変化する → この変化の異常検出が人体追跡の基礎。

2. **「Build, Don't Buy」(Zenn)** — 難しいフレームワークを買わずに自分でゼロから実装する。PicoLM の精神（昨日の延長）。

3. **Kilo Code Reviewer** (PR 自動レビュー) → 「信号に注目して異常を素早く見つける」という発想が共通。

掛け合わせると：「**WiFi DensePose の核心アルゴリズムである CSI 時系列異常検出を、ゼロ依存の純粋 Python で実装し、シミュレーションデモとして動かす**」というアイデアが浮かぶ。実際の WiFi ハードウェアがなくても、CSI データを数学的にシミュレートして「動き検知」の仕組みを体験できる。

---

### 本日のシステム: `csi-motion-detector` — WiFi 信号で動きを検知するシミュレーター

#### システム概要
WiFi DensePose の核心技術「CSI（Channel State Information）の時系列異常検出」を、**実際の WiFi ハードウェア不要**・**標準ライブラリのみ**で体験できる Python CLI ツール。

- **CSI シミュレーター**: 静止/歩行/高速移動の 3 状態を模した CSI 振幅時系列データを数学的に生成
- **スライディングウィンドウ Z スコア検出**: 局所平均・標準偏差からの逸脱度で動き事象を検出
- **PCA ベース多次元融合**: 複数アンテナ×サブキャリアの高次元 CSI を主成分分析で 1 次元スコアに圧縮（numpy なし、標準ライブラリで実装）
- **タイムライン表示**: ASCII グラフで検出イベントを可視化

#### 技術選定の理由
- **純粋 Python・ゼロ依存**: 「Build, Don't Buy」精神 & PicoLM の最小主義。numpy / scipy なしで行列演算・統計処理を実装することで、アルゴリズムの本質が透過的に見える
- **数学的シミュレーション**: 実ハードウェアがないと動かない wifi-densepose の核心部分を「学べる形」に変換
- **モジュール設計**: CSI 生成・特徴抽出・異常検出・表示を分離し、実データへの差し替えが容易

#### 動作イメージ
```
$ python src/main.py --duration 30 --antennas 3 --subcarriers 30

CSI Motion Detector v1.0 — 2026-03-01
Inspired by: ruvnet/wifi-densepose (GitHub Trending #1)

Simulating 30s of WiFi CSI data (3 antennas × 30 subcarriers)...

 Time  Signal  Motion Score  Event
──────────────────────────────────────────────────
  0.0s  ▂▂▂▂▂   0.12  ░░░░░░░░░░  [IDLE]
  1.0s  ▂▂▂▃▂   0.18  ░░░░░░░░░░
  5.0s  ▄▅▄▅▄   1.84  ████░░░░░░  [MOTION DETECTED] person walking
  6.0s  ▅▆▅▆▅   2.31  █████░░░░░  [MOTION] confidence: HIGH
 10.0s  ▂▂▂▂▂   0.09  ░░░░░░░░░░  [IDLE]
 18.0s  ▇█▇█▇   3.92  ██████████  [MOTION DETECTED] fast movement
 19.0s  █▇█▇█   4.10  ██████████  [MOTION] confidence: HIGH

Summary: 2 motion events detected in 30s
  Event 1:  5.0s –  9.2s  (4.2s, avg score: 2.1)
  Event 2: 18.0s – 20.1s  (2.1s, avg score: 3.8)
```
