// src/pages/HomePage.tsx
import React, { useState, useEffect } from 'react';
import './HomePage.css';

interface HomePageProps {
  onTryNow: () => void;
  onLearnMore: () => void;
}

const HomePage: React.FC<HomePageProps> = ({ onTryNow, onLearnMore }) => {
  const [currentAnimation, setCurrentAnimation] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentAnimation((prev) => (prev + 1) % 3);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Understanding Diabetes Through
              <span className="gradient-text"> Mathematical Modeling</span>
            </h1>
            <p className="hero-subtitle">
              Explore glucose dynamics, insulin resistance, and treatment effects using 
              an interactive simulation based on peer-reviewed research
            </p>
            <div className="hero-buttons">
              <button className="btn-primary-large" onClick={onTryNow}>
                🧪 Try Simulation Now
              </button>
              <button className="btn-secondary-large" onClick={onLearnMore}>
                📚 Learn About Research
              </button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="glucose-molecule-animation">
              <div className="molecule-container">
                <div className="glucose-ring">
                  <div className="carbon-atom c1"></div>
                  <div className="carbon-atom c2"></div>
                  <div className="carbon-atom c3"></div>
                  <div className="carbon-atom c4"></div>
                  <div className="carbon-atom c5"></div>
                  <div className="carbon-atom c6"></div>
                  <div className="oxygen-atom o1"></div>
                </div>
                <div className="molecule-label">C₆H₁₂O₆</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Key Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔬</div>
              <h3>Scientific Accuracy</h3>
              <p>Based on peer-reviewed research with 12-variable ODE system modeling glucose dynamics</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">👤</div>
              <h3>Patient Profiles</h3>
              <p>Customize demographics, medical history, and lifestyle factors for personalized simulations</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Interactive Visualization</h3>
              <p>Real-time parameter adjustment with immediate feedback on glucose and insulin dynamics</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💊</div>
              <h3>Treatment Modeling</h3>
              <p>Simulate effects of GLP-1 agonist medications like Mounjaro and Ozempic</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pathophysiology Animation Section */}
      <section className="pathophysiology-section">
        <div className="container">
          <h2 className="section-title">Diabetes Pathophysiology</h2>
          <p className="section-subtitle">
            Interactive visualization of normal vs. diabetic glucose regulation
          </p>
          
          <div className="pathophysiology-container">
            <div className="scenario-tabs">
              <button 
                className={`tab ${currentAnimation === 0 ? 'active' : ''}`}
                onClick={() => setCurrentAnimation(0)}
              >
                Normal Physiology
              </button>
              <button 
                className={`tab ${currentAnimation === 1 ? 'active' : ''}`}
                onClick={() => setCurrentAnimation(1)}
              >
                Obesity & Inflammation
              </button>
              <button 
                className={`tab ${currentAnimation === 2 ? 'active' : ''}`}
                onClick={() => setCurrentAnimation(2)}
              >
                Type 2 Diabetes
              </button>
            </div>

            <div className="animation-container">
              {currentAnimation === 0 && <NormalPathwayAnimation />}
              {currentAnimation === 1 && <ObesityPathwayAnimation />}
              {currentAnimation === 2 && <DiabetesPathwayAnimation />}
            </div>

            <div className="pathway-description">
              {currentAnimation === 0 && (
                <div className="description-card normal">
                  <h3>🟢 Normal Glucose Regulation</h3>
                  <ul>
                    <li>Food intake triggers GLP-1 release</li>
                    <li>β-cells secrete insulin efficiently</li>
                    <li>GLUT-4 transports glucose into cells</li>
                    <li>Blood glucose returns to normal levels</li>
                  </ul>
                </div>
              )}
              {currentAnimation === 1 && (
                <div className="description-card warning">
                  <h3>🟡 Obesity-Induced Changes</h3>
                  <ul>
                    <li>Increased palmitic acid from adipose tissue</li>
                    <li>TNF-α inflammation impairs insulin signaling</li>
                    <li>GLUT-4 function becomes compromised</li>
                    <li>Insulin resistance begins to develop</li>
                  </ul>
                </div>
              )}
              {currentAnimation === 2 && (
                <div className="description-card danger">
                  <h3>🔴 Type 2 Diabetes</h3>
                  <ul>
                    <li>β-cell dysfunction and apoptosis</li>
                    <li>Severe insulin resistance</li>
                    <li>Chronic hyperglycemia</li>
                    <li>Complications develop over time</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Research Overview Section */}
      <section className="research-section">
        <div className="container">
          <div className="research-content">
            <div className="research-text">
              <h2>Built on Research</h2>
              <p>
                This simulation is based on the mathematical model developed by 
                <strong> Nourridine Siewe</strong> and <strong>Avner Friedman</strong>, 
                published in the Journal of Theoretical Biology (2024).
              </p>
              <p>
                The model incorporates 12 physiological variables and over 50 parameters 
                to accurately simulate glucose dynamics in health and disease.
              </p>
              <div className="research-stats">
                <div className="stat">
                  <div className="stat-number">12</div>
                  <div className="stat-label">Variables</div>
                </div>
                <div className="stat">
                  <div className="stat-number">50+</div>
                  <div className="stat-label">Parameters</div>
                </div>
                <div className="stat">
                  <div className="stat-number">2024</div>
                  <div className="stat-label">Published</div>
                </div>
              </div>
              <button className="btn-secondary" onClick={onLearnMore}>
                Explore the Research →
              </button>
            </div>
            <div className="research-visual">
              <div className="equation-showcase">
                <div className="equation-card">
                  <h4>GLP-1 Dynamics</h4>
                  <div className="equation">
                    dL/dt = λ<sub>L</sub>(t) - μ<sub>LB</sub>BL - μ<sub>LA</sub>AL
                  </div>
                </div>
                <div className="equation-card">
                  <h4>Insulin Dynamics</h4>
                  <div className="equation">
                    dI/dt = λ<sub>IB</sub>B - μ<sub>I</sub>I - μ<sub>IG</sub>GI
                  </div>
                </div>
                <div className="equation-card">
                  <h4>Glucose Dynamics</h4>
                  <div className="equation">
                    dG/dt = λ<sub>G</sub>(t) - λ<sub>G*</sub>(t)G + ...
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Explore?</h2>
            <p>
              Start simulating glucose dynamics with customizable patient profiles 
              and treatment scenarios
            </p>
            <button className="btn-primary-large" onClick={onTryNow}>
              🚀 Launch Simulation
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

// Animation Components
const NormalPathwayAnimation: React.FC = () => {
  return (
    <div className="pathway-animation normal-pathway">
      <div className="pathway-step step-1">
        <div className="step-icon">🍽️</div>
        <div className="step-label">Food Intake</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-2">
        <div className="step-icon">🧬</div>
        <div className="step-label">GLP-1 Release</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-3">
        <div className="step-icon">🔬</div>
        <div className="step-label">β-cell Activation</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-4">
        <div className="step-icon">💉</div>
        <div className="step-label">Insulin Release</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-5">
        <div className="step-icon">📉</div>
        <div className="step-label">Glucose Uptake</div>
      </div>
    </div>
  );
};

const ObesityPathwayAnimation: React.FC = () => {
  return (
    <div className="pathway-animation obesity-pathway">
      <div className="pathway-step step-1">
        <div className="step-icon">🍔</div>
        <div className="step-label">Overeating</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-2">
        <div className="step-icon">🏮</div>
        <div className="step-label">Adipose Tissue</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-3">
        <div className="step-icon">⚡</div>
        <div className="step-label">Palmitic Acid</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-4">
        <div className="step-icon">🔥</div>
        <div className="step-label">TNF-α Inflammation</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-5">
        <div className="step-icon">🚫</div>
        <div className="step-label">Insulin Resistance</div>
      </div>
    </div>
  );
};

const DiabetesPathwayAnimation: React.FC = () => {
  return (
    <div className="pathway-animation diabetes-pathway">
      <div className="pathway-step step-1">
        <div className="step-icon">💀</div>
        <div className="step-label">β-cell Death</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-2">
        <div className="step-icon">📉</div>
        <div className="step-label">↓ Insulin</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-3">
        <div className="step-icon">📈</div>
        <div className="step-label">↑ Glucose</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-4">
        <div className="step-icon">🩸</div>
        <div className="step-label">Hyperglycemia</div>
      </div>
      <div className="pathway-arrow">→</div>
      <div className="pathway-step step-5">
        <div className="step-icon">⚠️</div>
        <div className="step-label">Complications</div>
      </div>
    </div>
  );
};

export default HomePage;