from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime

class PatientData(BaseModel):
    # Basic Information
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=1, le=120)
    weight: float = Field(..., gt=20, lt=300)  # kg
    height: float = Field(..., gt=100, lt=250)  # cm
    gender: Literal['male', 'female']
    
    # Medical Information
    diabetes_type: Optional[Literal['normal', 'prediabetic', 'diabetic']] = None
    obesity_level: Optional[Literal['normal', 'overweight', 'obese']] = None
    meal_frequency: int = Field(default=3, ge=1, le=10)
    sugar_intake: Optional[float] = None
    exercise_level: Optional[Literal['sedentary', 'light', 'moderate', 'active']] = 'moderate'
    medications: List[str] = []
    fasting_glucose: Optional[float] = Field(None, ge=50, le=400)  # mg/dL
    a1c_level: Optional[float] = Field(None, ge=3, le=15)  # %
    activity_level: Optional[Literal['sedentary', 'light', 'moderate', 'active']] = 'moderate'
    smoking_status: Optional[Literal['non_smoker', 'former_smoker', 'smoker']] = 'non_smoker'
    family_history: bool = False
    
    # Calculated fields
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None
    diabetes_risk: Optional[str] = None
    
    @validator('bmi', always=True)
    def calculate_bmi(cls, v, values):
        if 'weight' in values and 'height' in values:
            height_m = values['height'] / 100
            return round(values['weight'] / (height_m ** 2), 1)
        return v
    
    @validator('bmi_category', always=True)
    def calculate_bmi_category(cls, v, values):
        if 'bmi' in values and values['bmi']:
            bmi = values['bmi']
            if bmi < 18.5:
                return 'Underweight'
            elif bmi < 25:
                return 'Normal'
            elif bmi < 30:
                return 'Overweight'
            else:
                return 'Obese'
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "age": 45,
                "weight": 85,
                "height": 175,
                "gender": "male",
                "diabetes_type": "prediabetic",
                "medications": ["Metformin"],
                "fasting_glucose": 110,
                "a1c_level": 6.2,
                "family_history": True
            }
        }