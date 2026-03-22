## 本日のスタック選定
- カテゴリ: [H] AIインテグレーション
- 言語/FW: Node.js + Express + EJS
- 選定理由: Agentic AI Code Review（Google Sashiko）と GitHub Trending AI Agent の支配が継続。リアルタイムトレンド分析 + AI分類ロジック実装でトレンドを反映。外部API キー不要な実装。
- 実行方法: `npm install && npm start` → http://localhost:3000 で起動

---

## 収集トレンド

### Hacker News
- タイトル: Google Sashiko - Agentic AI Code Review for Linux Kernel
- URL: https://news.ycombinator.com/front
- 概要: AI エージェント技術が OSS コードレビュー領域に進出。自動化された脆弱性検出が注目。

- タイトル: CVE-2026-3888 - Ubuntu systemd 脆弱性
- URL: https://thehackernews.com/
- 概要: セキュリティ脆弱性の継続的な発見・報告。AI セキュリティスキャナーへの需要が高い。

### GitHub Trending
- タイトル: NVIDIA/NemoClaw, OpenClaw (210k+ stars)
- URL: https://github.com/trending
- 概要: AI Agent フレームワークが GitHub を支配。企業がエージェント開発を加速。

- タイトル: Godot Engine Momentum
- URL: https://github.com/trending
- 概要: オープンソースゲームエンジンが新しい注目を集めている。

### Product Hunt
- タイトル: AI Agents 主導 - Voice/Automation ツール拡大
- URL: https://www.producthunt.com/categories/ai-agents
- 概要: 音声ベースの自動化、顧客サービス AI が月次ランキングを占有。

---

## 本日のアイデア

### 組み合わせたトレンド
1. **Agentic AI の普及** × **GitHub Trending の AI Agent 支配**
2. **セキュリティ脆弱性の継続注目** × **AI 分類技術**
3. **リアルタイムトレンド監視ニーズ**

### システム概要
「**Agentic Trend Classifier**」

GitHub Trending と Hacker News Top Stories をリアルタイムスクレイプし、以下を自動分類：
- **AI Agent 関連度スコア** (0-100%)
- **セキュリティ関連度** (脆弱性・CVE 検知)
- **トレンドカテゴリ** (言語、フレームワーク、キーワード)

Node.js スクリプトで各ページを定期取得→テキスト分析→EJS テンプレートで HTML レンダリング。
外部 API キーなし。ローカルキーワードマッチング + 簡易スコアリングで即座に動作。

### スコープ
- リアルタイムデータソース: GitHub Trending (1時間ごと更新)
- トレンド分類: AI Agent, Security, 言語別カテゴリ
- UI: 単一ページダッシュボード + リアルタイム更新
- 実装時間: 2 時間以内
- 依存パッケージ: express, ejs, cheerio (HTMLパース)

---

## 実装メモ

### 工夫した点
1. **キーワードベースの分類エンジン** - 複数の分野信号を検知
2. **ローカル処理** - 外部 API キー・サービス不要
3. **リアルタイム更新** - Node.js setInterval で 1 時間ごと自動更新
4. **レスポンシブUI** - モバイル対応 CSS

### 今後の拡張案
- [ ] Claude API 統合による NLP ベース感情分析
- [ ] データベース化してトレンド履歴を保存・グラフ化
- [ ] Slack/Discord bot 化して毎日のトレンドを定期配信
- [ ] Zenn・はてなブックマークなど日本国内トレンド源の追加
