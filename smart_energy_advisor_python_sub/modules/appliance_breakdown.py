"""Appliance-wise share of the latest month."""
from .common import APPLIANCE_NAMES, js_round


def total(ap: dict) -> float:
    return sum(ap.values()) or 1.0


def shares(ap: dict) -> dict:
    t = total(ap)
    return {k: v / t for k, v in ap.items()}


def ranked(ap: dict) -> list[str]:
    return sorted(ap, key=lambda k: ap[k], reverse=True)


def breakdown(ap: dict) -> list[dict]:
    t = total(ap)
    return [{"key": k, "name": APPLIANCE_NAMES[k], "units": round(ap[k], 1), "pct": js_round(100 * ap[k] / t)}
            for k in ranked(ap)]
