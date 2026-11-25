"""Unusual-month detection: a month is flagged when it is 35%+ away from the same month a year earlier.

Comparing with the same month last year (instead of the previous months) means the normal summer
rise in AC usage is *not* reported as a spike.
"""
from .common import previous_year


def detect_anomalies(rows, high=1.35, low=0.65, min_diff=5.0):
    by_month = {r["m"]: r for r in rows}
    found = []
    for r in rows:
        prev = by_month.get(previous_year(r["m"]))
        if not prev or prev["u"] <= 0:
            continue
        ratio = r["u"] / prev["u"]
        if (ratio > high or ratio < low) and abs(r["u"] - prev["u"]) >= min_diff:
            found.append({"m": r["m"], "u": r["u"], "prev": prev["u"], "ratio": ratio})
    return found
