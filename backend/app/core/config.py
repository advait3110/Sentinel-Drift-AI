# app/core/config.py
"""All settings come from environment variables (backend/.env)."""

import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Sentinel Drift AI"
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

# Supabase. Use the SERVICE ROLE key here: it stays on the server only and is
# what allows the backend to read/write tables protected by Row Level Security.
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY", "")
SUPABASE_SCANS_TABLE = os.getenv("SUPABASE_SCANS_TABLE", "scans")

# Gemini (optional). If no key is set, scans still work without an AI summary.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() in ("1", "true", "yes")

# Uploads
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(1_000_000)))  # 1 MB
