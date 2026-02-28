#!/usr/bin/env python3
"""
skill_runner.py
===============
Mini-DeerFlow: DeerFlow 2.0 インスパイアのスキルベース軽量エージェントランタイム

2026-02-28 トレンドの掛け合わせ:
  - ByteDance DeerFlow 2.0 のスキルアーキテクチャ
  - Google TimesFM のゼロショット時系列予測の思想
  - RightNow-AI/picolm のゼロ依存・最小主義設計

使用方法:
  python skill_runner.py --pipeline fetch_trending,score_growth,forecast_stars,render_report
  python skill_runner.py --pipeline fetch_trending,score_growth,forecast_stars,render_report --json
  python skill_runner.py --list

依存関係: 標準ライブラリのみ
"""

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

# ────────────────────────────────────────────
# ANSI カラー
# ────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    WHITE  = "\033[97m"
    DIM    = "\033[2m"
    MAGENTA = "\033[95m"


# ────────────────────────────────────────────
# スキルベースクラス (DeerFlow の Skill 仕様に相当)
# ────────────────────────────────────────────
class BaseSkill:
    """
    全スキルが継承する基底クラス。
    DeerFlow 2.0 では Markdown ファイルで定義されるが、
    ここでは Python クラスとして実装する。
    """
    name: str = "base_skill"
    description: str = "Base skill"
    version: str = "1.0.0"

    def run(self, context: dict) -> dict:
        """
        スキルを実行してコンテキストを更新して返す。
        context: 前のスキルが追記した状態辞書
        返り値: 更新済みのコンテキスト辞書
        """
        raise NotImplementedError


# ────────────────────────────────────────────
# スキルチェーン (DeerFlow の Pipeline/SubAgent 連鎖に相当)
# ────────────────────────────────────────────
class SkillChain:
    """複数のスキルを順番に実行し、コンテキストを次のスキルへ渡す"""

    def __init__(self, skills: list[BaseSkill]):
        self.skills = skills

    def run(self, initial_context: dict | None = None) -> dict:
        context = initial_context or {}
        for skill in self.skills:
            _log_step(f"Running skill: {skill.name} — {skill.description}")
            try:
                context = skill.run(context)
            except Exception as e:
                _log_error(f"Skill '{skill.name}' failed: {e}")
                context["_error"] = {"skill": skill.name, "message": str(e)}
                break
        return context


# ────────────────────────────────────────────
# スキル動的ロード
# ────────────────────────────────────────────
SKILLS_DIR = Path(__file__).parent / "skills"

def _is_skill_class(attr: Any) -> bool:
    """
    BaseSkill のサブクラスかどうかを判定する。
    importlib でロードしたモジュールは別の module instance になるため
    issubclass ではなく属性の有無でダックタイピング判定する。
    """
    return (
        isinstance(attr, type)
        and attr.__name__ != "BaseSkill"
        and callable(getattr(attr, "run", None))
        and isinstance(getattr(attr, "name", None), str)
        and isinstance(getattr(attr, "description", None), str)
    )


def load_skill(skill_name: str) -> BaseSkill:
    """skills/ ディレクトリから指定名のスキルをロードして返す"""
    module_path = SKILLS_DIR / f"{skill_name}.py"
    if not module_path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_name} (expected: {module_path})")

    spec = importlib.util.spec_from_file_location(skill_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # モジュール内のスキルクラスをダックタイピングで探してインスタンス化
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if _is_skill_class(attr):
            return attr()

    raise ImportError(f"No skill class found in {module_path}")


def list_skills() -> list[dict]:
    """利用可能なスキル一覧を返す"""
    skills = []
    for path in sorted(SKILLS_DIR.glob("*.py")):
        if path.name.startswith("_"):
            continue
        try:
            skill = load_skill(path.stem)
            skills.append({
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
            })
        except Exception:
            pass
    return skills


# ────────────────────────────────────────────
# ロギングユーティリティ
# ────────────────────────────────────────────
def _log_step(msg: str):
    print(f"  {C.DIM}▶{C.RESET} {C.WHITE}{msg}{C.RESET}", file=sys.stderr)

def _log_error(msg: str):
    print(f"  {C.RED}✗ {msg}{C.RESET}", file=sys.stderr)


# ────────────────────────────────────────────
# エントリポイント
# ────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Mini-DeerFlow: DeerFlow 2.0 インスパイアのスキルベース軽量エージェントランタイム"
    )
    parser.add_argument(
        "--pipeline", "-p",
        help="実行するスキルをカンマ区切りで指定 (例: fetch_trending,score_growth,forecast_stars,render_report)",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="利用可能なスキル一覧を表示",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="最終コンテキストを JSON で出力",
    )
    parser.add_argument(
        "--data", "-d",
        default=str(Path(__file__).parent / "data" / "sample_repos.json"),
        help="入力データ JSONファイルパス",
    )
    args = parser.parse_args()

    # バナー（JSON モード時は stderr へ）
    out = sys.stderr if args.json else sys.stdout
    print(f"\n{C.CYAN}{C.BOLD}Mini-DeerFlow v1.0 — 2026-02-28{C.RESET}", file=out)
    print(f"{C.DIM}DeerFlow 2.0 + TimesFM + PicoLM インスパイア{C.RESET}\n", file=out)

    # スキル一覧表示
    if args.list:
        skills = list_skills()
        print(f"{C.BOLD}Available Skills ({len(skills)}):{C.RESET}")
        for s in skills:
            print(f"  {C.GREEN}● {s['name']:<22}{C.RESET} v{s['version']}  {C.DIM}{s['description']}{C.RESET}")
        print()
        return

    if not args.pipeline:
        parser.print_help()
        sys.exit(1)

    # スキルをロードしてチェーンを構築
    skill_names = [s.strip() for s in args.pipeline.split(",") if s.strip()]
    print(f"{C.BOLD}Pipeline:{C.RESET} {C.CYAN}{' → '.join(skill_names)}{C.RESET}\n", file=out)

    skills = []
    for name in skill_names:
        try:
            skills.append(load_skill(name))
        except (FileNotFoundError, ImportError) as e:
            _log_error(str(e))
            sys.exit(1)

    # 初期コンテキスト
    initial_context = {"_data_path": args.data, "_json_mode": args.json}

    # チェーン実行
    chain = SkillChain(skills)
    final_context = chain.run(initial_context)

    # JSON 出力
    if args.json:
        # シリアライズ不可なキーを除外
        output = {k: v for k, v in final_context.items() if not k.startswith("_")}
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
