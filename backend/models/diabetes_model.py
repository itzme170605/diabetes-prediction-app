from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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

class MealSchedule(BaseModel):
    """Define meal timing and intensity"""
    breakfast_time: float = 0.0  # hours from start
    breakfast_factor: float = 1.0  # multiplier for food intake
    lunch_time: float = 6.0
    lunch_factor: float = 1.0
    dinner_time: float = 12.0
    dinner_factor: float = 2.0  # Typically larger dinner
    
class DrugSchedule(BaseModel):
    """Drug administration schedule"""
    drug_type: str = "GLP-1_agonist"  # "Mounjaro" or "Ozempic"
    initial_dose: float = 0.0
    dose_increase_week: int = 4  # Week to increase dose
    increased_dose: float = 0.0
    
class SimulationParams(BaseModel):
    patient_data: PatientData
    simulation_hours: int = 24
    simulation_days: Optional[int] = None  # For multi-day simulations
    
    # Meal-specific parameters
    meal_schedule: Optional[MealSchedule] = MealSchedule()
    
    # Global food factors (can be overridden by meal schedule)
    food_factor: float = 1.0  # Global multiplier
    palmitic_factor: float = 1.0  # Obesity-related palmitic acid
    
    # Drug parameters
    drug_dosage: float = 0.0  # Simple dose
    drug_schedule: Optional[DrugSchedule] = None  # Advanced scheduling
    
    # Simulation options
    show_optimal: bool = True
    include_all_variables: bool = False  # Show all 12 ODE variables
    
class ExtendedSimulationResult(BaseModel):
    """Extended result including all ODE variables"""
    time_points: List[float]
    
    # Primary variables (always included)
    glucose: List[float]  # mg/dL
    insulin: List[float]  # pmol/L
    glucagon: List[float]  # pg/mL
    glp1: List[float]  # pmol/L
    
    # Additional ODE variables (optional)
    alpha_cells: Optional[List[float]] = None
    beta_cells: Optional[List[float]] = None
    glut2: Optional[List[float]] = None
    glut4: Optional[List[float]] = None
    stored_glucose: Optional[List[float]] = None
    oleic_acid: Optional[List[float]] = None
    palmitic_acid: Optional[List[float]] = None
    tnf_alpha: Optional[List[float]] = None
    
    # Analysis results
    optimal_glucose: Optional[List[float]] = None
    a1c_estimate: float
    diagnosis: str
    avg_glucose: float  # Average glucose over simulation
    glucose_variability: float  # Standard deviation
    time_in_range: float  # Percentage of time 70-140 mg/dL
    
class SimulationResult(BaseModel):
    """Simplified result for backward compatibility"""
    time_points: List[float]
    glucose: List[float]
    insulin: List[float]
    glucagon: List[float]
    glp1: List[float]
    optimal_glucose: Optional[List[float]] = None
    a1c_estimate: float
    diagnosis: str