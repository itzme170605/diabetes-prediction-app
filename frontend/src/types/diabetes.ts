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
}

export interface SimulationParams {
  patient_data: PatientData;
  simulation_hours: number;
  food_factor: number;
  palmitic_factor: number;
  drug_dosage: number;
  show_optimal: boolean;
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