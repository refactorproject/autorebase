from __future__ import annotations

from fastapi import FastAPI

from .routers import runs, uploads

app = FastAPI(title="auto-rebase API")

app.include_router(runs.router)
app.include_router(uploads.router)

