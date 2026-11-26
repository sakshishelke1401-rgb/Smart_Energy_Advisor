"""Small shared helpers: month arithmetic, labels and appliance names."""
import math

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

APPLIANCE_NAMES = {
    "ac": "Air Conditioner",
    "fridge": "Refrigerator",
    "light": "Lighting",
    "wash": "Washing Machine",
    "tv": "Television",
    "misc": "Other / Misc",
}

# internal appliance key -> CSV column name
APPLIANCE_COLUMNS = {
    "ac": "ac_units",
    "fridge": "fridge_units",
    "light": "lighting_units",
    "wash": "washing_machine_units",
    "tv": "tv_units",
    "misc": "misc_units",
}


def month_label(m: str) -> str:
    """'2026-09' -> 'Sep 2026'"""
    return f"{MONTHS[int(m[5:7]) - 1]} {m[:4]}"


def short_month(m: str) -> str:
    return MONTHS[int(m[5:7]) - 1]


def next_month(m: str) -> str:
    year, month = int(m[:4]), int(m[5:7]) + 1
    if month > 12:
        year, month = year + 1, 1
    return f"{year}-{month:02d}"


def previous_year(m: str) -> str:
    return f"{int(m[:4]) - 1}{m[4:]}"


def js_round(x: float) -> int:
    """Round half up (what people expect on a bill), unlike Python's banker's rounding."""
    return int(math.floor(x + 0.5))
