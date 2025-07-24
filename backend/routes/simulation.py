from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from models.diabetes_model import PatientData, SimulationParams, SimulationResult, HealthMetrics, DrugTreatmentParams, ComparisonAnalysis
from utils.ode_solver import DiabetesODESolver
import traceback
import json
import os
from datetime import datetime
import uuid
from typing import List, Optional
from pydantic import BaseModel
import statistics

router = APIRouter()

# In-memory storage for simulation results
simulation_cache = {}

@router.post("/run", response_model=SimulationResult)
async def run_simulation(params: SimulationParams):
    """Run diabetes simulation with enhanced meal parameters"""
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
            meal_factors=params.meal_factors
        )
        
        # Store result in cache
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

@router.post("/compare-meals")
async def compare_meal_scenarios(base_params: SimulationParams):
    """Compare different meal scenarios"""
    try:
        # Define different meal scenarios
        scenarios = [
            {
                "name": "Balanced Meals",
                "meal_factors": [1.0, 1.0, 1.0, 0.0],
                "description": "Equal portions for all meals"
            },
            {
                "name": "Light Breakfast, Heavy Dinner",
                "meal_factors": [0.5, 1.0, 2.0, 0.0],
                "description": "Traditional eating pattern"
            },
            {
                "name": "Heavy Breakfast, Light Dinner",
                "meal_factors": [2.0, 1.0, 0.5, 0.0],
                "description": "Diabetes-friendly pattern"
            },
            {
                "name": "Frequent Small Meals",
                "meal_factors": [0.8, 0.8, 0.8, 0.6],
                "description": "Four smaller meals including evening snack"
            }
        ]
        
        results = []
        solver = DiabetesODESolver(base_params.patient_data)
        
        for scenario in scenarios:
            result = solver.simulate(
                hours=base_params.simulation_hours,
                food_factor=base_params.food_factor,
                palmitic_factor=base_params.palmitic_factor,
                drug_dosage=base_params.drug_dosage,
                meal_times=base_params.meal_times,
                meal_factors=scenario["meal_factors"]
            )
            
            results.append({
                "scenario": scenario["name"],
                "description": scenario["description"],
                "meal_factors": scenario["meal_factors"],
                "result": result
            })
        
        # Calculate comparison metrics
        baseline_a1c = results[0]["result"].a1c_estimate
        comparison_metrics = []
        
        for i, result in enumerate(results):
            a1c_change = result["result"].a1c_estimate - baseline_a1c
            avg_glucose = result["result"].simulation_summary.get("average_glucose", 0)
            glucose_variability = result["result"].simulation_summary.get("glucose_variability", 0)
            
            comparison_metrics.append({
                "scenario": result["scenario"],
                "a1c_estimate": result["result"].a1c_estimate,
                "a1c_change": round(a1c_change, 2),
                "average_glucose": avg_glucose,
                "glucose_variability": glucose_variability,
                "time_in_range": result["result"].simulation_summary.get("time_in_range", 0)
            })
        
        return {
            "comparison_results": results,
            "comparison_metrics": comparison_metrics,
            "recommendations": _generate_meal_recommendations(comparison_metrics)
        }
        
    except Exception as e:
        print(f"Meal comparison error: {e}")
        raise HTTPException(status_code=400, detail=f"Meal comparison failed: {str(e)}")

@router.post("/obesity-progression")
async def simulate_obesity_progression(base_params: SimulationParams):
    """Simulate progression from normal to obese state as in the paper"""
    try:
        # Simulate different obesity levels as shown in Figure 7 of the paper
        obesity_scenarios = [
            {
                "name": "Normal Health (Factor=1, 0γ̂P)",
                "food_factor": 1.0,
                "palmitic_factor": 1.0,
                "description": "Healthy baseline"
            },
            {
                "name": "Mild Overeating (Factor=2, 1γ̂P)",
                "food_factor": 2.0,
                "palmitic_factor": 2.0,
                "description": "Early obesity development"
            },
            {
                "name": "Moderate Obesity (Factor=3, 2γ̂P)",
                "food_factor": 3.0,
                "palmitic_factor": 3.0,
                "description": "Established obesity"
            },
            {
                "name": "Severe Obesity (Factor=4, 3γ̂P)",
                "food_factor": 4.0,
                "palmitic_factor": 4.0,
                "description": "Severe obesity with high diabetes risk"
            },
            {
                "name": "Morbid Obesity (Factor=4, 4γ̂P)",
                "food_factor": 4.0,
                "palmitic_factor": 5.0,
                "description": "Morbid obesity with very high diabetes risk"
            }
        ]
        
        results = []
        
        for scenario in obesity_scenarios:
            # Create modified patient data for different obesity levels
            modified_patient = base_params.patient_data.copy(deep=True)
            
            # Adjust BMI based on scenario (simplified approach)
            if scenario["food_factor"] >= 4.0:
                modified_patient.weight = modified_patient.weight * 1.4  # Simulate obesity
            elif scenario["food_factor"] >= 3.0:
                modified_patient.weight = modified_patient.weight * 1.3
            elif scenario["food_factor"] >= 2.0:
                modified_patient.weight = modified_patient.weight * 1.2
            
            modified_patient.calculate_derived_values()
            
            solver = DiabetesODESolver(modified_patient)
            result = solver.simulate(
                hours=base_params.simulation_hours,
                food_factor=scenario["food_factor"],
                palmitic_factor=scenario["palmitic_factor"],
                drug_dosage=base_params.drug_dosage,
                meal_times=base_params.meal_times,
                meal_factors=base_params.meal_factors
            )
            
            results.append({
                "scenario": scenario["name"],
                "description": scenario["description"],
                "food_factor": scenario["food_factor"],
                "palmitic_factor": scenario["palmitic_factor"],
                "patient_bmi": modified_patient.bmi,
                "result": result
            })
        
        return {
            "progression_results": results,
            "progression_summary": _generate_progression_summary(results)
        }
        
    except Exception as e:
        print(f"Obesity progression simulation error: {e}")
        raise HTTPException(status_code=400, detail=f"Obesity progression simulation failed: {str(e)}")

@router.post("/drug-treatment-analysis")
async def analyze_drug_treatment(base_params: SimulationParams, treatment_params: Optional[DrugTreatmentParams] = None):
    """Analyze drug treatment effects as shown in Figures 8-9 of the paper"""
    try:
        if treatment_params is None:
            treatment_params = DrugTreatmentParams()
        
        # Drug dosage scenarios from the paper
        treatment_scenarios = [
            {
                "name": "No Treatment",
                "drug_dosage": 0.0,
                "food_reduction": 1.0,
                "description": "Baseline without treatment"
            },
            {
                "name": "Low Dose GLP-1 Agonist",
                "drug_dosage": 0.5,  # Normalized dosage
                "food_reduction": 0.85,  # 15% food reduction
                "description": "Low dose GLP-1 agonist with modest lifestyle changes"
            },
            {
                "name": "Medium Dose GLP-1 Agonist",
                "drug_dosage": 1.0,  # Normalized dosage
                "food_reduction": 0.80,  # 20% food reduction
                "description": "Medium dose GLP-1 agonist with moderate lifestyle changes"
            },
            {
                "name": "High Dose GLP-1 Agonist",
                "drug_dosage": 1.5,  # Normalized dosage
                "food_reduction": 0.75,  # 25% food reduction
                "description": "High dose GLP-1 agonist with significant lifestyle changes"
            }
        ]
        
        results = []
        
        # Use patient data with potential obesity
        treatment_patient = base_params.patient_data.copy(deep=True)
        if treatment_patient.bmi < 30:  # If not already obese, simulate obesity for treatment analysis
            treatment_patient.weight = treatment_patient.weight * 1.3
            treatment_patient.diabetes_type = "prediabetic" if treatment_patient.diabetes_type == "normal" else treatment_patient.diabetes_type
        treatment_patient.calculate_derived_values()
        
        solver = DiabetesODESolver(treatment_patient)
        
        for scenario in treatment_scenarios:
            result = solver.simulate(
                hours=base_params.simulation_hours,
                food_factor=base_params.food_factor * scenario["food_reduction"],
                palmitic_factor=base_params.palmitic_factor * 0.8,  # Weight loss effect
                drug_dosage=scenario["drug_dosage"],
                meal_times=base_params.meal_times,
                meal_factors=base_params.meal_factors
            )
            
            results.append({
                "treatment": scenario["name"],
                "description": scenario["description"],
                "drug_dosage": scenario["drug_dosage"],
                "food_reduction": scenario["food_reduction"],
                "result": result
            })
        
        # Calculate treatment effectiveness
        baseline_a1c = results[0]["result"].a1c_estimate
        treatment_analysis = []
        
        for result in results[1:]:  # Skip baseline
            a1c_reduction = baseline_a1c - result["result"].a1c_estimate
            percent_reduction = (a1c_reduction / baseline_a1c) * 100 if baseline_a1c > 0 else 0
            
            treatment_analysis.append({
                "treatment": result["treatment"],
                "a1c_before": baseline_a1c,
                "a1c_after": result["result"].a1c_estimate,
                "a1c_reduction": round(a1c_reduction, 2),
                "percent_reduction": round(percent_reduction, 1),
                "diagnosis_change": f"{results[0]['result'].diagnosis} → {result['result'].diagnosis}"
            })
        
        return {
            "treatment_results": results,
            "treatment_analysis": treatment_analysis,
            "clinical_outcomes": _generate_clinical_outcomes(treatment_analysis)
        }
        
    except Exception as e:
        print(f"Drug treatment analysis error: {e}")
        raise HTTPException(status_code=400, detail=f"Drug treatment analysis failed: {str(e)}")

@router.post("/sensitivity-analysis")
async def sensitivity_analysis(base_params: SimulationParams, parameter_ranges: dict = None):
    """Perform sensitivity analysis by varying parameters"""
    try:
        if parameter_ranges is None:
            # Default parameter ranges for sensitivity analysis
            parameter_ranges = {
                "food_factor": [0.5, 1.0, 1.5, 2.0],
                "drug_dosage": [0.0, 0.5, 1.0, 2.0],
                "meal_factors": [
                    [1.0, 1.0, 1.0, 0.0],  # Balanced
                    [0.5, 1.0, 2.0, 0.0],  # Light breakfast, heavy dinner
                    [2.0, 1.0, 0.5, 0.0],  # Heavy breakfast, light dinner
                ]
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
                elif param_name == "meal_factors":
                    modified_params.meal_factors = value
                
                # Run simulation
                solver = DiabetesODESolver(modified_params.patient_data)
                result = solver.simulate(
                    hours=modified_params.simulation_hours,
                    food_factor=modified_params.food_factor,
                    palmitic_factor=modified_params.palmitic_factor,
                    drug_dosage=modified_params.drug_dosage,
                    meal_times=modified_params.meal_times,
                    meal_factors=modified_params.meal_factors
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
            {"name": "Baseline", "food_factor": 1.0, "drug_dosage": 0.0, "meal_factors": [1.0, 1.0, 1.0, 0.0]},
            {"name": "Diet Control", "food_factor": 0.7, "drug_dosage": 0.0, "meal_factors": [1.0, 1.0, 1.0, 0.0]},
            {"name": "Medication", "food_factor": 1.0, "drug_dosage": 1.0, "meal_factors": [1.0, 1.0, 1.0, 0.0]},
            {"name": "Meal Timing", "food_factor": 1.0, "drug_dosage": 0.0, "meal_factors": [2.0, 1.0, 0.5, 0.0]},
            {"name": "Combined", "food_factor": 0.8, "drug_dosage": 0.5, "meal_factors": [1.5, 1.0, 0.8, 0.0]}
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
                meal_factors=intervention["meal_factors"]
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

@router.post("/batch-simulate")
async def batch_simulate(simulation_list: list[SimulationParams]):
    """Run multiple simulations for comparison or analysis"""
    try:
        results = []
        
        for params in simulation_list:
            patient_data = params.patient_data
            patient_data.calculate_derived_values()
            
            solver = DiabetesODESolver(patient_data)
            result = solver.simulate(
                hours=params.simulation_hours,
                food_factor=params.food_factor,
                palmitic_factor=params.palmitic_factor,
                drug_dosage=params.drug_dosage,
                meal_times=params.meal_times,
                meal_factors=params.meal_factors
            )
            
            results.append(result)
        
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        print(f"Batch simulation error: {e}")
        raise HTTPException(status_code=400, detail=f"Batch simulation failed: {str(e)}")

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
            "software_version": "2.0.0"
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
        "Glucagon (pg/mL)", "GLP-1 (pmol/L)", "Beta Cells", "Alpha Cells",
        "GLUT-2", "GLUT-4", "Palmitic Acid", "Oleic Acid", "TNF-α", "Stored Glucose"
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
            result.alpha_cells[i],
            result.glut2[i] if result.glut2 else 0,
            result.glut4[i] if result.glut4 else 0,
            result.palmitic_acid[i] if result.palmitic_acid else 0,
            result.oleic_acid[i] if result.oleic_acid else 0,
            result.tnf_alpha[i] if result.tnf_alpha else 0,
            result.stored_glucose[i] if result.stored_glucose else 0
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

def _generate_meal_recommendations(comparison_metrics):
    """Generate recommendations based on meal comparison"""
    recommendations = []
    
    # Find best scenario for glucose control
    best_scenario = min(comparison_metrics, key=lambda x: x["glucose_variability"])
    recommendations.append(f"For best glucose stability, consider the '{best_scenario['scenario']}' eating pattern")
    
    # Find best scenario for A1C
    best_a1c = min(comparison_metrics, key=lambda x: x["a1c_estimate"])
    if best_a1c != best_scenario:
        recommendations.append(f"For lowest A1C, the '{best_a1c['scenario']}' pattern shows best results")
    
    # Time in range recommendations
    best_tir = max(comparison_metrics, key=lambda x: x["time_in_range"])
    recommendations.append(f"The '{best_tir['scenario']}' pattern provides {best_tir['time_in_range']:.1f}% time in target range")
    
    return recommendations

def _generate_progression_summary(results):
    """Generate summary of obesity progression"""
    summary = {
        "a1c_progression": [r["result"].a1c_estimate for r in results],
        "diagnosis_progression": [r["result"].diagnosis for r in results],
        "bmi_progression": [r["patient_bmi"] for r in results],
        "risk_assessment": []
    }
    
    for i, result in enumerate(results):
        if result["result"].diagnosis == "Diabetic":
            summary["risk_assessment"].append(f"Scenario {i+1}: High diabetes risk - A1C {result['result'].a1c_estimate}%")
        elif result["result"].diagnosis == "Prediabetic":
            summary["risk_assessment"].append(f"Scenario {i+1}: Moderate diabetes risk - A1C {result['result'].a1c_estimate}%")
        else:
            summary["risk_assessment"].append(f"Scenario {i+1}: Normal glucose tolerance - A1C {result['result'].a1c_estimate}%")
    
    return summary

def _generate_clinical_outcomes(treatment_analysis):
    """Generate clinical outcomes assessment"""
    outcomes = []
    
    for analysis in treatment_analysis:
        if analysis["a1c_reduction"] >= 1.0:
            outcomes.append(f"{analysis['treatment']}: Excellent response - clinically significant A1C reduction")
        elif analysis["a1c_reduction"] >= 0.5:
            outcomes.append(f"{analysis['treatment']}: Good response - meaningful A1C improvement")
        elif analysis["a1c_reduction"] >= 0.2:
            outcomes.append(f"{analysis['treatment']}: Modest response - some A1C improvement")
        else:
            outcomes.append(f"{analysis['treatment']}: Limited response - minimal A1C change")
    
    return outcomes

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
            "percent_improvement": round((improvement / baseline_a1c) * 100, 1) if baseline_a1c > 0 else 0
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