from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from models.diabetes_model import PatientData, SimulationParams, SimulationResult, HealthMetrics
from utils.ode_solver import DiabetesODESolver
import traceback
import json
import os
from datetime import datetime
import uuid

router = APIRouter()

# In-memory storage for simulation results (use database in production)
simulation_cache = {}

@router.post("/run", response_model=SimulationResult)
async def run_simulation(params: SimulationParams):
    """Run diabetes simulation with enhanced parameters"""
    try:
        # Validate and prepare patient data
        patient_data = params.patient_data
        patient_data.calculate_derived_values()
        
        # Create solver and run simulation
        solver = DiabetesODESolver(patient_data)
        result = solver.simulate(
            hours=params.simulation_hours,
            food_factor=params.food_factor,
            palmitic_factor=params.palmitic_factor,
            drug_dosage=params.drug_dosage,
            meal_times=params.meal_times,
            exercise_times=params.exercise_times
        )
        
        # Store result in cache with unique ID
        simulation_id = str(uuid.uuid4())
        simulation_cache[simulation_id] = {
            "result": result,
            "timestamp": datetime.now(),
            "params": params
        }
        
        # Add simulation ID to result
        result.simulation_summary["simulation_id"] = simulation_id
        
        return result
        
    except Exception as e:
        print(f"Simulation error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Simulation failed: {str(e)}")

@router.get("/result/{simulation_id}")
async def get_simulation_result(simulation_id: str):
    """Retrieve a cached simulation result"""
    if simulation_id not in simulation_cache:
        raise HTTPException(status_code=404, detail="Simulation result not found")
    
    cached_result = simulation_cache[simulation_id]
    return cached_result["result"]

@router.post("/compare")
async def compare_simulations(simulation_ids: list[str]):
    """Compare multiple simulation results"""
    if len(simulation_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 simulations required for comparison")
    
    results = []
    for sim_id in simulation_ids:
        if sim_id not in simulation_cache:
            raise HTTPException(status_code=404, detail=f"Simulation {sim_id} not found")
        results.append(simulation_cache[sim_id]["result"])
    
    # Generate comparison data
    comparison = {
        "simulations": results,
        "comparison_metrics": _generate_comparison_metrics(results),
        "recommendations": _generate_comparison_recommendations(results)
    }
    
    return comparison

@router.post("/batch-simulate")
async def batch_simulate(simulation_list: list[SimulationParams]):
    """Run multiple simulations for comparison or analysis"""
    try:
        results = []
        
        for params in simulation_list:
            # Validate and prepare patient data
            patient_data = params.patient_data
            patient_data.calculate_derived_values()
            
            # Create solver and run simulation
            solver = DiabetesODESolver(patient_data)
            result = solver.simulate(
                hours=params.simulation_hours,
                food_factor=params.food_factor,
                palmitic_factor=params.palmitic_factor,
                drug_dosage=params.drug_dosage,
                meal_times=params.meal_times,
                exercise_times=params.exercise_times
            )
            
            results.append(result)
        
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        print(f"Batch simulation error: {e}")
        raise HTTPException(status_code=400, detail=f"Batch simulation failed: {str(e)}")

@router.post("/sensitivity-analysis")
async def sensitivity_analysis(base_params: SimulationParams, 
                             parameter_ranges: dict = None):
    """Perform sensitivity analysis by varying parameters"""
    try:
        if parameter_ranges is None:
            # Default parameter ranges for sensitivity analysis
            parameter_ranges = {
                "food_factor": [0.5, 1.0, 1.5, 2.0],
                "drug_dosage": [0.0, 0.5, 1.0, 2.0],
                "exercise_times": [[], [14], [10, 16]]  # No exercise, afternoon, morning+evening
            }
        
        results = []
        
        for param_name, param_values in parameter_ranges.items():
            for value in param_values:
                # Create modified parameters
                modified_params = base_params.copy(deep=True)
                
                if param_name == "food_factor":
                    modified_params.food_factor = value
                elif param_name == "drug_dosage":
                    modified_params.drug_dosage = value
                elif param_name == "exercise_times":
                    modified_params.exercise_times = value
                
                # Run simulation
                solver = DiabetesODESolver(modified_params.patient_data)
                result = solver.simulate(
                    hours=modified_params.simulation_hours,
                    food_factor=modified_params.food_factor,
                    palmitic_factor=modified_params.palmitic_factor,
                    drug_dosage=modified_params.drug_dosage,
                    meal_times=modified_params.meal_times,
                    exercise_times=modified_params.exercise_times
                )
                
                results.append({
                    "parameter": param_name,
                    "value": value,
                    "result": result
                })
        
        return {"sensitivity_results": results}
        
    except Exception as e:
        print(f"Sensitivity analysis error: {e}")
        raise HTTPException(status_code=400, detail=f"Sensitivity analysis failed: {str(e)}")

@router.post("/intervention-analysis")
async def intervention_analysis(params: SimulationParams):
    """Analyze the effect of different interventions"""
    try:
        interventions = [
            {"name": "Baseline", "food_factor": 1.0, "drug_dosage": 0.0, "exercise_times": []},
            {"name": "Diet Control", "food_factor": 0.7, "drug_dosage": 0.0, "exercise_times": []},
            {"name": "Medication", "food_factor": 1.0, "drug_dosage": 1.0, "exercise_times": []},
            {"name": "Exercise", "food_factor": 1.0, "drug_dosage": 0.0, "exercise_times": [14]},
            {"name": "Combined", "food_factor": 0.8, "drug_dosage": 0.5, "exercise_times": [14]}
        ]
        
        results = []
        solver = DiabetesODESolver(params.patient_data)
        
        for intervention in interventions:
            result = solver.simulate(
                hours=params.simulation_hours,
                food_factor=intervention["food_factor"],
                palmitic_factor=params.palmitic_factor,
                drug_dosage=intervention["drug_dosage"],
                meal_times=params.meal_times,
                exercise_times=intervention["exercise_times"]
            )
            
            results.append({
                "intervention": intervention["name"],
                "parameters": intervention,
                "result": result
            })
        
        # Calculate intervention effectiveness
        baseline_a1c = results[0]["result"].a1c_estimate
        effectiveness = []
        
        for i, result in enumerate(results[1:], 1):
            a1c_reduction = baseline_a1c - result["result"].a1c_estimate
            effectiveness.append({
                "intervention": result["intervention"],
                "a1c_reduction": round(a1c_reduction, 2),
                "effectiveness_score": min(100, max(0, a1c_reduction * 20))  # Scale to 0-100
            })
        
        return {
            "intervention_results": results,
            "effectiveness_ranking": sorted(effectiveness, key=lambda x: x["a1c_reduction"], reverse=True)
        }
        
    except Exception as e:
        print(f"Intervention analysis error: {e}")
        raise HTTPException(status_code=400, detail=f"Intervention analysis failed: {str(e)}")

@router.post("/export-json/{simulation_id}")
async def export_simulation_json(simulation_id: str):
    """Export simulation result as JSON"""
    if simulation_id not in simulation_cache:
        raise HTTPException(status_code=404, detail="Simulation result not found")
    
    cached_result = simulation_cache[simulation_id]
    
    # Create export data
    export_data = {
        "simulation_metadata": {
            "simulation_id": simulation_id,
            "timestamp": cached_result["timestamp"].isoformat(),
            "software_version": "1.0.0"
        },
        "patient_data": cached_result["params"].patient_data.dict(),
        "simulation_parameters": cached_result["params"].dict(),
        "results": cached_result["result"].dict()
    }
    
    # Save to temporary file
    filename = f"simulation_{simulation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = f"/tmp/{filename}"
    
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    return FileResponse(
        filepath,
        media_type='application/json',
        filename=filename
    )

@router.post("/export-csv/{simulation_id}")
async def export_simulation_csv(simulation_id: str):
    """Export simulation result as CSV"""
    if simulation_id not in simulation_cache:
        raise HTTPException(status_code=404, detail="Simulation result not found")
    
    cached_result = simulation_cache[simulation_id]
    result = cached_result["result"]
    
    # Create CSV content
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Time (hours)", "Glucose (mg/dL)", "Insulin (pmol/L)", 
        "Glucagon (pg/mL)", "GLP-1 (pmol/L)", "Beta Cells", "Alpha Cells"
    ])
    
    # Write data
    for i in range(len(result.time_points)):
        writer.writerow([
            result.time_points[i],
            result.glucose[i],
            result.insulin[i],
            result.glucagon[i],
            result.glp1[i],
            result.beta_cells[i],
            result.alpha_cells[i]
        ])
    
    # Save to temporary file
    filename = f"simulation_{simulation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = f"/tmp/{filename}"
    
    with open(filepath, 'w', newline='') as f:
        f.write(output.getvalue())
    
    return FileResponse(
        filepath,
        media_type='text/csv',
        filename=filename
    )

@router.delete("/clear-cache")
async def clear_simulation_cache():
    """Clear all cached simulation results"""
    global simulation_cache
    count = len(simulation_cache)
    simulation_cache.clear()
    return {"message": f"Cleared {count} cached simulations"}

@router.get("/cache-status")
async def get_cache_status():
    """Get simulation cache status"""
    return {
        "cached_simulations": len(simulation_cache),
        "cache_size_mb": sum(len(str(v)) for v in simulation_cache.values()) / (1024 * 1024),
        "oldest_simulation": min(
            (v["timestamp"] for v in simulation_cache.values()),
            default=None
        )
    }

def _generate_comparison_metrics(results: list[SimulationResult]) -> dict:
    """Generate metrics for comparing multiple simulation results"""
    metrics = {
        "a1c_comparison": [r.a1c_estimate for r in results],
        "average_glucose": [r.simulation_summary.get("average_glucose", 0) for r in results],
        "glucose_variability": [r.simulation_summary.get("glucose_variability", 0) for r in results],
        "time_in_range": [r.simulation_summary.get("time_in_range", 0) for r in results],
        "diagnosis_comparison": [r.diagnosis for r in results]
    }
    
    # Calculate improvement scores
    baseline_a1c = metrics["a1c_comparison"][0]
    improvements = []
    
    for i, a1c in enumerate(metrics["a1c_comparison"][1:], 1):
        improvement = baseline_a1c - a1c
        improvements.append({
            "simulation_index": i,
            "a1c_improvement": round(improvement, 2),
            "percent_improvement": round((improvement / baseline_a1c) * 100, 1)
        })
    
    metrics["improvements"] = improvements
    return metrics

def _generate_comparison_recommendations(results: list[SimulationResult]) -> list[str]:
    """Generate recommendations based on comparison results"""
    recommendations = []
    
    if len(results) < 2:
        return recommendations
    
    baseline = results[0]
    best_result = min(results[1:], key=lambda r: r.a1c_estimate)
    
    a1c_improvement = baseline.a1c_estimate - best_result.a1c_estimate
    
    if a1c_improvement > 0.5:
        recommendations.append(f"Significant A1C improvement of {a1c_improvement:.1f}% observed with intervention")
    
    if best_result.simulation_summary.get("time_in_range", 0) > baseline.simulation_summary.get("time_in_range", 0):
        recommendations.append("Time in target glucose range improved with intervention")
    
    if best_result.diagnosis != baseline.diagnosis:
        recommendations.append(f"Diabetes classification improved from {baseline.diagnosis} to {best_result.diagnosis}")
    
    return recommendations