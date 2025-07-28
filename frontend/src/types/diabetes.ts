export interface PatientData {
  name: string;
  age: number;
  weight: number;
  height: number;
  gender: string;
  diabetes_type?: string | null;
  meal_frequency: number;
  medications: string[];
  fasting_glucose?: number | null;
  a1c_level?: number | null;
  activity_level?: string;
  smoking_status?: string;
  family_history?: boolean;
  
  // Calculated fields
  bmi?: number | null;
  bmi_category?: string | null;
}

export interface SimulationParams {
  patient_data: PatientData;
  simulation_hours: number;
  food_factor: number;
  palmitic_factor: number;
  drug_dosage: number;
  show_optimal: boolean;
  meal_times: number[];
  meal_factors: number[];
}

export interface SimulationResult {
  time_points: number[];
  glucose: number[];
  insulin: number[];
  glucagon: number[];
  glp1: number[];
  beta_cells: number[];
  alpha_cells: number[];
  
  optimal_glucose?: number[];
  a1c_estimate: number;
  diagnosis: string;
  
  patient_info: {
    name: string;
    age: number;
    gender: string;
    bmi: number;
    bmi_category: string;
  };
  
  simulation_summary: {
    average_glucose: number;
    max_glucose: number;
    min_glucose: number;
    glucose_variability: number;
    time_in_range: number;
    time_in_tight_range?: number;
    time_above_range: number;
    time_below_range: number;
    estimated_a1c: number;
  };
  
  glucose_metrics?: {
    dawn_phenomenon?: number;
    glucose_stability?: {
      stability_score: number;
      mean_rate_of_change: number;
      mage: number;
    };
  };
  
  recommendations: string[];
  risk_factors: string[];
}

export interface ComparisonResult {
  comparison_metrics: Array<{
    scenario: string;
    a1c_estimate: number;
    a1c_change: number;
    average_glucose: number;
    glucose_variability: number;
    time_in_range: number;
  }>;
  recommendations: string[];
  clinical_outcomes: string[];
}