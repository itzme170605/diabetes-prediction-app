from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime

class SimulationParams(BaseModel):
    patient_data: Dict[str, Any]
    simulation_hours: int = Field(default=24, ge=6, le=168)
    food_factor: float = Field(default=1.0, ge=0.5, le=4.0)
    palmitic_factor: float = Field(default=1.0, ge=0.5, le=4.0)
    drug_dosage: float = Field(default=0.0, ge=0.0, le=2.0)
    show_optimal: bool = True
    meal_times: List[int] = [0, 6, 12, 18]
    meal_factors: List[float] = [1.0, 1.0, 2.0, 0.0]  # breakfast, lunch, dinner, snack
    drug_type: Optional[Literal['mounjaro', 'ozempic']] = None

class SimulationResult(BaseModel):
    time_points: List[float]
    glucose: List[float]
    insulin: List[float]
    glucagon: List[float]
    glp1: List[float]
    beta_cells: List[float]
    alpha_cells: List[float]
    glut2: List[float]
    glut4: List[float]
    palmitic_acid: List[float]
    oleic_acid: List[float]
    tnf_alpha: List[float]
    stored_glucose: List[float]
    total_energy: List[float]
    
    # Analysis results
    a1c_estimate: float
    diagnosis: str
    average_glucose: float
    max_glucose: float
    min_glucose: float
    glucose_variability: float
    time_in_range: float
    time_above_range: float
    time_below_range: float
    
    # Recommendations
    recommendations: List[str]
    risk_factors: List[str]
    
    # Metadata
    simulation_id: str
    timestamp: datetime
    patient_info: Dict[str, Any]

class MealPattern(BaseModel):
    name: str
    factors: List[float]
    description: str

class ComparisonResult(BaseModel):
    scenarios: List[Dict[str, Any]]
    comparison_metrics: List[Dict[str, Any]]
    recommendations: List[str]
    clinical_outcomes: List[str]