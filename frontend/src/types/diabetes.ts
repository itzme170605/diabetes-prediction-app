// src/types/diabetes.ts
export interface PatientData {
  name: string;
  age: number;
  weight: number;
  height: number;
  gender: string;
  diabetes_type?: string | null;
  obesity_level?: string | null;
  meal_frequency: number;
  sugar_intake?: number | null;
  exercise_level?: string;
  medications: string[];
  fasting_glucose?: number | null;
  a1c_level?: number | null;
  activity_level?: string;
  smoking_status?: string;
  family_history?: boolean;
  
  // Calculated fields (returned by backend)
  bmi?: number;
  bmi_category?: string;
  diabetes_risk?: string;
}

export interface SimulationParams {
  patient_data: PatientData;
  simulation_hours: number;
  food_factor: number;
  palmitic_factor: number;
  drug_dosage: number;
  show_optimal: boolean;
  meal_times?: number[];
  exercise_times?: number[];
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
    diabetes_type: string;
    diabetes_risk: string;
    activity_level: string;
    medications: string[];
  };
  simulation_summary: {
    average_glucose: number;
    max_glucose: number;
    min_glucose: number;
    glucose_variability: number;
    time_in_range: number;
    time_above_range: number;
    time_below_range: number;
    estimated_a1c: number;
    simulation_id?: string;
  };
  recommendations: string[];
  risk_factors: string[];
}

export interface ValidationResponse {
  bmi: number;
  bmi_category: string;
  obesity_level: string;
  diabetes_type: string;
  diabetes_risk: string;
  valid: boolean;
  warnings: string[];
  recommendations: string[];
}

export interface HealthMetrics {
  basic_metrics: {
    bmi: number;
    bmi_category: string;
    diabetes_risk: string;
  };
  metabolic_metrics: {
    basal_metabolic_rate: number;
    daily_calorie_needs: number;
    metabolic_age: number;
  };
  target_ranges: {
    ideal_weight_range: [number, number];
    target_glucose_fasting: string;
    target_a1c: string;
  };
  recommendations: {
    weekly_exercise_minutes: number;
    cardiovascular_risk: string;
    screening_frequency: string;
  };
}

export interface ODEParameters {
  // Half-saturation constants
  K_L: number;
  K_U2: number;
  K_U4: number;
  K_I: number;
  
  // Activation rates
  lambda_tilde_A: number;
  lambda_tilde_B: number;
  gamma_L: number;
  lambda_IB: number;
  lambda_U4_I: number;
  lambda_U2C: number;
  lambda_CA: number;
  gamma_G: number;
  gamma_G_star: number;
  gamma_O: number;
  gamma_P: number;
  gamma_P_hat: number;
  
  // Transport rates
  lambda_GU4: number;
  lambda_G_star_U2: number;
  lambda_T_alpha: number;
  lambda_T_alpha_P: number;
  
  // Decay rates
  mu_A: number;
  mu_B: number;
  mu_LB: number;
  mu_LA: number;
  mu_I: number;
  mu_U4: number;
  mu_U2: number;
  mu_C: number;
  mu_T_alpha: number;
  mu_O: number;
  mu_P: number;
  mu_IG: number;
  
  // Switch parameters
  gamma_1: number;
  gamma_2: number;
  xi_1: number;
  xi_2: number;
  xi_3: number;
  xi_4: number;
  eta_T_alpha: number;
  I_hypo: number;
  L_0: number;
  K_hat_L: number;
  K_hat_O: number;
  
  // Patient-specific adjustments
  obesity_factor?: number;
}

export interface PDFReportData {
  patient_info: PatientData;
  simulation_result: SimulationResult;
  ode_parameters: ODEParameters;
  chart_image: string; // Base64 encoded image
}