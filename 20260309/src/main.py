#!/usr/bin/env python3
"""
AgentAudit v1.0 — AIエージェント設定セキュリティスキャナー
2026-03-09

今日のトレンド:
  - Agent Safehouse (HN #3): ローカルAIエージェントのサンドボックス化
  - MCP2CLI (HN Show HN): MCPエコシステムの爆発的普及
  - Anthropic × Firefox: AIによるセキュリティ脆弱性自動検出
  - NIST AI Agent Security RFI: エージェントセキュリティの標準化

使い方:
  python3 src/main.py          # ローカル設定をスキャン
  python3 src/main.py --demo   # デモモード（サンプルデータで動作）
  python3 src/main.py --json   # JSON形式でレポート出力
"""

import json
import os
import argparse
import sys
from pathlib import Path
from datetime import datetime


# ─── 設定ファイルの検索パス ────────────────────────────────────────────────────

SCAN_TARGETS = [
    {
        "name": "Claude Code",
        "paths": [
            Path.home() / ".claude" / "settings.json",
            Path.home() / ".claude" / "mcp.json",
            Path(".claude") / "settings.json",
        ],
        "type": "claude",
    },
    {
        "name": "Cursor",
        "paths": [
            Path.home() / ".cursor" / "mcp.json",
            Path(".cursor") / "mcp.json",
        ],
        "type": "cursor",
    },
    {
        "name": "Continue",
        "paths": [
            Path.home() / ".continue" / "config.json",
        ],
        "type": "continue",
    },
    {
        "name": "Cline / Roo Code",
        "paths": [
            Path.home() / ".cline" / "mcp.json",
        ],
        "type": "cline",
    },
]


# ─── セキュリティルール定義 ───────────────────────────────────────────────────

RISK_RULES = [
    {
        "id": "AGENT-001",
        "severity": "HIGH",
        "name": "ルートディレクトリへのファイルシステムアクセス",
        "description": "ファイルシステムサーバーがルート(/)または広範なパスへのアクセスを許可しています",
        "check": "filesystem_root_access",
        "recommendation": "アクセスパスをプロジェクトディレクトリ（例: ~/projects）に限定してください",
        "nist_ref": "NIST AI Agent Security RFI 2026: スコープ付きクレデンシャル原則",
    },
    {
        "id": "AGENT-002",
        "severity": "HIGH",
        "name": "無制限シェルコマンド実行",
        "description": "bashサーバーが全てのシェルコマンドの実行を許可しています",
        "check": "unrestricted_bash",
        "recommendation": "allowedCommands リストで許可コマンドを明示的に制限してください",
        "nist_ref": "NIST AI Agent Security RFI 2026: ツール呼び出し毎のポリシーゲート",
    },
    {
        "id": "AGENT-003",
        "severity": "MEDIUM",
        "name": "クレデンシャルのハードコーディング",
        "description": "APIキー・トークン・パスワードが設定ファイルに直書きされています",
        "check": "hardcoded_credentials",
        "recommendation": "環境変数または OS キーチェーン / シークレット管理ツールを使用してください",
        "nist_ref": "Agent Safehouse (HN 2026-03-09): クレデンシャル分離",
    },
    {
        "id": "AGENT-004",
        "severity": "MEDIUM",
        "name": "承認なしの自律アクション",
        "description": "エージェントが人間の確認なしに外部サービスへの書き込みを実行できます",
        "check": "auto_approve_all",
        "recommendation": "危険な操作（push, delete, send）には autoApprove: false を設定してください",
        "nist_ref": "NIST AI Agent Security RFI 2026: 承認ワークフロー原則",
    },
    {
        "id": "AGENT-005",
        "severity": "LOW",
        "name": "接続文字列にパスワードを含む",
        "description": "データベース接続文字列にパスワードが埋め込まれています",
        "check": "db_password_in_url",
        "recommendation": ".env ファイルまたは DATABASE_URL 環境変数を使用してください",
        "nist_ref": "Agent Safehouse (HN 2026-03-09): シークレット分離",
    },
    {
        "id": "AGENT-006",
        "severity": "LOW",
        "name": "アクションログ無効",
        "description": "エージェントのアクション記録（監査ログ）が無効になっています",
        "check": "logging_disabled",
        "recommendation": "logging: true を設定し、エージェントの全アクションを記録してください",
        "nist_ref": "NIST AI Agent Security RFI 2026: 完全アクション記録原則",
    },
    {
        "id": "AGENT-007",
        "severity": "INFO",
        "name": "ネットワークアクセス制限なし",
        "description": "エージェントが任意の外部URLにアクセスできる可能性があります",
        "check": "unrestricted_network",
        "recommendation": "allowedHosts リストで許可ドメインを制限することを検討してください",
        "nist_ref": "MCP2CLI (HN 2026-03-09): 最小権限原則",
    },
]


# ─── デモ用サンプルデータ ─────────────────────────────────────────────────────

DEMO_CONFIGS = {
    "Claude Code (demo)": {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"],
                "description": "Full filesystem access"
            },
            "bash": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-bash"],
                "env": {
                    "ALLOWED_COMMANDS": ""
                }
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxx1234567890abcdef"
                },
                "autoApprove": ["push", "delete", "create"]
            },
            "postgres": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-postgres",
                    "postgresql://admin:secretpassword123@localhost:5432/mydb"
                ],
                "logging": False
            },
            "fetch": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-fetch"]
            }
        }
    }
}


# ─── スキャナーロジック ───────────────────────────────────────────────────────

def check_filesystem_root_access(config: dict) -> list:
    findings = []
    servers = config.get("mcpServers", {})
    for name, server in servers.items():
        args = server.get("args", [])
        for arg in args:
            if isinstance(arg, str) and (arg == "/" or arg == "~" or arg == str(Path.home())):
                findings.append({
                    "rule_id": "AGENT-001",
                    "server": name,
                    "detail": f"引数 '{arg}' でルートアクセスが検出されました",
                })
    return findings


def check_unrestricted_bash(config: dict) -> list:
    findings = []
    servers = config.get("mcpServers", {})
    for name, server in servers.items():
        args = server.get("args", [])
        is_bash_server = any("bash" in str(a).lower() for a in args)
        if is_bash_server:
            env = server.get("env", {})
            allowed = env.get("ALLOWED_COMMANDS", "")
            if not allowed or allowed.strip() == "":
                findings.append({
                    "rule_id": "AGENT-002",
                    "server": name,
                    "detail": "ALLOWED_COMMANDS が未設定 — 全コマンド実行が可能な状態です",
                })
    return findings


def check_hardcoded_credentials(config: dict) -> list:
    findings = []
    credential_keywords = [
        "token", "key", "secret", "password", "passwd", "api_key",
        "apikey", "access_key", "auth", "credential"
    ]
    servers = config.get("mcpServers", {})
    for name, server in servers.items():
        env = server.get("env", {})
        for env_key, env_val in env.items():
            if isinstance(env_val, str) and len(env_val) > 8:
                key_lower = env_key.lower()
                if any(kw in key_lower for kw in credential_keywords):
                    # 環境変数参照（$VAR形式）は許可
                    if not env_val.startswith("$") and not env_val.startswith("${"):
                        findings.append({
                            "rule_id": "AGENT-003",
                            "server": name,
                            "detail": f"環境変数 '{env_key}' に値が直書きされています（{env_val[:4]}...）",
                        })
    return findings


def check_auto_approve_all(config: dict) -> list:
    findings = []
    dangerous_actions = {"push", "delete", "create", "drop", "truncate", "send", "publish"}
    servers = config.get("mcpServers", {})
    for name, server in servers.items():
        auto_approve = server.get("autoApprove", [])
        if isinstance(auto_approve, bool) and auto_approve:
            findings.append({
                "rule_id": "AGENT-004",
                "server": name,
                "detail": "autoApprove: true — 全操作が自動承認されます",
            })
        elif isinstance(auto_approve, list):
            risky = [a for a in auto_approve if a.lower() in dangerous_actions]
            if risky:
                findings.append({
                    "rule_id": "AGENT-004",
                    "server": name,
                    "detail": f"危険な操作が自動承認設定: {', '.join(risky)}",
                })
    return findings


def check_db_password_in_url(config: dict) -> list:
    findings = []
    servers = config.get("mcpServers", {})
    for name, server in servers.items():
        args = server.get("args", [])
        for arg in args:
            if isinstance(arg, str):
                # postgresql://user:password@host/db の形式を検出
                for prefix in ["postgresql://", "postgres://", "mysql://", "mongodb://"]:
                    if prefix in arg and "@" in arg:
                        # user:pass@host の pass 部分が存在するか確認
                        try:
                            after_scheme = arg.split(prefix, 1)[1]
                            userinfo = after_scheme.split("@")[0]
                            if ":" in userinfo:
                                password = userinfo.split(":", 1)[1]
                                if password and password != "":
                                    findings.append({
                                        "rule_id": "AGENT-005",
                                        "server": name,
                                        "detail": f"接続文字列にパスワードが埋め込まれています",
                                    })
                        except (IndexError, ValueError):
                            pass
    return findings


def check_logging_disabled(config: dict) -> list:
    findings = []
    servers = config.get("mcpServers", {})
    for name, server in servers.items():
        logging_val = server.get("logging", None)
        if logging_val is False:
            findings.append({
                "rule_id": "AGENT-006",
                "server": name,
                "detail": "logging: false — アクション記録が無効です",
            })
    return findings


def check_unrestricted_network(config: dict) -> list:
    findings = []
    servers = config.get("mcpServers", {})
    for name, server in servers.items():
        args = server.get("args", [])
        is_fetch_server = any("fetch" in str(a).lower() for a in args)
        if is_fetch_server:
            allowed_hosts = server.get("allowedHosts", None)
            if allowed_hosts is None:
                findings.append({
                    "rule_id": "AGENT-007",
                    "server": name,
                    "detail": "allowedHosts 未設定 — 任意URLへのアクセスが可能です",
                })
    return findings


CHECKERS = {
    "filesystem_root_access": check_filesystem_root_access,
    "unrestricted_bash": check_unrestricted_bash,
    "hardcoded_credentials": check_hardcoded_credentials,
    "auto_approve_all": check_auto_approve_all,
    "db_password_in_url": check_db_password_in_url,
    "logging_disabled": check_logging_disabled,
    "unrestricted_network": check_unrestricted_network,
}

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
SEVERITY_SCORE_PENALTY = {"HIGH": 30, "MEDIUM": 15, "LOW": 5, "INFO": 2}
SEVERITY_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡", "INFO": "🔵"}


def scan_config(config_name: str, config: dict) -> list:
    all_findings = []
    for rule in RISK_RULES:
        checker_fn = CHECKERS.get(rule["check"])
        if checker_fn:
            results = checker_fn(config)
            for r in results:
                all_findings.append({**rule, **r, "config_source": config_name})
    return all_findings


def calculate_score(findings: list) -> int:
    score = 100
    for f in findings:
        score -= SEVERITY_SCORE_PENALTY.get(f["severity"], 0)
    return max(0, score)


def format_bar(score: int, width: int = 30) -> str:
    filled = int(score / 100 * width)
    if score >= 80:
        color_char = "█"
    elif score >= 60:
        color_char = "▓"
    elif score >= 40:
        color_char = "▒"
    else:
        color_char = "░"
    return color_char * filled + "─" * (width - filled)


# ─── メイン出力 ───────────────────────────────────────────────────────────────

def print_banner():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║           AgentAudit v1.0 — 2026-03-09                  ║")
    print("║     AIエージェント設定セキュリティスキャナー               ║")
    print("║  Inspired by: Agent Safehouse (HN) × NIST AI Agent RFI  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()


def print_scan_summary(loaded: list, skipped: list):
    print("🔍 スキャン対象を検索中...")
    for name, path in loaded:
        print(f"  ✓ {path} が見つかりました ({name})")
    for name, path in skipped:
        print(f"  - {path} は見つかりませんでした")
    print()


def print_findings(findings: list):
    if not findings:
        print("✅ 問題は検出されませんでした！\n")
        return

    print("📋 スキャン結果:\n")
    sorted_findings = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 99))

    for f in sorted_findings:
        emoji = SEVERITY_EMOJI.get(f["severity"], "⚪")
        print(f"  {emoji} [{f['severity']:6}] ({f['id']}) {f['name']}")
        print(f"           サーバー: {f['server']}")
        print(f"           詳細: {f['detail']}")
        print(f"           推奨: {f['recommendation']}")
        print(f"           参考: {f['nist_ref']}")
        print()


def print_score(score: int, findings: list):
    counts = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    bar = format_bar(score)
    print("━" * 60)
    print(f"  📊 セキュリティスコア: {score:3d}/100  [{bar}]")
    print()
    for sev in ["HIGH", "MEDIUM", "LOW", "INFO"]:
        n = counts.get(sev, 0)
        emoji = SEVERITY_EMOJI[sev]
        print(f"     {emoji} {sev:6}: {n}件")
    print()


def print_today_trends():
    print("💡 本日のトレンド参考 (2026-03-09):")
    print("   [HN #3 ] Agent Safehouse — ローカルエージェントのmacOSネイティブサンドボックス化を検討")
    print("   [HN Show] MCP2CLI — MCPサーバーのアクセス範囲を最小権限に設定することを推奨")
    print("   [NIST  ] AI Agent Security RFI — ツール呼び出し毎のポリシーゲート・承認ワークフローを標準化")
    print("   [Trend ] Anthropic×Firefox — AIによる設定ファイル脆弱性の自動検出が実用化段階")
    print()


def save_report(findings: list, score: int, output_path: Path):
    report = {
        "generated_at": datetime.now().isoformat(),
        "tool": "AgentAudit v1.0",
        "date": "2026-03-09",
        "security_score": score,
        "summary": {
            "total": len(findings),
            "HIGH": sum(1 for f in findings if f["severity"] == "HIGH"),
            "MEDIUM": sum(1 for f in findings if f["severity"] == "MEDIUM"),
            "LOW": sum(1 for f in findings if f["severity"] == "LOW"),
            "INFO": sum(1 for f in findings if f["severity"] == "INFO"),
        },
        "findings": [
            {
                "id": f["id"],
                "severity": f["severity"],
                "name": f["name"],
                "server": f["server"],
                "config_source": f["config_source"],
                "detail": f["detail"],
                "recommendation": f["recommendation"],
                "nist_ref": f["nist_ref"],
            }
            for f in findings
        ],
        "trend_context": {
            "hn_top": "Agent Safehouse — macOS-native sandboxing for local agents",
            "hn_show": "MCP2CLI — One CLI for every API, 96-99% fewer tokens than native MCP",
            "security": "Anthropic discovered 22 Firefox vulnerabilities using Claude Opus 4.6",
            "nist": "NIST AI Agent Security RFI closed March 9, 2026",
        },
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"📄 詳細レポート: {output_path}")
    print()


# ─── エントリポイント ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AgentAudit — AIエージェント設定セキュリティスキャナー (2026-03-09)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python3 src/main.py           # ローカル設定をスキャン
  python3 src/main.py --demo    # デモモード（サンプルデータで動作）
  python3 src/main.py --json    # JSONレポートも出力

今日のトレンド参考:
  HN #3: Agent Safehouse — macOS-native sandboxing for local agents
  HN Show HN: MCP2CLI — One CLI for every API
  NIST AI Agent Security RFI closed today (2026-03-09)
        """,
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="デモモード: サンプル設定データでスキャンを実行",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSONレポートファイルを出力する",
    )
    args = parser.parse_args()

    print_banner()

    all_findings = []
    loaded = []
    skipped = []

    if args.demo:
        print("  ℹ️  デモモードで実行中（サンプルMCP設定を使用）\n")
        for config_name, config in DEMO_CONFIGS.items():
            findings = scan_config(config_name, config)
            all_findings.extend(findings)
            loaded.append((config_name, "~/.claude/settings.json (demo)"))
    else:
        # 実際のファイルをスキャン
        found_any = False
        for target in SCAN_TARGETS:
            for path in target["paths"]:
                if path.exists():
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                        findings = scan_config(target["name"], config)
                        all_findings.extend(findings)
                        loaded.append((target["name"], str(path)))
                        found_any = True
                        break
                    except (json.JSONDecodeError, PermissionError) as e:
                        skipped.append((target["name"], f"{path} (読み込みエラー: {e})"))
                else:
                    skipped.append((target["name"], str(path)))

        if not found_any:
            print("  ℹ️  ローカルのAIエージェント設定ファイルが見つかりませんでした。")
            print("      --demo オプションを使用してサンプルデータでお試しください。\n")
            print("  対応ツール: Claude Code, Cursor, Continue, Cline")
            print()
            print_today_trends()
            sys.exit(0)

    print_scan_summary(loaded, [s for s in skipped if s not in loaded])
    print_findings(all_findings)

    score = calculate_score(all_findings)
    print_score(score, all_findings)

    print_today_trends()

    if args.json:
        report_path = Path(f"agent_audit_report_{datetime.now().strftime('%Y%m%d')}.json")
        save_report(all_findings, score, report_path)


if __name__ == "__main__":
    main()
