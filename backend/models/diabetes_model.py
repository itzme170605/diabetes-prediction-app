from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import math

class PatientData(BaseModel):
    name: str
    age: int
    weight: float  # kg
    height: float  # cm
    gender: str
    diabetes_type: Optional[str] = None  # "normal", "prediabetic", "diabetic"
    obesity_level: Optional[str] = None  # "normal", "overweight", "obese"
    meal_frequency: int = 3
    sugar_intake: Optional[float] = None  # g/day
    exercise_level: Optional[str] = "moderate"
    medications: List[str] = []
    fasting_glucose: Optional[float] = None  # mg/dL
    a1c_level: Optional[float] = None  # %
    activity_level: Optional[str] = "sedentary"  # "sedentary", "light", "moderate", "active"
    smoking_status: Optional[str] = "non_smoker"  # "non_smoker", "smoker", "former_smoker"
    family_history: Optional[bool] = False
    
    # Derived fields (calculated automatically)
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None
    diabetes_risk: Optional[str] = None
    
    @validator('age')
    def validate_age(cls, v):
        if v < 1 or v > 120:
            raise ValueError('Age must be between 1 and 120')
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        if v < 1 or v > 500:
            raise ValueError('Weight must be between 1 and 500 kg')
        return v
    
    @validator('height')
    def validate_height(cls, v):
        if v < 30 or v > 250:
            raise ValueError('Height must be between 30 and 250 cm')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v.lower() not in ['male', 'female', 'm', 'f']:
            raise ValueError('Gender must be male, female, m, or f')
        return v.lower()
    
    def calculate_derived_values(self):
        """Calculate BMI and other derived values"""
        # Calculate BMI
        height_m = self.height / 100
        self.bmi = round(self.weight / (height_m ** 2), 1)
        
        # Determine BMI category
        if self.bmi < 18.5:
            self.bmi_category = "underweight"
            self.obesity_level = "underweight"
        elif self.bmi < 25:
            self.bmi_category = "normal"
            self.obesity_level = "normal"
        elif self.bmi < 30:
            self.bmi_category = "overweight"
            self.obesity_level = "overweight"
        else:
            self.bmi_category = "obese"
            self.obesity_level = "obese"
        
        # Estimate diabetes type if not provided
        if not self.diabetes_type and self.fasting_glucose:
            if self.fasting_glucose < 100:
                self.diabetes_type = "normal"
            elif self.fasting_glucose < 126:
                self.diabetes_type = "prediabetic"
            else:
                self.diabetes_type = "diabetic"
        elif not self.diabetes_type and self.a1c_level:
            if self.a1c_level < 5.7:
                self.diabetes_type = "normal"
            elif self.a1c_level < 6.5:
                self.diabetes_type = "prediabetic"
            else:
                self.diabetes_type = "diabetic"
        elif not self.diabetes_type:
            self.diabetes_type = "normal"  # Default
        
        # Calculate diabetes risk
        self.diabetes_risk = self._calculate_diabetes_risk()
    
    def _calculate_diabetes_risk(self) -> str:
        """Calculate diabetes risk based on multiple factors"""
        risk_score = 0
        
        # Age factor
        if self.age >= 45:
            risk_score += 2
        elif self.age >= 35:
            risk_score += 1
        
        # BMI factor
        if self.bmi >= 30:
            risk_score += 3
        elif self.bmi >= 25:
            risk_score += 2
        
        # Family history
        if self.family_history:
            risk_score += 2
        
        # Activity level
        if self.activity_level == "sedentary":
            risk_score += 1
        
        # Smoking
        if self.smoking_status == "smoker":
            risk_score += 1
        
        # Current diabetes status
        if self.diabetes_type == "diabetic":
            return "high"
        elif self.diabetes_type == "prediabetic":
            return "moderate"
        
        # Risk assessment
        if risk_score >= 6:
            return "high"
        elif risk_score >= 3:
            return "moderate"
        else:
            return "low"

class SimulationParams(BaseModel):
    patient_data: PatientData
    simulation_hours: int = 24
    food_factor: float = 1.0
    palmitic_factor: float = 1.0
    drug_dosage: float = 0.0
    show_optimal: bool = True
    meal_times: List[float] = [0, 6, 12, 18]  # Hours when meals occur
    exercise_times: List[float] = []  # Hours when exercise occurs
    
    @validator('simulation_hours')
    def validate_simulation_hours(cls, v):
        if v < 1 or v > 168:  # Max 1 week
            raise ValueError('Simulation hours must be between 1 and 168')
        return v
    
    @validator('food_factor')
    def validate_food_factor(cls, v):
        if v < 0.1 or v > 5.0:
            raise ValueError('Food factor must be between 0.1 and 5.0')
        return v

class SimulationResult(BaseModel):
    time_points: List[float]
    glucose: List[float]
    insulin: List[float]
    glucagon: List[float]
    glp1: List[float]
    beta_cells: List[float]
    alpha_cells: List[float]
    optimal_glucose: Optional[List[float]] = None
    a1c_estimate: float
    diagnosis: str
    patient_info: dict
    simulation_summary: dict
    recommendations: List[str]
    risk_factors: List[str]
    
    def generate_summary(self):
        """Generate simulation summary statistics"""
        if not self.glucose:
            return
        
        import statistics
        
        # Glucose statistics
        avg_glucose = round(statistics.mean(self.glucose), 1)
        max_glucose = round(max(self.glucose), 1)
        min_glucose = round(min(self.glucose), 1)
        glucose_variability = round(statistics.stdev(self.glucose), 1)
        
        # Time in range (70-180 mg/dL for general population)
        time_in_range = sum(1 for g in self.glucose if 70 <= g <= 180) / len(self.glucose) * 100
        time_above_range = sum(1 for g in self.glucose if g > 180) / len(self.glucose) * 100
        time_below_range = sum(1 for g in self.glucose if g < 70) / len(self.glucose) * 100
        
        self.simulation_summary = {
            "average_glucose": avg_glucose,
            "max_glucose": max_glucose,
            "min_glucose": min_glucose,
            "glucose_variability": glucose_variability,
            "time_in_range": round(time_in_range, 1),
            "time_above_range": round(time_above_range, 1),
            "time_below_range": round(time_below_range, 1),
            "estimated_a1c": self.a1c_estimate
        }

class ValidationResponse(BaseModel):
    bmi: float
    bmi_category: str
    obesity_level: str
    diabetes_type: str
    diabetes_risk: str
    valid: bool
    warnings: List[str] = []
    recommendations: List[str] = []

class HealthMetrics(BaseModel):
    """Additional health metrics that can be calculated"""
    ideal_weight_range: tuple
    daily_calorie_needs: float
    recommended_exercise_minutes: int
    cardiovascular_risk: str
    metabolic_age: Optional[int] = None
    
    @staticmethod
    def calculate_ideal_weight(height_cm: float, gender: str) -> tuple:
        """Calculate ideal weight range using multiple formulas"""
        height_m = height_cm / 100
        
        # Healthy BMI range (18.5-24.9)
        min_weight = 18.5 * (height_m ** 2)
        max_weight = 24.9 * (height_m ** 2)
        
        return (round(min_weight, 1), round(max_weight, 1))
    
    @staticmethod
    def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation"""
        if gender.lower() in ['male', 'm']:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        return round(bmr, 0)
    
    @staticmethod
    def calculate_daily_calories(bmr: float, activity_level: str) -> float:
        """Calculate daily calorie needs based on activity level"""
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.375)
        return round(bmr * multiplier, 0)