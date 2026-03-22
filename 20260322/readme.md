## 本日のスタック選定
- カテゴリ: [F] ブラウザ拡張 / ユーザースクリプト
- 言語/FW: Manifest V3 (JavaScript, JSON)
- 選定理由: GlassWorm 供給チェーン攻撃（VSX/npm 72拡張機能悪用）がホット。Anthropic の自動脆弱性検出論文との組み合わせで、開発者向けセキュリティ拡張の需要が時事的。Manifest V3 は前回未使用カテゴリ。
- 実行方法: Chrome/Edge で拡張機能 → `src/` をアンパックフォルダとして読み込み、または `npm run build` で圧縮

## 収集トレンド

### Hacker News / The Hacker News
- **タイトル**: GlassWorm Supply-Chain Attack Abuses 72 Open VSX Extensions to Target Developers
  - URL: https://thehackernews.com/2026/03/glassworm-supply-chain-attack-abuses-72.html
  - 概要: 72個のVisual Studio Code拡張機能を悪用した大規模サプライチェーン攻撃。GitHub盗難トークンでPythonリポジトリへマルウェア直接push。

- **タイトル**: North Korean Hackers Publish 26 npm Packages Hiding Pastebin C2 for Cross-Platform RAT
  - URL: https://thehackernews.com/2026/03/north-korean-hackers-publish-26-npm.html
  - 概要: 26個の公式npm パッケージにC2 RAT隠蔽。開発者を直接マルウェア感染のリスク。

- **タイトル**: Critical Langflow Flaw CVE-2026-33017 Triggers Attacks within 20 Hours of Disclosure
  - URL: https://thehackernews.com/2026/03/critical-langflow-flaw-cve-2026-33017.html
  - 概要: AI/LangChain関連の重大脆弱性が20時間で攻撃化。

### GitHub Trending
- **タイトル**: LangChain Continues Dominance in GitHub Trending
  - 概要: AI開発ツール・LangChain がGitHub Trendingで継続支配。AI統合トレンドは継続。
  - URL: https://github.com/trending

### セキュリティブログ
- **タイトル**: Anthropic Finds 22 Firefox Vulnerabilities Using Claude Opus 4.6 AI Model
  - URL: https://thehackernews.com/2026/03/anthropic-finds-22-firefox.html
  - 概要: Claude Opus 4.6 による自動脆弱性検出の実証。AI が開発者のセキュリティ検査を自動化するトレンド。

---

## 本日のアイデア

### 組み合わせたトレンド
1. GlassWorm / North Korean npm パッケージ供給チェーン攻撃（2月下旬～3月）
2. Anthropic Claude による自動脆弱性検出・セキュリティ分析の自動化
3. 開発者向けセキュリティツールの高い需要（macOS 26, Firefox セキュリティ強化など新OS/ブラウザリリース）

### システム概要
**「PackageGuard」 — ブラウザ拡張機能（Manifest V3）**

npm.com と Visual Studio Marketplace でパッケージを閲覧中に、リアルタイムでセキュリティ信頼度スコアを表示するChrome/Edge拡張機能。

**動作**:
1. npm / VSCode Marketplace のページを検出
2. パッケージ名・バージョンを抽出
3. セキュリティシグナル（ダウンロード数 / 更新日 / GitHub 星数 / license 有無等）から信頼度スコア (0-100) を計算
4. ページ上にバッジ・スコアバーを挿入
5. リスク警告（新規パッケージ・更新停止・未署名など）をポップアップで通知

### スコープ
- 実装時間: 1.5時間程度
- 外部 API: 不要（クライアント側 heuristics ベース）
- 対象ブラウザ: Chrome / Edge（Manifest V3）
- UIコンポーネント: popup.html + content-script.js で DOM 操作

### 実装メモ
- 工夫した点:
  - Manifest V3 の新しいAPI（service worker等）を活用
  - パフォーマンス: content script で軽量な heuristic スコア計算のみ（重い外部呼び出し無し）
  - リスク検知: npm 新規パッケージ（作成1週間以内）を自動検出・警告
  - UI: スコアを視覚的に（色: 🟢緑=安全, 🟡黄=注意, 🔴赤=危険）

- 今後の拡張案:
  - 外部セキュリティDB連携（Snyk API等）で CVE チェック
  - HistoryAPI 統合で パッケージバージョン遷歴表示
  - ユーザーレビュー・フラグ機能（信頼スコア投票）
