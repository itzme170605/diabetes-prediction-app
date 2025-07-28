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
    activity_level: Optional[str] = "moderate"  # "sedentary", "light", "moderate", "active"
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
    meal_times: List[float] = [0, 6, 12, 18]  # Hours when meals occur [breakfast, lunch, dinner, night_snack]
    meal_factors: List[float] = [1.0, 1.0, 2.0, 0.0]  # Individual meal multipliers
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
    
    @validator('palmitic_factor')
    def validate_palmitic_factor(cls, v):
        if v < 0.1 or v > 5.0:
            raise ValueError('Palmitic factor must be between 0.1 and 5.0')
        return v
    
    @validator('drug_dosage')
    def validate_drug_dosage(cls, v):
        if v < 0 or v > 5.0:
            raise ValueError('Drug dosage must be between 0 and 5.0')
        return v
    
    @validator('meal_times')
    def validate_meal_times(cls, v):
        if len(v) != 4:
            raise ValueError('meal_times must contain exactly 4 values')
        for time in v:
            if time < 0 or time >= 24:
                raise ValueError('Meal times must be between 0 and 23 hours')
        return v
    
    @validator('meal_factors')
    def validate_meal_factors(cls, v):
        if len(v) != 4:
            raise ValueError('meal_factors must contain exactly 4 values')
        for factor in v:
            if factor < 0 or factor > 5.0:
                raise ValueError('Each meal factor must be between 0 and 5.0')
        return v

class SimulationResult(BaseModel):
    time_points: List[float]
    glucose: List[float]
    insulin: List[float]
    glucagon: List[float]
    glp1: List[float]
    beta_cells: List[float]
    alpha_cells: List[float]
    # Additional variables from the paper
    glut2: List[float] = []
    glut4: List[float] = []
    palmitic_acid: List[float] = []
    oleic_acid: List[float] = []
    tnf_alpha: List[float] = []
    stored_glucose: List[float] = []
    
    optimal_glucose: Optional[List[float]] = None
    a1c_estimate: float
    diagnosis: str
    patient_info: dict
    simulation_summary: dict
    recommendations: List[str]
    risk_factors: List[str]
    
    # Enhanced clinical metrics
    glucose_metrics: dict = {}
    insulin_metrics: dict = {}
    hormone_balance: dict = {}
    
    def generate_summary(self):
        """Generate comprehensive simulation summary statistics"""
        if not self.glucose:
            return
        
        import statistics
        
        # Glucose statistics
        avg_glucose = round(statistics.mean(self.glucose), 1)
        max_glucose = round(max(self.glucose), 1)
        min_glucose = round(min(self.glucose), 1)
        glucose_variability = round(statistics.stdev(self.glucose), 1)
        
        # Time in range analysis (multiple ranges)
        time_in_tight_range = sum(1 for g in self.glucose if 70 <= g <= 140) / len(self.glucose) * 100  # Tight range
        time_in_range = sum(1 for g in self.glucose if 70 <= g <= 180) / len(self.glucose) * 100  # Standard range
        time_above_range = sum(1 for g in self.glucose if g > 180) / len(self.glucose) * 100
        time_below_range = sum(1 for g in self.glucose if g < 70) / len(self.glucose) * 100
        time_very_high = sum(1 for g in self.glucose if g > 250) / len(self.glucose) * 100
        
        # Glucose excursions
        post_meal_spikes = []
        if len(self.glucose) >= 12:  # At least 1 hour of data
            for i in range(0, len(self.glucose) - 12, 12):  # Check each hour
                hour_max = max(self.glucose[i:i+12])
                hour_min = min(self.glucose[i:i+12])
                post_meal_spikes.append(hour_max - hour_min)
        
        avg_excursion = round(statistics.mean(post_meal_spikes), 1) if post_meal_spikes else 0
        
        # Insulin metrics
        insulin_metrics = {}
        if self.insulin:
            insulin_metrics = {
                "average_insulin": round(statistics.mean(self.insulin), 1),
                "peak_insulin": round(max(self.insulin), 1),
                "insulin_variability": round(statistics.stdev(self.insulin), 1),
                "fasting_insulin": round(statistics.mean(self.insulin[:12]), 1) if len(self.insulin) >= 12 else 0
            }
        
        # Hormone balance metrics
        hormone_balance = {}
        if self.insulin and self.glucagon:
            # Calculate insulin:glucagon ratio
            avg_insulin = statistics.mean(self.insulin)
            avg_glucagon = statistics.mean(self.glucagon)
            hormone_balance = {
                "insulin_glucagon_ratio": round(avg_insulin / avg_glucagon, 3) if avg_glucagon > 0 else 0,
                "hormone_variability": round(statistics.stdev([i/g if g > 0 else 0 for i, g in zip(self.insulin, self.glucagon)]), 3)
            }
        
        # A1C calculation using more accurate formula: A1C = (avg_glucose + 46.7) / 28.7
        estimated_a1c = round((avg_glucose + 46.7) / 28.7, 2)
        
        self.simulation_summary = {
            "average_glucose": avg_glucose,
            "max_glucose": max_glucose,
            "min_glucose": min_glucose,
            "glucose_variability": glucose_variability,
            "time_in_tight_range": round(time_in_tight_range, 1),
            "time_in_range": round(time_in_range, 1),
            "time_above_range": round(time_above_range, 1),
            "time_below_range": round(time_below_range, 1),
            "time_very_high": round(time_very_high, 1),
            "average_excursion": avg_excursion,
            "estimated_a1c": estimated_a1c
        }
        
        self.glucose_metrics = {
            "dawn_phenomenon": self._calculate_dawn_phenomenon(),
            "post_meal_response": self._calculate_post_meal_response(),
            "glucose_stability": self._calculate_glucose_stability()
        }
        
        self.insulin_metrics = insulin_metrics
        self.hormone_balance = hormone_balance
    
    def _calculate_dawn_phenomenon(self):
        """Calculate dawn phenomenon (early morning glucose rise)"""
        if len(self.glucose) < 288:  # Less than 24 hours of data
            return 0
        
        # Compare 4-6 AM glucose with 2-4 AM glucose
        hours_4_6 = self.glucose[48:72]  # 4-6 AM (assuming 12 points per hour)
        hours_2_4 = self.glucose[24:48]  # 2-4 AM
        
        if hours_4_6 and hours_2_4:
            import statistics
            dawn_rise = statistics.mean(hours_4_6) - statistics.mean(hours_2_4)
            return round(dawn_rise, 1)
        return 0
    
    def _calculate_post_meal_response(self):
        """Calculate average post-meal glucose response"""
        if len(self.glucose) < 288:
            return {}
        
        # Assuming meals at hours 0, 6, 12 (breakfast, lunch, dinner)
        meal_responses = []
        meal_times = [0, 72, 144]  # 0, 6, 12 hours in 12-point intervals
        
        for meal_time in meal_times:
            if meal_time + 24 < len(self.glucose):  # 2 hours post-meal
                pre_meal = statistics.mean(self.glucose[meal_time:meal_time+6]) if meal_time >= 6 else self.glucose[0]
                post_meal_peak = max(self.glucose[meal_time:meal_time+24])
                meal_responses.append(post_meal_peak - pre_meal)
        
        if meal_responses:
            import statistics
            return {
                "average_post_meal_rise": round(statistics.mean(meal_responses), 1),
                "max_post_meal_rise": round(max(meal_responses), 1),
                "meal_response_variability": round(statistics.stdev(meal_responses), 1) if len(meal_responses) > 1 else 0
            }
        return {}
    
    def _calculate_glucose_stability(self):
        """Calculate glucose stability metrics"""
        if len(self.glucose) < 12:
            return {}
        
        import statistics
        
        # Calculate rate of change
        glucose_changes = [abs(self.glucose[i+1] - self.glucose[i]) for i in range(len(self.glucose)-1)]
        
        # Calculate mean amplitude of glucose excursions (MAGE)
        # Simplified MAGE calculation
        excursions = []
        threshold = statistics.stdev(self.glucose)
        
        for i in range(1, len(self.glucose)-1):
            if abs(self.glucose[i] - self.glucose[i-1]) > threshold:
                excursions.append(abs(self.glucose[i] - self.glucose[i-1]))
        
        mage = statistics.mean(excursions) if excursions else 0
        
        return {
            "mean_rate_of_change": round(statistics.mean(glucose_changes), 2),
            "max_rate_of_change": round(max(glucose_changes), 2),
            "mage": round(mage, 1),
            "stability_score": round(100 / (1 + mage), 1)  # Higher score = more stable
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

# Enhanced model for drug treatment analysis
class DrugTreatmentParams(BaseModel):
    """Parameters for drug treatment simulation"""
    drug_name: str = "GLP-1 Agonist"  # Mounjaro, Ozempic, etc.
    dosage_mg: float = 5.0  # Dosage in mg
    administration_schedule: str = "weekly"  # weekly, daily
    treatment_duration_weeks: int = 12
    lifestyle_modifications: dict = {
        "food_reduction": 0.85,  # 15% reduction
        "exercise_increase": 1.5,  # 50% increase
        "meal_timing_improvement": True
    }

class ComparisonAnalysis(BaseModel):
    """Model for comparative analysis results"""
    scenarios: List[dict]
    comparison_metrics: dict
    statistical_significance: dict
    clinical_recommendations: List[str]
    risk_benefit_analysis: dict