"""
TaskLens Aggregator Backend - FastAPI Application
High-performance asynchronous backend for orchestrating NVIDIA Nemotron models.
"""
import logging
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

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
    if not settings.nvidia_api_key:
        logger.warning("NVIDIA_API_KEY not set - API calls will fail!")

    yield

    logger.info("Shutting down TaskLens backend")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Secure aggregator backend for TaskLens - orchestrating NVIDIA Nemotron models",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
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
    """Health check endpoint."""
    api_key_configured = bool(settings.nvidia_api_key)

    return {
        "status": "healthy",
        "api_key_configured": api_key_configured,
        "nano2_vlm_url": settings.nano2_vlm_url,
        "nano3_llm_url": settings.nano3_llm_url
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

    # Validate image data
    if not request.image_data or len(request.image_data) < 100:
        logger.error("Invalid or missing image data")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing base64 image data"
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
