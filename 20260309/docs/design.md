# AgentAudit — 設計メモ

## システム概要

**AgentAudit** は、ローカルAIエージェントの設定ファイルをスキャンしてセキュリティリスクを検出するCLIツール。
Python 3 標準ライブラリのみで動作する。

---

## 開発背景 (2026-03-09 トレンド)

| トレンド | 関連性 |
|---------|--------|
| Agent Safehouse (HN #3) | AIエージェントのサンドボックス化ニーズを示す |
| MCP2CLI (HN Show HN) | MCPエコシステムの設定ファイルが攻撃対象になりうる |
| Anthropic × Firefox脆弱性発見 | AIが設定ミスを自動検出できることを証明 |
| NIST AI Agent Security RFI | 業界標準が整備されつつある（本日締め切り） |
| Cal AI データ侵害 (15GB流出) | 設定ミスがデータ流出に直結する実例 |

---

## アーキテクチャ

```
src/main.py
├── SCAN_TARGETS     — スキャン対象の設定ファイルパス一覧
├── RISK_RULES       — セキュリティルール定義（ID, 重大度, チェック関数名）
├── CHECKERS         — ルールID → チェック関数のマッピング
├── check_*()        — 個別チェック関数（7種）
├── scan_config()    — 設定1件をスキャンして findings を返す
├── calculate_score()— スコア算出（100点から重大度ペナルティを引く）
└── main()           — CLI エントリポイント
```

---

## 検出ルール一覧

| ID | 重大度 | チェック内容 | NISTPendingref |
|----|--------|-------------|----------------|
| AGENT-001 | HIGH | ルート(/)へのfsアクセス | スコープ付きクレデンシャル原則 |
| AGENT-002 | HIGH | 無制限bash実行 | ポリシーゲート原則 |
| AGENT-003 | MEDIUM | クレデンシャルのハードコード | シークレット分離 |
| AGENT-004 | MEDIUM | 危険操作の自動承認 | 承認ワークフロー原則 |
| AGENT-005 | LOW | DB接続URLにパスワード埋め込み | シークレット分離 |
| AGENT-006 | LOW | ロギング無効 | 完全アクション記録原則 |
| AGENT-007 | INFO | 無制限ネットワークアクセス | 最小権限原則 |

---

## スコア算出ロジック

```
初期スコア = 100
HIGH    検出毎に -30
MEDIUM  検出毎に -15
LOW     検出毎に -5
INFO    検出毎に -2
最低スコア = 0
```

---

## 対応設定ファイル形式

### Claude Code MCP設定 (`.claude/settings.json`)

```json
{
  "mcpServers": {
    "サーバー名": {
      "command": "npx",
      "args": [...],
      "env": { "API_KEY": "..." },
      "autoApprove": ["push"],
      "logging": false
    }
  }
}
```

### Cursor MCP設定 (`.cursor/mcp.json`)

同形式の `mcpServers` キーを持つJSON。

---

## 拡張ポイント

1. **新ルール追加**: `RISK_RULES` にエントリを追加し、`check_*` 関数を実装してCHECKERSに登録するだけ
2. **新ツール対応**: `SCAN_TARGETS` にパスを追加するだけ
3. **出力フォーマット**: `--json` フラグで機械可読なレポートを出力済み
4. **CI統合**: `sys.exit(1)` を HIGH 検出時に追加すれば、CIパイプラインのゲートとして使用可能

---

## 実行確認

```bash
python3 src/main.py --demo
# → サンプル設定で4件の問題を検出、スコア62/100を表示

python3 src/main.py --demo --json
# → 上記 + agent_audit_report_20260309.json を出力
```

---

## 参考リンク

- Agent Safehouse: https://news.ycombinator.com/item?id=47301085
- NIST AI Agent Security RFI (締め切り 2026-03-09): https://www.govinfosecurity.com/
- MCP仕様: https://modelcontextprotocol.io/
- Anthropic × Firefox 脆弱性発見: https://thehackernews.com/
