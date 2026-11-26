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
cd smart_energy_advisor_python_csv
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

## Organization energy dashboard

The original household dashboard is preserved. The organization dashboard is available at:

- `http://127.0.0.1:5000/enterprise`

It supports schools, colleges, hospitals, hotels, restaurants, offices, factories and other organizations. The organization dashboard now uses the same shared green/yellow design tokens, fonts, card styling and responsive layout as the household application. It accepts department-level monthly meter records and provides:

- Department-wise consumption and estimated cost summaries
- Deterministic K-Means grouping of departments by average monthly units (NumPy implementation)
- Simple linear-trend next-month estimates when at least 3 months are available
- Month-to-month spike/drop flags using a 35% and 5-unit threshold
- Recommendations tied to highest usage, after-hours usage, anomalies and forecasts

### Input data format (CSV only)

Use the **Automatic CSV detection** section on the Enterprise page. The upload is the only organization-data entry workflow in the interface; there is no JSON editor or JSON upload section.

Required CSV columns:
- `month` in `YYYY-MM` format
- `units` (numeric energy consumption)
- At least one of `department` or `building`

Optional columns:
- `amount`
- `after_hours_units` (only when supported by meter data or a defensible measurement method)
- `organization_type` or industry-specific terms in column names/values to help automatic detection

At least 3 valid records are required. Built-in demonstration data, if used for testing, is synthetic and must not be presented as real field research.

### Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000/enterprise`. The enterprise API is `POST /api/enterprise/analyze` and uses the same session CSRF protection as the rest of the application.

### Important limitations

This is an academic prototype, not yet a production multi-tenant enterprise platform. It does not yet include organization accounts/roles, live smart-meter integration, time-of-use tariff modeling, or a production database migration. K-Means uses only average monthly department units, so its labels are relative to the uploaded dataset. Forecasts are indicative, not guaranteed. Validate all recommendations with facilities staff before acting on them.

## Automatic CSV dataset detection

The CSV upload flow now calls `/api/upload/auto`. It examines column headers and
sample values, calculates a heuristic confidence score, validates the records,
and routes the file:

- Household: existing bill-history parser and household dashboard.
- School, college, hospital, hotel, restaurant, factory, office, or other organization: organization CSV validation, enterprise analysis, and the shared-theme organization dashboard.
- Unknown / low-evidence files: the user is asked to confirm the organization type rather than silently assigning an industry.

The confidence score is an explainable heuristic evidence score, **not** a
trained machine-learning probability. When evidence is weak, the response sets
`needs_confirmation` and the API asks for a clearer CSV structure. Organization
CSV files need a month column (`YYYY-MM`), a numeric units column, and at least
one of department or building. Optional fields include amount and
`after_hours_units`. Organization analysis needs at least three valid rows.

API response includes `dataset_type`, `dataset_label`, `confidence`, `evidence`,
`validation`, `route`, and the analysis result for organization datasets.


## CSV data profiling (Phase 2)

The automatic CSV upload now creates a data-quality profile before analysis. It reports row/column counts, blank cells by column, duplicate rows, invalid numeric values, negative values, unrecognized dates, and possible IQR-based outliers. Possible outliers are review flags, not automatic errors, and zero consumption is allowed. The quality score is a transparent rule-based indicator (0–100), not an ML probability. Critical numeric/date issues stop analysis until corrected.

If a dataset has a generic organization-level structure but no clear industry-specific evidence, it is classified as **Other organization** (or left unknown when there is no organizational structure) with a request for user confirmation. Hotel and restaurant are available as explicit confirmation choices. The application does not infer industry-specific columns that are not present in the file. After-hours recommendations are omitted unless an `after_hours_units` column is supplied.


## Organization CSV dashboard and Watt guide

For organization CSV files (school, college, hospital, hotel, restaurant, office or factory),
the upload step now keeps the existing **See my dashboard** button. After a successful upload,
use that same button to open the organization dashboard. No extra dashboard-opening button is
added to the upload screen.

The organization dashboard uses the shared Smart Energy Advisor stylesheet and includes
subtle card/chart entrance animations. Watt remains visible on the dashboard and starts a
guided tour of the summary cards, department chart, monthly trend, alerts, recommendations,
and data notes. Click Watt to replay the tour.

### Dashboard guide and Watt assistant

The organization CSV dashboard includes a highlighted next-month consumption prediction when every displayed department has at least three months of readings. The prediction sums the department-level linear forecasts; the estimated cost uses the latest effective average tariff and is indicative only.

Watt automatically guides users through the organization dashboard once after the analysis is displayed. During the guide, the selected card or chart is highlighted while the rest of the page is blurred and dimmed. After the guide is completed or skipped, clicking the floating Watt character opens the dashboard Q&A assistant. It can answer questions about the prediction, department rankings, trend chart, alerts, after-hours readings and recommendations using the currently displayed CSV analysis. Use **Replay tour** inside the chat to start the guide again.



## Multiple bill entry (updated)

- Manual entry supports up to **24 monthly bills in one save**. Use “Add another month” to add rows.
- Bill Photo (OCR) supports up to **12 photos per selection**, with each image limited to **8 MB**.
- OCR reads each photo separately. Review/correct the detected billing month, units and amount before saving.
- Every bill must have a month, units and bill amount. Duplicate months in one batch are rejected; adding a month already stored updates that month.
- A forecast still requires at least 3 distinct billing months with valid data. More months generally provide a more useful trend, but OCR values should always be checked against the original bill.
