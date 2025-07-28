// src/App.tsx - Updated to handle meal and drug schedules
import React, { useState, useEffect } from 'react';
import './App.css';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import ResearchPage from './pages/ResearchPage';
import PatientForm from './components/PatientForms';
import SimulationDashboard from './components/SimulationDashboard';
import { PatientData, MealSchedule, DrugSchedule } from './types/diabetes';
import { simulationAPI } from './utils/api';

type AppView = 'home' | 'about' | 'research' | 'simulation' | 'form';

function App() {
  const [currentView, setCurrentView] = useState<AppView>('home');
  const [patientData, setPatientData] = useState<PatientData | null>(null);
  const [mealSchedule, setMealSchedule] = useState<MealSchedule | undefined>();
  const [drugSchedule, setDrugSchedule] = useState<DrugSchedule | undefined>();
  const [apiConnected, setApiConnected] = useState<boolean>(false);

  useEffect(() => {
    // Test API connection on app start
    const testConnection = async () => {
      const connected = await simulationAPI.testConnection();
      setApiConnected(connected);
    };
    testConnection();
  }, []);

  const handlePatientSubmit = (
    data: PatientData, 
    mealSchedule?: MealSchedule, 
    drugSchedule?: DrugSchedule
  ) => {
    setPatientData(data);
    setMealSchedule(mealSchedule);
    setDrugSchedule(drugSchedule);
    setCurrentView('simulation');
  };

  const handleTryNow = () => {
    setCurrentView('form');
  };

  const handleBackToHome = () => {
    setCurrentView('home');
    setPatientData(null);
    setMealSchedule(undefined);
    setDrugSchedule(undefined);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'home':
        return <HomePage onTryNow={handleTryNow} onLearnMore={() => setCurrentView('research')} />;
      case 'about':
        return <AboutPage />;
      case 'research':
        return <ResearchPage />;
      case 'form':
        return <PatientForm onSubmit={handlePatientSubmit} />;
      case 'simulation':
        return patientData ? (
          <SimulationDashboard 
            patientData={patientData} 
            mealSchedule={mealSchedule}
            drugSchedule={drugSchedule}
          />
        ) : null;
      default:
        return <HomePage onTryNow={handleTryNow} onLearnMore={() => setCurrentView('research')} />;
    }
  };

  return (
    <div className="App">
      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="navbar-container">
          <div className="navbar-logo" onClick={handleBackToHome}>
            <h1>DiabetesScope</h1>
            <span>Glucose Dynamics Simulator</span>
          </div>
          <div className="navbar-menu">
            <button 
              className={`nav-link ${currentView === 'home' ? 'active' : ''}`}
              onClick={() => setCurrentView('home')}
            >
              Home
            </button>
            <button 
              className={`nav-link ${currentView === 'research' ? 'active' : ''}`}
              onClick={() => setCurrentView('research')}
            >
              Research
            </button>
            <button 
              className={`nav-link ${currentView === 'about' ? 'active' : ''}`}
              onClick={() => setCurrentView('about')}
            >
              About
            </button>
            <button 
              className="btn-try-now"
              onClick={handleTryNow}
            >
              Try Now
            </button>
          </div>
          <div className="navbar-mobile-menu">
            <div className={`api-status ${apiConnected ? 'connected' : 'disconnected'}`}>
              {apiConnected ? '🟢 API Ready' : '🔴 API Offline'}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {!apiConnected && (currentView === 'form' || currentView === 'simulation') ? (
          <div className="error-message">
            <h2>⚠️ Backend Connection Required</h2>
            <p>Please make sure the backend server is running on localhost:8000</p>
            <p>Run: <code>cd backend && python ./app/main.py</code></p>
            <button onClick={() => window.location.reload()} className="btn-primary">
              Retry Connection
            </button>
          </div>
        ) : (
          renderCurrentView()
        )}
      </main>

      {/* Footer */}
      {currentView === 'home' && (
        <footer className="footer">
          <div className="footer-container">
            <div className="footer-content">
              <div className="footer-section">
                <h3>DiabetesScope</h3>
                <p>Advanced mathematical modeling of glucose dynamics in diabetes.</p>
              </div>
              <div className="footer-section">
                <h3>Quick Links</h3>
                <ul>
                  <li><button onClick={() => setCurrentView('research')}>Research Paper</button></li>
                  <li><button onClick={() => setCurrentView('about')}>About Team</button></li>
                  <li><button onClick={handleTryNow}>Try Simulation</button></li>
                </ul>
              </div>
              <div className="footer-section">
                <h3>Academic Citation</h3>
                <p className="citation">
                  Siewe, N., & Friedman, A. (2024). A mathematical model of obesity-induced type 2 diabetes 
                  and efficacy of anti-diabetic weight reducing drug. <em>Journal of Theoretical Biology</em>, 
                  581, 111756.
                </p>
                <p>
                  Research reported in this publication was supported by the National Institute Of General Medical Sciences of the National Institutes of Health under Award Number R16GM154782.
                  The content is solely the responsibility of the authors and does not necessarily represent the official views of the National Institutes of Health.
                </p>
              </div>
            </div>
            <div className="footer-bottom">
              <p>© 2024 Rochester Institute of Technology. Educational and Research Use Only.</p>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
}

export default App;