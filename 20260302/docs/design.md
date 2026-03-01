# ai-red-lines 設計ドキュメント

作成日: 2026-03-02

---

## 1. 背景・着想

### Anthropic Pentagon 追放事件（2026-02-27 → 世界規模の話題に）

2026-02-27、トランプ大統領が全連邦機関に Anthropic の使用禁止を命令。
Hegseth 国防長官は Anthropic を「国家安全保障へのサプライチェーンリスク」に指定した。

**追放の直接原因**：Anthropic が提示した **2 つのレッドライン** をPentagon が受け入れなかったこと。

```
Anthropic Red Lines（Anthropic が主張した禁止事項）:
  1. 完全自律型兵器システムへの AI 利用禁止
  2. 米国市民の大量監視への AI 利用禁止
```

この「レッドライン（AI 利用の絶対的禁止ライン）」という概念を、
**コードとして検査可能にする** のが本プロジェクトのアイデア。

### AI が攻撃に悪用された実例（同時期のトレンド）

Amazon Threat Intelligence が報告: 技術力の低い攻撃者が **Anthropic Claude と DeepSeek を使って** 攻撃計画を立案し、55 ヵ国 600 台超の FortiGate を侵害。
→ AI の「使われ方」の監査ツールは単なる政策ツールではなく、セキュリティ上の必需品。

### Deno 2.7 リリース（2026-02-25）とTypeScript #1

Deno v2.7 が `deno audit`（依存関係を CVE DB でスキャン）を搭載してリリース。
TypeScript が GitHub 言語ランキング #1 になり、「Python 以外で CLI ツールを書く」ことへの機運が高まっている。

---

## 2. システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                      main.ts                            │
│                                                         │
│  1. Parse CLI args (--demo, --json, --policy, dir)      │
│  2. Load policy (policy.json or DEFAULT_POLICY)         │
│  3. walkDir() / DEMO_SAMPLES  — ファイル収集            │
│  4. scanContent()             — パターンマッチング      │
│  5. buildResult()             — 統計集計                │
│  6. printReport() / JSON      — 出力                    │
└─────────────────────────────────────────────────────────┘
         ↑                   ↑
    policy.json         ソースコード群
  (AI 利用ポリシー)      (スキャン対象)
```

---

## 3. コアアルゴリズム

### ポリシー評価

```
policy.json
  └── rules[]
        ├── id           — 識別子（例: NO_AUTONOMOUS_WEAPONS）
        ├── severity     — CRITICAL / HIGH / MEDIUM / LOW
        └── patterns[]   — 違反を示す正規表現リスト

違反判定:
  各ファイルの各行に対して全パターンを RegExp(pattern, "gi") で試行
  → 一致した場合 Finding として記録（行番号・マッチ文字列付き）
```

### デフォルトポリシー（Anthropic レッドライン準拠）

| Rule ID | 深刻度 | 検出するもの |
|---------|-------|------------|
| `NO_AUTONOMOUS_WEAPONS` | CRITICAL | "autonomous targeting/weapon/kill/strike" パターン |
| `NO_MASS_SURVEILLANCE`  | CRITICAL | "mass surveillance/bulk monitor citizen" パターン |
| `NO_HARDCODED_AI_KEYS`  | HIGH     | Anthropic・OpenAI・Google AI の API キー文字列 |
| `NO_UNREVIEWED_MODEL_EXECUTION` | MEDIUM | `autoApprove: true`, `skipHumanReview: true` 等 |
| `NO_PII_WITHOUT_CONSENT_FLAG`  | MEDIUM | `sendPII: true`, `piiConsent: false` 等 |

### 結果判定

```
passed = (CRITICAL count == 0) AND (HIGH count == 0)
exit code: 0 = passed, 1 = failed
```

MEDIUM/LOW は警告として表示するが、CI/CD パイプラインを止めない設計。

---

## 4. 対応ファイル種別

```
.ts .tsx .js .jsx .mjs .cjs
.py .rs .go .sh .bash
.json .yaml .yml .env .toml
```

AI SDK は多言語で利用されるため、特定言語に限定しない全文スキャン方式。

---

## 5. ランタイムと依存関係

| 項目 | 詳細 |
|------|------|
| 実行環境 | **bun** (TypeScript ネイティブ) または ts-node + Node.js |
| 外部依存 | **ゼロ** — `node:fs/promises`, `node:path` のみ |
| 型定義 | TypeScript の `interface` でポリシー・結果を厳密に型付け |
| カラー出力 | ANSI エスケープコード直書き（外部ライブラリ不使用） |

> **Deno との互換性について**: 元々 Deno 向けに設計（`Deno.readDir` 等）したが、`node:fs/promises` を使う Node.js 互換 API に書き直して bun でも動作可能にした。Deno 2.7 の `--compat` モードまたは `node:` prefix API サポートにより、Deno でも動作可能。

---

## 6. Policy as Code の思想

本ツールの本質は「**AI 利用ポリシーをバージョン管理可能なコードとして表現する**」こと。

```json
// policy.json をリポジトリに含めることで:
// - ポリシーの変更が git diff で追跡可能
// - CI/CD パイプラインで自動チェック
// - チームレビューのワークフローに組み込み可能
{
  "name": "AI Usage Policy — Red Lines",
  "rules": [
    { "id": "NO_AUTONOMOUS_WEAPONS", "severity": "CRITICAL", ... }
  ]
}
```

Anthropic が Pentagon との交渉で求めた「利用規約への同意」を、
**コードレベルで自動検査可能**にするという逆転の発想。

---

## 7. 実行例

```bash
# デモ（内蔵サンプルコードをスキャン）
bun src/main.ts --demo

# カレントディレクトリをスキャン
bun src/main.ts .

# カスタムポリシーでスキャン
bun src/main.ts --policy src/policy.json /path/to/project

# JSON 出力（CI/CD 向け、exit code 1 = violation）
bun src/main.ts --json --demo
```

---

## 8. AI 利用禁止条件の実例（本家との比較）

| 項目 | Anthropic の要求（実際） | ai-red-lines の実装 |
|------|------------------------|-------------------|
| 自律型兵器禁止 | 利用規約への同意 | `NO_AUTONOMOUS_WEAPONS` パターン検出 |
| 大量監視禁止 | 利用規約への同意 | `NO_MASS_SURVEILLANCE` パターン検出 |
| 人間による監視 | 暗黙的な期待 | `NO_UNREVIEWED_MODEL_EXECUTION` 検出 |
| API キー管理 | 規約外（ベストプラクティス） | `NO_HARDCODED_AI_KEYS` 検出 |
| PII 保護 | 暗黙的な期待 | `NO_PII_WITHOUT_CONSENT_FLAG` 検出 |
