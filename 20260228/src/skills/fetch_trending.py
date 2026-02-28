"""
fetch_trending.py — スキル #1
GitHub Trending 風のリポジトリデータを JSON ファイルから読み込む。
DeerFlow 2.0 の fetch/scraping スキルに相当。
"""
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from skill_runner import BaseSkill


class FetchTrendingSkill(BaseSkill):
    name = "fetch_trending"
    description = "GitHub Trending リポジトリデータを読み込む"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        data_path = context.get("_data_path", "data/sample_repos.json")
        path = Path(data_path)

        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        repos = data.get("repos", [])
        context["repos"] = repos
        context["fetched_at"] = data.get("fetched_at", "")
        context["source"] = data.get("source", "")
        context["_fetch_count"] = len(repos)

        print(f"    Loaded {len(repos)} repos from {path.name}", file=sys.stderr)
        return context
