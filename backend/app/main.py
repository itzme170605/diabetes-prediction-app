import sys
import os

# Add the parent directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.simulation import router as simulation_router
from routes.user_data import router as user_router
import uvicorn

app = FastAPI(title="Diabetes Simulation API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(simulation_router, prefix="/api/simulation", tags=["simulation"])
app.include_router(user_router, prefix="/api/user", tags=["user"])

@app.get("/")
async def root():
    return {"message": "Diabetes Simulation API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)