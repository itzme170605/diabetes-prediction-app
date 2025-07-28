// src/utils/api.ts - Updated with new backend endpoints
import axios from 'axios';
import { 
  PatientData, 
  SimulationParams, 
  SimulationResult, 
  ExtendedSimulationResult 
} from '../types/diabetes';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const simulationAPI = {
  testConnection: async (): Promise<boolean> => {
    try {
      const response = await api.get('/');
      return response.status === 200;
    } catch (error) {
      console.error('API connection failed:', error);
      return false;
    }
  },

  validatePatientData: async (patientData: PatientData) => {
    try {
      const response = await api.post('/api/user/validate', patientData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Validation failed');
    }
  },

  runSimulation: async (params: SimulationParams): Promise<SimulationResult> => {
    try {
      const response = await api.post('/api/simulation/run', params);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Simulation failed');
    }
  },

  runExtendedSimulation: async (params: SimulationParams): Promise<ExtendedSimulationResult> => {
    try {
      const response = await api.post('/api/simulation/run-extended', params);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Extended simulation failed');
    }
  },

  runMultiDaySimulation: async (params: SimulationParams): Promise<ExtendedSimulationResult> => {
    try {
      const response = await api.post('/api/simulation/multi-day', params);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Multi-day simulation failed');
    }
  },

  compareScenarios: async (baseParams: SimulationParams, scenarios: any[]): Promise<any> => {
    try {
      const response = await api.post('/api/simulation/compare-scenarios', {
        base_params: baseParams,
        scenarios: scenarios
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Scenario comparison failed');
    }
  },

  getPresetScenarios: async (): Promise<any> => {
    try {
      const response = await api.post('/api/simulation/preset-scenarios');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get preset scenarios');
    }
  },

  exportPDF: async (params: SimulationParams): Promise<Blob> => {
    try {
      const response = await api.post('/api/simulation/export-pdf', params, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'PDF export failed');
    }
  },
};