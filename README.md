# Smart Energy Advisor — all-Python version (Flask)

Every source file in this folder is **Python**. Same website as before (login → add bill → dashboard, the Watt chatbot, the guided tour, the lightbulb
mascot and all animations). The difference: **everything that "thinks" now runs in Python on the server.**

| What | Where it lives |
|---|---|
| Accounts (signup / login / guest), hashed passwords, SQLite | `app.py`, `db.py` |
| CSV reading + cleaning (pandas) | `modules/preprocessing.py` |
| Next-month forecast (numpy regression, seasonal after 12 months) + what-if simulator | `modules/forecasting.py` |
| Unusual-month detection (vs. the same month last year) | `modules/anomaly_detection.py` |
| Appliance breakdown, saving tips, dashboard numbers | `modules/appliance_breakdown.py`, `recommendations.py`, `dashboard.py` |
| Bill-photo OCR (Tesseract, English + Marathi) | `modules/ocr_extractor.py` |
| Watt's answers (use your real data) | `modules/chatbot.py` |
| The page itself (HTML, CSS and the browser script, kept as Python strings and served by Flask) | `ui/page.py`, `ui/styles.py`, `ui/script.py` |

The browser only draws the page and calls the JSON API (`/api/...`). A browser can only show a page
written in HTML/CSS/JavaScript, so those three are stored as text inside the `ui/` modules and sent to
the browser by `app.py` (`/`, `/assets/app.css`, `/assets/app.js`). Only `requirements.txt`, `Procfile`,
`.gitignore` and this README are not `.py`, because pip, the host and Git need them in that form.

## Run it (Windows)

```bat
cd smart_energy_advisor_flask
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open **http://127.0.0.1:5000**. (First run creates `instance/app.db` and `instance/secret.key`.)

### OCR (bill photos)
OCR needs the **Tesseract program** installed (not just the Python package). Install it, then if Python
can't find it, tell the app where it is *before* starting:
```bat
set TESSERACT_CMD=D:\smart_energy_advisor\tesseract.exe
python app.py
```
For **Marathi bills** also copy `mar.traineddata` into Tesseract's `tessdata` folder — it is picked up
automatically (English + Marathi). If Tesseract is missing the app still works: the photo box says
"automatic reading isn't set up" and you type the three values yourself.

## Run the tests
```bat
python -m pytest -q
```
39 tests cover accounts, CSV upload, manual entry, forecast, anomalies, simulator, chatbot, OCR and security.

## Deploying
**GitHub Pages cannot run Python** — it only hosts static files. Use a Python host, for example
**Render**, **Railway** or **PythonAnywhere**:
* start command: `gunicorn app:app` (a `Procfile` is included)
* environment variables: `SECRET_KEY` = a long random string, `SEA_HTTPS=1` (secure cookies on https)
* SQLite lives in `instance/`. On hosts with a temporary disk (Render free tier) accounts and bills are
  lost on every restart — attach a persistent disk, or move `db.py` to PostgreSQL.

## Good to know
* Passwords are stored hashed (werkzeug). Login is limited to 8 wrong tries per 10 minutes.
* All POST requests need a CSRF token; the page sends it automatically.
* Guest data is deleted after 3 days. A guest who then signs up keeps what they added.
* Uploads: CSV up to 5 MB, photos up to 6 MB.
* The forecast needs 3+ months; unusual-month detection needs 13+ months (it compares each month with the
  same month a year earlier, so the normal summer rise is not reported as a spike).
* The login rate limiter is per process; with several gunicorn workers use a shared store (e.g. Redis).
