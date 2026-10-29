# Smart Mandi — local pilot starter

A React + Vite frontend and FastAPI backend for browsing mandi prices in Annamayya, Anantapuram and Sri Sathya Sai districts.

## Important data note

Until you receive and configure a `data.gov.in` API key, the application uses **synthetic sample history** generated for local testing. It is clearly labelled as demo data and is **not official, current, or suitable for making selling decisions**. Do not describe these sample prices as real market prices. No API key is needed to run the local demo.

## Windows quick start (no Docker required)

Prerequisites: Python 3.11+ (Python 3.12 is a good choice), Node.js LTS, and npm.

### 1. Backend

Open PowerShell in the extracted `smart-mandi` folder and run:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
# The supplied backend/.env is preconfigured for SQLite and demo data.
uvicorn app.main:app --reload
```

Keep this terminal open. On startup, the app creates local SQLite tables and seeds 30 days of clearly labelled synthetic sample history. API docs: <http://127.0.0.1:8000/docs>; health: <http://127.0.0.1:8000/health>.

### 2. Frontend

Open a second PowerShell window in the project folder:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (normally <http://localhost:5173>).

### 3. Basic checks

In the API docs, test `GET /api/v1/districts`, `/api/v1/crops`, `/api/v1/markets`, `/api/v1/prices?crop_id=tomato`, and `/api/v1/price-history?crop_id=tomato&market_id=madanapalle`. The price-history endpoint should return multiple dated demo observations. `/api/v1/price-analytics?crop_id=tomato&market_id=madanapalle` should explicitly identify its data as demo.

The demo truck and buyer records are unverified and should not be treated as available verified providers. Booking and offer endpoints require authentication. Real Supabase authentication must be configured before testing signed-in workflows.

## When the data.gov.in API key arrives

1. Stop the backend.
2. Open `backend/.env` in a text editor.
3. Set `DATA_GOV_IN_API_KEY=your_actual_key` (do not include quotes unless needed).
4. Save the file and restart the backend.
5. Run the importer as described below and inspect the returned records before using them.

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.sync_market_prices
```

Check the importer command and API resource fields against the current data.gov.in resource documentation before relying on its output; government data availability and field mappings may change. Never commit the real API key. `backend/.env` is git-ignored; keep the key in a local environment variable or deployment secret when deploying.

## Tests

From `backend` with the virtual environment active:

```powershell
python -m pytest -q
python -m compileall -q app tests
```

## GitHub publishing (after local testing)

The `.env` files are excluded by `.gitignore`. Confirm that no real API keys or passwords are in tracked files before pushing. Use GitHub Actions CI in `.github/workflows/ci.yml` to validate the backend and build the frontend.

## Current pilot limitations

- Local development uses SQLite. Use managed PostgreSQL and migrations for deployment.
- Supabase auth values are blank until you configure your own Supabase project.
- Admin verification endpoints only record an admin's verification decision; document review/upload workflow is not implemented.
- Freight comparison uses matching verified truck base quotes where available; it does not calculate road distance yet.
- Price forecasting is an illustrative baseline only and is not advice. Validate with enough real historical data and chronological backtesting before operational use.
