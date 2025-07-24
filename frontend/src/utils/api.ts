// src/utils/api.ts
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface SimulationParams {
  patient_data: any;
  simulation_hours: number;
  food_factor: number;
  palmitic_factor: number;
  drug_dosage: number;
  show_optimal: boolean;
  meal_times: number[];
  meal_factors: number[];
  exercise_times?: number[];
}

export interface PatientValidationRequest {
  patient_data: any;
}

export interface RiskAssessmentRequest {
  patient_data: any;
}

export interface LifestyleRecommendationRequest {
  patient_data: any;
  goals?: string[];
}

export interface DrugTreatmentParams {
  drug_name?: string;
  dosage_mg?: number;
  administration_schedule?: string;
  treatment_duration_weeks?: number;
  lifestyle_modifications?: {
    food_reduction: number;
    exercise_increase: number;
    meal_timing_improvement: boolean;
  };
}

export interface ConnectionTestResult {
  connected: boolean;
  api_version?: string;
  features?: string[];
  backend_status?: string;
  error?: {
    error: string;
    message: string;
    suggestion: string;
  };
}

class SimulationAPI {
  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Enhanced Simulation Endpoints
  async runSimulation(params: SimulationParams) {
    return this.request('/api/v1/simulation/run', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async compareMealPatterns(params: SimulationParams) {
    return this.request('/api/v1/simulation/compare-meals', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async simulateObesityProgression(params: SimulationParams) {
    return this.request('/api/v1/simulation/obesity-progression', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async analyzeDrugTreatment(params: SimulationParams, treatmentParams?: DrugTreatmentParams) {
    const payload = treatmentParams ? 
      { base_params: params, treatment_params: treatmentParams } : 
      params;
    
    return this.request('/api/v1/simulation/drug-treatment-analysis', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async performSensitivityAnalysis(params: SimulationParams, parameterRanges?: any) {
    return this.request('/api/v1/simulation/sensitivity-analysis', {
      method: 'POST',
      body: JSON.stringify({ 
        base_params: params, 
        parameter_ranges: parameterRanges 
      }),
    });
  }

  async analyzeInterventions(params: SimulationParams) {
    return this.request('/api/v1/simulation/intervention-analysis', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async batchSimulate(simulationList: SimulationParams[]) {
    return this.request('/api/v1/simulation/batch-simulate', {
      method: 'POST',
      body: JSON.stringify(simulationList),
    });
  }

  async compareSimulations(simulationIds: string[]) {
    return this.request('/api/v1/simulation/compare', {
      method: 'POST',
      body: JSON.stringify(simulationIds),
    });
  }

  async getSimulationResult(simulationId: string) {
    return this.request(`/api/v1/simulation/result/${simulationId}`);
  }

  async exportSimulationJSON(simulationId: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/simulation/export-json/${simulationId}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }
    
    return response.blob();
  }

  async exportSimulationCSV(simulationId: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/simulation/export-csv/${simulationId}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }
    
    return response.blob();
  }

  async clearSimulationCache() {
    return this.request('/api/v1/simulation/clear-cache', {
      method: 'DELETE',
    });
  }

  async getCacheStatus() {
    return this.request('/api/v1/simulation/cache-status');
  }

  // Enhanced User Data Endpoints
  async validatePatientData(patientData: any) {
    return this.request('/api/v1/user/validate', {
      method: 'POST',
      body: JSON.stringify(patientData),
    });
  }

  async calculateHealthMetrics(patientData: any) {
    return this.request('/api/v1/user/health-metrics', {
      method: 'POST',
      body: JSON.stringify(patientData),
    });
  }

  async performRiskAssessment(request: RiskAssessmentRequest) {
    return this.request('/api/v1/user/risk-assessment', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async generateLifestyleRecommendations(request: LifestyleRecommendationRequest) {
    return this.request('/api/v1/user/lifestyle-recommendations', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // System Endpoints
  async getHealthStatus() {
    return this.request('/health', { method: 'GET' });
  }

  async getSystemMetrics() {
    return this.request('/metrics', { method: 'GET' });
  }

  async getAPIInfo() {
    return this.request('/api-info', { method: 'GET' });
  }

  // Root endpoint for system info - FIXED to use correct endpoint
  async getSystemInfo() {
    return this.request('/', { method: 'GET' });
  }

  // Utility Methods
  async downloadFile(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  async exportAndDownloadJSON(simulationId: string, filename?: string) {
    try {
      const blob = await this.exportSimulationJSON(simulationId);
      const defaultFilename = `RIT_simulation_${simulationId}_${new Date().toISOString().split('T')[0]}.json`;
      await this.downloadFile(blob, filename || defaultFilename);
    } catch (error) {
      console.error('JSON export failed:', error);
      throw error;
    }
  }

  async exportAndDownloadCSV(simulationId: string, filename?: string) {
    try {
      const blob = await this.exportSimulationCSV(simulationId);
      const defaultFilename = `RIT_simulation_${simulationId}_${new Date().toISOString().split('T')[0]}.csv`;
      await this.downloadFile(blob, filename || defaultFilename);
    } catch (error) {
      console.error('CSV export failed:', error);
      throw error;
    }
  }

  // Enhanced Error Handling
  handleError(error: any, context: string = 'API request') {
    console.error(`${context} failed:`, error);
    
    if (error.message?.includes('fetch')) {
      return {
        error: 'Network Error',
        message: 'Unable to connect to the RIT diabetes simulation service. Please check your connection and try again.',
        suggestion: 'Verify that the backend service is running on the correct port (8000) and accessible.'
      };
    }
    
    if (error.message?.includes('validation')) {
      return {
        error: 'Validation Error',
        message: 'The provided patient data contains invalid values.',
        suggestion: 'Please check all required fields and ensure values are within acceptable ranges.'
      };
    }
    
    if (error.message?.includes('simulation')) {
      return {
        error: 'Simulation Error',
        message: 'The diabetes simulation encountered an error during execution.',
        suggestion: 'Try adjusting the simulation parameters or patient data values.'
      };
    }
    
    return {
      error: 'Unknown Error',
      message: error.message || 'An unexpected error occurred',
      suggestion: 'Please try again or contact RIT support if the problem persists.'
    };
  }

  // Batch Operations
  async runMultipleAnalyses(params: SimulationParams) {
    const analyses = [
      this.runSimulation(params),
      this.compareMealPatterns(params),
      this.simulateObesityProgression(params),
      this.analyzeDrugTreatment(params)
    ];

    try {
      const results = await Promise.allSettled(analyses);
      
      return {
        basic: results[0].status === 'fulfilled' ? results[0].value : null,
        meals: results[1].status === 'fulfilled' ? results[1].value : null,
        progression: results[2].status === 'fulfilled' ? results[2].value : null,
        treatment: results[3].status === 'fulfilled' ? results[3].value : null,
        errors: results
          .map((result, index) => ({ 
            analysis: ['basic', 'meals', 'progression', 'treatment'][index], 
            error: result.status === 'rejected' ? result.reason : null 
          }))
          .filter(item => item.error)
      };
    } catch (error) {
      console.error('Batch analysis failed:', error);
      throw error;
    }
  }

  // Patient Data Helpers
  validatePatientDataLocally(patientData: any): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Required fields
    if (!patientData.name || patientData.name.trim().length === 0) {
      errors.push('Patient name is required');
    }

    if (!patientData.age || patientData.age < 1 || patientData.age > 120) {
      errors.push('Age must be between 1 and 120 years');
    }

    if (!patientData.weight || patientData.weight < 20 || patientData.weight > 300) {
      errors.push('Weight must be between 20 and 300 kg');
    }

    if (!patientData.height || patientData.height < 100 || patientData.height > 250) {
      errors.push('Height must be between 100 and 250 cm');
    }

    if (!patientData.gender || !['male', 'female', 'm', 'f'].includes(patientData.gender.toLowerCase())) {
      errors.push('Gender must be specified as male or female');
    }

    // Optional field validation
    if (patientData.fasting_glucose && (patientData.fasting_glucose < 50 || patientData.fasting_glucose > 400)) {
      errors.push('Fasting glucose must be between 50 and 400 mg/dL');
    }

    if (patientData.a1c_level && (patientData.a1c_level < 3 || patientData.a1c_level > 15)) {
      errors.push('A1C level must be between 3% and 15%');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  calculateBMI(weight: number, height: number): number {
    const heightM = height / 100;
    return Number((weight / (heightM * heightM)).toFixed(1));
  }

  getBMICategory(bmi: number): string {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  }

  // Response Formatters
  formatSimulationResult(result: any) {
    return {
      ...result,
      formatted_timestamp: new Date(result.timestamp || Date.now()).toLocaleString(),
      formatted_duration: `${result.simulation_hours || 24} hours`,
      formatted_a1c: `${result.a1c_estimate || 0}%`,
      clinical_interpretation: this.interpretA1C(result.a1c_estimate || 0),
      rit_branding: 'Rochester Institute of Technology - Enhanced Diabetes Simulation'
    };
  }

  private interpretA1C(a1c: number): string {
    if (a1c < 5.7) return 'Normal glucose tolerance';
    if (a1c < 6.5) return 'Prediabetes - increased risk';
    if (a1c < 7.0) return 'Diabetes - good control';
    if (a1c < 8.0) return 'Diabetes - fair control';
    if (a1c < 9.0) return 'Diabetes - poor control';
    return 'Diabetes - very poor control';
  }

  // Backend Status Check
  async checkBackendStatus() {
    try {
      const response = await this.getHealthStatus();
      return {
        status: 'connected',
        message: 'Successfully connected to RIT Diabetes Simulation API',
        backend_info: response
      };
    } catch (error) {
      return {
        status: 'disconnected',
        message: 'Unable to connect to backend service',
        error: this.handleError(error, 'Backend connection')
      };
    }
  }

  // Enhanced connection testing - Fixed to use correct endpoints
  async testConnection(): Promise<ConnectionTestResult> {
    try {
      console.log('Testing connection to:', API_BASE_URL);
      
      // Test root endpoint first
      const systemInfo = await this.getSystemInfo();
      console.log('System info:', systemInfo);
      
      // Test health endpoint
      const healthStatus = await this.getHealthStatus();
      console.log('Health status:', healthStatus);
      
      return {
        connected: true,
        api_version: systemInfo.version || 'Unknown',
        features: systemInfo.core_features || [],
        backend_status: healthStatus.status
      };
    } catch (error) {
      console.error('Connection test failed:', error);
      return {
        connected: false,
        error: this.handleError(error, 'Connection test')
      };
    }
  }

  // Simple connection test that returns only boolean
  async isConnected(): Promise<boolean> {
    try {
      await this.getHealthStatus();
      return true;
    } catch (error) {
      return false;
    }
  }
}

// Create and export singleton instance
export const simulationAPI = new SimulationAPI();

// Export for testing or direct instantiation
export default SimulationAPI;