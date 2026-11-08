# app/database/supabase_client.py
from functools import lru_cache

from app.core.config import SUPABASE_KEY, SUPABASE_URL


@lru_cache(maxsize=1)
def get_supabase():
    """Return a Supabase client, or None if Supabase is not configured."""
    if not (SUPABASE_URL and SUPABASE_KEY):
        return None
    from supabase import create_client  # imported here so tests run without it

    return create_client(SUPABASE_URL, SUPABASE_KEY)
