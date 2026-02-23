# CT Public Records Platform

Full-stack web application for scraping, storing, and browsing Connecticut public records (assessor/property tax, land records, business filings, CT Open Data).

## Quick Start

### Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

Open http://localhost — the SPA loads immediately, backend API at http://localhost/api/v1.

### Local Development

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev    # Vite dev server on :5173, proxies /api → :8000
```

## API Docs

Swagger UI: http://localhost:8000/api/docs
ReDoc: http://localhost:8000/api/redoc

## Adding a Data Source

1. Go to **Sources** page → **Add Source**
2. Fill in name, type, base URL, and optional JSON config
3. Set a cron schedule (e.g. `0 2 * * *`) or click **Run Now**
4. Monitor progress in **Jobs** page

### Config JSON examples

**CT Open Data (CKAN):**
```json
{"dataset_id": "abc123-...", "dataset_name": "My Dataset", "tags": ["ct", "open"]}
```

**Vision Assessor:**
```json
{"town": "Greenwich", "assessment_year": 2024, "use_playwright": false}
```

**Land Records:**
```json
{"town": "Hartford", "days_back": 30}
```

**CT SoS Business:**
```json
{}
```

## Architecture

```
connecticut/
├── backend/          FastAPI + SQLAlchemy + APScheduler
│   ├── app/
│   │   ├── models/   SQLAlchemy ORM (6 tables)
│   │   ├── schemas/  Pydantic request/response models
│   │   ├── api/      REST routers (/api/v1/...)
│   │   ├── scrapers/ BaseScraper + 4 concrete scrapers
│   │   ├── quality/  Validator + Deduplicator
│   │   ├── exports/  CSV + Excel streaming
│   │   └── scheduler/ APScheduler cron dispatch
│   └── alembic/      DB migrations
├── frontend/         React 18 + Vite + TypeScript + Tailwind
│   └── src/
│       ├── pages/    Dashboard, Sources, Jobs, Properties, LandRecords, Businesses, OpenData
│       ├── hooks/    TanStack Query wrappers
│       ├── components/
│       └── lib/api.ts Typed API client
└── nginx/            Reverse proxy config
```

## Swapping to PostgreSQL

In `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/ct_records
```

Add a `db` service to `docker-compose.yml` and run `alembic upgrade head` inside the backend container.
