"""Enterprise energy analytics for schools, colleges, offices and factories.

Input records: month (YYYY-MM), building, department, units, amount,
optional after_hours_units and organization_type. Additive to household workflow.
"""
from collections import defaultdict
from datetime import date
import math
import numpy as np


def _number(value, field, minimum=0):
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be a number.")
    if not math.isfinite(result) or result < minimum:
        raise ValueError(f"{field} must be a finite number >= {minimum}.")
    return result


def validate_records(records):
    if not isinstance(records, list) or len(records) < 3:
        raise ValueError("Provide at least 3 monthly department records.")
    clean = []
    for i, row in enumerate(records, 1):
        if not isinstance(row, dict):
            raise ValueError(f"Record {i} must be an object.")
        month = str(row.get("month", "")).strip()
        try:
            date.fromisoformat(month + "-01")
        except ValueError:
            raise ValueError(f"Record {i}: month must use YYYY-MM format.")
        building = str(row.get("building", "")).strip()[:80]
        department = str(row.get("department", "")).strip()[:80]
        if not building or not department:
            raise ValueError(f"Record {i}: building and department are required.")
        units = _number(row.get("units"), f"Record {i} units")
        amount = _number(row.get("amount"), f"Record {i} amount")
        after = _number(row.get("after_hours_units", 0), f"Record {i} after_hours_units")
        if after > units:
            raise ValueError(f"Record {i}: after_hours_units cannot exceed units.")
        clean.append({"month": month, "building": building, "department": department,
                      "units": units, "amount": amount, "after_hours_units": after,
                      "after_hours_available": bool(row.get("after_hours_available", "after_hours_units" in row)),
                      "organization_type": str(row.get("organization_type", "school")).lower()})
    return sorted(clean, key=lambda r: (r["department"], r["month"], r["building"]))


def _kmeans_groups(items, k=3, iterations=30):
    """Deterministic 1-D K-Means over department average monthly units (NumPy only)."""
    if not items:
        return {}
    values = np.array([x["average_units"] for x in items], dtype=float)
    k = min(k, len(values))
    if k == 1:
        return {x["department"]: "Typical" for x in items}
    centers = np.quantile(values, np.linspace(0, 1, k))
    labels = np.zeros(len(values), dtype=int)
    for _ in range(iterations):
        new_labels = np.argmin(np.abs(values[:, None] - centers[None, :]), axis=1)
        new_centers = np.array([values[new_labels == j].mean() if np.any(new_labels == j) else centers[j]
                                for j in range(k)])
        if np.array_equal(labels, new_labels) and np.allclose(centers, new_centers):
            labels, centers = new_labels, new_centers
            break
        labels, centers = new_labels, new_centers
    order = np.argsort(centers)
    names = ["Low consumption", "Medium consumption", "High consumption"]
    label_names = {int(old): names[pos] for pos, old in enumerate(order)}
    return {x["department"]: label_names[int(labels[i])] for i, x in enumerate(items)}


def _linear_forecast(monthly):
    if len(monthly) < 3:
        return None
    y = np.array([x["units"] for x in monthly], dtype=float)
    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    return round(max(0.0, float(intercept + slope * len(y))), 1)


def analyze_enterprise(records):
    rows = validate_records(records)
    groups = defaultdict(list)
    for row in rows:
        groups[row["department"]].append(row)
    departments, alerts = [], []
    for name, values in groups.items():
        by_month = defaultdict(lambda: {"units": 0.0, "amount": 0.0, "after": 0.0})
        for row in values:
            item = by_month[row["month"]]
            item["units"] += row["units"]
            item["amount"] += row["amount"]
            item["after"] += row["after_hours_units"]
        monthly = [{"month": m, "units": round(v["units"], 2), "amount": round(v["amount"], 2),
                    "after_hours_units": round(v["after"], 2)} for m, v in sorted(by_month.items())]
        avg, latest = sum(x["units"] for x in monthly) / len(monthly), monthly[-1]
        item = {"department": name, "buildings": sorted({r["building"] for r in values}),
                "months": len(monthly), "latest_month": latest["month"], "latest_units": latest["units"],
                "average_units": round(avg, 1), "latest_amount": latest["amount"],
                "forecast_next_month_units": _linear_forecast(monthly),
                "after_hours_units": latest["after_hours_units"],
                "after_hours_share_pct": round(100 * latest["after_hours_units"] / latest["units"], 1)
                    if latest["units"] else 0.0, "after_hours_available": all(r["after_hours_available"] for r in values), "history": monthly}
        departments.append(item)
        if len(monthly) >= 2 and monthly[-2]["units"] > 0:
            prev = monthly[-2]["units"]
            change = (latest["units"] - prev) / prev * 100
            if abs(change) >= 35 and abs(latest["units"] - prev) >= 5:
                alerts.append({"department": name, "month": latest["month"], "change_pct": round(change, 1),
                               "message": f"{name} usage {'increased' if change > 0 else 'decreased'} by {abs(change):.1f}% versus the previous month."})
    departments.sort(key=lambda x: x["latest_units"], reverse=True)
    clusters = _kmeans_groups(departments)
    for item in departments:
        item["consumption_group"] = clusters.get(item["department"], "Typical")
    recommendations = []
    if departments:
        top = departments[0]
        recommendations.append({"basis": "Highest latest-month consumption", "priority": "High",
            "target": top["department"], "recommendation":
            f"Review operating schedules and major equipment in {top['department']}; it has the highest recorded consumption ({top['latest_units']:g} units)."})
        organization = rows[0]["organization_type"]
        department = top["department"].lower()
        guidance = {
            "school": "For classrooms, check that lights and fans are off when rooms are empty; compare classroom and lab usage.",
            "college": "For laboratories or computer rooms, review equipment schedules and switch off non-essential lighting when spaces are unoccupied.",
            "hospital": "Review lighting and HVAC schedules in this department, while keeping all critical clinical and life-support equipment operational.",
            "hotel": "Review guest-room occupancy controls and air-conditioning schedules; retain required ventilation and guest comfort.",
            "restaurant": "Review kitchen operating schedules and refrigeration efficiency; do not interrupt required food-safety temperature control.",
            "office": "Check workstation shutdown settings, lighting schedules and electricity use outside normal office hours.",
            "factory": "Compare machine-level operating hours and maintenance condition in this production area before changing equipment schedules.",
        }
        if organization in guidance:
            recommendations.append({"basis": f"{organization.replace('_', ' ').title()} operating guidance", "priority": "Medium",
                "target": top["department"], "recommendation": guidance[organization]})
    for item in departments:
        if item["after_hours_available"] and item["after_hours_share_pct"] >= 15:
            recommendations.append({"basis": "After-hours consumption",
                "priority": "High" if item["after_hours_share_pct"] >= 30 else "Medium",
                "target": item["department"], "recommendation":
                f"{item['after_hours_share_pct']}% of the latest recorded usage in {item['department']} is marked after-hours. Check timers, standby loads and shutdown procedures."})
        if item["forecast_next_month_units"] is not None and item["forecast_next_month_units"] > item["average_units"] * 1.10:
            recommendations.append({"basis": "Consumption forecast", "priority": "Medium", "target": item["department"],
                "recommendation": f"Forecast for {item['department']} is {item['forecast_next_month_units']} units, more than 10% above its historical average. Review planned usage."})
    for alert in alerts:
        recommendations.append({"basis": "Month-to-month anomaly", "priority": "High", "target": alert["department"],
            "recommendation": alert["message"] + " Check meter readings, occupancy and equipment schedules before taking action."})
    latest_total_units = round(sum(x["latest_units"] for x in departments), 1)
    latest_total_amount = round(sum(x["latest_amount"] for x in departments), 2)
    forecast_values = [x["forecast_next_month_units"] for x in departments
                       if x["forecast_next_month_units"] is not None]
    total_forecast_units = round(sum(forecast_values), 1) if forecast_values and len(forecast_values) == len(departments) else None
    effective_rate = latest_total_amount / latest_total_units if latest_total_units else None
    total_forecast_amount = round(total_forecast_units * effective_rate, 2) if total_forecast_units is not None and effective_rate is not None else None
    return {"organization_type": rows[0]["organization_type"], "records_analyzed": len(rows),
            "departments": departments, "alerts": alerts,
            "clusters": [{"department": x["department"], "group": x["consumption_group"]} for x in departments],
            "summary": {"departments": len(departments),
                        "latest_total_units": latest_total_units,
                        "latest_total_amount": latest_total_amount,
                        "forecast_next_month_units": total_forecast_units,
                        "forecast_next_month_amount": total_forecast_amount},
            "recommendations": recommendations,
            "method_notes": ["K-Means groups departments using average monthly units only; groups are relative to this uploaded dataset.",
                "Forecasts use a simple linear trend and are indicative, not guaranteed.",
                "After-hours insights are shown only when the CSV includes an after_hours_units column.",
                "Organization-specific tips are operational guidance; consumption alerts and rankings are calculated from the uploaded readings."]}


def demo_records():
    """Synthetic demo data; replace with authorized meter/export data for field research."""
    source = []
    values = {"Classrooms": [420, 390, 460, 510, 540, 620],
              "Computer Lab": [300, 310, 320, 390, 430, 610],
              "Library": [180, 175, 190, 200, 210, 220],
              "Administration": [150, 145, 160, 165, 170, 175]}
    months = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
    for dept, series in values.items():
        for i, units in enumerate(series):
            after = round(units * (0.08 if dept == "Library" else 0.22 if dept == "Computer Lab" else 0.10), 1)
            source.append({"month": months[i], "building": "Main Campus", "department": dept,
                           "units": units, "amount": round(units * 9.2, 2),
                           "after_hours_units": after, "organization_type": "school"})
    return source
