from modules.enterprise import analyze_enterprise


def rows(org, department="Area A", after=False):
    data = []
    for month, units in [("2026-01", 100), ("2026-02", 110), ("2026-03", 180)]:
        item = {"month": month, "building": "Main", "department": department,
                "units": units, "amount": units * 9, "organization_type": org}
        if after:
            item["after_hours_units"] = units * .25
        data.append(item)
    return data


def test_hospital_advice_never_suggests_switching_off_critical_equipment():
    result = analyze_enterprise(rows("hospital", "ICU"))
    advice = " ".join(x["recommendation"] for x in result["recommendations"]).lower()
    assert "critical clinical" in advice
    assert result["departments"][0]["after_hours_available"] is False
    assert not any(x["basis"] == "After-hours consumption" for x in result["recommendations"])


def test_after_hours_recommendation_requires_the_column():
    absent = analyze_enterprise(rows("office"))
    present = analyze_enterprise(rows("office", after=True))
    assert not any(x["basis"] == "After-hours consumption" for x in absent["recommendations"])
    assert any(x["basis"] == "After-hours consumption" for x in present["recommendations"])


def test_hotel_and_restaurant_guidance_is_type_specific():
    hotel = analyze_enterprise(rows("hotel", "Guest Rooms"))
    restaurant = analyze_enterprise(rows("restaurant", "Kitchen"))
    assert any("guest-room" in x["recommendation"] for x in hotel["recommendations"])
    assert any("refrigeration" in x["recommendation"] for x in restaurant["recommendations"])
