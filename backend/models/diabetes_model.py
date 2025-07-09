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

class SimulationParams(BaseModel):
    patient_data: PatientData
    simulation_hours: int = 24
    food_factor: float = 1.0
    palmitic_factor: float = 1.0
    drug_dosage: float = 0.0
    show_optimal: bool = True

class SimulationResult(BaseModel):
    time_points: List[float]
    glucose: List[float]
    insulin: List[float]
    glucagon: List[float]
    glp1: List[float]
    optimal_glucose: Optional[List[float]] = None
    a1c_estimate: float
    diagnosis: str