"""
forecast_stars.py — スキル #3
Holt 二重指数平滑法で 7 日先のスター数を予測する。

Google TimesFM の「ゼロショット時系列予測（事前学習済みモデルで
未見データをチューニングなしで予測）」という思想を、
標準ライブラリのみで軽量実装したもの。

TimesFM はトランスフォーマーで学習済み重みを使うのに対し、
こちらは Holt 二重指数平滑法（level + trend の 2 成分モデル）で
同等の「トレンドを捉えたゼロショット予測」を実現する。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from skill_runner import BaseSkill


def holt_double_exponential_smoothing(
    series: list[float],
    alpha: float = 0.3,
    beta: float = 0.1,
    horizon: int = 7,
) -> tuple[list[float], list[float]]:
    """
    Holt 二重指数平滑法 (DES / Holt's Linear Method)

    Args:
        series: 時系列データ (整数でもOK)
        alpha:  レベルの平滑化係数 (0 < α < 1)
        beta:   トレンドの平滑化係数 (0 < β < 1)
        horizon: 予測する将来ステップ数

    Returns:
        (forecasts, confidence_halfwidths)
        - forecasts: horizon 個の予測値
        - confidence_halfwidths: 95%信頼区間の半幅（残差標準偏差ベース）
    """
    if len(series) < 2:
        raise ValueError("Series must have at least 2 data points")

    # 初期値
    level = float(series[0])
    trend = float(series[1] - series[0])

    fitted = []
    residuals = []

    for obs in series:
        fitted_val = level + trend
        fitted.append(fitted_val)
        residuals.append(obs - fitted_val)

        new_level = alpha * obs + (1 - alpha) * (level + trend)
        new_trend = beta * (new_level - level) + (1 - beta) * trend
        level = new_level
        trend = new_trend

    # 残差標準偏差（信頼区間計算用）
    n = len(residuals)
    mse = sum(r ** 2 for r in residuals) / max(n - 1, 1)
    sigma = math.sqrt(mse)

    # 予測
    forecasts = []
    half_widths = []
    for h in range(1, horizon + 1):
        f = level + h * trend
        forecasts.append(f)
        # 95% 信頼区間（正規近似: ±1.96σ√h）
        half_widths.append(1.96 * sigma * math.sqrt(h))

    return forecasts, half_widths


class ForecastStarsSkill(BaseSkill):
    name = "forecast_stars"
    description = "Holt二重指数平滑法で7日先のスター数を予測する（TimesFM インスパイア）"
    version = "1.0.0"

    ALPHA   = 0.3   # レベル平滑化係数
    BETA    = 0.1   # トレンド平滑化係数
    HORIZON = 7     # 予測日数

    def run(self, context: dict) -> dict:
        repos = context.get("repos", [])
        if not repos:
            raise ValueError("No repos in context. Run fetch_trending first.")

        for repo in repos:
            history = [float(s) for s in repo.get("star_history", [])]
            if len(history) < 2:
                repo["forecast_7d"] = None
                repo["forecast_ci_lower"] = None
                repo["forecast_ci_upper"] = None
                continue

            forecasts, half_widths = holt_double_exponential_smoothing(
                history, alpha=self.ALPHA, beta=self.BETA, horizon=self.HORIZON
            )

            repo["forecast_7d"]         = round(forecasts[-1])          # 7日後予測
            repo["forecast_ci_lower"]   = round(forecasts[-1] - half_widths[-1])
            repo["forecast_ci_upper"]   = round(forecasts[-1] + half_widths[-1])
            repo["forecast_all"]        = [round(f) for f in forecasts] # 全ホライゾン
            repo["forecast_method"]     = f"Holt DES (α={self.ALPHA}, β={self.BETA})"

        context["repos"] = repos
        context["forecast_horizon"] = self.HORIZON
        print(f"    Forecasted {len(repos)} repos for next {self.HORIZON} days", file=sys.stderr)
        return context
