"""
score_growth.py — スキル #2
スター履歴から日次増加率・加速度・総合トレンドスコアを計算する。
DeerFlow 2.0 の分析スキルに相当。
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from skill_runner import BaseSkill


class ScoreGrowthSkill(BaseSkill):
    name = "score_growth"
    description = "スター成長率・加速度からトレンドスコアを算出する"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        repos = context.get("repos", [])
        if not repos:
            raise ValueError("No repos in context. Run fetch_trending first.")

        scored = []
        for repo in repos:
            history = repo.get("star_history", [])
            if len(history) < 2:
                continue

            current_stars = history[-1]
            oldest_stars  = history[0]
            n_days = len(history) - 1

            # 日次平均増加数
            avg_daily = (current_stars - oldest_stars) / n_days if n_days > 0 else 0

            # 加速度: 後半7日間 vs 前半7日間の増加率比較（直近の勢いを反映）
            mid = len(history) // 2
            first_half_gain  = history[mid] - history[0]
            second_half_gain = history[-1] - history[mid]
            acceleration = (second_half_gain / first_half_gain) if first_half_gain > 0 else 1.0

            # 総合トレンドスコア (対数スケールで正規化)
            import math
            score = math.log1p(avg_daily) * acceleration * 100

            scored.append({
                **repo,
                "current_stars":   current_stars,
                "avg_daily_gain":  round(avg_daily, 1),
                "acceleration":    round(acceleration, 3),
                "trend_score":     round(score, 2),
            })

        # スコア降順でソート
        scored.sort(key=lambda r: r["trend_score"], reverse=True)

        context["repos"] = scored
        print(f"    Scored {len(scored)} repos (top: {scored[0]['name']} score={scored[0]['trend_score']})", file=sys.stderr)
        return context
