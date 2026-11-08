# check_setup.py - run from the backend folder:  python check_setup.py
import os

from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL", "")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY", "")
gemini = os.getenv("GEMINI_API_KEY", "")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
cors = os.getenv("CORS_ORIGINS", "")


def mask(value):
    return f"{value[:10]}... ({len(value)} chars)" if value else "(empty)"


def ok(msg):
    print(f"  [OK]   {msg}")


def bad(msg):
    print(f"  [FAIL] {msg}")


print("\n1. .env values")
print(f"  SUPABASE_URL              = {url or '(empty)'}")
print(f"  SUPABASE_SERVICE_ROLE_KEY = {mask(key)}")
print(f"  GEMINI_API_KEY            = {mask(gemini)}")
print(f"  CORS_ORIGINS              = {cors or '(empty)'}")

for name, value in [("SUPABASE_URL", url), ("SUPABASE_SERVICE_ROLE_KEY", key), ("GEMINI_API_KEY", gemini)]:
    if value and (value != value.strip() or value[0] in "\"'" or value[-1] in "\"'"):
        bad(f"{name} has spaces or quotes around it. Remove them.")

if "localhost:3000" not in cors:
    bad("CORS_ORIGINS should be http://localhost:3000")

print("\n2. Supabase")
if not url or not key:
    bad("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is empty.")
elif "YOUR-PROJECT" in url:
    bad("SUPABASE_URL is still the placeholder. Use your real Project URL.")
elif not url.startswith("https://") or ".supabase.co" not in url:
    bad("SUPABASE_URL should look like https://xxxxxxxx.supabase.co")
elif key.startswith("sb_publishable_"):
    bad("That is the PUBLISHABLE key. Use the SECRET key (sb_secret_...).")
else:
    try:
        from supabase import create_client

        client = create_client(url.rstrip("/"), key)
        client.table("scans").select("id").limit(1).execute()
        ok("Connected, and the 'scans' table exists.")
    except Exception as exc:
        text = str(exc)
        low = text.lower()
        if "getaddrinfo" in low or "connecterror" in low:
            bad("Cannot reach that URL. Check SUPABASE_URL for typos.")
        elif "pgrst205" in low or "42p01" in low or "could not find the table" in low:
            bad("Connected, but the 'scans' table does not exist. "
                "Run migrations/001_create_scans.sql in the Supabase SQL Editor.")
        elif "invalid api key" in low or "jwt" in low or "unauthorized" in low:
            bad("Supabase rejected the key. Copy the secret key again.")
        else:
            bad(f"Supabase error: {text[:300]}")

print("\n3. Gemini")
if not gemini:
    bad("GEMINI_API_KEY is empty (scans still work, just without an AI summary).")
else:
    try:
        from google import genai

        reply = genai.Client(api_key=gemini).models.generate_content(
            model=model, contents="Reply with the single word: OK"
        )
        ok(f"Gemini answered with model {model}: {(reply.text or '').strip()[:40]}")
    except ImportError:
        bad("google-genai is not installed. Run: pip install google-genai")
    except Exception as exc:
        bad(f"Gemini error: {str(exc)[:300]}")

print("\nDone. Fix any [FAIL] lines, then restart uvicorn.\n")
