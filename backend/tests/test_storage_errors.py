"""Supabase failures must become clear StorageError messages, not crashes."""

import pytest

from app.services.scan_repository import (
    StorageError,
    SupabaseScanRepository,
    explain_storage_error,
)


class _FailingQuery:
    def __init__(self, exc):
        self._exc = exc

    def __getattr__(self, name):          # select/order/limit/eq/insert chain
        return lambda *a, **k: self

    def execute(self):
        raise self._exc


class _FakeClient:
    def __init__(self, exc):
        self._exc = exc

    def table(self, name):
        return _FailingQuery(self._exc)


@pytest.mark.parametrize("raw,expected", [
    ("{'code': 'PGRST205', 'message': \"Could not find the table 'public.scans'\"}", "does not exist"),
    ('relation "public.scans" does not exist (42P01)', "does not exist"),
    ("Invalid API key", "rejected the API key"),
    ("permission denied for table scans (42501)", "service_role key"),
    ("[Errno 11001] getaddrinfo failed", "Cannot connect"),
    ("something odd", "Supabase request failed"),
])
def test_explain(raw, expected):
    assert expected in explain_storage_error(Exception(raw))


@pytest.mark.parametrize("call", [
    lambda r: r.list(),
    lambda r: r.get("x"),
    lambda r: r.save({"a": 1}),
    lambda r: r.check(),
])
def test_repository_raises_storage_error(call):
    repo = SupabaseScanRepository(_FakeClient(Exception("Could not find the table 'public.scans' PGRST205")))
    with pytest.raises(StorageError, match="migrations/001_create_scans.sql"):
        call(repo)
