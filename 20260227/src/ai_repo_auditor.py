#!/usr/bin/env python3
"""
ai_repo_auditor.py
==================
AI エージェント設定ファイル セキュリティ監査 CLI

2026-02-27 に公開された以下のトレンドに基づいて開発:
  - CVE-2025-59536: Claude Code の .claude/settings.json Hooks 経由 RCE
  - CVE-2026-21852: ANTHROPIC_BASE_URL によるAPIキー外部送信
  - ClawHavoc: OpenClaw/ClawHub スキルレジストリへのサプライチェーン攻撃
  - 一般的なシークレット漏洩パターン

使用方法:
  python ai_repo_auditor.py --path /path/to/project [--json]

依存関係:
  標準ライブラリのみ（外部インストール不要）
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# ───────────────────────────────────────────────
# ANSI カラーコード（ターミナル出力用）
# ───────────────────────────────────────────────
class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    WHITE   = "\033[97m"
    MAGENTA = "\033[95m"


# ───────────────────────────────────────────────
# データモデル
# ───────────────────────────────────────────────
@dataclass
class Finding:
    severity: str          # CRITICAL / HIGH / MEDIUM / LOW / INFO
    file_path: str
    title: str
    detail: str
    cve: Optional[str] = None
    line: Optional[int] = None

    def severity_color(self) -> str:
        colors = {
            "CRITICAL": Color.RED + Color.BOLD,
            "HIGH":     Color.RED,
            "MEDIUM":   Color.YELLOW,
            "LOW":      Color.CYAN,
            "INFO":     Color.WHITE,
        }
        return colors.get(self.severity, Color.WHITE)


@dataclass
class AuditResult:
    target_path: str
    findings: List[Finding] = field(default_factory=list)

    def count_by_severity(self) -> dict:
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts


# ───────────────────────────────────────────────
# 危険パターン定義
# ───────────────────────────────────────────────

# シェルコマンドとして疑わしいキーワード
DANGEROUS_SHELL_PATTERNS = [
    r"curl\s+",
    r"wget\s+",
    r"nc\s+",
    r"ncat\s+",
    r"bash\s+-[ci]",
    r"/bin/sh",
    r"/bin/bash",
    r"python\s+-c",
    r"ruby\s+-e",
    r"perl\s+-e",
    r"eval\s*\(",
    r"\$\(.*\)",       # コマンド置換
    r"`[^`]+`",        # バッククォート
    r"chmod\s+[0-7]+",
    r"mkfifo\s+",
    r"exec\s+",
    r"rm\s+-rf",
    r"base64\s+",
    r">>\s*/etc/",
    r"crontab\s+",
]

# APIキーのパターン
API_KEY_PATTERNS = [
    (r"sk-ant-[A-Za-z0-9\-_]{20,}", "Anthropic API Key"),
    (r"sk-[A-Za-z0-9]{48}", "OpenAI API Key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[A-Za-z0-9]{36}", "GitHub OAuth Token"),
    (r"glpat-[A-Za-z0-9\-_]{20}", "GitLab Personal Access Token"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
]

# ClawHavoc に関連する既知の悪意あるパッケージ名（サンプル）
CLAWHAVOC_KNOWN_PACKAGES = {
    "openclaw-skill-executor",
    "mcp-skill-runner",
    "clawhub-auto-install",
    "skill-bootstrap-util",
    "openclaw-remote-shell",
    "mcp-webhook-trigger",
    "ai-agent-backdoor",
    "claw-skill-fetcher",
}


# ───────────────────────────────────────────────
# チェッカー関数群
# ───────────────────────────────────────────────

def check_claude_settings(file_path: Path) -> List[Finding]:
    """
    .claude/settings.json を解析して CVE-2025-59536 / CVE-2026-21852 を検出する。
    """
    findings = []
    try:
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)
    except (json.JSONDecodeError, OSError) as e:
        findings.append(Finding(
            severity="LOW",
            file_path=str(file_path),
            title="設定ファイルの解析に失敗しました",
            detail=f"JSONパースエラー: {e}",
        ))
        return findings

    # ── 1. ANTHROPIC_BASE_URL の外部ドメイン確認 (CVE-2026-21852) ──
    env_vars = data.get("env", {})
    if isinstance(env_vars, dict):
        base_url = env_vars.get("ANTHROPIC_BASE_URL", "")
        if base_url and not _is_safe_url(base_url):
            findings.append(Finding(
                severity="HIGH",
                file_path=str(file_path),
                title="ANTHROPIC_BASE_URL が外部ホストを指定しています",
                detail=f"値: {base_url!r} — 攻撃者のサーバーへ API キーが送信される恐れがあります",
                cve="CVE-2026-21852",
            ))

    # ── 2. Hooks のシェルコマンド検査 (CVE-2025-59536) ──
    hooks = data.get("hooks", {})
    if isinstance(hooks, dict):
        for hook_name, hook_value in hooks.items():
            commands = _extract_commands(hook_value)
            for cmd in commands:
                if _is_dangerous_command(cmd):
                    findings.append(Finding(
                        severity="CRITICAL",
                        file_path=str(file_path),
                        title=f"Hook '{hook_name}' に危険なシェルコマンドが含まれています",
                        detail=f"コマンド: {cmd!r}",
                        cve="CVE-2025-59536",
                    ))

    # ── 3. MCP サーバー設定の不審な URL / コマンド確認 ──
    mcp_servers = data.get("mcpServers", {})
    if isinstance(mcp_servers, dict):
        for server_name, server_conf in mcp_servers.items():
            if isinstance(server_conf, dict):
                # 外部 URL を持つ MCP サーバー
                server_url = server_conf.get("url", "")
                if server_url and not _is_safe_url(server_url):
                    findings.append(Finding(
                        severity="HIGH",
                        file_path=str(file_path),
                        title=f"MCP サーバー '{server_name}' が外部 URL を使用しています",
                        detail=f"URL: {server_url!r} — 信頼できない MCP サーバーはプロンプトインジェクションの温床になります",
                    ))
                # コマンド実行型 MCP サーバーの args チェック
                args = server_conf.get("args", [])
                if isinstance(args, list):
                    for arg in args:
                        if isinstance(arg, str) and _is_dangerous_command(arg):
                            findings.append(Finding(
                                severity="HIGH",
                                file_path=str(file_path),
                                title=f"MCP サーバー '{server_name}' の args に危険な引数があります",
                                detail=f"引数: {arg!r}",
                            ))

    return findings


def check_env_files(file_path: Path) -> List[Finding]:
    """
    .env ファイルや設定ファイルから平文の API キーを検出する。
    """
    findings = []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return findings

    for lineno, line in enumerate(lines, start=1):
        # コメント行は除外
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for pattern, key_type in API_KEY_PATTERNS:
            if re.search(pattern, line):
                # 値を一部マスクして表示
                masked = re.sub(pattern, lambda m: m.group()[:8] + "..." + m.group()[-4:], line)
                findings.append(Finding(
                    severity="MEDIUM",
                    file_path=str(file_path),
                    title=f"平文の {key_type} が検出されました",
                    detail=f"Line {lineno}: {masked.strip()}",
                    line=lineno,
                ))
    return findings


def check_requirements(file_path: Path) -> List[Finding]:
    """
    requirements.txt に ClawHavoc 既知パッケージが含まれていないか確認する。
    """
    findings = []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return findings

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip().lower()
        # バージョン指定を除去してパッケージ名だけ取得
        pkg_name = re.split(r"[>=<!~\[]", stripped)[0].strip()
        if pkg_name in CLAWHAVOC_KNOWN_PACKAGES:
            findings.append(Finding(
                severity="CRITICAL",
                file_path=str(file_path),
                title=f"ClawHavoc 既知の悪意あるパッケージ: '{pkg_name}'",
                detail=f"Line {lineno}: {line.strip()} — ClawHavoc サプライチェーン攻撃に関連するパッケージです",
                line=lineno,
            ))
    return findings


def check_package_json(file_path: Path) -> List[Finding]:
    """
    package.json に ClawHavoc 既知パッケージが含まれていないか確認する。
    """
    findings = []
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return findings

    all_deps = {}
    all_deps.update(data.get("dependencies", {}))
    all_deps.update(data.get("devDependencies", {}))

    for pkg_name in all_deps:
        if pkg_name.lower() in CLAWHAVOC_KNOWN_PACKAGES:
            findings.append(Finding(
                severity="CRITICAL",
                file_path=str(file_path),
                title=f"ClawHavoc 既知の悪意あるパッケージ: '{pkg_name}'",
                detail=f"パッケージ: {pkg_name} — ClawHavoc サプライチェーン攻撃に関連するパッケージです",
            ))
    return findings


# ───────────────────────────────────────────────
# ヘルパー関数
# ───────────────────────────────────────────────

def _is_safe_url(url: str) -> bool:
    """localhost / 127.x.x.x / 空文字列のみ安全とみなす"""
    safe_patterns = [
        r"^https?://localhost",
        r"^https?://127\.",
        r"^https?://\[::1\]",
        r"^$",
    ]
    return any(re.match(p, url, re.IGNORECASE) for p in safe_patterns)


def _extract_commands(hook_value) -> List[str]:
    """Hooks の値から実行コマンド文字列を抽出する"""
    commands = []
    if isinstance(hook_value, str):
        commands.append(hook_value)
    elif isinstance(hook_value, list):
        for item in hook_value:
            if isinstance(item, str):
                commands.append(item)
            elif isinstance(item, dict):
                cmd = item.get("command", item.get("run", item.get("exec", "")))
                if cmd:
                    commands.append(str(cmd))
    elif isinstance(hook_value, dict):
        cmd = hook_value.get("command", hook_value.get("run", hook_value.get("exec", "")))
        if cmd:
            commands.append(str(cmd))
    return commands


def _is_dangerous_command(cmd: str) -> bool:
    """コマンド文字列が危険なパターンを含むか確認"""
    for pattern in DANGEROUS_SHELL_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return True
    return False


# ───────────────────────────────────────────────
# メインスキャナ
# ───────────────────────────────────────────────

def scan_directory(target: Path) -> AuditResult:
    result = AuditResult(target_path=str(target))

    # 1. .claude/settings.json
    claude_settings = target / ".claude" / "settings.json"
    if claude_settings.exists():
        result.findings.extend(check_claude_settings(claude_settings))
    else:
        result.findings.append(Finding(
            severity="INFO",
            file_path=str(claude_settings),
            title=".claude/settings.json が見つかりません（Claude Code 未設定）",
            detail="Claude Code を使用している場合は設定ファイルを確認してください",
        ))

    # 2. .env 系ファイル（重複スキャンを防ぐため scanned_files で管理）
    scanned_env_files = set()
    env_patterns = [".env", ".env.local", ".env.production", ".env.development",
                    ".env.staging", "config.env", "secrets.env"]
    for env_name in env_patterns:
        env_file = target / env_name
        if env_file.exists() and env_file not in scanned_env_files:
            scanned_env_files.add(env_file)
            result.findings.extend(check_env_files(env_file))

    # サブディレクトリも再帰的にスキャン（深さ3まで）
    for env_file in target.rglob("*.env"):
        if env_file.is_file() and env_file not in scanned_env_files:
            scanned_env_files.add(env_file)
            result.findings.extend(check_env_files(env_file))

    # 3. requirements.txt
    req_file = target / "requirements.txt"
    if req_file.exists():
        result.findings.extend(check_requirements(req_file))

    # 4. package.json
    pkg_json = target / "package.json"
    if pkg_json.exists():
        result.findings.extend(check_package_json(pkg_json))

    # 5. openclaw 設定ファイル (.openclaw/config.json 等)
    for openclaw_cfg in target.rglob(".openclaw/*.json"):
        if openclaw_cfg.is_file():
            try:
                data = json.loads(openclaw_cfg.read_text(encoding="utf-8"))
                # MCP サーバー設定の確認
                for server in data.get("mcpServers", {}).values():
                    if isinstance(server, dict):
                        url = server.get("url", "")
                        if url and not _is_safe_url(url):
                            result.findings.append(Finding(
                                severity="HIGH",
                                file_path=str(openclaw_cfg),
                                title="OpenClaw MCP サーバーが外部 URL を使用しています",
                                detail=f"URL: {url!r} — OpenClaw CVE-2026-25253 の攻撃ベクターになりえます",
                                cve="CVE-2026-25253",
                            ))
            except (json.JSONDecodeError, OSError):
                pass

    return result


# ───────────────────────────────────────────────
# 出力フォーマッター
# ───────────────────────────────────────────────

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}

def print_banner():
    print(f"{Color.BOLD}{Color.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        AI Repo Auditor v1.0  —  2026-02-27             ║")
    print("║  AI エージェント設定ファイル セキュリティ監査 CLI      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(Color.RESET)


def print_finding(f: Finding):
    color = f.severity_color()
    severity_label = f"[{f.severity:<8}]"
    print(f"  {color}{severity_label}{Color.RESET} {Color.BOLD}{f.title}{Color.RESET}")
    print(f"             {Color.WHITE}File:{Color.RESET} {f.file_path}")
    if f.line:
        print(f"             {Color.WHITE}Line:{Color.RESET} {f.line}")
    print(f"             {Color.WHITE}Detail:{Color.RESET} {f.detail}")
    if f.cve:
        print(f"             {Color.MAGENTA}CVE:{Color.RESET} {f.cve}")
    print()


def print_report(result: AuditResult):
    print_banner()
    print(f"{Color.BOLD}Scanning:{Color.RESET} {result.target_path}\n")

    if not result.findings:
        print(f"{Color.GREEN}✓ 問題は検出されませんでした。{Color.RESET}\n")
        return

    # 重大度順に並び替えて出力
    sorted_findings = sorted(result.findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 99))

    for finding in sorted_findings:
        print_finding(finding)

    # サマリー
    counts = result.count_by_severity()
    print("─" * 60)
    print(f"{Color.BOLD}Summary:{Color.RESET} {len(result.findings)} issues found")
    for sev, count in counts.items():
        if count > 0:
            color = Finding(sev, "", "", "").severity_color()
            print(f"  {color}● {sev}: {count}{Color.RESET}")
    print()

    # 終了コード: CRITICAL/HIGH があれば非ゼロ
    if counts["CRITICAL"] > 0 or counts["HIGH"] > 0:
        sys.exit(1)


def print_json_report(result: AuditResult):
    output = {
        "target": result.target_path,
        "total_findings": len(result.findings),
        "summary": result.count_by_severity(),
        "findings": [
            {
                "severity": f.severity,
                "file": f.file_path,
                "line": f.line,
                "title": f.title,
                "detail": f.detail,
                "cve": f.cve,
            }
            for f in sorted(result.findings, key=lambda x: SEVERITY_ORDER.get(x.severity, 99))
        ]
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


# ───────────────────────────────────────────────
# エントリポイント
# ───────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI エージェント設定ファイルのセキュリティリスクを検出する監査ツール"
    )
    parser.add_argument(
        "--path", "-p",
        default=".",
        help="スキャン対象のディレクトリ（デフォルト: カレントディレクトリ）"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 形式で結果を出力（CI/CD 連携用）"
    )
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.is_dir():
        print(f"Error: '{target}' はディレクトリではありません", file=sys.stderr)
        sys.exit(2)

    result = scan_directory(target)

    if args.json:
        print_json_report(result)
    else:
        print_report(result)


if __name__ == "__main__":
    main()
