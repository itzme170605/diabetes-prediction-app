// src/App.tsx
import React, { useState, useEffect } from 'react';
import './App.css';
import PatientForm from './components/PatientForms';
import SimulationDashboard from './components/SimulationDashboard';
import { PatientData } from './types/diabetes';
import { simulationAPI } from './utils/api';

function App() {
  const [currentView, setCurrentView] = useState<'form' | 'simulation'>('form');
  const [patientData, setPatientData] = useState<PatientData | null>(null);
  const [apiConnected, setApiConnected] = useState<boolean>(false);

  useEffect(() => {
    // Test API connection on app start
    const testConnection = async () => {
      const connected = await simulationAPI.testConnection();
      setApiConnected(connected);
      if (!connected) {
        console.warn('API connection failed - make sure backend is running on localhost:8000');
      }
    };
    testConnection();
  }, []);

  const handlePatientSubmit = (data: PatientData) => {
    setPatientData(data);
    setCurrentView('simulation');
  };

  const handleNewPatient = () => {
    setPatientData(null);
    setCurrentView('form');
  };

  return (
    <div className="App">
      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="navbar-container">
          <div className="navbar-logo">
            <h1>DiabetesScope</h1>
            <span>Glucose Dynamics Simulator</span>
          </div>
          <div className="navbar-actions">
            <div className={`api-status ${apiConnected ? 'connected' : 'disconnected'}`}>
              {apiConnected ? '🟢 API Connected' : '🔴 API Disconnected'}
            </div>
            {currentView === 'simulation' && (
              <button className="btn-secondary" onClick={handleNewPatient}>
                New Patient
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {!apiConnected ? (
          <div className="error-message">
            <h2>⚠️ Backend Connection Required</h2>
            <p>Please make sure the backend server is running on localhost:8000</p>
            <p>Run: <code>cd backend && python run.py</code></p>
            <button onClick={() => window.location.reload()} className="btn-primary">
              Retry Connection
            </button>
          </div>
        ) : currentView === 'form' ? (
          <PatientForm onSubmit={handlePatientSubmit} />
        ) : (
          patientData && <SimulationDashboard patientData={patientData} />
        )}
      </main>
    </div>
  );
}

export default App;