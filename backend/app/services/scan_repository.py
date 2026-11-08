# app/services/scan_repository.py
"""
Storage for scan results.

- SupabaseScanRepository: used when SUPABASE_URL and a key are set.
- InMemoryScanRepository: fallback for local development and tests.
  Data is lost when the server restarts.

Supabase failures are raised as StorageError with a message that says what
to fix (missing table, wrong key, unreachable project).
"""

import logging
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from threading import Lock

from app.core.config import SUPABASE_SCANS_TABLE
from app.database.supabase_client import get_supabase

logger = logging.getLogger("sentinel_drift")

# Columns returned by the list endpoint (no heavy findings payload).
SUMMARY_FIELDS = (
    "id", "created_at", "filename", "resources_scanned",
    "risk_score", "risk_level", "findings_count", "severity_counts",
)

# Every column the app reads or writes; the health check verifies all of them.
REQUIRED_COLUMNS = SUMMARY_FIELDS + ("risk", "findings", "ai_summary")


class StorageError(Exception):
    """The scan store could not be read or written. The message is safe to show."""


def explain_storage_error(exc: Exception, table: str = SUPABASE_SCANS_TABLE) -> str:
    text = str(exc)
    low = text.lower()
    if "pgrst205" in low or "42p01" in low or ("relation" in low and "does not exist" in low) \
            or "could not find the table" in low:
        return (f"Supabase table '{table}' does not exist. Run "
                "backend/migrations/001_create_scans.sql in the Supabase SQL Editor.")
    if "invalid api key" in low or "jwt" in low or "no api key" in low or "unauthorized" in low:
        return ("Supabase rejected the API key. Check SUPABASE_URL and "
                "SUPABASE_SERVICE_ROLE_KEY in backend/.env (use the service_role key).")
    if "42501" in low or "permission denied" in low or "row-level security" in low:
        return ("Supabase denied access to the table. Use the service_role key, "
                "not the anon key, in SUPABASE_SERVICE_ROLE_KEY.")
    if any(s in low for s in ("connecterror", "name or service not known", "getaddrinfo",
                              "timed out", "connection refused", "nodename nor servname")):
        return "Cannot connect to Supabase. Check SUPABASE_URL and your internet connection."
    if "pgrst204" in low or "42703" in low or ("column" in low and "does not exist" in low):
        return (f"Supabase table '{table}' exists but has the wrong columns. Run "
                "backend/migrations/000_reset_scans.sql in the Supabase SQL Editor.")
    return f"Supabase request failed: {text[:300]}"


class ScanRepository:
    def save(self, row: dict) -> dict:
        raise NotImplementedError

    def list(self, limit: int = 50) -> list[dict]:
        raise NotImplementedError

    def get(self, scan_id: str) -> dict | None:
        raise NotImplementedError

    def delete(self, scan_id: str) -> bool:
        """Delete one scan. Returns False if it did not exist."""
        raise NotImplementedError

    def update(self, scan_id: str, fields: dict) -> dict | None:
        """Change some columns of one scan. Returns the updated scan, or None if missing."""
        raise NotImplementedError

    def check(self) -> None:
        """Raise StorageError if the store is not usable."""


class InMemoryScanRepository(ScanRepository):
    def __init__(self) -> None:
        self._rows: dict[str, dict] = {}
        self._lock = Lock()

    def save(self, row: dict) -> dict:
        saved = {
            **row,
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self._rows[saved["id"]] = saved
        return saved

    def list(self, limit: int = 50) -> list[dict]:
        with self._lock:
            rows = sorted(self._rows.values(), key=lambda r: r["created_at"], reverse=True)
        return [{k: r.get(k) for k in SUMMARY_FIELDS} for r in rows[:limit]]

    def get(self, scan_id: str) -> dict | None:
        with self._lock:
            return self._rows.get(scan_id)

    def delete(self, scan_id: str) -> bool:
        with self._lock:
            return self._rows.pop(scan_id, None) is not None

    def update(self, scan_id: str, fields: dict) -> dict | None:
        with self._lock:
            row = self._rows.get(scan_id)
            if row is None:
                return None
            row.update(fields)
            return row


class SupabaseScanRepository(ScanRepository):
    def __init__(self, client, table: str = SUPABASE_SCANS_TABLE) -> None:
        self._client = client
        self._table = table

    def _run(self, action: str, fn):
        try:
            return fn()
        except StorageError:
            raise
        except Exception as exc:
            logger.exception("Supabase %s failed", action)
            raise StorageError(explain_storage_error(exc, self._table)) from exc

    def save(self, row: dict) -> dict:
        resp = self._run("insert", lambda: self._client.table(self._table).insert(row).execute())
        if not resp.data:
            raise StorageError("Supabase insert returned no data. Check that the service_role key is used.")
        return resp.data[0]

    def list(self, limit: int = 50) -> list[dict]:
        resp = self._run("list", lambda: (
            self._client.table(self._table)
            .select(",".join(SUMMARY_FIELDS))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        ))
        return resp.data or []

    def get(self, scan_id: str) -> dict | None:
        resp = self._run("get", lambda: (
            self._client.table(self._table).select("*").eq("id", scan_id).limit(1).execute()
        ))
        return resp.data[0] if resp.data else None

    def delete(self, scan_id: str) -> bool:
        resp = self._run("delete", lambda: (
            self._client.table(self._table).delete().eq("id", scan_id).execute()
        ))
        return bool(resp.data)

    def update(self, scan_id: str, fields: dict) -> dict | None:
        resp = self._run("update", lambda: (
            self._client.table(self._table).update(fields).eq("id", scan_id).execute()
        ))
        return resp.data[0] if resp.data else None

    def check(self) -> None:
        self._run("health check", lambda: (
            self._client.table(self._table).select(",".join(REQUIRED_COLUMNS)).limit(1).execute()
        ))


@lru_cache(maxsize=1)
def get_repository() -> ScanRepository:
    client = get_supabase()
    if client is None:
        logger.warning("Supabase is not configured. Using in-memory storage: "
                       "scans will be lost when the server restarts.")
        return InMemoryScanRepository()
    return SupabaseScanRepository(client)