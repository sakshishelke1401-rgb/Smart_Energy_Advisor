"""Unit tests for the data-science modules."""
import pytest

from modules.anomaly_detection import detect_anomalies
from modules.forecasting import forecast_next_month, what_if
from modules.ocr_extractor import parse_bill_text
from modules.preprocessing import parse_csv_bytes, parse_month, to_number, validate_entry
from modules.sample_data import sample_rows


def test_to_number():
    assert to_number("₹1,850.50") == 1850.5
    assert to_number("Rs. 360") == 360
    assert to_number("28,5") == 28.5          # decimal comma
    assert to_number("1,850") == 1850         # thousands comma
    assert to_number("") is None and to_number("abc") is None and to_number(None) is None


@pytest.mark.parametrize("raw,expected", [("2026-09", "2026-09"), ("2026-9-15", "2026-09"), ("09/2026", "2026-09"),
                                          ("Sep 2026", "2026-09"), ("September 2026", "2026-09"),
                                          ("15-09-2026", "2026-09"), ("nonsense", None), ("2026-13", None)])
def test_parse_month(raw, expected):
    assert parse_month(raw) == expected


def test_csv_semicolons_aliases_dedupe_and_skips():
    rows, skipped = parse_csv_bytes(b"Month;Units;Amount\n2026-01;30;320\nJan 2026;31;330\n2026-02;28,5;300\nbad;x;y\n")
    assert [r["m"] for r in rows] == ["2026-01", "2026-02"]
    assert rows[0]["u"] == 31 and rows[1]["u"] == 28.5 and skipped == 1


def test_csv_errors():
    with pytest.raises(ValueError, match="required columns"):
        parse_csv_bytes(b"a,b\n1,2\n")
    with pytest.raises(ValueError, match="empty"):
        parse_csv_bytes(b"only a header")
    with pytest.raises(ValueError, match="No valid rows"):
        parse_csv_bytes(b"billing_month,units_consumed,bill_amount\nx,y,z\n")


def test_validate_entry():
    row = validate_entry("2026-09", "33", "360", {"ac": "5", "fridge": ""})
    assert row == {"m": "2026-09", "u": 33.0, "a": 360.0, "ap": {"ac": 5.0}}
    for bad in [("", "1", "1"), ("2026-09", "", "1"), ("2026-09", "1", "-5"), ("2026-09", "9e9", "1")]:
        with pytest.raises(ValueError):
            validate_entry(*bad)


def test_forecast_needs_three_months_and_uses_seasons_after_twelve():
    rows = sample_rows()
    assert forecast_next_month(rows[:2]) is None
    assert forecast_next_month(rows[:6])["seasonal"] is False
    f = forecast_next_month(rows)
    assert f["seasonal"] is True and f["m"] == "2026-10" and 25 < f["u"] < 36 and f["lo"] < f["u"] < f["hi"]


def test_what_if_reduces_the_bill():
    f = forecast_next_month(sample_rows())
    base = what_if(f, 0.1, 0)
    cut = what_if(f, 0.1, -50)
    assert base["savings"] == 0 and cut["savings"] > 0 and cut["amount"] < base["amount"]


def test_anomalies_ignore_normal_summer_rise():
    found = detect_anomalies(sample_rows())
    assert [a["m"] for a in found] == ["2026-08"]          # the genuine spike only
    assert detect_anomalies(sample_rows()[:12]) == []     # no year-on-year comparison possible yet


def test_ocr_text_parser_english_and_marathi():
    en = parse_bill_text("BILL OF SUPPLY FOR THE MONTH OF Sep 2026\nUnits Consumed : 33\nNet Payable Rs. 1,850.50")
    assert en == {"m": "2026-09", "u": 33.0, "a": 1850.5}
    mr = parse_bill_text("बिलिंग महिना सप्टेंबर-२०२६  एकूण वापर : ३३ युनिट  देयक रक्कम रु : ३६०.००")
    assert mr == {"m": "2026-09", "u": 33.0, "a": 360.0}
    assert parse_bill_text("nothing useful here") == {"m": None, "u": None, "a": None}
