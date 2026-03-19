# 20260319 — Gravity Playground: N体問題インタラクティブシミュレーター

## 本日のスタック選定
- カテゴリ: [E] データ可視化
- 言語/FW: HTML/CSS + Vanilla JS (Canvas API)
- 選定理由: HN トレンド「Show HN: Interactive 3D three-body problem simulator in browser」が本日急上昇（トップ議論）、GitHub Trending の `newton-physics/newton`（GPU物理シミュレーション）が 345★/day 獲得。物理シミュレーション × ブラウザ可視化の需要が高まっており、外部依存ゼロで即動くデータ可視化として実装。
- 実行方法: `20260319/src/index.html` をブラウザで開く（サーバー不要）

---

## 収集トレンド

### GitHub Trending (2026-03-19)
- タイトル: `jarrodwatts/claude-hud` — Claude Code plugin displaying context usage
- URL: https://github.com/jarrodwatts/claude-hud
- 概要: Claude Code のコンテキスト使用量・エージェント状態をリアルタイム表示するプラグイン。1,851★/day で急上昇中。

- タイトル: `newton-physics/newton` — GPU-accelerated physics simulation engine
- URL: https://github.com/newton-physics/newton
- 概要: ロボット研究向けGPU物理シミュレーションエンジン（Python）。345★/day。

- タイトル: `gsd-build/get-shit-done` — Meta-prompting context engineering for Claude Code
- URL: https://github.com/gsd-build/get-shit-done
- 概要: Claude Code 向けのメタプロンプト・コンテキストエンジニアリングシステム。1,414★/day。

- タイトル: `obra/superpowers` — Agentic skills framework
- URL: https://github.com/obra/superpowers
- 概要: エージェント型スキルフレームワーク。3,476★/day と最多。

### Hacker News (2026-03-18〜19)
- タイトル: Show HN: I built an interactive 3D three-body problem simulator in the browser
- URL: https://news.ycombinator.com/
- 概要: ブラウザ上で動作する三体問題3Dシミュレーターがトップ議論に。物理シミュレーションの可視化がHN界隈で大きな反響。

- タイトル: Python 3.15's JIT is now back on track
- URL: https://news.ycombinator.com/
- 概要: Python 3.15 のJITコンパイラ実装が再び進展。パフォーマンス改善への期待高まる。

- タイトル: 2025 Turing Award given for quantum information science
- URL: https://news.ycombinator.com/
- 概要: 2025年チューリング賞が量子情報科学分野に授与。

### Tech News (March 2026)
- タイトル: Claude Sonnet 4.6 & Anthropic $100M Partner Network
- URL: https://www.technologyreview.com/2026/01/12/1130027/generative-coding-ai-software-2026-breakthrough-technology/
- 概要: Anthropicが3月12日に$100Mクロードパートナーネットワークを発表。AI生成コードがMicrosoftの30%、Googleの25%を占めるように。

- タイトル: The Rise of "Super Agents" & Multi-Agent Systems
- URL: https://www.ibm.com/think/news/ai-tech-trends-predictions-2026
- 概要: IBMは「エージェントコントロールプレーン」と「マルチエージェントダッシュボード」が2026年のキートレンドと予測。

### Zenn/Qiita トレンド (2026-03-19)
- タイトル: プログラミング雑記 2026年3月19日 #AI
- URL: https://qiita.com/ishisaka/items/198a69e57f4bee422cfc
- 概要: VS Code 1.112（エージェント機能強化）リリース。Claude Code / Codex 移行議論が国内エンジニアコミュニティで活発化。

- タイトル: 2026年のAIトレンド：推論モデルの時代から実装の時代へ
- URL: https://zenn.dev/7788/articles/af11fbce6c3379
- 概要: RLVR・GRPOなど推論モデルの実装フェーズへの移行が本格化。

---

## 本日のアイデア

- 組み合わせたトレンド:
  1. HN「三体問題ブラウザシミュレーター」（リアルタイム物理可視化の注目）
  2. GitHub Trending `newton-physics/newton`（物理シミュレーション需要）
  3. 「データ可視化 × ブラウザ完結」の潮流（外部APIなし、即実行可能）

- システム概要: **Gravity Playground — N体問題インタラクティブシミュレーター**
  - 任意の数の天体を配置し、重力相互作用をリアルタイムでCanvas描画
  - ドラッグで初速設定、5つのプリセット（8の字軌道・太陽系・連星系・カオス・銀河衝突）
  - 重力定数G・減衰・トレイル長・速度スケールをスライダーでリアルタイム調整
  - タッチ操作対応（モバイル）

- スコープ:
  - `src/index.html` 1ファイル完結
  - 外部ライブラリ・APIキー不要
  - ブラウザで即起動

---

## 実装メモ

- 工夫した点:
  - **リープフロッグ積分**（Velocity Verlet風）で数値的安定性を確保
  - **ソフトニング係数**（softening=200）で天体同士の近接時の爆発的加速を防止
  - **トレイルグラデーション**で軌跡の時間的方向感を視覚化
  - **Radial Gradient glow** で天体の発光表現（shadow/blur使用）
  - 8の字軌道（Chenciner & Montgomery 解）の正確な初期条件を実装
  - 銀河衝突プリセットで多天体（32体）の集団ダイナミクスを表現
  - キーボードショートカット（Space/R/C）対応

- 今後の拡張案:
  - Barnes-Hut ツリーアルゴリズム（O(N log N)）で大規模N体に対応
  - WebWorker でシミュレーションをメインスレッドから分離
  - WebGL/Three.js で真の3D表示（HNのShow HNに近い形）
  - 衝突検出・合体処理の追加
  - シミュレーション状態のJSONエクスポート/インポート
