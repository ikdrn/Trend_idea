# CLAUDE.md — 日次トレンド調査 & プロトタイプ開発 自動化手順書

このファイルは Claude Code が毎日実行する「トレンド調査 → アイデア統合 → ミニアプリ開発 → Git コミット」の標準手順を定義します。

---

## リポジトリ構成

Trend_idea/  
├── CLAUDE.md          ← 本ファイル（作業手順書）  
├── .gitignore  
├── YYYYMMDD/          ← 日付ごとのルートディレクトリ  
│   ├── readme.md      ← トレンドまとめ・システムアイデア  
│   ├── src/           ← ソースコード  
│   └── docs/          ← 設計メモ・補足資料  
└── ...

---

## 毎日の作業フロー（Step 1〜6）

---

## Step 1: 日付取得と作業環境の構築

**JST（日本標準時、UTC+9）** で本日の日付を YYYYMMDD 形式で取得し、以下のディレクトリ・ファイルを作成する。

```bash
# JSTで日付を取得する
DATE=$(TZ='Asia/Tokyo' date +%Y%m%d)
mkdir -p $DATE/src $DATE/docs
touch $DATE/readme.md
```

作成物:

- `YYYYMMDD/`          — 本日のルートディレクトリ
- `YYYYMMDD/src/`      — ソースコード配置用
- `YYYYMMDD/docs/`     — 設計メモ・補足資料用
- `YYYYMMDD/readme.md` — 本日のまとめ・ドキュメント用

---

## Step 2: 情報収集（過去 24 時間以内厳守）

以下の必須情報源すべてから、過去 24 時間以内に公開・話題になった情報のみを収集する。

| 情報源 | 収集すべき情報の種類 |
|--------|-------------------|
| Hacker News | フロントページのトップ記事・Show HN・Ask HN |
| Reddit | r/programming, r/MachineLearning, r/netsec, r/devops のホット |
| Twitter(X) テック界隈 | エンジニア・研究者の注目投稿・バズツイート |
| YouTube 最新テック系動画 | Fireship, Two Minute Papers, Tech With Tim 等の新着 |
| セキュリティ関連ブログ | The Hacker News, Krebs on Security, Schneier on Security |
| GitHub Trending | Daily の上位リポジトリ（言語・スター数・説明） |
| Product Hunt | Today's top products |
| Zenn トレンド | 国内エンジニアの話題記事 |
| はてなブックマーク IT カテゴリ | ホットエントリ上位 |

収集の注意点:

- 取得情報の対象期間は厳密に過去 24 時間以内のみ
- 各情報源から最低 2 件以上のトピックを収集すること
- URL（ポスト・動画・記事）を正確に記録しておくこと

---

## Step 3: アイデアの統合とシステム考案

収集した複数のトレンドトピックを掛け合わせて、本日開発する小さなシステムのアイデアを 1 つ考案する。

考案のコツ:

- 単一トレンドをそのまま実装するのではなく、2〜3 のトレンドを組み合わせる
- 「今日この瞬間でないと意味がない」時事性のあるアイデアを優先する
- 1〜3 時間で実装できる小ささにスコープを絞る
- 外部 API キーや有料サービスなしで動作することを優先する

---

## Step 3.5: 実装スタック選定（強制多様化ルール）

### 禁止事項（厳守）

- 同じ言語・スタックを **2日連続で使うことを禁止** する
- Python 単体スクリプト（CLIツール）は **週に最大2回まで**
- 「とりあえずPython」による選定を禁止する

### アプリカテゴリを毎日ローテーションする

以下の8カテゴリから、**前日と異なるカテゴリ**を選ぶこと。
readme.md に「本日のカテゴリ」を必ず明記する。

| # | カテゴリ | 実装スタック例 |
|---|---------|--------------|
| A | フロントエンドUI | HTML/CSS/Vanilla JS, React, Vue, Svelte, Alpine.js |
| B | フルスタックWebアプリ | Next.js, SvelteKit, Remix, FastAPI+Jinja2, Hono |
| C | CLIツール | Rust(clap), Go, Node.js(commander), Python(typer) |
| D | セキュリティ／ネットワーク | Python(scapy/requests), Go, Bash+curl, Nmap連携 |
| E | データ可視化 | D3.js, Observable Plot, Chart.js, Plotly(Python/JS) |
| F | ブラウザ拡張 / ユーザースクリプト | Manifest V3(JS), Tampermonkey |
| G | WebAssembly / 低レイヤー | Rust→WASM, C→WASM, AssemblyScript |
| H | AIインテグレーション | LangChain.js, Vercel AI SDK, Ollama API連携 |

### スタック選定フロー

1. 前日の `readme.md` を確認し、使用済みカテゴリ・言語を把握する
2. 本日のトレンドで最も話題のカテゴリを選ぶ（前日と異なること）
3. そのカテゴリ内で、トレンドと合致するスタックを1つ選定する
4. **選定理由をreadme.mdの冒頭に必ず記載する**（トレンドとの紐付け）

### readme.md 冒頭テンプレート（必須）

```
## 本日のスタック選定
- カテゴリ: [A〜H + カテゴリ名]
- 言語/FW: [例: Svelte + TypeScript]
- 選定理由: [トレンドとの関連を1〜2文で]
- 実行方法: [例: npm run dev]
```

---

## Step 4: 実装

実装前に以下を自己確認すること:

- [ ] カテゴリが前日と異なる
- [ ] Python CLIは今週2回未満
- [ ] `src/` に README 記載の実行コマンドで動くエントリポイントがある
- [ ] 外部有料APIキー不要で動作する

### フロントエンド系（A/B/E/F カテゴリ）の追加要件

- `docs/` に画面設計メモ（箇条書き可）を置く
- レスポンシブ対応 or モバイル考慮を明記する
- `src/index.html` または `npm run dev` で即起動できること

### セキュリティ系（D カテゴリ）の追加要件

- 倫理的・合法的な用途（自環境テスト・教育目的）に限定する
- 実行時に用途の注意書きを出力すること

---

## Step 5: ドキュメント整備

`YYYYMMDD/readme.md` に以下をすべて記載する。

```
## 本日のスタック選定
- カテゴリ: 
- 言語/FW: 
- 選定理由: 
- 実行方法: 

## 収集トレンド
### [情報源名]
- タイトル: 
- URL: 
- 概要: 

## 本日のアイデア
- 組み合わせたトレンド: 
- システム概要: 
- スコープ: 

## 実装メモ
- 工夫した点: 
- 今後の拡張案: 
```

---

## Step 6: Git コミット

```bash
git add YYYYMMDD/
git commit -m "feat(YYYYMMDD): [カテゴリ] アプリ名 - 使用スタック"
git push
```

コミットメッセージ例:
- `feat(20250310): [FrontendUI] トレンドダッシュボード - Svelte+TS`
- `feat(20250311): [Security] ヘッダー診断CLI - Go`
- `feat(20250312): [DataViz] GitHub Trending可視化 - D3.js`
