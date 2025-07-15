// src/utils/api.ts
import axios from 'axios';
import { SimulationParams, SimulationResult, PatientData, ValidationResponse, HealthMetrics } from '../types/diabetes';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Increased timeout for complex simulations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const simulationAPI = {
  // Test API connection
  testConnection: async (): Promise<boolean> => {
    try {
      const response = await apiClient.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('API connection failed:', error);
      return false;
    }
  },

  // Get API info
  getAPIInfo: async () => {
    try {
      const response = await apiClient.get('/');
      return response.data;
    } catch (error: any) {
      console.error('Failed to get API info:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get API info');
    }
  },

  // Run diabetes simulation
  runSimulation: async (params: SimulationParams): Promise<SimulationResult> => {
    try {
      console.log('Running simulation with params:', params);
      const response = await apiClient.post('/api/v1/simulation/run', params);
      return response.data;
    } catch (error: any) {
      console.error('Simulation failed:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to run simulation';
      throw new Error(Array.isArray(errorMessage) ? errorMessage[0]?.msg || 'Validation error' : errorMessage);
    }
  },

  // Validate patient data
  validatePatientData: async (patientData: PatientData): Promise<ValidationResponse> => {
    try {
      const response = await apiClient.post('/api/v1/user/validate', patientData);
      return response.data;
    } catch (error: any) {
      console.error('Validation failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to validate patient data');
    }
  },

  // Get health metrics
  getHealthMetrics: async (patientData: PatientData): Promise<HealthMetrics> => {
    try {
      const response = await apiClient.post('/api/v1/user/health-metrics', patientData);
      return response.data;
    } catch (error: any) {
      console.error('Health metrics calculation failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to calculate health metrics');
    }
  },

  // Get risk assessment
  getRiskAssessment: async (patientData: PatientData) => {
    try {
      const response = await apiClient.post('/api/v1/user/risk-assessment', patientData);
      return response.data;
    } catch (error: any) {
      console.error('Risk assessment failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to perform risk assessment');
    }
  },

  // Get lifestyle recommendations
  getLifestyleRecommendations: async (patientData: PatientData) => {
    try {
      const response = await apiClient.post('/api/v1/user/lifestyle-recommendations', patientData);
      return response.data;
    } catch (error: any) {
      console.error('Lifestyle recommendations failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get lifestyle recommendations');
    }
  },

  // Compare simulations
  compareSimulations: async (simulationIds: string[]) => {
    try {
      const response = await apiClient.post('/api/v1/simulation/compare', simulationIds);
      return response.data;
    } catch (error: any) {
      console.error('Simulation comparison failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to compare simulations');
    }
  },

  // Run intervention analysis
  runInterventionAnalysis: async (params: SimulationParams) => {
    try {
      const response = await apiClient.post('/api/v1/simulation/intervention-analysis', params);
      return response.data;
    } catch (error: any) {
      console.error('Intervention analysis failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to run intervention analysis');
    }
  },

  // Export simulation data
  exportSimulationJSON: async (simulationId: string) => {
    try {
      const response = await apiClient.post(`/api/v1/simulation/export-json/${simulationId}`, {}, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `simulation_${simulationId}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Export failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export simulation data');
    }
  },

  // Export simulation as CSV
  exportSimulationCSV: async (simulationId: string) => {
    try {
      const response = await apiClient.post(`/api/v1/simulation/export-csv/${simulationId}`, {}, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `simulation_${simulationId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('CSV export failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export CSV data');
    }
  },

  // Get cached simulation result
  getCachedSimulation: async (simulationId: string): Promise<SimulationResult> => {
    try {
      const response = await apiClient.get(`/api/v1/simulation/result/${simulationId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get cached simulation:', error);
      throw new Error(error.response?.data?.detail || 'Failed to retrieve simulation result');
    }
  },

  // Get API metrics
  getAPIMetrics: async () => {
    try {
      const response = await apiClient.get('/metrics');
      return response.data;
    } catch (error: any) {
      console.error('Failed to get API metrics:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get API metrics');
    }
  },

  // Clear simulation cache
  clearSimulationCache: async () => {
    try {
      const response = await apiClient.delete('/api/v1/simulation/clear-cache');
      return response.data;
    } catch (error: any) {
      console.error('Failed to clear cache:', error);
      throw new Error(error.response?.data?.detail || 'Failed to clear simulation cache');
    }
  }
};

// Default export to make it a proper module
export default simulationAPI;