"""Rule-based saving tips driven by the user's own appliance mix, anomalies and forecast."""
from .appliance_breakdown import ranked, total
from .common import APPLIANCE_NAMES, js_round, month_label

TIPS = {
    "ac": "Set the AC to 24–26°C and clean its filters monthly — each degree lower adds roughly 6% to cooling cost.",
    "fridge": "Keep the fridge away from walls and sunlight, and check that the door seal is tight.",
    "light": "Swap any remaining CFL or old bulbs for LEDs and switch lights off in empty rooms.",
    "wash": "Run full loads and use cold-water cycles when you can.",
    "tv": "Turn on eco mode and avoid leaving the TV on standby.",
    "misc": "Unplug chargers and small appliances when idle — standby load adds up.",
}
GENERAL = "Shift heavy appliance use to off-peak hours if your tariff has time-of-day pricing."


def build_recommendations(last, forecast, anomalies, avg_units):
    recs = []
    ap = last.get("ap")
    if ap:
        top = ranked(ap)[0]
        pct = js_round(100 * ap[top] / total(ap))
        recs.append({"title": APPLIANCE_NAMES[top],
                     "text": f"{TIPS[top]} It makes up {pct}% of {month_label(last['m'])}."})
    if anomalies:
        a = anomalies[-1]
        if a["ratio"] > 1:
            text = (f"Check whether an appliance ran longer than usual in {month_label(a['m'])} — usage was "
                    f"{js_round((a['ratio'] - 1) * 100)}% higher than a year earlier.")
            recs.append({"title": "Unusual spike", "text": text})
        else:
            text = (f"Usage fell {js_round((1 - a['ratio']) * 100)}% in {month_label(a['m'])} compared with a year "
                    "earlier — make sure that was expected.")
            recs.append({"title": "Unusual drop", "text": text})
    if forecast and forecast["u"] > avg_units * 1.1:
        recs.append({"title": "Next month",
                     "text": f"Your forecast ({js_round(forecast['u'])} units) is above your average of "
                             f"{js_round(avg_units)}. Plan heavy-appliance use and cooling carefully."})
    recs.append({"title": "General", "text": GENERAL})
    return recs
