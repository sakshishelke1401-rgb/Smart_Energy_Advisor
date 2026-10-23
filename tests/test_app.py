"""End-to-end tests for the Flask API (accounts, uploads, dashboard, simulator, chat, OCR)."""
import io

import pytest
from PIL import Image, ImageDraw, ImageFont

from modules import ocr_extractor
from modules.preprocessing import rows_to_csv
from modules.sample_data import sample_rows

CSV_OK = rows_to_csv(sample_rows()[-12:]).encode()


def csv_file(content=CSV_OK, name="bills.csv"):
    return {"file": (io.BytesIO(content), name)}


# ---- pages & security ---------------------------------------------------------------------------
def test_index_page_and_security_headers(client):
    r = client.get("/")
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "Smart Energy Advisor" in html
    assert "<script>" not in html                       # no inline scripts, so the strict CSP works
    assert "script-src" not in r.headers["Content-Security-Policy"] or "unsafe-inline" not in r.headers["Content-Security-Policy"]
    assert r.headers["X-Frame-Options"] == "DENY" and r.headers["X-Content-Type-Options"] == "nosniff"
    css, js = client.get("/assets/app.css"), client.get("/assets/app.js")
    assert css.status_code == 200 and css.mimetype == "text/css" and "--acc" in css.get_data(as_text=True)
    assert js.status_code == 200 and js.mimetype == "text/javascript" and "api('/api/me')" in js.get_data(as_text=True)
    assert client.get("/assets/app.css", headers={"If-None-Match": css.headers["ETag"]}).status_code == 304
    assert client.get("/static/js/app.js").status_code == 404           # no loose static files any more
    assert 'href="/assets/app.css?v=' in html and 'src="/assets/app.js?v=' in html


def test_post_requires_csrf_token(app):
    c = app.test_client()
    assert c.post("/api/guest").status_code == 403
    assert c.post("/api/guest", headers={"X-CSRF-Token": "wrong"}).status_code == 403


def test_api_requires_a_session(client):
    for path in ("/api/dashboard",):
        assert client.get(path).status_code == 401
    assert client.post("/api/sample").status_code == 401
    assert client.post("/api/bills", json={}).status_code == 401


# ---- accounts -------------------------------------------------------------------------------------
def test_signup_login_logout(client, app):
    r = client.post("/api/signup", json={"email": "Sakshi@Example.com", "password": "secret1", "name": "Sakshi"})
    assert r.status_code == 200 and r.get_json()["user"] == {"email": "sakshi@example.com", "name": "Sakshi"}
    assert client.get("/api/me").get_json()["user"]["name"] == "Sakshi"
    import sqlite3
    stored = sqlite3.connect(app.config["DATABASE"]).execute("SELECT pw_hash FROM users").fetchone()[0]
    assert "secret1" not in stored and stored != "secret1"        # hashed, never plain text

    assert client.post("/api/logout").get_json()["user"] is None
    assert client.post("/api/login", json={"email": "sakshi@example.com", "password": "secret1"}).status_code == 200
    assert client.get("/api/me").get_json()["user"]["email"] == "sakshi@example.com"


def test_signup_and_login_validation(client):
    assert client.post("/api/signup", json={"email": "bad", "password": "secret1"}).status_code == 400
    assert client.post("/api/signup", json={"email": "a@b.co", "password": "123"}).status_code == 400
    assert client.post("/api/signup", json={"email": "a@b.co", "password": "secret1"}).status_code == 200
    client.post("/api/logout")
    assert client.post("/api/signup", json={"email": "a@b.co", "password": "secret1"}).status_code == 409
    r = client.post("/api/login", json={"email": "a@b.co", "password": "wrongpw"})
    assert r.status_code == 401 and "Wrong email or password" in r.get_json()["error"]
    assert client.post("/api/login", json={"email": "nobody@b.co", "password": "secret1"}).status_code == 401


def test_login_is_rate_limited(client):
    client.post("/api/signup", json={"email": "a@b.co", "password": "secret1"})
    client.post("/api/logout")
    codes = [client.post("/api/login", json={"email": "a@b.co", "password": "nope-nope"}).status_code for _ in range(10)]
    assert codes[:8] == [401] * 8 and codes[8] == 429
    assert client.post("/api/login", json={"email": "a@b.co", "password": "secret1"}).status_code == 429


def test_guest_session(client):
    me = client.post("/api/guest").get_json()
    assert me["guest"] is True and me["user"] is None and me["has_data"] is False


# ---- data in ------------------------------------------------------------------------------------
def test_dashboard_needs_data(guest):
    assert guest.get("/api/dashboard").status_code == 409


def test_sample_data_dashboard(guest):
    assert guest.post("/api/sample").status_code == 200
    assert guest.get("/api/me").get_json()["has_data"] is True
    d = guest.get("/api/dashboard").get_json()
    assert d["sample"] is True and d["bill"]["month"] == "Sep 2026" and d["months"] == 24
    assert d["forecast"]["month"] == "Oct 2026" and 25 < d["forecast"]["units"] < 36
    assert d["anomaly"] == {"value": "Aug 2026", "label": "Spike", "tone": "warn"}
    assert d["chart"]["points"][-1]["fc"] is True and any(p["an"] for p in d["chart"]["points"])
    assert d["appliances"]["items"][0]["name"] == "Other / Misc" and d["simulator"]["enabled"] is True
    assert d["recommendations"][-1]["title"] == "General"


def test_csv_upload_replaces_data_and_persists(client):
    client.post("/api/signup", json={"email": "a@b.co", "password": "secret1"})
    r = client.post("/api/upload/csv", data=csv_file(), content_type="multipart/form-data")
    assert r.status_code == 200 and r.get_json()["months"] == 12 and r.get_json()["source"] == "bills.csv"
    d = client.get("/api/dashboard").get_json()
    assert d["sample"] is False and d["source"] == "bills.csv" and d["months"] == 12
    # still there after logging out and back in
    client.post("/api/logout")
    client.post("/api/login", json={"email": "a@b.co", "password": "secret1"})
    assert client.get("/api/dashboard").get_json()["source"] == "bills.csv"


def test_csv_upload_errors(guest):
    post = lambda **kw: guest.post("/api/upload/csv", content_type="multipart/form-data", **kw)
    assert post(data={}).status_code == 400
    assert post(data=csv_file(name="bills.pdf")).status_code == 400
    r = post(data=csv_file(b"a,b\n1,2\n"))
    assert r.status_code == 400 and "required columns" in r.get_json()["error"]
    assert post(data=csv_file(b"x" * (5 * 1024 * 1024 + 10))).status_code in (400, 413)
    assert post(data=csv_file(b"x" * (7 * 1024 * 1024))).status_code == 413


def test_manual_entries_unlock_forecast_after_three_months(guest):
    r = guest.post("/api/bills", json={"month": "2026-07", "units": "30", "amount": "320"})
    assert r.get_json()["months"] == 1 and r.get_json()["month_label"] == "Jul 2026"
    d = guest.get("/api/dashboard").get_json()
    assert d["forecast"] is None and d["simulator"]["enabled"] is False and d["sample"] is False
    guest.post("/api/bills", json={"month": "2026-08", "units": "34", "amount": "360"})
    r = guest.post("/api/bills", json={"month": "2026-09", "units": "33", "amount": "355", "appliances": {"ac": "5", "fridge": "6"}})
    assert r.get_json()["months"] == 3
    d = guest.get("/api/dashboard").get_json()
    assert d["forecast"]["month"] == "Oct 2026"
    assert d["appliances"]["items"][0]["name"] == "Refrigerator"      # 6 units beats 5 units of AC
    assert d["simulator"]["enabled"] is True


def test_manual_entry_validation(guest):
    for payload in [{"month": "", "units": "1", "amount": "1"}, {"month": "2026-09", "units": "", "amount": "1"},
                    {"month": "2026-09", "units": "1", "amount": "x"}, {"month": "2026-09", "units": "-3", "amount": "1"}]:
        assert guest.post("/api/bills", json=payload).status_code == 400
    assert guest.post("/api/bills", data="not json", content_type="text/plain").status_code == 400


def test_same_month_is_updated_not_duplicated(guest):
    guest.post("/api/bills", json={"month": "2026-09", "units": "30", "amount": "300"})
    r = guest.post("/api/bills", json={"month": "2026-09", "units": "35", "amount": "380"})
    assert r.get_json()["months"] == 1
    assert guest.get("/api/dashboard").get_json()["bill"]["units"] == 35


def test_users_cannot_see_each_others_data(app):
    from tests.conftest import Client
    a, b = Client(app), Client(app)
    a.post("/api/signup", json={"email": "a@x.co", "password": "secret1"})
    b.post("/api/signup", json={"email": "b@x.co", "password": "secret1"})
    a.post("/api/upload/csv", data=csv_file(), content_type="multipart/form-data")
    assert a.get("/api/me").get_json()["has_data"] is True
    assert b.get("/api/me").get_json()["has_data"] is False and b.get("/api/dashboard").status_code == 409


def test_guest_data_follows_them_into_a_new_account(client):
    client.post("/api/guest")
    client.post("/api/bills", json={"month": "2026-09", "units": "33", "amount": "360"})
    client.post("/api/signup", json={"email": "a@b.co", "password": "secret1"})
    me = client.get("/api/me").get_json()
    assert me["guest"] is False and me["has_data"] is True
    assert client.get("/api/dashboard").get_json()["months"] == 1


# ---- simulator ----------------------------------------------------------------------------------
def test_simulator(guest):
    guest.post("/api/sample")
    base = guest.post("/api/simulate", json={"appliance": "ac", "pct": 0}).get_json()
    cut = guest.post("/api/simulate", json={"appliance": "ac", "pct": -50}).get_json()
    more = guest.post("/api/simulate", json={"appliance": "ac", "pct": 50}).get_json()
    assert base["savings"] == 0 and cut["savings"] > 0 and more["savings"] < 0 and cut["amount"] < base["amount"] < more["amount"]
    assert guest.post("/api/simulate", json={"appliance": "toaster", "pct": 5}).status_code == 400
    assert guest.post("/api/simulate", json={"appliance": "ac", "pct": 500}).status_code == 400
    assert guest.post("/api/simulate", json={"appliance": "ac", "pct": "abc"}).status_code == 400


# ---- chatbot ------------------------------------------------------------------------------------
def test_chat_answers_use_real_data(guest):
    ask = lambda m, s="dashboard": guest.post("/api/chat", json={"message": m, "section": s}).get_json()
    assert "Add your bills first" in ask("how is the forecast made?")["reply"]
    guest.post("/api/sample")
    assert "Oct 2026" in ask("how is the forecast made?")["reply"]
    assert "Aug 2026" in ask("what's the anomaly flag?")["reply"]
    assert "This dashboard" in ask("Explain this dashboard")["reply"]
    assert ask("show me the dashboard")["action"] == "open_dashboard"
    assert "not sure" in ask("blorp zzz")["reply"]
    assert guest.post("/api/chat", json={"message": "  "}).status_code == 400


def test_chat_works_before_login_but_keeps_dashboard_locked(client):
    r = client.post("/api/chat", json={"message": "show me the dashboard", "section": "login"}).get_json()
    assert r["action"] is None and "unlocks" in r["reply"]
    assert "login page" in client.post("/api/chat", json={"message": "explain this page", "section": "login"}).get_json()["reply"]


# ---- misc ---------------------------------------------------------------------------------------
def test_csv_template_download(client):
    r = client.get("/api/template.csv")
    assert r.status_code == 200 and "attachment" in r.headers["Content-Disposition"]
    assert r.get_data(as_text=True).splitlines()[0].startswith("billing_month,units_consumed,bill_amount")


# ---- OCR ----------------------------------------------------------------------------------------
def bill_image(lines):
    img = Image.new("RGB", (1400, 700), "white")
    d, font = ImageDraw.Draw(img), ImageFont.load_default(size=48)
    for i, line in enumerate(lines):
        d.text((50, 60 + i * 110), line, fill="black", font=font)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def test_ocr_unavailable_falls_back_gracefully(guest, monkeypatch):
    monkeypatch.setattr(ocr_extractor, "ocr_available", lambda: False)
    r = guest.post("/api/ocr", data={"image": (io.BytesIO(bill_image(["x"])), "bill.png")}, content_type="multipart/form-data")
    assert r.status_code == 503 and r.get_json()["fallback"] is True


@pytest.mark.skipif(not ocr_extractor.ocr_available(), reason="Tesseract is not installed")
def test_ocr_reads_a_bill_photo(guest):
    png = bill_image(["BILL OF SUPPLY FOR THE MONTH OF September 2026", "Units Consumed : 33", "Net Payable Rs. 360.00"])
    r = guest.post("/api/ocr", data={"image": (io.BytesIO(png), "bill.png")}, content_type="multipart/form-data")
    j = r.get_json()
    assert r.status_code == 200 and j["found"] is True
    assert (j["m"], j["u"], j["a"]) == ("2026-09", 33.0, 360.0)


@pytest.mark.skipif(not ocr_extractor.ocr_available(), reason="Tesseract is not installed")
def test_ocr_rejects_non_images(guest):
    r = guest.post("/api/ocr", data={"image": (io.BytesIO(b"not an image"), "bill.png")}, content_type="multipart/form-data")
    assert r.status_code == 400 and "readable image" in r.get_json()["error"]
