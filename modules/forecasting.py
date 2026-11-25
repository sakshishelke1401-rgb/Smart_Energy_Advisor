"""Next-month forecast (trend, plus seasonal terms once there are 12+ months) and the what-if simulator."""
import math

import numpy as np

from .common import js_round, next_month


def _features(index: int, month: int, seasonal: bool):
    f = [1.0, float(index)]
    if seasonal:
        angle = 2 * math.pi * month / 12
        f += [math.sin(angle), math.cos(angle)]
    return f


def forecast_next_month(rows):
    """Least-squares regression on the bill history. Returns None with fewer than 3 months."""
    n = len(rows)
    if n < 3:
        return None
    seasonal = n >= 12
    X = np.array([_features(i, int(r["m"][5:7]), seasonal) for i, r in enumerate(rows)])
    y = np.array([r["u"] for r in rows], dtype=float)
    beta = np.linalg.solve(X.T @ X + 1e-6 * np.eye(X.shape[1]), X.T @ y)
    month = next_month(rows[-1]["m"])
    pred = max(0.0, float(np.array(_features(n, int(month[5:7]), seasonal)) @ beta))
    sd = float(np.sqrt(np.mean((y - X @ beta) ** 2))) or pred * 0.1
    rates = sorted(r["a"] / r["u"] for r in rows if r["u"] > 0)
    rate = rates[len(rates) // 2] if rates else 0.0
    return {"m": month, "u": pred, "lo": max(0.0, pred - sd), "hi": pred + sd,
            "amt": pred * rate, "rate": rate, "seasonal": seasonal}


def what_if(forecast: dict, share: float, pct: float) -> dict:
    """Change one appliance's usage by `pct` percent and see the effect on next month's bill."""
    new_units = max(0.0, forecast["u"] + forecast["u"] * share * pct / 100)
    new_amount = js_round(new_units * forecast["rate"])
    return {"units": round(new_units, 1), "amount": new_amount, "savings": js_round(forecast["amt"]) - new_amount}
