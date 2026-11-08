# app/api/scans.py
"""
Scans API.

POST /api/scans          upload a .json/.yaml config, run a scan, store it
GET  /api/scans          list recent scans (summary only)
GET  /api/scans/{id}     one scan with all findings
DELETE /api/scans/{id}   delete one scan
POST /api/scans/{id}/summary   (re)generate the AI summary for a saved scan

Scan responses include "ai_error": why the AI summary is missing, or null.
It is returned to the UI but not stored.
"""

from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Query, Response, UploadFile

from app.ai.analyzer import generate_summary
from app.schemas import ScanResult
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
    ai_summary, ai_error = generate_summary(result)   # never raises

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
    saved = get_repository().save(row)
    return {**saved, "ai_error": ai_error}


@router.get("")
def list_scans(limit: int = Query(50, ge=1, le=200)):
    return get_repository().list(limit)


@router.get("/{scan_id}")
def get_scan(scan_id: UUID):
    scan = get_repository().get(str(scan_id))
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return {**scan, "ai_error": None}


@router.delete("/{scan_id}", status_code=204)
def delete_scan(scan_id: UUID):
    if not get_repository().delete(str(scan_id)):
        raise HTTPException(status_code=404, detail="Scan not found.")
    return Response(status_code=204)


@router.post("/{scan_id}/summary")
def regenerate_summary(scan_id: UUID):
    """Generate the AI summary again from the stored findings."""
    repo = get_repository()
    scan = repo.get(str(scan_id))
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")

    result = ScanResult.model_validate({
        "resources_scanned": scan["resources_scanned"],
        "findings": scan.get("findings") or [],
        "risk": scan["risk"],
    })
    ai_summary, ai_error = generate_summary(result)
    if ai_summary:
        scan = repo.update(str(scan_id), {"ai_summary": ai_summary}) or {**scan, "ai_summary": ai_summary}
    return {**scan, "ai_error": ai_error}