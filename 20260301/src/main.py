#!/usr/bin/env python3
"""
csi-motion-detector / main.py
==============================
WiFi CSI（Channel State Information）時系列異常検出シミュレーター

2026-03-01 トレンドの掛け合わせ:
  - ruvnet/wifi-densepose (GitHub Trending #1): WiFi CSI による壁越し人体追跡
  - 「Build, Don't Buy」(Zenn 話題記事): ゼロ依存で核心アルゴリズムを自前実装
  - Kilo Code Reviewer (Product Hunt #2): 「信号から異常を即座に検出」の発想

WiFi DensePose の核心技術「CSI の変化パターンから動きを検出する」を
実際の WiFi ハードウェア不要・標準ライブラリのみで体験できる CLI ツール。

使用方法:
  python src/main.py
  python src/main.py --duration 60 --antennas 3 --subcarriers 30 --seed 42
  python src/main.py --json

依存関係: 標準ライブラリのみ
"""

import argparse
import json
import math
import random
import sys
from dataclasses import dataclass, field
from typing import Optional

# ────────────────────────────────────────────
# ANSI カラー
# ────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"


# ────────────────────────────────────────────
# CSI シミュレーター
# ────────────────────────────────────────────

@dataclass
class MotionEvent:
    """シミュレーション中の動きイベント定義"""
    start: float      # 開始時刻 (秒)
    duration: float   # 継続時間 (秒)
    intensity: float  # 動きの強度 (1.0=歩行, 3.0=高速移動)
    label: str        # ラベル


def simulate_csi(
    duration_s: float,
    sample_rate: float,
    n_antennas: int,
    n_subcarriers: int,
    events: list[MotionEvent],
    noise_std: float,
    rng: random.Random,
) -> list[list[list[float]]]:
    """
    CSI 振幅時系列データをシミュレートする。

    WiFi DensePose では各アンテナペア×サブキャリアの複素 CSI を計測するが、
    ここでは振幅（絶対値）のみを模倣する。

    静止状態: 基準振幅 + ガウスノイズ
    動き状態: 基準振幅 + 動き振幅（正弦波で体の揺れを模倣）+ ノイズ

    Returns:
        data[t][antenna][subcarrier] の 3 次元リスト
    """
    n_samples = int(duration_s * sample_rate)
    BASE_AMP = 1.0  # 基準 CSI 振幅

    # 動きイベントをタイムラインに展開
    def motion_intensity_at(t: float) -> float:
        for ev in events:
            if ev.start <= t < ev.start + ev.duration:
                # 立ち上がり/立ち下がりを滑らかにするためコサイン窓
                progress = (t - ev.start) / ev.duration
                envelope = math.sin(math.pi * progress)
                return ev.intensity * envelope
        return 0.0

    data = []
    for i in range(n_samples):
        t = i / sample_rate
        motion = motion_intensity_at(t)
        frame = []
        for a in range(n_antennas):
            row = []
            for s in range(n_subcarriers):
                # アンテナ・サブキャリアごとに位相オフセットを持つ正弦波で「体の揺れ」を表現
                phase = 2 * math.pi * (a * 0.3 + s * 0.1)
                wave = motion * math.sin(2 * math.pi * 1.5 * t + phase)
                noise = rng.gauss(0, noise_std)
                amplitude = BASE_AMP + wave + noise
                row.append(amplitude)
            frame.append(row)
        data.append(frame)

    return data


# ────────────────────────────────────────────
# 特徴抽出 — 超軽量 PCA（標準ライブラリのみ）
# ────────────────────────────────────────────

def mat_transpose(m: list[list[float]]) -> list[list[float]]:
    rows, cols = len(m), len(m[0])
    return [[m[r][c] for r in range(rows)] for c in range(cols)]


def mat_multiply(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    rA, cA = len(A), len(A[0])
    rB, cB = len(B), len(B[0])
    assert cA == rB
    C_ = [[0.0] * cB for _ in range(rA)]
    for i in range(rA):
        for j in range(cB):
            s = 0.0
            for k in range(cA):
                s += A[i][k] * B[k][j]
            C_[i][j] = s
    return C_


def column_means(m: list[list[float]]) -> list[float]:
    rows, cols = len(m), len(m[0])
    return [sum(m[r][c] for r in range(rows)) / rows for c in range(cols)]


def center_matrix(m: list[list[float]]) -> list[list[float]]:
    means = column_means(m)
    return [[m[r][c] - means[c] for c in range(len(m[0]))] for r in range(len(m))]


def power_iteration(cov: list[list[float]], n_iter: int = 20, rng: Optional[random.Random] = None) -> list[float]:
    """べき乗法で最大固有ベクトルを求める（1 次主成分方向）"""
    n = len(cov)
    rng = rng or random.Random(0)
    v = [rng.gauss(0, 1) for _ in range(n)]
    norm = math.sqrt(sum(x * x for x in v))
    v = [x / norm for x in v]
    for _ in range(n_iter):
        # v = cov @ v
        new_v = [sum(cov[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x * x for x in new_v))
        if norm < 1e-12:
            break
        v = [x / norm for x in new_v]
    return v


def extract_pca_scores(data: list[list[list[float]]], rng: random.Random) -> list[float]:
    """
    各フレームの (n_antennas × n_subcarriers) 次元 CSI を
    1 次主成分スコアに射影して 1 次元時系列を返す。

    numpy なしで実装:
    1. フレームをフラット化して (T × D) 行列を作成
    2. 列平均でセンタリング
    3. 共分散行列を計算
    4. べき乗法で第 1 主成分ベクトルを取得
    5. 各フレームを射影してスコアを得る
    """
    T = len(data)
    D = len(data[0]) * len(data[0][0])  # n_antennas × n_subcarriers

    # フラット化: (T × D)
    X = [[val for row in frame for val in row] for frame in data]

    # センタリング
    Xc = center_matrix(X)

    # 共分散行列 (D × D) — 小さい次元に限定して計算可能にする
    # D が大きすぎる場合はランダム射影でダウンサンプリング
    MAX_DIM = 30
    if D > MAX_DIM:
        # ランダム投影で次元削減 (D → MAX_DIM)
        rng2 = random.Random(999)
        proj = [[rng2.gauss(0, 1 / math.sqrt(MAX_DIM)) for _ in range(MAX_DIM)] for _ in range(D)]
        Xc = mat_multiply(Xc, proj)
        D = MAX_DIM

    # 共分散行列
    Xt = mat_transpose(Xc)
    cov = mat_multiply(Xt, Xc)
    cov = [[cov[i][j] / T for j in range(D)] for i in range(D)]

    # 第 1 主成分
    pc1 = power_iteration(cov, n_iter=30, rng=rng)

    # 射影スコア
    scores = [sum(Xc[t][d] * pc1[d] for d in range(D)) for t in range(T)]
    return scores


# ────────────────────────────────────────────
# 異常検出 — スライディングウィンドウ Z スコア
# ────────────────────────────────────────────

def sliding_zscore(
    scores: list[float],
    window: int,
    threshold: float,
) -> list[float]:
    """
    スライディングウィンドウ Z スコアで動き強度を計算する。

    各時刻 t について、過去 window ステップの平均・標準偏差を計算し、
    現在値の偏差（Z スコア）を返す。Z スコアが threshold を超えると動きを検出。

    これが WiFi DensePose において「静止 vs 動き」を判別する基礎となる処理。
    """
    n = len(scores)
    z_scores = []
    for i in range(n):
        start = max(0, i - window)
        window_data = scores[start:i] if i > 0 else [scores[0]]
        if len(window_data) < 2:
            z_scores.append(0.0)
            continue
        mean = sum(window_data) / len(window_data)
        variance = sum((x - mean) ** 2 for x in window_data) / len(window_data)
        std = math.sqrt(variance) if variance > 0 else 1e-9
        z_scores.append(abs((scores[i] - mean) / std))
    return z_scores


# ────────────────────────────────────────────
# イベント集約
# ────────────────────────────────────────────

@dataclass
class DetectedEvent:
    start_t: float
    end_t:   float
    peak_score: float
    avg_score:  float
    label: str = "MOTION"

    @property
    def duration(self) -> float:
        return self.end_t - self.start_t

    def confidence(self) -> str:
        if self.peak_score >= 3.0:
            return "HIGH"
        elif self.peak_score >= 1.5:
            return "MEDIUM"
        return "LOW"


def aggregate_events(
    z_scores: list[float],
    sample_rate: float,
    threshold: float,
    min_duration_s: float = 0.3,
) -> list[DetectedEvent]:
    """Z スコアが閾値を超えた連続区間をイベントとして集約する"""
    events: list[DetectedEvent] = []
    in_event = False
    start_idx = 0
    event_scores: list[float] = []

    for i, z in enumerate(z_scores):
        if z >= threshold and not in_event:
            in_event = True
            start_idx = i
            event_scores = [z]
        elif z >= threshold and in_event:
            event_scores.append(z)
        elif z < threshold and in_event:
            in_event = False
            duration = (i - start_idx) / sample_rate
            if duration >= min_duration_s:
                events.append(DetectedEvent(
                    start_t=start_idx / sample_rate,
                    end_t=i / sample_rate,
                    peak_score=max(event_scores),
                    avg_score=sum(event_scores) / len(event_scores),
                ))
            event_scores = []

    # 末尾まで続いているイベント
    if in_event and event_scores:
        duration = (len(z_scores) - start_idx) / sample_rate
        if duration >= min_duration_s:
            events.append(DetectedEvent(
                start_t=start_idx / sample_rate,
                end_t=len(z_scores) / sample_rate,
                peak_score=max(event_scores),
                avg_score=sum(event_scores) / len(event_scores),
            ))

    return events


# ────────────────────────────────────────────
# ターミナル表示
# ────────────────────────────────────────────

BAR_CHARS = " ▁▂▃▄▅▆▇█"

def amp_bar(value: float, max_val: float = 5.0, width: int = 10) -> str:
    ratio = min(max(value / max_val, 0.0), 1.0)
    idx = round(ratio * (len(BAR_CHARS) - 1))
    return BAR_CHARS[idx] * width

def score_bar(value: float, max_val: float = 5.0, width: int = 10) -> str:
    ratio = min(max(value / max_val, 0.0), 1.0)
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)

def print_report(
    duration_s: float,
    sample_rate: float,
    n_antennas: int,
    n_subcarriers: int,
    z_scores: list[float],
    detected: list[DetectedEvent],
    ground_truth: list[MotionEvent],
    threshold: float,
):
    print(f"\n{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}║      CSI Motion Detector v1.0  —  2026-03-01           ║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}║  Inspired by ruvnet/wifi-densepose (GitHub Trending #1) ║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}╚══════════════════════════════════════════════════════════╝{C.RESET}\n")

    print(f"  {C.BOLD}Config:{C.RESET} {duration_s:.0f}s · {n_antennas} antennas × {n_subcarriers} subcarriers "
          f"· {sample_rate:.0f} Hz · threshold={threshold}")
    print(f"  {C.DIM}PCA + Sliding-window Z-score anomaly detection (numpy-free){C.RESET}\n")

    # タイムライン表示（間引いて表示）
    step = max(1, int(sample_rate))  # 1秒ごと
    n_samples = len(z_scores)
    print(f"  {C.BOLD}{'Time':>6}  {'Z-Score':>8}  {'Motion Bar':<12}  Status{C.RESET}")
    print("  " + "─" * 58)

    for i in range(0, n_samples, step):
        t = i / sample_rate
        z = z_scores[i]
        bar = score_bar(z, max_val=5.0, width=12)

        # このフレームが ground truth のイベント中か判定
        gt_label = ""
        for ev in ground_truth:
            if ev.start <= t < ev.start + ev.duration:
                gt_label = f"[GT: {ev.label}]"
                break

        # 検出イベント中か
        det_label = ""
        color = C.DIM
        for ev in detected:
            if ev.start_t <= t < ev.end_t:
                conf = ev.confidence()
                conf_color = C.RED if conf == "HIGH" else C.YELLOW
                det_label = f"{conf_color}[MOTION {conf}]{C.RESET}"
                color = C.WHITE
                break

        z_color = C.RED if z >= threshold else (C.YELLOW if z >= threshold * 0.6 else C.DIM)
        print(
            f"  {color}{t:>5.1f}s{C.RESET}  "
            f"{z_color}{z:>8.2f}{C.RESET}  "
            f"{C.CYAN}{bar}{C.RESET}  "
            f"{det_label} {C.DIM}{gt_label}{C.RESET}"
        )

    print()
    print("  " + "─" * 58)

    # 検出イベントサマリー
    print(f"\n  {C.BOLD}Detected Events: {len(detected)}{C.RESET}")
    if not detected:
        print(f"  {C.DIM}No motion events detected.{C.RESET}")
    else:
        for i, ev in enumerate(detected, 1):
            conf = ev.confidence()
            conf_color = C.RED if conf == "HIGH" else C.YELLOW
            print(
                f"  {conf_color}Event {i}:{C.RESET}  "
                f"{ev.start_t:.1f}s – {ev.end_t:.1f}s  "
                f"({ev.duration:.1f}s)  "
                f"peak={ev.peak_score:.2f}  avg={ev.avg_score:.2f}  "
                f"confidence={conf_color}{conf}{C.RESET}"
            )

    # Ground Truth との比較
    print(f"\n  {C.BOLD}Ground Truth Events: {len(ground_truth)}{C.RESET}")
    for ev in ground_truth:
        print(f"  {C.GREEN}●{C.RESET} {ev.start:.1f}s – {ev.start + ev.duration:.1f}s  "
              f"intensity={ev.intensity:.1f}  [{ev.label}]")

    # 精度評価（簡易）
    tp = sum(
        1 for gt in ground_truth
        if any(
            det.start_t < gt.start + gt.duration and det.end_t > gt.start
            for det in detected
        )
    )
    precision = tp / len(detected) if detected else 0.0
    recall    = tp / len(ground_truth) if ground_truth else 0.0

    print(f"\n  {C.BOLD}Simple Accuracy:{C.RESET}")
    print(f"  Precision: {C.GREEN}{precision:.0%}{C.RESET}  "
          f"Recall: {C.GREEN}{recall:.0%}{C.RESET}  "
          f"(TP={tp}/{len(ground_truth)} GT events covered)")
    print()
    print(f"  {C.DIM}Algorithm: PCA (power iteration) + Sliding Z-score{C.RESET}")
    print(f"  {C.DIM}Inspired by WiFi-DensePose CSI anomaly detection pipeline{C.RESET}\n")


# ────────────────────────────────────────────
# エントリポイント
# ────────────────────────────────────────────

def make_default_events(duration_s: float, rng: random.Random) -> list[MotionEvent]:
    """デモ用のランダムなモーションイベントを生成"""
    events = []
    t = rng.uniform(2.0, max(3.0, duration_s * 0.1))
    while t < duration_s - 3.0:
        dur = rng.uniform(1.5, min(5.0, duration_s * 0.2))
        intensity = rng.uniform(1.0, 4.0)
        label = "fast movement" if intensity > 2.5 else "walking"
        events.append(MotionEvent(start=t, duration=dur, intensity=intensity, label=label))
        t += dur + rng.uniform(3.0, max(4.0, duration_s * 0.15))
    return events


def main():
    parser = argparse.ArgumentParser(
        description="CSI Motion Detector — WiFi DensePose コアアルゴリズムのシミュレーター"
    )
    parser.add_argument("--duration",    type=float, default=30.0,  help="シミュレーション秒数 (default: 30)")
    parser.add_argument("--antennas",    type=int,   default=3,     help="アンテナ数 (default: 3)")
    parser.add_argument("--subcarriers", type=int,   default=30,    help="サブキャリア数 (default: 30)")
    parser.add_argument("--sample-rate", type=float, default=10.0,  help="サンプリングレート Hz (default: 10)")
    parser.add_argument("--threshold",   type=float, default=1.5,   help="検出閾値 Z スコア (default: 1.5)")
    parser.add_argument("--window",      type=int,   default=20,    help="スライディングウィンドウサイズ (default: 20)")
    parser.add_argument("--noise",       type=float, default=0.15,  help="ガウスノイズ標準偏差 (default: 0.15)")
    parser.add_argument("--seed",        type=int,   default=None,  help="乱数シード (再現性用)")
    parser.add_argument("--json",        action="store_true",       help="JSON 形式で結果を出力")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.randint(0, 99999)
    rng = random.Random(seed)

    if not args.json:
        print(f"\n{C.CYAN}{C.BOLD}CSI Motion Detector  —  2026-03-01{C.RESET}")
        print(f"{C.DIM}Seed: {seed}  |  ruvnet/wifi-densepose インスパイア  |  ゼロ外部依存{C.RESET}\n")
        print(f"  Simulating {args.duration:.0f}s of WiFi CSI data "
              f"({args.antennas} antennas × {args.subcarriers} subcarriers)...")

    # 1. Ground truth イベント生成
    gt_events = make_default_events(args.duration, rng)

    # 2. CSI データシミュレーション
    csi_data = simulate_csi(
        duration_s=args.duration,
        sample_rate=args.sample_rate,
        n_antennas=args.antennas,
        n_subcarriers=args.subcarriers,
        events=gt_events,
        noise_std=args.noise,
        rng=rng,
    )

    # 3. PCA で 1 次元スコアに圧縮
    if not args.json:
        print("  Extracting PCA features (power iteration, numpy-free)...")
    pca_scores = extract_pca_scores(csi_data, rng=rng)

    # 4. スライディングウィンドウ Z スコア異常検出
    z_scores = sliding_zscore(pca_scores, window=args.window, threshold=args.threshold)

    # 5. イベント集約
    detected = aggregate_events(z_scores, sample_rate=args.sample_rate, threshold=args.threshold)

    # 6. 出力
    if args.json:
        tp = sum(
            1 for gt in gt_events
            if any(d.start_t < gt.start + gt.duration and d.end_t > gt.start for d in detected)
        )
        result = {
            "config": {
                "duration_s": args.duration,
                "n_antennas": args.antennas,
                "n_subcarriers": args.subcarriers,
                "sample_rate": args.sample_rate,
                "threshold": args.threshold,
                "window": args.window,
                "seed": seed,
            },
            "ground_truth": [
                {"start": e.start, "duration": e.duration, "intensity": e.intensity, "label": e.label}
                for e in gt_events
            ],
            "detected_events": [
                {
                    "start_t": e.start_t, "end_t": e.end_t,
                    "duration": e.duration,
                    "peak_score": round(e.peak_score, 3),
                    "avg_score": round(e.avg_score, 3),
                    "confidence": e.confidence(),
                }
                for e in detected
            ],
            "summary": {
                "gt_events": len(gt_events),
                "detected_events": len(detected),
                "true_positives": tp,
                "precision": round(tp / len(detected), 3) if detected else 0.0,
                "recall": round(tp / len(gt_events), 3) if gt_events else 0.0,
            }
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(
            duration_s=args.duration,
            sample_rate=args.sample_rate,
            n_antennas=args.antennas,
            n_subcarriers=args.subcarriers,
            z_scores=z_scores,
            detected=detected,
            ground_truth=gt_events,
            threshold=args.threshold,
        )


if __name__ == "__main__":
    main()
