"""Main FastAPI application for Court Service"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.routes import router as facilities_router
import logging
import sys

# Structured JSON logging setup
from pythonjsonlogger import jsonlogger

logger = logging.getLogger("court-service")
handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s',
    rename_fields={"levelname": "level", "asctime": "timestamp"}
)
handler.setFormatter(formatter)
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

settings = get_settings()

FACILITIES_PREFIX = f"/api/{settings.api_version}/facilities"

# Enable docs for documentation generation
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    openapi_url=f"{FACILITIES_PREFIX}/openapi.json",
    docs_url=f"{FACILITIES_PREFIX}/docs",
    redoc_url=f"{FACILITIES_PREFIX}/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics instrumentation
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(facilities_router, prefix=FACILITIES_PREFIX)


# Custom exception handler for validation errors (UUID parsing, etc.)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors (like invalid UUID format) and return 400 instead of 422.
    This makes the API more consistent with REST conventions.
    """
    errors = exc.errors()
    
    # Check if it's a UUID validation error in path parameters
    for error in errors:
        if error.get("type") == "uuid_parsing" and "path" in error.get("loc", []):
            # Return 400 Bad Request for invalid UUID in path
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": f"Invalid UUID format: {error.get('input', 'unknown')}"
                }
            )
    
    # For other validation errors, return 422 (default behavior)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
    )


logger.info(f"Court Service started in {settings.env} mode")
logger.info(f"API available at: {FACILITIES_PREFIX}")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "service": "Court Service",
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""

    return {
        "status": "healthy",
        "service": "court-service"
    }
