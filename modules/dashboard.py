"""Turns a user's bill rows into everything the dashboard shows (forecast, chart, anomalies, tips...)."""
from .anomaly_detection import detect_anomalies
from .appliance_breakdown import breakdown, ranked, shares
from .common import APPLIANCE_NAMES, js_round, month_label, short_month
from .forecasting import forecast_next_month
from .recommendations import build_recommendations


def build_dashboard(rows, source: str, sample: bool) -> dict:
    last, n = rows[-1], len(rows)
    ap = last.get("ap")
    f = forecast_next_month(rows)
    anomalies = detect_anomalies(rows)
    la = anomalies[-1] if anomalies else None
    avg = sum(r["u"] for r in rows) / n
    flagged = {a["m"] for a in anomalies}

    points = [{"m": r["m"], "label": short_month(r["m"]), "v": r["u"], "an": r["m"] in flagged, "fc": False}
              for r in rows[-12:]]
    if f:
        points.append({"m": f["m"], "label": short_month(f["m"]) + "*", "v": round(f["u"], 1), "an": False, "fc": True})

    high, low = last["u"] > avg * 1.2, last["u"] < avg * 0.8
    if la:
        pct = js_round(abs(la["ratio"] - 1) * 100)
        note = (f"{month_label(la['m'])} ({la['u']:g} units) was {pct}% {'higher' if la['ratio'] > 1 else 'lower'} "
                f"than the same month a year earlier ({la['prev']:g} units).")
    elif n < 13:
        note = "Add 13+ months of bills and I’ll compare each month with the same month last year to spot unusual ones."
    else:
        note = "No month stands out compared with the same month a year earlier."

    if f and ap:
        sim = {"enabled": True, "appliances": [{"key": k, "name": APPLIANCE_NAMES[k]} for k in ranked(ap)]}
    else:
        sim = {"enabled": False,
               "message": "Add appliance columns to your data to use the simulator." if f
               else "Add at least 3 months of bills to use the simulator."}

    return {
        "sample": sample,
        "source": source,
        "months": n,
        "bill": {"month": month_label(last["m"]), "units": round(last["u"], 1), "amount": f"{last['a']:.2f}"},
        "forecast": None if not f else {
            "month": month_label(f["m"]), "units": js_round(f["u"]), "lo": js_round(f["lo"]),
            "hi": js_round(f["hi"]), "amount": js_round(f["amt"]), "months_used": min(12, n)},
        "usage": {"value": f"{last['u']:g} units",
                  "label": "Above average" if high else "Below average" if low else "Normal",
                  "tone": "warn" if high else "ok"},
        "anomaly": {"value": month_label(la["m"]) if la else "None found",
                    "label": ("Spike" if la["ratio"] > 1 else "Drop") if la else ("Needs 13+ months" if n < 13 else "All clear"),
                    "tone": "warn" if la else "ok"},
        "top_appliance": None if not ap else {"name": APPLIANCE_NAMES[ranked(ap)[0]],
                                              "label": f"{round(ap[ranked(ap)[0]], 1):g} u"},
        "chart": {"points": points},
        "chart_note": {"text": note, "ok": la is None},
        "appliances": None if not ap else {
            "subtitle": f"Share of {month_label(last['m'])}’s {js_round(last['u'])} units",
            "items": breakdown(ap)},
        "simulator": sim,
        "recommendations": build_recommendations(last, f, anomalies, avg),
    }


def simulator_shares(rows):
    """Appliance shares of the latest month (None when the data has no appliance split)."""
    ap = rows[-1].get("ap")
    return shares(ap) if ap else None
