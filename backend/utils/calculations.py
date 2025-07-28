import numpy as np
from typing import Dict, List, Tuple

def calculate_a1c(average_glucose_mg_dl: float) -> float:
    """
    Calculate A1C from average glucose using the formula:
    A1C = (average_glucose + 46.7) / 28.7
    """
    return (average_glucose_mg_dl + 46.7) / 28.7

def calculate_glucose_metrics(glucose_values: np.ndarray, 
                            time_points: np.ndarray) -> Dict[str, float]:
    """Calculate various glucose metrics"""
    
    # Basic statistics
    average_glucose = np.mean(glucose_values)
    max_glucose = np.max(glucose_values)
    min_glucose = np.min(glucose_values)
    glucose_variability = np.std(glucose_values)
    
    # Time in range calculations
    total_time = len(glucose_values)
    time_in_range = np.sum((glucose_values >= 70) & (glucose_values <= 180)) / total_time * 100
    time_above_range = np.sum(glucose_values > 180) / total_time * 100
    time_below_range = np.sum(glucose_values < 70) / total_time * 100
    time_in_tight_range = np.sum((glucose_values >= 70) & (glucose_values <= 140)) / total_time * 100
    
    # Additional metrics
    coefficient_of_variation = (glucose_variability / average_glucose) * 100 if average_glucose > 0 else 0
    
    # Dawn phenomenon (early morning glucose rise)
    if len(time_points) > 24:  # If we have more than 24 hours of data
        morning_indices = [i for i, t in enumerate(time_points) if 4 <= (t % 24) <= 8]
        if morning_indices:
            dawn_glucose = np.mean([glucose_values[i] for i in morning_indices])
            night_indices = [i for i, t in enumerate(time_points) if 0 <= (t % 24) <= 4]
            if night_indices:
                night_glucose = np.mean([glucose_values[i] for i in night_indices])
                dawn_phenomenon = dawn_glucose - night_glucose
            else:
                dawn_phenomenon = 0
        else:
            dawn_phenomenon = 0
    else:
        dawn_phenomenon = 0
    
    return {
        'average_glucose': average_glucose,
        'max_glucose': max_glucose,
        'min_glucose': min_glucose,
        'glucose_variability': glucose_variability,
        'time_in_range': time_in_range,
        'time_above_range': time_above_range,
        'time_below_range': time_below_range,
        'time_in_tight_range': time_in_tight_range,
        'coefficient_of_variation': coefficient_of_variation,
        'dawn_phenomenon': dawn_phenomenon
    }

def calculate_insulin_sensitivity_index(fasting_glucose: float, 
                                      fasting_insulin: float) -> float:
    """Calculate HOMA-IR (insulin resistance index)"""
    # HOMA-IR = (glucose in mg/dL × insulin in μU/mL) / 405
    # Convert insulin from pmol/L to μU/mL (1 pmol/L = 0.144 μU/mL)
    insulin_uU_ml = fasting_insulin * 0.144
    return (fasting_glucose * insulin_uU_ml) / 405

def estimate_beta_cell_function(fasting_insulin: float, 
                               fasting_glucose: float) -> float:
    """Estimate beta cell function using HOMA-B"""
    # HOMA-B = (20 × insulin in μU/mL) / (glucose in mg/dL - 63)
    insulin_uU_ml = fasting_insulin * 0.144
    if fasting_glucose > 63:
        return (20 * insulin_uU_ml) / (fasting_glucose - 63)
    return 0

def calculate_glucose_management_indicator(a1c: float) -> float:
    """Calculate GMI from A1C"""
    # GMI = 3.31 + 0.02392 × mean glucose in mg/dL
    mean_glucose = (a1c * 28.7) - 46.7
    return 3.31 + 0.02392 * mean_glucose