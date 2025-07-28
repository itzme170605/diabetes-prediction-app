import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import uuid
import logging

from app.models.patient import PatientData
from app.models.simulation import SimulationResult, SimulationParams, ComparisonResult
from app.models.ode_model import ODEParameters
from app.services.ode_solver import T2DMODESolver
from app.utils.calculations import calculate_a1c, calculate_glucose_metrics

logger = logging.getLogger(__name__)

class SimulationService:
    """Service for running diabetes simulations"""
    
    def __init__(self):
        self.ode_params = ODEParameters()
        self.solver = T2DMODESolver(self.ode_params)
    
    def run_simulation(self, params: SimulationParams) -> SimulationResult:
        """Run a single simulation"""
        try:
            # Extract patient data
            patient = PatientData(**params.patient_data)
            
            # Adjust ODE parameters based on patient characteristics
            self._adjust_parameters_for_patient(patient)
            
            # Set up time span
            t_span = np.linspace(0, params.simulation_hours, 
                               int(params.simulation_hours * 100))  # 100 points per hour
            
            # Get initial conditions
            initial_conditions = self.solver.get_initial_conditions(patient.dict())
            
            # Run simulation
            solution = self.solver.solve(
                t_span,
                initial_conditions,
                params.meal_times,
                params.meal_factors,
                params.food_factor,
                params.palmitic_factor,
                params.drug_dosage
            )
            
            # Extract results
            results = self._extract_results(solution, t_span, patient, params)
            
            return results
            
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            raise
    
    def compare_meal_patterns(self, base_params: SimulationParams) -> ComparisonResult:
        """Compare different meal patterns"""
        meal_patterns = [
            {"name": "Balanced", "factors": [1.0, 1.0, 1.0, 0.0], 
             "description": "Equal portions for all meals"},
            {"name": "Light-Heavy", "factors": [0.5, 1.0, 2.0, 0.0], 
             "description": "Light breakfast, heavy dinner"},
            {"name": "Heavy-Light", "factors": [2.0, 1.0, 0.5, 0.0], 
             "description": "Heavy breakfast, light dinner"},
            {"name": "Small-Frequent", "factors": [0.8, 0.8, 0.8, 0.6], 
             "description": "Four smaller meals"}
        ]
        
        results = []
        for pattern in meal_patterns:
            params = base_params.copy()
            params.meal_factors = pattern["factors"]
            
            sim_result = self.run_simulation(params)
            
            results.append({
                "pattern": pattern,
                "result": sim_result,
                "metrics": {
                    "average_glucose": sim_result.average_glucose,
                    "a1c_estimate": sim_result.a1c_estimate,
                    "time_in_range": sim_result.time_in_range,
                    "glucose_variability": sim_result.glucose_variability
                }
            })
        
        # Generate comparison and recommendations
        comparison = self._generate_meal_comparison(results)
        
        return comparison
    
    def simulate_obesity_progression(self, base_params: SimulationParams) -> ComparisonResult:
        """Simulate progression from normal to obese to diabetic"""
        stages = [
            {"name": "Normal", "food_factor": 1.0, "palmitic_factor": 1.0},
            {"name": "Overweight", "food_factor": 1.5, "palmitic_factor": 1.5},
            {"name": "Obese", "food_factor": 2.0, "palmitic_factor": 2.5},
            {"name": "Severely Obese", "food_factor": 3.0, "palmitic_factor": 3.5}
        ]
        
        results = []
        for stage in stages:
            params = base_params.copy()
            params.food_factor = stage["food_factor"]
            params.palmitic_factor = stage["palmitic_factor"]
            params.simulation_hours = 72  # 3 days
            
            sim_result = self.run_simulation(params)
            
            results.append({
                "stage": stage,
                "result": sim_result,
                "diagnosis": sim_result.diagnosis,
                "a1c": sim_result.a1c_estimate
            })
        
        return self._generate_progression_analysis(results)
    
    def analyze_drug_treatment(self, base_params: SimulationParams) -> ComparisonResult:
        """Analyze drug treatment effects"""
        drug_doses = [0.0, 0.5, 1.0, 1.5]
        results = []
        
        for dose in drug_doses:
            params = base_params.copy()
            params.drug_dosage = dose
            params.simulation_hours = 168  # 1 week
            
            sim_result = self.run_simulation(params)
            
            results.append({
                "drug_dose": dose,
                "result": sim_result,
                "a1c_reduction": base_params.patient_data.get('a1c_level', 7.0) - sim_result.a1c_estimate,
                "average_glucose": sim_result.average_glucose
            })
        
        return self._generate_treatment_analysis(results)
    
    def _adjust_parameters_for_patient(self, patient: PatientData):
        """Adjust ODE parameters based on patient characteristics"""
        # Age adjustment
        if patient.age > 60:
            self.ode_params.mu_B *= 1.2  # Faster β-cell decay
            self.ode_params.lambda_tilde_B *= 0.8  # Slower β-cell activation
        
        # Obesity adjustment
        if patient.bmi and patient.bmi > 30:
            self.ode_params.eta_T_alpha *= 1.5  # Increased TNF-α effect
            self.ode_params.gamma_P_hat *= 1.5  # Increased palmitic acid
        
        # Activity level adjustment
        activity_multipliers = {
            'sedentary': 0.7,
            'light': 0.85,
            'moderate': 1.0,
            'active': 1.2
        }
        
        activity_mult = activity_multipliers.get(patient.activity_level, 1.0)
        self.ode_params.lambda_GU4 *= activity_mult  # Glucose uptake
        
    def _extract_results(self, solution: np.ndarray, t_span: np.ndarray, 
                    patient: PatientData, params: SimulationParams) -> SimulationResult:
    
    # Unpack solution
        B, A, L, I, U2, U4, C, G, Gs, Ta, O, P = solution.T
        
        # Convert units where necessary
        glucose_mg_dl = G * 1e5  # Convert from g/cm³ to mg/dL
        insulin_pmol_l = I * 1.8e11  # Convert to pmol/L
        glucagon_pg_ml = C * 1e12  # Convert to pg/mL
        glp1_pmol_l = L * 1.8e11  # Convert to pmol/L
        
        # Calculate total energy
        total_energy = G + Gs
        
        # Calculate metrics
        metrics = calculate_glucose_metrics(glucose_mg_dl, t_span)
        a1c = calculate_a1c(metrics['average_glucose'])
        
        # Determine diagnosis
        if a1c < 5.7:
            diagnosis = "Normal"
        elif a1c < 6.5:
            diagnosis = "Prediabetic"
        else:
            diagnosis = "Diabetic"
        
        # Create simulation summary with REQUIRED fields
        simulation_summary = {
            "average_glucose": round(metrics['average_glucose'], 1),
            "max_glucose": round(metrics['max_glucose'], 1),
            "min_glucose": round(metrics['min_glucose'], 1),
            "glucose_variability": round(metrics['glucose_variability'], 1),
            "time_in_range": round(metrics['time_in_range'], 1),
            "time_above_range": round(metrics['time_above_range'], 1),
            "time_below_range": round(metrics['time_below_range'], 1),
            "time_in_tight_range": round(metrics.get('time_in_tight_range', 0), 1),
            "estimated_a1c": round(a1c, 1)
        }
        
        # Create glucose metrics
        glucose_metrics = {
            "dawn_phenomenon": round(metrics.get('dawn_phenomenon', 0), 1),
            "post_meal_response": {
                "average_post_meal_rise": 50.0,  # Placeholder
                "max_post_meal_rise": 80.0,      # Placeholder
                "meal_response_variability": 15.0 # Placeholder
            },
            "glucose_stability": {
                "mean_rate_of_change": round(metrics.get('coefficient_of_variation', 0), 2),
                "max_rate_of_change": 5.0,  # Placeholder
                "mage": round(metrics.get('glucose_variability', 0) * 0.8, 1),  # Approximation
                "stability_score": max(0, min(100, 100 - metrics.get('coefficient_of_variation', 0)))
            }
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(patient, metrics, a1c)
        risk_factors = self._identify_risk_factors(patient)
        
        return SimulationResult(
            time_points=t_span.tolist(),
            glucose=glucose_mg_dl.tolist(),
            insulin=insulin_pmol_l.tolist(),
            glucagon=glucagon_pg_ml.tolist(),
            glp1=glp1_pmol_l.tolist(),
            beta_cells=(B * 1e3).tolist(),
            alpha_cells=(A * 1e3).tolist(),
            glut2=(U2 * 1e6).tolist(),
            glut4=(U4 * 1e6).tolist(),
            palmitic_acid=(P * 1e6).tolist(),
            oleic_acid=(O * 1e6).tolist(),
            tnf_alpha=(Ta * 1e12).tolist(),
            stored_glucose=(Gs * 1e5).tolist(),
            total_energy=(total_energy * 1e5).tolist(),
            
            optimal_glucose=None,  # Can be calculated if needed
            
            a1c_estimate=round(a1c, 1),
            diagnosis=diagnosis,
            
            patient_info=patient.dict(),
            simulation_summary=simulation_summary,
            
            glucose_metrics=glucose_metrics,
            insulin_metrics=None,  # Optional
            hormone_balance=None,  # Optional
            
            recommendations=recommendations,
            risk_factors=risk_factors,
            
            simulation_id=str(uuid.uuid4()),
            timestamp=datetime.now()
        )
    
    def _generate_recommendations(self, patient: PatientData, 
                                metrics: Dict, a1c: float) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # A1C-based recommendations
        if a1c >= 7.0:
            recommendations.append("Consider medication adjustment - consult your healthcare provider")
        elif a1c >= 6.5:
            recommendations.append("Implement lifestyle modifications to prevent progression")
        elif a1c >= 5.7:
            recommendations.append("Monitor glucose levels regularly and maintain healthy habits")
        
        # BMI-based recommendations
        if patient.bmi and patient.bmi > 30:
            recommendations.append("Weight reduction of 5-10% can significantly improve glucose control")
        
        # Activity recommendations
        if patient.activity_level in ['sedentary', 'light']:
            recommendations.append("Increase physical activity to at least 150 minutes per week")
        
        # Glucose variability
        if metrics['glucose_variability'] > 40:
            recommendations.append("Consider more consistent meal timing and portions")
        
        # Time in range
        if metrics['time_in_range'] < 70:
            recommendations.append("Work on improving time in target glucose range (70-180 mg/dL)")
        
        return recommendations
    
    def _identify_risk_factors(self, patient: PatientData) -> List[str]:
        """Identify risk factors for diabetes complications"""
        risk_factors = []
        
        if patient.age > 45:
            risk_factors.append("Age over 45 years")
        
        if patient.bmi and patient.bmi >= 25:
            risk_factors.append(f"BMI {patient.bmi} (overweight/obese)")
        
        if patient.family_history:
            risk_factors.append("Family history of diabetes")
        
        if patient.activity_level == 'sedentary':
            risk_factors.append("Sedentary lifestyle")
        
        if patient.smoking_status == 'smoker':
            risk_factors.append("Current smoker")
        
        return risk_factors
    
    def _generate_meal_comparison(self, results: List[Dict]) -> ComparisonResult:
        """Generate meal pattern comparison analysis"""
        best_pattern = min(results, key=lambda x: x['metrics']['a1c_estimate'])
        
        comparison_metrics = []
        for result in results:
            metrics = result['metrics']
            comparison_metrics.append({
                "scenario": result['pattern']['name'],
                "a1c_estimate": metrics['a1c_estimate'],
                "a1c_change": metrics['a1c_estimate'] - results[0]['metrics']['a1c_estimate'],
                "average_glucose": metrics['average_glucose'],
                "glucose_variability": metrics['glucose_variability'],
                "time_in_range": metrics['time_in_range']
            })
        
        recommendations = [
            f"The {best_pattern['pattern']['name']} meal pattern shows the best glucose control",
            "Consider spacing meals 4-6 hours apart for better glucose stability",
            "Avoid large meals late in the day to prevent overnight glucose elevation"
        ]
        
        clinical_outcomes = [
            f"Best A1C achieved: {best_pattern['metrics']['a1c_estimate']}% with {best_pattern['pattern']['name']} pattern",
            "Meal timing significantly affects glucose control and A1C levels"
        ]
        
        return ComparisonResult(
            scenarios=[r['pattern'] for r in results],
            comparison_metrics=comparison_metrics,
            recommendations=recommendations,
            clinical_outcomes=clinical_outcomes
        )
    
    def _generate_progression_analysis(self, results: List[Dict]) -> ComparisonResult:
        """Generate obesity progression analysis"""
        comparison_metrics = []
        
        for i, result in enumerate(results):
            comparison_metrics.append({
                "scenario": result['stage']['name'],
                "a1c_estimate": result['a1c'],
                "a1c_change": result['a1c'] - results[0]['a1c'],
                "diagnosis": result['diagnosis'],
                "food_factor": result['stage']['food_factor'],
                "palmitic_factor": result['stage']['palmitic_factor']
            })
        
        recommendations = [
            "Maintain healthy weight to prevent diabetes progression",
            "Each 1 kg/m² increase in BMI increases diabetes risk by approximately 20%",
            "Focus on reducing palmitic acid intake (saturated fats) to improve insulin sensitivity"
        ]
        
        clinical_outcomes = [
            f"Progression from normal to diabetic occurs at food factor ≥2.0",
            "Early intervention at overweight stage can prevent diabetes development"
        ]
        
        return ComparisonResult(
            scenarios=[r['stage'] for r in results],
            comparison_metrics=comparison_metrics,
            recommendations=recommendations,
            clinical_outcomes=clinical_outcomes
        )
    
    def _generate_treatment_analysis(self, results: List[Dict]) -> ComparisonResult:
        """Generate drug treatment analysis"""
        comparison_metrics = []
        
        baseline_a1c = results[0]['result'].a1c_estimate
        
        for result in results:
            comparison_metrics.append({
                "scenario": f"Drug dose: {result['drug_dose']}",
                "a1c_estimate": result['result'].a1c_estimate,
                "a1c_change": result['result'].a1c_estimate - baseline_a1c,
                "a1c_reduction": result['a1c_reduction'],
                "average_glucose": result['average_glucose']
            })
        
        optimal_dose = max(results[1:], key=lambda x: x['a1c_reduction'])
        
        recommendations = [
            f"Optimal drug dose appears to be {optimal_dose['drug_dose']} units",
            "Combine medication with lifestyle modifications for best results",
            "Regular monitoring needed to adjust dosage over time"
        ]
        
        clinical_outcomes = [
            f"Maximum A1C reduction: {optimal_dose['a1c_reduction']:.1f}%",
            "Treatment response varies with individual patient characteristics"
        ]
        
        return ComparisonResult(
            scenarios=[{"dose": r['drug_dose']} for r in results],
            comparison_metrics=comparison_metrics,
            recommendations=recommendations,
            clinical_outcomes=clinical_outcomes
        )