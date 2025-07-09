from fastapi import APIRouter, HTTPException
from models.diabetes_model import PatientData

router = APIRouter()

@router.post("/validate")
async def validate_patient_data(patient_data: PatientData):
    """Validate patient data and return calculated parameters"""
    try:
        # Calculate BMI
        height_m = patient_data.height / 100
        bmi = patient_data.weight / (height_m ** 2)
        
        # Determine obesity level if not provided
        if not patient_data.obesity_level:
            if bmi < 25:
                obesity_level = "normal"
            elif bmi < 30:
                obesity_level = "overweight"
            else:
                obesity_level = "obese"
        else:
            obesity_level = patient_data.obesity_level
            
        # Estimate diabetes type if not provided
        diabetes_type = patient_data.diabetes_type
        if not diabetes_type and patient_data.fasting_glucose:
            if patient_data.fasting_glucose < 100:
                diabetes_type = "normal"
            elif patient_data.fasting_glucose < 126:
                diabetes_type = "prediabetic"
            else:
                diabetes_type = "diabetic"
                
        return {
            "bmi": round(bmi, 1),
            "obesity_level": obesity_level,
            "diabetes_type": diabetes_type,
            "valid": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "User data service is running"}