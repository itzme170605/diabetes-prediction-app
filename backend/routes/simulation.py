from typing import List
from fastapi import APIRouter, HTTPException
from models.diabetes_model import (
    PatientData, SimulationParams, SimulationResult, 
    ExtendedSimulationResult, MealSchedule
)
from utils.ode_solver import DiabetesODESolver
from utils.pdf_generator import generate_simulation_pdf
from fastapi.responses import JSONResponse, FileResponse
import traceback
import os
import tempfile

router = APIRouter()

@router.post("/run", response_model=SimulationResult)
async def run_simulation(params: SimulationParams):
    """Run basic simulation for backward compatibility"""
    try:
        solver = DiabetesODESolver(params.patient_data)
        result = solver.simulate(
            hours=params.simulation_hours,
            food_factor=params.food_factor,
            palmitic_factor=params.palmitic_factor,
            drug_dosage=params.drug_dosage,
            meal_schedule=params.meal_schedule,
            include_all_variables=False
        )
        return result
    except Exception as e:
        print(f"Simulation error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Simulation failed: {str(e)}")

@router.post("/run-extended", response_model=ExtendedSimulationResult)
async def run_extended_simulation(params: SimulationParams):
    """Run simulation with all ODE variables included"""
    try:
        solver = DiabetesODESolver(params.patient_data)
        
        # Handle multi-day simulations
        if params.simulation_days:
            hours = params.simulation_days * 24
        else:
            hours = params.simulation_hours
            
        result = solver.simulate(
            hours=hours,
            food_factor=params.food_factor,
            palmitic_factor=params.palmitic_factor,
            drug_dosage=params.drug_dosage,
            meal_schedule=params.meal_schedule,
            include_all_variables=True
        )
        return result
    except Exception as e:
        print(f"Extended simulation error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Simulation failed: {str(e)}")

@router.post("/multi-day")
async def run_multi_day_simulation(params: SimulationParams):
    """Run multi-day simulation with daily pattern repetition"""
    try:
        if not params.simulation_days:
            params.simulation_days = 7  # Default to 1 week
            
        solver = DiabetesODESolver(params.patient_data)
        
        # For multi-day, we need to handle meal patterns repeating
        # This is a simplified version - could be enhanced
        hours = params.simulation_days * 24
        
        result = solver.simulate(
            hours=hours,
            food_factor=params.food_factor,
            palmitic_factor=params.palmitic_factor,
            drug_dosage=params.drug_dosage,
            meal_schedule=params.meal_schedule,
            include_all_variables=params.include_all_variables
        )
        
        return result
    except Exception as e:
        print(f"Multi-day simulation error: {e}")
        raise HTTPException(status_code=400, detail=f"Simulation failed: {str(e)}")

@router.post("/compare-scenarios")
async def compare_scenarios(base_params: SimulationParams, scenarios: List[dict]):
    """Compare multiple simulation scenarios"""
    try:
        results = []
        
        # Run base scenario
        solver = DiabetesODESolver(base_params.patient_data)
        base_result = solver.simulate(
            hours=base_params.simulation_hours,
            food_factor=base_params.food_factor,
            palmitic_factor=base_params.palmitic_factor,
            drug_dosage=base_params.drug_dosage,
            meal_schedule=base_params.meal_schedule
        )
        results.append({"name": "Base", "result": base_result})
        
        # Run each scenario
        for scenario in scenarios:
            params = base_params.copy(update=scenario.get("params", {}))
            result = solver.simulate(
                hours=params.simulation_hours,
                food_factor=params.food_factor,
                palmitic_factor=params.palmitic_factor,
                drug_dosage=params.drug_dosage,
                meal_schedule=params.meal_schedule
            )
            results.append({
                "name": scenario.get("name", "Scenario"),
                "result": result
            })
            
        return {"scenarios": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/export-pdf")
async def export_pdf(params: SimulationParams):
    """Generate PDF report of simulation results"""
    try:
        # Run simulation first
        solver = DiabetesODESolver(params.patient_data)
        result = solver.simulate(
            hours=params.simulation_hours,
            food_factor=params.food_factor,
            palmitic_factor=params.palmitic_factor,
            drug_dosage=params.drug_dosage,
            meal_schedule=params.meal_schedule,
            include_all_variables=True  # Get all data for comprehensive report
        )
        
        # Generate PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
            generate_simulation_pdf(params, result, pdf_path)
            
        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=f'diabetes_simulation_{params.patient_data.name}.pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/preset-scenarios")
async def get_preset_scenarios():
    """Return preset simulation scenarios"""
    return {
        "scenarios": [
            {
                "name": "Normal Healthy",
                "params": {
                    "food_factor": 1.0,
                    "palmitic_factor": 1.0,
                    "drug_dosage": 0.0
                }
            },
            {
                "name": "High-Risk Lifestyle",
                "params": {
                    "food_factor": 2.0,
                    "palmitic_factor": 2.0,
                    "drug_dosage": 0.0
                }
            },
            {
                "name": "Treated with GLP-1",
                "params": {
                    "food_factor": 1.5,
                    "palmitic_factor": 1.5,
                    "drug_dosage": 1.0
                }
            },
            {
                "name": "Optimal Treatment",
                "params": {
                    "food_factor": 0.85,
                    "palmitic_factor": 1.0,
                    "drug_dosage": 1.5
                }
            }
        ]
    }