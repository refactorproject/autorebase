from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, UploadFile


router = APIRouter(prefix="/uploads", tags=["uploads"]) 


@router.post("")
async def upload(file: UploadFile) -> dict[str, Any]:
    root = Path("artifacts/uploads")
    root.mkdir(parents=True, exist_ok=True)
    out = root / file.filename
    out.write_bytes(await file.read())
    return {"path": str(out)}

