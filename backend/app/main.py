# app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.scans import router as scans_router
from app.core.config import APP_NAME, APP_VERSION, CORS_ORIGINS, ENVIRONMENT, LOG_LEVEL
from app.services.rule_engine import get_rules
from app.services.scan_repository import StorageError, get_repository

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("sentinel_drift")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail at startup, not on the first upload, if a rule file is broken.
    logger.info("Loaded %d security rules.", len(get_rules()))
    repo = get_repository()
    logger.info("Storage: %s", type(repo).__name__)
    try:
        repo.check()
    except StorageError as exc:
        # Don't block startup; /health and the UI will show the problem.
        logger.error("STORAGE PROBLEM: %s", exc)
    yield


app = FastAPI(
    lifespan=lifespan,
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-Powered Security Control Drift & Misconfiguration Detection",
    docs_url=None if ENVIRONMENT == "production" else "/docs",
    redoc_url=None if ENVIRONMENT == "production" else "/redoc",
)


# Registered BEFORE CORSMiddleware so CORS wraps it: even a crash returns a
# JSON error WITH CORS headers, and the browser shows the real message instead
# of a generic "cannot reach the backend".
@app.middleware("http")
async def catch_unhandled_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={
            "error": "internal_error",
            "detail": "Unexpected server error. Check the uvicorn terminal for details.",
        })


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(StorageError)
async def storage_error_handler(request: Request, exc: StorageError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"error": "storage_unavailable", "detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": "invalid_input", "detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "validation_error", "detail": exc.errors()})


app.include_router(scans_router)


@app.get("/", tags=["system"])
def root():
    return {"status": "running", "project": APP_NAME, "version": APP_VERSION}


@app.get("/health", tags=["system"])
def health():
    repo = get_repository()
    result = {
        "status": "ok",
        "rules_loaded": len(get_rules()),
        "storage": type(repo).__name__,
        "storage_ok": True,
        "storage_error": None,
    }
    try:
        repo.check()
    except StorageError as exc:
        result.update(status="degraded", storage_ok=False, storage_error=str(exc))
    return result
