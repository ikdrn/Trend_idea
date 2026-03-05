# ThreatPulse — 設計ドキュメント

## 概要

**ThreatPulse** は 2026-03-05 の過去24時間トレンドを素材として作成した、
ターミナル完結型のセキュリティ脅威ダッシュボードです。

---

## アーキテクチャ

```
src/main.py
├── データ層（モジュール内定数）
│   ├── CVE_DATA       — 本日の CVE（CVSS スコア / 深刻度 / 製品）
│   ├── DDOS_DATA      — ハクティビスト DDoS 統計
│   └── PRODUCT_RISK   — 製品別リスクマトリクス
│
├── ロジック層
│   └── wifi_risk_score() — ローカル Wi-Fi 環境からリスクスコアを推定
│                           (iwconfig で NIC 検出 → 環境ヒューリスティック)
│
└── 表示層（純粋 ANSI カラー出力）
    ├── render_header()       — タイムスタンプ付きヘッダーボックス
    ├── render_cve()          — CVE テーブル（製品フィルター対応）
    ├── render_ddos()         — DDoS レーダー（棒グラフ）
    ├── render_wifi()         — Wi-Fi プライバシーリスク
    ├── render_product_map()  — 製品別リスクマップ
    └── render_footer()       — ヘルプ表示
```

---

## トレンドとの対応関係

| 本日のトレンド | ThreatPulse の対応機能 |
|--------------|----------------------|
| **RuView** — Wi-Fi で人体追跡（GitHub Trending #2）| `render_wifi()` — Wi-Fi センシングリスク可視化 |
| **CVE-2026-20127** — Cisco SD-WAN CVSS 10.0 | `render_cve()` + `PRODUCT_RISK["cisco"]` |
| **149 件 DDoS** — 16ヶ国 12グループ | `render_ddos()` — リアルデータの棒グラフ |
| **CyberStrikeAI** — AI 駆動型自動攻撃 | `CVE_DATA[3]` — Fortinet スキャン観測データ |
| **MacBook Neo 発売** — 「万人のための Mac」| `PRODUCT_RISK["apple"]` — 低リスク表示 |

---

## 設計上の判断

### 外部依存ゼロ戦略

`pip install` 不要で `python3 src/main.py` 一発実行できることを最優先。
ANSI カラーは標準の ESC コード直書き（`curses` や `rich` を使わない）。

### Wi-Fi リスク評価のアプローチ

実際の Wi-Fi CSI（Channel State Information）の取得には ESP32-S3 等の特殊ハードウェアが必要。
本ツールでは教育目的のデモとして `subprocess` + `iwconfig` でインターフェース有無を検出し、
「Wi-Fi 環境が存在すれば潜在的に RuView 型攻撃に暴露されうる」という概念を数値スコアで伝える。

### ライブモードの設計

`--live` フラグで 5秒インターバルの自動リフレッシュ。
`CLEAR` エスケープ（`\033[2J\033[H`）で画面を毎回クリアし、
Wi-Fi スコアに `±3` の微変動を加えることでライブ感を演出。

---

## データソース（2026-03-05 実際のニュース）

| データ | 出典 |
|-------|------|
| CVE-2026-20127 (CVSS 10.0) | The Hacker News, Cisco Security Advisory |
| CVE-2026-0006, CVE-2026-21385 | Google Android Security Bulletin, CISA KEV |
| DDoS 149件 / 110組織 / 12グループ | The Hacker News (2026-03-05) |
| RuView Wi-Fi DensePose | github.com/ruvnet/RuView (22.4k ⭐) |
| CyberStrikeAI Fortinet スキャン | The Hacker News セキュリティレポート |
| MacBook Neo $599 発売 | Apple, TechCrunch, TechRadar (2026-03-04) |

---

## 実行方法

```bash
# 基本実行（全製品表示）
python3 src/main.py

# 製品フィルター
python3 src/main.py --product cisco      # Cisco 関連のみ
python3 src/main.py --product android    # Android 関連のみ
python3 src/main.py --product fortinet   # Fortinet 関連のみ
python3 src/main.py --product apple      # Apple 関連のみ

# ライブモード（5秒ごと自動更新）
python3 src/main.py --live
python3 src/main.py --live --product android
```

---

## 動作環境

| 条件 | 詳細 |
|------|------|
| Python | 3.10 以上（`str | None` 型ヒント使用） |
| 依存ライブラリ | なし（標準ライブラリのみ） |
| ターミナル | ANSI カラー対応（macOS Terminal / iTerm2 / GNOME Terminal / Windows Terminal） |
| Wi-Fi NIC | なくても動作（リスクスコアが LOW 寄りになるだけ） |
