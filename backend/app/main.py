import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Add the parent directory to Python path so we can import our modules
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from routes.simulation import router as simulation_router
from routes.user_data import router as user_router
import uvicorn
import logging
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diabetes_api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Lifespan event handler (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Advanced Diabetes Simulation API v2.0.0")
    logger.info("All systems initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down Advanced Diabetes Simulation API")
    # Clean up resources if needed

# Create FastAPI app with enhanced metadata
app = FastAPI(
    title="Advanced Diabetes Simulation API",
    description="""
    A comprehensive diabetes simulation API that provides:
    
    - **Patient Data Management**: Comprehensive patient profiling with health metrics
    - **Diabetes Simulation**: Advanced ODE-based glucose dynamics modeling
    - **Risk Assessment**: Multi-factor diabetes and cardiovascular risk analysis
    - **Intervention Analysis**: Compare different treatment and lifestyle interventions
    - **Lifestyle Recommendations**: Personalized nutrition, exercise, and health plans
    - **Export Capabilities**: JSON and CSV export for analysis and reporting
    
    Built with FastAPI, SciPy, and NumPy for high-performance medical simulations.
    """,
    version="2.0.0",
    contact={
        "name": "Diabetes Simulation Team",
        "email": "support@diabetessim.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enhanced CORS middleware with more specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "https://yourwebsite.com",  # Add your production domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url}: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again.",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} ({duration:.3f}s)")
    
    return response

# Include routers with enhanced prefixes
app.include_router(
    simulation_router, 
    prefix="/api/v1/simulation", 
    tags=["Diabetes Simulation"],
    responses={
        404: {"description": "Simulation not found"},
        422: {"description": "Validation error"},
        500: {"description": "Simulation error"}
    }
)

app.include_router(
    user_router, 
    prefix="/api/v1/user", 
    tags=["User Data & Health Metrics"],
    responses={
        404: {"description": "User data not found"},
        422: {"description": "Validation error"},
        500: {"description": "Calculation error"}
    }
)

# Root endpoint with API information
@app.get("/", tags=["System"])
async def root():
    """API root endpoint with system information"""
    return {
        "message": "Advanced Diabetes Simulation API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Patient health profiling",
            "ODE-based glucose simulation",
            "Multi-factor risk assessment",
            "Intervention analysis",
            "Lifestyle recommendations",
            "Data export capabilities"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "simulation": "/api/v1/simulation",
            "user_data": "/api/v1/user"
        },
        "timestamp": datetime.now().isoformat()
    }

# Enhanced health check with system status
@app.get("/health", tags=["System"])
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test imports
        import numpy as np
        import scipy
        from models.diabetes_model import PatientData
        
        # Test basic calculations
        test_data = PatientData(
            name="Test User",
            age=30,
            weight=70,
            height=170,
            gender="male"
        )
        test_data.calculate_derived_values()
        
        return {
            "status": "healthy",
            "message": "All systems operational",
            "timestamp": datetime.now().isoformat(),
            "dependencies": {
                "numpy": np.__version__,
                "scipy": scipy.__version__,
                "fastapi": "operational"
            },
            "services": {
                "ode_solver": "operational",
                "patient_validation": "operational",
                "risk_calculation": "operational"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "System components not functioning properly",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# API metrics endpoint
@app.get("/metrics", tags=["System"])
async def get_metrics():
    """Get API usage metrics"""
    try:
        from routes.simulation import simulation_cache
        
        return {
            "cached_simulations": len(simulation_cache),
            "memory_usage": {
                "cache_size_mb": sum(len(str(v)) for v in simulation_cache.values()) / (1024 * 1024),
                "oldest_simulation": min(
                    (v["timestamp"] for v in simulation_cache.values()),
                    default=None
                )
            },
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# API documentation endpoint
@app.get("/api-info", tags=["System"])
async def api_info():
    """Get detailed API information and usage examples"""
    return {
        "api_name": "Advanced Diabetes Simulation API",
        "version": "2.0.0",
        "description": "Comprehensive diabetes modeling and health assessment platform",
        "key_features": {
            "simulation": {
                "description": "ODE-based glucose dynamics simulation",
                "endpoints": [
                    "POST /api/v1/simulation/run",
                    "POST /api/v1/simulation/compare",
                    "POST /api/v1/simulation/intervention-analysis"
                ]
            },
            "health_assessment": {
                "description": "Comprehensive health and risk assessment",
                "endpoints": [
                    "POST /api/v1/user/validate",
                    "POST /api/v1/user/health-metrics",
                    "POST /api/v1/user/risk-assessment"
                ]
            },
            "lifestyle": {
                "description": "Personalized lifestyle and intervention recommendations",
                "endpoints": [
                    "POST /api/v1/user/lifestyle-recommendations",
                    "POST /api/v1/user/simulate-intervention"
                ]
            }
        },
        "example_usage": {
            "basic_simulation": {
                "endpoint": "/api/v1/simulation/run",
                "method": "POST",
                "description": "Run a basic 24-hour glucose simulation"
            },
            "risk_assessment": {
                "endpoint": "/api/v1/user/risk-assessment",
                "method": "POST",
                "description": "Calculate diabetes and cardiovascular risk"
            }
        },
        "supported_formats": ["JSON", "CSV"],
        "rate_limits": "None currently implemented",
        "authentication": "None required (public API)"
    }

# Startup and shutdown events - REMOVED (now using lifespan)

# Development server configuration
if __name__ == "__main__":
    logger.info("Starting development server...")
    uvicorn.run(
        "main:app",  # Use import string instead of app object
        host="0.0.0.0", 
        port=8000,
        reload=True,  # Enable auto-reload for development
        access_log=True,
        log_level="info"
    )