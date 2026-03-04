# 20260303 — 過去24時間のトレンドまとめ & 本日のシステム開発

---

## 【過去24時間のトレンドまとめ】

### AI & ツール / LLM

#### 1. Go言語がAIエージェント開発のベストチョイスとして急浮上
- Hacker Newsで「A case for Go as the best language for AI agents」が大きな話題に
- Agent2Agent (A2A) / MCP (Model Context Protocol) などのプロトコル実装でGoが優勢
- Go製AIエージェントフレームワーク（LocalAGI, Crush, LangChainGo）がGitHub Trendingに多数登場
- Google Cloudレポート: GoベースのマイクロサービスはPython比でレイテンシ30%改善・スループット25%向上

#### 2. OpenClawがReactを抜いてGitHub最多スター数プロジェクトへ
- 60日間で9,000→188,000スターに急増（HN掲載）
- AI関連プロジェクトがGitHubトップを席巻。Ollama 162,000・Dify 130,000も追跡中
- 2025年のGitHub上位成長プロジェクトの約60%がAI関連と判明（InfoQ調査）

#### 3. Google DeepMindがAlphaEvolveを公開
- GeminiとEvolutionary Algorithmを組み合わせた新システム
- 未解決問題に対して新アルゴリズムを自律的に考案・検証・改善するループを実現
- MIT Technology ReviewがX/LinkedLiveで解説ライブを実施（3月3日）

---

### セキュリティ

#### 4. Android 3月2026セキュリティアップデート — 過去最大129件の脆弱性パッチ
- **CVE-2026-21385**: Qualcomm Displayドライバのinteger overflow/wraparound起因のゼロデイ、野外で限定的に悪用確認済み
- **CVE-2026-0006**: Systemコンポーネントの重大なRCE（リモートコード実行）、権限・ユーザー操作不要
- CVE-2026-0047（Frameworkの権限昇格）、CVE-2025-48631（DoS）など多数
- Samsungも65件のGalaxyデバイス向けパッチを同時展開

#### 5. APT28（ロシア連携）がMSHTML 0-dayを悪用
- CVE-2026-21513（CVSS 8.8）: MicrosoftのFebruary Patch Tuesdayで修正済み
- MSHTML Security Feature Bypassの脆弱性がAPT28に悪用されていたと判明

#### 6. Cisco Catalyst SD-WAN Controller にCVSS 10.0の最高深刻度脆弱性
- CVE-2026-20127: 認証なしのリモート攻撃者がバイパスできる最高深刻度
- 現在積極的に悪用中（野外エクスプロイト確認済み）
- CISAがKnown Exploited Vulnerabilities (KEV) カタログに追加

---

### GitHub Trending

#### 7. WiFi DensePose — WiFi信号で壁越しに人体姿勢推定（Rust実装）
- ruvnet/RuView: 25,164スター。WiFiのCSI（Channel State Information）を解析
- カーネギーメロン大学の2023年研究を実用実装、精度94.2%
- 30FPS・50ms以下のレイテンシで最大10人同時トラッキング
- 災害救助・非接触患者モニタリングへの応用が話題

#### 8. airi — セルフホスト型AIコンパニオン（TypeScript）
- moeru-ai/airi: 22,120スター。リアルタイム音声チャット・ゲーム機能付き
- Web・macOS・Windows対応

#### 9. LMCache — LLM向け高速KVキャッシュレイヤー（Python）
- LMCache/LMCache: 7,382スター。LLM推論の高速化に特化

---

### Product Hunt

#### 10. Figr AI: UX Agent for Product Teams
- AIがプロダクトを学習しUX設計を自動提案
- Product Hunt March 2026リーダーボード上位

#### 11. Community Figma MCP Server
- AIエージェントがFigmaデザインを操作するMCPサーバー
- MCP (Model Context Protocol) エコシステムの急速拡大を象徴

#### 12. Claude for PowerPoint
- ClaudeでPPT資料の構築・編集・改善を自動化

---

### Twitter/X テック界隈

#### 13. WiFi DensePoseがバイラル拡散
- 「カメラなし・WiFiだけで壁越しに人を検出」という衝撃でXで大拡散
- プライバシー面での議論も勃発（視覚データゼロだが位置情報は取れる）

#### 14. Pianoterm — ピアノからシェルコマンドを実行するLinux CLIツール
- Hacker News Show HN掲載。「コンピュータをピアノで操作する」という遊び心が受け話題に
- CLIツール文化・ターミナルハック系コンテンツが盛り上がり

---

### YouTube 最新テック系動画

#### 15. Fireship: Android 129 CVEs解説動画
- 「最大規模のAndroidパッチがリリース」トピックでFireship系チャンネルが解説動画を投稿
- CVE-2026-21385の技術的解析が注目を集める

---

### Zenn トレンド（日本エンジニアコミュニティ）

#### 16. AIは「推論モデルの時代」から「実装の時代」へ
- 2025年のパラダイムシフト（推論モデル台頭・エージェントAI普及）が企業導入フェーズへ
- 銀行・製造業・医療での具体的なAIエージェント事例が続々
- Claude Code + MCPサーバーの社内特化型活用TipsがZennに毎日投稿

#### 17. NDLOCR-Lite — GPU不要の軽量AI OCRツール（国会図書館）
- 国会図書館が無償公開、はてなブックマーク週間ランキング上位
- GPU環境なしで動作する実用的なOCRツールとして話題

---

### はてなブックマーク IT カテゴリ

#### 18. NDLOCR-Lite（窓の杜）
- 国会図書館のAI OCRツール、2026年3月第1週ランキング上位

#### 19. Plurality（デジタル民主主義書籍）
- Audrey Tang & Glen Weylの著作、技術と民主主義の交差点を論じる

---

## 【参照URL一覧】

| # | タイトル | URL |
|---|---------|-----|
| 1 | A case for Go as the best language for AI agents (HN) | https://news.ycombinator.com/front |
| 2 | Why Go Is Becoming a Language for AI Tooling in 2026 | https://dasroot.net/posts/2026/02/why-go-becoming-language-ai-tooling-2026/ |
| 3 | Ai and Go in 2026 – Applied Go | https://appliedgo.net/spotlight/ai-and-go/ |
| 4 | GitHub's Points to a More Global, AI-Challenged Open Source Ecosystem 2026 | https://infoq.com/news/2026/03/github-ai-2026/ |
| 5 | Android Security Update — 129 Vulnerabilities Including Zero-Day | https://thehackernews.com/2026/03/google-confirms-cve-2026-21385-in.html |
| 6 | APT28 Tied to CVE-2026-21513 MSHTML 0-Day | https://thehackernews.com/2026/03/apt28-tied-to-cve-2026-21513-mshtml-0.html |
| 7 | Android Security Update — CybersecurityNews | https://cybersecuritynews.com/android-security-update-march/ |
| 8 | Samsung March 2026 Security Update (65 fixes) | https://www.sammobile.com/news/samsung-march-2026-security-patch-65-vulnerabilities |
| 9 | WiFi-DensePose Tutorial: Track Poses Through Walls 2026 | https://byteiota.com/wifi-densepose-tutorial-track-poses-through-walls-2026/ |
| 10 | GitHub Trending | https://github.com/trending |
| 11 | Product Hunt March 2026 Leaderboard | https://www.producthunt.com/leaderboard/daily/2026/3/1 |
| 12 | Zenn — 2026年のAIトレンド：推論モデルの時代から実装の時代へ | https://zenn.dev/7788/articles/af11fbce6c3379 |
| 13 | はてなブックマーク 2026年3月第1週ランキング | https://bookmark.hatenastaff.com/entry/2026/03/03/142330 |
| 14 | CISA Known Exploited Vulnerabilities Catalog | https://www.cisa.gov/known-exploited-vulnerabilities-catalog |
| 15 | MIT Technology Review — What's next for AI in 2026 | https://www.technologyreview.com/2026/01/05/1130662/whats-next-for-ai-in-2026/ |
| 16 | Hacker News Ask HN: Who is hiring? (March 2026) | https://news.ycombinator.com/item?id=47219668 |
| 17 | Top AI influencers on X/Twitter in 2026 | https://tweetstorm.ai/blog/top-ai-influencers |

---

## 【本日のシステムアイデア】

### アイデアの着想プロセス

本日のトレンドを俯瞰すると、**「Go言語の台頭」**と**「セキュリティ脆弱性の爆発的増加」**という2つの大きな波が見えた。

- **HN**: 「GoがAIエージェントのベスト言語」という議論が活発化
- **セキュリティ**: Android 129件CVEパッチ・APT28 MSHTML悪用・Cisco CVSS 10.0と、**既知悪用脆弱性（KEV）**が急増中
- **CLIツール文化**: HN掲載の「Pianoterm」、GitHub Trending「Crush（ターミナルベースAIコーディングエージェント）」など、ターミナルツールが盛り上がり
- **CISA KEV**: CISAのKnown Exploited Vulnerabilitiesカタログへの追加が相次いでおり、セキュリティチームは「今日何が悪用されているか」をリアルタイムで把握する必要がある

**→ GoでCISAのKEVカタログをリアルタイム監視するCLIツールを作れば、今日のトレンドを完璧に体現できる**

### 本日のシステム: `KEV-Watch` — Go製・CISA既知悪用脆弱性リアルタイム監視CLI

#### システム概要

CISA（米国サイバーセキュリティ・インフラセキュリティ庁）が公開する **Known Exploited Vulnerabilities (KEV) カタログ** をリアルタイムでフェッチし、「直近N日以内に追加されたCVE」を美しいターミナルUIで一覧表示するGoのCLIツール。

セキュリティエンジニアが朝一で「今日は何が悪用されているか？」を確認するためのワンライナーコマンドとして機能する。

#### 技術選定の理由

| 技術 | 採用理由 | トレンドとの関係 |
|------|----------|----------------|
| **Go 1.24** | 高速・シングルバイナリ・標準ライブラリだけで完結 | HN「Go is the best language for AI agents」がトレンド入り |
| **CISA KEV API** | 公式JSON API、無料・APIキー不要 | Cisco CVE-2026-20127・Android CVE-2026-21385が今日KEVに追加 |
| **ANSI Terminal UI** | 依存なし・どの環境でも動く | Pianoterm・Crushなどターミナルツールが3月のHNトレンド |

#### 動作イメージ（CLI出力例）

```
$ go run src/main.go -days 7

╔══════════════════════════════════════════════════╗
║  KEV-Watch — CISA Known Exploited Vulnerabilities ║
╚══════════════════════════════════════════════════╝
  Fetching catalog...

  Catalog: CISA Known Exploited Vulnerabilities Catalog
  Version : 2026.03.03  | Released: 2026-03-03
  Total   : 1247 CVEs | Filtered (last 7 days): 8 CVEs

  CVE ID               Vendor/Project         Product            Date Added
  ──────────────────────────────────────────────────────────────────────────────
🔴 CVE-2026-20127      Cisco                  Catalyst SD-WAN    2026-03-03
   Cisco SD-WAN Authentication Bypass Vulnerability

🟡 CVE-2026-21385      Qualcomm               Android Display    2026-03-03
   Qualcomm Display Driver Integer Overflow Vulnerability

  ...

  Top Vendors by CVE Count (last 7 days):
  Cisco                ████ (4)
  Microsoft            ██ (2)
  Google               ██ (2)

  ✅ Scan complete — 8 exploited CVEs in last 7 days
  Source: https://www.cisa.gov/.../known_exploited_vulnerabilities.json
```

#### セットアップ手順（3ステップ以内）

```bash
# 1. Goのインストール確認（1.18以上）
go version

# 2. 実行（外部依存ゼロ）
go run src/main.go

# 3. オプション付きで実行
go run src/main.go -days 7              # 直近7日間のCVEを表示
go run src/main.go -vendor Cisco        # Cisco関連のみフィルタ
go run src/main.go -days 30 -detail     # 詳細説明付きで30日分
```
