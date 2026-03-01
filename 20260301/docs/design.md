# csi-motion-detector 設計ドキュメント

作成日: 2026-03-01

---

## 1. 背景・着想

### WiFi DensePose (ruvnet/wifi-densepose) — GitHub Trending #1

2026-03-01 に GitHub Trending デイリー 1 位を獲得した `ruvnet/wifi-densepose` は、
WiFi 信号の **CSI（Channel State Information: チャネル状態情報）** を解析して
壁越しに人体の全身ポーズをリアルタイム追跡するシステム。

核心技術は「**CSI 時系列の振幅・位相パターンの変化から動きを検出する**」というアルゴリズムで、
本プロジェクトはそれをゼロ依存の純粋 Python で実装したシミュレーターである。

### CSI とは

WiFi 送受信間の各サブキャリア・各アンテナペアの複素数応答。
人体が WiFi 信号を遮断・反射・吸収すると振幅と位相が変化するため、
この変化のパターンを解析することで「人がいる/動いている」を判定できる。

```
送信機                        受信機
  ├── サブキャリア 1 ─────(人体に反射)──→ 振幅変化 Δ
  ├── サブキャリア 2 ──────────────────→ 振幅安定
  └── サブキャリア n ─────(壁透過後)───→ 位相変化 Φ
```

---

## 2. システムアーキテクチャ

```
┌────────────────────────────────────────────────────────┐
│                    main.py                             │
│                                                        │
│  1. make_default_events()   — Ground Truth 生成        │
│  2. simulate_csi()          — CSI 時系列シミュレーション │
│  3. extract_pca_scores()    — PCA で 1 次元に圧縮       │
│  4. sliding_zscore()        — スライディング Z スコア   │
│  5. aggregate_events()      — イベント集約              │
│  6. print_report() / JSON   — 出力                     │
└────────────────────────────────────────────────────────┘
```

---

## 3. 処理パイプライン詳細

### Step 1: CSI シミュレーション

実際の WiFi ハードウェアがない環境でも動作するよう、
数学的にリアルな CSI 時系列を生成する。

```
振幅(t, a, s) = BASE_AMP
              + intensity(t) × sin(2π × 1.5 × t + phase(a, s))   ← 動き成分（正弦波）
              + Gaussian(0, noise_std)                            ← 熱雑音
```

- `intensity(t)`: Ground Truth イベント中はコサイン包絡線で滑らかに立ち上がる
- `phase(a, s)`: アンテナ a・サブキャリア s ごとの位相オフセット（空間的多様性を模倣）

### Step 2: PCA 次元削減（numpy なし）

アンテナ × サブキャリアの高次元 CSI を主成分分析で 1 次元スコアに圧縮。

**実装アルゴリズム**:
1. フレームを (T × D) 行列にフラット化（D = n_antennas × n_subcarriers）
2. 列平均でセンタリング
3. D > 30 の場合はランダム射影で次元削減（Johnson-Lindenstrauss 近似）
4. 共分散行列 (D × D) を計算
5. **べき乗法 (Power Iteration)** で第 1 主成分ベクトルを収束計算
6. 各フレームを PC1 に射影して 1 次元スコア列を得る

### Step 3: スライディングウィンドウ Z スコア異常検出

```
Z(t) = | (score(t) - μ_window) / σ_window |

μ_window = 過去 W ステップの平均
σ_window = 過去 W ステップの標準偏差
Z(t) >= threshold → 動き検出
```

WiFi DensePose 本家では深層学習（DensePose-RCNN）で骨格推定まで行うが、
「動き有無の検出」という前段処理はこの Z スコア法と原理が近い。

### Step 4: イベント集約

Z スコアが閾値を超えた連続区間を 1 イベントとして集約し、
`min_duration_s`（デフォルト 0.3秒）以下の短すぎる区間を除去（デノイズ）。

---

## 4. パラメータガイド

| パラメータ | デフォルト | 説明 |
|-----------|---------|------|
| `--duration` | 30.0 | シミュレーション時間（秒） |
| `--antennas` | 3 | WiFi アンテナ数（実システムは 3×3=9 ペア推奨） |
| `--subcarriers` | 30 | サブキャリア数（IEEE 802.11n は 64 サブキャリア） |
| `--sample-rate` | 10.0 | CSI 収集レート（Hz）。実システムは最大 100Hz |
| `--threshold` | 1.5 | Z スコア検出閾値。高くすると見逃しが増え誤検知が減る |
| `--window` | 20 | Z スコア計算ウィンドウ幅（サンプル数） |
| `--noise` | 0.15 | ガウスノイズ標準偏差（環境の静寂度に相当） |
| `--seed` | random | 乱数シード（再現性のある実験用） |

---

## 5. WiFi DensePose 本家との比較

| 項目 | ruvnet/wifi-densepose | csi-motion-detector |
|------|----------------------|---------------------|
| 入力 | 実 WiFi CSI（ESP32/TP-Link） | 数学的シミュレーション |
| 出力 | 24 部位の人体ポーズ座標 | 動きイベントの有無・強度 |
| モデル | DensePose-RCNN + Rust | PCA + スライディング Z スコア |
| 精度 | 94.2%（カメラ比較） | recall ~100%、precision ~75% |
| 依存 | Rust, Python, PyTorch | 標準ライブラリのみ |
| ハードウェア | WiFi ルーター 3 台必須 | 不要（純シミュレーション） |
| 用途 | 本番見守り/ポーズ推定 | 学習/アルゴリズム理解 |

---

## 6. 実データへの差し替え方法

実際の WiFi CSI を取得できる場合、`simulate_csi()` の呼び出しを以下に置き換えるだけ:

```python
# 実データ差し替えの例（ESP32 + nexmon_csi などで取得した場合）
import json

def load_real_csi(path: str) -> list[list[list[float]]]:
    """
    CSI データを (T × n_antennas × n_subcarriers) の 3D リストで返す。
    各値は振幅 (sqrt(I^2 + Q^2)) を使用。
    """
    with open(path) as f:
        raw = json.load(f)
    return raw["frames"]

# main() の simulate_csi() 呼び出しをこれに差し替える
csi_data = load_real_csi("path/to/csi_capture.json")
```

---

## 7. 実行例

```bash
# デフォルト 30 秒シミュレーション
python src/main.py

# 再現性のある 60 秒シミュレーション
python src/main.py --duration 60 --seed 2026

# 高精度設定（アンテナ・サブキャリア増加）
python src/main.py --antennas 3 --subcarriers 64 --sample-rate 30 --seed 1

# JSON 出力（CI/CD・パイプライン向け）
python src/main.py --json --seed 42 | python -m json.tool

# 低閾値（感度高・誤検知多）
python src/main.py --threshold 1.0

# 高閾値（感度低・誤検知少）
python src/main.py --threshold 2.5
```
