import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Add the parent directory to Python path so we can import our modules
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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
    logger.info("Starting Enhanced Diabetes Simulation API v2.1.0")
    logger.info("Features: Enhanced ODE model, meal patterns, drug treatment analysis")
    logger.info("All systems initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down Enhanced Diabetes Simulation API")
    # Clean up resources if needed

# Create FastAPI app with enhanced metadata
app = FastAPI(
    title="Enhanced Diabetes Simulation API",
    description="""
    A comprehensive diabetes simulation API based on the mathematical model by Siewe & Friedman (2024):
    
    ## Core Features
    - **Advanced ODE Simulation**: 12-variable differential equation system modeling glucose dynamics
    - **Patient Profiling**: Comprehensive health assessment with BMI, diabetes risk, and lifestyle factors
    - **Meal Pattern Analysis**: Compare different eating patterns and their effects on glucose control
    - **Drug Treatment Modeling**: Simulate GLP-1 agonist effects (Mounjaro, Ozempic) with lifestyle changes
    - **Obesity Progression**: Model progression from normal weight to obesity and diabetes development
    - **Risk Assessment**: Multi-factor diabetes and cardiovascular risk calculation
    - **Lifestyle Recommendations**: Personalized nutrition, exercise, and health management plans
    
    ## Enhanced Capabilities (v2.1.0)
    - **Individual Meal Factors**: Customize breakfast, lunch, dinner, and snack portions
    - **Enhanced Glucose Metrics**: Dawn phenomenon, post-meal response, glucose stability analysis
    - **Comprehensive Health Metrics**: BMR, daily calorie needs, metabolic age calculation
    - **Advanced Interventions**: Compare diet, medication, meal timing, and combined approaches
    - **Clinical Outcomes**: Treatment effectiveness analysis with A1C reduction predictions
    - **Export Functions**: JSON and CSV export for detailed analysis and reporting
    
    ## Scientific Foundation
    Based on peer-reviewed research published in Journal of Theoretical Biology (2024):
    "A mathematical model of obesity-induced type 2 diabetes and efficacy of anti-diabetic weight reducing drug"
    
    Built with FastAPI, SciPy, and NumPy for high-performance medical simulations.
    """,
    version="2.1.0",
    contact={
        "name": "Enhanced Diabetes Simulation Team",
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
        "http://localhost:5173",  # Vite default port
        "https://yourwebsite.com",  # Add your production domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# REMOVE the GZip middleware that's causing issues
# app.add_middleware(GZipMiddleware, minimum_size=1000)

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
    tags=["Enhanced Diabetes Simulation"],
    responses={
        404: {"description": "Simulation not found"},
        422: {"description": "Validation error"},
        500: {"description": "Simulation error"}
    }
)

app.include_router(
    user_router, 
    prefix="/api/v1/user", 
    tags=["User Data & Health Assessment"],
    responses={
        404: {"description": "User data not found"},
        422: {"description": "Validation error"},
        500: {"description": "Calculation error"}
    }
)

# Root endpoint with comprehensive API information
@app.get("/", tags=["System"])
async def root():
    """API root endpoint with enhanced system information"""
    return {
        "message": "Enhanced Diabetes Simulation API",
        "version": "2.1.0",
        "status": "running",
        "scientific_basis": {
            "paper": "Siewe, N., & Friedman, A. (2024). A mathematical model of obesity-induced type 2 diabetes and efficacy of anti-diabetic weight reducing drug",
            "journal": "Journal of Theoretical Biology",
            "doi": "10.1016/j.jtbi.2024.111756",
            "model_type": "12-variable ODE system"
        },
        "core_features": [
            "Advanced ODE-based glucose simulation",
            "Personalized patient profiling",
            "Meal pattern analysis",
            "Drug treatment modeling (GLP-1 agonists)",
            "Obesity progression simulation",
            "Comprehensive risk assessment",
            "Lifestyle recommendations"
        ],
        "enhanced_features_v2_1": [
            "Individual meal factor customization",
            "Enhanced glucose stability metrics",
            "Dawn phenomenon analysis",
            "Post-meal response profiling",
            "Metabolic age calculation",
            "Advanced intervention comparisons",
            "Clinical outcomes prediction"
        ],
        "simulation_capabilities": {
            "variables": 12,
            "parameters": "50+",
            "time_resolution": "5-minute intervals",
            "simulation_duration": "6-168 hours",
            "patient_personalization": "Age, BMI, diabetes status, medications, lifestyle"
        },
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

# ADD the missing /api/v1/ endpoint that the frontend is trying to access
@app.get("/api/v1/", tags=["System"])
async def api_v1_root():
    """API v1 root endpoint"""
    return {
        "message": "Enhanced Diabetes Simulation API v1",
        "version": "2.1.0",
        "status": "running",
        "available_endpoints": {
            "simulation": "/api/v1/simulation",
            "user_data": "/api/v1/user",
            "health_check": "/health",
            "system_info": "/",
            "documentation": "/docs"
        },
        "timestamp": datetime.now().isoformat()
    }

# Enhanced health check with comprehensive system validation
@app.get("/health", tags=["System"])
async def health_check():
    """Comprehensive health check endpoint with dependency validation"""
    try:
        # Test critical imports
        import numpy as np
        import scipy
        from models.diabetes_model import PatientData, SimulationParams, SimulationResult
        from utils.ode_solver import DiabetesODESolver
        
        # Test basic model functionality
        test_patient = PatientData(
            name="Health Check User",
            age=35,
            weight=75,
            height=175,
            gender="male",
            activity_level="moderate"
        )
        test_patient.calculate_derived_values()
        
        # Test ODE solver initialization
        solver = DiabetesODESolver(test_patient)
        initial_conditions = solver.get_initial_conditions()
        
        # Validate that we have 12 initial conditions (12-variable system)
        if len(initial_conditions) != 12:
            raise Exception(f"Expected 12 initial conditions, got {len(initial_conditions)}")
        
        return {
            "status": "healthy",
            "message": "All systems operational - Enhanced Diabetes Simulation API ready",
            "timestamp": datetime.now().isoformat(),
            "system_validation": {
                "dependencies": {
                    "numpy": np.__version__,
                    "scipy": scipy.__version__,
                    "fastapi": "operational"
                },
                "core_services": {
                    "ode_solver": "operational",
                    "patient_validation": "operational",
                    "risk_calculation": "operational",
                    "12_variable_system": "validated"
                },
                "model_validation": {
                    "initial_conditions_count": len(initial_conditions),
                    "patient_profiling": "functional",
                    "bmi_calculation": f"Test BMI: {test_patient.bmi}",
                    "risk_assessment": f"Test risk: {test_patient.diabetes_risk}"
                }
            },
            "api_features": {
                "simulation_endpoints": 8,
                "user_data_endpoints": 4,
                "export_formats": ["JSON", "CSV"],
                "cache_system": "active"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "System components not functioning properly",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "troubleshooting": {
                    "common_issues": [
                        "Missing required dependencies (numpy, scipy)",
                        "Import path issues with models or utils",
                        "ODE solver initialization problems"
                    ],
                    "recommended_actions": [
                        "Check Python environment and dependencies",
                        "Verify all model files are present",
                        "Review log files for detailed error information"
                    ]
                }
            }
        )

# Enhanced API metrics endpoint
@app.get("/metrics", tags=["System"])
async def get_metrics():
    """Get comprehensive API usage metrics and performance data"""
    try:
        from routes.simulation import simulation_cache
        
        # Calculate cache statistics
        cache_size_bytes = sum(len(str(v)) for v in simulation_cache.values())
        cache_size_mb = cache_size_bytes / (1024 * 1024)
        
        # Get oldest simulation timestamp
        oldest_simulation = None
        if simulation_cache:
            oldest_simulation = min(
                (v["timestamp"] for v in simulation_cache.values()),
                default=None
            )
        
        # Simulation statistics
        simulation_stats = {
            "total_cached": len(simulation_cache),
            "cache_size_mb": round(cache_size_mb, 2),
            "oldest_simulation": oldest_simulation.isoformat() if oldest_simulation else None
        }
        
        # System performance metrics
        performance_metrics = {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "memory_usage": {
                "cache_memory_mb": round(cache_size_mb, 2),
                "estimated_per_simulation_kb": round(cache_size_bytes / len(simulation_cache) / 1024, 2) if simulation_cache else 0
            }
        }
        
        return {
            "api_metrics": {
                "version": "2.1.0",
                "uptime_check": "healthy",
                "timestamp": datetime.now().isoformat()
            },
            "simulation_statistics": simulation_stats,
            "performance_metrics": performance_metrics,
            "feature_usage": {
                "simulation_types": [
                    "basic_glucose_simulation",
                    "meal_pattern_comparison", 
                    "drug_treatment_analysis",
                    "obesity_progression_modeling",
                    "intervention_effectiveness"
                ],
                "supported_patient_parameters": [
                    "age", "weight", "height", "gender", "bmi",
                    "diabetes_type", "activity_level", "medications",
                    "smoking_status", "family_history"
                ],
                "output_variables": [
                    "glucose", "insulin", "glucagon", "glp1",
                    "beta_cells", "alpha_cells", "glut2", "glut4",
                    "palmitic_acid", "oleic_acid", "tnf_alpha", "stored_glucose"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Metrics collection failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Enhanced API documentation endpoint
@app.get("/api-info", tags=["System"])
async def api_info():
    """Get detailed API information, usage examples, and scientific background"""
    return {
        "api_overview": {
            "name": "Enhanced Diabetes Simulation API",
            "version": "2.1.0",
            "description": "Advanced glucose dynamics modeling based on peer-reviewed research",
            "scientific_foundation": {
                "authors": ["Nourridine Siewe", "Avner Friedman"],
                "title": "A mathematical model of obesity-induced type 2 diabetes and efficacy of anti-diabetic weight reducing drug",
                "journal": "Journal of Theoretical Biology",
                "year": 2024,
                "doi": "10.1016/j.jtbi.2024.111756"
            }
        },
        "mathematical_model": {
            "type": "12-variable ODE system",
            "variables": [
                "L (GLP-1)", "A (α-cells)", "B (β-cells)", "I (Insulin)",
                "U2 (GLUT-2)", "U4 (GLUT-4)", "C (Glucagon)", "G (Glucose)",
                "G* (Stored Glucose)", "O (Oleic Acid)", "P (Palmitic Acid)", "Tα (TNF-α)"
            ],
            "key_processes": [
                "Food intake and glucose absorption",
                "Insulin and glucagon secretion",
                "Glucose transport (GLUT-2, GLUT-4)",
                "Obesity-induced inflammation (TNF-α)",
                "Drug effects (GLP-1 agonists)"
            ]
        },
        "key_features": {
            "simulation": {
                "description": "Run comprehensive glucose dynamics simulations",
                "main_endpoint": "POST /api/v1/simulation/run",
                "enhanced_endpoints": [
                    "POST /api/v1/simulation/compare-meals - Compare meal patterns",
                    "POST /api/v1/simulation/drug-treatment-analysis - Model GLP-1 agonist effects",
                    "POST /api/v1/simulation/obesity-progression - Track obesity development",
                    "POST /api/v1/simulation/intervention-analysis - Compare interventions"
                ]
            },
            "health_assessment": {
                "description": "Comprehensive health and risk assessment",
                "endpoints": [
                    "POST /api/v1/user/validate - Validate patient data",
                    "POST /api/v1/user/health-metrics - Calculate health metrics",
                    "POST /api/v1/user/risk-assessment - Assess diabetes/CV risk",
                    "POST /api/v1/user/lifestyle-recommendations - Generate recommendations"
                ]
            }
        },
        "example_usage": {
            "basic_simulation": {
                "endpoint": "/api/v1/simulation/run",
                "method": "POST",
                "description": "Run 24-hour glucose simulation with personalized parameters",
                "example_payload": {
                    "patient_data": {
                        "name": "John Doe",
                        "age": 45,
                        "weight": 85,
                        "height": 175,
                        "gender": "male",
                        "diabetes_type": "prediabetic",
                        "activity_level": "moderate"
                    },
                    "simulation_hours": 24,
                    "meal_times": [0, 6, 12, 18],
                    "meal_factors": [1.0, 1.0, 2.0, 0.0]
                }
            },
            "drug_treatment": {
                "endpoint": "/api/v1/simulation/drug-treatment-analysis",
                "method": "POST",
                "description": "Compare different GLP-1 agonist dosages with lifestyle changes"
            },
            "risk_assessment": {
                "endpoint": "/api/v1/user/risk-assessment",
                "method": "POST",
                "description": "Calculate comprehensive diabetes and cardiovascular risk scores"
            }
        },
        "output_formats": {
            "simulation_results": {
                "time_series_data": ["glucose", "insulin", "glucagon", "glp1", "beta_cells", "alpha_cells"],
                "enhanced_variables": ["glut2", "glut4", "palmitic_acid", "oleic_acid", "tnf_alpha"],
                "clinical_metrics": ["a1c_estimate", "diagnosis", "time_in_range", "glucose_variability"],
                "advanced_analysis": ["dawn_phenomenon", "post_meal_response", "glucose_stability"]
            },
            "export_options": ["JSON", "CSV"],
            "visualization_ready": "All data formatted for direct plotting"
        },
        "personalization_features": {
            "patient_factors": [
                "Age-related β-cell decline",
                "BMI-based insulin resistance",
                "Activity level effects",
                "Medication adjustments",
                "Gender-specific metabolism",
                "Smoking impact"
            ],
            "meal_customization": [
                "Individual meal portions",
                "Flexible meal timing",
                "Meal pattern comparisons",
                "Post-meal response analysis"
            ]
        },
        "clinical_applications": [
            "Diabetes risk assessment and prevention",
            "Treatment effectiveness prediction",
            "Lifestyle intervention planning",
            "Patient education and counseling",
            "Research and clinical trial support"
        ],
        "rate_limits": "None currently implemented (suitable for research use)",
        "authentication": "None required (open research API)",
        "support": {
            "documentation": "/docs (Swagger) and /redoc (ReDoc)",
            "health_check": "/health",
            "metrics": "/metrics",
            "contact": "support@diabetessim.com"
        }
    }

# Development server configuration
if __name__ == "__main__":
    logger.info("Starting Enhanced Diabetes Simulation API development server...")
    logger.info("Version 2.1.0 - Enhanced meal patterns, drug modeling, and clinical outcomes")
    uvicorn.run(
        "main:app",  # Use import string instead of app object
        host="0.0.0.0", 
        port=8000,
        reload=True,  # Enable auto-reload for development
        access_log=True,
        log_level="info",
        reload_dirs=[".", "../models", "../utils", "../routes"]  # Monitor all relevant directories
    )