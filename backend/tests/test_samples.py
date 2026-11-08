"""The sample files in uploads/ must always parse and scan cleanly."""

from pathlib import Path

from app.services.scan_service import run_scan
from app.utils.parser import parse_config

UPLOADS = Path(__file__).resolve().parent.parent / "uploads"


def scan(name: str):
    path = UPLOADS / name
    return run_scan(parse_config(path.read_bytes(), path.name))


def test_secure_sample_is_clean():
    result = scan("sample_secure.json")
    assert result.findings == []
    assert result.risk.risk_score == 100


def test_insecure_sample_is_critical():
    result = scan("sample_insecure.json")
    assert result.risk.risk_level == "Critical"
    assert result.risk.severity_counts["critical"] == 3


def test_multi_resource_sample():
    result = scan("sample_multi_resource.yaml")
    assert result.resources_scanned == 3
    ids = {f.resource_id for f in result.findings}
    assert "marketing-assets-bucket" in ids
    assert "deploy-bot" in ids


def test_multi_resource_secure_bucket_is_clean():
    result = scan("sample_multi_resource.yaml")
    assert not [f for f in result.findings if f.resource_id == "prod-logs-bucket"]
