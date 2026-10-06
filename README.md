# Smart Energy Advisor — Web Pages (Frontend Preview)

Three standalone HTML pages, each fully self-contained (open directly in any browser, no server needed):

1. **1_welcome.html** — Landing/welcome page with the lightbulb mascot (cursor-tracking eyes) and animated flowing background
2. **2_add_bill.html** — Data input page: choose CSV upload, manual entry, or bill photo (OCR)
3. **3_dashboard.html** — Main dashboard: uploaded bill summary, forecast, consumption trend chart, appliance breakdown, what-if simulator, and recommendations

## How to view
Just double-click any `.html` file to open it in your browser. No installation needed — everything (fonts load from Google Fonts online, charts from a CDN) runs from a single file.

## The chatbot — "Watt"
All three pages include a floating assistant in the bottom-right corner, named **Watt** (a little lightbulb character with cursor-tracking eyes, same mascot as the welcome page). Click it to open a chat panel with page-specific guidance — it's a simple rule-based FAQ assistant (pre-written questions/answers per page), not a live AI, so it works fully offline with no API key.

## Important note
These are **visual design mockups** — all data (₹412 forecast, 33 units, appliance percentages, etc.) is hardcoded sample data for demonstration. They are NOT connected to the actual Python/Streamlit backend (the `smart_energy_advisor/` project with real forecasting, OCR, and anomaly detection logic) delivered earlier.

Use these pages to:
- Show your guide/evaluators what the finished product could look like
- Get design feedback before wiring up real functionality

If you want these pages actually wired to the working Python backend (real forecasts, real OCR results, live data instead of hardcoded numbers), let me know — that's a separate integration step.

## Customizing
- Colors/theme: edit the CSS variables at the top of each file's `<style>` block (`--accent`, `--bg`, etc.)
- Watt's answers: each page has a `window.WATT_CONFIG` script near the bottom with `greeting` and `options` (question/answer pairs) — edit the text directly
- Background motion: the `.blob` elements and their `@keyframes` control the flowing background animation
