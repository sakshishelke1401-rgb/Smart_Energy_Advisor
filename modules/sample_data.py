"""A 24-month sample household (Oct 2024 - Sep 2026) with one genuine spike in Aug 2026."""
from .common import next_month

SAMPLE_UNITS = [26, 25, 20, 19, 22, 33, 45, 41, 37, 30, 34, 31,
                27, 26, 21, 20, 24, 36, 49, 45, 40, 32, 58, 33]
SAMPLE_START = "2024-10"
RATE_PER_UNIT = 10.8


def sample_rows() -> list[dict]:
    rows, month = [], SAMPLE_START
    for units in SAMPLE_UNITS:
        mo = int(month[5:7])
        ap = {
            "ac": units * (0.35 if 3 <= mo <= 8 else 0.10),
            "fridge": units * 0.15,
            "light": units * 0.10,
            "wash": units * 0.08,
            "tv": units * 0.07,
        }
        ap["misc"] = units - sum(ap.values())
        ap = {k: round(v, 1) for k, v in ap.items()}
        rows.append({"m": month, "u": float(units), "a": round(units * RATE_PER_UNIT, 2), "ap": ap})
        month = next_month(month)
    return rows
