from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging

from app.models.patient import PatientData
from app.models.simulation import SimulationParams, SimulationResult, ComparisonResult
from app.services.simulation_services import SimulationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["simulation"])
simulation_service = SimulationService()

# Cache for storing results (in production, use Redis or similar)
simulation_cache: Dict[str, Any] = {}

@router.post("/simulation/run", response_model=SimulationResult)
async def run_simulation(params: SimulationParams):
    """Run a diabetes simulation for a patient"""
    try:
        logger.info(f"Starting simulation for patient: {params.patient_data.get('name')}")
        
        result = simulation_service.run_simulation(params)
        
        # Cache the result
        simulation_cache[result.simulation_id] = result
        
        logger.info(f"Simulation completed: {result.simulation_id}")
        return result
        
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation/compare-meals", response_model=ComparisonResult)
async def compare_meal_patterns(params: SimulationParams):
    """Compare different meal patterns for glucose control"""
    try:
        result = simulation_service.compare_meal_patterns(params)
        return result
    except Exception as e:
        logger.error(f"Meal comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation/obesity-progression", response_model=ComparisonResult)
async def simulate_obesity_progression(params: SimulationParams):
    """Simulate progression from normal weight to obesity and diabetes"""
    try:
        result = simulation_service.simulate_obesity_progression(params)
        return result
    except Exception as e:
        logger.error(f"Obesity progression simulation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation/drug-treatment-analysis", response_model=ComparisonResult)
async def analyze_drug_treatment(params: SimulationParams):
    """Analyze the effects of drug treatment"""
    try:
        result = simulation_service.analyze_drug_treatment(params)
        return result
    except Exception as e:
        logger.error(f"Drug treatment analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simulation/result/{simulation_id}")
async def get_simulation_result(simulation_id: str):
    """Retrieve a cached simulation result"""
    if simulation_id not in simulation_cache:
        raise HTTPException(status_code=404, detail="Simulation result not found")
    
    return simulation_cache[simulation_id]

@router.post("/user/validate")
async def validate_patient_data(patient_data: PatientData):
    """Validate patient data and calculate derived fields"""
    try:
        # The Pydantic model handles validation
        return {
            "valid": True,
            "patient_data": patient_data.dict(),
            "warnings": [],
            "recommendations": []
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "warnings": ["Please check all required fields"],
            "recommendations": ["Ensure all values are within acceptable ranges"]
        }

@router.post("/user/health-metrics")
async def calculate_health_metrics(patient_data: PatientData):
    """Calculate health metrics for a patient"""
    
    # Calculate ideal weight range
    height_m = patient_data.height / 100
    ideal_bmi_min = 18.5
    ideal_bmi_max = 24.9
    ideal_weight_min = ideal_bmi_min * (height_m ** 2)
    ideal_weight_max = ideal_bmi_max * (height_m ** 2)
    
    # Calculate BMR (Basal Metabolic Rate)
    if patient_data.gender == 'male':
        bmr = 88.362 + (13.397 * patient_data.weight) + (4.799 * patient_data.height) - (5.677 * patient_data.age)
    else:
        bmr = 447.593 + (9.247 * patient_data.weight) + (3.098 * patient_data.height) - (4.330 * patient_data.age)
    
    # Activity multipliers
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725
    }
    
    activity_mult = activity_multipliers.get(patient_data.activity_level, 1.55)
    daily_calories = bmr * activity_mult
    
    # Determine cardiovascular risk
    risk_score = 0
    if patient_data.age > 45:
        risk_score += 1
    if patient_data.bmi and patient_data.bmi > 30:
        risk_score += 2
    if patient_data.smoking_status == 'smoker':
        risk_score += 2
    if patient_data.family_history:
        risk_score += 1
    if patient_data.diabetes_type == 'diabetic':
        risk_score += 2
    
    cv_risk = 'Low' if risk_score < 3 else 'Moderate' if risk_score < 5 else 'High'
    
    # Calculate metabolic age (simplified)
    metabolic_age = patient_data.age
    if patient_data.bmi and patient_data.bmi > 25:
        metabolic_age += (patient_data.bmi - 25) * 0.5
    if patient_data.activity_level == 'active':
        metabolic_age -= 5
    elif patient_data.activity_level == 'sedentary':
        metabolic_age += 5
    
    return {
        "patient_info": {
            "name": patient_data.name,
            "age": patient_data.age,
            "bmi": patient_data.bmi,
            "bmi_category": patient_data.bmi_category,
            "diabetes_risk": patient_data.diabetes_risk or "To be determined"
        },
        "health_metrics": {
            "ideal_weight_range": [round(ideal_weight_min, 1), round(ideal_weight_max, 1)],
            "current_weight": patient_data.weight,
            "weight_status": patient_data.bmi_category,
            "bmr": round(bmr, 0),
            "daily_calorie_needs": round(daily_calories, 0),
            "recommended_exercise_minutes": 150 if patient_data.activity_level in ['sedentary', 'light'] else 75,
            "cardiovascular_risk": cv_risk,
            "metabolic_age": round(metabolic_age, 0)
        }
    }

@router.delete("/simulation/clear-cache")
async def clear_simulation_cache():
    """Clear the simulation cache"""
    simulation_cache.clear()
    return {"message": "Cache cleared successfully"}

@router.get("/simulation/cache-status")
async def get_cache_status():
    """Get cache status information"""
    return {
        "cache_size": len(simulation_cache),
        "cached_simulations": list(simulation_cache.keys())
    }