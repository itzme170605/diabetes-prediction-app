// src/types/diabetes.ts - Updated with new backend types
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
}

export interface MealSchedule {
  breakfast_time: number;
  breakfast_factor: number;
  lunch_time: number;
  lunch_factor: number;
  dinner_time: number;
  dinner_factor: number;
}

export interface DrugSchedule {
  drug_type: string;
  initial_dose: number;
  dose_increase_week: number;
  increased_dose: number;
}

export interface SimulationParams {
  patient_data: PatientData;
  simulation_hours: number;
  simulation_days?: number;
  meal_schedule?: MealSchedule;
  food_factor: number;
  palmitic_factor: number;
  drug_dosage: number;
  drug_schedule?: DrugSchedule;
  show_optimal: boolean;
  include_all_variables?: boolean;
}

export interface SimulationResult {
  time_points: number[];
  glucose: number[];
  insulin: number[];
  glucagon: number[];
  glp1: number[];
  optimal_glucose?: number[];
  a1c_estimate: number;
  diagnosis: string;
}

export interface ExtendedSimulationResult extends SimulationResult {
  alpha_cells?: number[];
  beta_cells?: number[];
  glut2?: number[];
  glut4?: number[];
  stored_glucose?: number[];
  oleic_acid?: number[];
  palmitic_acid?: number[];
  tnf_alpha?: number[];
  avg_glucose: number;
  glucose_variability: number;
  time_in_range: number;
}