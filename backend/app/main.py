from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting RIT Diabetes Simulation API...")
    yield
    # Shutdown
    logger.info("Shutting down RIT Diabetes Simulation API...")

app = FastAPI(
    title="RIT Enhanced Diabetes Simulation API",
    description="Implementation of the 12-variable ODE model from 'A mathematical model of obesity-induced type 2 diabetes'",
    version="2.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "RIT Enhanced Diabetes Simulation API",
        "version": "2.1.0",
        "status": "operational",
        "scientific_basis": {
            "paper": "A mathematical model of obesity-induced type 2 diabetes and efficacy of anti-diabetic weight reducing drug",
            "journal": "Journal of Theoretical Biology",
            "doi": "10.1016/j.jtbi.2024.111756",
            "model_type": "12-variable ODE system"
        },
        "core_features": [
            "Patient-specific simulations",
            "Meal pattern analysis",
            "Obesity progression modeling",
            "Drug treatment optimization",
            "Real-time glucose dynamics"
        ],
        "enhanced_features_v2_1": [
            "GLP-1 and glucagon dynamics",
            "GLUT-2/GLUT-4 transport mechanisms",
            "TNF-α inflammatory response",
            "Palmitic/oleic acid metabolism",
            "Drug intervention modeling (Mounjaro/Ozempic)"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "API is operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)