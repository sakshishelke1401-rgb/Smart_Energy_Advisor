"""Automatic CSV dataset classification and validation for Smart Energy Advisor."""
import io
import re
import pandas as pd

ALIASES = {
    "month": {"month", "billing_month", "date", "billing_period", "period"},
    "units": {"units", "units_consumed", "kwh", "consumption", "energy_kwh", "electricity_units"},
    "amount": {"amount", "bill_amount", "total_amount", "cost", "electricity_cost"},
    "building": {"building", "block", "site", "facility", "campus", "location"},
    "department": {"department", "dept", "section", "unit_name", "area"},
    "appliance": {"appliance", "device", "equipment"},
    "after_hours": {"after_hours_units", "afterhours_units", "night_units"},
}
TYPE_TERMS = {
    "hospital": {"hospital", "icu", "ward", "emergency", "operating_theatre", "operating_theaters", "surgery", "diagnostic", "imaging", "patient", "clinical", "pharmacy"},
    "college": {"college", "classroom", "computer_lab", "library", "hostel", "auditorium", "academic_block", "canteen", "student"},
    "school": {"school", "classroom", "school_lab", "playground", "staff_room", "principal"},
    "factory": {"factory", "production", "machinery", "machine", "manufacturing", "assembly_line", "boiler", "industrial"},
    "office": {"office", "floor", "server_room", "workstation", "conference_room", "corporate"},
    "hotel": {"hotel", "guest_room", "guest_rooms", "guestroom", "guestrooms", "housekeeping", "banquet", "lobby", "laundry", "restaurant_kitchen"},
    "restaurant": {"restaurant", "kitchen", "refrigeration", "cold_storage", "dining_area", "dishwasher", "cooking_line", "food_service"},
    "other_organization": {"warehouse", "mall", "retail", "data_center", "airport", "station", "municipal", "water_treatment"},
    "household": {"household", "home", "residential", "ac", "fridge", "refrigerator", "washing_machine", "television", "kitchen"},
}

def norm(value):
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")

def detect_dataset_bytes(data: bytes):
    """Classify from header/value evidence. Confidence is a heuristic score, not ML probability."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
    try:
        df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    except Exception as exc:
        raise ValueError("Could not read this file as a CSV. Check its delimiter and header row.") from exc
    if df.empty or len(df.columns) < 2:
        raise ValueError("CSV needs a header row and at least one data row.")
    if len(df) > 5000:
        raise ValueError("Too many rows (maximum 5,000).")
    normalized = [norm(c) for c in df.columns]
    roles = {}
    for role, aliases in ALIASES.items():
        match = next((c for c in normalized if c in aliases), None)
        if match:
            roles[role] = match
    scores = {k: 0 for k in TYPE_TERMS}
    evidence = {k: [] for k in TYPE_TERMS}
    for col in normalized:
        for kind, terms in TYPE_TERMS.items():
            if col in terms or any(term in col for term in terms):
                scores[kind] += 2
                evidence[kind].append(f"column '{col}'")
    for col in df.columns:
        values = {norm(v) for v in df[col].astype(str).head(200)}
        for kind, terms in TYPE_TERMS.items():
            hits = sorted(values.intersection(terms))
            if hits:
                scores[kind] += min(6, 2 * len(hits))
                evidence[kind].extend(hits[:4])
    appliance_columns = {"ac_units", "fridge_units", "refrigerator_units", "lighting_units", "washing_machine_units", "tv_units", "misc_units"}
    if "appliance" in roles or appliance_columns.intersection(normalized):
        scores["household"] += 4
        evidence["household"].append("appliance field")
    # Generic structure is not evidence for a particular industry. Do not award
    # industry points merely because a file has departments/buildings/months.
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best, top = ranked[0]
    second = ranked[1][1]
    confidence = min(99, round(45 + 7 * top + 3 * (top - second))) if top else 0
    detected = best if confidence >= 60 else "unknown"
    structural_org = "month" in roles and "units" in roles and ("department" in roles or "building" in roles)
    explicit_industry_evidence = top > 0
    if not explicit_industry_evidence and structural_org:
        detected = "other_organization"
        confidence = 62
        evidence["other_organization"].append("generic organization-level month/units/building-or-department structure; industry needs confirmation")
    elif not explicit_industry_evidence:
        detected = "unknown"
        confidence = 0
    # Preserve the evidence for the selected class, including the generic fallback.
    selected_evidence = evidence.get(detected, [])
    labels = {"household":"Household", "school":"School", "college":"College", "hospital":"Hospital", "factory":"Factory", "office":"Office", "hotel":"Hotel", "restaurant":"Restaurant", "other_organization":"Other organization", "unknown":"Unknown"}
    return {"dataset_type": detected, "dataset_label": labels[detected], "confidence": confidence,
            "needs_confirmation": confidence < 75 or detected in ("unknown", "other_organization"), "scores": scores,
            "evidence": selected_evidence, "columns": list(df.columns), "roles": roles, "dataframe": df}

def validate_and_convert_enterprise(detection):
    """Validate organization CSV and convert it to the enterprise analysis schema."""
    df, roles = detection["dataframe"], detection["roles"]
    missing = [r for r in ("month", "units") if r not in roles]
    if "department" not in roles and "building" not in roles:
        missing.append("department or building")
    if missing:
        raise ValueError("Organization dataset is missing required fields: " + ", ".join(missing) + ". Required: month, units, and department or building.")
    def value(row, role, default=""):
        c = roles.get(role)
        return row[c] if c else default
    records, errors = [], []
    for idx, row in df.iterrows():
        month = str(value(row, "month")).strip()
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
            errors.append(f"Row {idx+2}: month must use YYYY-MM format.")
            continue
        try:
            units = float(str(value(row, "units")).replace(",", "").strip())
            amount_text = str(value(row, "amount", "0")).replace("₹", "").replace(",", "").strip()
            amount = float(amount_text) if amount_text else 0.0
            after_text = str(value(row, "after_hours", "0")).replace(",", "").strip()
            after = float(after_text) if after_text else 0.0
        except ValueError:
            errors.append(f"Row {idx+2}: units, amount and after-hours values must be numeric.")
            continue
        if units < 0 or amount < 0 or after < 0 or after > units:
            errors.append(f"Row {idx+2}: values must be non-negative and after-hours units cannot exceed total units.")
            continue
        building = str(value(row, "building", "Unspecified building")).strip() or "Unspecified building"
        department = str(value(row, "department", building)).strip() or building
        records.append({"month": month, "building": building, "department": department, "units": units,
                        "amount": amount, "after_hours_units": after, "after_hours_available": "after_hours" in roles, "organization_type": detection["dataset_type"]})
    if errors:
        raise ValueError("CSV validation failed: " + " ".join(errors[:5]))
    if len(records) < 3:
        raise ValueError("At least 3 valid monthly records are required for organization analysis.")
    return records
