Server API (FastAPI)

- Run: `uvicorn server.api.main:app --reload`
- Endpoints:
  - POST /runs
  - GET /runs
  - GET /runs/{id}
  - POST /uploads

Storage providers:
- sqlite_store.py: JSON-file backed demo
- convex_store.py: stubbed unless CONVEX_URL is set

