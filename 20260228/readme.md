# 20260228 — 過去24時間のトレンドまとめ & 本日のシステム開発

> 取得日時: 2026-02-28
> 対象期間: 過去24時間以内に公開・話題になった情報のみ

---

## 【過去24時間のトレンドまとめ】

### 🦌 AI エージェント & フレームワーク

#### 1. ByteDance DeerFlow 2.0 リリース — GitHub Trending 急上昇 (21.5k⭐)
- **概要**: ByteDance がオープンソースの SuperAgent ハーネス **DeerFlow 2.0** を公開。v1 との互換性なしのフルスクラッチ書き直し。
- **特徴**: スキル（Markdown ファイル定義）・サンドボックス実行・メモリ・サブエージェント生成を標準装備。LangGraph + LangChain ベース。
- **スキルシステム**: スキルは Markdown ファイルとして定義し、ワークフロー・ベストプラクティス・リソース参照を記述。研究・レポート生成・スライド作成・Web ページ・画像/動画生成を内蔵スキルとして提供。
- **MCP 統合**: MCP サーバー経由で外部ツールを呼び出せるオープンアーキテクチャ。
- **注目点**: "フレームワーク" から "エージェントが実際に仕事をするためのランタイム" へのシフト。

#### 2. GitHub Agent HQ — Claude/Codex/Copilot を同時起動 (GitHub 発表)
- GitHub が **Agent HQ** を発表。Claude Code、Codex、GitHub Copilot を同一タスクに並列展開し、コードレビュー・テスト生成・セキュリティスキャン・デプロイを専門エージェントが分担して処理。

#### 3. Superset が Product Hunt 1位 (485 upvotes)
- 「ローカルマシン上で Claude Code や Codex の軍団を走らせる」ツール **Superset** が Product Hunt デイリー1位。AIコーディングエージェントの大量並列実行への需要を示す。

#### 4. obra/superpowers — エージェントスキルフレームワーク (61.1k⭐)
- Shell ベースのスキルフレームワーク。1週間で +7,000 スターを追加し月間チャートに留まり続け、スキルエコシステムがフレームワークインフラとして確立されたことを示すマイルストーン。

---

### 📊 時系列予測 × AI — TimesFM が Google Sheets に統合

#### 5. Google TimesFM × Connected Sheets — ノーコード時系列予測
- **概要**: Google が 2026-02-16 より Connected Sheets（BigQuery）に TimesFM を統合。SQL/Python 不要で Google Sheets から直接将来予測が可能に。
- **TimesFM の特性**: 1,000億件の実データで事前学習済み。ゼロショット予測でチューニング不要。500M パラメータながら ARIMA・ETS・DeepAR を上回る精度。
- **`AI.FORECAST` 関数**: 動的コンテキストウィンドウ最大 15,000 タイムポイント。`AI.EVALUATE`・`AI.DETECT_ANOMALIES` も同時提供。
- **影響**: 非技術者でも「未来の売上・需要量」を数クリックで予測可能に。

---

### ⚡ エッジ AI — PicoLM: $10 ボードで 1B LLM を動かす

#### 6. RightNow-AI/picolm — 超軽量 LLM 推論エンジン (1.1k⭐)
- **概要**: C11 の約 2,500行、ゼロ依存、バイナリ 80KB で 1B パラメータの LLM を 256MB RAM/$10 ボードで推論。
- **対応モデル**: TinyLlama 1.1B Q4_K_M（GGUF 形式、LLaMA アーキテクチャ全般）。RAM 使用量 45MB。
- **llama.cpp との違い**: llama.cpp はランタイムだけで 200MB+ 必要でデスクトップ向け。PicoLM は組み込みターゲット専用設計。
- **PicoClaw との連携**: Go 製エージェントループ。Telegram/Discord/CLI から入力を受け、picolm にプロンプトをパイプして応答を取得。クラウド不要・API キー不要。

---

### 🔐 セキュリティ — AI ツールを悪用した攻撃が本格化

#### 7. AI 支援で FortiGate 600台以上を侵害 (55カ国)
- ロシア語話者の金銭目的の脅威アクターが DeepSeek・Anthropic Claude などの商用生成 AI を活用し、2026年1月〜2月の期間で FortiGate デバイス 600台超を侵害。

#### 8. Cline CLI へのサプライチェーン攻撃
- オープンソース AI コーディングアシスタント **Cline CLI** の npm publish トークンが 2026-02-17 に侵害され、OpenClaw を密かにインストールする悪意ある更新が配布。

#### 9. Moltbook — 「エージェントの Reddit」が話題沸騰
- 2026年1月末ローンチの **Moltbook** は AI エージェント専用コミュニケーション基盤。エージェント同士が情報共有・調整するための SNS。X/Reddit の開発者コミュニティで急速に拡散。

---

### 📺 YouTube テック

#### 10. YouTube × AI — 1,000万チャンネルが AI ツールを毎日使用
- CEO Neal Mohan が AI 活用チャンネルの増加を発表。Shorts に **Veo 3 Fast**（AI動画生成）を統合。Gemini 3 を使ったノーコードゲーム作成ツール **Playables** β版も公開。

---

### 🇯🇵 Zenn / はてなブックマーク — 国内技術トレンド

#### 11. AIエージェント実践記事の増加 + GAS/Slack 自動配信
- Zenn での「DeerFlow 使ってみた」「Claude Code でフルスタック構築」系記事が急増。技術記事の自動収集・配信（GAS + Slack Webhook）への関心継続。

---

## 【参照URL一覧】

| # | タイトル | URL |
|---|--------|-----|
| 1 | GitHub - bytedance/deer-flow | https://github.com/bytedance/deer-flow |
| 2 | DeerFlow Official Site | https://deerflow.tech/ |
| 3 | ByteDance Open-Sources DeerFlow — MarkTechPost | https://www.marktechpost.com/2025/05/09/bytedance-open-sources-deerflow-a-modular-multi-agent-framework-for-deep-research-automation/ |
| 4 | GitHub - RightNow-AI/picolm | https://github.com/RightNow-AI/picolm |
| 5 | GitHub Workspace Updates: TimesFM in Connected Sheets | https://workspaceupdates.googleblog.com/2026/02/forecast-data-in-connected-sheets-BigQueryML-TimesFM.html |
| 6 | GitHub - google-research/timesfm | https://github.com/google-research/timesfm |
| 7 | GitHub Trending Daily 2026-02-25 | https://sejiwork.com/en/blog/post/github-trending-daily-2026-02-25 |
| 8 | GitHub Open Source Weekly 2026-02-25 — ShareUHack | https://www.shareuhack.com/en/posts/github-trending-weekly-2026-02-25 |
| 9 | obra/superpowers | https://github.com/obra/superpowers |
| 10 | AI-Assisted Threat Actor Compromises 600+ FortiGate Devices — The Hacker News | https://thehackernews.com/2026/02/ai-assisted-threat-actor-compromises.html |
| 11 | Weekly Recap: AI Skill Malware, 31Tbps DDoS — The Hacker News | https://thehackernews.com/2026/02/weekly-recap-ai-skill-malware-31tbps.html |
| 12 | Best of Product Hunt: February 28, 2026 | https://www.producthunt.com/leaderboard/daily/2026/2/28 |
| 13 | xAI opens Grok algorithm (Rust, open-source) | https://x.com/ByteDanceOSS/status/1920827356215693800 |
| 14 | YouTube 2026 Creator Tools Focus on AI | https://www.podcastvideos.com/articles/youtube-2026-updates-ai-live-streaming-monetization/ |
| 15 | Hacker News Front Page | https://news.ycombinator.com/front |
| 16 | GitHub Trending | https://github.com/trending |
| 17 | Trendshift | https://trendshift.io/ |

---

## 【本日のシステムアイデア】

### アイデアの着想プロセス

本日のトレンドを横断すると、3つの流れが交差している:

1. **DeerFlow 2.0 のスキルシステム**: スキルを Markdown ファイルで定義し、エージェントがそれを読み込んでパイプライン実行する設計思想
2. **TimesFM の「ゼロショット時系列予測」**: 事前学習済みモデルが未見データをチューニングなしで予測する考え方
3. **PicoLM の「ゼロ依存・最小主義」**: C11 の 2,500行、依存なし、バイナリ 80KB という設計哲学

掛け合わせると:「**DeerFlow のスキルアーキテクチャを純粋 Python で再現しつつ、そのパイプラインの一スキルとして TimesFM 風の軽量時系列予測を組み込む、ゼロ依存のミニエージェントランタイム**」というアイデアが生まれた。

---

### 本日のシステム: `mini-deerflow` — スキルベース軽量エージェントランタイム

#### システム概要
DeerFlow 2.0 の「スキル = 構造化された能力モジュール」という設計思想を、**標準ライブラリのみの Python** で再現したミニエージェントランタイム。

| モジュール | 役割 |
|----------|------|
| `skill_runner.py` | スキルを動的ロード・連鎖実行するランタイムコア |
| `skills/fetch_trending.py` | GitHub Trending 風のデータ（JSON）を読み込むスキル |
| `skills/score_growth.py` | スター増加率を計算してトレンドスコアを付けるスキル |
| `skills/forecast_stars.py` | Holt二重指数平滑法でスター数を 7 日先予測するスキル（TimesFM インスパイア） |
| `skills/render_report.py` | 結果をターミナルにカラー表示するスキル |
| `data/sample_repos.json` | サンプルデータ（GitHub スター時系列） |

#### パイプライン設計
```
[fetch_trending] → [score_growth] → [forecast_stars] → [render_report]
     ↓                  ↓                  ↓                  ↓
  JSON 読み込み      成長率スコア       7日先予測        ターミナル表示
```

#### 技術選定の理由
- **Python 標準ライブラリのみ**: PicoLM の「ゼロ依存」哲学を踏襲
- **スキルを Python モジュールとして定義**: DeerFlow の Markdown スキルを Python クラスで実装
- **SkillChain でパイプライン化**: DeerFlow のサブエージェント連鎖を単一プロセス内で表現
- **Holt 二重指数平滑法**: TimesFM の「ゼロショット予測（事前学習不要）」の精神を軽量実装で体現。トレンド成分を捕捉するため単純 SES ではなく Holt を採用
- **JSON 出力対応**: CI/CD・他スキルへのデータ受け渡しを想定

#### 動作イメージ
```
$ python src/skill_runner.py --pipeline fetch_trending,score_growth,forecast_stars,render_report

Mini-DeerFlow v1.0 — 2026-02-28
Running pipeline: fetch_trending → score_growth → forecast_stars → render_report

╔══════════════════════════════════════════════════╗
║        Tech Repo Trend Forecast Report          ║
║               2026-02-28                        ║
╚══════════════════════════════════════════════════╝

Rank  Repository                Stars  Growth/day  7-day Forecast
  1   bytedance/deer-flow       21500   +312.4     ████████  ~23687
  2   obra/superpowers          61100   +180.1     ██████    ~62361
  3   RightNow-AI/picolm         1100    +89.3     ████      ~1725
  4   D4Vinci/Scrapling         17300    +64.2     ███       ~17749
  5   shareAI-lab/learn-claude  17900    +55.8     ██        ~18291

Forecast method: Holt Double Exponential Smoothing (α=0.3, β=0.1)
```
