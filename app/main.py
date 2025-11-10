"""Main FastAPI application for Court Service"""
from fastapi import FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routes import router as facilities_router

settings = get_settings()

# Get settings

FACILITIES_PREFIX = f"/api/{settings.api_version}/facilities"

if settings.env=="prod":
    # Create FastAPI application
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        
    )
else:
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

security = HTTPBearer()

app.include_router(facilities_router, prefix=FACILITIES_PREFIX)


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
