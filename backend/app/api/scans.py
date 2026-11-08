# app/api/scans.py
"""
Scans API.

POST /api/scans          upload a .json/.yaml config, run a scan, store it
GET  /api/scans          list recent scans (summary only)
GET  /api/scans/{id}     one scan with all findings
"""

from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.ai.analyzer import summarize_findings
from app.core.config import MAX_UPLOAD_BYTES
from app.services.scan_repository import get_repository
from app.services.scan_service import run_scan
from app.utils.parser import parse_config

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("", status_code=201)
def create_scan(file: UploadFile = File(...)):
    # Read one byte past the limit so oversized files are detected
    # without loading an unlimited amount into memory.
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    filename = (file.filename or "upload")[:255]

    config = parse_config(content, filename)   # ValueError -> 400
    result = run_scan(config)                  # ValueError -> 400
    ai_summary = summarize_findings(result)    # never raises

    data = result.model_dump(mode="json")
    row = {
        "filename": filename,
        "resources_scanned": data["resources_scanned"],
        "risk_score": data["risk"]["risk_score"],
        "risk_level": data["risk"]["risk_level"],
        "findings_count": data["risk"]["findings_count"],
        "severity_counts": data["risk"]["severity_counts"],
        "risk": data["risk"],
        "findings": data["findings"],
        "ai_summary": ai_summary,
    }
    return get_repository().save(row)


@router.get("")
def list_scans(limit: int = Query(50, ge=1, le=200)):
    return get_repository().list(limit)


@router.get("/{scan_id}")
def get_scan(scan_id: UUID):
    scan = get_repository().get(str(scan_id))
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan
