from fastapi import APIRouter, HTTPException
from models.diabetes_model import PatientData, ValidationResponse, HealthMetrics
from pydantic import BaseModel
from typing import List, Optional
import statistics

router = APIRouter()

class RiskAssessmentRequest(BaseModel):
    patient_data: PatientData

class LifestyleRecommendationRequest(BaseModel):
    patient_data: PatientData
    goals: Optional[List[str]] = ["weight_management", "glucose_control", "cardiovascular_health"]

class InterventionSimulationRequest(BaseModel):
    patient_data: PatientData
    intervention_type: str = "lifestyle"  # "lifestyle", "medication", "combined"
    target_weight_loss_percent: Optional[float] = 10.0
    exercise_increase_factor: Optional[float] = 2.0

@router.post("/validate", response_model=ValidationResponse)
async def validate_patient_data(patient_data: PatientData):
    """Validate patient data and return calculated parameters with warnings and recommendations"""
    try:
        # Calculate derived values
        patient_data.calculate_derived_values()
        
        warnings = []
        recommendations = []
        
        # Generate warnings based on data
        if patient_data.bmi >= 35:
            warnings.append("Severe obesity detected - significant health risks")
        elif patient_data.bmi >= 30:
            warnings.append("Obesity detected - increased diabetes and cardiovascular risk")
        elif patient_data.bmi >= 25:
            warnings.append("Overweight - consider weight management")
        elif patient_data.bmi < 18.5:
            warnings.append("Underweight - may indicate nutritional deficiency")
        
        if patient_data.age >= 65 and patient_data.activity_level == "sedentary":
            warnings.append("Sedentary lifestyle in elderly increases multiple health risks")
        
        if patient_data.smoking_status == "smoker":
            warnings.append("Smoking significantly increases diabetes and cardiovascular risk")
        
        if patient_data.fasting_glucose and patient_data.fasting_glucose >= 126:
            warnings.append("Fasting glucose indicates diabetes - medical evaluation needed")
        elif patient_data.fasting_glucose and patient_data.fasting_glucose >= 100:
            warnings.append("Elevated fasting glucose - prediabetes risk")
        
        if patient_data.a1c_level and patient_data.a1c_level >= 6.5:
            warnings.append("A1C indicates diabetes - medical management required")
        elif patient_data.a1c_level and patient_data.a1c_level >= 5.7:
            warnings.append("Elevated A1C indicates prediabetes")
        
        # Generate recommendations
        if patient_data.bmi >= 25:
            recommendations.append("Weight loss of 5-10% can significantly improve health outcomes")
        
        if patient_data.activity_level == "sedentary":
            recommendations.append("Increase physical activity to at least 150 minutes per week")
        
        if patient_data.diabetes_risk == "high":
            recommendations.append("High diabetes risk - lifestyle intervention and medical screening recommended")
        elif patient_data.diabetes_risk == "moderate":
            recommendations.append("Moderate diabetes risk - lifestyle modifications recommended")
        
        if patient_data.family_history:
            recommendations.append("Family history present - regular screening and preventive measures important")
        
        if patient_data.smoking_status == "smoker":
            recommendations.append("Smoking cessation is critical for reducing health risks")
        
        if not patient_data.medications and patient_data.diabetes_type == "diabetic":
            recommendations.append("Diabetes diagnosed - medical consultation for treatment options needed")
        
        return ValidationResponse(
            bmi=patient_data.bmi,
            bmi_category=patient_data.bmi_category,
            obesity_level=patient_data.obesity_level,
            diabetes_type=patient_data.diabetes_type,
            diabetes_risk=patient_data.diabetes_risk,
            valid=True,
            warnings=warnings,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/health-metrics")
async def calculate_health_metrics(patient_data: PatientData):
    """Calculate comprehensive health metrics"""
    try:
        patient_data.calculate_derived_values()
        
        # Calculate ideal weight range
        ideal_weight_range = HealthMetrics.calculate_ideal_weight(patient_data.height, patient_data.gender)
        
        # Calculate BMR and daily calorie needs
        bmr = HealthMetrics.calculate_bmr(patient_data.weight, patient_data.height, patient_data.age, patient_data.gender)
        daily_calories = HealthMetrics.calculate_daily_calories(bmr, patient_data.activity_level)
        
        # Calculate recommended exercise
        if patient_data.activity_level == "sedentary":
            recommended_exercise = 150  # Start with minimum recommendation
        elif patient_data.activity_level == "light":
            recommended_exercise = 200
        elif patient_data.activity_level == "moderate":
            recommended_exercise = 250
        else:
            recommended_exercise = 300
        
        # Cardiovascular risk assessment
        cv_risk_score = 0
        if patient_data.age >= 65:
            cv_risk_score += 3
        elif patient_data.age >= 45:
            cv_risk_score += 2
        elif patient_data.age >= 35:
            cv_risk_score += 1
        
        if patient_data.bmi >= 30:
            cv_risk_score += 2
        elif patient_data.bmi >= 25:
            cv_risk_score += 1
        
        if patient_data.smoking_status == "smoker":
            cv_risk_score += 3
        elif patient_data.smoking_status == "former_smoker":
            cv_risk_score += 1
        
        if patient_data.diabetes_type == "diabetic":
            cv_risk_score += 3
        elif patient_data.diabetes_type == "prediabetic":
            cv_risk_score += 1
        
        if patient_data.activity_level == "sedentary":
            cv_risk_score += 1
        
        if cv_risk_score >= 8:
            cardiovascular_risk = "high"
        elif cv_risk_score >= 5:
            cardiovascular_risk = "moderate"
        elif cv_risk_score >= 2:
            cardiovascular_risk = "low-moderate"
        else:
            cardiovascular_risk = "low"
        
        # Estimate metabolic age (simplified calculation)
        metabolic_age_adjustment = 0
        if patient_data.bmi >= 30:
            metabolic_age_adjustment += 10
        elif patient_data.bmi >= 25:
            metabolic_age_adjustment += 5
        
        if patient_data.activity_level == "sedentary":
            metabolic_age_adjustment += 5
        elif patient_data.activity_level == "active":
            metabolic_age_adjustment -= 5
        
        if patient_data.smoking_status == "smoker":
            metabolic_age_adjustment += 10
        
        metabolic_age = patient_data.age + metabolic_age_adjustment
        
        return {
            "patient_info": {
                "name": patient_data.name,
                "age": patient_data.age,
                "bmi": patient_data.bmi,
                "bmi_category": patient_data.bmi_category,
                "diabetes_risk": patient_data.diabetes_risk
            },
            "health_metrics": {
                "ideal_weight_range": ideal_weight_range,
                "current_weight": patient_data.weight,
                "weight_status": "underweight" if patient_data.weight < ideal_weight_range[0] else 
                                "overweight" if patient_data.weight > ideal_weight_range[1] else "normal",
                "bmr": bmr,
                "daily_calorie_needs": daily_calories,
                "recommended_exercise_minutes": recommended_exercise,
                "cardiovascular_risk": cardiovascular_risk,
                "metabolic_age": metabolic_age
            },
            "risk_factors": {
                "age_risk": patient_data.age >= 45,
                "weight_risk": patient_data.bmi >= 25,
                "family_history_risk": patient_data.family_history,
                "lifestyle_risk": patient_data.activity_level == "sedentary",
                "smoking_risk": patient_data.smoking_status == "smoker",
                "diabetes_risk_level": patient_data.diabetes_risk
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Health metrics calculation failed: {str(e)}")

@router.post("/risk-assessment")
async def comprehensive_risk_assessment(request: RiskAssessmentRequest):
    """Perform comprehensive diabetes and cardiovascular risk assessment"""
    try:
        patient_data = request.patient_data
        patient_data.calculate_derived_values()
        
        # Diabetes risk assessment (ADA risk calculator approach)
        diabetes_risk_score = 0
        
        # Age factor
        if patient_data.age >= 65:
            diabetes_risk_score += 3
        elif patient_data.age >= 45:
            diabetes_risk_score += 2
        elif patient_data.age >= 35:
            diabetes_risk_score += 1
        
        # BMI factor
        if patient_data.bmi >= 35:
            diabetes_risk_score += 4
        elif patient_data.bmi >= 30:
            diabetes_risk_score += 3
        elif patient_data.bmi >= 25:
            diabetes_risk_score += 2
        
        # Family history
        if patient_data.family_history:
            diabetes_risk_score += 2
        
        # Lifestyle factors
        if patient_data.activity_level == "sedentary":
            diabetes_risk_score += 1
        
        if patient_data.smoking_status == "smoker":
            diabetes_risk_score += 2
        elif patient_data.smoking_status == "former_smoker":
            diabetes_risk_score += 1
        
        # Clinical indicators
        if patient_data.fasting_glucose:
            if patient_data.fasting_glucose >= 126:
                diabetes_risk_score += 5  # Already diabetic
            elif patient_data.fasting_glucose >= 100:
                diabetes_risk_score += 3  # Prediabetic
        
        if patient_data.a1c_level:
            if patient_data.a1c_level >= 6.5:
                diabetes_risk_score += 5  # Already diabetic
            elif patient_data.a1c_level >= 5.7:
                diabetes_risk_score += 3  # Prediabetic
        
        # Determine diabetes risk level
        if diabetes_risk_score >= 10:
            diabetes_risk_level = "very_high"
            diabetes_risk_percentage = "80-90%"
        elif diabetes_risk_score >= 7:
            diabetes_risk_level = "high"
            diabetes_risk_percentage = "60-80%"
        elif diabetes_risk_score >= 4:
            diabetes_risk_level = "moderate"
            diabetes_risk_percentage = "30-60%"
        elif diabetes_risk_score >= 2:
            diabetes_risk_level = "low_moderate"
            diabetes_risk_percentage = "10-30%"
        else:
            diabetes_risk_level = "low"
            diabetes_risk_percentage = "<10%"
        
        # Cardiovascular risk assessment (simplified Framingham approach)
        cv_risk_score = 0
        
        # Age and gender
        if patient_data.gender.lower() in ['male', 'm']:
            if patient_data.age >= 65:
                cv_risk_score += 5
            elif patient_data.age >= 55:
                cv_risk_score += 4
            elif patient_data.age >= 45:
                cv_risk_score += 3
        else:  # Female
            if patient_data.age >= 65:
                cv_risk_score += 4
            elif patient_data.age >= 55:
                cv_risk_score += 3
            elif patient_data.age >= 45:
                cv_risk_score += 2
        
        # Diabetes
        if patient_data.diabetes_type == "diabetic":
            cv_risk_score += 4
        elif patient_data.diabetes_type == "prediabetic":
            cv_risk_score += 2
        
        # BMI/Obesity
        if patient_data.bmi >= 30:
            cv_risk_score += 3
        elif patient_data.bmi >= 25:
            cv_risk_score += 1
        
        # Smoking
        if patient_data.smoking_status == "smoker":
            cv_risk_score += 4
        elif patient_data.smoking_status == "former_smoker":
            cv_risk_score += 1
        
        # Physical activity
        if patient_data.activity_level == "sedentary":
            cv_risk_score += 2
        elif patient_data.activity_level == "active":
            cv_risk_score -= 1
        
        # Determine cardiovascular risk
        if cv_risk_score >= 12:
            cv_risk_level = "very_high"
            cv_risk_percentage = ">30%"
        elif cv_risk_score >= 8:
            cv_risk_level = "high"
            cv_risk_percentage = "20-30%"
        elif cv_risk_score >= 5:
            cv_risk_level = "moderate"
            cv_risk_percentage = "10-20%"
        elif cv_risk_score >= 2:
            cv_risk_level = "low_moderate"
            cv_risk_percentage = "5-10%"
        else:
            cv_risk_level = "low"
            cv_risk_percentage = "<5%"
        
        # Generate specific recommendations
        risk_recommendations = []
        
        if diabetes_risk_level in ["high", "very_high"]:
            risk_recommendations.append("Immediate medical evaluation for diabetes screening recommended")
            risk_recommendations.append("Lifestyle intervention program strongly recommended")
        elif diabetes_risk_level == "moderate":
            risk_recommendations.append("Annual diabetes screening recommended")
            risk_recommendations.append("Lifestyle modifications to prevent diabetes progression")
        
        if cv_risk_level in ["high", "very_high"]:
            risk_recommendations.append("Cardiovascular risk reduction strategies essential")
            risk_recommendations.append("Consider medical consultation for heart disease prevention")
        
        if patient_data.bmi >= 30:
            risk_recommendations.append("Weight loss of 5-10% can significantly reduce both diabetes and cardiovascular risk")
        
        if patient_data.activity_level == "sedentary":
            risk_recommendations.append("Increase physical activity to 150+ minutes/week moderate exercise")
        
        if patient_data.smoking_status == "smoker":
            risk_recommendations.append("Smoking cessation is the single most important risk reduction strategy")
        
        return {
            "patient_summary": {
                "name": patient_data.name,
                "age": patient_data.age,
                "bmi": patient_data.bmi,
                "current_diabetes_status": patient_data.diabetes_type
            },
            "diabetes_risk": {
                "risk_level": diabetes_risk_level,
                "risk_percentage": diabetes_risk_percentage,
                "risk_score": diabetes_risk_score,
                "primary_risk_factors": _identify_primary_diabetes_risk_factors(patient_data)
            },
            "cardiovascular_risk": {
                "risk_level": cv_risk_level,
                "risk_percentage": cv_risk_percentage,
                "risk_score": cv_risk_score,
                "primary_risk_factors": _identify_primary_cv_risk_factors(patient_data)
            },
            "recommendations": risk_recommendations,
            "screening_schedule": _generate_screening_schedule(diabetes_risk_level, cv_risk_level)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Risk assessment failed: {str(e)}")

@router.post("/lifestyle-recommendations")
async def generate_lifestyle_recommendations(request: LifestyleRecommendationRequest):
    """Generate personalized lifestyle recommendations"""
    try:
        patient_data = request.patient_data
        goals = request.goals
        patient_data.calculate_derived_values()
        
        recommendations = {
            "nutrition": [],
            "exercise": [],
            "lifestyle": [],
            "monitoring": [],
            "medical": []
        }
        
        # Nutrition recommendations
        if "weight_management" in goals and patient_data.bmi >= 25:
            calorie_reduction = 500 if patient_data.bmi >= 30 else 300
            recommendations["nutrition"].append(f"Reduce daily calories by {calorie_reduction} for gradual weight loss")
            recommendations["nutrition"].append("Focus on low glycemic index foods")
            recommendations["nutrition"].append("Increase fiber intake to 25-30g daily")
        
        if "glucose_control" in goals:
            recommendations["nutrition"].append("Eat regular meals at consistent times")
            recommendations["nutrition"].append("Limit refined carbohydrates and added sugars")
            recommendations["nutrition"].append("Include protein with each meal to stabilize glucose")
            if patient_data.meal_frequency < 3:
                recommendations["nutrition"].append("Increase meal frequency to 3 regular meals daily")
        
        # Exercise recommendations
        if patient_data.activity_level == "sedentary":
            recommendations["exercise"].append("Start with 10-15 minutes daily walking, gradually increase")
            recommendations["exercise"].append("Target 150 minutes moderate exercise weekly")
        elif patient_data.activity_level == "light":
            recommendations["exercise"].append("Increase to 30 minutes moderate exercise 5 days/week")
            recommendations["exercise"].append("Add 2 days resistance training weekly")
        else:
            recommendations["exercise"].append("Add high-intensity interval training 1-2x weekly")
            recommendations["exercise"].append("Consider exercise variety to maintain engagement")
        
        if "glucose_control" in goals:
            recommendations["exercise"].append("Exercise after meals to improve glucose uptake")
            recommendations["exercise"].append("Include both aerobic and resistance training")
        
        # Lifestyle recommendations
        if patient_data.smoking_status == "smoker":
            recommendations["lifestyle"].append("Smoking cessation is critical - consider cessation programs")
            recommendations["lifestyle"].append("Avoid secondhand smoke exposure")
        
        if "cardiovascular_health" in goals:
            recommendations["lifestyle"].append("Manage stress through relaxation techniques")
            recommendations["lifestyle"].append("Ensure 7-9 hours quality sleep nightly")
            recommendations["lifestyle"].append("Limit alcohol consumption")
        
        # Monitoring recommendations
        if patient_data.diabetes_type in ["prediabetic", "diabetic"]:
            recommendations["monitoring"].append("Monitor blood glucose as recommended by healthcare provider")
            recommendations["monitoring"].append("Track A1C levels every 3-6 months")
        
        if patient_data.bmi >= 25:
            recommendations["monitoring"].append("Weekly weight monitoring")
            recommendations["monitoring"].append("Track waist circumference monthly")
        
        recommendations["monitoring"].append("Blood pressure monitoring if cardiovascular risk factors present")
        
        # Medical recommendations
        if patient_data.diabetes_type == "diabetic" and not patient_data.medications:
            recommendations["medical"].append("Consult healthcare provider about diabetes medications")
        
        if patient_data.diabetes_risk == "high":
            recommendations["medical"].append("Annual comprehensive diabetes screening")
        
        if patient_data.bmi >= 35:
            recommendations["medical"].append("Consider medical weight management consultation")
        
        # Generate specific meal plan suggestions
        meal_plan = _generate_sample_meal_plan(patient_data, goals)
        
        # Generate exercise plan
        exercise_plan = _generate_exercise_plan(patient_data)
        
        return {
            "patient_profile": {
                "name": patient_data.name,
                "current_status": {
                    "bmi": patient_data.bmi,
                    "diabetes_type": patient_data.diabetes_type,
                    "activity_level": patient_data.activity_level
                },
                "goals": goals
            },
            "recommendations": recommendations,
            "sample_meal_plan": meal_plan,
            "exercise_plan": exercise_plan,
            "expected_outcomes": _generate_expected_outcomes(patient_data, goals)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lifestyle recommendations failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "User data service is running"}

def _identify_primary_diabetes_risk_factors(patient_data: PatientData) -> List[str]:
    """Identify primary diabetes risk factors"""
    risk_factors = []
    
    if patient_data.age >= 45:
        risk_factors.append(f"Age {patient_data.age} (≥45 increases risk)")
    
    if patient_data.bmi >= 30:
        risk_factors.append(f"Obesity (BMI {patient_data.bmi})")
    elif patient_data.bmi >= 25:
        risk_factors.append(f"Overweight (BMI {patient_data.bmi})")
    
    if patient_data.family_history:
        risk_factors.append("Family history of diabetes")
    
    if patient_data.activity_level == "sedentary":
        risk_factors.append("Sedentary lifestyle")
    
    if patient_data.smoking_status == "smoker":
        risk_factors.append("Current smoking")
    
    return risk_factors

def _identify_primary_cv_risk_factors(patient_data: PatientData) -> List[str]:
    """Identify primary cardiovascular risk factors"""
    risk_factors = []
    
    if patient_data.diabetes_type == "diabetic":
        risk_factors.append("Diabetes")
    elif patient_data.diabetes_type == "prediabetic":
        risk_factors.append("Prediabetes")
    
    if patient_data.bmi >= 30:
        risk_factors.append("Obesity")
    
    if patient_data.smoking_status == "smoker":
        risk_factors.append("Smoking")
    
    if patient_data.activity_level == "sedentary":
        risk_factors.append("Physical inactivity")
    
    if patient_data.age >= 55:
        risk_factors.append("Advanced age")
    
    return risk_factors

def _generate_screening_schedule(diabetes_risk_level: str, cv_risk_level: str) -> dict:
    """Generate appropriate screening schedule"""
    schedule = {}
    
    # Diabetes screening
    if diabetes_risk_level in ["high", "very_high"]:
        schedule["diabetes_screening"] = "Every 6 months"
        schedule["a1c_testing"] = "Every 3-6 months"
    elif diabetes_risk_level == "moderate":
        schedule["diabetes_screening"] = "Annually"
        schedule["a1c_testing"] = "Annually if prediabetic"
    else:
        schedule["diabetes_screening"] = "Every 3 years after age 45"
    
    # Cardiovascular screening
    if cv_risk_level in ["high", "very_high"]:
        schedule["blood_pressure"] = "Monthly monitoring"
        schedule["lipid_panel"] = "Every 6 months"
        schedule["cardiovascular_exam"] = "Annually"
    elif cv_risk_level == "moderate":
        schedule["blood_pressure"] = "Every 3 months"
        schedule["lipid_panel"] = "Annually"
    else:
        schedule["blood_pressure"] = "Every 6 months"
        schedule["lipid_panel"] = "Every 2 years"
    
    return schedule

def _generate_sample_meal_plan(patient_data: PatientData, goals: List[str]) -> dict:
    """Generate sample meal plan based on patient needs"""
    meal_plan = {
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "snacks": []
    }
    
    if "glucose_control" in goals:
        meal_plan["breakfast"] = [
            "Steel-cut oats with berries and nuts",
            "Greek yogurt with fiber-rich fruit",
            "Vegetable omelet with whole grain toast"
        ]
        meal_plan["lunch"] = [
            "Grilled chicken salad with mixed vegetables",
            "Lentil soup with whole grain roll",
            "Quinoa bowl with roasted vegetables"
        ]
        meal_plan["dinner"] = [
            "Baked salmon with roasted vegetables",
            "Lean protein with steamed broccoli and brown rice",
            "Turkey and vegetable stir-fry"
        ]
    
    if "weight_management" in goals and patient_data.bmi >= 25:
        meal_plan["snacks"] = [
            "Apple with small amount of nuts",
            "Vegetable sticks with hummus",
            "Greek yogurt (plain, small portion)"
        ]
    
    return meal_plan

def _generate_exercise_plan(patient_data: PatientData) -> dict:
    """Generate personalized exercise plan"""
    plan = {
        "weekly_structure": {},
        "progression": {},
        "precautions": []
    }
    
    if patient_data.activity_level == "sedentary":
        plan["weekly_structure"] = {
            "week_1_2": "10 minutes walking daily",
            "week_3_4": "15 minutes walking daily + 1 day light resistance",
            "week_5_8": "20-30 minutes moderate exercise 3-4 days/week"
        }
        plan["precautions"] = ["Start slowly", "Listen to your body", "Consult doctor if chest pain or shortness of breath"]
    
    elif patient_data.activity_level == "light":
        plan["weekly_structure"] = {
            "aerobic": "30 minutes moderate exercise 4-5 days/week",
            "resistance": "2 days/week full body strength training",
            "flexibility": "Daily stretching or yoga"
        }
    
    else:
        plan["weekly_structure"] = {
            "aerobic": "45-60 minutes moderate-vigorous exercise 5-6 days/week",
            "resistance": "3 days/week strength training",
            "high_intensity": "1-2 days/week HIIT sessions"
        }
    
    if patient_data.diabetes_type in ["prediabetic", "diabetic"]:
        plan["precautions"].append("Monitor blood glucose before and after exercise")
        plan["precautions"].append("Exercise after meals when possible")
    
    return plan

def _generate_expected_outcomes(patient_data: PatientData, goals: List[str]) -> dict:
    """Generate expected outcomes from lifestyle changes"""
    outcomes = {}
    
    if "weight_management" in goals and patient_data.bmi >= 25:
        target_weight_loss = min(patient_data.weight * 0.1, patient_data.weight - 70)  # 10% or to reasonable minimum
        outcomes["weight_loss"] = {
            "target": f"{target_weight_loss:.1f} kg in 6 months",
            "weekly_rate": "0.5-1 kg per week initially",
            "health_benefits": "Improved insulin sensitivity, reduced diabetes risk"
        }
    
    if "glucose_control" in goals:
        if patient_data.diabetes_type == "prediabetic":
            outcomes["glucose_improvement"] = {
                "a1c_reduction": "0.5-1.0% reduction expected",
                "timeline": "3-6 months",
                "diabetes_prevention": "50-60% risk reduction with lifestyle changes"
            }
        elif patient_data.diabetes_type == "diabetic":
            outcomes["glucose_improvement"] = {
                "a1c_reduction": "1.0-2.0% reduction possible",
                "timeline": "3-6 months",
                "medication_adjustment": "May allow medication reduction with doctor approval"
            }
    
    if "cardiovascular_health" in goals:
        outcomes["cardiovascular_benefits"] = {
            "blood_pressure": "5-10 mmHg reduction expected",
            "cholesterol": "10-15% improvement in lipid profile",
            "overall_risk": "20-30% cardiovascular risk reduction"
        }
    
    return outcomes