# mini-deerflow 設計ドキュメント

作成日: 2026-02-28

---

## 1. アーキテクチャ概要

```
skill_runner.py  (ランタイムコア)
│
├── BaseSkill           — 全スキルが実装すべき抽象インタフェース
├── SkillChain          — スキルを順番に実行してコンテキストを伝播
├── load_skill()        — skills/ から動的にスキルをロード
└── main()              — CLI エントリポイント

skills/
├── fetch_trending.py   — スキル #1: データ読み込み
├── score_growth.py     — スキル #2: 成長率スコアリング
├── forecast_stars.py   — スキル #3: 時系列予測
└── render_report.py    — スキル #4: ターミナル表示

data/
└── sample_repos.json   — サンプル入力データ
```

---

## 2. DeerFlow 2.0 との対応関係

| DeerFlow 2.0 概念 | mini-deerflow 実装 |
|------------------|------------------|
| Skill (Markdown定義) | `BaseSkill` サブクラス (Python) |
| Skill の `workflow` フィールド | `run(context) -> context` メソッド |
| Context/Memory | `dict` として Skills 間で伝播 |
| Pipeline / SubAgent 連鎖 | `SkillChain.run()` |
| Skills Registry | `skills/` ディレクトリ + `load_skill()` |
| MCP Tool 統合 | 今後の拡張点 (現在は JSON ファイル入力) |

---

## 3. コンテキスト辞書のスキーマ

スキル実行後のコンテキスト辞書の主要フィールド:

```json
{
  // fetch_trending が追加するフィールド
  "repos": [...],           // リポジトリリスト
  "fetched_at": "ISO8601",  // データ取得日時
  "source": "文字列",        // データソース名

  // score_growth が各 repo に追加するフィールド
  "current_stars": 21500,
  "avg_daily_gain": 312.4,
  "acceleration": 1.15,     // 後半/前半 成長率比
  "trend_score": 744.93,    // log(avg_daily) * accel * 100

  // forecast_stars が各 repo に追加するフィールド
  "forecast_7d": 23687,         // 7日後予測値
  "forecast_ci_lower": 19200,   // 95%CI 下限
  "forecast_ci_upper": 28100,   // 95%CI 上限
  "forecast_all": [...],        // 7日分の全予測値
  "forecast_method": "Holt DES (α=0.3, β=0.1)",

  // 内部状態 (JSON出力から除外される _ prefix フィールド)
  "_data_path": "...",
  "_json_mode": false,
  "_fetch_count": 7,
  "_rendered": true
}
```

---

## 4. Holt 二重指数平滑法の数式

TimesFM のゼロショット予測の思想を軽量実装したもの。

### 更新式

```
レベル: L_t = α * y_t + (1 - α) * (L_{t-1} + T_{t-1})
トレンド: T_t = β * (L_t - L_{t-1}) + (1 - β) * T_{t-1}

h ステップ先の予測:
F_{t+h} = L_t + h * T_t
```

### パラメータ

| パラメータ | 値 | 意味 |
|-----------|-----|------|
| α (alpha) | 0.3 | レベルの平滑化係数 (小さいほど過去データを重視) |
| β (beta)  | 0.1 | トレンドの平滑化係数 (小さいほどトレンドが安定) |
| horizon   | 7日 | 予測ホライゾン |

### 信頼区間（95%）

```
CI: F_{t+h} ± 1.96 * σ * √h
σ: 訓練データ上の残差標準偏差
```

### TimesFM との比較

| 項目 | Google TimesFM | mini-deerflow |
|------|---------------|---------------|
| モデル | Decoder-only Transformer | Holt DES |
| パラメータ数 | 500M | 2個 (α, β) |
| 学習データ | 1,000億タイムポイント | 不要（解析的解） |
| 多変量対応 | あり | なし (univariate) |
| 依存ライブラリ | PyTorch, JAX | なし |
| 推論速度 | GPU推奨 | ~0.1ms/series |
| 精度 | 高 | 中 (stationary trend 仮定) |

---

## 5. スキルパイプラインの実行例

### 基本パイプライン

```bash
# フルパイプライン (ターミナル表示)
python skill_runner.py --pipeline fetch_trending,score_growth,forecast_stars,render_report

# JSON 出力 (CI/CD 連携)
python skill_runner.py --pipeline fetch_trending,score_growth,forecast_stars,render_report --json

# カスタムデータ
python skill_runner.py --pipeline fetch_trending,score_growth,forecast_stars,render_report \
  --data /path/to/my_repos.json

# 利用可能なスキル一覧
python skill_runner.py --list
```

### 部分パイプライン (スコアリングのみ)

```bash
python skill_runner.py --pipeline fetch_trending,score_growth --json
```

---

## 6. 入力データ形式

`data/sample_repos.json` の形式:

```json
{
  "fetched_at": "2026-02-28T00:00:00Z",
  "source": "GitHub Trending (2026-02-28)",
  "repos": [
    {
      "owner": "bytedance",
      "name": "deer-flow",
      "description": "SuperAgent harness",
      "language": "TypeScript",
      "url": "https://github.com/bytedance/deer-flow",
      "star_history": [14200, 15100, 16300, 17800, 18900, 20100, 21500]
    }
  ]
}
```

`star_history` は古い日付から新しい日付の順に 2 件以上の整数リスト。

---

## 7. 終了コード

| コード | 意味 |
|------|------|
| 0 | 正常終了 |
| 1 | スキルのロードまたは実行エラー |

---

## 8. 今後の拡張案

1. **実際の GitHub API 連携**: `fetch_trending` スキルをGitHub API で動的取得に改良
2. **MCP サーバー経由でのデータ取得**: DeerFlow 本家と同様の MCP 統合
3. **カスタムスキル追加**: `skills/` に Python ファイルを置くだけで利用可能
4. **Prophet / ARIMA スキル**: `forecast_stars` の予測精度向上版スキル
5. **Slack/Discord 通知スキル**: `render_report` の出力先を Webhook に変更するスキル
6. **並列スキル実行**: `SkillParallel` クラスで独立スキルを並列実行
