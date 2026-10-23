"""Smart Energy Advisor — Flask app (every file of the project is Python).

The page itself (HTML, CSS and the browser script) is stored in the ui/ modules and served from here.
Python does the real work: accounts (hashed passwords + SQLite), CSV/photo reading, forecasting,
anomaly detection, the what-if simulator, OCR and the Watt chatbot. The browser only shows the UI.

Run:   python app.py        (then open http://127.0.0.1:5000)
"""
import hmac
import os
import re
import secrets
import time
from datetime import timedelta

from flask import Flask, Response, g, jsonify, request, session
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

import db
import ui
from modules import chatbot, ocr_extractor
from modules.common import APPLIANCE_NAMES, month_label
from modules.dashboard import build_dashboard, simulator_shares
from modules.forecasting import forecast_next_month, what_if
from modules.preprocessing import parse_csv_bytes, rows_to_csv, validate_entry
from modules.sample_data import sample_rows

EMAIL_RE = re.compile(r"^\S+@\S+\.\S+$")
MAX_UPLOAD = 6 * 1024 * 1024          # hard limit for any request body
MAX_CSV = 5 * 1024 * 1024
GUEST_TTL = 3 * 24 * 3600             # guest data is deleted after 3 days
ENTRY_SOURCES = {"Manual entry", "Bill photo"}
CSP = ("default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self'; "
       "frame-ancestors 'none'; base-uri 'self'; form-action 'self'")


class ApiError(Exception):
    def __init__(self, status, message, **extra):
        super().__init__(message)
        self.status, self.message, self.extra = status, message, extra


def _secret_key(instance_path):
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    path = os.path.join(instance_path, "secret.key")
    if not os.path.exists(path):
        with open(path, "w") as fh:
            fh.write(secrets.token_hex(32))
        os.chmod(path, 0o600)
    with open(path) as fh:
        return fh.read().strip()


def create_app(test_config=None):
    app = Flask(__name__, static_folder=None)      # no static files: the UI lives in the ui/ Python modules
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.update(
        DATABASE=os.path.join(app.instance_path, "app.db"),
        SECRET_KEY=_secret_key(app.instance_path),
        MAX_CONTENT_LENGTH=MAX_UPLOAD,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SEA_HTTPS") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(days=14),
    )
    if test_config:
        app.config.update(test_config)
    db.init_db(app.config["DATABASE"])
    attempts: dict[str, list[float]] = {}

    # ---- plumbing --------------------------------------------------------------------------------
    def conn():
        if "db" not in g:
            g.db = db.connect(app.config["DATABASE"])
        return g.db

    @app.teardown_appcontext
    def _close(_exc):
        c = g.pop("db", None)
        if c is not None:
            c.close()

    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(24)
        return session["csrf"]

    def owner():
        if "uid" in session:
            return f"u:{session['uid']}"
        if "guest" in session:
            return f"g:{session['guest']}"
        return None

    def need_owner():
        o = owner()
        if not o:
            raise ApiError(401, "Please log in or continue as a guest first.")
        return o

    def me():
        o, user = owner(), None
        if "uid" in session:
            row = db.get_user(conn(), session["uid"])
            if row is None:                       # account vanished: drop the stale session
                session.clear()
                o = None
            else:
                user = {"email": row["email"], "name": row["name"]}
        return {"user": user, "guest": bool(o and o.startswith("g:")),
                "has_data": bool(o and db.dataset(conn(), o)), "csrf": csrf_token()}

    def rows_for(o):
        info = db.dataset(conn(), o)
        if info is None:
            raise ApiError(409, "Add your bill data first.")
        return (sample_rows() if info["sample"] else db.load_rows(conn(), o)), info

    def body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ApiError(400, "Invalid request.")
        return data

    def throttled(key, limit=8, window=600):
        now = time.time()
        recent = [t for t in attempts.get(key, []) if now - t < window]
        attempts[key] = recent
        return len(recent) >= limit

    def start_session(**values):
        session.clear()
        session.permanent = True
        session.update(values)
        csrf_token()

    @app.before_request
    def _csrf_guard():
        if request.method == "POST" and request.path.startswith("/api/"):
            sent, expected = request.headers.get("X-CSRF-Token", ""), session.get("csrf", "")
            if not expected or not hmac.compare_digest(sent, expected):
                raise ApiError(403, "Your session expired — please refresh the page and try again.")

    @app.after_request
    def _headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        resp.headers.setdefault("Content-Security-Policy", CSP)
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.errorhandler(ApiError)
    def _api_error(e):
        return jsonify(error=e.message, **e.extra), e.status

    @app.errorhandler(HTTPException)
    def _http_error(e):
        if request.path.startswith("/api/"):
            msg = "That file is too large (max 5 MB)." if e.code == 413 else e.description
            return jsonify(error=msg), e.code
        return e

    # ---- pages -----------------------------------------------------------------------------------
    @app.get("/")
    def index():
        return Response(ui.render_index(), mimetype="text/html")

    def asset(text, mimetype):
        resp = Response(text, mimetype=mimetype)
        resp.headers["Cache-Control"] = "public, max-age=3600"
        resp.add_etag()
        return resp.make_conditional(request)

    @app.get("/assets/app.css")
    def asset_css():
        return asset(ui.CSS, "text/css")

    @app.get("/assets/app.js")
    def asset_js():
        return asset(ui.JS, "text/javascript")

    @app.get("/favicon.ico")
    def favicon():
        return Response(status=204)

    # ---- accounts --------------------------------------------------------------------------------
    def credentials():
        data = body()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        if not EMAIL_RE.match(email) or len(email) > 254:
            raise ApiError(400, "Please enter a valid email address.")
        if len(password) < 6:
            raise ApiError(400, "Password must be at least 6 characters.")
        if len(password) > 200:
            raise ApiError(400, "That password is too long.")
        return email, password, str(data.get("name", "")).strip()[:80]

    def log_in(user_id):
        guest = session.get("guest")
        start_session(uid=user_id)
        if guest:                                   # keep what they added as a guest
            db.move_dataset(conn(), f"g:{guest}", f"u:{user_id}")

    @app.get("/api/me")
    def api_me():
        return jsonify(me())

    @app.post("/api/signup")
    def api_signup():
        email, password, name = credentials()
        if db.find_user(conn(), email):
            raise ApiError(409, "An account with this email already exists. Try logging in.")
        try:
            uid = db.create_user(conn(), email, name, generate_password_hash(password))
        except Exception:
            raise ApiError(409, "An account with this email already exists. Try logging in.")
        log_in(uid)
        return jsonify(me())

    @app.post("/api/login")
    def api_login():
        email, password, _ = credentials()
        key = f"{request.remote_addr}|{email}"
        if throttled(key):
            raise ApiError(429, "Too many attempts. Please wait a few minutes and try again.")
        user = db.find_user(conn(), email)
        if not user or not check_password_hash(user["pw_hash"], password):
            attempts.setdefault(key, []).append(time.time())
            raise ApiError(401, "Wrong email or password.")
        log_in(user["id"])
        return jsonify(me())

    @app.post("/api/guest")
    def api_guest():
        db.purge_guests(conn(), GUEST_TTL)
        start_session(guest=secrets.token_urlsafe(16))
        return jsonify(me())

    @app.post("/api/logout")
    def api_logout():
        session.clear()
        return jsonify(me())

    # ---- data in ---------------------------------------------------------------------------------
    @app.post("/api/upload/csv")
    def api_upload_csv():
        o = need_owner()
        f = request.files.get("file")
        if f is None or not f.filename:
            raise ApiError(400, "Choose a CSV file first.")
        if not f.filename.lower().endswith((".csv", ".txt")):
            raise ApiError(400, "Please upload a .csv file.")
        data = f.read(MAX_CSV + 1)
        if len(data) > MAX_CSV:
            raise ApiError(413, "That file is too large (max 5 MB).")
        try:
            rows, skipped = parse_csv_bytes(data)
        except ValueError as exc:
            raise ApiError(400, str(exc))
        source = re.sub(r"[\x00-\x1f]", "", os.path.basename(f.filename))[:80] or "Uploaded CSV"
        db.replace_rows(conn(), o, rows, source)
        return jsonify(ok=True, months=len(rows), skipped=skipped, source=source)

    @app.post("/api/bills")
    def api_bills():
        o = need_owner()
        data = body()
        source = data.get("source") if data.get("source") in ENTRY_SOURCES else "Manual entry"
        try:
            row = validate_entry(data.get("month"), data.get("units"), data.get("amount"), data.get("appliances"))
        except ValueError as exc:
            raise ApiError(400, str(exc))
        months = db.upsert_row(conn(), o, row, source)
        return jsonify(ok=True, months=months, month_label=month_label(row["m"]))

    @app.post("/api/sample")
    def api_sample():
        db.replace_rows(conn(), need_owner(), [], "Sample data", sample=True)
        return jsonify(ok=True)

    @app.post("/api/ocr")
    def api_ocr():
        need_owner()
        f = request.files.get("image")
        if f is None or not f.filename:
            raise ApiError(400, "Choose a photo first.")
        try:
            result = ocr_extractor.read_bill(f.read())
        except ocr_extractor.OCRUnavailable as exc:
            raise ApiError(503, str(exc), fallback=True)
        except ValueError as exc:
            raise ApiError(400, str(exc))
        return jsonify(ok=True, found=any(result[k] is not None for k in ("m", "u", "a")), **result)

    @app.get("/api/template.csv")
    def api_template():
        csv_text = rows_to_csv(sample_rows()[-12:])
        return Response(csv_text, mimetype="text/csv",
                        headers={"Content-Disposition": 'attachment; filename="smart_energy_template.csv"'})

    # ---- insights --------------------------------------------------------------------------------
    @app.get("/api/dashboard")
    def api_dashboard():
        rows, info = rows_for(need_owner())
        return jsonify(build_dashboard(rows, info["source"], info["sample"]))

    @app.post("/api/simulate")
    def api_simulate():
        rows, _ = rows_for(need_owner())
        data = body()
        appliance = data.get("appliance")
        try:
            pct = float(data.get("pct"))
        except (TypeError, ValueError):
            raise ApiError(400, "Invalid percentage.")
        if appliance not in APPLIANCE_NAMES or not -100 <= pct <= 100:
            raise ApiError(400, "Invalid simulator input.")
        forecast, shares = forecast_next_month(rows), simulator_shares(rows)
        if not forecast or not shares or appliance not in shares:
            raise ApiError(409, "The simulator needs 3+ months of bills and an appliance split.")
        return jsonify(what_if(forecast, shares[appliance], pct))

    @app.post("/api/chat")
    def api_chat():
        data = body()
        message = str(data.get("message", "")).strip()[:500]
        if not message:
            raise ApiError(400, "Type a question first.")
        o = owner()
        info = db.dataset(conn(), o) if o else None
        rows = (sample_rows() if info and info["sample"] else db.load_rows(conn(), o)) if info else None
        return jsonify(chatbot.reply(message, str(data.get("section", "login")), bool(o), rows))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("FLASK_DEBUG") == "1")
