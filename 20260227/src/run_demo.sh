#!/bin/bash
# run_demo.sh — ai_repo_auditor のデモ実行スクリプト
# 使用方法: bash src/run_demo.sh (20260227/ ディレクトリから実行)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDITOR="$SCRIPT_DIR/ai_repo_auditor.py"

echo "========================================"
echo "  AI Repo Auditor — デモ実行"
echo "========================================"
echo ""

echo "【テスト 1】安全なプロジェクトのスキャン"
echo "----------------------------------------"
python3 "$AUDITOR" --path "$SCRIPT_DIR/test_data/safe_project"
echo ""

echo "【テスト 2】悪意あるプロジェクトのスキャン"
echo "--------------------------------------------"
python3 "$AUDITOR" --path "$SCRIPT_DIR/test_data/malicious_project" || true
echo ""

echo "【テスト 3】JSON 形式での出力（CI/CD 連携用）"
echo "-----------------------------------------------"
python3 "$AUDITOR" --path "$SCRIPT_DIR/test_data/malicious_project" --json 2>/dev/null | python3 -m json.tool || true
echo ""

echo "【テスト 4】カレントディレクトリのスキャン"
echo "--------------------------------------------"
python3 "$AUDITOR" --path "$(pwd)"
