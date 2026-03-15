# システム開発ドキュメント

---

## 1. 文書情報

| 項目 | 内容 |
|------|------|
| 文書名 | patch-pulse 設計ドキュメント |
| 作成日 | 2026-03-15 |
| 作成者 | Claude Code |
| バージョン | 1.0.0 |
| 更新履歴 | 2026-03-15 初版作成 |

---

## 2. 要件定義

### 2.1 背景

2026-03-10 の Microsoft Patch Tuesday で83件のCVEが公開された。同日前後に n8n (CVE-2026-21858, CVSS 10.0)、Chromium V8/Skia (CISA KEV)、VMware Aria Operations などの重大脆弱性も相次ぎ、セキュリティ担当者が優先順位を付けにくい状況が生じた。脆弱性データを素早く把握・比較できるビジュアルツールが求められている。

### 2.2 目的

- March 2026 Patch Tuesday CVE データを直感的に可視化する
- 実環境悪用 / CISA KEV 掲載の優先度が高いCVEを一目で識別可能にする
- セキュリティ担当者がパッチ適用の優先順位を決定しやすくする

### 2.3 対象範囲

- Microsoft Patch Tuesday 2026-03-10 (83 CVEs)
- 同週に公開された注目CVE（n8n, Chromium, VMware, Cisco, Android）
- CISA KEV 追加分 (2026-03-13)

### 2.4 用語定義

| 用語 | 説明 |
|------|------|
| CVE | Common Vulnerabilities and Exposures。脆弱性の識別番号 |
| CVSS | Common Vulnerability Scoring System。脆弱性の深刻度スコア (0〜10) |
| CISA KEV | CISA が管理する既知悪用脆弱性カタログ。連邦機関は期限内にパッチ適用が義務 |
| Patch Tuesday | Microsoftが毎月第2火曜に行うセキュリティ更新リリース |
| EoP | Elevation of Privilege（特権昇格）脆弱性 |
| RCE | Remote Code Execution（リモートコード実行）脆弱性 |

---

### 2.5 利用者

| ユーザー種別 | 説明 |
|-------------|------|
| セキュリティエンジニア | パッチ優先度の判断・社内報告用に使用 |
| システム管理者 | 影響製品の特定・パッチ適用計画立案 |
| CTI アナリスト | 脅威トレンドの把握・レポート作成 |

---

### 2.6 業務概要

**業務フロー**

1. Patch Tuesday 公開 → CVEデータをJSファイルに整理
2. `index.html` をブラウザで開いてダッシュボード表示
3. フィルターで Critical / In-Wild / KEV に絞り込み
4. ツールチップで各CVEの詳細確認
5. パッチ適用優先度を決定

**業務課題**

- 大量CVEを表形式だけで追うと重要なものを見落としやすい
- 実環境悪用の有無が埋もれて判断が遅れる
- 複数情報源（Microsoft, CISA, ベンダー）をまたぐ集計が手間

---

### 2.7 機能要件

| ID | 機能名 | 概要 | 優先度 |
|----|--------|------|--------|
| FR-01 | サマリーカード | 総CVE数・Critical数・KEV数・最高CVSS をカード表示 | 高 |
| FR-02 | ドーナツチャート | 脆弱性タイプ（EoP/RCE等）の分布を円グラフ表示 | 高 |
| FR-03 | スキャッタープロット | 製品 × CVSS スコアの散布図、悪用済みを強調 | 高 |
| FR-04 | バブルチャート | タイプ × 平均CVSS のバブル（件数=サイズ）マトリクス | 中 |
| FR-05 | CVE テーブル | 全注目CVEを CVSS バーとアイコン付きで一覧表示 | 高 |
| FR-06 | フィルター機能 | テーブルを Critical/実環境悪用/CISA KEV で絞り込み | 高 |
| FR-07 | インタラクティブツールチップ | ホバーで詳細情報をポップアップ表示 | 中 |

---

### 2.8 非機能要件

**性能**

- ブラウザ初期表示 2 秒以内（D3.js CDN ロード込み）
- データは全てクライアントサイドで処理、サーバーリクエスト不要

**可用性**

- オフライン環境ではD3.js CDNが使えないため動作しない（許容）
- 外部APIキー不要

**セキュリティ**

- 外部入力を一切受け取らないため XSS リスクは限定的
- CDN（jsdelivr.net）からのスクリプト読み込みのみ

**運用・保守**

- `data.js` のCVEデータを更新するだけで新しい月に対応可能

---

### 2.9 制約条件

- ブラウザの ESモジュール対応が必要（Chrome/Firefox/Safari 最新版を想定）
- CDN アクセスが必要（D3.js v7）

---

### 2.10 前提条件

- ローカルサーバーなしで動作（file:// プロトコルまたは http://localhost）
- 有料 API・外部認証不要

---

## 3. 基本設計

### 3.1 システム構成

**システム構成図**

```
ブラウザ
├── index.html  (エントリポイント)
├── style.css   (ダークテーマ CSS)
├── main.js     (D3.js 可視化ロジック / ESモジュール)
└── data.js     (CVE データ定義 / ESモジュール)
         ↓
    D3.js v7 (CDN: jsdelivr.net)
```

**技術スタック**

| 分類 | 内容 |
|------|------|
| OS | 不問（ブラウザ動作） |
| 言語 | HTML5 / CSS3 / JavaScript (ES2022) |
| フレームワーク | D3.js v7 |
| DB | なし（データはJSファイルに内包） |

---

### 3.2 機能一覧

| ID | 機能名 | 概要 |
|----|--------|------|
| F-01 | Stats Row | 6枚のサマリーカード（総数・Critical・Important・KEV・実環境・最高CVSS） |
| F-02 | Donut Chart | D3 pie/arc で脆弱性タイプ分布を可視化 |
| F-03 | Scatter Plot | D3 scaleLinear × scaleBand で製品×CVSSスコアをプロット |
| F-04 | Bubble Matrix | D3 scaleSqrt でバブルサイズを件数にマッピング |
| F-05 | CVE Table | フィルター対応テーブル、CVSS バー・アイコン付き |
| F-06 | Tooltip | mouseover/mousemove/mouseout で動的ポップアップ |

---

### 3.3 画面設計

| 画面ID | 画面名 | 概要 |
|--------|--------|------|
| SCR-01 | メインダッシュボード | 全機能を1ページに集約したSPA |

**画面遷移図**

- シングルページアプリケーション。ページ遷移なし。
- フィルターボタンでテーブル内容のみ動的更新。

**レイアウト（モバイル考慮済み）**

```
Header: ロゴ・バッジ・サブタイトル
Stats Row: 6カラムグリッド（モバイル: 2カラム）
Charts Grid: 2カラム（モバイル: 1カラム）
  ├─ Donut Chart
  ├─ Scatter Plot
  └─ Bubble Matrix (full-width)
CVE Table: フィルターバー + テーブル
Footer: データ源リンク
```

---

### 3.4 API設計

| API ID | エンドポイント | 概要 | メソッド |
|--------|--------------|------|---------|
| - | なし | 外部API連携なし | - |

---

### 3.5 データ設計

**ER図**

- ファイルベース。DBなし。

**テーブル一覧**

| データ名 | 概要 |
|---------|------|
| cveByType | 脆弱性タイプ別集計（6種類） |
| notableCVEs | 注目CVE詳細（14件） |
| patchTuesdayData | Patch Tuesday サマリー情報 |
| weeklyTrend | 週次CVE公開トレンド（参考値） |

---

### 3.6 外部連携

| 連携先 | 概要 |
|--------|------|
| jsdelivr.net CDN | D3.js v7 ライブラリ読み込み |

---

### 3.7 エラー処理

- CDN 読み込み失敗時：D3 未定義エラーがコンソールに出力。フォールバックなし（許容）。
- データ不整合：D3 のスケール計算でNaNが出た場合、要素が非表示になる。

---

### 3.8 ログ設計

- クライアントサイドのみ。コンソールログなし（本番考慮不要）。

---

### 3.9 セキュリティ設計

- 外部ユーザー入力なし → XSS リスクなし
- フィルターはdata-filter属性の固定値のみ使用
- CDN スクリプトはサブリソース整合性（SRI）を未設定（開発用途のため許容）

---

## 4. 詳細設計

### 4.1 モジュール一覧

| モジュールID | モジュール名 | 概要 |
|------------|------------|------|
| M-01 | data.js | CVEデータ定義。ESモジュールとしてエクスポート |
| M-02 | main.js | D3.js 可視化。renderDonut / renderScatter / renderBubble / renderTable の4関数 |
| M-03 | style.css | CSS変数ベースのダークテーマ |

---

### 4.2 クラス設計

- クラス不使用（関数型スタイル）

**主要関数**

| メソッド名 | 引数 | 戻り値 | 説明 |
|-----------|------|--------|------|
| renderDonut | なし | void | ドーナツチャートをSVGに描画 |
| renderScatter | なし | void | 散布図をSVGに描画 |
| renderBubble | なし | void | バブルマトリクスをSVGに描画 |
| renderTable | filter: string | void | CVEテーブルをHTMLに動的生成 |
| showTooltip | event, html | void | ツールチップを表示・配置 |
| moveTooltip | event | void | ツールチップ位置を追従 |
| hideTooltip | なし | void | ツールチップを非表示 |
| cvssColor | score: number | string | CVSSスコアに応じたCSSカラー変数を返す |

---

### 4.3 処理フロー

```
DOMContentLoaded
  └─ renderDonut()
       ├─ D3 pie() で cveByType を角度計算
       ├─ arc() でパス生成
       ├─ mouseover → showTooltip()
       └─ 凡例HTMLをDOMに注入

  └─ renderScatter()
       ├─ scaleLinear (x: CVSS 6〜10.5)
       ├─ scaleBand (y: 製品名)
       ├─ circle 描画（in_wild → r拡大、cisa_kev → stroke色変更）
       └─ mouseover → showTooltip()

  └─ renderBubble()
       ├─ rollup() でCVEをタイプ別に集計
       ├─ scaleSqrt (r: 件数)
       ├─ circle 描画
       └─ text ラベル（件数）

  └─ renderTable("all")
       ├─ notableCVEs をCVSS降順ソート
       └─ HTMLテーブル行を動的生成

filter-btn.click
  └─ renderTable(filter)
```

---

### 4.4 API詳細

- 外部API連携なし

---

### 4.5 テーブル定義

**notableCVEs（JSオブジェクト配列）**

| カラム | 型 | 説明 |
|--------|-----|------|
| id | string | CVE ID (例: CVE-2026-21536) |
| product | string | 影響製品名 |
| type | string | 脆弱性タイプ |
| severity | string | "Critical" または "Important" |
| cvss | number | CVSSv3.1 スコア (0〜10) |
| auth_required | boolean | 認証が必要か |
| user_interaction | boolean | ユーザー操作が必要か |
| attack_vector | string | 攻撃ベクター |
| description | string | 概要文 |
| in_wild | boolean | 実環境での悪用確認済みか |
| cisa_kev | boolean | CISA KEV 掲載済みか |

---

### 4.6 バリデーション

| 項目 | 条件 | エラーメッセージ |
|------|------|----------------|
| CVSS スコア | 0〜10 の数値 | D3スケールでNaN → 要素非表示 |
| フィルター値 | data-filter 属性の固定値のみ | - |

---

### 4.7 例外処理

- D3.js 未ロード時はコンソールエラーのみ（フォールバックなし）

---

## 5. 単体テスト

### 5.1 テスト対象

- cvssColor() 関数
- renderTable() のフィルター処理

---

### 5.2 テスト環境

| 項目 | 内容 |
|------|------|
| OS | Linux (開発機) / Chrome |
| 言語 | JavaScript (ES2022) |
| DB | なし |

---

### 5.3 テストケース

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-01 | cvssColor: CVSS 10.0 | 10.0 | "var(--critical)" |
| UT-02 | cvssColor: CVSS 8.5 | 8.5 | "var(--orange)" |
| UT-03 | cvssColor: CVSS 7.0 | 7.0 | "var(--yellow)" |
| UT-04 | renderTable: filter=Critical | "Critical" | Critical のみ14→8行に絞り込み |
| UT-05 | renderTable: filter=wild | "wild" | in_wild=true のCVEのみ表示 |
| UT-06 | renderTable: filter=kev | "kev" | cisa_kev=true のCVEのみ表示 |

---

### 5.4 境界値テスト

| 項目 | 条件 | 期待結果 |
|------|------|---------|
| CVSS | 9.0（境界） | "var(--critical)" |
| CVSS | 8.99 | "var(--orange)" |
| CVSS | 7.0 | "var(--yellow)" |

---

### 5.5 異常系テスト

| TC ID | テスト内容 | 入力 | 期待結果 |
|-------|-----------|------|---------|
| UT-E01 | CDN読み込み失敗 | D3未定義 | コンソールエラー、白紙ページ |
| UT-E02 | 空データ | cveByType=[] | 空のドーナツ表示 |

---

### 5.6 テスト結果

| TC ID | 結果 | 備考 |
|-------|------|------|
| UT-01〜06 | 手動確認OK | ブラウザコンソールで動作確認済み |

---

## 6. 結合テスト

### 6.1 テスト目的

data.js のデータが main.js の各チャートに正しく反映されることを確認する。

---

### 6.2 テスト範囲

- data.js → renderDonut()
- data.js → renderScatter()
- data.js → renderBubble()
- data.js → renderTable()

---

### 6.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | Chrome / Firefox（最新版） |
| DB | なし |

---

### 6.4 テストシナリオ

| シナリオID | 内容 |
|----------|------|
| IT-01 | ページロード後、全チャートが正しく描画される |
| IT-02 | フィルターボタン操作でテーブルが正しく絞り込まれる |
| IT-03 | ホバーでツールチップが正しい情報を表示する |

---

### 6.5 テストケース

| TC ID | シナリオ | 手順 | 期待結果 |
|-------|---------|------|---------|
| IT-01-01 | ページロード | index.html を開く | ドーナツ・散布図・バブル・テーブルが表示 |
| IT-02-01 | フィルター | "Critical のみ" ボタンを押す | テーブルが Critical CVE のみに絞られる |
| IT-03-01 | ツールチップ | scatter chart の dot にホバー | CVE ID・製品名・CVSS・説明が表示 |

---

### 6.6 不具合管理

| ID | 内容 | 対応状況 |
|----|------|---------|
| - | 不具合なし | - |

---

## 7. 総合テスト

### 7.1 テスト目的

ブラウザ上でエンドツーエンドの動作を確認する。

---

### 7.2 テスト範囲

- Chrome / Firefox での表示
- モバイル幅（375px）でのレスポンシブ確認
- ツールチップのビューポート端での位置補正

---

### 7.3 テスト環境

| 項目 | 内容 |
|------|------|
| 環境 | Chrome 最新版 |
| サーバ | file:// または localhost |
| DB | なし |

---

### 7.4 業務シナリオ

| シナリオID | 内容 |
|----------|------|
| ST-01 | セキュリティエンジニアが Patch Tuesday 後にダッシュボードで優先CVEを確認 |

---

### 7.5 テストケース

| TC ID | シナリオ | 操作 | 期待結果 |
|-------|---------|------|---------|
| ST-01-01 | 優先CVE確認 | "実環境悪用あり" フィルターを選択 | n8n・Chromium等の実悪用CVEのみ表示 |
| ST-01-02 | 優先CVE確認 | "CISA KEV" フィルターを選択 | KEV掲載3件のみ表示 |
| ST-01-03 | 詳細確認 | バブルチャートの RCE バブルにホバー | 件数・平均CVSS・実悪用数がポップアップ |

---

### 7.6 受入基準

- 全チャートが初回ロードで2秒以内に表示される
- フィルター操作が即時反映される
- モバイル幅（375px）でレイアウト崩れがない

---

### 7.7 テスト結果

| TC ID | 結果 | 備考 |
|-------|------|------|
| ST-01-01 | OK | - |
| ST-01-02 | OK | - |
| ST-01-03 | OK | - |
