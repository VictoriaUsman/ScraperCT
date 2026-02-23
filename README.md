# CT Public Records Platform

Full-stack web application for scraping, storing, and browsing Connecticut public records — assessor/property tax, land records, business filings, court records, tax collector data, municipal meeting documents, and CT Open Data.

Covers 10 source types across the major platforms used by CT's 169 towns.

## Quick Start

### Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

Open http://localhost — the SPA loads immediately, backend API at http://localhost/api/v1.

### After adding new scrapers — run the migration

```bash
docker compose up --build -d backend
docker compose exec backend alembic upgrade head
docker compose up -d frontend
```

### Local Development

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev    # Vite dev server on :5173, proxies /api → :8000
```

## API Docs

Swagger UI: http://localhost/api/docs
ReDoc: http://localhost/api/redoc

## Data Sources

| Source Type | Platform | Records Table | Towns/Scope |
|------------|----------|--------------|-------------|
| `ckan_api` | CT Open Data Portal (CKAN) | `open_data_records` | Statewide datasets |
| `vision_gov` | Vision Government Solutions assessor | `property_records` | ~80 CT towns |
| `land_records` | Laredo/Granicus town clerk portals | `land_records` | Major CT towns |
| `ct_sos` | CT Secretary of State business search | `business_records` | Statewide |
| `iqs_land_records` | IQS/Index Systems land records | `land_records` | Milford, East Haven, Guilford, Madison, West Haven, etc. |
| `patriot_assessor` | Patriot Properties assessor portals | `property_records` | New Haven, Bridgeport, Waterbury, Norwalk, etc. |
| `arcgis_parcels` | ArcGIS REST Feature Services (GIS parcel data) | `property_records` | CT CTECO statewide + town GIS portals |
| `ct_courts` | CT Judicial Branch civil + small claims | `court_records` | Statewide |
| `ct_tax` | TaxSys / Invoice Cloud tax collector portals | `tax_records` | Hartford, and other TaxSys/Invoice Cloud towns |
| `municipal_data` | Granicus/Legistar meeting documents | `municipal_records` | Hartford, New Haven, Bridgeport, Stamford, etc. |

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

**Land Records (Laredo/Granicus):**
```json
{"town": "Hartford", "days_back": 30}
```

**IQS Land Records:**
```json
{"town": "Milford", "days_back": 30}
```

**Patriot Properties Assessor:**
```json
{"town": "New Haven", "assessment_year": 2024, "use_playwright": false}
```

**ArcGIS Parcels:**
```json
{
  "town": "Glastonbury",
  "layer_id": 0,
  "field_map": {"PARCEL_ID": "parcel_id", "OWNERNAME": "owner_name", "TOTAL_VAL": "assessed_value"}
}
```

**CT Courts:**
```json
{"case_type": "civil", "days_back": 30, "court_location": "Hartford", "use_playwright": false}
```

**CT Tax Collector (TaxSys):**
```json
{"town": "Hartford", "platform": "taxsys", "levy_year": 2025, "status_filter": "all"}
```

**CT Tax Collector (Invoice Cloud):**
```json
{"town": "Norwalk", "platform": "invoice_cloud", "levy_year": 2025, "status_filter": "delinquent"}
```

**Municipal Documents (Legistar):**
```json
{"town": "hartford", "days_back": 90, "body_filter": "City Council", "document_types": ["agenda", "minutes"]}
```

**CT SoS Business:**
```json
{}
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/v1/sources` | List configured sources |
| `POST /api/v1/sources` | Add a new source |
| `POST /api/v1/sources/{id}/trigger` | Run a scrape job immediately |
| `GET /api/v1/jobs` | List scrape jobs |
| `GET /api/v1/properties` | Property/assessor records |
| `GET /api/v1/land-records` | Land/deed records |
| `GET /api/v1/businesses` | Business filings |
| `GET /api/v1/open-data` | CT Open Data records |
| `GET /api/v1/court-records` | Court case records |
| `GET /api/v1/tax-records` | Tax collector records |
| `GET /api/v1/municipal-records` | Meeting documents |
| `GET /api/v1/exports/{type}/csv` | Stream CSV export |
| `GET /api/v1/exports/{type}/excel` | Download Excel export |
| `GET /api/v1/dashboard` | Summary stats |

Each record collection endpoint also has `/stats` and `/{id}` sub-routes.

## Architecture

```
connecticut/
├── backend/                  FastAPI + SQLAlchemy + APScheduler
│   ├── app/
│   │   ├── models/           SQLAlchemy ORM (9 tables)
│   │   │   ├── source.py         Source + SourceType enum (10 types)
│   │   │   ├── scrape_job.py     ScrapeJob
│   │   │   ├── property_record.py  Assessor data (+ lat/lon for ArcGIS)
│   │   │   ├── land_record.py    Deed/land records
│   │   │   ├── business_record.py  SoS business filings
│   │   │   ├── open_data_record.py CT Open Data rows
│   │   │   ├── court_record.py   Civil + small claims cases
│   │   │   ├── tax_record.py     Tax collector bills
│   │   │   └── municipal_record.py Meeting documents
│   │   ├── schemas/          Pydantic request/response models
│   │   ├── api/              REST routers (/api/v1/...)
│   │   ├── scrapers/         BaseScraper + 10 concrete scrapers
│   │   │   ├── vision_assessor.py
│   │   │   ├── land_records.py
│   │   │   ├── sos_business.py
│   │   │   ├── ct_open_data.py
│   │   │   ├── iqs_land_records.py
│   │   │   ├── patriot_assessor.py
│   │   │   ├── arcgis_parcels.py
│   │   │   ├── ct_courts.py
│   │   │   ├── ct_tax.py
│   │   │   └── municipal_data.py
│   │   ├── quality/          Validator + Deduplicator (all 10 source types)
│   │   ├── exports/          CSV + Excel streaming
│   │   └── scheduler/        APScheduler cron dispatch
│   └── alembic/              DB migrations (0001 initial, 0002 new tables)
├── frontend/                 React 18 + Vite + TypeScript + Tailwind
│   └── src/
│       ├── pages/
│       ├── hooks/            TanStack Query wrappers
│       ├── components/
│       └── lib/api.ts        Typed API client
└── nginx/                    Reverse proxy config
```

## Useful Commands

| Command | What it does |
|---------|-------------|
| `docker compose up --build` | Build and start everything |
| `docker compose up --build -d` | Start in background |
| `docker compose logs -f backend` | Tail backend logs |
| `docker compose exec backend alembic upgrade head` | Apply DB migrations |
| `docker compose exec backend alembic current` | Check current migration |
| `docker compose down` | Stop everything |
| `docker compose down -v` | Stop and wipe database volume |

## Swapping to PostgreSQL

In `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/ct_records
```

Add a `db` service to `docker-compose.yml` and run `alembic upgrade head` inside the backend container.
