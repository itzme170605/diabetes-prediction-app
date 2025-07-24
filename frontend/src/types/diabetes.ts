// src/types/diabetes.ts
export interface PatientData {
  name: string;
  age: number;
  weight: number; // kg
  height: number; // cm
  gender: string;
  diabetes_type?: string | null;
  obesity_level?: string | null;
  meal_frequency: number;
  sugar_intake?: number | null;
  exercise_level?: string;
  medications: string[];
  fasting_glucose?: number | null; // mg/dL
  a1c_level?: number | null; // %
  activity_level?: string;
  smoking_status?: string;
  family_history?: boolean;
  
  // Calculated fields (returned by backend)
  bmi?: number | null;
  bmi_category?: string | null;
  diabetes_risk?: string | null;
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
  
  // Additional enhanced variables from the 12-variable ODE model
  glut2?: number[];
  glut4?: number[];
  palmitic_acid?: number[];
  oleic_acid?: number[];
  tnf_alpha?: number[];
  stored_glucose?: number[];
  
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
    obesity_multiplier?: number;
    food_adaptation_factor?: number;
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
    time_very_high?: number;
    average_excursion?: number;
    estimated_a1c: number;
    simulation_id?: string;
  };
  
  // Enhanced glucose metrics from the backend
  glucose_metrics?: {
    dawn_phenomenon?: number;
    post_meal_response?: {
      average_post_meal_rise: number;
      max_post_meal_rise: number;
      meal_response_variability: number;
    };
    glucose_stability?: {
      mean_rate_of_change: number;
      max_rate_of_change: number;
      mage: number; // Mean Amplitude of Glucose Excursions
      stability_score: number;
    };
  };
  
  // Enhanced insulin metrics
  insulin_metrics?: {
    average_insulin: number;
    peak_insulin: number;
    insulin_variability: number;
    fasting_insulin: number;
  };
  
  // Hormone balance metrics
  hormone_balance?: {
    insulin_glucagon_ratio: number;
    hormone_variability: number;
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
  patient_info: {
    name: string;
    age: number;
    bmi: number;
    bmi_category: string;
    diabetes_risk: string;
  };
  health_metrics: {
    ideal_weight_range: [number, number];
    current_weight: number;
    weight_status: string;
    bmr: number;
    daily_calorie_needs: number;
    recommended_exercise_minutes: number;
    cardiovascular_risk: string;
    metabolic_age: number;
  };
  risk_factors: {
    age_risk: boolean;
    weight_risk: boolean;
    family_history_risk: boolean;
    lifestyle_risk: boolean;
    smoking_risk: boolean;
    diabetes_risk_level: string;
  };
}

export interface RiskAssessment {
  patient_summary: {
    name: string;
    age: number;
    bmi: number;
    current_diabetes_status: string;
  };
  diabetes_risk: {
    risk_level: string;
    risk_percentage: string;
    risk_score: number;
    primary_risk_factors: string[];
  };
  cardiovascular_risk: {
    risk_level: string;
    risk_percentage: string;
    risk_score: number;
    primary_risk_factors: string[];
  };
  recommendations: string[];
  screening_schedule: {
    diabetes_screening: string;
    a1c_testing?: string;
    blood_pressure: string;
    lipid_panel: string;
    cardiovascular_exam?: string;
  };
}

export interface LifestyleRecommendations {
  patient_profile: {
    name: string;
    current_status: {
      bmi: number;
      diabetes_type: string;
      activity_level: string;
    };
    goals: string[];
  };
  recommendations: {
    nutrition: string[];
    exercise: string[];
    lifestyle: string[];
    monitoring: string[];
    medical: string[];
  };
  sample_meal_plan: {
    breakfast: string[];
    lunch: string[];
    dinner: string[];
    snacks: string[];
  };
  exercise_plan: {
    weekly_structure: any;
    progression: any;
    precautions: string[];
  };
  expected_outcomes: any;
}

export interface ComparisonResults {
  comparison_results?: any[];
  comparison_metrics?: {
    scenario: string;
    a1c_estimate: number;
    a1c_change: number;
    average_glucose: number;
    glucose_variability: number;
    time_in_range: number;
  }[];
  recommendations?: string[];
  clinical_outcomes?: string[];
  
  // For obesity progression
  progression_results?: any[];
  progression_summary?: any;
  
  // For treatment analysis
  treatment_results?: any[];
  treatment_analysis?: any[];
}

export interface ODEParameters {
  // Half-saturation constants (g/cm³)
  K_L: number;           // Half-saturation of GLP-1
  K_hat_L: number;       // Inhibitory-saturation by GLP-1
  K_U2: number;          // Half-saturation of GLUT-2
  K_U4: number;          // Half-saturation of GLUT-4
  K_I: number;           // Half-saturation of insulin
  K_hat_O: number;       // Inhibitory-saturation of P by O
  K_D?: number;          // Half-saturation of G by D (drug)
  K_hat_D?: number;      // Inhibitory-saturation of G by D
  
  // Activation rates (d⁻¹)
  lambda_tilde_A: number;        // Activation rate of A
  lambda_tilde_B: number;        // Activation rate of B
  gamma_L: number;               // Baseline secretion rate of GLP-1
  lambda_IB: number;             // Secretion rate of insulin by B
  lambda_U4_I: number;           // Secretion rate of GLUT-4 by I
  lambda_U2C: number;            // Secretion rate of GLUT-2 by C
  lambda_CA: number;             // Secretion rate of glucagon by A
  gamma_G: number;               // Baseline secretion rate of glucose
  gamma_G_star: number;          // Baseline rate of early glucose elimination
  gamma_O: number;               // Baseline secretion rate of oleic acid
  gamma_P: number;               // Baseline secretion rate of palmitic acid
  gamma_P_hat: number;           // Obesity-prone secretion rate of palmitic acid
  
  // Transport rates (d⁻¹)
  lambda_GU4: number;            // Transportation rate of glucose by U4
  lambda_G_star_U2: number;      // Importation rate of liver-glucose by U2
  lambda_T_alpha: number;        // Normal secretion rate of TNF-α
  lambda_T_alpha_P: number;      // Secretion rate of TNF-α by palmitic acid
  
  // Decay/degradation rates (d⁻¹)
  mu_A: number;                  // Deactivation rate of A
  mu_B: number;                  // Deactivation rate of B
  mu_LB: number;                 // Absorption rate of GLP-1 by B
  mu_LA: number;                 // Absorption rate of GLP-1 by A
  mu_I: number;                  // Decay rate of insulin
  mu_U4: number;                 // Decay rate of GLUT-4
  mu_U2: number;                 // Decay rate of GLUT-2
  mu_C: number;                  // Decay rate of glucagon
  mu_T_alpha: number;            // Decay rate of TNF-α
  mu_O: number;                  // Degradation rate of oleic acid
  mu_P: number;                  // Degradation rate of palmitic acid
  mu_D?: number;                 // Degradation rate of drug
  mu_IG: number;                 // Baseline decay rate of I by G
  
  // Switch parameters
  gamma_1: number;               // Blocking rate of glucagon
  gamma_2: number;               // Inducing rate of glucagon
  xi_1: number;                  // Deactivation rate of B by G
  xi_2: number;                  // Deactivation rate of B by P
  xi_3: number;                  // Switch level of G for inhibition of C-secretion
  xi_4: number;                  // Switch level of G for activation of C-secretion
  eta_T_alpha: number;           // Rate of inhibiting-effect of TNF-α on GLUT-4
  I_hypo: number;                // Level of I in hypoglycemia
  L_0: number;                   // Threshold GLP-1 level
  
  // Patient-specific adjustments
  obesity_factor?: number;
  age_factor?: number;
  activity_factor?: number;
}

export interface EnhancedSimulationMetrics {
  // Time-in-range metrics
  time_in_tight_range: number;    // 70-140 mg/dL
  time_in_range: number;          // 70-180 mg/dL
  time_above_range: number;       // >180 mg/dL
  time_below_range: number;       // <70 mg/dL
  time_very_high: number;         // >250 mg/dL
  
  // Glucose variability metrics
  coefficient_of_variation: number;
  standard_deviation: number;
  mean_amplitude_glucose_excursions: number;
  
  // Clinical metrics
  estimated_a1c: number;
  dawn_phenomenon: number;        // Early morning glucose rise
  post_meal_peaks: number[];      // Post-meal glucose peaks
  
  // Advanced metrics
  glucose_management_indicator: number;
  time_in_tight_range_percentage: number;
}

export interface DrugTreatmentParams {
  drug_name: string;
  dosage_mg: number;
  administration_schedule: string;
  treatment_duration_weeks: number;
  lifestyle_modifications: {
    food_reduction: number;
    exercise_increase: number;
    meal_timing_improvement: boolean;
  };
}

export interface ComparisonAnalysis {
  scenarios: {
    name: string;
    description: string;
    parameters: any;
    result: SimulationResult;
  }[];
  comparison_metrics: {
    scenario: string;
    a1c_estimate: number;
    a1c_change: number;
    average_glucose: number;
    glucose_variability: number;
    time_in_range: number;
    effectiveness_score?: number;
  }[];
  statistical_significance?: any;
  clinical_recommendations: string[];
  risk_benefit_analysis?: any;
}

export interface PDFReportData {
  patient_info: PatientData;
  simulation_result: SimulationResult;
  ode_parameters?: ODEParameters;
  chart_image: string; // Base64 encoded image
  analysis_type: string;
  generation_date: string;
  rit_branding: {
    institution: string;
    logo_url?: string;
    website: string;
  };
}

// Enhanced API Response Types
export interface APIResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
  timestamp: string;
  api_version?: string;
}

export interface SystemInfo {
  message: string;
  version: string;
  status: string;
  scientific_basis: {
    paper: string;
    journal: string;
    doi: string;
    model_type: string;
  };
  core_features: string[];
  enhanced_features_v2_1: string[];
  simulation_capabilities: {
    variables: number;
    parameters: string;
    time_resolution: string;
    simulation_duration: string;
    patient_personalization: string;
  };
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  message: string;
  timestamp: string;
  system_validation: {
    dependencies: any;
    core_services: any;
    model_validation: any;
  };
  api_features: {
    simulation_endpoints: number;
    user_data_endpoints: number;
    export_formats: string[];
    cache_system: string;
  };
}

// Meal-specific types
export interface MealPattern {
  name: string;
  factors: number[]; // [breakfast, lunch, dinner, snack]
  description: string;
}

export interface MealAnalysis {
  pattern: MealPattern;
  glucose_impact: {
    peak_glucose: number;
    time_to_peak: number;
    area_under_curve: number;
  };
  insulin_response: {
    peak_insulin: number;
    insulin_sensitivity_index: number;
  };
}

// Export commonly used constants
export const MEAL_PATTERNS: MealPattern[] = [
  {
    name: 'Balanced',
    factors: [1.0, 1.0, 1.0, 0.0],
    description: 'Equal portions for all meals'
  },
  {
    name: 'Light-Heavy',
    factors: [0.5, 1.0, 2.0, 0.0],
    description: 'Traditional eating pattern with light breakfast, heavy dinner'
  },
  {
    name: 'Heavy-Light',
    factors: [2.0, 1.0, 0.5, 0.0],
    description: 'Diabetes-friendly pattern with heavy breakfast, light dinner'
  },
  {
    name: 'Small-Frequent',
    factors: [0.8, 0.8, 0.8, 0.6],
    description: 'Four smaller meals including evening snack'
  }
];

export const GLUCOSE_TARGET_RANGES = {
  normal: { min: 70, max: 140 },
  tight: { min: 70, max: 120 },
  standard: { min: 70, max: 180 },
  hypoglycemia: { min: 0, max: 70 },
  hyperglycemia: { min: 180, max: 400 }
};

export const A1C_CATEGORIES = {
  normal: { min: 0, max: 5.7 },
  prediabetic: { min: 5.7, max: 6.5 },
  diabetic: { min: 6.5, max: 15 }
};

// RIT-specific branding constants
export const RIT_BRANDING = {
  institution: 'Rochester Institute of Technology',
  colors: {
    primary_orange: '#f76902',
    secondary_orange: '#ff8c00',
    gray: '#58595b',
    light_gray: '#e9ecef',
    white: '#ffffff'
  },
  website: 'https://www.rit.edu',
  department: 'School of Mathematics and Statistics'
};