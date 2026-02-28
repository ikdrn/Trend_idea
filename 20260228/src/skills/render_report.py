"""
render_report.py — スキル #4
パイプラインの最終スキル。全スキルが蓄積したコンテキストを
カラフルなターミナルレポートとして表示する。
DeerFlow 2.0 の output/report スキルに相当。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from skill_runner import BaseSkill, C


# バーチャートの最大幅
BAR_MAX_WIDTH = 20


def make_bar(value: float, max_value: float, width: int = BAR_MAX_WIDTH) -> str:
    """ASCII バーチャートを生成"""
    if max_value <= 0:
        return ""
    ratio = min(value / max_value, 1.0)
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


def fmt_stars(n: int) -> str:
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


class RenderReportSkill(BaseSkill):
    name = "render_report"
    description = "トレンドスコアと予測をターミナルにカラー表示する"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        # JSON モード時は端末出力をスキップ
        if context.get("_json_mode"):
            context["_rendered"] = True
            return context

        repos   = context.get("repos", [])
        source  = context.get("source", "Unknown")
        horizon = context.get("forecast_horizon", 7)

        print()
        print(f"{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════╗{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}║       Tech Repo Trend Forecast Report               ║{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}║             2026-02-28  (DeerFlow Skills)           ║{C.RESET}")
        print(f"{C.CYAN}{C.BOLD}╚══════════════════════════════════════════════════════╝{C.RESET}")
        print()
        print(f"{C.DIM}Source: {source}{C.RESET}")
        print()

        if not repos:
            print(f"{C.YELLOW}No repos to display.{C.RESET}")
            return context

        # ヘッダー
        print(
            f"  {C.BOLD}{'Rank':<5}"
            f"{'Repository':<35}"
            f"{'Stars':>7}"
            f"{'Growth/d':>10}"
            f"  {'Trend Bar':<22}"
            f"{f'{horizon}d Forecast':>12}"
            f"{C.RESET}"
        )
        print("  " + "─" * 95)

        max_score = repos[0]["trend_score"] if repos else 1

        for rank, repo in enumerate(repos, start=1):
            full_name    = f"{repo['owner']}/{repo['name']}"
            current      = repo.get("current_stars", 0)
            daily        = repo.get("avg_daily_gain", 0)
            accel        = repo.get("acceleration", 1.0)
            score        = repo.get("trend_score", 0)
            forecast_7d  = repo.get("forecast_7d")
            ci_lower     = repo.get("forecast_ci_lower")
            ci_upper     = repo.get("forecast_ci_upper")

            bar = make_bar(score, max_score)

            # 加速度でカラー変化
            if accel > 1.2:
                accel_color = C.GREEN
            elif accel > 0.9:
                accel_color = C.YELLOW
            else:
                accel_color = C.RED

            # 順位バッジ
            rank_badge = ["🥇", "🥈", "🥉", "  4", "  5", "  6", "  7"][min(rank - 1, 6)]

            forecast_str = (
                f"~{fmt_stars(forecast_7d)}"
                if forecast_7d is not None
                else "N/A"
            )

            print(
                f"  {rank_badge} "
                f"{C.BOLD}{full_name[:33]:<33}{C.RESET} "
                f"{C.WHITE}{fmt_stars(current):>6}{C.RESET} "
                f"{accel_color}{f'+{daily:.0f}':>9}/d{C.RESET}  "
                f"{C.CYAN}{bar:<22}{C.RESET}"
                f"{C.MAGENTA}{forecast_str:>12}{C.RESET}"
            )

            # 信頼区間
            if ci_lower is not None and ci_upper is not None:
                print(
                    f"       {C.DIM}{'':<33} "
                    f"{'':>6} {'':>9}   "
                    f"{'':22}  "
                    f"95%CI: [{fmt_stars(ci_lower)}, {fmt_stars(ci_upper)}]{C.RESET}"
                )

        print()
        print("  " + "─" * 95)
        print(
            f"  {C.DIM}Forecast method: Holt Double Exponential Smoothing (α=0.3, β=0.1), "
            f"horizon={horizon} days{C.RESET}"
        )
        print(
            f"  {C.DIM}Inspired by: ByteDance DeerFlow 2.0 (skills), "
            f"Google TimesFM (zero-shot forecasting), PicoLM (zero-dep){C.RESET}"
        )
        print()

        # サマリー統計
        total_repos = len(repos)
        avg_daily   = sum(r.get("avg_daily_gain", 0) for r in repos) / total_repos if total_repos else 0
        print(f"  {C.BOLD}Summary:{C.RESET} {total_repos} repos analyzed, "
              f"avg daily gain: {avg_daily:.0f} stars/day")
        print()

        context["_rendered"] = True
        return context
