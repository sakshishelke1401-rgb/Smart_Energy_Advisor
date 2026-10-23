"""Reading and cleaning bill data (CSV uploads and manual entries) with pandas."""
import csv
import io
import math
import re
from datetime import datetime

import pandas as pd

from .common import APPLIANCE_COLUMNS, APPLIANCE_NAMES, MONTHS

MAX_ROWS = 5000

HEADER_MAP = {
    "month": "m", "billing_month": "m", "date": "m", "billing_period": "m",
    "units": "u", "units_consumed": "u", "kwh": "u", "consumption": "u",
    "amount": "a", "bill_amount": "a", "total_amount": "a", "bill": "a",
    **{col: key for key, col in APPLIANCE_COLUMNS.items()},
}

_DATE_FORMATS = ("%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y")


def to_number(value):
    """'₹1,850.50' -> 1850.5, '28,5' -> 28.5, ''/junk -> None."""
    if value is None:
        return None
    s = re.sub(r"(?i)[₹\s]|rs\.?", "", str(value))
    if not s:
        return None
    s = s.replace(",", ".") if re.fullmatch(r"\d+,\d{1,2}", s) else s.replace(",", "")
    try:
        n = float(s)
    except ValueError:
        return None
    return n if math.isfinite(n) else None


def parse_month(value):
    """Accepts 2026-09, 2026-09-15, 09/2026, Sep 2026, 15-09-2026 ... -> '2026-09' or None."""
    s = str(value or "").strip()
    m = re.match(r"^(\d{4})[-/.](\d{1,2})", s)
    if m and 1 <= int(m[2]) <= 12:
        return f"{m[1]}-{int(m[2]):02d}"
    m = re.match(r"^(\d{1,2})[-/.](\d{4})$", s)
    if m and 1 <= int(m[1]) <= 12:
        return f"{m[2]}-{int(m[1]):02d}"
    m = re.match(r"^([A-Za-z]{3,9})[\s\-,]*(\d{4})$", s)
    if m:
        names = [x.lower() for x in MONTHS]
        if m[1][:3].lower() in names:
            return f"{m[2]}-{names.index(m[1][:3].lower()) + 1:02d}"
    for fmt in _DATE_FORMATS:
        try:
            d = datetime.strptime(s, fmt)
            return f"{d.year}-{d.month:02d}"
        except ValueError:
            pass
    return None


def parse_csv_bytes(data: bytes):
    """Return (rows, skipped). Raises ValueError with a friendly message on bad files."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) < 2:
        raise ValueError("The file looks empty — it needs a header row and at least one bill.")
    if len(lines) > MAX_ROWS + 1:
        raise ValueError(f"Too many rows (max {MAX_ROWS}).")
    delim = max([",", ";", "\t"], key=lambda d: lines[0].count(d))
    try:
        df = pd.read_csv(io.StringIO("\n".join(lines)), sep=delim, dtype=str, keep_default_na=False,
                         skipinitialspace=True, engine="python", on_bad_lines="skip")
    except Exception:
        raise ValueError("That file couldn't be read as a CSV.")
    cols = {}
    for pos, name in enumerate(df.columns):
        key = HEADER_MAP.get(re.sub(r"[\s-]+", "_", str(name).strip().lower()))
        if key and key not in cols:
            cols[key] = pos
    if not {"m", "u", "a"} <= cols.keys():
        raise ValueError("Could not find the required columns. The header row needs billing_month, units_consumed and bill_amount.")
    by_month, skipped = {}, 0
    for row in df.itertuples(index=False, name=None):
        m, u, a = parse_month(row[cols["m"]]), to_number(row[cols["u"]]), to_number(row[cols["a"]])
        if not m or u is None or u < 0 or a is None or a < 0:
            skipped += 1
            continue
        ap = {}
        for key in APPLIANCE_NAMES:
            if key in cols:
                v = to_number(row[cols[key]])
                if v is not None and v >= 0:
                    ap[key] = v
        by_month[m] = {"m": m, "u": u, "a": a, "ap": ap or None}
    if not by_month:
        raise ValueError("No valid rows found. Check that months look like 2026-09 and that units and amount are numbers.")
    return sorted(by_month.values(), key=lambda r: r["m"]), skipped


def validate_entry(month, units, amount, appliances=None) -> dict:
    """Validate a hand-typed or photo-confirmed bill. Raises ValueError with a friendly message."""
    m = parse_month(month)
    if not m:
        raise ValueError("Pick a billing month.")
    u, a = to_number(units), to_number(amount)
    if u is None or u < 0:
        raise ValueError("Enter the units consumed.")
    if a is None or a < 0:
        raise ValueError("Enter the bill amount.")
    if u > 1_000_000 or a > 100_000_000:
        raise ValueError("Those numbers look too large — please check them.")
    ap = {}
    for key, value in (appliances or {}).items():
        if key in APPLIANCE_NAMES and value not in (None, ""):
            v = to_number(value)
            if v is None or v < 0:
                raise ValueError(f"Check the {APPLIANCE_NAMES[key]} value.")
            ap[key] = v
    return {"m": m, "u": u, "a": a, "ap": ap or None}


def rows_to_csv(rows) -> str:
    keys = list(APPLIANCE_COLUMNS)
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(["billing_month", "units_consumed", "bill_amount", *APPLIANCE_COLUMNS.values()])
    for r in rows:
        ap = r.get("ap") or {}
        w.writerow([r["m"], r["u"], r["a"], *[ap.get(k, "") for k in keys]])
    return out.getvalue()
