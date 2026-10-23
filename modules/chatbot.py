"""Watt — the rule-based assistant. Answers come from Python and use the visitor's real data."""
import re

from .anomaly_detection import detect_anomalies
from .appliance_breakdown import ranked, total
from .common import APPLIANCE_NAMES, js_round, month_label
from .forecasting import forecast_next_month
from .recommendations import GENERAL, TIPS

PAGES = {
    "login": "This is the login page. Log in (or continue as a guest) to get started — your bills and forecasts "
             "stay tied to your account. After that you'll move on to “Add Bill”, where you bring in your usage data.",
    "add-bill": "This page is where you give me your electricity data. Pick one of three ways: CSV Upload for a "
                "spreadsheet of past bills, Manual Entry for a single bill, or Bill Photo (OCR) to read a photo of "
                "your bill. When you're done, tap “See my dashboard”.",
    "dashboard": "This dashboard turns your bill into insight. At the top is the latest bill in your data, then next "
                 "month's forecast, a trend chart with unusual months flagged, an appliance-wise breakdown, a "
                 "what-if simulator to test savings, and personalized tips at the bottom.",
}
NEED_DATA = "Add your bills first (CSV, manual entry or a photo) and I'll work that out from your data."
FALLBACK = ("I'm not sure about that one yet. Try asking about the forecast, anomalies, the simulator, CSV or photo "
            "upload — or tap “Explain this page”.")


def _forecast_text(ctx):
    rows = ctx["rows"]
    if not rows:
        return NEED_DATA
    f = forecast_next_month(rows)
    if not f:
        return "I need at least 3 months of bills to forecast. Add more on the Add Bill page."
    tail = (" that also learns your seasonal pattern." if len(rows) >= 12
            else " (once you have 12+ months it also learns the seasons).")
    return (f"Your forecast for {month_label(f['m'])} is about {js_round(f['u'])} units (₹{js_round(f['amt'])}), "
            f"likely between {js_round(f['lo'])} and {js_round(f['hi'])}. It is a regression on your bill history{tail}")


def _anomaly_text(ctx):
    rows = ctx["rows"]
    if not rows:
        return NEED_DATA
    found = detect_anomalies(rows)
    if not found:
        return ("Unusual-month checks compare each month with the same month a year earlier, so I need 13+ months "
                "of bills first." if len(rows) < 13
                else "No month stands out against the same month a year earlier, so nothing is flagged.")
    a = found[-1]
    return (f"{month_label(a['m'])} ({a['u']:g} units) is {js_round(abs(a['ratio'] - 1) * 100)}% "
            f"{'higher' if a['ratio'] > 1 else 'lower'} than the same month a year earlier ({a['prev']:g} units), "
            "so it is flagged.")


def _appliance_text(ctx):
    rows = ctx["rows"]
    if not rows:
        return NEED_DATA
    ap = rows[-1].get("ap")
    if not ap:
        return "Your data has no appliance columns yet. Add ac_units, fridge_units and so on to see a breakdown."
    top = ranked(ap)[0]
    return f"{APPLIANCE_NAMES[top]} is the biggest share ({js_round(100 * ap[top] / total(ap))}%) of {month_label(rows[-1]['m'])}."


def _tip_text(ctx):
    rows = ctx["rows"]
    ap = rows[-1].get("ap") if rows else None
    return TIPS[ranked(ap)[0]] if ap else GENERAL


def _open_dashboard(ctx):
    if not (ctx["signed_in"] and ctx["rows"]):
        return "The dashboard unlocks once you're logged in (or a guest) and have added your bill data.", None
    return "Sure — taking you to the dashboard now. ⬇️", "open_dashboard"


KB = [
    (["show me the dashboard", "take me to the dashboard", "go to dashboard"], _open_dashboard),
    (["smart energy advisor", "what is smart"],
     "Smart Energy Advisor forecasts your next electricity bill, flags unusual usage, shows which appliances use the "
     "most and gives personalised saving tips — all from your own bill history."),
    (["what can you do", "capabilit"],
     "I can explain any part of this page, tell you how the forecast, anomaly flag and simulator work, and guide you "
     "through adding your bill. Just ask — or tap an option."),
    (["get started", "how do i start", "begin"],
     "Easy: log in (or continue as a guest), add your bill by CSV, manual entry or a photo, then tap “See my "
     "dashboard” to see your forecast and tips."),
    (["what can i do", "what is this", "overview"], lambda ctx: PAGES[ctx["section"]]),
    (["safe", "privacy", "secure"],
     "Your bills are stored in this app's database and are only shown when you're logged in. Passwords are stored "
     "hashed, never in plain text."),
    (["account", "sign", "guest", "password", "login", "log in"],
     "Create an account to keep your bills saved, or tap “Continue as guest” to try everything. Guest data is "
     "temporary and is cleared after a few days."),
    (["which option", "pick", "choose", "best way"],
     "Got a spreadsheet of past bills? Use CSV Upload. Just one bill in hand? Manual Entry is quickest. Have a photo? "
     "OCR reads it for you — no typing."),
    (["csv", "spreadsheet", "column", "excel"],
     "Your CSV needs billing_month, units_consumed and bill_amount. Add appliance columns (ac_units, fridge_units…) "
     "to unlock the appliance breakdown and the what-if simulator."),
    (["ocr", "photo", "misread", "scan", "image"],
     "OCR runs on the server with Tesseract. It works best on clear bills; Marathi text needs the Marathi language "
     "pack. Always check the month, units and amount before confirming."),
    (["manual", "type"],
     "Manual Entry takes three things from your paper bill: the billing month, units consumed and bill amount. Add "
     "one month at a time."),
    (["forecast", "predict", "next month"], _forecast_text),
    (["anomal", "spike", "unusual", "flag"], _anomaly_text),
    (["simulat", "what-if", "what if", "slider"],
     "Pick an appliance, drag the slider to use it more or less, and the simulated bill and savings update instantly "
     "— e.g. cutting AC use by 20% changes next month's estimate."),
    (["appliance", "breakdown", "fridge", "share"], _appliance_text),
    (["recommend", "tip", "save", "reduce", "lower"], _tip_text),
    (["who", "made", "project", "built"],
     "Smart Energy Advisor is a final-year Data Science field project by Sakshi Shelke — forecasting, anomaly "
     "detection, OCR and recommendations in one place."),
    (["hi", "hello", "hey", "thanks", "thank"],
     "Hi! I'm Watt ⚡ — ask me about anything on this page, or tap “Explain this page”."),
]


def _matches(keyword: str, text: str) -> bool:
    return bool(re.search(r"\b" + re.escape(keyword) + r"\b", text)) if len(keyword) <= 3 else keyword in text


def reply(message: str, section: str, signed_in: bool, rows) -> dict:
    """Return {'reply': str, 'action': optional str}."""
    section = section if section in PAGES else "login"
    ctx = {"section": section, "signed_in": signed_in, "rows": rows}
    text = message.lower()
    if re.search(r"explain|describe|this page|this dashboard|walk me", text):
        return {"reply": PAGES[section], "action": None}
    for keywords, answer in KB:
        if any(_matches(k, text) for k in keywords):
            if callable(answer):
                out = answer(ctx)
                return {"reply": out[0], "action": out[1]} if isinstance(out, tuple) else {"reply": out, "action": None}
            return {"reply": answer, "action": None}
    return {"reply": FALLBACK, "action": None}
