from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter

from ..storage.sqlite_store import SQLiteStore


router = APIRouter(prefix="/runs", tags=["runs"]) 
store = SQLiteStore(Path("artifacts/store"))


@router.get("")
def list_runs() -> list[dict[str, Any]]:
    return [r.__dict__ for r in store.list_runs()]


@router.post("")
def create_run(meta: dict[str, Any]) -> dict[str, Any]:
    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    rec = {
        "id": run_id,
        "status": "created",
        "created_at": datetime.utcnow().isoformat() + "Z",
        **meta,
    }
    store.create_run(rec)
    return rec


@router.get("/{run_id}")
def get_run(run_id: str) -> dict[str, Any] | None:
    r = store.get_run(run_id)
    return r.__dict__ if r else None

