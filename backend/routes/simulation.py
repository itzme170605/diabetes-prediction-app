from fastapi import APIRouter, HTTPException
from models.diabetes_model import PatientData, SimulationParams, SimulationResult
from utils.ode_solver import DiabetesODESolver
from fastapi.responses import JSONResponse
import traceback

router = APIRouter()

@router.post("/run", response_model=SimulationResult)
async def run_simulation(params: SimulationParams):
    try:
        solver = DiabetesODESolver(params.patient_data)
        result = solver.simulate(
            hours=params.simulation_hours,
            food_factor=params.food_factor,
            palmitic_factor=params.palmitic_factor,
            drug_dosage=params.drug_dosage
        )
        return result
    except Exception as e:
        print(f"Simulation error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Simulation failed: {str(e)}")

@router.post("/export-pdf")
async def export_pdf(params: SimulationParams):
    try:
        # For now, return a simple response
        # We'll implement PDF generation later
        return JSONResponse(content={"message": "PDF export not yet implemented"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))