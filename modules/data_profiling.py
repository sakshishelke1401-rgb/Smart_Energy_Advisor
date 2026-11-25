"""Transparent data-quality profiling for uploaded energy CSV files."""
import re
import pandas as pd

NUMERIC_ALIASES = {
    "units": {"units", "units_consumed", "kwh", "consumption", "energy_kwh", "electricity_units"},
    "amount": {"amount", "bill_amount", "total_amount", "cost", "electricity_cost"},
    "after_hours_units": {"after_hours_units", "afterhours_units", "night_units"},
}
DATE_ALIASES = {"month", "billing_month", "date", "billing_period", "period"}

def _norm(value):
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")

def profile_dataframe(df):
    """Return a compact quality report; never silently edits or drops source rows."""
    rows, cols = df.shape
    missing_by_column = {str(c): int(df[c].isna().sum() + df[c].astype(str).str.strip().isin([""]).sum()) for c in df.columns}
    missing_cells = sum(missing_by_column.values())
    duplicate_rows = int(df.astype(str).duplicated().sum())
    normalized = {_norm(c): c for c in df.columns}
    numeric_checks = {}
    invalid_numeric = 0
    negative_values = 0
    outlier_cells = 0
    for role, aliases in NUMERIC_ALIASES.items():
        col = next((normalized[a] for a in aliases if a in normalized), None)
        if col is None:
            continue
        raw = df[col].astype(str).str.replace(",", "", regex=False).str.replace("₹", "", regex=False).str.strip()
        raw = raw.mask(raw.eq(""))
        values = pd.to_numeric(raw, errors="coerce")
        bad = int((raw.notna() & values.isna()).sum())
        neg = int((values < 0).sum())
        valid = values.dropna()
        outliers = 0
        if len(valid) >= 4:
            q1, q3 = valid.quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr > 0:
                outliers = int(((values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)).sum())
        invalid_numeric += bad
        negative_values += neg
        outlier_cells += outliers
        numeric_checks[role] = {"column": str(col), "invalid_values": bad, "negative_values": neg, "outlier_values": outliers}
    date_col = next((normalized[a] for a in DATE_ALIASES if a in normalized), None)
    invalid_dates = 0
    if date_col:
        vals = df[date_col].astype(str).str.strip()
        # Accept YYYY-MM, common day-first/month-first dates, and ISO dates.
        parsed = pd.to_datetime(vals, errors="coerce", format="mixed")
        invalid_dates = int(parsed.isna().sum())
    issues = []
    if missing_cells: issues.append(f"{missing_cells} missing/blank cells")
    if duplicate_rows: issues.append(f"{duplicate_rows} duplicate rows")
    if invalid_numeric: issues.append(f"{invalid_numeric} non-numeric energy/cost values")
    if negative_values: issues.append(f"{negative_values} negative energy/cost values")
    if invalid_dates: issues.append(f"{invalid_dates} unrecognized date values")
    if outlier_cells: issues.append(f"{outlier_cells} possible numeric outliers (review, not automatic errors)")
    # Transparent penalty-based score; outliers are informational and do not reduce score.
    denominator = max(1, rows * max(1, cols))
    score = round(max(0, 100 - (missing_cells / denominator * 45) - (duplicate_rows / max(1, rows) * 20)
                      - (invalid_numeric / max(1, rows) * 25) - (negative_values / max(1, rows) * 20)
                      - (invalid_dates / max(1, rows) * 15)))
    critical = invalid_numeric > 0 or negative_values > 0 or invalid_dates > 0
    return {
        "rows": int(rows), "columns": int(cols), "missing_cells": missing_cells,
        "missing_by_column": missing_by_column, "duplicate_rows": duplicate_rows,
        "numeric_checks": numeric_checks, "invalid_dates": invalid_dates,
        "possible_outlier_values": outlier_cells, "quality_score": score,
        "quality_score_note": "Rule-based quality indicator (0–100), not an ML probability.",
        "critical_issues": critical, "issues": issues,
    }
