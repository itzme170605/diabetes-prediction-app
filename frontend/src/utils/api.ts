// src/utils/api.ts
import axios from 'axios';
import { SimulationParams, SimulationResult, PatientData } from '../types/diabetes';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const simulationAPI = {
  // Test API connection
  testConnection: async (): Promise<boolean> => {
    try {
      const response = await apiClient.get('/');
      return response.status === 200;
    } catch (error) {
      console.error('API connection failed:', error);
      return false;
    }
  },

  // Run diabetes simulation
  runSimulation: async (params: SimulationParams): Promise<SimulationResult> => {
    try {
      const response = await apiClient.post('/api/simulation/run', params);
      return response.data;
    } catch (error: any) {
      console.error('Simulation failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to run simulation');
    }
  },

  // Validate patient data
  validatePatientData: async (patientData: PatientData) => {
    try {
      const response = await apiClient.post('/api/user/validate', patientData);
      return response.data;
    } catch (error: any) {
      console.error('Validation failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to validate patient data');
    }
  },
};

// Default export to make it a proper module
export default simulationAPI;