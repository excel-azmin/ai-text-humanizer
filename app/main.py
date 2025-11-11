"""
Main FastAPI Application
Production-ready application entry point
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
from pathlib import Path

from app.core.config import settings
from app.core.logging import logger
# Import the dependencies module itself so we can set globals on it
from app.core import dependencies as deps
from app.services.humanizer_service import HumanizerService
from app.services.cache_service import CacheService
from app.api.v1.router import api_router


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Fast, open-source API for humanizing AI-generated content",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Mount static files
static_path = Path(settings.STATIC_DIR)
if static_path.exists():
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")


# Include API routers
app.include_router(api_router)


# Root endpoint - serve UI
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the web interface"""
    try:
        template_path = Path(settings.TEMPLATES_DIR) / "web_interface.html"
        if not template_path.exists():
            # Fallback to root directory
            template_path = Path("web_interface.html")
        
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            return HTMLResponse(
                content="<h1>AI Text Humanizer</h1><p>UI template not found</p>",
                status_code=200
            )
    except Exception as e:
        logger.error(f"Error serving UI: {e}", exc_info=True)
        return HTMLResponse(
            content=f"<h1>AI Text Humanizer</h1><p>Error loading UI: {str(e)}</p>",
            status_code=200
        )

def _serve_template(name: str) -> HTMLResponse:
    path = Path(settings.TEMPLATES_DIR) / name
    if not path.exists():
        return HTMLResponse(content=f"<h1>{name}</h1><p>Page not found</p>", status_code=200)
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Additional site pages
@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page():
    return _serve_template("pricing.html")

@app.get("/features", response_class=HTMLResponse)
async def features_page():
    return _serve_template("features.html")

@app.get("/faq", response_class=HTMLResponse)
async def faq_page():
    return _serve_template("faq.html")

@app.get("/blog", response_class=HTMLResponse)
async def blog_page():
    return _serve_template("blog.html")

@app.get("/about", response_class=HTMLResponse)
async def about_page():
    return _serve_template("about.html")

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page():
    return _serve_template("privacy.html")


# API index endpoint
@app.get("/api", response_model=dict)
async def api_index():
    """API information endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "POST /api/v1/humanize": "Humanize single text",
            "POST /api/v1/humanize/batch": "Humanize multiple texts",
            "GET /api/v1/health": "Check service health",
            "POST /api/v1/analyze": "Analyze text for AI patterns",
            "POST /api/v1/analyze/detect-and-humanize": "Auto-detect and humanize",
            "GET /api/v1/techniques": "List available techniques",
            "WS /api/v1/humanize/ws": "WebSocket for real-time humanization"
        }
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    try:
        # Initialize cache service
        deps.cache_service = CacheService()
        logger.info("Cache service initialized")
        
        # Initialize humanizer service
        deps.humanizer_service = HumanizerService()
        deps.humanizer_service.initialize()
        logger.info("Humanizer service initialized")
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")
    # Add any cleanup logic here


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower()
    )

