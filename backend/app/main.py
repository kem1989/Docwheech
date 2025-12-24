"""
Docwheech MVP - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import auth, upload, extraction, acord, export, gap_detection
from app.config import settings
from app.database import create_tables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Docwheech API...")
    print("🚀 Backend update test - Container restarted successfully!")
    create_tables()
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Docwheech API...")


# Create FastAPI application
app = FastAPI(
    title="Docwheech API",
    description="Automated ACORD form processing for commercial insurance",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["File Upload"])
app.include_router(extraction.router, prefix="/api/extraction", tags=["AI Extraction"])
app.include_router(acord.router, prefix="/api/acord", tags=["ACORD Forms"])
app.include_router(export.router, prefix="/api/export", tags=["PDF Export"])
app.include_router(gap_detection.router, prefix="/api/gaps", tags=["Gap Detection"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Docwheech API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "updated": "Container restart test successful! 🎉"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "docwheech-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
