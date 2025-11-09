"""
TaskLens Aggregator Backend - FastAPI Application
High-performance asynchronous backend for orchestrating NVIDIA Nemotron models.
"""
import logging
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import httpx
import base64
import uuid
import time
from collections import defaultdict

from core.schemas import TaskRequest, TaskPlan, WiringStep
from services.nemotron import NemotronService
from core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug_mode}")

    # Validate API key on startup
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY not set - API calls will fail!")

    yield

    logger.info("Shutting down TaskLens backend")


# Simple in-memory rate limiter
class RateLimiter:
    """Simple token bucket rate limiter."""
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Check if under limit
        if len(self.requests[client_ip]) < self.requests_per_minute:
            self.requests[client_ip].append(now)
            return True
        return False


# Middleware for request ID tracking, size limits, and rate limiting
class RequestMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking, validation, and rate limiting."""
    
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB limit
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests_per_minute=30)
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Rate limiting (skip for health checks)
        if not request.url.path.endswith('/health'):
            client_ip = request.client.host if request.client else "unknown"
            if not self.rate_limiter.is_allowed(client_ip):
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded. Maximum 30 requests per minute allowed."
                    },
                    headers={"X-Request-ID": request_id}
                )
        
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request payload too large. Maximum size is 10MB."}
            )
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Secure aggregator backend for TaskLens - orchestrating NVIDIA Nemotron models",
    lifespan=lifespan
)

# Add middleware in correct order (request tracking first, then CORS)
app.add_middleware(RequestMiddleware)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*", "X-Request-ID"]
)

# Initialize service
nemotron_service = NemotronService()


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "endpoints": {
            "plan_generation": "/api/v1/plan/generate",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - minimal information disclosure."""
    # Only return basic health status, no sensitive configuration details
    return {
        "status": "healthy",
        "version": settings.app_version
    }


@app.post(
    "/api/v1/plan/generate",
    response_model=List[WiringStep],
    status_code=status.HTTP_200_OK,
    summary="Generate Wiring Plan",
    description="Orchestrates Nemotron Nano 2 VL (simulated) and Nano 3 to generate a structured wiring plan with pin guidance"
)
async def generate_plan(request: TaskRequest):
    """
    Primary endpoint: Generate a complete wiring plan from an image and user goal.

    This endpoint orchestrates two stages:
    1. Nemotron Nano 2 VL - Visual identification of hardware component (SIMULATED)
    2. Nemotron Nano 3 - 5-step wiring plan with safe/unsafe pin guidance

    Args:
        request: TaskRequest containing base64 image and user goal

    Returns:
        List[WiringStep]: JSON array of 5 wiring steps with pin guidance and coordinates

    Raises:
        HTTPException: 400 for invalid input, 500 for internal errors, 503 for API failures
    """
    logger.info(f"Received wiring plan request - Goal: {request.user_goal[:50]}...")

    # Validate API key
    if not settings.nvidia_api_key:
        logger.error("NVIDIA_API_KEY not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured. Please set NVIDIA_API_KEY environment variable."
        )

    # Enhanced validation for image data
    if not request.image_data or len(request.image_data) < 100:
        logger.error("Invalid or missing image data")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing base64 image data"
        )
    
    # Validate base64 encoding and reasonable size limits
    try:
        # Remove data URL prefix if present
        image_data = request.image_data
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Validate base64 format
        decoded = base64.b64decode(image_data, validate=True)
        
        # Check decoded size (max 8MB for image)
        if len(decoded) > 8 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image size too large. Maximum 8MB allowed."
            )
        
        # Update request with cleaned data
        request.image_data = image_data
        
    except Exception as decode_error:
        logger.error(f"Invalid base64 image data: {str(decode_error)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 encoding in image data"
        )

    try:
        # Orchestrate the full pipeline
        wiring_plan = await nemotron_service.orchestrate_full_pipeline(
            image_base64=request.image_data,
            user_goal=request.user_goal
        )

        logger.info(f"Successfully generated wiring plan with {len(wiring_plan)} steps")
        return wiring_plan

    except httpx.HTTPStatusError as e:
        logger.error(f"NVIDIA API error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"NVIDIA API error: {e.response.status_code}. Please check your API key and endpoint configuration."
        )

    except httpx.TimeoutException:
        logger.error("Request to NVIDIA API timed out")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request to AI model timed out. Please try again."
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )

    except Exception as e:
        logger.exception(f"Unexpected error in plan generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}" if settings.debug_mode else "Internal server error occurred"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc) if settings.debug_mode else None
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug_mode,
        log_level="info"
    )
