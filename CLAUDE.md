# CLAUDE.md — 日次トレンド調査 & プロトタイプ開発 自動化手順書

このファイルは Claude Code が毎日実行する「トレンド調査 → アイデア統合 → ミニアプリ開発 → Git コミット」の標準手順を定義します。

---

## リポジトリ構成

```
Trend_idea/
├── CLAUDE.md          ← 本ファイル（作業手順書）
├── .gitignore
├── YYYYMMDD/          ← 日付ごとのルートディレクトリ
│   ├── readme.md      ← トレンドまとめ・システムアイデア
│   ├── src/           ← ソースコード
│   └── docs/          ← 設計メモ・補足資料
└── ...
```

---

## 毎日の作業フロー（Step 1〜6）

### Step 1: 日付取得と作業環境の構築

システム時刻から本日の日付を `YYYYMMDD` 形式で取得し、以下のディレクトリ・ファイルを作成する。

```bash
mkdir -p YYYYMMDD/src YYYYMMDD/docs
touch YYYYMMDD/readme.md
```

**作成物**:
- `YYYYMMDD/`           — 本日のルートディレクトリ
- `YYYYMMDD/src/`       — ソースコード配置用
- `YYYYMMDD/docs/`      — 設計メモ・補足資料用
- `YYYYMMDD/readme.md`  — 本日のまとめ・ドキュメント用

---

### Step 2: 情報収集（過去 24 時間以内厳守）

以下の**必須情報源すべて**から、過去 24 時間以内に公開・話題になった情報のみを収集する。

| 情報源 | 収集すべき情報の種類 |
|-------|-------------------|
| **Hacker News** | フロントページのトップ記事・Show HN・Ask HN |
| **Reddit** | r/programming, r/MachineLearning, r/netsec, r/devops のホット |
| **Twitter(X) テック界隈** | エンジニア・研究者の注目投稿・バズツイート |
| **YouTube 最新テック系動画** | Fireship, Two Minute Papers, Tech With Tim 等の新着 |
| **セキュリティ関連ブログ** | The Hacker News, Krebs on Security, Schneier on Security |
| **GitHub Trending** | Daily の上位リポジトリ（言語・スター数・説明） |
| **Product Hunt** | Today's top products |
| **Zenn トレンド** | 国内エンジニアの話題記事 |
| **はてなブックマーク IT カテゴリ** | ホットエントリ上位 |

**収集の注意点**:
- 取得情報の対象期間は**厳密に過去 24 時間以内**のみ
- 各情報源から最低 2 件以上のトピックを収集すること
- URL（ポスト・動画・記事）を正確に記録しておくこと

---

### Step 3: アイデアの統合とシステム考案

収集した複数のトレンドトピックを**掛け合わせて**、本日開発する小さなシステムのアイデアを 1 つ考案する。

**考案のコツ**:
- 単一トレンドをそのまま実装するのではなく、**2〜3 のトレンドを組み合わせる**
- 「今日この瞬間でないと意味がない」時事性のあるアイデアを優先する
- 1〜3 時間で実装できる小ささにスコープを絞る
- 外部 API キーや有料サービスなしで動作することを優先する

---

### Step 4: README の記述

`YYYYMMDD/readme.md` に以下の内容を Markdown 形式で記述する。

#### 必須セクション

```markdown
# YYYYMMDD — 過去24時間のトレンドまとめ & 本日のシステム開発

## 【過去24時間のトレンドまとめ】
### カテゴリ名（例: AI & ツール / セキュリティ / GitHub Trending / ...）
#### 1. トピックタイトル
- 概要・要点（箇条書き）

## 【参照URL一覧】
| # | タイトル | URL |
|---|---------|-----|
| 1 | ... | https://... |

## 【本日のシステムアイデア】
### アイデアの着想プロセス
（どのトレンドをどう掛け合わせたか）

### 本日のシステム: `システム名` — キャッチコピー
#### システム概要
#### 技術選定の理由
#### 動作イメージ（コードブロックで CLI 出力例など）
```

---

### Step 5: ミニアプリ（小さいシステム）の開発

Step 3 で考案したシステムを `YYYYMMDD/src/` に実装する。

**実装基準**:
- 実際に動作する（または実行手順が明確な）コードであること
- 小さくて構わないが、`python3 main.py` 等で即座に動作確認できること
- 外部依存は最小限に（標準ライブラリ優先、必要な場合は `requirements.txt` を同梱）
- 設計図・API レスポンス例・シーケンス図があれば `YYYYMMDD/docs/` に配置

**推奨ファイル構成**（言語・内容に応じて調整）:

```
YYYYMMDD/src/
├── main.py（またはメインエントリポイント）
├── requirements.txt（外部依存がある場合のみ）
└── （必要に応じてサブモジュール・データファイル等）

YYYYMMDD/docs/
└── design.md（設計メモ・アーキテクチャ図・API 仕様等）
```

---

### Step 6: Git コミットとブランチへのプッシュ

以下の操作を**必ず**実行する。

```bash
# 1. ステージング
git add YYYYMMDD/

# 2. コミット
git commit -m "feat: [YYYYMMDD] トレンドまとめとシステム開発"

# 3. 開発ブランチへプッシュ
git push -u origin claude/daily-trends-automation-FuNfP

# 4. main ブランチへマージ（ローカル）
git checkout main
git merge claude/daily-trends-automation-FuNfP
```

**ブランチルール**:
- 開発は必ず `claude/daily-trends-automation-FuNfP` ブランチで行う
- リモートへの push も同ブランチのみ（`main` へのリモート push は権限制限あり）
- `__pycache__/` や `*.pyc` は `.gitignore` で除外済み

---

## コミットメッセージのフォーマット

```
feat: [YYYYMMDD] トレンドまとめとシステム開発

## 過去24時間のトレンド (YYYY-MM-DD)
- トピック1の一行要約
- トピック2の一行要約
- ...

## 本日のシステム: システム名
システムの概要を2〜3文で記述。
技術的な特徴・工夫点・トレンドとの関連を含める。
```

---

## 品質チェックリスト

作業完了前に以下を確認する。

### README
- [ ] 過去 24 時間以内の情報のみを使用しているか
- [ ] 必須情報源（8 ソース）すべてから情報を収集したか
- [ ] 参照 URL が正確に記載されているか
- [ ] システムアイデアが複数トレンドの組み合わせになっているか

### ソースコード
- [ ] `python3 src/main.py` 等で実際に動作するか
- [ ] エラーなく最後まで実行できるか
- [ ] `docs/design.md` に設計概要が記載されているか

### Git
- [ ] `git status` でコミット漏れがないか
- [ ] コミットメッセージが所定フォーマットに従っているか
- [ ] リモートへの push が成功したか（`origin/claude/daily-trends-automation-FuNfP`）

---

## 過去の実施記録

| 日付 | システム名 | 主なトレンド | ソース |
|------|-----------|------------|-------|
| 20260227 | `ai-repo-auditor` | Claude Code RCE (CVE-2025-59536)、OpenClaw/ClawHavoc | `20260227/` |
| 20260228 | `mini-deerflow` | ByteDance DeerFlow 2.0、Google TimesFM、PicoLM | `20260228/` |
| 20260301 | `csi-motion-detector` | wifi-densepose (GitHub Trending #1)、Claude in Excel (PH #1)、Cisco SD-WAN CISA緊急指令 | `20260301/` |
| 20260302 | `ai-red-lines` | Anthropic Pentagon 追放・AI レッドライン、FortiGate 600 台 AI 支援攻撃、Deno v2.7 / TypeScript #1 | `20260302/` |

---

## よくある問題と対処法

### `git push` が 403 で失敗する
- push 先ブランチが `claude/` で始まっているか確認する
- `git push -u origin claude/daily-trends-automation-FuNfP` のように完全なブランチ名を指定する

### スクリプトが `ModuleNotFoundError` で失敗する
- 外部ライブラリを使用している場合は `requirements.txt` を同梱し、README に `pip install -r requirements.txt` の手順を記載する
- 標準ライブラリのみで実装できないか再検討する

### 情報源から過去 24 時間以内の情報が見つからない
- Web 検索クエリに日付（例: `February 28 2026`）を明示的に含める
- GitHub Trending の "Today" フィルタを使用する
- Product Hunt の "Today" ページを参照する
