"""End-to-end API tests. Need fastapi + httpx (both in requirements.txt)."""

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from app.api import scans  # noqa: E402
from app.main import app  # noqa: E402
from app.services.scan_repository import InMemoryScanRepository  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    repo = InMemoryScanRepository()
    monkeypatch.setattr(scans, "get_repository", lambda: repo)
    monkeypatch.setattr(scans, "summarize_findings", lambda result: "test summary")
    with TestClient(app) as c:
        yield c


def test_upload_list_get(client):
    resp = client.post("/api/scans", files={"file": ("cfg.json", b'{"public": true}', "application/json")})
    assert resp.status_code == 201, resp.text
    scan = resp.json()
    assert scan["risk_level"] in ("High Risk", "Critical")
    assert scan["ai_summary"] == "test summary"

    listed = client.get("/api/scans").json()
    assert listed[0]["id"] == scan["id"]
    assert "findings" not in listed[0]

    detail = client.get(f"/api/scans/{scan['id']}").json()
    assert detail["findings"][0]["severity"] == "critical"


def test_bad_file_is_400(client):
    resp = client.post("/api/scans", files={"file": ("cfg.json", b"{bad", "application/json")})
    assert resp.status_code == 400
    assert "Invalid JSON" in resp.json()["detail"]


def test_unknown_scan_is_404_and_bad_id_is_422(client):
    assert client.get("/api/scans/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.get("/api/scans/not-a-uuid").status_code == 422


def test_storage_error_is_503_with_cors_headers(monkeypatch):
    from app.services.scan_repository import StorageError

    class Broken(InMemoryScanRepository):
        def list(self, limit=50):
            raise StorageError("Supabase table 'scans' does not exist.")

        def check(self):
            raise StorageError("Supabase table 'scans' does not exist.")

    broken = Broken()
    monkeypatch.setattr(scans, "get_repository", lambda: broken)
    monkeypatch.setattr("app.main.get_repository", lambda: broken)
    with TestClient(app) as c:
        resp = c.get("/api/scans", headers={"Origin": "http://localhost:3000"})
        assert resp.status_code == 503
        assert "does not exist" in resp.json()["detail"]
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"

        health = c.get("/health").json()
        assert health["status"] == "degraded"
        assert health["storage_ok"] is False


def test_crash_returns_500_with_cors_headers(monkeypatch):
    class Crashing(InMemoryScanRepository):
        def list(self, limit=50):
            raise RuntimeError("boom")

    crashing = Crashing()
    monkeypatch.setattr(scans, "get_repository", lambda: crashing)
    with TestClient(app, raise_server_exceptions=False) as c:
        resp = c.get("/api/scans", headers={"Origin": "http://localhost:3000"})
        assert resp.status_code == 500
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert "boom" not in resp.text
